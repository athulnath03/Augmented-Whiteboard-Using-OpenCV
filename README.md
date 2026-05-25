# AirBoard — Real-Time Gesture-Controlled Whiteboard Using OpenCV

Draw in the air using natural hand gestures.

AirBoard transforms a webcam into an interactive whiteboard using **MediaPipe Hand Tracking + OpenCV** with real-time gesture control — no stylus or touch required.

![Python](https://img.shields.io/badge/Python-3.9--3.11-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Tasks-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

> Final Year Major Project  
> Team of 4  
> Computer Vision · Human–Computer Interaction

---

## Demo

> Add screenshots or GIF here

```md
assets/demo.gif
assets/screenshot.png
```

---

## Features

- Real-time hand tracking using MediaPipe Tasks API
- Air drawing with gesture-based controls
- Dominant-hand locking to reduce jitter
- Continuous brush-size control
- Artifact-free erasing via bitwise compositing
- 20-level undo history
- Split-screen camera + canvas UI
- Save drawings instantly
───────────┬──────────────────────────────────┬────────────────────────────────┐
│ Challenge       │ Typical Projects                 │ AirBoard                       │
├─────────────────┼──────────────────────────────────┼────────────────────────────────┤
│ Hand Jitter     │ Cursor switches between hands    │ Dominant hand locking          │
│ Gesture Control │ Binary gestures only             │ Multiple gesture interactions  │
│ Drawing Quality │ Eraser artifacts                 │ Bitwise compositing            │
│ User Experience │ Overlay-only layout              │ Split-screen interface         │
│ Undo Support    │ Limited history                  │ 20-level undo                  │
└─────────────────┴──────────────────────────────────┴────────────────────────────────┘
```

---

## Gesture Controls

```text
┌────────────────────────┬────────────────┬──────────────────────────┐
│ Gesture                │ Action         │ Description              │
├────────────────────────┼────────────────┼──────────────────────────┤
│ Index only             │ Draw           │ Draw naturally           │
│ Index + Middle         │ Pen Up         │ Move without drawing     │
│ Index + Middle + Ring  │ Select Color   │ Choose toolbar color     │
│ Index + Pinky          │ Clear Canvas   │ Reset drawing            │
│ Thumb + Index          │ Brush Size     │ Adjust size dynamically  │
│ S Key                  │ Save           │ Export image             │
│ Q Key                  │ Quit           │ Exit application         │
└────────────────────────┴────────────────┴──────────────────────────┘
```

---

# Quick Start

## 1. Clone Repository

```bash
git clone https://github.com/athulnath03/Augmented-Whiteboard-Using-OpenCV.git

cd Augmented-Whiteboard-Using-OpenCV
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If installation fails:

```bash
pip install --upgrade mediapipe opencv-python numpy
```

---

## 4. Download Model

```bash
python download_model.py
```

Creates:

```text
assets/hand_landmarker.task
```

---

## 5. Generate Toolbar Assets

```bash
python generate_headers.py
```

---

## 6. Run

```bash
python main.py
```

Controls:

```text
Q → Quit
S → Save
```

---

## Project Structure

```text
airboard/
│
├── main.py
├── download_model.py
├── generate_headers.py
├── requirements.txt
├── README.md
│
├── assets/
│   └── hand_landmarker.task
│
├── headers/
│
├── saves/canvas_20260525_123924.png
│
└── src/
    ├── config.py
    ├── hand_tracker.py
    ├── canvas.py
    ├── toolbar.py
    └── app.py
```

---

## Architecture

```text
Camera
  ↓
MediaPipe Hand Detection
  ↓
Gesture Classification
  ↓
Canvas + Toolbar
  ↓
Frame Compositing
  ↓
Display
```

---

## Performance

```text
┌─────────────────┬─────────┬───────────────────────┐
│ Metric          │ Value   │ Notes                 │
├─────────────────┼─────────┼───────────────────────┤
│ FPS             │ 28–30   │ Stable                │
│ Latency         │ ~50 ms  │ Detection → Render    │
│ Memory Usage    │ ~300 MB │ Includes model        │
│ Model Size      │ 238 MB  │ MediaPipe Task Model  │
└─────────────────┴─────────┴───────────────────────┘
```

---

## Configuration

Edit:

```text
src/config.py
```

Example:

```python
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

DEFAULT_THICKNESS = 15

MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.5
```

---

## Troubleshooting

### Camera not detected

```text
Cannot open camera
```

Try:

- Check permissions
- Change `CAMERA_INDEX`
- Close other camera apps

---

### Model missing

```bash
python download_model.py
```

---

### MediaPipe issue

Supported:

```text
Python 3.9–3.11
```

---

## Future Improvements

- [ ] Multi-hand drawing
- [ ] ML gesture recognition
- [ ] SVG export
- [ ] Session recording
- [ ] Undo / Redo UI
- [ ] Custom gestures

---

## Tech Stack

- Python
- OpenCV
- MediaPipe
- NumPy

---

## Contributing

Issues and pull requests are welcome.

```bash
fork → clone → modify → PR
```

---

## License

MIT License

See `LICENSE`.

---

## Author

GitHub: **athulnath03**

⭐ If this project helped you, consider starring the repository.