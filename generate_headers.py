"""
generate_headers.py — creates high-quality toolbar images.
Run once:
python generate_headers.py
"""

import os
import cv2
import numpy as np

OUT_DIR = "headers"

# Generate at 2× resolution for sharp output
W, H = 1280, 160

# Must match COLOR_ZONES in src/config.py
SHIFT = 45

ZONES = [
    (72  + SHIFT, 160 + SHIFT, (0,   0,   255), "Red"),
    (205 + SHIFT, 295 + SHIFT, (255, 0,   0), "Blue"),
    (338 + SHIFT, 428 + SHIFT, (0,   255, 0), "Green"),
    (472 + SHIFT, 562 + SHIFT, (0,   0,   0), "Eraser"),
]

# Scale zones for 2× rendering
SCALE = W / 640
ZONES = [
    (
        int(x0 * SCALE),
        int(x1 * SCALE),
        color,
        label
    )
    for x0, x1, color, label in ZONES
]


def draw_centered_text(img, text, center_x, y,
                       font, scale, color, thickness):

    (tw, th), _ = cv2.getTextSize(
        text,
        font,
        scale,
        thickness
    )

    cv2.putText(
        img,
        text,
        (center_x - tw // 2, y),
        font,
        scale,
        color,
        thickness,
        cv2.LINE_AA
    )


def make_header(active_idx):

    img = np.full((H, W, 3), 28, dtype=np.uint8)

    # -------------------------
    # Title
    # -------------------------

    cv2.putText(
        img,
        "AirBoard",
        (16, 80),
        cv2.FONT_HERSHEY_COMPLEX_SMALL,
        1.4,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        img,
        "V1.0",
        (24, 112),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (220, 220, 220),
        1,
        cv2.LINE_AA
    )

    # -------------------------
    # Color sectors
    # -------------------------

    for i, (x0, x1, color, label) in enumerate(ZONES):

        cx = (x0 + x1) // 2

        display_color = (
            (220, 220, 220)
            if color == (0, 0, 0)
            else color
        )

        radius = 36
        border = 5 if i == active_idx else 2

        cy = H // 2 - 8

        cv2.circle(
            img,
            (cx, cy),
            radius,
            display_color,
            -1
        )

        cv2.circle(
            img,
            (cx, cy),
            radius,
            (220, 220, 220),
            border
        )

        draw_centered_text(
            img,
            label,
            cx,
            H - 18,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (185, 185, 185),
            1
        )

        # # Debug zone guides
        # cv2.line(
        #     img,
        #     (x0, 0),
        #     (x0, H),
        #     (60, 60, 60),
        #     1
        # )

        # cv2.line(
        #     img,
        #     (x1, 0),
        #     (x1, H),
        #     (60, 60, 60),
        #     1
        # )

    return img


os.makedirs(OUT_DIR, exist_ok=True)

for i in range(len(ZONES)):

    path = os.path.join(
        OUT_DIR,
        f"{i + 1}.png"
    )

    cv2.imwrite(
        path,
        make_header(i)
    )

    print(f"Saved {path}")

print("\nDone.")
print("Run: python main.py")