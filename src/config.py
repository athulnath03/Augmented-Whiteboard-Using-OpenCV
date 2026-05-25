"""
AirBoard Configuration
"""

# --- Camera ---
CAMERA_INDEX  = 1
CAMERA_WIDTH  = 640
CAMERA_HEIGHT = 480
CAMERA_FPS    = 30

# --- MediaPipe ---
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE  = 0.5
MAX_NUM_HANDS            = 2    # detect 2 but we'll pick the dominant one

# --- Drawing ---
DEFAULT_THICKNESS = 15
DEFAULT_COLOR     = (0, 0, 255)   # BGR red

# --- Header bar (in raw camera pixels, 640 wide) ---
HEADER_HEIGHT = 80

# Colour zones in raw camera pixel x-coords (640px wide header)
# Red swatch centre ~116, Blue ~250, Green ~382, Eraser ~521
COLOR_ZONES = [
    ( 72, 160, (0,   0,   255)),   # Red
    (205, 295, (255, 0,   0  )),   # Blue
    (338, 428, (0,   255, 0  )),   # Green
    (472, 562, (0,   0,   0  )),   # Eraser (draws white on canvas)
]

# --- Finger tip landmark indices ---
TIP_IDS = [4, 8, 12, 16, 20]
