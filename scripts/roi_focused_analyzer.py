"""
ROI-focused medical image analyzer.

Uses GeoJSON annotations to crop artery ROIs from WSI/SVS slides, extracts
DINO-family features from each ROI, and creates unsupervised K-means/PCA
visualizations for thesis baseline analysis.
"""

import argparse
from pathlib import Path
import json
from datetime import datetime

import numpy as np
from PIL import Image, PngImagePlugin
import torch

# Fix for large PNG files
PngImagePlugin.MAX_TEXT_CHUNK = 100 * (1024**2)
import torch.nn.functional as F
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import PCA

# Fix matplotlib font issue
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from tqdm import tqdm
import openslide

try:
    from transformers import AutoImageProcessor, AutoModel
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("⚠️  transformers not installed. Run: pip install transformers")

from roi_utils import get_rois_from_geojson, get_corresponding_geojson


def load_model_hf(model_name: str, device: str):
    """Load model from Hugging Face."""
    if not HF_AVAILABLE:
        raise ImportError("Please install transformers: pip install transformers")

    print(f"📥 Loading from Hugging Face: {model_name}")
    processor = AutoImageProcessor.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.to(device)
    model.eval()
    return model, processor


@torch.no_grad()
def extract_features_hf(model, processor, pil_img, device):
    """Extract features using Hugging Face model."""
    inputs = processor(images=pil_img, return_tensors="pt").to(device)
    outputs = model(**inputs)

    if hasattr(outputs, "last_hidden_state"):
        features = outputs.last_hidden_state[:, 1:, :]
    else:
        features = outputs[0][:, 1:, :]

    return features[0]


def create_segmentation_map(features, n_clusters=5):
    kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=42, batch_size=4096)
    feats_norm = F.normalize(features.float(), dim=-1).cpu().numpy()
    labels = kmeans.fit_predict(feats_norm)
    return labels, kmeans


def create_pca_visualization(features):
    pca = PCA(n_components=3)
    feats_np = features.cpu().numpy()
    pca_result = pca.fit_transform(feats_np)

    pca_min = pca_result.min()
    pca_range = pca_result.max() - pca_min
    if pca_range > 0:
        pca_result = (pca_result - pca_min) / pca_range
    else:
        pca_result = np.zeros_like(pca_result)

    return pca_result


def create_heatmap(features, patch_h, patch_w, output_size):
    feat_mean = features.mean(dim=-1).cpu().numpy()
    feat_map = feat_mean.reshape(patch_h, patch_w)

    feat_min = feat_map.min()
    feat_range = feat_map.max() - feat_min
    if feat_range > 0:
        feat_map = (feat_map - feat_min) / feat_range
    else:
        feat_map = np.zeros_like(feat_map)

    heatmap_t = torch.from_numpy(feat_map)[None, None].float()
    heatmap = F.interpolate(
        heatmap_t,
        size=output_size,
        mode="bilinear"
    )[0, 0].numpy()

    try:
        cmap = plt.get_cmap("jet")
        heatmap_colored = (cmap(heatmap)[..., :3] * 255).astype(np.uint8)
    except Exception:
        heatmap_colored = np.zeros((*heatmap.shape, 3), dtype=np.uint8)
        heatmap_colored[..., 0] = (heatmap * 255).astype(np.uint8)
        heatmap_colored[..., 2] = ((1 - heatmap) * 255).astype(np.uint8)

    return Image.fromarray(heatmap_colored)


def extract_roi_from_wsi(wsi_path, roi, target_size=2048):
    """
    Extract ROI directly from WSI file at level 0.

    Args:
        wsi_path: Path to .svs file.
        roi: Dictionary with x_min, y_min, width, height.
        target_size: Maximum side length for the extracted region.

    Returns:
        PIL Image of the ROI.
    """
    slide = openslide.OpenSlide(str(wsi_path))
    try:
        location = (roi["x_min"], roi["y_min"])
        size = (roi["width"], roi["height"])

        roi_img = slide.read_region(location, 0, size).convert("RGB")

        if max(roi_img.size) > target_size:
            roi_img.thumbnail((target_size, target_size), Image.BICUBIC)
    finally:
        slide.close()

    return roi_img


def save_results_html(results, output_dir):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DINO ROI-Focused Analysis Results</title>
        <style>
            body { font-family: Arial; margin: 20px; background: #f5f5f5; }
            h1 { color: #333; }
            .container { max-width: 1400px; margin: auto; }
            .image-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
            .image-card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .image-card img { width: 100%; border-radius: 4px; }
            .image-card h3 { margin: 10px 0 5px 0; color: #555; }
            .stats { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
            .stat-item { display: inline-block; margin: 10px 20px; }
            .stat-value { font-size: 24px; font-weight: bold; color: #007bff; }
            .stat-label { color: #666; }
            .roi-info { background: #e3f2fd; padding: 10px; border-radius: 4px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔬 DINO ROI-Focused Analysis Results</h1>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value">{total_rois}</div>
                    <div class="stat-label">ROIs Analyzed</div>
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

    for img_result in results["rois"]:
        html += f"""
            <h2>📄 {img_result['name']} - ROI {img_result['roi_idx']}</h2>
            <div class="roi-info">
                <strong>ROI Location:</strong> ({img_result['roi_x']}, {img_result['roi_y']}) |
                <strong>Size:</strong> {img_result['roi_width']} × {img_result['roi_height']} px
            </div>
            <div class="image-grid">
                <div class="image-card">
                    <h3>Original ROI</h3>
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

    metadata = results["metadata"]
    html = (
        html.replace("{total_rois}", str(metadata["total_rois"]))
        .replace("{model_name}", str(metadata["model_name"]))
        .replace("{timestamp}", str(metadata["timestamp"]))
    )

    html_path = output_dir / "results_roi.html"
    html_path.write_text(html, encoding="utf-8")
    return html_path


def main():
    parser = argparse.ArgumentParser(
        description="ROI-focused DINO medical image analyzer"
    )
    parser.add_argument(
        "--wsi_dir",
        type=str,
        required=True,
        help="Directory with WSI (.svs) and GeoJSON files"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output/roi_analysis",
        help="Output folder"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="facebook/dinov2-small",
        help="HF model: facebook/dinov2-small, facebook/dinov2-base, facebook/dinov2-large"
    )
    parser.add_argument(
        "--clusters",
        type=int,
        default=5,
        help="Number of segmentation clusters"
    )
    parser.add_argument(
        "--roi_size",
        type=int,
        default=2048,
        help="Max ROI extraction size"
    )
    parser.add_argument(
        "--process_size",
        type=int,
        default=518,
        help="Processing image size, 518 for DINOv2"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda" if torch.cuda.is_available() else "cpu"
    )
    parser.add_argument(
        "--slide",
        type=str,
        default="",
        help="Optional single slide filename or stem, e.g. C1-L2 or C1-L2.svs"
    )
    args = parser.parse_args()

    if args.device == "cuda" and not torch.cuda.is_available():
        print("⚠️  CUDA requested but unavailable. Falling back to CPU.")
        args.device = "cpu"

    wsi_dir = Path(args.wsi_dir)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    wsi_paths = []
    if args.slide:
        slide_name = args.slide if args.slide.lower().endswith(".svs") else f"{args.slide}.svs"
        candidates = [wsi_dir / slide_name]
    else:
        candidates = sorted(wsi_dir.glob("*.svs"))

    for svs_file in candidates:
        if not svs_file.exists():
            print(f"⚠️  Slide not found: {svs_file}")
            continue

        geojson_path = get_corresponding_geojson(str(svs_file))
        if Path(geojson_path).exists():
            wsi_paths.append(svs_file)
        else:
            print(f"⚠️  GeoJSON not found for {svs_file.name}: {geojson_path}")

    if not wsi_paths:
        raise FileNotFoundError(
            f"No WSI files with GeoJSON annotations found in {wsi_dir}"
        )

    print(f"🚀 Loading model: {args.model}")
    model, processor = load_model_hf(args.model, args.device)

    results = {
        "metadata": {
            "total_rois": 0,
            "model_name": args.model,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "rois": []
    }

    total_rois = 0

    for wsi_path in tqdm(wsi_paths, desc="🔬 Processing WSI files"):
        stem = wsi_path.stem
        geojson_path = get_corresponding_geojson(str(wsi_path))
        rois = get_rois_from_geojson(geojson_path)

        if not rois:
            print(f"⚠️  No ROIs found in {geojson_path}")
            continue

        print(f"\n📍 Processing {stem}: {len(rois)} ROI(s)")

        for roi_idx, roi in enumerate(rois):
            total_rois += 1

            print(f"  Extracting ROI {roi_idx + 1}/{len(rois)}...")
            roi_img = extract_roi_from_wsi(wsi_path, roi, args.roi_size)

            roi_img_resized = roi_img.resize(
                (args.process_size, args.process_size),
                Image.BICUBIC
            )

            features = extract_features_hf(
                model,
                processor,
                roi_img_resized,
                args.device
            )

            n_patches = features.shape[0]
            patch_h = patch_w = int(np.sqrt(n_patches))

            print(f"  Features: {features.shape}, Patches: {patch_h}×{patch_w}")

            roi_name = f"{stem}_roi{roi_idx}"
            roi_out_dir = out_dir / roi_name
            roi_out_dir.mkdir(exist_ok=True)

            orig_path = roi_out_dir / "original.png"
            roi_img.save(orig_path)

            labels, _ = create_segmentation_map(features, args.clusters)
            seg_map = labels.reshape(patch_h, patch_w).astype(np.uint8)
            seg_t = torch.from_numpy(seg_map)[None, None].float()
            seg_up = F.interpolate(
                seg_t,
                size=(args.process_size, args.process_size),
                mode="nearest"
            )[0, 0].numpy()

            cmap = plt.get_cmap("tab20", args.clusters)
            seg_colored = (cmap(seg_up / args.clusters)[..., :3] * 255).astype(np.uint8)
            seg_img = Image.fromarray(seg_colored)
            seg_path = roi_out_dir / "segmentation.png"
            seg_img.save(seg_path)

            pca_result = create_pca_visualization(features)
            pca_map = pca_result.reshape(patch_h, patch_w, 3)
            pca_t = torch.from_numpy(pca_map).permute(2, 0, 1)[None].float()
            pca_up = F.interpolate(
                pca_t,
                size=(args.process_size, args.process_size),
                mode="bilinear"
            )[0].permute(1, 2, 0).numpy()
            pca_img = Image.fromarray((pca_up * 255).astype(np.uint8))
            pca_path = roi_out_dir / "pca.png"
            pca_img.save(pca_path)

            heatmap = create_heatmap(
                features,
                patch_h,
                patch_w,
                (args.process_size, args.process_size)
            )
            heatmap_path = roi_out_dir / "heatmap.png"
            heatmap.save(heatmap_path)

            results["rois"].append({
                "name": stem,
                "roi_idx": roi_idx,
                "roi_x": roi["x_min"],
                "roi_y": roi["y_min"],
                "roi_width": roi["width"],
                "roi_height": roi["height"],
                "original": f"{roi_name}/original.png",
                "segmentation": f"{roi_name}/segmentation.png",
                "pca": f"{roi_name}/pca.png",
                "heatmap": f"{roi_name}/heatmap.png",
                "clusters": args.clusters
            })

    results["metadata"]["total_rois"] = total_rois

    html_path = save_results_html(results, out_dir)

    json_path = out_dir / "summary_roi.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n✅ Analysis complete!")
    print(f"📊 Processed {total_rois} ROIs from {len(wsi_paths)} WSI files")
    print(f"📁 Results: {out_dir.resolve()}")
    print(f"🌐 Open: {html_path.resolve()}")


if __name__ == "__main__":
    main()
+3
