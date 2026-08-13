# Face Recognition Attendance System (Python)

A modern, production-grade **Face Recognition Attendance System** built with Python, OpenCV, CustomTkinter, and SQLite.

---

## 🌟 Key Features

1. **Robust Real-Time Face Recognition**:
   - OpenCV Haar Cascade Face Detector with illumination normalization (CLAHE).
   - LBPH (Local Binary Patterns Histograms) Face Recognizer with confidence score metrics.
   - Built-in anti-duplicate attendance cooldown logic (prevents spamming logs for the same person).

2. **Modern Dark Dashboard GUI**:
   - **Dashboard**: Dynamic metrics for Total Enrolled, Present Today, Late Today, and Absent Today.
   - **Live Scanner**: Camera video feed with HUD bounding boxes, identified names, confidence badges, and audio sound alerts (`winsound`).
   - **Enrollment**: Interactive student/employee registration via live webcam auto-snapshot capture or photo file upload, with automated model training.
   - **Attendance Logs**: Search logs by Name/ID, date range filtering, manual attendance override, and single-click Excel/CSV exporter.
   - **Registered Users**: User management table with one-click record deletion.

3. **Headless / CLI Mode**:
   - Run background attendance camera scanners or batch management commands without launching the GUI.

4. **Multi-Format Exporting**:
   - Export structured logs to **Excel (`.xlsx`)** with formatting, **CSV**, or a styled **HTML Summary Report**.

---

## 📦 Project Structure

```
d:\faceattendance\
├── config.py             # System configuration, paths, thresholds, GUI settings
├── database.py           # SQLite DB manager (Persons & Attendance logs schema + CRUD)
├── face_engine.py        # Face detection, ROI preprocessing, LBPH model training & scoring
├── export.py             # Data exporter (CSV, Excel, HTML reports)
├── utils.py              # Audio alerts, styled bounding box renderer, camera helper
├── gui.py                # Modern CustomTkinter desktop GUI application
├── cli.py                # Command Line Interface (CLI) runner
├── main.py               # Main application entry point
├── requirements.txt      # Dependency specification
└── README.md             # Complete documentation
```

---

## 🚀 Quick Start Guide

### 1. Installation

Install required dependencies:

```bash
pip install -r requirements.txt
```

### 2. Launch GUI Application

Run the application dashboard:

```bash
python main.py
```

### 3. Launch CLI Mode

To run in command-line mode:

```bash
# List all registered persons
python main.py --cli list

# Start live camera scanner
python main.py --cli scan

# Train model from face dataset
python main.py --cli train

# Export attendance report
python main.py --cli export --format excel
```

---

## 💡 How to Register New Users

1. Open the app (`python main.py`).
2. Go to the **👤 Enrollment** tab.
3. Enter **Person ID** (e.g. `EMP001` or `STU101`) and **Full Name**.
4. Click **📸 Capture Samples via Webcam** (captures 15 face samples automatically while you turn your head slightly), OR click **📁 Import Photos from File**.
5. Click **⚙️ Train Face Recognition Model**.
6. Switch to **📹 Live Scanner** and click **▶ Start Camera Scanner** to begin real-time attendance logging!

---

## ⚙️ Configuration & Customization

Edit `config.py` to customize settings:

- `CONFIDENCE_THRESHOLD`: Set LBPH distance match limit (default: `75.0`).
- `ATTENDANCE_COOLDOWN_SECONDS`: Cooldown window before re-marking attendance (default: `300` seconds / 5 mins).
- `DEFAULT_START_TIME`: Official start time for determining "Present" vs "Late" status (default: `"09:00:00"`).
