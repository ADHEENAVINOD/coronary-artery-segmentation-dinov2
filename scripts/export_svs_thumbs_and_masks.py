import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from tqdm import tqdm

import openslide
from shapely.geometry import shape, Polygon, MultiPolygon


def find_matching_geojson(svs_path: Path) -> Path | None:
    gj = svs_path.with_suffix(".geojson")
    return gj if gj.exists() else None


def rasterize_geojson_to_mask(geojson_path: Path, out_size_wh: tuple[int, int], scale_x: float, scale_y: float) -> Image.Image:
    """
    Assumes GeoJSON coordinates are in level-0 pixel coordinates (common with QuPath-like exports).
    Produces a binary mask (0 background, 255 foreground) at thumbnail resolution.
    """
    W, H = out_size_wh
    mask = Image.new("L", (W, H), 0)
    draw = ImageDraw.Draw(mask)

    data = json.loads(geojson_path.read_text(encoding="utf-8"))
    features = data.get("features", [])

    for feat in features:
        geom = feat.get("geometry", None)
        if not geom:
            continue

        g = shape(geom)

        polys = []
        if isinstance(g, Polygon):
            polys = [g]
        elif isinstance(g, MultiPolygon):
            polys = list(g.geoms)
        else:
            continue

        for poly in polys:
            # exterior
            ext = [(x * scale_x, y * scale_y) for (x, y) in poly.exterior.coords]
            draw.polygon(ext, fill=255)

            # holes (interiors)
            for ring in poly.interiors:
                hole = [(x * scale_x, y * scale_y) for (x, y) in ring.coords]
                draw.polygon(hole, fill=0)

    return mask


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wsi_dir", type=str, required=True, help="Folder containing .svs and .geojson")
    ap.add_argument("--out_images", type=str, default="data/images", help="Where to save thumbnail PNGs")
    ap.add_argument("--out_masks", type=str, default="data/masks", help="Where to save mask PNGs (if geojson exists)")
    ap.add_argument("--max_side", type=int, default=2048, help="Thumbnail max side length in pixels")
    args = ap.parse_args()

    wsi_dir = Path(args.wsi_dir)
    out_images = Path(args.out_images); out_images.mkdir(parents=True, exist_ok=True)
    out_masks = Path(args.out_masks); out_masks.mkdir(parents=True, exist_ok=True)

    svs_paths = sorted(wsi_dir.glob("*.svs"))
    if not svs_paths:
        raise FileNotFoundError(f"No .svs files found in: {wsi_dir}")

    for svs_path in tqdm(svs_paths, desc="Exporting thumbnails/masks"):
        slide = openslide.OpenSlide(str(svs_path))

        W0, H0 = slide.dimensions  # level-0 size
        # Create thumbnail (keeps aspect ratio)
        thumb = slide.get_thumbnail((args.max_side, args.max_side)).convert("RGB")
        Wt, Ht = thumb.size

        # Save thumbnail
        out_img = out_images / f"{svs_path.stem}.png"
        thumb.save(out_img)

        # Rasterize geojson to mask if present
        gj = find_matching_geojson(svs_path)
        if gj is not None:
            scale_x = Wt / W0
            scale_y = Ht / H0
            mask = rasterize_geojson_to_mask(gj, (Wt, Ht), scale_x, scale_y)
            out_m = out_masks / f"{svs_path.stem}_mask.png"
            mask.save(out_m)

    print(f"Done.\nImages: {out_images.resolve()}\nMasks:  {out_masks.resolve()}")


if __name__ == "__main__":
    main()

    