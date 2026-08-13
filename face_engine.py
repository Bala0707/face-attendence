"""
Core Face Recognition Engine for Face Attendance System.
Handles face detection using OpenCV Haar Cascade, preprocessing, LBPH model training,
real-time recognition, confidence scoring, and anti-duplicate cooldown management.
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
import cv2
import numpy as np

from config import (
    DATA_DIR, CASCADE_FILENAME, FACES_DIR, MODEL_PATH, METADATA_PATH,
    CONFIDENCE_THRESHOLD, ATTENDANCE_COOLDOWN_SECONDS, SAMPLES_PER_PERSON,
    REQUIRED_RECOGNITION_FRAMES, MAX_RECOGNITION_TRACK_DISTANCE
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FaceEngine")


class FaceEngine:
    def __init__(self):
        # Path for Haar Cascade XML
        local_xml_path = DATA_DIR / CASCADE_FILENAME
        cv2_xml_path = Path(cv2.data.haarcascades) / CASCADE_FILENAME

        cascade_target = None
        if local_xml_path.exists():
            cascade_target = str(local_xml_path)
        elif cv2_xml_path.exists():
            cascade_target = str(cv2_xml_path)
        else:
            # Auto-download XML if missing
            try:
                import urllib.request
                url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
                urllib.request.urlretrieve(url, str(local_xml_path))
                cascade_target = str(local_xml_path)
                logger.info("Downloaded Haar Cascade XML to %s", local_xml_path)
            except Exception as e:
                logger.error("Failed to download Haar Cascade XML: %s", e)
                cascade_target = str(local_xml_path)

        self.face_cascade = cv2.CascadeClassifier(cascade_target)
        if self.face_cascade.empty():
            logger.error("Failed to load Haar Cascade from %s", cascade_target)
        else:
            logger.info("Successfully loaded Haar Cascade from %s", cascade_target)

        # Initialize LBPH Face Recognizer if available
        self.has_lbph = hasattr(cv2, "face") and hasattr(cv2.face, "LBPHFaceRecognizer_create")
        if self.has_lbph:
            self.recognizer = cv2.face.LBPHFaceRecognizer_create(
                radius=1, neighbors=8, grid_x=8, grid_y=8
            )
        else:
            self.recognizer = None
            logger.warning("cv2.face not available. Using fallback feature matcher.")

        # ID Mappings: numeric_id (int) <-> person_id (str)
        self.id_to_person: Dict[int, str] = {}
        self.person_to_id: Dict[str, int] = {}

        # Cooldown Tracker: person_id -> timestamp (float)
        self.last_attendance_time: Dict[str, float] = {}

        # Temporal confirmation prevents a single bad camera frame from being accepted.
        self.recognition_tracks: List[Dict[str, Any]] = []

        # Load existing model and metadata if available
        self.load_model()

    # ------------------------------------------------------------------
    # Preprocessing & Detection
    # ------------------------------------------------------------------

    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detects faces in a BGR frame.
        Returns a list of bounding boxes (x, y, w, h).
        """
        if frame is None or frame.size == 0 or self.face_cascade.empty():
            return []

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Apply CLAHE for illumination invariance
        if not hasattr(self, "clahe"):
            self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray_eq = self.clahe.apply(gray)

        faces = self.face_cascade.detectMultiScale(
            gray_eq,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60)
        )

        # Haar detection can miss faces under uneven lighting after equalization.
        # Retry on the original grayscale image before reporting no face.
        if len(faces) == 0:
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=4,
                minSize=(40, 40)
            )

        return [(int(x), int(y), int(w), int(h)) for (x, y, w, h) in faces]

    def preprocess_face(self, frame: np.ndarray, bbox: Tuple[int, int, int, int],
                        target_size: Tuple[int, int] = (160, 160)) -> np.ndarray:
        """Crops, grayscales, denoises with bilateral filter, CLAHE normalizes, and resizes face ROI."""
        x, y, w, h = bbox
        h_frame, w_frame = frame.shape[:2]
        pad_x, pad_y = int(w * 0.05), int(h * 0.05)
        x1 = max(0, x - pad_x)
        y1 = max(0, y - pad_y)
        x2 = min(w_frame, x + w + pad_x)
        y2 = min(h_frame, y + h + pad_y)

        face_roi = frame[y1:y2, x1:x2]
        if face_roi.size == 0:
            return None

        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY) if len(face_roi.shape) == 3 else face_roi
        # Denoise subtle webcam noise
        denoised = cv2.bilateralFilter(gray, 5, 75, 75)

        if not hasattr(self, "clahe"):
            self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray_clahe = self.clahe.apply(denoised)
        resized = cv2.resize(gray_clahe, target_size, interpolation=cv2.INTER_AREA)
        return resized

    # ------------------------------------------------------------------
    # Model Training & Storage
    # ------------------------------------------------------------------

    def train_model(self) -> bool:
        """
        Scans FACES_DIR for registered face images, prepares dataset, and trains LBPH model.
        """
        faces_samples: List[np.ndarray] = []
        labels: List[int] = []

        self.id_to_person.clear()
        self.person_to_id.clear()

        if not os.path.exists(FACES_DIR):
            os.makedirs(FACES_DIR, exist_ok=True)
            return False

        current_label = 1
        person_dirs = [d for d in os.listdir(FACES_DIR) if os.path.isdir(os.path.join(FACES_DIR, d))]

        if not person_dirs:
            logger.info("No registered person face directories found in %s", FACES_DIR)
            return False

        for person_id in person_dirs:
            person_path = os.path.join(FACES_DIR, person_id)
            image_files = [f for f in os.listdir(person_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

            if not image_files:
                continue

            self.id_to_person[current_label] = person_id
            self.person_to_id[person_id] = current_label

            for img_name in image_files:
                img_path = os.path.join(person_path, img_name)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue

                denoised = cv2.bilateralFilter(img, 5, 75, 75)
                if not hasattr(self, "clahe"):
                    self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                img_clahe = self.clahe.apply(denoised)
                resized = cv2.resize(img_clahe, (160, 160))
                
                faces_samples.append(resized)
                labels.append(current_label)

            current_label += 1

        if not faces_samples or not self.has_lbph:
            logger.warning("No face samples found or LBPH not available.")
            return False

        # Train LBPH Model
        self.recognizer.train(faces_samples, np.array(labels, dtype=np.int32))
        
        # Save model and metadata
        self.recognizer.write(str(MODEL_PATH))
        self._save_metadata()
        logger.info("Successfully trained LBPH model with %d samples across %d persons.",
                    len(faces_samples), len(self.id_to_person))
        return True

    def _save_metadata(self) -> None:
        """Saves ID mappings to JSON."""
        meta = {
            "id_to_person": {str(k): v for k, v in self.id_to_person.items()},
            "person_to_id": self.person_to_id
        }
        with open(METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

    def load_model(self) -> bool:
        """Loads trained LBPH model and metadata from disk."""
        if not (os.path.exists(MODEL_PATH) and os.path.exists(METADATA_PATH)):
            return False

        try:
            with open(METADATA_PATH, "r", encoding="utf-8") as f:
                meta = json.load(f)
                self.id_to_person = {int(k): v for k, v in meta.get("id_to_person", {}).items()}
                self.person_to_id = meta.get("person_to_id", {})

            if self.has_lbph:
                self.recognizer.read(str(MODEL_PATH))
                logger.info("Loaded LBPH model with %d registered persons.", len(self.id_to_person))
                return True
        except Exception as e:
            logger.error("Error loading face model: %s", e)
        return False

    # ------------------------------------------------------------------
    # Real-Time Recognition
    # ------------------------------------------------------------------

    def recognize_face(self, frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> Dict[str, Any]:
        """
        Recognizes a face in a frame given its bounding box.
        Returns dict with person_id, match_confidence (0-100%), distance, and raw_status.
        """
        if not self.has_lbph or not self.id_to_person:
            return {
                "person_id": "Unknown",
                "confidence": 0.0,
                "distance": 999.0,
                "is_recognized": False
            }

        face_roi = self.preprocess_face(frame, bbox)
        if face_roi is None:
            return {
                "person_id": "Unknown",
                "confidence": 0.0,
                "distance": 999.0,
                "is_recognized": False
            }

        # Predict using LBPH recognizer
        label, distance = self.recognizer.predict(face_roi)

        # Strict Matching Cutoff: borderline LBPH matches remain Unknown.
        if distance <= CONFIDENCE_THRESHOLD and label in self.id_to_person:
            person_id = self.id_to_person[label]
            x, y, w, h = bbox
            center = (x + w // 2, y + h // 2)
            track = next(
                (
                    item for item in self.recognition_tracks
                    if abs(center[0] - item["center"][0]) <= MAX_RECOGNITION_TRACK_DISTANCE
                    and abs(center[1] - item["center"][1]) <= MAX_RECOGNITION_TRACK_DISTANCE
                ),
                None
            )
            if track is None:
                track = {"center": center, "person_id": person_id, "frames": 1}
                self.recognition_tracks.append(track)
            elif track["person_id"] == person_id:
                track["center"] = center
                track["frames"] += 1
            else:
                track.update({"center": center, "person_id": person_id, "frames": 1})
            frame_count = track["frames"]

            if len(self.recognition_tracks) > 10:
                self.recognition_tracks = self.recognition_tracks[-10:]

            if frame_count < REQUIRED_RECOGNITION_FRAMES:
                return {
                    "person_id": "Unknown",
                    "confidence": 0.0,
                    "distance": round(distance, 1),
                    "is_recognized": False
                }

            # Map distance 0..52 -> 100%..60% confidence
            match_confidence = max(60.0, min(100.0, 100.0 - (distance / CONFIDENCE_THRESHOLD) * 40.0))
            return {
                "person_id": person_id,
                "confidence": round(match_confidence, 1),
                "distance": round(distance, 1),
                "is_recognized": True
            }
        else:
            return {
                "person_id": "Unknown",
                "confidence": 0.0,
                "distance": round(distance, 1),
                "is_recognized": False
            }

    # ------------------------------------------------------------------
    # Cooldown Logic
    # ------------------------------------------------------------------

    def can_mark_attendance(self, person_id: str) -> bool:
        """
        Checks whether attendance can be marked for person_id based on cooldown window.
        """
        if person_id == "Unknown":
            return False

        now = time.time()
        last_time = self.last_attendance_time.get(person_id, 0)
        if (now - last_time) >= ATTENDANCE_COOLDOWN_SECONDS:
            return True
        return False

    def record_attendance_cooldown(self, person_id: str) -> None:
        """Updates timestamp for attendance mark."""
        self.last_attendance_time[person_id] = time.time()

    # ------------------------------------------------------------------
    # Sample Capture Helper
    # ------------------------------------------------------------------

    def save_sample_face(self, person_id: str, frame: np.ndarray, bbox: Tuple[int, int, int, int], sample_idx: int) -> Optional[str]:
        """Saves a cropped face sample for training dataset."""
        face_roi = self.preprocess_face(frame, bbox)
        if face_roi is None:
            return None

        person_dir = os.path.join(FACES_DIR, person_id)
        os.makedirs(person_dir, exist_ok=True)

        filename = f"sample_{sample_idx:03d}_{int(time.time())}.jpg"
        file_path = os.path.join(person_dir, filename)
        cv2.imwrite(file_path, face_roi)
        return file_path


if __name__ == "__main__":
    engine = FaceEngine()
    print("Face Engine initialized successfully.")
