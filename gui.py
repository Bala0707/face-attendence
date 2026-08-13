"""
Modern Desktop GUI for Face Recognition Attendance System built with CustomTkinter.
Includes SaaS Landing Home Page, dynamic dashboard stats, live camera video feed,
student/employee enrollment, logs viewer with date filter, manual override, and report export.
"""

import sys
import os
import time
import threading
from datetime import datetime, date
from pathlib import Path
from typing import Optional, List, Dict, Any

import cv2
from PIL import Image, ImageTk
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog

from config import (
    APP_TITLE, APP_GEOMETRY, THEME_MODE,
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_WARNING, COLOR_DANGER,
    COLOR_BACKGROUND_DARK, COLOR_CARD_DARK, FACES_DIR, SAMPLES_PER_PERSON
)
from database import DatabaseManager
from face_engine import FaceEngine
from export import AttendanceExporter
from utils import draw_styled_bbox, play_attendance_beep, get_available_cameras

ctk.set_appearance_mode(THEME_MODE)
ctk.set_default_color_theme("blue")

# Modern SaaS Design Tokens
COLOR_BG = "#0F111A"            # Obsidian Deep Dark
COLOR_CARD_BG = "#1A1D2E"       # Glassmorphic Card Background
COLOR_HEADER_BG = "#141724"     # Top Navigation Bar
COLOR_BORDER = "#2A2E45"        # Subtle Border Outline
COLOR_CYAN = "#06B6D4"          # Accent Cyan
COLOR_BLUE = "#2563EB"          # Primary Blue
COLOR_GREEN = "#10B981"         # Success Emerald
COLOR_AMBER = "#F59E0B"         # Warning Amber
COLOR_RED = "#EF4444"           # Danger Red
COLOR_PURPLE = "#8B5CF6"        # SaaS Accent Purple
COLOR_TEXT_MAIN = "#F3F4F6"     # Bright White Text
COLOR_TEXT_MUTED = "#9CA3AF"    # Slate Gray Text


class FaceAttendanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.minsize(1120, 740)
        self.configure(fg_color=COLOR_BG)

        # Initialize Backend Components
        self.db = DatabaseManager()
        self.face_engine = FaceEngine()
        self.exporter = AttendanceExporter(self.db)

        # Camera & Threading State
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_camera_running = False
        self.camera_thread: Optional[threading.Thread] = None
        self.camera_index = 0
        self.enable_sound = True

        # Enrollment state
        self.is_enrolling = False
        self.enroll_samples_count = 0
        self.enroll_target_id = ""

        # Configure Custom Treeview Theme
        self._configure_treeview_styles()

        # Build UI Architecture
        self._create_header()
        self._create_main_layout()

        # Default to SaaS Landing Home Tab
        self.tabview.set("🏠 Home")

        # Initial Data Refresh
        self.refresh_dashboard_stats()
        self.refresh_logs_table()
        self.refresh_persons_list()

    def _configure_treeview_styles(self):
        """Applies ultra-modern dark theme styling to standard Tkinter Treeview widgets."""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configure Table Header
        style.configure(
            "Treeview.Heading",
            background="#1E2235",
            foreground="#F3F4F6",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padding=8
        )
        style.map("Treeview.Heading", background=[("active", "#2A2E45")])

        # Configure Table Rows
        style.configure(
            "Treeview",
            background="#161928",
            foreground="#E5E7EB",
            fieldbackground="#161928",
            rowheight=32,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.map(
            "Treeview",
            background=[("selected", "#2563EB")],
            foreground=[("selected", "#FFFFFF")]
        )

    # ------------------------------------------------------------------
    # Header Bar
    # ------------------------------------------------------------------

    def _create_header(self):
        self.header_frame = ctk.CTkFrame(self, height=64, corner_radius=0, fg_color=COLOR_HEADER_BG, border_width=1, border_color=COLOR_BORDER)
        self.header_frame.pack(side="top", fill="x")

        # Brand Container
        brand_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        brand_box.pack(side="left", padx=20, pady=12)

        # Status Dot Badge
        dot_lbl = ctk.CTkLabel(brand_box, text="🟢", font=ctk.CTkFont(size=10))
        dot_lbl.pack(side="left", padx=(0, 8))

        # Title Label
        title_lbl = ctk.CTkLabel(
            brand_box,
            text="FACE RECOGNITION ATTENDANCE PLATFORM",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLOR_TEXT_MAIN
        )
        title_lbl.pack(side="left")

        # Right Section: System Badge & Live Clock
        right_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        right_box.pack(side="right", padx=20)

        # SaaS Version Badge
        saas_pill = ctk.CTkFrame(right_box, fg_color="#1E2235", corner_radius=12, border_width=1, border_color=COLOR_BORDER)
        saas_pill.pack(side="left", padx=(0, 15), pady=12)

        saas_lbl = ctk.CTkLabel(saas_pill, text="v2.5 SaaS EDITION", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLOR_CYAN)
        saas_lbl.pack(padx=12, pady=4)

        # Live Clock Label
        self.clock_lbl = ctk.CTkLabel(
            right_box,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"),
            text_color=COLOR_TEXT_MUTED
        )
        self.clock_lbl.pack(side="right")
        self._update_clock()

    def _update_clock(self):
        now_str = datetime.now().strftime("%A, %B %d %Y | %I:%M:%S %p")
        self.clock_lbl.configure(text=now_str)
        self.after(1000, self._update_clock)

    # ------------------------------------------------------------------
    # Main Tabbed Layout
    # ------------------------------------------------------------------

    def _create_main_layout(self):
        self.tabview = ctk.CTkTabview(
            self,
            corner_radius=12,
            fg_color=COLOR_BG,
            segmented_button_fg_color="#181B2B",
            segmented_button_selected_color=COLOR_BLUE,
            segmented_button_selected_hover_color="#1D4ED8",
            segmented_button_unselected_color="#181B2B",
            segmented_button_unselected_hover_color="#22263B",
            text_color=COLOR_TEXT_MAIN
        )
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        # Tabs
        self.tab_home = self.tabview.add("🏠 Home")
        self.tab_dashboard = self.tabview.add("📊 Dashboard")
        self.tab_scanner = self.tabview.add("📹 Live Scanner")
        self.tab_enrollment = self.tabview.add("👤 Enrollment")
        self.tab_logs = self.tabview.add("📋 Attendance Logs")
        self.tab_persons = self.tabview.add("👥 Registered Users")

        # Setup Individual Tabs
        self._setup_home_tab()
        self._setup_dashboard_tab()
        self._setup_scanner_tab()
        self._setup_enrollment_tab()
        self._setup_logs_tab()
        self._setup_persons_tab()

    # ------------------------------------------------------------------
    # TAB 0: SaaS Landing Home Page
    # ------------------------------------------------------------------

    def _setup_home_tab(self):
        home_scroll = ctk.CTkScrollableFrame(self.tab_home, fg_color="transparent")
        home_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # --------------------------------------------------------------
        # HERO SECTION
        # --------------------------------------------------------------
        hero_card = ctk.CTkFrame(
            home_scroll,
            fg_color=COLOR_CARD_BG,
            corner_radius=16,
            border_width=1,
            border_color=COLOR_BORDER
        )
        hero_card.pack(fill="x", pady=(5, 20), padx=5)

        # Top Neon Accent Highlight
        accent_strip = ctk.CTkFrame(hero_card, height=4, fg_color=COLOR_BLUE, corner_radius=2)
        accent_strip.pack(fill="x", side="top")

        hero_box = ctk.CTkFrame(hero_card, fg_color="transparent")
        hero_box.pack(fill="x", padx=30, pady=28)

        # SaaS Pill Badge
        badge_box = ctk.CTkFrame(hero_box, fg_color="#1E2235", corner_radius=15, border_width=1, border_color=COLOR_BORDER)
        badge_box.pack(anchor="w", pady=(0, 12))
        badge_lbl = ctk.CTkLabel(
            badge_box,
            text="⚡ POWERED BY ARTIFICIAL INTELLIGENCE & COMPUTER VISION",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLOR_CYAN
        )
        badge_lbl.pack(padx=14, pady=5)

        # Headline
        hero_title = ctk.CTkLabel(
            hero_box,
            text="Intelligent Real-Time Face Attendance Platform",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color=COLOR_TEXT_MAIN,
            justify="left"
        )
        hero_title.pack(anchor="w", pady=(0, 8))

        # Subtitle
        hero_sub = ctk.CTkLabel(
            hero_box,
            text="Automate student and employee attendance logging with high-precision computer vision, anti-proxy cooldown protection, automated SQLite persistence, and instant 1-click multi-format report exports.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLOR_TEXT_MUTED,
            justify="left",
            wraplength=850
        )
        hero_sub.pack(anchor="w", pady=(0, 20))

        # Action Buttons (CTA)
        cta_box = ctk.CTkFrame(hero_box, fg_color="transparent")
        cta_box.pack(anchor="w")

        btn_cta_scan = ctk.CTkButton(
            cta_box,
            text="📹 Open Live Camera Scanner",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_GREEN, hover_color="#059669",
            height=44, corner_radius=8,
            command=lambda: self.tabview.set("📹 Live Scanner")
        )
        btn_cta_scan.pack(side="left", padx=(0, 12))

        btn_cta_enroll = ctk.CTkButton(
            cta_box,
            text="👤 Enroll New Member",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_BLUE, hover_color="#1D4ED8",
            height=44, corner_radius=8,
            command=lambda: self.tabview.set("👤 Enrollment")
        )
        btn_cta_enroll.pack(side="left", padx=(0, 12))

        btn_cta_dash = ctk.CTkButton(
            cta_box,
            text="📊 View Dashboard Stats",
            font=ctk.CTkFont(size=13),
            fg_color="#2A2E45", hover_color="#3B405D",
            text_color=COLOR_TEXT_MAIN,
            height=44, corner_radius=8,
            command=lambda: self.tabview.set("📊 Dashboard")
        )
        btn_cta_dash.pack(side="left")

        # --------------------------------------------------------------
        # FEATURES GRID (3 COLUMNS)
        # --------------------------------------------------------------
        grid_title = ctk.CTkLabel(
            home_scroll,
            text="🚀 Core SaaS Platform Features",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_TEXT_MAIN
        )
        grid_title.pack(anchor="w", padx=5, pady=(10, 12))

        grid_frame = ctk.CTkFrame(home_scroll, fg_color="transparent")
        grid_frame.pack(fill="x", pady=(0, 20), padx=5)
        grid_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self._create_saas_feature_card(
            grid_frame, 0,
            "🤖 Computer Vision AI",
            "OpenCV Haar Cascade & CLAHE illumination normalization engine for fast, multi-angle face localization.",
            COLOR_BLUE
        )
        self._create_saas_feature_card(
            grid_frame, 1,
            "🧠 Machine Learning Model",
            "LBPH (Local Binary Patterns Histograms) texture vector analysis with Euclidean distance confidence scoring.",
            COLOR_PURPLE
        )
        self._create_saas_feature_card(
            grid_frame, 2,
            "📊 Multi-Format Exports",
            "One-click data export to Excel (.xlsx) with formatting, standard CSV, and styled HTML summary reports.",
            COLOR_GREEN
        )

        # --------------------------------------------------------------
        # WORKFLOW STEPS (4 STEPS)
        # --------------------------------------------------------------
        flow_title = ctk.CTkLabel(
            home_scroll,
            text="⚡ How It Works (4 Simple Steps)",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_TEXT_MAIN
        )
        flow_title.pack(anchor="w", padx=5, pady=(10, 12))

        flow_card = ctk.CTkFrame(
            home_scroll,
            fg_color=COLOR_CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_BORDER
        )
        flow_card.pack(fill="x", padx=5, pady=(0, 20))
        flow_card.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._create_step_card(flow_card, 0, "1️⃣ Enroll Member", "Register ID & capture 20 face samples.")
        self._create_step_card(flow_card, 1, "2️⃣ Train Model", "Compile features into LBPH binary model.")
        self._create_step_card(flow_card, 2, "3️⃣ Live Scanner", "Scan faces & auto-log Present/Late.")
        self._create_step_card(flow_card, 3, "4️⃣ Export Reports", "Download Excel, CSV, or HTML reports.")

    def _create_saas_feature_card(self, parent, col, title, desc, accent_color):
        card = ctk.CTkFrame(
            parent,
            fg_color=COLOR_CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_BORDER
        )
        card.grid(row=0, column=col, padx=8, pady=5, sticky="nsew")

        strip = ctk.CTkFrame(card, height=3, fg_color=accent_color, corner_radius=2)
        strip.pack(fill="x", side="top")

        box = ctk.CTkFrame(card, fg_color="transparent")
        box.pack(fill="both", expand=True, padx=18, pady=16)

        lbl_t = ctk.CTkLabel(box, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_TEXT_MAIN)
        lbl_t.pack(anchor="w", pady=(0, 6))

        lbl_d = ctk.CTkLabel(box, text=desc, font=ctk.CTkFont(size=12), text_color=COLOR_TEXT_MUTED, justify="left", wraplength=260)
        lbl_d.pack(anchor="w")

    def _create_step_card(self, parent, col, step_title, step_desc):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.grid(row=0, column=col, padx=14, pady=16, sticky="ew")

        lbl_t = ctk.CTkLabel(box, text=step_title, font=ctk.CTkFont(size=13, weight="bold"), text_color=COLOR_TEXT_MAIN)
        lbl_t.pack(anchor="w", pady=(0, 4))

        lbl_d = ctk.CTkLabel(box, text=step_desc, font=ctk.CTkFont(size=11), text_color=COLOR_TEXT_MUTED, justify="left", wraplength=180)
        lbl_d.pack(anchor="w")

    # ------------------------------------------------------------------
    # TAB 1: Dashboard
    # ------------------------------------------------------------------

    def _setup_dashboard_tab(self):
        # Stats Cards Container
        cards_frame = ctk.CTkFrame(self.tab_dashboard, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(5, 15))
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Hero Stat Cards with Glassmorphic styling
        self.card_enrolled = self._create_stat_card(cards_frame, 0, "TOTAL REGISTERED", "0", COLOR_BLUE, "👥")
        self.card_present = self._create_stat_card(cards_frame, 1, "PRESENT TODAY", "0", COLOR_GREEN, "✅")
        self.card_late = self._create_stat_card(cards_frame, 2, "LATE TODAY", "0", COLOR_AMBER, "⚠️")
        self.card_absent = self._create_stat_card(cards_frame, 3, "ABSENT TODAY", "0", COLOR_RED, "❌")

        # Recent Activity Header
        header_box = ctk.CTkFrame(self.tab_dashboard, fg_color="transparent")
        header_box.pack(fill="x", pady=(15, 10))

        sec_title = ctk.CTkLabel(
            header_box,
            text="⚡ Live Attendance Feed (Today's Logs)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLOR_TEXT_MAIN
        )
        sec_title.pack(side="left")

        btn_ref_dash = ctk.CTkButton(
            header_box,
            text="🔄 Refresh Feed",
            width=110, height=32,
            fg_color="#1E2235", hover_color="#2A2E45",
            text_color=COLOR_TEXT_MAIN,
            command=self.refresh_dashboard_stats
        )
        btn_ref_dash.pack(side="right")

        # Recent Logs Treeview Container
        tree_frame = ctk.CTkFrame(self.tab_dashboard, fg_color=COLOR_CARD_BG, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        tree_frame.pack(fill="both", expand=True)

        cols = ("ID", "Name", "Department", "Time In", "Time Out", "Status", "Confidence")
        self.dash_tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=8)

        for col in cols:
            self.dash_tree.heading(col, text=col)
            self.dash_tree.column(col, anchor="center", width=120)

        self.dash_tree.pack(fill="both", expand=True, padx=8, pady=8)

    def _create_stat_card(self, parent, col, title, initial_val, accent_color, icon_symbol):
        card = ctk.CTkFrame(
            parent,
            fg_color=COLOR_CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_BORDER
        )
        card.grid(row=0, column=col, padx=8, pady=5, sticky="ew")

        # Top Accent Highlight Line
        accent_strip = ctk.CTkFrame(card, height=4, fg_color=accent_color, corner_radius=2)
        accent_strip.pack(fill="x", side="top")

        content_box = ctk.CTkFrame(card, fg_color="transparent")
        content_box.pack(fill="x", padx=16, pady=14)

        top_row = ctk.CTkFrame(content_box, fg_color="transparent")
        top_row.pack(fill="x")

        lbl_title = ctk.CTkLabel(
            top_row,
            text=title,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        )
        lbl_title.pack(side="left")

        lbl_icon = ctk.CTkLabel(top_row, text=icon_symbol, font=ctk.CTkFont(size=14))
        lbl_icon.pack(side="right")

        lbl_val = ctk.CTkLabel(
            content_box,
            text=initial_val,
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=COLOR_TEXT_MAIN
        )
        lbl_val.pack(anchor="w", pady=(6, 0))
        return lbl_val

    def refresh_dashboard_stats(self):
        stats = self.db.get_dashboard_stats()
        self.card_enrolled.configure(text=str(stats["total_enrolled"]))
        self.card_present.configure(text=str(stats["total_present"]))
        self.card_late.configure(text=str(stats["total_late"]))
        self.card_absent.configure(text=str(stats["total_absent"]))

        # Populate Dashboard Recent Activity
        for item in self.dash_tree.get_children():
            self.dash_tree.delete(item)

        today_logs = self.db.get_attendance_logs(target_date=date.today().isoformat())
        for log in today_logs[:10]:
            self.dash_tree.insert("", "end", values=(
                log["person_id"],
                log["name"],
                log.get("department", "N/A"),
                log["time_in"],
                log["time_out"] or "--",
                log["status"],
                f"{log['confidence']}%"
            ))

    # ------------------------------------------------------------------
    # TAB 2: Live Scanner
    # ------------------------------------------------------------------

    def _setup_scanner_tab(self):
        container = ctk.CTkFrame(self.tab_scanner, fg_color="transparent")
        container.pack(fill="both", expand=True)
        container.grid_columnconfigure(0, weight=3)
        container.grid_columnconfigure(1, weight=1)

        # Video Frame Container
        video_frame = ctk.CTkFrame(container, fg_color="#090A0F", corner_radius=12, border_width=1, border_color=COLOR_BORDER)
        video_frame.grid(row=0, column=0, padx=(0, 12), pady=8, sticky="nsew")

        self.video_label = ctk.CTkLabel(
            video_frame,
            text="🎥 [ Live Scanner Stream Offline ]\nSelect camera and click 'Start Camera Scanner' to begin",
            font=ctk.CTkFont(size=14, weight="normal"),
            text_color=COLOR_TEXT_MUTED
        )
        self.video_label.pack(fill="both", expand=True)

        # Controls Side Panel
        ctrl_frame = ctk.CTkFrame(container, fg_color=COLOR_CARD_BG, corner_radius=12, border_width=1, border_color=COLOR_BORDER)
        ctrl_frame.grid(row=0, column=1, pady=8, sticky="nsew")

        ctk.CTkLabel(ctrl_frame, text="Scanner Controls", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_TEXT_MAIN).pack(padx=18, pady=(18, 12))

        # Camera Select Dropdown
        ctk.CTkLabel(ctrl_frame, text="Select Camera Device:", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=18, pady=(8, 4))
        cams = [f"Camera {i}" for i in get_available_cameras()]
        self.cam_select = ctk.CTkOptionMenu(
            ctrl_frame,
            values=cams,
            fg_color="#141724",
            button_color=COLOR_BLUE,
            button_hover_color="#1D4ED8",
            dropdown_fg_color="#141724"
        )
        self.cam_select.pack(fill="x", padx=18, pady=(0, 15))

        # Sound Alert Toggle
        self.sound_switch = ctk.CTkSwitch(
            ctrl_frame,
            text="Audio Notification Beep",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MAIN,
            progress_color=COLOR_GREEN,
            command=self._toggle_sound
        )
        self.sound_switch.select()
        self.sound_switch.pack(anchor="w", padx=18, pady=10)

        # Action Buttons
        self.btn_start_cam = ctk.CTkButton(
            ctrl_frame,
            text="▶ Start Camera Scanner",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_GREEN, hover_color="#059669",
            height=42, corner_radius=8,
            command=self.start_camera
        )
        self.btn_start_cam.pack(fill="x", padx=18, pady=(20, 10))

        self.btn_stop_cam = ctk.CTkButton(
            ctrl_frame,
            text="⏹ Stop Scanner",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_RED, hover_color="#DC2626",
            height=42, corner_radius=8,
            command=self.stop_camera, state="disabled"
        )
        self.btn_stop_cam.pack(fill="x", padx=18, pady=5)

        # Status Alert Banner
        self.alert_banner = ctk.CTkLabel(
            ctrl_frame,
            text="Status: Scanner Ready",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#141724", text_color=COLOR_TEXT_MUTED,
            corner_radius=8, height=52
        )
        self.alert_banner.pack(fill="x", padx=18, pady=(25, 18))

    def _toggle_sound(self):
        self.enable_sound = bool(self.sound_switch.get())

    def start_camera(self):
        if self.is_camera_running:
            return

        cam_str = self.cam_select.get()
        try:
            self.camera_index = int(cam_str.split(" ")[1])
        except (IndexError, ValueError):
            self.camera_index = 0

        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW if sys.platform.startswith("win") else cv2.CAP_ANY)
        if not self.cap.isOpened():
            messagebox.showerror("Camera Error", f"Unable to access camera index {self.camera_index}.")
            return

        self.is_camera_running = True
        self.btn_start_cam.configure(state="disabled")
        self.btn_stop_cam.configure(state="normal")
        self.alert_banner.configure(text="Status: Active Scanning...", fg_color=COLOR_BLUE, text_color="#ffffff")

        # Start Camera Thread
        self.camera_thread = threading.Thread(target=self._camera_loop, daemon=True)
        self.camera_thread.start()

    def stop_camera(self):
        self.is_camera_running = False
        if self.cap:
            self.cap.release()
            self.cap = None

        self.btn_start_cam.configure(state="normal")
        self.btn_stop_cam.configure(state="disabled")
        self.video_label.configure(image=None, text="🎥 [ Live Scanner Stream Offline ]")
        self.alert_banner.configure(text="Status: Scanner Stopped", fg_color="#141724", text_color=COLOR_TEXT_MUTED)

    def _camera_loop(self):
        prev_time = time.time()
        fps = 0.0

        while self.is_camera_running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            # Calculate FPS
            curr_time = time.time()
            fps = 0.9 * fps + 0.1 * (1.0 / max(0.001, curr_time - prev_time))
            prev_time = curr_time

            # Detect Faces
            faces = self.face_engine.detect_faces(frame)

            for bbox in faces:
                rec_res = self.face_engine.recognize_face(frame, bbox)
                person_id = rec_res["person_id"]
                confidence = rec_res["confidence"]
                is_rec = rec_res["is_recognized"]

                if is_rec:
                    person = self.db.get_person(person_id)
                    name = person["name"] if person else person_id
                    color = (0, 220, 100)
                    subtitle = f"{confidence}%"

                    # Handle Attendance Logging
                    if self.face_engine.can_mark_attendance(person_id):
                        att_res = self.db.mark_attendance(person_id, confidence)
                        self.face_engine.record_attendance_cooldown(person_id)

                        if self.enable_sound:
                            play_attendance_beep(success=True)

                        status_txt = att_res.get("status", "Present")
                        self.after(0, self._update_alert, f"✅ Marked: {name} ({status_txt})", COLOR_GREEN)
                        self.after(0, self.refresh_dashboard_stats)
                else:
                    name = "Unknown"
                    color = (0, 100, 255)
                    subtitle = "Unrecognized"

                draw_styled_bbox(frame, bbox, name, subtitle=subtitle, color=color)

            # Draw FPS Overlay
            cv2.putText(frame, f"FPS: {int(fps)}", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # Convert BGR frame to RGB for Tkinter
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            img = img.resize((640, 480), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(image=img)

            # Update UI on main thread
            self.after(0, self._update_video_frame, img_tk)

        if self.cap:
            self.cap.release()

    def _update_video_frame(self, img_tk):
        if self.is_camera_running:
            self.video_label.configure(image=img_tk, text="")
            self.video_label.image = img_tk

    def _update_alert(self, text, bg_color):
        self.alert_banner.configure(text=text, fg_color=bg_color, text_color="#ffffff")

    # ------------------------------------------------------------------
    # TAB 3: Enrollment
    # ------------------------------------------------------------------

    def _setup_enrollment_tab(self):
        container = ctk.CTkFrame(self.tab_enrollment, fg_color="transparent")
        container.pack(fill="both", expand=True)
        container.grid_columnconfigure((0, 1), weight=1)

        # Form Column
        form_frame = ctk.CTkFrame(container, fg_color=COLOR_CARD_BG, corner_radius=12, border_width=1, border_color=COLOR_BORDER)
        form_frame.grid(row=0, column=0, padx=(0, 10), pady=8, sticky="nsew")

        ctk.CTkLabel(form_frame, text="Register New Student / Employee", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_TEXT_MAIN).pack(padx=20, pady=(20, 15))

        # Input Fields
        self.entry_id = self._create_form_field(form_frame, "Person ID / Roll No (Required):", "e.g., EMP001")
        self.entry_name = self._create_form_field(form_frame, "Full Name (Required):", "e.g., John Doe")
        self.entry_dept = self._create_form_field(form_frame, "Department:", "e.g., Computer Science")
        self.entry_role = self._create_form_field(form_frame, "Role:", "Student / Employee / Faculty")
        self.entry_email = self._create_form_field(form_frame, "Email Address:", "e.g., john@example.com")

        # Action Column (Face Photo Capture / Train)
        action_frame = ctk.CTkFrame(container, fg_color=COLOR_CARD_BG, corner_radius=12, border_width=1, border_color=COLOR_BORDER)
        action_frame.grid(row=0, column=1, pady=8, sticky="nsew")

        ctk.CTkLabel(action_frame, text="Face Photo Capture & Training", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_TEXT_MAIN).pack(padx=20, pady=(20, 15))

        # Info Box Card
        info_box = ctk.CTkFrame(action_frame, fg_color="#141724", corner_radius=8, border_width=1, border_color=COLOR_BORDER)
        info_box.pack(fill="x", padx=25, pady=10)

        self.lbl_samples_status = ctk.CTkLabel(
            info_box,
            text="💡 Fill form details and click below to capture face photos.",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED,
            wraplength=320
        )
        self.lbl_samples_status.pack(padx=15, pady=15)

        self.btn_capture_cam = ctk.CTkButton(
            action_frame,
            text="📸 Capture Samples via Webcam",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_BLUE, hover_color="#1D4ED8",
            height=44, corner_radius=8,
            command=self._start_webcam_enrollment
        )
        self.btn_capture_cam.pack(fill="x", padx=25, pady=10)

        self.btn_upload_files = ctk.CTkButton(
            action_frame,
            text="📁 Import Photos from File",
            font=ctk.CTkFont(size=14),
            fg_color="#2A2E45", hover_color="#3B405D",
            text_color=COLOR_TEXT_MAIN,
            height=42, corner_radius=8,
            command=self._upload_photo_files
        )
        self.btn_upload_files.pack(fill="x", padx=25, pady=10)

        self.btn_train_model = ctk.CTkButton(
            action_frame,
            text="⚙️ Train Face Recognition Model",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_GREEN, hover_color="#059669",
            height=48, corner_radius=8,
            command=self._train_model_action
        )
        self.btn_train_model.pack(fill="x", padx=25, pady=(25, 15))

    def _create_form_field(self, parent, label_text, placeholder):
        ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=20, pady=(8, 2))
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=38,
            fg_color="#141724",
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_MAIN
        )
        entry.pack(fill="x", padx=20, pady=(0, 4))
        return entry

    def _start_webcam_enrollment(self):
        p_id = self.entry_id.get().strip()
        p_name = self.entry_name.get().strip()

        if not p_id or not p_name:
            messagebox.showwarning("Missing Input", "Please enter both Person ID and Full Name before capturing photos.")
            return

        # Save Person details into SQLite DB
        self.db.add_person(
            person_id=p_id,
            name=p_name,
            department=self.entry_dept.get().strip(),
            role=self.entry_role.get().strip() or "Student",
            email=self.entry_email.get().strip()
        )

        messagebox.showinfo("Capture Guide", f"Webcam will now capture {SAMPLES_PER_PERSON} face samples.\nPlease look at the camera and turn your head slightly.")

        # Capture samples loop
        cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW if sys.platform.startswith("win") else cv2.CAP_ANY)
        if not cap.isOpened():
            messagebox.showerror("Error", "Unable to open webcam for enrollment.")
            return

        sample_idx = 0
        while sample_idx < SAMPLES_PER_PERSON:
            ret, frame = cap.read()
            if not ret:
                break

            faces = self.face_engine.detect_faces(frame)
            for bbox in faces:
                saved_path = self.face_engine.save_sample_face(p_id, frame, bbox, sample_idx)
                if saved_path:
                    sample_idx += 1
                    cv2.putText(frame, f"Captured Sample {sample_idx}/{SAMPLES_PER_PERSON}", (20, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.imshow("Enrollment Capture", frame)
                    cv2.waitKey(200)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        self.lbl_samples_status.configure(text=f"✅ Captured {sample_idx} samples for ID: {p_id}")
        self.refresh_persons_list()
        self.refresh_dashboard_stats()

    def _upload_photo_files(self):
        p_id = self.entry_id.get().strip()
        p_name = self.entry_name.get().strip()

        if not p_id or not p_name:
            messagebox.showwarning("Missing Input", "Please enter Person ID and Full Name first.")
            return

        files = filedialog.askopenfilenames(
            title="Select Face Photos",
            filetypes=[("Image Files", "*.jpg *.png *.jpeg")]
        )
        if not files:
            return

        # Save Person details into SQLite DB
        self.db.add_person(
            person_id=p_id,
            name=p_name,
            department=self.entry_dept.get().strip(),
            role=self.entry_role.get().strip() or "Student",
            email=self.entry_email.get().strip()
        )

        saved_count = 0
        for idx, f_path in enumerate(files):
            img = cv2.imread(f_path)
            if img is None:
                continue
            faces = self.face_engine.detect_faces(img)
            for bbox in faces:
                if self.face_engine.save_sample_face(p_id, img, bbox, idx):
                    saved_count += 1

        self.lbl_samples_status.configure(text=f"✅ Imported {saved_count} face photos for ID: {p_id}")
        self.refresh_persons_list()
        self.refresh_dashboard_stats()

    def _train_model_action(self):
        success = self.face_engine.train_model()
        if success:
            messagebox.showinfo("Success", "Face recognition model trained successfully!")
        else:
            messagebox.showerror("Error", "Model training failed. Please make sure face photos exist in data/faces/.")

    # ------------------------------------------------------------------
    # TAB 4: Attendance Logs & Filtering
    # ------------------------------------------------------------------

    def _setup_logs_tab(self):
        # Filter Bar Card
        filter_bar = ctk.CTkFrame(self.tab_logs, fg_color=COLOR_CARD_BG, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        filter_bar.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(filter_bar, text="Search/Filter:", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MAIN).pack(side="left", padx=12, pady=10)
        
        self.search_entry = ctk.CTkEntry(filter_bar, placeholder_text="Search Name or ID...", width=180, fg_color="#141724", border_color=COLOR_BORDER)
        self.search_entry.pack(side="left", padx=5)

        self.date_entry = ctk.CTkEntry(filter_bar, placeholder_text="Date YYYY-MM-DD", width=140, fg_color="#141724", border_color=COLOR_BORDER)
        self.date_entry.pack(side="left", padx=5)

        btn_filter = ctk.CTkButton(filter_bar, text="🔍 Filter", width=80, fg_color=COLOR_BLUE, hover_color="#1D4ED8", command=self.refresh_logs_table)
        btn_filter.pack(side="left", padx=5)

        btn_reset = ctk.CTkButton(filter_bar, text="Reset", width=70, fg_color="#2A2E45", hover_color="#3B405D", text_color=COLOR_TEXT_MAIN, command=self._reset_log_filters)
        btn_reset.pack(side="left", padx=5)

        # Export Buttons
        btn_exp_excel = ctk.CTkButton(filter_bar, text="📊 Export Excel", fg_color=COLOR_GREEN, hover_color="#059669", command=self._export_excel_action)
        btn_exp_excel.pack(side="right", padx=10)

        btn_exp_csv = ctk.CTkButton(filter_bar, text="📄 Export CSV", fg_color=COLOR_BLUE, hover_color="#1D4ED8", command=self._export_csv_action)
        btn_exp_csv.pack(side="right", padx=5)

        # Logs Table Container
        table_frame = ctk.CTkFrame(self.tab_logs, fg_color=COLOR_CARD_BG, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        table_frame.pack(fill="both", expand=True)

        cols = ("Log ID", "Person ID", "Name", "Department", "Date", "Time In", "Time Out", "Status", "Confidence", "Marked Via")
        self.logs_tree = ttk.Treeview(table_frame, columns=cols, show="headings")

        for col in cols:
            self.logs_tree.heading(col, text=col)
            self.logs_tree.column(col, anchor="center", width=110)

        self.logs_tree.pack(fill="both", expand=True, padx=8, pady=8)

        # Bind Keyboard Delete Key
        self.logs_tree.bind("<Delete>", lambda event: self._delete_log_action())

        # Create Right-Click Context Menu for Logs Table
        import tkinter as tk
        self.log_context_menu = tk.Menu(self, tearoff=0, bg="#1E2235", fg="#FFFFFF", activebackground=COLOR_RED, activeforeground="#FFFFFF")
        self.log_context_menu.add_command(label="🗑️ Delete This Attendance Log", command=self._delete_log_action)
        self.log_context_menu.add_separator()
        self.log_context_menu.add_command(label="🧹 Clear All Logs", command=self._clear_all_logs_action)

        def _on_log_right_click(event):
            item = self.logs_tree.identify_row(event.y)
            if item:
                self.logs_tree.selection_set(item)
                self.log_context_menu.post(event.x_root, event.y_root)

        self.logs_tree.bind("<Button-3>", _on_log_right_click)

        # Bottom Action Bar for Deletion
        action_bar = ctk.CTkFrame(self.tab_logs, fg_color="transparent")
        action_bar.pack(fill="x", pady=(10, 0))

        lbl_hint = ctk.CTkLabel(
            action_bar,
            text="💡 Hint: Click any record and press 'Delete' key or Right-Click to delete.",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color=COLOR_TEXT_MUTED
        )
        lbl_hint.pack(side="left", padx=5)

        btn_clear_all = ctk.CTkButton(
            action_bar, text="🧹 Clear All Logs",
            fg_color="#2A2E45", hover_color="#3B405D", text_color=COLOR_TEXT_MAIN,
            command=self._clear_all_logs_action
        )
        btn_clear_all.pack(side="right", padx=5)

        btn_del_log = ctk.CTkButton(
            action_bar, text="🗑️ Delete Selected Attendance Log",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLOR_RED, hover_color="#DC2626",
            height=36,
            command=self._delete_log_action
        )
        btn_del_log.pack(side="right", padx=5)

    def _reset_log_filters(self):
        self.search_entry.delete(0, "end")
        self.date_entry.delete(0, "end")
        self.refresh_logs_table()

    def _delete_log_action(self):
        selected = self.logs_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an attendance log row to delete.")
            return

        values = self.logs_tree.item(selected[0])["values"]
        log_id = int(values[0])
        p_name = values[2]
        log_date = values[4]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete attendance record (ID: {log_id}) for {p_name} on {log_date}?"):
            if self.db.delete_attendance_log(log_id):
                self.refresh_logs_table()
                self.refresh_dashboard_stats()
                messagebox.showinfo("Deleted", f"Attendance log #{log_id} deleted successfully.")
            else:
                messagebox.showerror("Error", "Failed to delete log entry.")

    def _clear_all_logs_action(self):
        d_val = self.date_entry.get().strip() or None
        target_desc = f"all logs for date {d_val}" if d_val else "ALL attendance logs from the entire database"

        if messagebox.askyesno("Confirm Clear All Logs", f"⚠️ Warning: Are you sure you want to permanently delete {target_desc}?"):
            count = self.db.clear_attendance_logs(target_date=d_val)
            self.refresh_logs_table()
            self.refresh_dashboard_stats()
            messagebox.showinfo("Logs Cleared", f"Successfully cleared {count} attendance log entries.")

    def refresh_logs_table(self):
        for item in self.logs_tree.get_children():
            self.logs_tree.delete(item)

        search_q = self.search_entry.get().strip() if hasattr(self, 'search_entry') else None
        date_q = self.date_entry.get().strip() if hasattr(self, 'date_entry') else None

        logs = self.db.get_attendance_logs(
            target_date=date_q if date_q else None,
            person_id=search_q if search_q else None
        )

        for log in logs:
            self.logs_tree.insert("", "end", values=(
                log["id"],
                log["person_id"],
                log["name"],
                log.get("department", "N/A"),
                log["date"],
                log["time_in"],
                log["time_out"] or "--",
                log["status"],
                f"{log['confidence']}%",
                log.get("marked_by", "AUTO")
            ))

    def _export_csv_action(self):
        d_val = self.date_entry.get().strip() or None
        filepath = self.exporter.export_to_csv(target_date=d_val)
        messagebox.showinfo("Export Successful", f"Saved CSV Report to:\n{filepath}")

    def _export_excel_action(self):
        d_val = self.date_entry.get().strip() or None
        filepath = self.exporter.export_to_excel(target_date=d_val)
        messagebox.showinfo("Export Successful", f"Saved Excel Report to:\n{filepath}")

    # ------------------------------------------------------------------
    # TAB 5: Registered Persons
    # ------------------------------------------------------------------

    def _setup_persons_tab(self):
        top_bar = ctk.CTkFrame(self.tab_persons, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(top_bar, text="Registered Students / Employees", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_TEXT_MAIN).pack(side="left", padx=10)
        ctk.CTkButton(
            top_bar,
            text="🔄 Refresh List",
            width=120,
            fg_color="#1E2235", hover_color="#2A2E45",
            text_color=COLOR_TEXT_MAIN,
            command=self.refresh_persons_list
        ).pack(side="right", padx=10)

        # Persons Table Container
        p_frame = ctk.CTkFrame(self.tab_persons, fg_color=COLOR_CARD_BG, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        p_frame.pack(fill="both", expand=True)

        cols = ("Person ID", "Name", "Department", "Role", "Email", "Registered At")
        self.persons_tree = ttk.Treeview(p_frame, columns=cols, show="headings")

        for col in cols:
            self.persons_tree.heading(col, text=col)
            self.persons_tree.column(col, anchor="center", width=140)

        self.persons_tree.pack(fill="both", expand=True, padx=8, pady=8)

        # Action Buttons Frame
        btn_bar = ctk.CTkFrame(self.tab_persons, fg_color="transparent")
        btn_bar.pack(fill="x", pady=10)

        btn_edit = ctk.CTkButton(
            btn_bar, text="✏️ Edit Selected Person",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLOR_BLUE, hover_color="#1D4ED8",
            height=36, command=self._edit_person_action
        )
        btn_edit.pack(side="right", padx=10)

        btn_del = ctk.CTkButton(
            btn_bar, text="🗑️ Delete Selected Person",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLOR_RED, hover_color="#DC2626",
            height=36, command=self._delete_person_action
        )
        btn_del.pack(side="right", padx=10)

        # Bind double click on table row to edit
        self.persons_tree.bind("<Double-1>", lambda event: self._edit_person_action())
        # Bind keyboard Delete key
        self.persons_tree.bind("<Delete>", lambda event: self._delete_person_action())

        # Context Menu for Registered Persons
        import tkinter as tk
        self.person_context_menu = tk.Menu(self, tearoff=0, bg="#1E2235", fg="#FFFFFF", activebackground=COLOR_BLUE, activeforeground="#FFFFFF")
        self.person_context_menu.add_command(label="✏️ Edit Person Details", command=self._edit_person_action)
        self.person_context_menu.add_separator()
        self.person_context_menu.add_command(label="🗑️ Delete Registered User & Face Data", command=self._delete_person_action)

        def _on_person_right_click(event):
            item = self.persons_tree.identify_row(event.y)
            if item:
                self.persons_tree.selection_set(item)
                self.person_context_menu.post(event.x_root, event.y_root)

        self.persons_tree.bind("<Button-3>", _on_person_right_click)

    def refresh_persons_list(self):
        for item in self.persons_tree.get_children():
            self.persons_tree.delete(item)

        persons = self.db.get_all_persons()
        for p in persons:
            self.persons_tree.insert("", "end", values=(
                p["id"],
                p["name"],
                p.get("department", "N/A"),
                p.get("role", "Student"),
                p.get("email", "N/A"),
                p["created_at"]
            ))

    def _edit_person_action(self):
        selected = self.persons_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a person from the table to edit.")
            return

        values = self.persons_tree.item(selected[0])["values"]
        p_id = str(values[0])
        person = self.db.get_person(p_id)
        if not person:
            messagebox.showerror("Error", "Person details not found in database.")
            return

        # Open Edit Dialog Modal
        edit_win = ctk.CTkToplevel(self)
        edit_win.title(f"Edit Details - {person['name']} ({p_id})")
        edit_win.geometry("450x520")
        edit_win.configure(fg_color=COLOR_BG)
        edit_win.transient(self)
        edit_win.grab_set()

        ctk.CTkLabel(edit_win, text=f"✏️ Edit Person Details", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_TEXT_MAIN).pack(pady=(20, 15))

        # Person ID (Read only)
        ctk.CTkLabel(edit_win, text="Person ID (Read-Only):", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=30, pady=(5, 2))
        id_entry = ctk.CTkEntry(edit_win, height=36, fg_color="#141724", border_color=COLOR_BORDER)
        id_entry.insert(0, person["id"])
        id_entry.configure(state="disabled")
        id_entry.pack(fill="x", padx=30, pady=(0, 10))

        # Full Name
        ctk.CTkLabel(edit_win, text="Full Name:", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=30, pady=(5, 2))
        name_entry = ctk.CTkEntry(edit_win, height=36, fg_color="#141724", border_color=COLOR_BORDER)
        name_entry.insert(0, person["name"])
        name_entry.pack(fill="x", padx=30, pady=(0, 10))

        # Department
        ctk.CTkLabel(edit_win, text="Department:", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=30, pady=(5, 2))
        dept_entry = ctk.CTkEntry(edit_win, height=36, fg_color="#141724", border_color=COLOR_BORDER)
        dept_entry.insert(0, person.get("department") or "")
        dept_entry.pack(fill="x", padx=30, pady=(0, 10))

        # Role
        ctk.CTkLabel(edit_win, text="Role:", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=30, pady=(5, 2))
        role_entry = ctk.CTkEntry(edit_win, height=36, fg_color="#141724", border_color=COLOR_BORDER)
        role_entry.insert(0, person.get("role") or "Student")
        role_entry.pack(fill="x", padx=30, pady=(0, 10))

        # Email
        ctk.CTkLabel(edit_win, text="Email Address:", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=30, pady=(5, 2))
        email_entry = ctk.CTkEntry(edit_win, height=36, fg_color="#141724", border_color=COLOR_BORDER)
        email_entry.insert(0, person.get("email") or "")
        email_entry.pack(fill="x", padx=30, pady=(0, 15))

        def save_changes():
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showwarning("Validation Error", "Full Name cannot be empty.", parent=edit_win)
                return

            # Update DB
            self.db.add_person(
                person_id=p_id,
                name=new_name,
                department=dept_entry.get().strip(),
                role=role_entry.get().strip(),
                email=email_entry.get().strip(),
                photo_path=person.get("photo_path") or ""
            )

            self.refresh_persons_list()
            self.refresh_dashboard_stats()
            self.refresh_logs_table()
            edit_win.destroy()
            messagebox.showinfo("Success", f"Updated details for {new_name} ({p_id}) successfully!")

        btn_save = ctk.CTkButton(edit_win, text="💾 Save Changes", fg_color=COLOR_GREEN, hover_color="#059669", height=40, command=save_changes)
        btn_save.pack(fill="x", padx=30, pady=10)

    def _delete_person_action(self):
        selected = self.persons_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a person from the table to delete.")
            return

        values = self.persons_tree.item(selected[0])["values"]
        p_id = str(values[0])
        p_name = values[1]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {p_name} ({p_id}) and all their attendance history & face samples?"):
            import shutil
            # Delete from DB
            self.db.delete_person(p_id)

            # Clean up face samples directory
            person_face_dir = FACES_DIR / p_id
            if person_face_dir.exists():
                shutil.rmtree(person_face_dir, ignore_errors=True)

            # Retrain model
            self.face_engine.train_model()

            self.refresh_persons_list()
            self.refresh_dashboard_stats()
            self.refresh_logs_table()
            messagebox.showinfo("Deleted", f"Person {p_name} and their face data deleted successfully.")

    def on_closing(self):
        self.stop_camera()
        self.destroy()


def main():
    app = FaceAttendanceApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
