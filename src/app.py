"""
app.py — Fullscreen split layout.

GESTURE MAP
───────────────────────────────────────────────────
☝  Index only              → DRAW (pen down)
✌  Index + Middle          → PEN UP (move freely)
🖖 Index + Middle + Ring   → SELECT colour / tool
🤘 Index + Pinky           → CLEAR canvas
🤏 Thumb + Index only      → BRUSH SIZE (spread = bigger)
───────────────────────────────────────────────────
s = save   q = quit
"""

import os
import cv2
import numpy as np
from collections import deque
from datetime import datetime

from src.config import CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_FPS
from src.hand_tracker import HandTracker
from src.canvas       import Canvas
from src.toolbar      import Toolbar

SMOOTH = 6


class AirBoard:
    def __init__(self):
        self.tracker     = HandTracker()
        self.canvas      = None
        self.toolbar     = Toolbar()
        self._xp, self._yp = 0, 0
        self._xs         = deque(maxlen=SMOOTH)
        self._ys         = deque(maxlen=SMOOTH)
        self._mode       = "standby"
        self._is_drawing = False
        self._sw = self._sh = 0
        self._cam_dw = self._cvs_w = self._cvs_h = 0

    # ── Main loop ────────────────────────────────────────────────────

    def run(self):
        cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  CAMERA_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS,          CAMERA_FPS)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open camera {CAMERA_INDEX}")

        cv2.namedWindow("AirBoard", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("AirBoard", cv2.WND_PROP_FULLSCREEN,
                              cv2.WINDOW_FULLSCREEN)
        cv2.imshow("AirBoard", np.zeros((100, 100, 3), np.uint8))
        cv2.waitKey(1)
        _, _, sw, sh = cv2.getWindowImageRect("AirBoard")

        cam_dw = int(CAMERA_WIDTH * sh / CAMERA_HEIGHT)
        cvs_w  = sw - cam_dw - 3
        cvs_h  = sh

        self._sw, self._sh        = sw, sh
        self._cam_dw              = cam_dw
        self._cvs_w, self._cvs_h = cvs_w, cvs_h
        self.canvas               = Canvas(cvs_w, cvs_h)
        self.toolbar.resize(cam_dw, sh)

        os.makedirs("saves", exist_ok=True)
        print(f"Screen {sw}x{sh} | camera pane {cam_dw}x{sh} | canvas {cvs_w}x{sh}")
        print("  ☝  Index only          → DRAW")
        print("  ✌  Index+Middle        → PEN UP")
        print("  🖖 Index+Middle+Ring   → SELECT colour")
        print("  🤘 Index+Pinky         → CLEAR")
        print("  🤏 Thumb+Index         → BRUSH SIZE")
        print("  s=save  q=quit")

        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break

                frame  = cv2.flip(frame, 1)
                result = self.tracker.process(frame)   # returns HandResult

                if result.detected:
                    pts     = result.landmarks         # list of 21 [x,y] in camera pixels
                    fingers = HandTracker.get_finger_states(pts)
                    frame   = self._dispatch(frame, pts, fingers)
                else:
                    self._mode = "no hand"
                    self._end_stroke()

                cv2.imshow("AirBoard", self._build_display(frame))

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                elif key == ord("s"):
                    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
                    path = os.path.join("saves", f"canvas_{ts}.png")
                    self.canvas.save(path)
                    print(f"  Saved → {os.path.abspath(path)}")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.tracker.close()

    # ── Gesture dispatcher ───────────────────────────────────────────

    def _dispatch(self, frame, pts, fingers):
        thumb, idx, mid, ring, pinky = fingers

        # 🤘 Index + Pinky, middle + ring down → CLEAR
        if idx and pinky and not mid and not ring:
            return self._gesture_clear(frame, pts)

        # 🖖 Index + Middle + Ring → SELECT
        if idx and mid and ring and not pinky:
            return self._gesture_select(frame, pts)

        # 🤏 Thumb + Index only → SIZE
        if thumb and idx and not mid and not ring and not pinky:
            return self._gesture_size(frame, pts)

        # ✌ Index + Middle only → PEN UP
        if idx and mid and not ring and not pinky:
            return self._gesture_penup(frame, pts)

        # ☝ Index only → DRAW
        if idx and not thumb and not mid and not ring and not pinky:
            return self._gesture_draw(frame, pts)

        # Anything else → STANDBY
        self._mode = "standby"
        self._end_stroke()
        return frame

    # ── Individual gestures ──────────────────────────────────────────

    def _gesture_draw(self, frame, pts):
        self._mode = "draw"
        x1, y1 = pts[8]

        self._xs.append(x1); self._ys.append(y1)
        sx = int(sum(self._xs) / len(self._xs))
        sy = int(sum(self._ys) / len(self._ys))

        dc = (220,220,220) if self.canvas.color==(0,0,0) else self.canvas.color
        r  = max(3, self.canvas.thickness // 2)
        cv2.circle(frame, (sx, sy), r,   dc,          cv2.FILLED)
        cv2.circle(frame, (sx, sy), r+1, (30,30,30),  1)

        cx = int(sx * self._cvs_w / CAMERA_WIDTH)
        cy = int(sy * self._cvs_h / CAMERA_HEIGHT)

        if self._xp and self._yp:
            self.canvas.draw_line((self._xp, self._yp), (cx, cy),
                                  first_point=not self._is_drawing)
            self._is_drawing = True
        self._xp, self._yp = cx, cy
        return frame

    def _gesture_penup(self, frame, pts):
        self._mode = "pen up"
        self._end_stroke()
        x1, y1 = pts[8]
        x2, y2 = pts[12]
        cv2.line(frame, (x1,y1), (x2,y2), (200,200,200), 2)
        cv2.circle(frame, (x1,y1), 8, (200,200,200), 2)
        return frame

    def _gesture_select(self, frame, pts):
        self._mode = "select"
        self._end_stroke()
        x1, y1 = pts[8]
        x2, y2 = pts[12]
        x3, y3 = pts[16]
        cv2.line(frame, (x1,y1), (x2,y2), self.toolbar.color, 2)
        cv2.line(frame, (x2,y2), (x3,y3), self.toolbar.color, 2)
        if self.toolbar.try_select(x1, y1):
            self.canvas.color = self.toolbar.color
        return frame

    def _gesture_size(self, frame, pts):
        self._mode = "size"
        self._end_stroke()
        x1, y1 = pts[8]
        x3, y3 = pts[4]
        dist = HandTracker.distance([x1,y1], [x3,y3])
        self.canvas.thickness = max(2, int(dist / 4))
        mx, my = int((x1+x3)/2), int((y1+y3)/2)
        dc = (220,220,220) if self.canvas.color==(0,0,0) else self.canvas.color
        cv2.circle(frame, (mx,my), max(1, self.canvas.thickness//2), dc, -1)
        cv2.circle(frame, (mx,my), max(1, self.canvas.thickness//2), (60,60,60), 1)
        cv2.line(frame, (x1,y1), (x3,y3), (120,120,120), 1)
        cv2.putText(frame, f"size {self.canvas.thickness}",
                    (mx+10, my-10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.55, (220,220,220), 1)
        return frame

    def _gesture_clear(self, frame, pts):
        self._mode = "clear"
        self._end_stroke()
        x1, y1 = pts[8]
        x4, y4 = pts[20]
        cv2.line(frame, (x1,y1), (x4,y4), (0,80,255), 3)
        cv2.putText(frame, "CLEAR!", (min(x1,x4)-10, min(y1,y4)-15),
                    cv2.FONT_HERSHEY_DUPLEX, 0.9, (0,80,255), 2)
        self.canvas.clear()
        return frame

    def _end_stroke(self):
        self._xp, self._yp = 0, 0
        self._xs.clear(); self._ys.clear()
        self._is_drawing = False

    # ── Display ──────────────────────────────────────────────────────

    def _build_display(self, cam_frame):
        cam = cv2.resize(cam_frame, (self._cam_dw, self._sh))

        # Composite canvas strokes onto camera preview
        canvas_img   = self.canvas.get_display()
        canvas_small = cv2.resize(canvas_img, (self._cam_dw, self._sh))
        gray         = cv2.cvtColor(canvas_small, cv2.COLOR_BGR2GRAY)
        _, mask      = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        mask3        = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        strokes      = cv2.bitwise_and(canvas_small, mask3)
        cam_bg       = cv2.bitwise_and(cam, cv2.bitwise_not(mask3))
        cam          = cv2.addWeighted(cam_bg, 1.0, strokes, 0.85, 0)

        cam = self.toolbar.apply(cam)

        # Mode badge
        badge_col = {
            "draw":    (0,210,0),
            "pen up":  (200,200,200),
            "select":  (210,210,0),
            "size":    (0,180,255),
            "clear":   (0,80,255),
            "standby": (120,120,120),
            "no hand": (60,60,60),
        }.get(self._mode, (120,120,120))
        cv2.putText(cam, self._mode.upper(),
                    (14, self._sh - 44),
                    cv2.FONT_HERSHEY_DUPLEX, 0.8, badge_col, 2)

        # Brush dot (bottom-right of camera pane)
        dc   = (220,220,220) if self.canvas.color==(0,0,0) else self.canvas.color
        drad = max(6, self.canvas.thickness // 2)
        cv2.circle(cam,
                   (self._cam_dw - drad - 14, self._sh - drad - 14),
                   drad, dc, -1)
        cv2.circle(cam,
                   (self._cam_dw - drad - 14, self._sh - drad - 14),
                   drad, (60,60,60), 1)

        # Canvas pane
        right = self.canvas.get_display()
        cv2.putText(right, "s=save   q=quit",
                    (10, self._cvs_h - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180,180,180), 1)

        divider = np.full((self._sh, 3, 3), 100, dtype=np.uint8)
        return np.hstack([cam, divider, right])
