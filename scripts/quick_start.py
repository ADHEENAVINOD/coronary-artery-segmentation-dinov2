import argparse
import subprocess
import sys
from pathlib import Path
import webbrowser


def run_command(cmd, desc):
    print(f"\n{'=' * 60}")
    print(f"🔄 {desc}")
    print(f"{'=' * 60}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        error_text = (result.stderr or result.stdout).strip()
        print(f"❌ Error: {error_text or 'Unknown failure'}")
        return False
    print(f"✅ {desc} - Complete!")
    return True


def main():
    parser = argparse.ArgumentParser(description="Quick Start: WSI to Analysis Pipeline")
    parser.add_argument("--wsi_dir", type=str, default="data/coronary-data-2", help="WSI folder")
    parser.add_argument("--model", type=str, default="dinov3_vits16", help="DINOv3 model")
    parser.add_argument("--clusters", type=int, default=5, help="Segmentation clusters")
    parser.add_argument("--skip_export", action="store_true", help="Skip WSI export if already done")
    args = parser.parse_args()

    print("🚀 DINOv3 Medical Image Analysis Pipeline")
    print("=" * 60)

    # Step 1: Export thumbnails from WSI
    if not args.skip_export:
        cmd1 = [
            sys.executable,
            "scripts/export_svs_thumbs_and_masks.py",
            "--wsi_dir",
            args.wsi_dir,
            "--out_images",
            "data/images",
            "--out_masks",
            "data/masks",
            "--max_side",
            "2048",
        ]
        if not run_command(cmd1, "Step 1: Exporting WSI thumbnails"):
            return
    else:
        print("\n⏭️  Skipping WSI export (using existing images)")

    # Step 2: Run advanced analysis
    cmd2 = [
        sys.executable,
        "scripts/medical_image_analyzer_hf.py",
        "--images",
        "data/images",
        "--output",
        "output/analysis",
        "--model",
        args.model,
        "--clusters",
        str(args.clusters),
        "--size",
        "1024",
    ]
    if not run_command(cmd2, "Step 2: Running DINOv3 analysis"):
        return

    # Step 3: Open results
    results_html = Path("output/analysis/results.html").resolve()
    if results_html.exists():
        print(f"\n{'=' * 60}")
        print("🎉 Pipeline Complete!")
        print(f"{'=' * 60}")
        print("📊 Results saved to: output/analysis/")
        print("🌐 Opening results in browser...")
        webbrowser.open(results_html.as_uri())
    else:
        print("\n⚠️  Results HTML not found")


if __name__ == "__main__":
    main()
    
