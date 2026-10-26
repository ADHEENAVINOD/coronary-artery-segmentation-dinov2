"""
Train segmentation head on DINOv3 features.
Handles large images by processing in patches.
"""

import argparse
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from tqdm import tqdm
import matplotlib.pyplot as plt
import random
from transformers import AutoImageProcessor, AutoModel

Image.MAX_IMAGE_PIXELS = None


def soft_erode(img):
    p1 = -F.max_pool2d(-img, (3, 1), (1, 1), (1, 0))
    p2 = -F.max_pool2d(-img, (1, 3), (1, 1), (0, 1))
    return torch.min(p1, p2)


def soft_dilate(img):
    return F.max_pool2d(img, (3, 3), (1, 1), (1, 1))


def soft_open(img):
    return soft_dilate(soft_erode(img))


def soft_skeletonize(img, iters=5):
    img1 = soft_open(img)
    sq = F.relu(img - img1)
    ret = sq
    for i in range(iters):
        img = soft_erode(img)
        img1 = soft_open(img)
        sq = F.relu(img - img1)
        ret = torch.max(ret, sq)
    return ret


def cldice_loss(pred, target, iters=5, smooth=1e-5):
    """
    Compute centerline Dice loss for soft probabilities.
    pred, target: (B, H, W) or (B, 1, H, W) soft probabilities in range [0, 1]
    """
    if pred.dim() == 3:
        pred = pred.unsqueeze(1)
    if target.dim() == 3:
        target = target.unsqueeze(1)
        
    cl_pred = soft_skeletonize(pred, iters)
    cl_target = soft_skeletonize(target, iters)
    
    tprec = (torch.sum(cl_pred * target) + smooth) / (torch.sum(cl_pred) + smooth)
    tsens = (torch.sum(cl_target * pred) + smooth) / (torch.sum(cl_target) + smooth)
    
    cldice = 2.0 * (tprec * tsens) / (tprec + tsens)
    return 1.0 - cldice


class PatchDataset(Dataset):
    """Extract random patches from large images for training (with fast caching to prevent MemoryError and slow IO)"""
    
    def __init__(self, image_dir, label_dir, patch_size=512, patches_per_image=50):
        self.image_dir = Path(image_dir)
        self.label_dir = Path(label_dir)
        self.patch_size = patch_size
        self.patches_per_image = patches_per_image
        
        # Find all images that have corresponding label files
        self.image_paths = sorted(self.image_dir.glob("*.png"))
        self.valid_pairs = []
        for img_path in self.image_paths:
            label_path = self.label_dir / f"{img_path.stem}.npy"
            if label_path.exists():
                self.valid_pairs.append((img_path, label_path))
                
        print(f"Found {len(self.image_paths)} images, {len(self.valid_pairs)} valid pairs with annotations.")
        
        # Create cache directory
        self.cache_dir = self.image_dir.parent / f"cache_p{patch_size}_n{patches_per_image}"
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        
        # Pre-generate and cache all patches if not already cached
        self.cached_patches = []
        
        print("Initializing patch cache (generating crops)...")
        for pair_idx, (img_path, label_path) in enumerate(self.valid_pairs):
            # Check if all patches for this slide are already cached
            all_cached = True
            for patch_idx in range(self.patches_per_image):
                img_cache_path = self.cache_dir / f"img_{pair_idx}_{patch_idx}.png"
                lbl_cache_path = self.cache_dir / f"lbl_{pair_idx}_{patch_idx}.npy"
                if not (img_cache_path.exists() and lbl_cache_path.exists()):
                    all_cached = False
                    break
            
            if all_cached:
                # Add existing cache paths
                for patch_idx in range(self.patches_per_image):
                    img_cache_path = self.cache_dir / f"img_{pair_idx}_{patch_idx}.png"
                    lbl_cache_path = self.cache_dir / f"lbl_{pair_idx}_{patch_idx}.npy"
                    self.cached_patches.append((img_cache_path, lbl_cache_path))
                continue
                
            # If not cached, load once and crop all patches
            print(f"Caching crops for {img_path.name}...")
            with Image.open(img_path) as img:
                W, H = img.size
                label = np.load(label_path, mmap_mode='r')
                
                for patch_idx in range(self.patches_per_image):
                    img_cache_path = self.cache_dir / f"img_{pair_idx}_{patch_idx}.png"
                    lbl_cache_path = self.cache_dir / f"lbl_{pair_idx}_{patch_idx}.npy"
                    
                    # Choose random crop location
                    if H > patch_size and W > patch_size:
                        top = random.randint(0, H - patch_size)
                        left = random.randint(0, W - patch_size)
                    else:
                        top, left = 0, 0
                        patch_size = min(H, W)
                        
                    # Crop and save image patch
                    img_patch = img.crop((left, top, left + patch_size, top + patch_size)).convert("RGB")
                    img_patch.save(img_cache_path)
                    
                    # Crop and save label patch
                    lbl_patch = np.array(label[top:top+patch_size, left:left+patch_size])
                    np.save(lbl_cache_path, lbl_patch)
                    
                    self.cached_patches.append((img_cache_path, lbl_cache_path))
                    
        print(f"Cache ready with {len(self.cached_patches)} patches.")
        
    def __len__(self):
        return len(self.cached_patches)
    
    def __getitem__(self, idx):
        img_cache_path, lbl_cache_path = self.cached_patches[idx]
        
        # Load small cached patch (instant)
        with Image.open(img_cache_path) as img:
            img_patch = np.array(img)
            
        label_patch = np.load(lbl_cache_path)
        
        # Convert to tensor
        img_tensor = torch.from_numpy(img_patch).permute(2, 0, 1).float() / 255.0
        label_tensor = torch.from_numpy(label_patch).long()
        
        # Normalize (ImageNet stats)
        mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
        img_tensor = (img_tensor - mean) / std
        
        return img_tensor, label_tensor


class SimpleSegmentationHead(nn.Module):
    """Lightweight segmentation head"""
    
    def __init__(self, in_channels, num_classes=4):
        super().__init__()
        self.num_classes = num_classes
        
        # Simple decoder
        self.conv1 = nn.Conv2d(in_channels, 256, 3, padding=1)
        self.bn1 = nn.BatchNorm2d(256)
        self.conv2 = nn.Conv2d(256, 128, 3, padding=1)
        self.bn2 = nn.BatchNorm2d(128)
        self.classifier = nn.Conv2d(128, num_classes, 1)
    
    def forward(self, x):
        """
        Args:
            x: (B, C, H, W) feature map
        Returns:
            logits: (B, num_classes, H, W)
        """
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = self.classifier(x)
        return x


class DINOv3Segmentor(nn.Module):
    """HuggingFace pre-trained backbone + segmentation head"""
    
    def __init__(self, backbone_name="facebook/dinov2-small", num_classes=4, freeze_backbone=True):
        super().__init__()
        
        # Load from HuggingFace
        print(f"Loading HF backbone: {backbone_name}...")
        self.backbone = AutoModel.from_pretrained(backbone_name)
        
        # Freeze backbone
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False
            print("Backbone frozen")
        
        # Get feature dimension
        if hasattr(self.backbone.config, "hidden_size"):
            hidden_size = self.backbone.config.hidden_size
        elif hasattr(self.backbone.config, "embed_dim"):
            hidden_size = self.backbone.config.embed_dim
        else:
            hidden_size = 384  # Default for dinov2-small
            
        print(f"Feature dimension: {hidden_size}")
        
        # Segmentation head
        self.head = SimpleSegmentationHead(hidden_size, num_classes)
        
        # Patch size
        if hasattr(self.backbone.config, "patch_size"):
            self.patch_size = self.backbone.config.patch_size
        else:
            self.patch_size = 14  # Default for dinov2
            
        print(f"Patch size: {self.patch_size}")
    
    def forward(self, x):
        """
        Args:
            x: (B, 3, H, W) input image
        Returns:
            logits: (B, num_classes, H, W)
        """
        B, _, H, W = x.shape
        
        # HuggingFace model expects dimensions to be multiples of patch_size (e.g. 14 or 16).
        # We check and pad if necessary:
        pad_h = (self.patch_size - H % self.patch_size) % self.patch_size
        pad_w = (self.patch_size - W % self.patch_size) % self.patch_size
        if pad_h > 0 or pad_w > 0:
            x_padded = F.pad(x, (0, pad_w, 0, pad_h))
        else:
            x_padded = x
            
        # Extract features using HF
        with torch.no_grad():
            outputs = self.backbone(x_padded)
            
            # last_hidden_state has shape (B, N_tokens, C)
            if hasattr(outputs, "last_hidden_state"):
                tokens = outputs.last_hidden_state
            else:
                tokens = outputs[0]
                
            # Skip CLS token (the first token)
            patch_tokens = tokens[:, 1:, :]  # Shape: (B, N_patches, C)
        
        # Reshape to 2D feature map
        B, N, C = patch_tokens.shape
        h = (H + pad_h) // self.patch_size
        w = (W + pad_w) // self.patch_size
        feat_map = patch_tokens.permute(0, 2, 1).reshape(B, C, h, w)
        
        # Segment
        logits = self.head(feat_map)
        
        # Upsample to the ORIGINAL input size (H, W)
        logits = F.interpolate(logits, size=(H, W), mode="bilinear", align_corners=False)
        
        return logits


def compute_metrics(pred, target, num_classes=4):
    """Compute IoU and Dice per class"""
    ious = []
    dices = []
    
    for c in range(num_classes):
        pred_c = (pred == c)
        target_c = (target == c)
        
        intersection = (pred_c & target_c).sum().item()
        union = (pred_c | target_c).sum().item()
        
        if union > 0:
            iou = intersection / union
            dice = 2 * intersection / (pred_c.sum().item() + target_c.sum().item())
        else:
            iou = dice = 1.0
        
        ious.append(iou)
        dices.append(dice)
    
    return {
        "mean_iou": np.mean(ious),
        "mean_dice": np.mean(dices),
        "per_class_iou": ious,
        "per_class_dice": dices
    }


def train_epoch(model, dataloader, optimizer, device, num_classes=4, cldice_weight=0.0, skel_iters=5):
    model.train()
    total_loss = 0
    
    pbar = tqdm(dataloader, desc="Training")
    for images, labels in pbar:
        images = images.to(device)
        labels = labels.to(device)
        
        # Forward
        logits = model(images)
        
        # Loss
        loss_ce = F.cross_entropy(logits, labels)
        
        if cldice_weight > 0.0:
            # Get probabilities
            probs = F.softmax(logits, dim=1)
            
            # We want to enforce connectivity on:
            # 1. Media (class 1)
            # 2. Lumen (class 3)
            media_pred = probs[:, 1]
            media_target = (labels == 1).float()
            loss_cldice_media = cldice_loss(media_pred, media_target, iters=skel_iters)
            
            lumen_pred = probs[:, 3]
            lumen_target = (labels == 3).float()
            loss_cldice_lumen = cldice_loss(lumen_pred, lumen_target, iters=skel_iters)
            
            loss_cldice = loss_cldice_media + loss_cldice_lumen
            loss = (1.0 - cldice_weight) * loss_ce + cldice_weight * loss_cldice
        else:
            loss = loss_ce
        
        # Backward
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        pbar.set_postfix({"loss": f"{loss.item():.4f}"})
    
    return total_loss / len(dataloader)


@torch.no_grad()
def evaluate(model, dataloader, device, num_classes=4):
    model.eval()
    all_metrics = []
    
    for images, labels in tqdm(dataloader, desc="Evaluating"):
        images = images.to(device)
        labels = labels.to(device)
        
        # Forward
        logits = model(images)
        pred = logits.argmax(dim=1)
        
        # Metrics
        for i in range(pred.shape[0]):
            metrics = compute_metrics(pred[i].cpu(), labels[i].cpu(), num_classes)
            all_metrics.append(metrics)
    
    # Average
    mean_iou = np.mean([m["mean_iou"] for m in all_metrics])
    mean_dice = np.mean([m["mean_dice"] for m in all_metrics])
    
    # Per-class
    per_class_iou = np.mean([m["per_class_iou"] for m in all_metrics], axis=0)
    
    return {
        "mean_iou": mean_iou,
        "mean_dice": mean_dice,
        "per_class_iou": per_class_iou.tolist()
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_dir", type=str, default="output/clear_kmeans_train/images")
    parser.add_argument("--label_dir", type=str, default="output/clear_kmeans_train/labels")
    parser.add_argument("--backbone", type=str, default="facebook/dinov2-small", 
                       help="Hugging Face model ID, e.g. facebook/dinov2-small, facebook/dinov2-base")
    parser.add_argument("--num_classes", type=int, default=5)
    parser.add_argument("--patch_size", type=int, default=512)
    parser.add_argument("--patches_per_image", type=int, default=50)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--output_dir", type=str, default="output/segmentation_baseline")
    parser.add_argument("--cldice_weight", type=float, default=0.5,
                        help="Weight for clDice topological loss (0.0 to disable)")
    parser.add_argument("--skel_iters", type=int, default=5,
                        help="Number of iterations for soft skeletonization")
    args = parser.parse_args()
    
    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Dataset
    dataset = PatchDataset(
        args.image_dir, 
        args.label_dir, 
        patch_size=args.patch_size,
        patches_per_image=args.patches_per_image
    )
    
    # Split train/val (80/20)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(
        dataset, [train_size, val_size],
        generator=torch.Generator().manual_seed(42)
    )
    
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=0)
    
    print(f"Train patches: {len(train_dataset)}, Val patches: {len(val_dataset)}")
    
    # Model
    model = DINOv3Segmentor(args.backbone, args.num_classes, freeze_backbone=True).to(device)
    
    # Optimizer (only head parameters)
    optimizer = torch.optim.Adam(model.head.parameters(), lr=args.lr)
    
    # Training loop
    best_iou = 0
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    history = {"train_loss": [], "val_iou": [], "val_dice": []}
    
    for epoch in range(args.epochs):
        print(f"\nEpoch {epoch+1}/{args.epochs}")
        
        # Train
        train_loss = train_epoch(model, train_loader, optimizer, device, args.num_classes,
                                 cldice_weight=args.cldice_weight, skel_iters=args.skel_iters)
        print(f"Train Loss: {train_loss:.4f}")
        history["train_loss"].append(train_loss)
        
        # Validate
        val_metrics = evaluate(model, val_loader, device, args.num_classes)
        print(f"Val IoU: {val_metrics['mean_iou']:.4f}, Val Dice: {val_metrics['mean_dice']:.4f}")
        print(f"Per-class IoU: {[f'{x:.3f}' for x in val_metrics['per_class_iou']]}")
        history["val_iou"].append(val_metrics['mean_iou'])
        history["val_dice"].append(val_metrics['mean_dice'])
        
        # Save best
        if val_metrics['mean_iou'] > best_iou:
            best_iou = val_metrics['mean_iou']
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'metrics': val_metrics,
            }, output_dir / "best_model.pth")
            print(f"Saved best model (IoU: {best_iou:.4f})")
    
    # Plot training curves
    plt.figure(figsize=(12, 4))
    
    plt.subplot(131)
    plt.plot(history["train_loss"])
    plt.title("Training Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.grid(True)
    
    plt.subplot(132)
    plt.plot(history["val_iou"])
    plt.title("Validation IoU")
    plt.xlabel("Epoch")
    plt.ylabel("IoU")
    plt.grid(True)
    
    plt.subplot(133)
    plt.plot(history["val_dice"])
    plt.title("Validation Dice")
    plt.xlabel("Epoch")
    plt.ylabel("Dice")
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(output_dir / "training_curves.png", dpi=150)
    print(f"\nTraining complete! Best IoU: {best_iou:.4f}")
    print(f"Results saved to: {output_dir}")


if __name__ == "__main__":
    main()
