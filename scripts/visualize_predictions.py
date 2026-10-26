"""
Visualize segmentation predictions from trained model.
Run this after training to see results.
"""

import argparse
import torch
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from pathlib import Path
import sys

Image.MAX_IMAGE_PIXELS = None

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.train_baseline import DINOv3Segmentor


def visualize_prediction(model, image_path, label_path, device, save_path=None):
    """Visualize model prediction vs ground truth"""
    
    # Load image
    img = Image.open(image_path).convert("RGB")
    W, H = img.size
    
    # Resize for inference (too large otherwise)
    max_size = 1024
    if max(W, H) > max_size:
        scale = max_size / max(W, H)
        new_w, new_h = int(W * scale), int(H * scale)
    else:
        new_w, new_h = W, H
        
    # Ensure divisible by 16 (patch size)
    new_w = (new_w // 16) * 16
    new_h = (new_h // 16) * 16
    img_resized = img.resize((new_w, new_h), Image.BILINEAR)
    
    # Convert to tensor
    img_array = np.array(img_resized).astype(np.float32) / 255.0
    img_tensor = torch.from_numpy(img_array).permute(2, 0, 1)
    
    # Normalize
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
    img_tensor = (img_tensor - mean) / std
    img_tensor = img_tensor.unsqueeze(0).to(device)
    
    # Predict
    model.eval()
    with torch.no_grad():
        logits = model(img_tensor)
        pred = logits.argmax(dim=1)[0].cpu().numpy()
    
    # Load ground truth
    gt = np.load(label_path)
    
    # Resize GT to match prediction
    if gt.shape != pred.shape:
        from scipy.ndimage import zoom
        scale_h = pred.shape[0] / gt.shape[0]
        scale_w = pred.shape[1] / gt.shape[1]
        gt_resized = zoom(gt, (scale_h, scale_w), order=0)
    else:
        gt_resized = gt
    
    # Compute metrics
    correct = (pred == gt_resized).sum()
    total = pred.size
    accuracy = correct / total
    
    # Per-class IoU
    num_classes = model.head.classifier.out_channels if hasattr(model.head, "classifier") else 4
    class_names = ["Background", "Media", "Intima", "Lumen", "Extra"][:num_classes]
    if len(class_names) < num_classes:
        class_names.extend([f"Class_{i}" for i in range(len(class_names), num_classes)])
    ious = []
    for c in range(num_classes):
        pred_c = (pred == c)
        gt_c = (gt_resized == c)
        intersection = (pred_c & gt_c).sum()
        union = (pred_c | gt_c).sum()
        iou = intersection / union if union > 0 else 1.0
        ious.append(iou)
    
    # Visualize
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Row 1: Original, GT, Prediction
    axes[0, 0].imshow(img_resized)
    axes[0, 0].set_title("Original Image", fontsize=14)
    axes[0, 0].axis("off")
    
    axes[0, 1].imshow(gt_resized, cmap="jet", vmin=0, vmax=num_classes-1)
    axes[0, 1].set_title("Ground Truth (KMeans)", fontsize=14)
    axes[0, 1].axis("off")
    
    axes[0, 2].imshow(pred, cmap="jet", vmin=0, vmax=num_classes-1)
    axes[0, 2].set_title(f"Prediction (Acc: {accuracy:.2%})", fontsize=14)
    axes[0, 2].axis("off")
    
    # Row 2: Overlays and metrics
    axes[1, 0].imshow(img_resized)
    axes[1, 0].imshow(gt_resized, alpha=0.5, cmap="jet", vmin=0, vmax=num_classes-1)
    axes[1, 0].set_title("GT Overlay", fontsize=14)
    axes[1, 0].axis("off")
    
    axes[1, 1].imshow(img_resized)
    axes[1, 1].imshow(pred, alpha=0.5, cmap="jet", vmin=0, vmax=num_classes-1)
    axes[1, 1].set_title("Prediction Overlay", fontsize=14)
    axes[1, 1].axis("off")
    
    # Metrics text
    axes[1, 2].axis("off")
    metrics_text = f"Overall Accuracy: {accuracy:.2%}\n\n"
    metrics_text += "Per-Class IoU:\n"
    for i, (name, iou) in enumerate(zip(class_names, ious)):
        metrics_text += f"  {i} ({name:10s}): {iou:.3f}\n"
    metrics_text += f"\nMean IoU: {np.mean(ious):.3f}"
    
    axes[1, 2].text(0.1, 0.5, metrics_text, fontsize=12, family="monospace",
                    verticalalignment="center")
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved to {save_path}")
    else:
        plt.show()
    
    plt.close()
    
    return {
        "accuracy": accuracy,
        "mean_iou": np.mean(ious),
        "per_class_iou": ious
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=str, default="output/segmentation_baseline/best_model.pth")
    parser.add_argument("--image_dir", type=str, default="output/clear_kmeans_train/images")
    parser.add_argument("--label_dir", type=str, default="output/clear_kmeans_train/labels")
    parser.add_argument("--backbone", type=str, default="facebook/dinov2-small")
    parser.add_argument("--output_dir", type=str, default="output/visualizations")
    parser.add_argument("--device", type=str, default="cuda")
    args = parser.parse_args()
    
    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Load model
    print(f"Loading model checkpoint from {args.checkpoint}...")
    checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=False)
    state_dict = checkpoint['model_state_dict']
    
    # Dynamically detect num_classes from saved classifier bias shape
    num_classes = state_dict['head.classifier.bias'].shape[0] if 'head.classifier.bias' in state_dict else 4
    print(f"Detected {num_classes} classes from checkpoint.")
    
    model = DINOv3Segmentor(args.backbone, num_classes=num_classes, freeze_backbone=True)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    
    print(f"Model loaded. Checkpoint metrics: {checkpoint.get('metrics', 'N/A')}")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all images
    image_dir = Path(args.image_dir)
    label_dir = Path(args.label_dir)
    image_paths = sorted(image_dir.glob("*.png"))
    
    print(f"\nFound {len(image_paths)} images to visualize\n")
    
    # Visualize each
    all_metrics = []
    for img_path in image_paths:
        label_path = label_dir / f"{img_path.stem}.npy"
        
        if not label_path.exists():
            print(f"Skipping {img_path.name} (no label)")
            continue
        
        print(f"Processing {img_path.name}...")
        save_path = output_dir / f"{img_path.stem}_prediction.png"
        
        metrics = visualize_prediction(
            model, img_path, label_path, device, save_path
        )
        all_metrics.append(metrics)
        
        print(f"  Accuracy: {metrics['accuracy']:.2%}, Mean IoU: {metrics['mean_iou']:.3f}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    avg_acc = np.mean([m['accuracy'] for m in all_metrics])
    avg_iou = np.mean([m['mean_iou'] for m in all_metrics])
    print(f"Average Accuracy: {avg_acc:.2%}")
    print(f"Average Mean IoU: {avg_iou:.3f}")
    print(f"\nVisualizations saved to: {output_dir}")


if __name__ == "__main__":
    main()
