import sqlite3
import hashlib
import secrets
from .database import get_db

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000).hex()
    return f"{salt}:{pwd_hash}"

def seed_database():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Seed Buildings
    buildings = [
        ("IET", "Institute of Engineering and Technology", "IET", "Main engineering campus hosting CSE, AI ML, AI DS, ECE, ME, and IT branches across 3 floors.", 0),
        ("DEEKSHA_BHAWAN", "Deeksha Bhawan", "DB", "Secondary academic building ~100m from IET, used for examinations, lectures, and capacity overflow.", 100)
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO buildings (id, name, code, description, distance_from_iet_meters)
        VALUES (?, ?, ?, ?, ?)
    """, buildings)

    # 2. Seed Rooms
    # Coordinates are mapped on a 1000x500 blueprint grid for interactive visualization
    rooms = [
        # --- IET GROUND FLOOR ---
        ("IET-G-LIB", "Library", "Library & Reading Hall", "IET", "Ground", "Library", 180,
         "Reading Desks, Exam Partitioning, Central AC, High-speed Wi-Fi", "Study, Minor Examination, General Exam", 1, 60, 40, 220, 110),
        ("IET-G-TO", "Teachers' Office", "Teachers' Office (Faculty Cabins)", "IET", "Ground", "Office", 25,
         "Faculty Cubicles, Consultation Table, Storage", "Faculty Work, Consultation", 1, 60, 170, 160, 80),
        ("IET-G-PC", "Placement Cell", "Placement & Training Cell", "IET", "Ground", "Office", 30,
         "Interview Rooms, Conference Table, Projector Screen", "Placements, Interviews, Corporate Meetings", 1, 350, 40, 130, 90),
        ("IET-G-DIR", "Director Office", "Director's Office & Suite", "IET", "Ground", "Office", 15,
         "Executive Conference Table, Secretary Desk, AC", "Administration, Official Meetings", 1, 350, 150, 130, 90),
        ("IET-G-ADM", "Admin Office", "Administrative & Accounts Office", "IET", "Ground", "Office", 20,
         "Clerical Counters, Records Archive, High-speed LAN", "Administration, Fee/Enquiry Desk", 1, 230, 170, 110, 80),

        # --- IET FIRST FLOOR ---
        # Labs (top row on blueprint: IET22 ME, IET16 CSE, IET14 ECE, IET15 IT)
        ("IET-1-ME-LAB", "ME Lab (IET22)", "Mechanical Engineering Lab", "IET", "1st Floor", "Laboratory", 40,
         "CAD/CAM Terminals, SolidWorks, Simulation Tools, Safety Gear", "Practical Session, CAD Workshop", 1, 60, 40, 100, 85),
        ("IET-1-CSE-LAB", "CSE Lab (IET16)", "Computer Science & Engineering Lab", "IET", "1st Floor", "Laboratory", 45,
         "45 High-end PCs, Ubuntu/Windows, Gigabit LAN, Projector", "Practical Session, Minor Examination, Coding Lab", 1, 175, 40, 100, 85),
        ("IET-1-ECE-LAB", "ECE Lab (IET14)", "Electronics & Comm. Engineering Lab", "IET", "1st Floor", "Laboratory", 40,
         "Digital Oscilloscopes, Microcontroller Kits, Function Generators", "Practical Session, Hardware Lab", 1, 290, 40, 100, 85),
        ("IET-1-IT-LAB", "IT Lab (IET15)", "Information Technology Lab", "IET", "1st Floor", "Laboratory", 45,
         "45 Networked Desktops, Cloud Sandbox, Projector, Wi-Fi", "Practical Session, Minor Examination", 1, 405, 40, 100, 85),
        # Classrooms (bottom row on blueprint: IET20, IET19, IET18, IET17)
        ("IET-1-20", "IET20", "Classroom IET 20", "IET", "1st Floor", "Classroom", 75,
         "Digital Projector, Audio System, Whiteboard, Stepped Desks", "Lecture, Minor Examination, Extra Lecture", 1, 60, 150, 100, 85),
        ("IET-1-19", "IET19", "Classroom IET 19", "IET", "1st Floor", "Classroom", 75,
         "Digital Projector, Whiteboard, Stepped Desks", "Lecture, Minor Examination, Extra Lecture", 1, 175, 150, 100, 85),
        ("IET-1-18", "IET18", "Classroom IET 18", "IET", "1st Floor", "Classroom", 75,
         "Digital Projector, Whiteboard, Stepped Desks", "Lecture, Minor Examination, Extra Lecture", 1, 290, 150, 100, 85),
        ("IET-1-17", "IET17", "Classroom IET 17", "IET", "1st Floor", "Classroom", 75,
         "Digital Projector, Whiteboard, Stepped Desks", "Lecture, Minor Examination, Extra Lecture", 1, 405, 150, 100, 85),

        # --- IET SECOND FLOOR ---
        # Seminar Hall (approx 200 students)
        ("IET-2-32", "Seminar Hall (IET32)", "Seminar Hall IET 32", "IET", "2nd Floor", "Seminar Hall", 200,
         "Dual HD Projectors, Surround Sound, Stage, Central AC, Podium", "Seminar, Minor Examination, Combined Lecture, Event", 1, 60, 40, 215, 85),
        # Classrooms
        ("IET-2-24", "IET24", "Classroom IET 24", "IET", "2nd Floor", "Classroom", 75,
         "Projector, Whiteboard, Stepped Desks", "Lecture, Minor Examination, Extra Lecture", 1, 290, 40, 100, 85),
        ("IET-2-25", "IET25", "Classroom IET 25", "IET", "2nd Floor", "Classroom", 75,
         "Projector, Whiteboard, Stepped Desks", "Lecture, Minor Examination, Extra Lecture", 1, 405, 40, 100, 85),
        ("IET-2-30", "IET30", "Classroom IET 30", "IET", "2nd Floor", "Classroom", 75,
         "Projector, Whiteboard, Stepped Desks", "Lecture, Minor Examination, Extra Lecture", 1, 60, 150, 100, 85),
        ("IET-2-29", "IET29", "Classroom IET 29", "IET", "2nd Floor", "Classroom", 75,
         "Projector, Whiteboard, Stepped Desks", "Lecture, Minor Examination, Extra Lecture", 1, 175, 150, 100, 85),
        ("IET-2-28", "IET28", "Classroom IET 28", "IET", "2nd Floor", "Classroom", 75,
         "Projector, Whiteboard, Stepped Desks", "Lecture, Minor Examination, Extra Lecture", 1, 290, 150, 100, 85),
        ("IET-2-23", "IET23", "Classroom IET 23", "IET", "2nd Floor", "Classroom", 75,
         "Projector, Whiteboard, Stepped Desks", "Lecture, Minor Examination, Extra Lecture", 1, 405, 150, 100, 85),

        # --- DEEKSHA BHAWAN GROUND FLOOR (LH01 - LH07) ---
        ("DB-G-LH01", "LH01", "Lecture Hall LH01", "DEEKSHA_BHAWAN", "Ground", "Classroom", 85,
         "Ceiling Projector, Mic & Amplification, Tiered Seating", "Lecture, Minor Examination, University Exam", 1, 550, 40, 110, 50),
        ("DB-G-LH02", "LH02", "Lecture Hall LH02", "DEEKSHA_BHAWAN", "Ground", "Classroom", 85,
         "Ceiling Projector, Whiteboard, Tiered Seating", "Lecture, Minor Examination, University Exam", 1, 550, 95, 110, 45),
        ("DB-G-LH03", "LH03", "Lecture Hall LH03", "DEEKSHA_BHAWAN", "Ground", "Classroom", 80,
         "Whiteboard, Tiered Desks", "Lecture, Minor Examination", 1, 580, 145, 60, 45),
        ("DB-G-LH04", "LH04", "Lecture Hall LH04", "DEEKSHA_BHAWAN", "Ground", "Classroom", 80,
         "Whiteboard, Tiered Desks", "Lecture, Minor Examination", 1, 645, 145, 60, 45),
        ("DB-G-LH05", "LH05", "Lecture Hall LH05", "DEEKSHA_BHAWAN", "Ground", "Classroom", 90,
         "Projector, Whiteboard, Podium", "Lecture, Minor Examination, University Exam", 1, 750, 70, 70, 75),
        ("DB-G-LH06", "LH06", "Lecture Hall LH06", "DEEKSHA_BHAWAN", "Ground", "Classroom", 85,
         "Whiteboard, Tiered Seating", "Lecture, Minor Examination", 1, 550, 205, 80, 50),
        ("DB-G-LH07", "LH07", "Lecture Hall LH07", "DEEKSHA_BHAWAN", "Ground", "Classroom", 85,
         "Whiteboard, Projector", "Lecture, Minor Examination", 1, 700, 205, 80, 50),

        # --- DEEKSHA BHAWAN FIRST FLOOR (LH08 - LH14) ---
        ("DB-1-LH08", "LH08", "Lecture Hall LH08", "DEEKSHA_BHAWAN", "1st Floor", "Classroom", 90,
         "Projector, Audio System, Whiteboard, Tiered Seating", "Lecture, Minor Examination, University Exam", 1, 550, 40, 110, 50),
        ("DB-1-LH09", "LH09", "Lecture Hall LH09", "DEEKSHA_BHAWAN", "1st Floor", "Classroom", 85,
         "Projector, Whiteboard", "Lecture, Minor Examination, University Exam", 1, 550, 95, 110, 45),
        ("DB-1-LH10", "LH10", "Lecture Hall LH10", "DEEKSHA_BHAWAN", "1st Floor", "Classroom", 80,
         "Whiteboard, Tiered Desks", "Lecture, Minor Examination", 1, 580, 145, 60, 45),
        ("DB-1-LH11", "LH11", "Lecture Hall LH11", "DEEKSHA_BHAWAN", "1st Floor", "Classroom", 80,
         "Whiteboard, Tiered Desks", "Lecture, Minor Examination", 1, 645, 145, 60, 45),
        ("DB-1-LH12", "LH12", "Lecture Hall LH12", "DEEKSHA_BHAWAN", "1st Floor", "Classroom", 90,
         "Projector, Whiteboard, Podium", "Lecture, Minor Examination, University Exam", 1, 750, 70, 70, 75),
        ("DB-1-LH13", "LH13", "Lecture Hall LH13", "DEEKSHA_BHAWAN", "1st Floor", "Classroom", 85,
         "Whiteboard, Tiered Seating", "Lecture, Minor Examination", 1, 550, 205, 80, 50),
        ("DB-1-LH14", "LH14", "Lecture Hall LH14", "DEEKSHA_BHAWAN", "1st Floor", "Classroom", 85,
         "Whiteboard, Projector", "Lecture, Minor Examination", 1, 700, 205, 80, 50),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO rooms (id, code, name, building_id, floor, room_type, capacity, facilities, permitted_uses, is_active, x_coord, y_coord, width, height)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rooms)

    # 3. Seed Standard Users across roles (Student, Faculty, Admin)
    # Check if admin already exists
    cursor.execute("SELECT id FROM users WHERE email = 'admin@ddugu.ac.in'")
    if not cursor.fetchone():
        admin_pwd = hash_password("admin123")
        cursor.execute("""
            INSERT INTO users (name, email, password, role, branch, year, section, department)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("System Administrator", "admin@ddugu.ac.in", admin_pwd, "admin", "ADMIN", 0, "ALL", "Academic Coordination Office"))

    # Faculty members
    faculty_members = [
        ("Dr. R. K. Sharma", "prof.sharma@ddugu.ac.in", "faculty123", "faculty", "CSE", 0, "ALL", "Computer Science & Engineering"),
        ("Dr. Sunita Verma", "prof.verma@ddugu.ac.in", "faculty123", "faculty", "AI ML", 0, "ALL", "Artificial Intelligence & Data Science"),
        ("Prof. Alok Singh", "prof.singh@ddugu.ac.in", "faculty123", "faculty", "ECE", 0, "ALL", "Electronics & Mechanical Engineering")
    ]
    for name, email, pwd, role, branch, year, sec, dept in faculty_members:
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if not cursor.fetchone():
            hashed = hash_password(pwd)
            cursor.execute("""
                INSERT INTO users (name, email, password, role, branch, year, section, department)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, email, hashed, role, branch, year, sec, dept))

    # Sample Students across branches and batches
    sample_students = [
        ("Rahul Gupta", "student.cse@ddugu.ac.in", "student123", "student", "CSE", 3, "A", "Computer Science"),
        ("Priya Maurya", "student.aiml@ddugu.ac.in", "student123", "student", "AI ML", 2, "B", "Artificial Intelligence"),
        ("Anurag Srivastava", "student.aids@ddugu.ac.in", "student123", "student", "AI DS", 3, "A", "Data Science"),
        ("Sneha Pandey", "student.ece@ddugu.ac.in", "student123", "student", "ECE", 4, "A", "Electronics & Comm"),
        ("Vikram Yadav", "student.me@ddugu.ac.in", "student123", "student", "ME", 2, "A", "Mechanical Eng"),
        ("Kavita Mishra", "student.it@ddugu.ac.in", "student123", "student", "IT", 3, "A", "Information Technology")
    ]
    for name, email, pwd, role, branch, year, sec, dept in sample_students:
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if not cursor.fetchone():
            hashed = hash_password(pwd)
            cursor.execute("""
                INSERT INTO users (name, email, password, role, branch, year, section, department)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, email, hashed, role, branch, year, sec, dept))
            # Also keep students table updated
            cursor.execute("""
                INSERT OR IGNORE INTO students (name, email, password, role, branch, year, section, department)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, email, hashed, role, branch, year, sec, dept))

    # 4. Seed Test Bookings (clearly marked with is_test_data = 1)
    # Check if test bookings already exist
    cursor.execute("SELECT COUNT(*) FROM bookings WHERE is_test_data = 1")
    count_test = cursor.fetchone()[0]
    if count_test == 0:
        test_bookings = [
            ("IET-1-17", "[TEST DATA] Minor Examination: Database Management Systems", "Minor Examination",
             "2026-11-10", "10:00", "12:00", 120, 2, "Dr. R. K. Sharma", "prof.sharma@ddugu.ac.in",
             "CSE", 3, "A", 75, "CONFIRMED", 1, "Minor Examination scheduled as per academic calendar."),

            ("IET-1-CSE-LAB", "[TEST DATA] Practical Session: Machine Learning Algorithms", "Practical Session",
             "2026-11-10", "14:00", "16:00", 120, 3, "Dr. Sunita Verma", "prof.verma@ddugu.ac.in",
             "AI ML", 2, "B", 42, "CONFIRMED", 1, "Students must bring their college ID cards."),

            ("IET-2-32", "[TEST DATA] Combined Guest Lecture: Emerging Trends in Generative AI", "Seminar",
             "2026-11-11", "11:00", "13:00", 120, 2, "Dr. R. K. Sharma", "prof.sharma@ddugu.ac.in",
             "ALL", 0, "ALL", 185, "CONFIRMED", 1, "Mandatory for 3rd and 4th year engineering students."),

            ("DB-G-LH01", "[TEST DATA] Minor Exam: NSS & Environmental Studies (Overflow)", "Minor Examination",
             "2026-11-12", "09:30", "11:30", 120, 4, "Prof. Alok Singh", "prof.singh@ddugu.ac.in",
             "AI ML", 1, "A", 75, "CONFIRMED", 1, "Deeksha Bhawan allocated to avoid NSS exam clashes.")
        ]
        cursor.executemany("""
            INSERT INTO bookings (room_id, title, purpose, date, start_time, end_time, duration_minutes,
                                  booked_by_user_id, booked_by_name, booked_by_email, branch, year, section,
                                  expected_students, status, is_test_data, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, test_bookings)

    # 5. Seed Academic Notices (Directly addressing the NSS examination confusion mentioned in problem statement)
    cursor.execute("SELECT COUNT(*) FROM notices")
    if cursor.fetchone()[0] == 0:
        test_notices = [
            ("IMPORTANT: NSS Minor Examination Hall Allotment",
             "All 1st and 2nd year students registered for NSS Minor Examination must report to Deeksha Bhawan LH01 and LH02 at 09:15 AM sharp. Do not report to IET main building as rooms IET17-20 are occupied by semester 5 exams.",
             "EXAM_SCHEDULE", "ALL", 1, "ALL", "DB-G-LH01", 4, "URGENT",
             1, "System Administrator", "admin@ddugu.ac.in", 1),

            ("Rescheduled: CSE 3rd Year DBMS Practical Session",
             "The DBMS practical lab scheduled for 10th Nov at 10:00 AM has been relocated to CSE Lab (IET16) on 1st Floor. Please bring your practical record books.",
             "RESCHEDULING", "CSE", 3, "A", "IET-1-CSE-LAB", 2, "HIGH",
             2, "Dr. R. K. Sharma", "prof.sharma@ddugu.ac.in", 1),

            ("Deeksha Bhawan Availability for Extra Classes",
             "Faculty members are notified that Deeksha Bhawan LH01 to LH07 (Ground Floor) are fully operational for supplementary and makeup classes whenever IET classrooms are occupied.",
             "GENERAL", "ALL", 0, "ALL", "DB-G-LH01", None, "NORMAL",
             1, "System Administrator", "admin@ddugu.ac.in", 1)
        ]
        cursor.executemany("""
            INSERT INTO notices (title, content, notice_type, target_branch, target_year, target_section,
                                 room_id, booking_id, priority, published_by_user_id, published_by_name,
                                 published_by_email, is_test_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, test_notices)

    # 6. Seed Sample Audit Log
    cursor.execute("SELECT COUNT(*) FROM audit_logs")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO audit_logs (action, user_id, user_name, user_email, user_role, entity_type, entity_id, details)
            VALUES ('SYSTEM_INIT', 1, 'System Administrator', 'admin@ddugu.ac.in', 'admin', 'SYSTEM', 'CAMPUS_INIT',
                    'Campus infrastructure initialized with IET (Ground, 1st, 2nd Floors) and Deeksha Bhawan (LH01-LH14)')
        """)

    conn.commit()
    conn.close()

