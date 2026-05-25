"""
hand_tracker.py
───────────────
Wraps MediaPipe HandLandmarker (Tasks API, mediapipe >= 0.10).

Key improvement: detects up to 2 hands but locks onto ONE dominant hand.
  - On first detection, the hand with higher confidence becomes dominant.
  - If two hands are visible, only the dominant hand is used — no stuttering.
  - Lock resets after LOCK_TIMEOUT_S seconds without seeing any hand.
  - User can force a re-lock by hiding both hands for 1 second.
"""

import math
import os
import time
import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision as mp_vision

from src.config import (
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    TIP_IDS,
)

MODEL_PATH     = os.path.join("assets", "hand_landmarker.task")
LOCK_TIMEOUT_S = 2.0   # seconds without any hand before the lock resets


class HandResult:
    """Simplified result object returned to app.py."""
    def __init__(self, landmarks=None, handedness=None):
        # landmarks: list of 21 [x,y] pixel points, or None
        # handedness: "Left" / "Right" / None
        self.landmarks  = landmarks
        self.handedness = handedness

    @property
    def detected(self):
        return self.landmarks is not None


class HandTracker:
    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Missing {MODEL_PATH} — run: python download_model.py"
            )

        # Detect up to 2 hands so we can choose the dominant one
        options = mp_vision.HandLandmarkerOptions(
            base_options=mp_tasks.BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=mp_vision.RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )
        self._lm           = mp_vision.HandLandmarker.create_from_options(options)
        self._t0           = time.time()
        self._locked_side  = None   # "Left" or "Right" — dominant hand
        self._last_seen    = 0.0    # timestamp of last successful detection

    # ── Public API ────────────────────────────────────────────────────

    def process(self, bgr_frame) -> HandResult:
        """
        Process one BGR frame. Returns a HandResult with the dominant hand's
        landmarks (pixel coords) and handedness string.
        """
        rgb    = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        ts_ms  = int((time.time() - self._t0) * 1000)
        result = self._lm.detect_for_video(mp_img, ts_ms)

        if not result.hand_landmarks:
            # No hand — reset lock after timeout
            if time.time() - self._last_seen > LOCK_TIMEOUT_S:
                self._locked_side = None
            return HandResult()

        self._last_seen = time.time()

        # Pick the dominant hand
        chosen_lms, chosen_side = self._pick_dominant(result)

        pts = [
            [int(lm.x * CAMERA_WIDTH), int(lm.y * CAMERA_HEIGHT)]
            for lm in chosen_lms
        ]
        return HandResult(landmarks=pts, handedness=chosen_side)

    def _pick_dominant(self, result):
        """
        If a hand is already locked, prefer that side.
        Otherwise lock onto the hand with the highest detection confidence.
        Returns (landmark_list, side_string).
        """
        hands = list(zip(result.hand_landmarks, result.handedness))

        if self._locked_side is not None:
            # Try to find the locked side
            for lms, hedness in hands:
                side = hedness[0].category_name   # "Left" or "Right"
                if side == self._locked_side:
                    return lms, side

        # Lock not set (or locked hand disappeared) — pick highest confidence
        best_lms, best_side, best_score = None, None, -1
        for lms, hedness in hands:
            score = hedness[0].score
            side  = hedness[0].category_name
            if score > best_score:
                best_score = score
                best_lms   = lms
                best_side  = side

        self._locked_side = best_side
        return best_lms, best_side

    # ── Static helpers ────────────────────────────────────────────────

    @staticmethod
    def get_finger_states(pts):
        """
        Returns [thumb, index, middle, ring, pinky] bools.
        True = finger is up / extended.

        Thumb uses x-axis (image already mirrored).
        Other fingers use y-axis (tip higher than two joints below = up).
        """
        fingers = [pts[TIP_IDS[0]][0] < pts[TIP_IDS[0] - 1][0]]
        for i in range(1, 5):
            fingers.append(pts[TIP_IDS[i]][1] < pts[TIP_IDS[i] - 2][1])
        return fingers

    @staticmethod
    def distance(p1, p2):
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def close(self):
        self._lm.close()
