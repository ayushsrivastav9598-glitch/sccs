import unittest
import json
import secrets
from fastapi.testclient import TestClient
import main

class TestSmartCampusSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        main.init_db()
        main.seed_database()
        cls.client = TestClient(main.app)

        # Obtain tokens for Faculty, Student, Admin
        # 1. Faculty
        res_fac = cls.client.post("/auth/login", json={
            "email": "prof.sharma@ddugu.ac.in",
            "password": "faculty123"
        })
        cls.faculty_token = res_fac.json().get("token")
        cls.faculty_header = {"Authorization": f"Bearer {cls.faculty_token}"}

        # 2. Student
        res_stu = cls.client.post("/auth/login", json={
            "email": "student.cse@ddugu.ac.in",
            "password": "student123"
        })
        cls.student_token = res_stu.json().get("token")
        cls.student_header = {"Authorization": f"Bearer {cls.student_token}"}

        # 3. Admin
        res_adm = cls.client.post("/auth/login", json={
            "email": "admin@ddugu.ac.in",
            "password": "admin123"
        })
        cls.admin_token = res_adm.json().get("token")
        cls.admin_header = {"Authorization": f"Bearer {cls.admin_token}"}

    def test_01_home_endpoint(self):
        """Verify home endpoint returns operational status."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "Backend is running successfully")

    def test_02_backward_compatibility_students(self):
        """Verify original student endpoints function as originally defined."""
        random_email = f"test_{secrets.token_hex(4)}@student.ddugu.ac.in"
        reg_res = self.client.post("/students/register", json={
            "name": "Integration Student",
            "email": random_email,
            "password": "pass123student"
        })
        self.assertEqual(reg_res.status_code, 200)

        login_res = self.client.post("/students/login", json={
            "email": random_email,
            "password": "pass123student"
        })
        self.assertEqual(login_res.status_code, 200)

        list_res = self.client.get("/students")
        self.assertEqual(list_res.status_code, 200)
        self.assertTrue(len(list_res.json()) >= 2)

    def test_03_room_discovery_and_blueprints(self):
        """Verify both IET and Deeksha Bhawan rooms and blueprints are available."""
        # List all rooms
        rooms_res = self.client.get("/rooms")
        self.assertEqual(rooms_res.status_code, 200)
        rooms = rooms_res.json()
        self.assertTrue(len(rooms) >= 20)

        # Verify IET rooms exist (Ground, 1st, 2nd)
        iet_rooms = [r for r in rooms if r["building_id"] == "IET"]
        self.assertTrue(any(r["code"] == "Library" for r in iet_rooms))
        self.assertTrue(any(r["code"] == "IET17" for r in iet_rooms))
        self.assertTrue(any("Seminar Hall" in r["name"] for r in iet_rooms))

        # Verify Deeksha Bhawan rooms exist (LH01-LH12)
        db_rooms = [r for r in rooms if r["building_id"] == "DEEKSHA_BHAWAN"]
        self.assertTrue(len(db_rooms) >= 10)
        self.assertTrue(any(r["code"] == "LH01" for r in db_rooms))

        # Test blueprints endpoint with live status
        bp_res = self.client.get("/rooms/blueprints?date=2026-11-10&time_slot=10:00")
        self.assertEqual(bp_res.status_code, 200)
        bp_data = bp_res.json()
        self.assertEqual(len(bp_data["buildings"]), 2)

    def test_04_availability_search(self):
        """Test search availability with capacity and room type filtering."""
        avail_res = self.client.post("/rooms/availability", json={
            "date": "2026-11-20",
            "start_time": "14:00",
            "duration_minutes": 60,
            "building_id": "IET",
            "required_capacity": 70
        })
        self.assertEqual(avail_res.status_code, 200)
        data = avail_res.json()
        self.assertGreater(data["available_rooms_count"], 0)

    def test_05_booking_and_conflict_prevention(self):
        """
        Verify that:
        1. A faculty member can successfully book a room.
        2. A conflicting overlapping booking is BLOCKED (HTTP 409).
        3. The response suggests intelligent alternative rooms in IET & Deeksha Bhawan.
        """
        # Clean up any leftover test booking from previous runs to ensure idempotency
        import app.database
        conn = app.database.get_db()
        conn.execute("DELETE FROM bookings WHERE title LIKE '%Unit Test Lecture%'")
        conn.commit()
        conn.close()

        target_date = "2026-12-01"
        target_room = "IET-1-18"

        # 1. Successful booking
        book_res = self.client.post("/bookings", headers=self.faculty_header, json={
            "room_id": target_room,
            "title": "Unit Test Lecture on Algorithms",
            "purpose": "Extra Lecture",
            "date": target_date,
            "start_time": "10:00",
            "duration_minutes": 120,
            "branch": "CSE",
            "year": 3,
            "section": "A",
            "expected_students": 70,
            "is_test_data": True
        })
        self.assertEqual(book_res.status_code, 201)
        booking_id = book_res.json()["booking_id"]

        # 2. Duplicate booking attempt on the same room & overlapping time: MUST FAIL WITH 409 CONFLICT
        conflict_res = self.client.post("/bookings", headers=self.faculty_header, json={
            "room_id": target_room,
            "title": "Conflicting Class Attempt",
            "purpose": "Minor Examination",
            "date": target_date,
            "start_time": "10:30",  # Overlaps with 10:00-12:00
            "duration_minutes": 60,
            "branch": "IT",
            "year": 2,
            "expected_students": 60,
            "is_test_data": True
        })
        self.assertEqual(conflict_res.status_code, 409)
        conflict_body = conflict_res.json()
        self.assertEqual(conflict_body["error"], "ROOM_CONFLICT")
        self.assertIn("Conflict detected", conflict_body["detail"])

        # 3. Alternatives must be returned
        alternatives = conflict_body.get("alternative_rooms", [])
        self.assertGreater(len(alternatives), 0)
        # Should include rooms with capacity >= 60
        for alt in alternatives:
            self.assertGreaterEqual(alt["capacity"], 55)

    def test_06_capacity_constraint_validation(self):
        """Booking 190 students in a 75-seat room should fail with capacity exceeded."""
        res = self.client.post("/bookings", headers=self.faculty_header, json={
            "room_id": "IET-1-19",  # capacity 75
            "title": "Mass Combined Session",
            "purpose": "Seminar",
            "date": "2026-12-05",
            "start_time": "14:00",
            "duration_minutes": 60,
            "expected_students": 190
        })
        self.assertEqual(res.status_code, 400)
        body = res.json()
        self.assertEqual(body["error"], "CAPACITY_EXCEEDED")
        # Should suggest Seminar Hall IET32 or Library which can hold ~180-200
        alt_ids = [alt["room_id"] for alt in body.get("alternative_rooms", [])]
        self.assertTrue("IET-2-32" in alt_ids or "IET-G-LIB" in alt_ids)

    def test_07_academic_timetable_and_notices(self):
        """Verify student timetable lookup and academic notice publishing."""
        # Query timetable for CSE Year 3 Section A
        tt_res = self.client.get("/schedules/timetable?branch=CSE&year=3&section=A")
        self.assertEqual(tt_res.status_code, 200)

        # Publish an urgent examination notice
        notice_res = self.client.post("/notices", headers=self.faculty_header, json={
            "title": "Minor Exam: Systems Programming Room Change",
            "content": "All students report to Deeksha Bhawan LH05 due to maintenance in IET19.",
            "notice_type": "EXAM_SCHEDULE",
            "target_branch": "CSE",
            "target_year": 3,
            "priority": "URGENT"
        })
        self.assertEqual(notice_res.status_code, 201)

        # Retrieve notices
        list_notices = self.client.get("/notices?priority=URGENT")
        self.assertEqual(list_notices.status_code, 200)
        self.assertTrue(len(list_notices.json()) >= 1)

    def test_08_student_conflict_reporting_and_resolution(self):
        """Student files report about outdated notice, Admin resolves it."""
        # 1. Student files report
        report_res = self.client.post("/reports", headers=self.student_header, json={
            "report_type": "EXAM_CLASH",
            "title": "Two exams overlapping on Friday 10 AM",
            "description": "NSS exam and Data Structures minor exam both listed in LH01."
        })
        self.assertEqual(report_res.status_code, 201)
        report_id = report_res.json()["id"]

        # 2. Admin resolves report
        resolve_res = self.client.put(f"/reports/{report_id}/resolve", headers=self.admin_header, json={
            "status": "RESOLVED",
            "admin_notes": "Data Structures exam shifted to LH02. Timetable updated."
        })
        self.assertEqual(resolve_res.status_code, 200)
        self.assertEqual(resolve_res.json()["status"], "RESOLVED")

    def test_09_audit_trail_accountability(self):
        """Verify audit trail keeps complete log of changes."""
        audit_res = self.client.get("/audit?limit=20", headers=self.admin_header)
        self.assertEqual(audit_res.status_code, 200)
        logs = audit_res.json()
        self.assertTrue(len(logs) > 0)
        actions = [l["action"] for l in logs]
        self.assertTrue(any("BOOKING" in a or "REPORT" in a or "NOTICE" in a or "SYSTEM" in a for a in actions))

    def test_10_ai_scheduling_assistant(self):
        """Test AI natural language assistant parsing and room recommendations."""
        ai_res = self.client.post("/ai/assist", json={
            "query": "Find a room for 75 students tomorrow at 10 AM for Minor Examination"
        })
        self.assertEqual(ai_res.status_code, 200)
        data = ai_res.json()
        self.assertEqual(data["extracted_params"]["capacity"], 75)
        self.assertEqual(data["extracted_params"]["purpose"], "Minor Examination")
        self.assertGreater(len(data["recommended_rooms"]), 0)

    def test_11_timetable_export(self):
        """Test exporting timetable to CSV and JSON formats."""
        res_csv = self.client.get("/schedules/export?branch=ALL&export_format=csv")
        self.assertEqual(res_csv.status_code, 200)
        self.assertIn("text/csv", res_csv.headers["content-type"])
        self.assertIn("Room Code", res_csv.text)

        res_json = self.client.get("/schedules/export?branch=ALL&export_format=json")
        self.assertEqual(res_json.status_code, 200)
        self.assertIsInstance(res_json.json(), list)

if __name__ == "__main__":
    unittest.main()
