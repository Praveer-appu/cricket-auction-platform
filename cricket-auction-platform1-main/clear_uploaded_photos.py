"""
Clear all uploaded player photos from static/uploads/players/
"""
import os
from pathlib import Path

UPLOAD_DIR = Path("static/uploads/players")

print("=" * 60)
print("CLEARING UPLOADED PLAYER PHOTOS")
print("=" * 60)

if not UPLOAD_DIR.exists():
    print(f"\n⚠️ Upload directory does not exist: {UPLOAD_DIR}")
    print("=" * 60)
    exit(0)

# Count files
photo_files = [f for f in UPLOAD_DIR.iterdir() if f.is_file() and f.name != ".gitkeep"]
count = len(photo_files)

print(f"\nFound {count} photo files to delete")

if count == 0:
    print("\n✅ No photos to delete - directory is already clean")
    print("=" * 60)
    exit(0)

# Delete all photos except .gitkeep
deleted = 0
for photo_file in photo_files:
    try:
        photo_file.unlink()
        deleted += 1
        print(f"  ✅ Deleted: {photo_file.name}")
    except Exception as e:
        print(f"  ❌ Failed to delete {photo_file.name}: {e}")

print(f"\n✅ Deleted {deleted} out of {count} photo files")
print("=" * 60)
print("PHOTO CLEANUP COMPLETE")
print("=" * 60)
