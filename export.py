"""
Export utilities for Face Recognition Attendance System.
Exports attendance logs from SQLite database to CSV, Excel (.xlsx), and HTML summary reports.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

import pandas as pd

from config import EXPORTS_DIR
from database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Exporter")


class AttendanceExporter:
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def _fetch_data(self, target_date: Optional[str] = None,
                    department: Optional[str] = None) -> pd.DataFrame:
        """Fetches attendance records into a Pandas DataFrame."""
        logs = self.db.get_attendance_logs(target_date=target_date, department=department)
        if not logs:
            return pd.DataFrame()

        df = pd.DataFrame(logs)

        # Rename columns for presentation
        column_mapping = {
            "id": "Log ID",
            "person_id": "Person ID",
            "name": "Full Name",
            "department": "Department",
            "date": "Date",
            "time_in": "Time In",
            "status": "Attendance Status",
            "confidence": "Match Confidence (%)",
            "marked_by": "Marked Via"
        }
        
        # Filter existing columns
        cols = [c for c in column_mapping.keys() if c in df.columns]
        df = df[cols].rename(columns=column_mapping)
        
        # Fill missing values
        df["Department"] = df["Department"].fillna("N/A")
        
        return df

    def export_to_csv(self, filename: Optional[str] = None,
                      target_date: Optional[str] = None,
                      department: Optional[str] = None) -> str:
        """Exports logs to a CSV file."""
        df = self._fetch_data(target_date=target_date, department=department)
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"attendance_report_{timestamp}.csv"

        filepath = EXPORTS_DIR / filename
        df.to_csv(filepath, index=False, encoding="utf-8")
        logger.info("Exported CSV report to %s", filepath)
        return str(filepath)

    def export_to_excel(self, filename: Optional[str] = None,
                       target_date: Optional[str] = None,
                       department: Optional[str] = None) -> str:
        """Exports formatted Excel report with styling using pandas/openpyxl."""
        df = self._fetch_data(target_date=target_date, department=department)

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"attendance_report_{timestamp}.xlsx"

        filepath = EXPORTS_DIR / filename

        # Export with ExcelWriter
        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Attendance Logs", index=False)
            
            # Format sheet columns
            workbook = writer.book
            worksheet = writer.sheets["Attendance Logs"]
            
            # Adjust column widths automatically
            for col in worksheet.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = col[0].column_letter
                worksheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

        logger.info("Exported Excel report to %s", filepath)
        return str(filepath)

    def export_to_html(self, filename: Optional[str] = None,
                       target_date: Optional[str] = None,
                       department: Optional[str] = None) -> str:
        """Exports a styled HTML summary report."""
        df = self._fetch_data(target_date=target_date, department=department)
        stats = self.db.get_dashboard_stats(target_date=target_date)

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"attendance_summary_{timestamp}.html"

        filepath = EXPORTS_DIR / filename
        date_heading = target_date if target_date else datetime.now().strftime("%Y-%m-%d")

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Attendance Summary Report - {date_heading}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f7f6;
            margin: 0;
            padding: 30px;
            color: #333;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        h1 {{
            color: #1f538d;
            border-bottom: 3px solid #1f538d;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin: 25px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            border-left: 4px solid #1f538d;
            padding: 15px;
            border-radius: 6px;
        }}
        .stat-card.present {{ border-left-color: #2fa572; }}
        .stat-card.late {{ border-left-color: #e67e22; }}
        .stat-card.absent {{ border-left-color: #e74c3c; }}
        .stat-num {{
            font-size: 24px;
            font-weight: bold;
            color: #222;
        }}
        .stat-label {{
            font-size: 13px;
            color: #666;
            text-transform: uppercase;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e1e1e1;
        }}
        th {{
            background-color: #1f538d;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{ background-color: #f1f5f9; }}
        .badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 12px;
        }}
        .badge-present {{ background: #d4edda; color: #155724; }}
        .badge-late {{ background: #fff3cd; color: #856404; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Face Attendance Summary Report</h1>
        <p><strong>Report Date:</strong> {date_heading} | <strong>Generated At:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-num">{stats['total_enrolled']}</div>
                <div class="stat-label">Total Enrolled</div>
            </div>
            <div class="stat-card present">
                <div class="stat-num">{stats['total_present']}</div>
                <div class="stat-label">Present</div>
            </div>
            <div class="stat-card late">
                <div class="stat-num">{stats['total_late']}</div>
                <div class="stat-label">Late</div>
            </div>
            <div class="stat-card absent">
                <div class="stat-num">{stats['total_absent']}</div>
                <div class="stat-label">Absent</div>
            </div>
        </div>

        <h2>Detailed Attendance Log</h2>
"""
        if not df.empty:
            html_content += df.to_html(index=False, classes="table", escape=False)
        else:
            html_content += "<p>No attendance records found for this selection.</p>"

        html_content += """
    </div>
</body>
</html>
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info("Exported HTML report to %s", filepath)
        return str(filepath)


if __name__ == "__main__":
    exporter = AttendanceExporter()
    csv_path = exporter.export_to_csv()
    print("Exporter module verified. Created CSV at:", csv_path)
