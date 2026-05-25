"""
download_model.py
-----------------
Downloads the MediaPipe hand landmark model required by mediapipe>=0.10.
Run this once before launching the app:

    python download_model.py
"""

import urllib.request
import os
import sys

MODEL_URL  = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
MODEL_DIR  = "assets"
MODEL_PATH = os.path.join(MODEL_DIR, "hand_landmarker.task")

def main():
    os.makedirs(MODEL_DIR, exist_ok=True)

    if os.path.exists(MODEL_PATH) and os.path.getsize(MODEL_PATH) > 100_000:
        print(f"Model already present at '{MODEL_PATH}'. Nothing to do.")
        return

    print(f"Downloading hand landmark model...")
    print(f"  Source : {MODEL_URL}")
    print(f"  Dest   : {MODEL_PATH}")

    def _progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            pct = min(downloaded / total_size * 100, 100)
            bar = int(pct / 2)
            sys.stdout.write(f"\r  [{'#'*bar}{' '*(50-bar)}] {pct:.1f}%")
            sys.stdout.flush()

    try:
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH, _progress)
        print(f"\n✓ Model saved to '{MODEL_PATH}'")
    except Exception as e:
        print(f"\n✗ Download failed: {e}")
        print("  Try manually downloading from:")
        print(f"  {MODEL_URL}")
        print(f"  and save it to: {MODEL_PATH}")
        sys.exit(1)

if __name__ == "__main__":
    main()
