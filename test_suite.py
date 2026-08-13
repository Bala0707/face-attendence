"""
Automated Test & Verification Suite for Face Recognition Attendance System.
Tests Database CRUD, Face Engine Training & Prediction, and Exporter capabilities.
"""

import os
import sys
import unittest
import numpy as np
import cv2

from database import DatabaseManager
from face_engine import FaceEngine
from export import AttendanceExporter


class TestFaceAttendanceSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = DatabaseManager()
        cls.engine = FaceEngine()
        cls.exporter = AttendanceExporter(cls.db)

    def test_01_database_operations(self):
        """Test Person CRUD & Attendance logging in SQLite DB."""
        test_id = "TEST_EMP_99"
        
        # Add Person
        success = self.db.add_person(
            person_id=test_id,
            name="Alice Smith",
            department="Engineering",
            role="Developer",
            email="alice@example.com"
        )
        self.assertTrue(success, "Failed to add test person to database.")

        # Get Person
        person = self.db.get_person(test_id)
        self.assertIsNotNone(person)
        self.assertEqual(person["name"], "Alice Smith")

        # Mark Attendance
        att_res = self.db.mark_attendance(person_id=test_id, confidence=92.5)
        self.assertTrue(att_res["success"], "Failed to mark attendance.")
        self.assertIn(att_res["status"], ["Present", "Late"])

        # Fetch Dashboard Stats
        stats = self.db.get_dashboard_stats()
        self.assertGreater(stats["total_enrolled"], 0)
        self.assertGreater(stats["total_marked"], 0)

    def test_02_face_engine_sample_and_train(self):
        """Test Face Engine sample saving and model training with synthetic face data."""
        test_id = "TEST_FACE_01"
        self.db.add_person(test_id, "Bob Tester", "QA", "Tester", "bob@example.com")

        # Create a synthetic test frame with a drawn square face
        synthetic_frame = np.ones((300, 300, 3), dtype=np.uint8) * 180
        # Draw face features
        cv2.circle(synthetic_frame, (150, 150), 60, (50, 50, 50), -1)
        cv2.circle(synthetic_frame, (130, 130), 10, (250, 250, 250), -1)
        cv2.circle(synthetic_frame, (170, 130), 10, (250, 250, 250), -1)
        cv2.ellipse(synthetic_frame, (150, 170), (25, 10), 0, 0, 180, (250, 250, 250), 3)

        bbox = (90, 90, 120, 120)
        sample_path = self.engine.save_sample_face(test_id, synthetic_frame, bbox, sample_idx=1)
        self.assertIsNotNone(sample_path, "Failed to save face sample.")

        # Train model
        train_success = self.engine.train_model()
        self.assertTrue(train_success, "Failed to train face recognition model.")

        # Predict
        prediction = self.engine.recognize_face(synthetic_frame, bbox)
        self.assertIn("person_id", prediction)

    def test_03_export_reports(self):
        """Test generating CSV, Excel, and HTML export reports."""
        csv_path = self.exporter.export_to_csv()
        self.assertTrue(os.path.exists(csv_path), "CSV report file not created.")

        excel_path = self.exporter.export_to_excel()
        self.assertTrue(os.path.exists(excel_path), "Excel report file not created.")

        html_path = self.exporter.export_to_html()
        self.assertTrue(os.path.exists(html_path), "HTML report file not created.")

    def test_04_validation_rejects_invalid_inputs(self):
        """Invalid person input and confidence values should be rejected safely."""
        self.assertFalse(self.db.add_person(person_id="   ", name="Valid Name"))
        self.assertFalse(self.db.add_person(person_id="VALID_001", name="   "))

        self.assertTrue(self.db.add_person(person_id="VALID_002", name="Validation Tester"))
        invalid_confidence = self.db.mark_attendance(person_id="VALID_002", confidence="not-a-number")
        self.assertFalse(invalid_confidence["success"])
        self.assertIn("confidence", invalid_confidence["message"].lower())

    def test_05_close_releases_database_resources(self):
        """DatabaseManager should offer an explicit cleanup path for connections."""
        cleanup_db = DatabaseManager()
        cleanup_db.add_person("CLEANUP_TEST", "Cleanup User")

        cleanup_db.close()

        self.assertTrue(cleanup_db.is_closed())

    @classmethod
    def tearDownClass(cls):
        # Cleanup test entries
        cls.db.delete_person("TEST_EMP_99")
        cls.db.delete_person("TEST_FACE_01")


if __name__ == "__main__":
    unittest.main()
