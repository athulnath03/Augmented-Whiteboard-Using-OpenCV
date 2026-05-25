"""
canvas.py — White drawing canvas with undo support.
"""

import cv2
import numpy as np
from src.config import DEFAULT_THICKNESS, DEFAULT_COLOR

MAX_UNDO = 20


class Canvas:
    def __init__(self, width, height):
        self._w        = width
        self._h        = height
        self.color     = DEFAULT_THICKNESS  # fixed below
        self.color     = DEFAULT_COLOR
        self.thickness = DEFAULT_THICKNESS
        self._current  = self._blank()
        self._history  = []
        self._fist_held = False   # debounce: one undo per fist gesture
        self._stroke_started = False  # track if we've saved undo point for this stroke

    def _blank(self):
        return np.ones((self._h, self._w, 3), np.uint8) * 255

    def draw_line(self, pt1, pt2, first_point=False):
        """Draw a line segment. Pass first_point=True on the first point of a new stroke."""
        if first_point:
            self._push_history()
        draw_color = (255, 255, 255) if self.color == (0, 0, 0) else self.color
        cv2.line(self._current, pt1, pt2, draw_color, self.thickness)
        self._fist_held = False

    def on_fist(self):
        """Call every frame while fist is held. Undoes one stroke per gesture."""
        if not self._fist_held:
            if self._history:
                self._current = self._history.pop()
            self._fist_held = True

    def on_fist_released(self):
        self._fist_held = False

    def _push_history(self):
        if len(self._history) >= MAX_UNDO:
            self._history.pop(0)
        self._history.append(self._current.copy())

    def clear(self):
        self._push_history()
        self._current = self._blank()
        self._fist_held = False

    def get_display(self):
        return self._current.copy()

    def save(self, path):
        cv2.imwrite(path, self._current)
        return path
