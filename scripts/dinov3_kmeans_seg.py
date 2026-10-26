import argparse
from pathlib import Path

import numpy as np
from PIL import Image
from tqdm import tqdm

import torch
import torch.nn.functional as F
import torchvision.transforms.functional as TF

from sklearn.cluster import MiniBatchKMeans
import matplotlib.pyplot as plt


IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD  = (0.229, 0.224, 0.225)


def resize_longest_side(pil_img: Image.Image, longest: int) -> Image.Image:
    w, h = pil_img.size
    if max(w, h) <= longest:
        return pil_img
    scale = longest / max(w, h)
    new_w = int(round(w * scale))
    new_h = int(round(h * scale))
    return pil_img.resize((new_w, new_h), resample=Image.BICUBIC)


def pad_to_multiple(x: torch.Tensor, m: int):
    H, W = x.shape[-2], x.shape[-1]
    pad_h = (m - H % m) % m
    pad_w = (m - W % m) % m
    x_pad = F.pad(x, (0, pad_w, 0, pad_h))
    return x_pad, (pad_h, pad_w)


def infer_patch_size(model) -> int:
    # Best effort across DINOv3 variants
    if hasattr(model, "patch_size") and isinstance(model.patch_size, int):
        return model.patch_size
    if hasattr(model, "patch_embed") and hasattr(model.patch_embed, "patch_size"):
        ps = model.patch_embed.patch_size
        if isinstance(ps, int):
            return ps
        if isinstance(ps, (tuple, list)) and len(ps) > 0:
            return int(ps[0])
    # DINOv3 vits16/vitb16 are typically patch=16
    return 16


@torch.no_grad()
def extract_patch_tokens(model, x: torch.Tensor) -> torch.Tensor:
    """
    Returns patch tokens: (B, N, C) (without CLS).
    Works for common DINO-style forward_features outputs.
    """
    if hasattr(model, "forward_features"):
        out = model.forward_features(x)

        # Often a dict
        if isinstance(out, dict):
            # Common DINO keys
            for k in ["x_norm_patchtokens", "patchtokens", "patch_tokens", "x_patchtokens", "x_patch_tokens"]:
                if k in out and isinstance(out[k], torch.Tensor):
                    return out[k]

            # Sometimes full tokens are provided (CLS + patches)
            for k in ["x_norm_tokens", "tokens", "last_hidden_state"]:
                if k in out and isinstance(out[k], torch.Tensor):
                    tok = out[k]
                    if tok.dim() == 3 and tok.shape[1] >= 2:
                        return tok[:, 1:, :]  # drop CLS
                    return tok

        if isinstance(out, torch.Tensor):
            tok = out
            if tok.dim() == 3 and tok.shape[1] >= 2:
                return tok[:, 1:, :]
            return tok

    if hasattr(model, "get_intermediate_layers"):
        tok = model.get_intermediate_layers(x, n=1)[0]  # (B, N+1, C)
        return tok[:, 1:, :]

    raise RuntimeError(
        "Could not extract patch tokens from model. "
        "Tell me which model you used and I’ll adapt the extraction."
    )


def make_palette(n: int):
    cmap = plt.get_cmap("tab20", n)
    palette = []
    for i in range(n):
        r, g, b, _ = cmap(i)
        palette.extend([int(255*r), int(255*g), int(255*b)])
    palette = (palette + [0] * (768 - len(palette)))[:768]
    return palette


def save_segmentation(seg_hw: np.ndarray, out_png: Path, n_clusters: int):
    seg_img = Image.fromarray(seg_hw.astype(np.uint8), mode="P")
    seg_img.putpalette(make_palette(n_clusters))
    seg_img.save(out_png)


def save_overlay(pil_img: Image.Image, seg_hw: np.ndarray, out_png: Path, alpha=0.45):
    img = np.array(pil_img.convert("RGB")).astype(np.float32) / 255.0
    cmap = plt.get_cmap("tab20")
    colors = cmap((seg_hw % 20) / 20.0)[..., :3]
    overlay = (1 - alpha) * img + alpha * colors
    overlay = np.clip(overlay * 255.0, 0, 255).astype(np.uint8)
    Image.fromarray(overlay).save(out_png)


def load_model_local_hub(model_name: str, device: str):
    model = torch.hub.load(repo_or_dir=".", model=model_name, source="local", pretrained=True)
    model.eval().to(device)
    return model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", type=str, required=True, help="Folder with input PNG/JPG images")
    ap.add_argument("--out", type=str, default="outputs", help="Output folder")
    ap.add_argument("--model", type=str, required=True, help="hubconf model name, e.g. dinov3_vits16")
    ap.add_argument("--clusters", type=int, default=5, help="K-means clusters (pseudo-classes)")
    ap.add_argument("--resize-longest", type=int, default=1024, help="Resize longest side (keep aspect ratio)")
    ap.add_argument("--fit-max-images", type=int, default=20, help="How many images to use to fit k-means")
    ap.add_argument("--sample-patches-per-image", type=int, default=4000, help="Patch vectors sampled per image")
    ap.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    img_dir = Path(args.images)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    img_paths = []
    for ext in ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tif", "*.tiff", "*.webp"]:
        img_paths += list(img_dir.glob(ext))
    img_paths = sorted(img_paths)
    if not img_paths:
        raise FileNotFoundError(f"No images found in {img_dir.resolve()}")

    device = args.device
    print(f"[INFO] Loading model {args.model} on {device} ...")
    model = load_model_local_hub(args.model, device=device)
    patch = infer_patch_size(model)
    print(f"[INFO] Patch size: {patch}")
    print(f"[INFO] Found {len(img_paths)} images in {img_dir.resolve()}")

    kmeans = MiniBatchKMeans(n_clusters=args.clusters, random_state=0, batch_size=8192)

    fit_paths = img_paths[: min(len(img_paths), args.fit_max_images)]
    for p in tqdm(fit_paths, desc="Fitting KMeans"):
        pil = Image.open(p).convert("RGB")
        pil = resize_longest_side(pil, args.resize_longest)

        x = TF.to_tensor(pil)
        x = TF.normalize(x, IMAGENET_MEAN, IMAGENET_STD)
        x = x.unsqueeze(0).to(device)

        x_pad, _ = pad_to_multiple(x, patch)
        tokens = extract_patch_tokens(model, x_pad)  # (1, N, C)

        feats = F.normalize(tokens[0].float(), dim=-1).cpu().numpy()

        if feats.shape[0] > args.sample_patches_per_image:
            idx = np.random.choice(feats.shape[0], args.sample_patches_per_image, replace=False)
            feats = feats[idx]

        kmeans.partial_fit(feats)

    for p in tqdm(img_paths, desc="Segmenting"):
        pil0 = Image.open(p).convert("RGB")
        pil = resize_longest_side(pil0, args.resize_longest)

        x = TF.to_tensor(pil)
        x = TF.normalize(x, IMAGENET_MEAN, IMAGENET_STD)
        x = x.unsqueeze(0).to(device)

        x_pad, (pad_h, pad_w) = pad_to_multiple(x, patch)
        Hp = x_pad.shape[-2] // patch
        Wp = x_pad.shape[-1] // patch

        tokens = extract_patch_tokens(model, x_pad)
        feats = F.normalize(tokens[0].float(), dim=-1).cpu().numpy()

        seg = kmeans.predict(feats).reshape(Hp, Wp).astype(np.uint8)

        seg_t = torch.from_numpy(seg)[None, None].float()
        seg_up = F.interpolate(seg_t, size=x_pad.shape[-2:], mode="nearest")[0, 0].byte().numpy()

        if pad_h > 0:
            seg_up = seg_up[:-pad_h, :]
        if pad_w > 0:
            seg_up = seg_up[:, :-pad_w]

        stem = p.stem
        save_segmentation(seg_up, out_dir / f"{stem}_seg.png", args.clusters)
        save_overlay(pil, seg_up, out_dir / f"{stem}_overlay.png", alpha=0.45)

    print(f"[DONE] Saved results to: {out_dir.resolve()}")


if __name__ == "__main__":
    main()