"""
Topology Enforcement for Coronary Artery Segmentation

This script implements and tests different topology constraint methods:
1. Morphological post-processing (simple, fast)
2. Hierarchical prediction (requires retraining)
3. Topology violation measurement

Start with Method 1 - it works with your existing baseline model!
"""

import numpy as np
from scipy.ndimage import binary_dilation, binary_erosion, binary_fill_holes
from scipy.ndimage import label as connected_components
import matplotlib.pyplot as plt
from pathlib import Path
from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def enforce_topology_morphological(mask, dilation_iters=3):
    """
    Method 1: Morphological post-processing
    
    Enforces nested structure: Background ⊃ Media ⊃ Intima ⊃ Lumen
    
    Args:
        mask: (H, W) numpy array with values 0=bg, 1=media, 2=intima, 3=lumen
        dilation_iters: How many pixels to dilate for containment check
    
    Returns:
        corrected_mask: (H, W) numpy array with topology violations fixed
    """
    corrected = mask.copy()
    
    # Extract each layer
    lumen = (mask == 3)
    intima = (mask == 2)
    media = (mask == 1)
    
    # Fix 1: Lumen must be inside Intima
    # Dilate intima to create a "safe zone"
    intima_dilated = binary_dilation(intima, iterations=dilation_iters)
    
    # Find lumen pixels outside the safe zone
    invalid_lumen = lumen & ~intima_dilated
    
    # Reassign invalid lumen to intima
    corrected[invalid_lumen] = 2
    
    # Update lumen mask after correction
    lumen = (corrected == 3)
    
    # Fix 2: Intima must be inside Media
    media_dilated = binary_dilation(media, iterations=dilation_iters)
    
    # Find intima pixels outside media
    invalid_intima = (corrected == 2) & ~media_dilated
    
    # Reassign invalid intima to media
    corrected[invalid_intima] = 1
    
    # Optional: Fill holes in each layer (makes segmentation cleaner)
    for class_id in [1, 2, 3]:
        class_mask = (corrected == class_id)
        if class_mask.any():
            filled = binary_fill_holes(class_mask)
            corrected[filled] = class_id
    
    return corrected


def measure_topology_violations(mask, dilation_iters=3):
    """
    Measure how many pixels violate the nesting constraint
    
    Returns:
        dict with violation statistics
    """
    lumen = (mask == 3)
    intima = (mask == 2)
    media = (mask == 1)
    
    # Violation 1: Lumen outside intima
    intima_dilated = binary_dilation(intima, iterations=dilation_iters)
    lumen_violations = (lumen & ~intima_dilated).sum()
    
    # Violation 2: Intima outside media
    media_dilated = binary_dilation(media, iterations=dilation_iters)
    intima_violations = (intima & ~media_dilated).sum()
    
    total_violations = lumen_violations + intima_violations
    total_pixels = mask.size
    
    # Additional topology metrics
    # Count connected components (should be 1 per class ideally)
    lumen_components, n_lumen = connected_components(lumen)
    intima_components, n_intima = connected_components(intima)
    media_components, n_media = connected_components(media)
    
    return {
        "total_violations": int(total_violations),
        "violation_rate": float(total_violations / total_pixels),
        "lumen_violations": int(lumen_violations),
        "intima_violations": int(intima_violations),
        "n_lumen_components": int(n_lumen),
        "n_intima_components": int(n_intima),
        "n_media_components": int(n_media),
    }


def visualize_topology_correction(original_mask, corrected_mask, save_path=None):
    """
    Visualize the effect of topology correction
    """
    # Compute violations
    orig_violations = measure_topology_violations(original_mask)
    corr_violations = measure_topology_violations(corrected_mask)
    
    # Find pixels that were changed
    changed = (original_mask != corrected_mask)
    
    # Create visualization
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Row 1: Original
    axes[0, 0].imshow(original_mask, cmap="jet", vmin=0, vmax=3)
    axes[0, 0].set_title(f"Original Segmentation\nViolations: {orig_violations['total_violations']:,} pixels ({orig_violations['violation_rate']:.2%})", 
                         fontsize=12)
    axes[0, 0].axis("off")
    
    axes[0, 1].imshow(corrected_mask, cmap="jet", vmin=0, vmax=3)
    axes[0, 1].set_title(f"Topology-Corrected\nViolations: {corr_violations['total_violations']:,} pixels ({corr_violations['violation_rate']:.2%})", 
                         fontsize=12)
    axes[0, 1].axis("off")
    
    axes[0, 2].imshow(changed, cmap="Reds")
    axes[0, 2].set_title(f"Changed Pixels\n{changed.sum():,} pixels modified", fontsize=12)
    axes[0, 2].axis("off")
    
    # Row 2: Per-class analysis
    class_names = ["Background", "Media", "Intima", "Lumen"]
    
    # Show violation locations
    lumen = (original_mask == 3)
    intima = (original_mask == 2)
    intima_dilated = binary_dilation(intima, iterations=3)
    lumen_violations = lumen & ~intima_dilated
    
    axes[1, 0].imshow(original_mask, cmap="gray", alpha=0.3)
    axes[1, 0].imshow(lumen_violations, cmap="Reds", alpha=0.7)
    axes[1, 0].set_title(f"Lumen Violations\n{lumen_violations.sum():,} pixels", fontsize=12)
    axes[1, 0].axis("off")
    
    # Show connected components
    axes[1, 1].axis("off")
    metrics_text = "Topology Metrics:\n\n"
    metrics_text += "BEFORE Correction:\n"
    metrics_text += f"  Lumen violations:  {orig_violations['lumen_violations']:8,}\n"
    metrics_text += f"  Intima violations: {orig_violations['intima_violations']:8,}\n"
    metrics_text += f"  Total violations:  {orig_violations['total_violations']:8,}\n"
    metrics_text += f"  Violation rate:    {orig_violations['violation_rate']:8.2%}\n\n"
    metrics_text += "AFTER Correction:\n"
    metrics_text += f"  Lumen violations:  {corr_violations['lumen_violations']:8,}\n"
    metrics_text += f"  Intima violations: {corr_violations['intima_violations']:8,}\n"
    metrics_text += f"  Total violations:  {corr_violations['total_violations']:8,}\n"
    metrics_text += f"  Violation rate:    {corr_violations['violation_rate']:8.2%}\n\n"
    metrics_text += f"Improvement: {(1 - corr_violations['violation_rate']/max(orig_violations['violation_rate'], 1e-10)):.1%}"
    
    axes[1, 1].text(0.1, 0.5, metrics_text, fontsize=11, family="monospace",
                    verticalalignment="center")
    
    # Connected components
    axes[1, 2].axis("off")
    comp_text = "Connected Components:\n\n"
    comp_text += "BEFORE:\n"
    comp_text += f"  Media:  {orig_violations['n_media_components']}\n"
    comp_text += f"  Intima: {orig_violations['n_intima_components']}\n"
    comp_text += f"  Lumen:  {orig_violations['n_lumen_components']}\n\n"
    comp_text += "AFTER:\n"
    comp_text += f"  Media:  {corr_violations['n_media_components']}\n"
    comp_text += f"  Intima: {corr_violations['n_intima_components']}\n"
    comp_text += f"  Lumen:  {corr_violations['n_lumen_components']}\n\n"
    comp_text += "(Ideally 1 per class)"
    
    axes[1, 2].text(0.1, 0.5, comp_text, fontsize=11, family="monospace",
                    verticalalignment="center")
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved to {save_path}")
    else:
        plt.show()
    
    plt.close()
    
    return orig_violations, corr_violations


def test_on_dataset(label_dir, output_dir):
    """
    Test topology enforcement on all labels in dataset
    """
    label_dir = Path(label_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    label_files = sorted(label_dir.glob("*.npy"))
    
    print("="*60)
    print("TOPOLOGY ENFORCEMENT TEST")
    print("="*60)
    print(f"\nFound {len(label_files)} label files\n")
    
    all_results = []
    
    for label_path in label_files:
        name = label_path.stem
        print(f"\nProcessing {name}...")
        
        # Load mask
        mask = np.load(label_path)
        
        # Apply topology correction
        corrected = enforce_topology_morphological(mask, dilation_iters=3)
        
        # Visualize
        save_path = output_dir / f"{name}_topology_correction.png"
        orig_violations, corr_violations = visualize_topology_correction(
            mask, corrected, save_path
        )
        
        # Save corrected mask
        corrected_path = output_dir / f"{name}_corrected.npy"
        np.save(corrected_path, corrected)
        
        # Store results
        all_results.append({
            "name": name,
            "original": orig_violations,
            "corrected": corr_violations
        })
        
        print(f"  Original violations: {orig_violations['total_violations']:,} ({orig_violations['violation_rate']:.2%})")
        print(f"  Corrected violations: {corr_violations['total_violations']:,} ({corr_violations['violation_rate']:.2%})")
        print(f"  Improvement: {(1 - corr_violations['violation_rate']/max(orig_violations['violation_rate'], 1e-10)):.1%}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    total_orig_violations = sum(r["original"]["total_violations"] for r in all_results)
    total_corr_violations = sum(r["corrected"]["total_violations"] for r in all_results)
    total_pixels = sum(r["original"]["total_violations"] + r["corrected"]["total_violations"] for r in all_results)
    
    avg_orig_rate = np.mean([r["original"]["violation_rate"] for r in all_results])
    avg_corr_rate = np.mean([r["corrected"]["violation_rate"] for r in all_results])
    
    print(f"\nTotal violations BEFORE: {total_orig_violations:,}")
    print(f"Total violations AFTER:  {total_corr_violations:,}")
    print(f"Average violation rate BEFORE: {avg_orig_rate:.2%}")
    print(f"Average violation rate AFTER:  {avg_corr_rate:.2%}")
    print(f"Overall improvement: {(1 - avg_corr_rate/max(avg_orig_rate, 1e-10)):.1%}")
    
    print(f"\nResults saved to: {output_dir}")
    
    return all_results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test topology enforcement on segmentation masks")
    parser.add_argument("--label_dir", type=str, 
                       default="output/coronary-data-2/train_data/labels",
                       help="Directory containing .npy label files")
    parser.add_argument("--output_dir", type=str,
                       default="output/topology_enforcement",
                       help="Where to save results")
    args = parser.parse_args()
    
    results = test_on_dataset(args.label_dir, args.output_dir)
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("\n1. Check visualizations in:", args.output_dir)
    print("2. Use corrected masks for training:")
    print(f"   - Original masks: {args.label_dir}")
    print(f"   - Corrected masks: {args.output_dir}/*_corrected.npy")
    print("\n3. Compare model performance:")
    print("   - Train on original masks")
    print("   - Train on corrected masks")
    print("   - Which gives better topology correctness?")
    print("\n4. Add to your paper:")
    print("   - 'Post-processing reduces violations by X%'")
    print("   - Show before/after visualizations")
