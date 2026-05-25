"""
AirBoard - Augmented Whiteboard Using OpenCV & MediaPipe
Entry point. Run this file to start the application.
"""

from src.app import AirBoard

if __name__ == "__main__":
    app = AirBoard()
    app.run()
