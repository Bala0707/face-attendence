"""
Configuration file for Face Recognition Attendance System.
Contains default parameters, paths, thresholds, and styling settings.
"""

import os
from pathlib import Path

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Data Directories
DATA_DIR = BASE_DIR / "data"
FACES_DIR = DATA_DIR / "faces"
MODELS_DIR = DATA_DIR / "models"
EXPORTS_DIR = BASE_DIR / "exports"

# Create required directories automatically
for directory in [DATA_DIR, FACES_DIR, MODELS_DIR, EXPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Database Configuration
DB_PATH = DATA_DIR / "attendance_system.db"

# Model Configuration
CASCADE_FILENAME = "haarcascade_frontalface_default.xml"
MODEL_PATH = MODELS_DIR / "lbph_model.yml"
METADATA_PATH = MODELS_DIR / "face_metadata.json"

# Face Recognition Settings
# Strict LBPH distance threshold for high precision (lower distance = stricter match)
# A lower threshold rejects more borderline matches as Unknown.
CONFIDENCE_THRESHOLD = 75.0  # Max distance to consider a valid match
REQUIRED_RECOGNITION_FRAMES = 3  # Consecutive matching frames before acceptance
MAX_RECOGNITION_TRACK_DISTANCE = 100  # Maximum face-center movement between frames
SAMPLES_PER_PERSON = 20      # Number of sample face photos captured during registration

# Attendance Logic
ATTENDANCE_COOLDOWN_SECONDS = 300  # 5 minutes cooldown before re-marking attendance
DEFAULT_START_TIME = "09:00:00"     # Standard start time to calculate 'Late' status

# Camera Configuration
DEFAULT_CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30

# GUI Visual Settings
APP_TITLE = "Face Recognition Attendance System"
APP_GEOMETRY = "1200x750"
THEME_MODE = "Dark"                 # "Dark", "Light", or "System"
COLOR_PRIMARY = "#1f538d"
COLOR_ACCENT = "#2fa572"
COLOR_WARNING = "#e67e22"
COLOR_DANGER = "#e74c3c"
COLOR_BACKGROUND_DARK = "#1a1a1a"
COLOR_CARD_DARK = "#2b2b2b"
