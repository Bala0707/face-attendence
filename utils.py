"""
Utility functions for Face Recognition Attendance System.
Handles audio alerts, camera capture helpers, frame annotation, and formatting.
"""

import sys
import time
import logging
from typing import Tuple, Optional
import cv2
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Utils")


def play_attendance_beep(success: bool = True) -> None:
    """Plays an audio sound alert when attendance is marked."""
    try:
        if sys.platform.startswith("win"):
            import winsound
            if success:
                winsound.Beep(1000, 200)  # High pitch beep for success
            else:
                winsound.Beep(400, 400)   # Low pitch beep for warning/failure
    except Exception as e:
        logger.debug("Beep notification skipped: %s", e)


def draw_styled_bbox(frame: np.ndarray, bbox: Tuple[int, int, int, int],
                     title: str, subtitle: str = "",
                     color: Tuple[int, int, int] = (0, 255, 0),
                     thickness: int = 2) -> np.ndarray:
    """
    Draws a modern HUD-style bounding box around detected face with corners and top label badge.
    """
    x, y, w, h = bbox
    l = int(min(w, h) * 0.2)  # Corner line length

    # Draw main box rectangle
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 1, cv2.LINE_AA)

    # Top-Left corner accent
    cv2.line(frame, (x, y), (x + l, y), color, thickness, cv2.LINE_AA)
    cv2.line(frame, (x, y), (x, y + l), color, thickness, cv2.LINE_AA)

    # Top-Right corner accent
    cv2.line(frame, (x + w, y), (x + w - l, y), color, thickness, cv2.LINE_AA)
    cv2.line(frame, (x + w, y), (x + w, y + l), color, thickness, cv2.LINE_AA)

    # Bottom-Left corner accent
    cv2.line(frame, (x, y + h), (x + l, y + h), color, thickness, cv2.LINE_AA)
    cv2.line(frame, (x, y + h), (x, y + h - l), color, thickness, cv2.LINE_AA)

    # Bottom-Right corner accent
    cv2.line(frame, (x + w, y + h), (x + w - l, y + h), color, thickness, cv2.LINE_AA)
    cv2.line(frame, (x + w, y + h), (x + w, y + h - l), color, thickness, cv2.LINE_AA)

    # Label Badge Background
    label_text = title.strip()
    if subtitle:
        label_text += f" ({subtitle})"

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.55
    text_thickness = 1

    (text_w, text_h), baseline = cv2.getTextSize(label_text, font, font_scale, text_thickness)
    
    badge_y1 = max(0, y - text_h - 10)
    badge_y2 = y
    badge_x1 = x
    badge_x2 = x + text_w + 12

    # Draw solid filled label box
    cv2.rectangle(frame, (badge_x1, badge_y1), (badge_x2, badge_y2), color, -1)
    
    # Text inside badge (White text for contrast)
    cv2.putText(
        frame,
        label_text,
        (x + 6, y - 6),
        font,
        font_scale,
        (255, 255, 255),
        text_thickness,
        cv2.LINE_AA
    )

    return frame


def get_available_cameras(max_tested: int = 4) -> list:
    """Returns a list of working camera device indices."""
    available = []
    for index in range(max_tested):
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW if sys.platform.startswith("win") else cv2.CAP_ANY)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                available.append(index)
            cap.release()
    return available if available else [0]


if __name__ == "__main__":
    print("Utils module loaded. Available cameras:", get_available_cameras(2))
