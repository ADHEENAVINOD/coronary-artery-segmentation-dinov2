import os
import json
import argparse
from pathlib import Path

import torch
import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import PngImagePlugin
from tqdm import tqdm

import openslide
from openslide import OpenSlide
from transformers import AutoImageProcessor, AutoModel
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

PngImagePlugin.MAX_TEXT_CHUNK = 100 * 1024 * 1024


def parse_args():
    ap = argparse.ArgumentParser(description="DINOv3 WSI ROI feature extraction + clustering (Windows-friendly)")

    ap.add_argument("--svs_dir", type=str, required=True, help="Folder containing .svs and .geojson files")
    ap.add_argument("--out_dir", type=str, required=True, help="Folder to save visualization/check images")
    ap.add_argument("--train_dir", type=str, required=True, help="Folder to save training pairs (images + labels)")

    ap.add_argument(
        "--model_id",
        type=str,
        default="facebook/dinov3-vitl16-pretrain-lvd1689m",
        help="HuggingFace model id (default: vitl16). You can try a smaller model if available.",
    )

    ap.add_argument("--device", type=str, default="cuda", choices=["cuda", "cpu"], help="Device preference")
    ap.add_argument("--patch_size", type=int, default=1008, help="Tile size (level-0 pixels) for ROI gridding")
    ap.add_argument("--overlap", type=int, default=28, help="Overlap context pixels to reduce grid artifacts")
    ap.add_argument("--layers", type=str, default="9,15,20", help="Comma-separated hidden-state layer indices")
    ap.add_argument("--n_clusters", type=int, default=4, help="Number of kmeans clusters (biological classes)")
    ap.add_argument("--pca_dim", type=int, default=20, help="PCA dimension before clustering")
    ap.add_argument("--max_side_check", type=int, default=2000, help="Max side for CHECK image saving")
    ap.add_argument("--hf_home", type=str, default="", help="Optional HF cache dir (e.g. C:\\...\\hf_cache)")
    ap.add_argument("--slide", type=str, default="", help="Optional: process only one slide filename (e.g. C2-L1.svs)")
    ap.add_argument("--smooth_kernel", type=int, default=5, help="Morphology kernel size for cleaner K-means masks; use 0 to disable")
    ap.add_argument("--min_region_area", type=int, default=2500, help="Remove connected regions smaller than this many pixels; use 0 to disable")

    return ap.parse_args()


def get_device(preferred: str) -> torch.device:
    if preferred == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def get_rois_from_geojson(geojson_path: str):
    """
    Extract simple bounding boxes from GeoJSON polygon features.
    Assumes coordinates are level-0 pixel coordinates.
    """
    with open(geojson_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    rois = []
    features = data.get("features", [])
    for feature in features:
        geom = feature.get("geometry", {})
        coords = geom.get("coordinates", None)
        if not coords:
            continue

        # Expect Polygon: coordinates[0] is the exterior ring
        # If it is MultiPolygon, coords[0][0] etc. This keeps it simple:
        ring = None
        if geom.get("type") == "Polygon":
            ring = coords[0]
        elif geom.get("type") == "MultiPolygon":
            ring = coords[0][0]
        else:
            continue

        x_coords = [c[0] for c in ring]
        y_coords = [c[1] for c in ring]
        x_min, x_max = float(min(x_coords)), float(max(x_coords))
        y_min, y_max = float(min(y_coords)), float(max(y_coords))

        rois.append(
            {
                "x_min": int(x_min),
                "y_min": int(y_min),
                "width": int(max(1, x_max - x_min)),
                "height": int(max(1, y_max - y_min)),
            }
        )

    return rois



def safe_read_region(slide: OpenSlide, x: int, y: int, level: int, size_wh: tuple[int, int]):
    """
    OpenSlide can misbehave if x/y are negative. Clamp to 0.
    (This can slightly change the border behavior, but avoids crashes.)
    """
    x = max(0, int(x))
    y = max(0, int(y))
    return slide.read_region((x, y), level, size_wh)


def save_check_overlay(out_dir: str, name: str, orig_rgb: np.ndarray, mask: np.ndarray, max_side: int = 2000):
    os.makedirs(out_dir, exist_ok=True)

    h, w = orig_rgb.shape[:2]
    scale = max_side / max(h, w)
    scale = min(1.0, float(scale))

    if scale < 1.0:
        orig_rgb = cv2.resize(orig_rgb, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        mask = cv2.resize(mask, (orig_rgb.shape[1], orig_rgb.shape[0]), interpolation=cv2.INTER_NEAREST)

    plt.figure(figsize=(20, 10))
    plt.subplot(1, 2, 1)
    plt.imshow(orig_rgb)
    plt.axis("off")
    plt.title("Original ROI")

    plt.subplot(1, 2, 2)
    plt.imshow(orig_rgb)
    plt.imshow(mask, alpha=0.5, cmap="jet")
    plt.axis("off")
    plt.title("Overlay (mask)")
    plt.savefig(os.path.join(out_dir, f"{name}_overlay.png"), bbox_inches="tight")
    plt.close()


def clean_cluster_mask(mask: np.ndarray, n_clusters: int, smooth_kernel: int = 5, min_region_area: int = 2500):
    """
    Clean noisy K-means masks for visualization and baseline labels.

    This removes tiny disconnected islands and applies light open/close morphology
    per cluster. It is only a post-processing cleanup; the true thesis improvement
    should still come from a trained segmentation head plus topology constraints.
    """
    cleaned = mask.copy()

    if min_region_area > 0:
        for class_id in range(n_clusters):
            class_mask = (cleaned == class_id).astype(np.uint8)
            n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(class_mask, connectivity=8)
            for label_id in range(1, n_labels):
                if stats[label_id, cv2.CC_STAT_AREA] < min_region_area:
                    cleaned[labels == label_id] = 0

    if smooth_kernel and smooth_kernel > 1:
        kernel_size = smooth_kernel if smooth_kernel % 2 == 1 else smooth_kernel + 1
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        smoothed = cleaned.copy()

        for class_id in range(n_clusters):
            class_mask = (cleaned == class_id).astype(np.uint8)
            class_mask = cv2.morphologyEx(class_mask, cv2.MORPH_OPEN, kernel)
            class_mask = cv2.morphologyEx(class_mask, cv2.MORPH_CLOSE, kernel)
            smoothed[class_mask == 1] = class_id

        cleaned = smoothed

    return cleaned


def process_wsi_automatically(
    svs_path: str,
    processor,
    model,
    device: torch.device,
    out_dir: str,
    train_dir: str,
    n_clusters: int = 4,
    selected_layers=None,
    patch_size: int = 1008,
    overlap: int = 28,
    pca_dim: int = 20,
    max_side_check: int = 2000,
    smooth_kernel: int = 5,
    min_region_area: int = 2500,
):
    if selected_layers is None:
        selected_layers = [9, 15, 20]

    svs_path = str(svs_path)
    basename = Path(svs_path).stem
    geojson_path = str(Path(svs_path).with_suffix(".geojson"))

    if not os.path.exists(geojson_path):
        print(f"[SKIP] No geojson for {basename}: {geojson_path}")
        return

    slide = OpenSlide(svs_path)
    rois = get_rois_from_geojson(geojson_path)
    if len(rois) == 0:
        print(f"[SKIP] No ROI polygons found in geojson for {basename}")
        return

    img_dir = os.path.join(train_dir, "images")
    lab_dir = os.path.join(train_dir, "labels")
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(lab_dir, exist_ok=True)

    for roi_idx, roi in enumerate(rois):
        roi_name = f"{basename}_roi_{roi_idx + 1}"

        grid_w = int(np.ceil(roi["width"] / patch_size))
        grid_h = int(np.ceil(roi["height"] / patch_size))
        n_patches = grid_w * grid_h

        roi_orig = np.zeros((grid_h * patch_size, grid_w * patch_size, 3), dtype=np.uint8)
        feature_bank = None
        write_ptr = 0


        read_size = patch_size + (2 * overlap)

        print(f"\n=== {roi_name} ===")
        print(f"[INFO] ROI bbox: {roi}")
        print(f"[INFO] grid: {grid_w} x {grid_h} -> {n_patches} patches")
        print(f"[3/5] Streaming patches with overlap={overlap} ...")

        for y_idx in tqdm(range(grid_h), desc=f"{roi_name}: rows", leave=False):
            for x_idx in range(grid_w):
                curr_x = roi["x_min"] + (x_idx * patch_size) - overlap
                curr_y = roi["y_min"] + (y_idx * patch_size) - overlap

                patch_img = safe_read_region(slide, curr_x, curr_y, 0, (read_size, read_size)).convert("RGB")

                # Inner patch for reconstruction (crop overlap away)
                inner_patch = patch_img.crop((overlap, overlap, overlap + patch_size, overlap + patch_size))
                roi_orig[
                    y_idx * patch_size : (y_idx + 1) * patch_size,
                    x_idx * patch_size : (x_idx + 1) * patch_size,
                ] = np.array(inner_patch)

                inputs = processor(images=patch_img, return_tensors="pt")
                inputs = {k: v.to(device) for k, v in inputs.items()}

                with torch.no_grad():
                    outputs = model(**inputs, output_hidden_states=True)

                multi_scale_feats = []
                for l in selected_layers:
                    layer_output = outputs.hidden_states[l][0]  # (tokens, dim)

                    # Take last 196 tokens as patch tokens (14x14) safely even if there are extra tokens
                    layer_feats = layer_output[-196:, :]  # (196, dim)
                    dim = layer_feats.shape[-1]

                    feat_map = layer_feats.reshape(1, 14, 14, dim).permute(0, 3, 1, 2)  # (1, dim, 14, 14)
                    feat_map = torch.nn.functional.avg_pool2d(feat_map, 3, stride=1, padding=1)
                    smooth_map = torch.nn.functional.interpolate(feat_map, size=(28, 28), mode="bilinear", align_corners=False)

                    # Crop off 1-cell border => 26x26
                    clean_map = smooth_map[:, :, 1:-1, 1:-1]  # (1, dim, 26, 26)
                    clean_flat = clean_map.permute(0, 2, 3, 1).reshape(-1, dim)  # (26*26, dim)
                    multi_scale_feats.append(clean_flat.cpu().numpy())

                patch_features = np.concatenate(multi_scale_feats, axis=-1).astype(np.float16, copy=False)  # (676, dim*L)

                if feature_bank is None:
                    feature_bank = np.empty((n_patches * patch_features.shape[0], patch_features.shape[1]), dtype=np.float16)

                end_ptr = write_ptr + patch_features.shape[0]
                feature_bank[write_ptr:end_ptr] = patch_features
                write_ptr = end_ptr

                # cleanup
                del outputs, inputs, patch_features

        print("[4/5] Clustering (PCA + StandardScaler + KMeans) ...")
        feature_bank = feature_bank[:write_ptr].astype(np.float32, copy=False)

        # PCA components must be <= min(n_samples-1, n_features)
        n_samples, n_features = feature_bank.shape
        pca_components = min(pca_dim, n_features, max(1, n_samples - 1))

        if pca_components < 2:
            print(f"[SKIP] Not enough samples for PCA/KMeans in {roi_name} (samples={n_samples}).")
            continue

        features_pca = PCA(n_components=pca_components, random_state=42).fit_transform(feature_bank)
        features_norm = StandardScaler().fit_transform(features_pca)

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels_raw = kmeans.fit_predict(features_norm)

        # Brightness-based cluster ordering (kept from your original script)
        cluster_info = []
        for i in range(n_clusters):
            cluster_mask = (labels_raw == i)
            mean_brightness = float(np.mean(feature_bank[cluster_mask])) if np.any(cluster_mask) else -1e9
            cluster_info.append({"id": i, "brightness": mean_brightness})

        cluster_info.sort(key=lambda x: x["brightness"], reverse=True)

        # For n_clusters=4, map to standard labels: 0 background, 3 lumen, 2 intima, 1 media
        # If n_clusters != 4, this mapping is undefined; we will just keep raw labels.
        if n_clusters == 4:
            standard_map = {
                cluster_info[0]["id"]: 0,
                cluster_info[1]["id"]: 3,
                cluster_info[2]["id"]: 2,
                cluster_info[3]["id"]: 1,
            }
            labels = np.array([standard_map[l] for l in labels_raw], dtype=np.uint8)
        else:
            labels = labels_raw.astype(np.uint8)

        print("[5/5] Reconstructing mask + saving outputs ...")

        roi_mask = np.zeros((grid_h * patch_size, grid_w * patch_size), dtype=np.uint8)

        # 676 = 26*26
        cells_per_patch = 26 * 26
        for idx in range(n_patches):
            patch_labels = labels[idx * cells_per_patch : (idx + 1) * cells_per_patch].reshape(26, 26)
            upsampled = cv2.resize(patch_labels, (patch_size, patch_size), interpolation=cv2.INTER_NEAREST)

            r, c = idx // grid_w, idx % grid_w
            roi_mask[r * patch_size : (r + 1) * patch_size, c * patch_size : (c + 1) * patch_size] = upsampled

        if smooth_kernel > 0 or min_region_area > 0:
            roi_mask = clean_cluster_mask(
                roi_mask,
                n_clusters=n_clusters,
                smooth_kernel=smooth_kernel,
                min_region_area=min_region_area,
            )

        # Save training pair
        cv2.imwrite(os.path.join(img_dir, f"{roi_name}.png"), cv2.cvtColor(roi_orig, cv2.COLOR_RGB2BGR))
        np.save(os.path.join(lab_dir, f"{roi_name}.npy"), roi_mask)

        # Save check image (resized)
         #save_check_overlay(out_dir, roi_name, roi_orig, roi_mask)
        scale = max_side_check / max(roi_orig.shape[:2])
        scale = min(1.0, float(scale))
        small_mask = cv2.resize(roi_mask, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
        plt.imsave(os.path.join(lab_dir, f"{roi_name}_CHECK.png"), small_mask, cmap="jet")

        # Save overlay visualization
        save_check_overlay(out_dir, roi_name, roi_orig, roi_mask, max_side=max_side_check)

        print(f"[OK] Saved: {roi_name} -> images/, labels/, overlay")


def main():
    args = parse_args()

    if args.hf_home.strip():
        os.environ["HF_HOME"] = args.hf_home.strip()

    svs_dir = Path(args.svs_dir)
    if not svs_dir.exists():
        raise FileNotFoundError(f"svs_dir not found: {svs_dir}")

    out_dir = str(Path(args.out_dir))
    train_dir = str(Path(args.train_dir))

    device = get_device(args.device)
    print(f"[INFO] device: {device}")

    # Parse layers
    selected_layers = [int(x.strip()) for x in args.layers.split(",") if x.strip()]

    print(f"[INFO] Loading HF model: {args.model_id}")
    processor = AutoImageProcessor.from_pretrained(args.model_id)
    model = AutoModel.from_pretrained(args.model_id).eval().to(device)

    # Gather slides
    if args.slide.strip():
        svs_paths = [svs_dir / args.slide.strip()]
    else:
        svs_paths = sorted(svs_dir.glob("*.svs"))

    if not svs_paths:
        raise FileNotFoundError(f"No .svs files found in: {svs_dir}")

    # Process
    for svs_path in svs_paths:
        if not svs_path.exists():
            print(f"[SKIP] missing slide: {svs_path}")
            continue

        process_wsi_automatically(
            str(svs_path),
            processor=processor,
            model=model,
            device=device,
            out_dir=out_dir,
            train_dir=train_dir,
            n_clusters=args.n_clusters,
            selected_layers=selected_layers,
            patch_size=args.patch_size,
            overlap=args.overlap,
            pca_dim=args.pca_dim,
            max_side_check=args.max_side_check,
            smooth_kernel=args.smooth_kernel,
            min_region_area=args.min_region_area,
        )

    print("[DONE] All slides processed.")


if __name__ == "__main__":
    main()
