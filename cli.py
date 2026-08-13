"""
Command Line Interface (CLI) for Face Recognition Attendance System.
Enables headless / terminal management and camera recognition.
"""

import sys
import os
import argparse
import logging
import cv2
import time

from database import DatabaseManager
from face_engine import FaceEngine
from export import AttendanceExporter
from utils import draw_styled_bbox, play_attendance_beep

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CLI")


def run_camera_recognition(camera_index: int = 0):
    """Runs live webcam face detection & attendance logging."""
    db = DatabaseManager()
    engine = FaceEngine()
    
    if not engine.load_model():
        logger.info("No pre-trained model found. Attempting to train model from dataset...")
        if not engine.train_model():
            logger.warning("No face training dataset found. Run enrollment first to register faces.")

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        logger.error("Failed to open camera index %d", camera_index)
        return

    logger.info("Started live camera attendance scanner. Press 'q' in window to exit.")

    prev_time = time.time()
    fps = 0.0

    while True:
        ret, frame = cap.read()
        if not ret:
            logger.error("Failed to capture video frame.")
            break

        # Calculate FPS
        curr_time = time.time()
        fps = 0.9 * fps + 0.1 * (1.0 / max(0.001, curr_time - prev_time))
        prev_time = curr_time

        # Detect faces
        faces = engine.detect_faces(frame)

        for bbox in faces:
            result = engine.recognize_face(frame, bbox)
            person_id = result["person_id"]
            confidence = result["confidence"]
            is_rec = result["is_recognized"]

            if is_rec:
                person = db.get_person(person_id)
                name = person["name"] if person else person_id
                bbox_color = (0, 220, 100)  # Green
                subtitle = f"{confidence}%"

                # Mark attendance if cooldown passed
                if engine.can_mark_attendance(person_id):
                    att_res = db.mark_attendance(person_id, confidence)
                    engine.record_attendance_cooldown(person_id)
                    play_attendance_beep(success=True)
                    logger.info("ATTENDANCE MARKED: %s (%s) - Status: %s",
                                name, person_id, att_res.get("status"))
            else:
                name = "Unknown"
                bbox_color = (0, 100, 255)  # Red/Orange
                subtitle = "Unrecognized"

            draw_styled_bbox(frame, bbox, name, subtitle=subtitle, color=bbox_color)

        # FPS & Info Overlay
        cv2.putText(frame, f"FPS: {int(fps)} | Faces: {len(faces)}", (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow("Face Attendance CLI Scanner (Press 'q' to Quit)", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    logger.info("Camera scanner stopped.")


def main():
    parser = argparse.ArgumentParser(description="Face Recognition Attendance System CLI")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Scanner command
    scan_parser = subparsers.add_parser("scan", help="Start camera attendance scanner")
    scan_parser.add_argument("--cam", type=int, default=0, help="Camera index (default: 0)")

    # Train command
    subparsers.add_parser("train", help="Train face recognition model from dataset")

    # List command
    subparsers.add_parser("list", help="List all registered persons")

    # Export command
    exp_parser = subparsers.add_parser("export", help="Export attendance logs")
    exp_parser.add_argument("--format", choices=["csv", "excel", "html"], default="csv")
    exp_parser.add_argument("--date", help="Target date YYYY-MM-DD")

    args = parser.parse_args()

    db = DatabaseManager()
    engine = FaceEngine()
    exporter = AttendanceExporter(db)

    if args.command == "scan":
        run_camera_recognition(args.cam)
    elif args.command == "train":
        if engine.train_model():
            print("[SUCCESS] Face model trained successfully.")
        else:
            print("[ERROR] Model training failed. Ensure face images are stored in data/faces/<person_id>/.")
    elif args.command == "list":
        persons = db.get_all_persons()
        print(f"\n--- Registered Persons ({len(persons)}) ---")
        for p in persons:
            print(f"ID: {p['id']} | Name: {p['name']} | Dept: {p['department']} | Role: {p['role']}")
    elif args.command == "export":
        if args.format == "excel":
            path = exporter.export_to_excel(target_date=args.date)
        elif args.format == "html":
            path = exporter.export_to_html(target_date=args.date)
        else:
            path = exporter.export_to_csv(target_date=args.date)
        print(f"[SUCCESS] Exported report to: {path}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
