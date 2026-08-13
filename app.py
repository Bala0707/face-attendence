"""
Flask REST API Backend for TanStack Face Attendance Web Application.
Bridges WebRTC browser frontend directly with OpenCV FaceEngine and SQLite DatabaseManager.
"""

import os
import base64
import logging
from typing import Dict, Any, List
import cv2
import numpy as np
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

from database import DatabaseManager
from face_engine import FaceEngine
from export import AttendanceExporter
from config import EXPORTS_DIR, FACES_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FlaskAPI")

app = Flask(__name__)
CORS(app)

# Initialize Core Backend Components
db = DatabaseManager()
engine = FaceEngine()
exporter = AttendanceExporter(db)

def decode_base64_image(base64_str: str) -> np.ndarray:
    """Decodes base64 data URI string to BGR OpenCV numpy image array."""
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]
    image_bytes = base64.b64decode(base64_str)
    np_arr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return frame

# ----------------------------------------------------------------------
# API Endpoints
# ----------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ONLINE",
        "version": "2.5.0-TanStack",
        "has_model": bool(engine.id_to_person)
    })

@app.route("/api/stats", methods=["GET"])
def get_stats():
    target_date = request.args.get("date")
    return jsonify(db.get_dashboard_stats(target_date=target_date))

@app.route("/api/persons", methods=["GET"])
def get_persons():
    return jsonify(db.get_all_persons())

@app.route("/api/persons", methods=["POST"])
def add_person():
    data = request.json or {}
    p_id = data.get("id", "").strip()
    name = data.get("name", "").strip()
    
    if not p_id or not name:
        return jsonify({"success": False, "message": "Person ID and Name are required"}), 400

    success = db.add_person(
        person_id=p_id,
        name=name,
        department=data.get("department", "").strip(),
        role=data.get("role", "Student").strip(),
        email=data.get("email", "").strip()
    )
    return jsonify({"success": success})

@app.route("/api/persons/<person_id>", methods=["DELETE"])
def delete_person(person_id):
    import shutil
    success = db.delete_person(person_id)
    
    # Delete sample photos folder
    p_dir = FACES_DIR / person_id
    if p_dir.exists():
        shutil.rmtree(p_dir, ignore_errors=True)

    # Retrain engine
    engine.train_model()
    return jsonify({"success": success})

@app.route("/api/logs", methods=["GET"])
def get_logs():
    target_date = request.args.get("date")
    search_q = request.args.get("search")
    department = request.args.get("department")
    return jsonify(db.get_attendance_logs(target_date=target_date, person_id=search_q, department=department))

@app.route("/api/logs/<int:log_id>", methods=["DELETE"])
def delete_log(log_id):
    success = db.delete_attendance_log(log_id)
    return jsonify({"success": success})

@app.route("/api/logs/clear", methods=["POST"])
def clear_logs():
    data = request.json or {}
    target_date = data.get("date")
    count = db.clear_attendance_logs(target_date=target_date)
    return jsonify({"success": True, "count": count})

@app.route("/api/mark-attendance", methods=["POST"])
def mark_attendance():
    data = request.json or {}
    p_id = data.get("person_id")
    confidence = float(data.get("confidence", 95.0))
    if not p_id:
        return jsonify({"success": False, "message": "Person ID is required"}), 400

    res = db.mark_attendance(p_id, confidence)
    return jsonify(res)

@app.route("/api/recognize-frame", methods=["POST"])
def recognize_frame():
    """
    Receives base64 camera frame from browser, detects faces using OpenCV,
    recognizes registered individuals, marks attendance in SQLite, and returns bounding box details.
    """
    data = request.json or {}
    image_data = data.get("image")
    if not image_data:
        return jsonify({"faces": []})

    try:
        frame = decode_base64_image(image_data)
        if frame is None:
            return jsonify({"faces": []})

        detected_faces = engine.detect_faces(frame)
        results = []

        for bbox in detected_faces:
            rec_res = engine.recognize_face(frame, bbox)
            person_id = rec_res["person_id"]
            confidence = rec_res["confidence"]
            is_rec = rec_res["is_recognized"]

            attendance_marked = False
            status = "Unknown"
            name = "Unknown"

            if is_rec:
                person = db.get_person(person_id)
                name = person["name"] if person else person_id

                if engine.can_mark_attendance(person_id):
                    att_res = db.mark_attendance(person_id, confidence)
                    engine.record_attendance_cooldown(person_id)
                    attendance_marked = True
                    status = att_res.get("status", "Present")
                else:
                    status = "Present (Recorded)"

            results.append({
                "bbox": [int(b) for b in bbox],
                "person_id": person_id,
                "name": name,
                "confidence": confidence,
                "is_recognized": is_rec,
                "attendance_marked": attendance_marked,
                "status": status
            })

        return jsonify({"faces": results})
    except Exception as e:
        logger.error("Error recognizing frame: %s", e)
        return jsonify({"faces": [], "error": str(e)}), 500

@app.route("/api/enroll-sample", methods=["POST"])
def enroll_sample():
    """Captures and saves a face sample photo from base64 webcam frame."""
    data = request.json or {}
    p_id = data.get("person_id")
    image_data = data.get("image")
    sample_idx = int(data.get("sample_idx", 0))

    if not p_id or not image_data:
        return jsonify({"success": False, "message": "Missing arguments"}), 400

    try:
        frame = decode_base64_image(image_data)
        if frame is None:
            return jsonify({"success": False, "message": "Invalid image"}), 400

        faces = engine.detect_faces(frame)
        if not faces:
            return jsonify({"success": False, "message": "No face detected in frame"})

        bbox = faces[0]
        file_path = engine.save_sample_face(p_id, frame, bbox, sample_idx)
        return jsonify({"success": bool(file_path), "path": file_path})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/train", methods=["POST"])
def train_model():
    success = engine.train_model()
    return jsonify({"success": success})

@app.route("/api/export/<format_type>", methods=["GET"])
def export_logs(format_type):
    target_date = request.args.get("date")
    if format_type == "excel":
        filepath = exporter.export_to_excel(target_date=target_date)
        mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif format_type == "html":
        filepath = exporter.export_to_html(target_date=target_date)
        mimetype = "text/html"
    else:
        filepath = exporter.export_to_csv(target_date=target_date)
        mimetype = "text/csv"

    return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath), mimetype=mimetype)

if __name__ == "__main__":
    logger.info("Starting Flask API Server on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
