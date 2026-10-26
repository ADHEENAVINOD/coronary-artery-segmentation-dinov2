from pathlib import Path
from PIL import Image, PngImagePlugin
from tqdm import tqdm

# Fix for large PNG files
PngImagePlugin.MAX_TEXT_CHUNK = 100 * (1024**2)

input_dir = Path("data/images")
output_dir = Path("data/images_resized")
output_dir.mkdir(exist_ok=True)

max_size = 2048

for img_path in tqdm(list(input_dir.glob("*.png")), desc="Resizing images"):
    try:
        img = Image.open(img_path)
        
        # Resize if too large
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size), Image.BICUBIC)
        
        # Save
        out_path = output_dir / img_path.name
        img.save(out_path, "PNG", optimize=True)
        print(f"✅ {img_path.name}: {img.size}")
    except Exception as e:
        print(f"❌ Error with {img_path.name}: {e}")

print(f"\n✅ Done! Resized images saved to: {output_dir}")
