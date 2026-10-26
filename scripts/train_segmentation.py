"""
Train a segmentation head on top of frozen DINOv3 features.
This is the baseline before adding topology constraints.
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

from transformers import AutoImageProcessor, AutoModel


class SegmentationDataset(Dataset):
    """Load image + label pairs from Phase 1 output"""
    
    def __init__(self, image_dir, label_dir, processor, max_samples=None):
        self.image_dir = Path(image_dir)
        self.label_dir = Path(label_dir)
        self.processor = processor
        
        # Find all images
        self.image_paths = sorted(self.image_dir.glob("*.png"))
        if max_samples:
            self.image_paths = self.image_paths[:max_samples]
        
        print(f"Found {len(self.image_paths)} training samples")
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        label_path = self.label_dir / f"{img_path.stem}.npy"
        
        # Load image
        image = Image.open(img_path).convert("RGB")
        
        # Load label
        label = np.load(label_path).astype(np.int64)
        
        # Process image for DINOv3
        inputs = self.processor(images=image, return_tensors="pt")
        pixel_values = inputs["pixel_values"][0]  # (3, H, W)
        
        # Resize label to match feature map size (will be 1/16 of input for patch_size=16)
        # For now, keep original size and we'll handle in model
        label_tensor = torch.from_numpy(label)
        
        return {
            "pixel_values": pixel_values,
            "labels": label_tensor,
            "image_size": (image.height, image.width)
        }


class LinearSegmentationHead(nn.Module):
    """Simple linear head for segmentation"""
    
    def __init__(self, in_channels, num_classes=4, patch_size=16):
        super().__init__()
        self.patch_size = patch_size
        self.num_classes = num_classes
        
        # Simple 1x1 conv to map features to classes
        self.classifier = nn.Conv2d(in_channels, num_classes, kernel_size=1)
    
    def forward(self, features, target_size):
        """
        Args:
            features: (B, N, C) patch tokens from DINOv3
            target_size: (H, W) original image size
        Returns:
            logits: (B, num_classes, H, W)
        """
        B, N, C = features.shape
        
        # Reshape to 2D feature map
        # Assume square grid: N = h*w
        h = w = int(np.sqrt(N))
        assert h * w == N, f"Expected square grid, got N={N}"
        
        feat_map = features.permute(0, 2, 1).reshape(B, C, h, w)  # (B, C, h, w)
        
        # Classify
        logits = self.classifier(feat_map)  # (B, num_classes, h, w)
        
        # Upsample to target size
        logits = F.interpolate(logits, size=target_size, mode="bilinear", align_corners=False)
        
        return logits


class DINOv3Segmentor(nn.Module):
    """DINOv3 backbone + segmentation head"""
    
    def __init__(self, model_id, num_classes=4, freeze_backbone=True):
        super().__init__()
        
        # Load DINOv3
        self.backbone = AutoModel.from_pretrained(model_id)
        
        # Freeze backbone
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False
        
        # Get feature dimension
        hidden_size = self.backbone.config.hidden_size
        
        # Segmentation head
        self.head = LinearSegmentationHead(hidden_size, num_classes)
    
    def forward(self, pixel_values, target_size):
        """
        Args:
            pixel_values: (B, 3, H, W)
            target_size: (H, W) for output
        Returns:
            logits: (B, num_classes, H, W)
        """
        # Extract features
        outputs = self.backbone(pixel_values, output_hidden_states=False)
        
        # Get patch tokens (without CLS token)
        if hasattr(outputs, 'last_hidden_state'):
            features = outputs.last_hidden_state[:, 1:, :]  # (B, N, C) - skip CLS
        else:
            raise ValueError("Could not extract patch tokens")
        
        # Segment
        logits = self.head(features, target_size)
        
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
            iou = dice = 1.0  # Perfect if class not present
        
        ious.append(iou)
        dices.append(dice)
    
    return {
        "mean_iou": np.mean(ious),
        "mean_dice": np.mean(dices),
        "per_class_iou": ious,
        "per_class_dice": dices
    }


def train_epoch(model, dataloader, optimizer, device, num_classes=4):
    model.train()
    total_loss = 0
    
    for batch in tqdm(dataloader, desc="Training"):
        pixel_values = batch["pixel_values"].to(device)
        labels = batch["labels"].to(device)
        target_size = batch["image_size"][0]  # Assume same size in batch
        
        # Forward
        logits = model(pixel_values, target_size=(target_size[0].item(), target_size[1].item()))
        
        # Loss
        loss = F.cross_entropy(logits, labels, ignore_index=-1)
        
        # Backward
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    
    return total_loss / len(dataloader)


@torch.no_grad()
def evaluate(model, dataloader, device, num_classes=4):
    model.eval()
    all_metrics = []
    
    for batch in tqdm(dataloader, desc="Evaluating"):
        pixel_values = batch["pixel_values"].to(device)
        labels = batch["labels"].to(device)
        target_size = batch["image_size"][0]
        
        # Forward
        logits = model(pixel_values, target_size=(target_size[0].item(), target_size[1].item()))
        pred = logits.argmax(dim=1)
        
        # Metrics
        for i in range(pred.shape[0]):
            metrics = compute_metrics(pred[i].cpu(), labels[i].cpu(), num_classes)
            all_metrics.append(metrics)
    
    # Average
    mean_iou = np.mean([m["mean_iou"] for m in all_metrics])
    mean_dice = np.mean([m["mean_dice"] for m in all_metrics])
    
    return {"mean_iou": mean_iou, "mean_dice": mean_dice}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_dir", type=str, required=True)
    parser.add_argument("--label_dir", type=str, required=True)
    parser.add_argument("--model_id", type=str, default="facebook/dinov3-vitl16-pretrain-lvd1689m")
    parser.add_argument("--num_classes", type=int, default=4)
    parser.add_argument("--batch_size", type=int, default=2)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--output_dir", type=str, default="output/segmentation")
    args = parser.parse_args()
    
    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Load processor
    processor = AutoImageProcessor.from_pretrained(args.model_id)
    
    # Dataset
    dataset = SegmentationDataset(args.image_dir, args.label_dir, processor)
    
    # Split train/val (80/20)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=0)
    
    print(f"Train: {len(train_dataset)}, Val: {len(val_dataset)}")
    
    # Model
    model = DINOv3Segmentor(args.model_id, args.num_classes, freeze_backbone=True).to(device)
    
    # Optimizer (only head parameters)
    optimizer = torch.optim.Adam(model.head.parameters(), lr=args.lr)
    
    # Training loop
    best_iou = 0
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for epoch in range(args.epochs):
        print(f"\nEpoch {epoch+1}/{args.epochs}")
        
        # Train
        train_loss = train_epoch(model, train_loader, optimizer, device, args.num_classes)
        print(f"Train Loss: {train_loss:.4f}")
        
        # Validate
        val_metrics = evaluate(model, val_loader, device, args.num_classes)
        print(f"Val IoU: {val_metrics['mean_iou']:.4f}, Val Dice: {val_metrics['mean_dice']:.4f}")
        
        # Save best
        if val_metrics['mean_iou'] > best_iou:
            best_iou = val_metrics['mean_iou']
            torch.save(model.state_dict(), output_dir / "best_model.pth")
            print(f"Saved best model (IoU: {best_iou:.4f})")
    
    print(f"\nTraining complete! Best IoU: {best_iou:.4f}")


if __name__ == "__main__":
    main()
