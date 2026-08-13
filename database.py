"""
Database manager for Face Recognition Attendance System using SQLite.
Handles persons (employees/students) schema, attendance logs, and statistics.
"""

import sqlite3
import logging
from contextlib import contextmanager
from datetime import datetime, date, time
from typing import List, Dict, Any, Optional, Tuple


class _ConnectionManager:
    """Simple connection wrapper that tracks whether the database is closed."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def is_closed(self) -> bool:
        return self._conn is None

from config import DB_PATH, DEFAULT_START_TIME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DatabaseManager")


class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_path = str(db_path or DB_PATH)
        self._conn_manager = _ConnectionManager(self.db_path)
        self.init_db()

    @contextmanager
    def _get_connection(self):
        """Yield a database connection and ensure it is closed after use."""
        conn = self._conn_manager.connect()
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise
        else:
            conn.commit()
        finally:
            self._conn_manager.close()

    def close(self) -> None:
        """Close the underlying SQLite connection when the manager is no longer needed."""
        self._conn_manager.close()

    def is_closed(self) -> bool:
        """Return whether the managed connection has been closed."""
        return self._conn_manager.is_closed()

    def init_db(self) -> None:
        """Creates tables if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Persons Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS persons (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    department TEXT,
                    role TEXT,
                    email TEXT,
                    photo_path TEXT,
                    created_at TEXT NOT NULL
                )
            """)

            # Attendance Logs Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time_in TEXT NOT NULL,
                    time_out TEXT,
                    status TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    marked_by TEXT DEFAULT 'AUTO_FACE_RECOGNITION',
                    FOREIGN KEY (person_id) REFERENCES persons (id) ON DELETE CASCADE
                )
            """)

            # Create indices for fast queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_person ON attendance(person_id)")
            
            conn.commit()
            logger.info("Database initialized successfully at %s", self.db_path)

    # ------------------------------------------------------------------
    # Person Management (CRUD)
    # ------------------------------------------------------------------

    def add_person(self, person_id: str, name: str, department: str = "",
                   role: str = "Student", email: str = "", photo_path: str = "") -> bool:
        """Add or update a registered person after basic validation."""
        if not isinstance(person_id, str) or not person_id.strip():
            logger.warning("Person ID is required")
            return False

        if not isinstance(name, str) or not name.strip():
            logger.warning("Person name is required")
            return False

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO persons (id, name, department, role, email, photo_path, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        name=excluded.name,
                        department=excluded.department,
                        role=excluded.role,
                        email=excluded.email,
                        photo_path=excluded.photo_path
                """, (person_id.strip(), name.strip(), department.strip(), role.strip(), email.strip(), photo_path, created_at))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error("Error adding person %s: %s", person_id, e)
            return False

    def get_person(self, person_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve person details by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM persons WHERE id = ?", (person_id.strip(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_persons(self) -> List[Dict[str, Any]]:
        """Get list of all registered persons."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM persons ORDER BY name ASC")
            return [dict(row) for row in cursor.fetchall()]

    def delete_person(self, person_id: str) -> bool:
        """Delete a person and associated attendance records."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM persons WHERE id = ?", (person_id.strip(),))
                cursor.execute("DELETE FROM attendance WHERE person_id = ?", (person_id.strip(),))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error("Error deleting person %s: %s", person_id, e)
            return False

    # ------------------------------------------------------------------
    # Attendance Operations
    # ------------------------------------------------------------------

    def mark_attendance(self, person_id: str, confidence: float,
                        start_time_str: str = DEFAULT_START_TIME) -> Dict[str, Any]:
        """
        Mark or update attendance for today.
        - If first scan today: Insert new log record ('Present' or 'Late').
        - If already scanned today: Update 'time_out'.
        Returns dict with status, action taken ('CREATED' or 'UPDATED'), and log details.
        """
        if not isinstance(person_id, str) or not person_id.strip():
            return {"success": False, "message": "Person ID is required."}

        try:
            confidence_value = float(confidence)
        except (TypeError, ValueError):
            return {"success": False, "message": "Confidence must be a numeric value."}

        if not 0 <= confidence_value <= 100:
            return {"success": False, "message": "Confidence must be between 0 and 100."}

        person = self.get_person(person_id)
        if not person:
            return {"success": False, "message": f"Person ID {person_id} not found."}

        today_str = date.today().isoformat()
        now = datetime.now()
        current_time_str = now.strftime("%I:%M:%S %p")

        # Determine Present vs Late
        try:
            start_t = datetime.strptime(start_time_str, "%H:%M:%S").time()
        except ValueError:
            start_t = datetime.strptime("09:00:00", "%H:%M:%S").time()

        status = "Present" if now.time() <= start_t else "Late"

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM attendance WHERE person_id = ? AND date = ?
            """, (person_id, today_str))
            existing_log = cursor.fetchone()

            if existing_log:
                # College attendance needs one check-in record per person per day.
                return {
                    "success": True,
                    "action": "ALREADY_MARKED",
                    "status": existing_log["status"],
                    "person_id": person_id,
                    "name": person["name"],
                    "time_in": existing_log["time_in"],
                    "time_out": existing_log["time_out"],
                    "confidence": existing_log["confidence"]
                }
            else:
                # First check-in today
                cursor.execute("""
                    INSERT INTO attendance (person_id, name, date, time_in, status, confidence)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (person_id, person["name"], today_str, current_time_str, status, round(confidence_value, 2)))
                conn.commit()
                return {
                    "success": True,
                    "action": "CREATED",
                    "status": status,
                    "person_id": person_id,
                    "name": person["name"],
                    "time_in": current_time_str,
                    "time_out": None,
                    "confidence": confidence_value
                }

    def manual_mark_attendance(self, person_id: str, target_date: str,
                               time_in: str, status: str = "Present") -> bool:
        """Manually insert or override attendance log."""
        person = self.get_person(person_id)
        if not person:
            return False

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO attendance (person_id, name, date, time_in, status, confidence, marked_by)
                    VALUES (?, ?, ?, ?, ?, ?, 'MANUAL_OVERRIDE')
                """, (person_id, person["name"], target_date, time_in, status, 100.0))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error("Manual attendance error: %s", e)
            return False

    def get_attendance_logs(self, target_date: Optional[str] = None,
                            person_id: Optional[str] = None,
                            department: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve attendance logs with optional filters."""
        query = """
            SELECT a.id, a.person_id, a.name, p.department, a.date, a.time_in, a.time_out,
                   a.status, a.confidence, a.marked_by
            FROM attendance a
            LEFT JOIN persons p ON a.person_id = p.id
            WHERE 1=1
        """
        params = []

        if target_date:
            query += " AND a.date = ?"
            params.append(target_date)

        if person_id:
            query += " AND (a.person_id LIKE ? OR a.name LIKE ?)"
            params.append(f"%{person_id}%")
            params.append(f"%{person_id}%")

        if department and department != "All":
            query += " AND p.department = ?"
            params.append(department)

        query += " ORDER BY a.date DESC, a.time_in DESC"

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def delete_attendance_log(self, log_id: int) -> bool:
        """Delete an attendance log entry by ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM attendance WHERE id = ?", (log_id,))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error("Error deleting log %s: %s", log_id, e)
            return False

    def clear_attendance_logs(self, target_date: Optional[str] = None) -> int:
        """Clears attendance logs (optionally for a specific date). Returns number of deleted rows."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if target_date:
                    cursor.execute("DELETE FROM attendance WHERE date = ?", (target_date,))
                else:
                    cursor.execute("DELETE FROM attendance")
                deleted_count = cursor.rowcount
                conn.commit()
                return deleted_count
        except sqlite3.Error as e:
            logger.error("Error clearing attendance logs: %s", e)
            return 0

    def get_dashboard_stats(self, target_date: Optional[str] = None) -> Dict[str, int]:
        """Calculates current statistics for GUI dashboard metrics."""
        today_str = target_date or date.today().isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Total Enrolled
            cursor.execute("SELECT COUNT(*) FROM persons")
            total_enrolled = cursor.fetchone()[0]

            # Today's Present
            cursor.execute("""
                SELECT COUNT(*) FROM attendance WHERE date = ? AND status = 'Present'
            """, (today_str,))
            total_present = cursor.fetchone()[0]

            # Today's Late
            cursor.execute("""
                SELECT COUNT(*) FROM attendance WHERE date = ? AND status = 'Late'
            """, (today_str,))
            total_late = cursor.fetchone()[0]

            # Total Marked Today
            total_marked = total_present + total_late
            total_absent = max(0, total_enrolled - total_marked)

            return {
                "total_enrolled": total_enrolled,
                "total_present": total_present,
                "total_late": total_late,
                "total_absent": total_absent,
                "total_marked": total_marked
            }


if __name__ == "__main__":
    db = DatabaseManager()
    print("Database system check completed.")
