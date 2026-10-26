import argparse
from pathlib import Path
import json
from datetime import datetime

import numpy as np
from PIL import Image, PngImagePlugin
import torch
import torch.nn.functional as F
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from tqdm import tqdm

# Fix for large PNG files
PngImagePlugin.MAX_TEXT_CHUNK = 100 * (1024**2)  # 100MB

try:
    from transformers import AutoImageProcessor, AutoModel
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("⚠️  transformers not installed. Run: pip install transformers")


def load_model_hf(model_name: str, device: str, image_size: int):
    """Load model from Hugging Face and configure processor to use image_size."""
    if not HF_AVAILABLE:
        raise ImportError("Please install transformers: pip install transformers")

    print(f"📥 Loading from Hugging Face: {model_name}")
    processor = AutoImageProcessor.from_pretrained(model_name)

    # Force processor to use the requested resolution (attempt best-effort across versions)
    if hasattr(processor, "do_resize"):
        processor.do_resize = True
    if hasattr(processor, "size"):
        # most common format
        processor.size = {"height": image_size, "width": image_size}
    if hasattr(processor, "do_center_crop"):
        processor.do_center_crop = False
    if hasattr(processor, "crop_size"):
        processor.crop_size = {"height": image_size, "width": image_size}

    model = AutoModel.from_pretrained(model_name)
    model = model.to(device)
    model.eval()
    return model, processor


@torch.no_grad()
def extract_features_hf(model, processor, pil_img, device, image_size: int):
    """
    Extract patch features and return:
      features: (N_patches, dim)
      patch_h, patch_w
      proc_h, proc_w (actual tensor size fed into the model)
    """
    # Try to explicitly pass resize/crop settings in call (works for many HF processors)
    try:
        inputs = processor(
            images=pil_img,
            return_tensors="pt",
            do_resize=True,
            size={"height": image_size, "width": image_size},
            do_center_crop=False,
        ).to(device)
    except TypeError:
        # Fallback: rely on processor attributes set in load_model_hf()
        inputs = processor(images=pil_img, return_tensors="pt").to(device)

    outputs = model(**inputs)

    # Get patch tokens (exclude CLS token)
    if hasattr(outputs, "last_hidden_state"):
        patch_tokens = outputs.last_hidden_state[:, 1:, :]  # (B, N, D)
    else:
        patch_tokens = outputs[0][:, 1:, :]

    features = patch_tokens[0]  # (N, D)

    proc_h, proc_w = inputs["pixel_values"].shape[-2:]
    ps = int(getattr(model.config, "patch_size", 14))  # DINOv2 usually 14

    patch_h = proc_h // ps
    patch_w = proc_w // ps

    return features, patch_h, patch_w, proc_h, proc_w


def create_segmentation_map(features, n_clusters=5):
    kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=42, batch_size=4096)
    feats_norm = F.normalize(features.float(), dim=-1).cpu().numpy()
    labels = kmeans.fit_predict(feats_norm)
    return labels, kmeans


def create_pca_visualization(features):
    pca = PCA(n_components=3)
    feats_np = features.float().cpu().numpy()
    pca_result = pca.fit_transform(feats_np)
    pca_result = (pca_result - pca_result.min()) / (pca_result.max() - pca_result.min() + 1e-12)
    return pca_result


def create_heatmap(features, patch_h, patch_w, output_size_hw):
    feat_mean = features.mean(dim=-1).float().cpu().numpy()
    feat_map = feat_mean.reshape(patch_h, patch_w)
    feat_map = (feat_map - feat_map.min()) / (feat_map.max() - feat_map.min() + 1e-12)

    heatmap_t = torch.from_numpy(feat_map)[None, None].float()
    heatmap = F.interpolate(heatmap_t, size=output_size_hw, mode="bilinear", align_corners=False)[0, 0].numpy()

    try:
        cmap = plt.get_cmap("jet")
        heatmap_colored = (cmap(heatmap)[..., :3] * 255).astype(np.uint8)
    except Exception:
        heatmap_colored = np.zeros((*heatmap.shape, 3), dtype=np.uint8)
        heatmap_colored[..., 0] = (heatmap * 255).astype(np.uint8)          # red
        heatmap_colored[..., 2] = ((1 - heatmap) * 255).astype(np.uint8)    # blue

    return Image.fromarray(heatmap_colored)


def save_results_html(results, output_dir: Path):
    # IMPORTANT: escape CSS braces because we later use .format(**metadata)
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <title>DINOv2 Medical Image Analysis Results</title>
        <style>
            body {{ font-family: Arial; margin: 20px; background: #f5f5f5; }}
            h1 {{ color: #333; }}
            .container {{ max-width: 1400px; margin: auto; }}
            .image-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }}
            .image-card {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .image-card img {{ width: 100%; border-radius: 4px; }}
            .image-card h3 {{ margin: 10px 0 5px 0; color: #555; }}
            .stats {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .stat-item {{ display: inline-block; margin: 10px 20px; }}
            .stat-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
            .stat-label {{ color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔬 DINOv2 Medical Image Analysis Results</h1>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value">{total_images}</div>
                    <div class="stat-label">Images Analyzed</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{model_name}</div>
                    <div class="stat-label">Model Used</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{timestamp}</div>
                    <div class="stat-label">Analysis Date</div>
                </div>
            </div>
    """

    for img_result in results["images"]:
        html += f"""
            <h2>📄 {img_result['name']}</h2>
            <div class="image-grid">
                <div class="image-card">
                    <h3>Original Image</h3>
                    <img src="{img_result['original']}" />
                </div>
                <div class="image-card">
                    <h3>Segmentation ({img_result['clusters']} clusters)</h3>
                    <img src="{img_result['segmentation']}" />
                </div>
                <div class="image-card">
                    <h3>PCA Visualization</h3>
                    <img src="{img_result['pca']}" />
                </div>
                <div class="image-card">
                    <h3>Feature Heatmap</h3>
                    <img src="{img_result['heatmap']}" />
                </div>
            </div>
        """

    html += """
        </div>
    </body>
    </html>
    """

    html_path = output_dir / "results.html"
    html_path.write_text(html.format(**results["metadata"]), encoding="utf-8")
    return html_path


def main():
    parser = argparse.ArgumentParser(description="DINOv2 Medical Image Analyzer (Hugging Face)")
    parser.add_argument("--images", type=str, required=True, help="Input images folder")
    parser.add_argument("--output", type=str, default="output/analysis", help="Output folder")
    parser.add_argument(
        "--model",
        type=str,
        default="facebook/dinov2-small",
        help="HF model: facebook/dinov2-small, facebook/dinov2-base, facebook/dinov2-large",
    )
    parser.add_argument("--clusters", type=int, default=5, help="Number of segmentation clusters")
    parser.add_argument("--size", type=int, default=518, help="Processing image size (518 for DINOv2)")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()

    img_dir = Path(args.images)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    img_paths = []
    for ext in ["*.png", "*.jpg", "*.jpeg", "*.tif", "*.tiff"]:
        img_paths.extend(img_dir.glob(ext))
    img_paths = sorted(img_paths)

    if not img_paths:
        raise FileNotFoundError(f"No images found in {img_dir}")

    print(f"🚀 Loading model: {args.model}")
    model, processor = load_model_hf(args.model, args.device, args.size)

    results = {
        "metadata": {
            "total_images": len(img_paths),
            "model_name": args.model,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
        "images": [],
    }

    for img_path in tqdm(img_paths, desc="🔬 Analyzing images"):
        pil_img = Image.open(img_path).convert("RGB")

        # Extract features (processor handles resizing to args.size)
        features, patch_h, patch_w, proc_h, proc_w = extract_features_hf(
            model, processor, pil_img, args.device, args.size
        )

        n_patches = features.shape[0]
        print(
            f"  Processed tensor: {proc_h}x{proc_w} | patch grid: {patch_h}x{patch_w} | "
            f"patches: {n_patches} | feat dim: {features.shape[1]}"
        )

        # Output visualization size (fixed to args.size for consistent outputs)
        out_hw = (args.size, args.size)

        stem = img_path.stem
        img_out_dir = out_dir / stem
        img_out_dir.mkdir(exist_ok=True)

        # Save original
        orig_path = img_out_dir / "original.png"
        pil_img.save(orig_path)

        # Segmentation
        labels, _ = create_segmentation_map(features, args.clusters)
        if labels.size != patch_h * patch_w:
            raise ValueError(
                f"Label count ({labels.size}) != patch_h*patch_w ({patch_h*patch_w}). "
                f"Processed image was {proc_h}x{proc_w}, patch_size={getattr(model.config,'patch_size',None)}"
            )

        seg_map = labels.reshape(patch_h, patch_w).astype(np.uint8)
        seg_t = torch.from_numpy(seg_map)[None, None].float()
        seg_up = F.interpolate(seg_t, size=out_hw, mode="nearest")[0, 0].numpy()

        cmap = plt.get_cmap("tab20", args.clusters)
        seg_colored = (cmap(seg_up / max(args.clusters, 1))[..., :3] * 255).astype(np.uint8)
        seg_img = Image.fromarray(seg_colored)
        seg_path = img_out_dir / "segmentation.png"
        seg_img.save(seg_path)

        # PCA visualization
        pca_result = create_pca_visualization(features)  # (N,3)
        pca_map = pca_result.reshape(patch_h, patch_w, 3)
        pca_t = torch.from_numpy(pca_map).permute(2, 0, 1)[None].float()
        pca_up = F.interpolate(pca_t, size=out_hw, mode="bilinear", align_corners=False)[0].permute(1, 2, 0).numpy()
        pca_img = Image.fromarray((np.clip(pca_up, 0, 1) * 255).astype(np.uint8))
        pca_path = img_out_dir / "pca.png"
        pca_img.save(pca_path)

        # Heatmap
        heatmap = create_heatmap(features, patch_h, patch_w, out_hw)
        heatmap_path = img_out_dir / "heatmap.png"
        heatmap.save(heatmap_path)

        results["images"].append(
            {
                "name": stem,
                "original": f"{stem}/original.png",
                "segmentation": f"{stem}/segmentation.png",
                "pca": f"{stem}/pca.png",
                "heatmap": f"{stem}/heatmap.png",
                "clusters": args.clusters,
            }
        )

    # Save HTML report
    html_path = save_results_html(results, out_dir)

    # Save JSON summary
    json_path = out_dir / "summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Analysis complete!")
    print(f"📊 Results: {out_dir.resolve()}")
    print(f"🌐 Open: {html_path.resolve()}")


if __name__ == "__main__":
    main()