"""
toolbar.py
Colour zones are always stored in raw camera coordinates (0..CAMERA_WIDTH).
try_select() receives raw camera coords — no scaling confusion.
resize() only scales the header image for display, not the zone coords.
"""

import os
import cv2
from src.config import CAMERA_WIDTH, HEADER_HEIGHT, COLOR_ZONES


class Toolbar:
    def __init__(self, headers_dir="headers"):
        files = sorted(f for f in os.listdir(headers_dir)
                       if f.lower().endswith((".png", ".jpg")))
        self._raw = [cv2.imread(os.path.join(headers_dir, f)) for f in files]
        if not self._raw:
            raise FileNotFoundError("Run: python generate_headers.py")

        # zones always in raw camera pixel space
        self._zones    = COLOR_ZONES
        self._header_h = HEADER_HEIGHT   # in raw camera pixels
        self._headers  = self._raw
        self.current   = self._headers[0]
        self.color     = COLOR_ZONES[0][2]
        self._display_w = CAMERA_WIDTH
        self._display_h_header = HEADER_HEIGHT

    def resize(self, display_w, display_h):
        """Scale header images for display — zones stay in camera coords."""
        # Header display height scales proportionally with width
        scale = display_w / CAMERA_WIDTH
        disp_h = int(HEADER_HEIGHT * scale)
        self._display_w = display_w
        self._display_h_header = disp_h
        self._headers = [cv2.resize(img, (display_w, disp_h)) for img in self._raw]
        self.current  = self._headers[0]

    def try_select(self, raw_x, raw_y):
        """
        raw_x, raw_y are in camera pixel space (0..CAMERA_WIDTH, 0..CAMERA_HEIGHT).
        Zones are also in camera pixel space — no scaling needed.
        """
        if raw_y >= self._header_h:
            return False
        for idx, (x0, x1, color) in enumerate(self._zones):
            if x0 < raw_x < x1:
                self.current = self._headers[min(idx, len(self._headers) - 1)]
                self.color   = color
                return True
        return False

    def apply(self, frame):
        """Stamp header onto the (already display-scaled) camera frame."""
        h = self.current.shape[0]
        w = self.current.shape[1]
        frame[0:h, 0:w] = self.current
        return frame
