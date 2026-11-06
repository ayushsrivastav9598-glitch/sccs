import sqlite3
import os
from .config import DATABASE_PATH

def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Users table (enhanced from students table)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student',
            branch TEXT,
            year INTEGER,
            section TEXT,
            department TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Ensure backward compatibility with existing 'students' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student',
            branch TEXT,
            year INTEGER,
            section TEXT,
            department TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Check if extra columns exist on students table, if not add them
    cursor.execute("PRAGMA table_info(students)")
    columns = [col[1] for col in cursor.fetchall()]
    for col_name, col_type in [
        ("role", "TEXT DEFAULT 'student'"),
        ("branch", "TEXT"),
        ("year", "INTEGER"),
        ("section", "TEXT"),
        ("department", "TEXT"),
        ("created_at", "TIMESTAMP")
    ]:
        if col_name not in columns:
            cursor.execute(f"ALTER TABLE students ADD COLUMN {col_name} {col_type}")

    # Copy any existing students into users table if not already present
    cursor.execute("SELECT id, name, email, password, role, branch, year, section FROM students")
    for s in cursor.fetchall():
        cursor.execute("""
            INSERT OR IGNORE INTO users (id, name, email, password, role, branch, year, section)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (s["id"], s["name"], s["email"], s["password"], s["role"] or "student", s["branch"], s["year"], s["section"]))

    # 2. Buildings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS buildings (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT NOT NULL,
            description TEXT,
            distance_from_iet_meters INTEGER DEFAULT 0
        )
    """)

    # 3. Rooms table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id TEXT PRIMARY KEY,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            building_id TEXT NOT NULL,
            floor TEXT NOT NULL,
            room_type TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            facilities TEXT,
            permitted_uses TEXT,
            is_active INTEGER DEFAULT 1,
            x_coord INTEGER DEFAULT 0,
            y_coord INTEGER DEFAULT 0,
            width INTEGER DEFAULT 100,
            height INTEGER DEFAULT 60,
            FOREIGN KEY (building_id) REFERENCES buildings (id)
        )
    """)

    # 4. Bookings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id TEXT NOT NULL,
            title TEXT NOT NULL,
            purpose TEXT NOT NULL,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            booked_by_user_id INTEGER NOT NULL,
            booked_by_name TEXT NOT NULL,
            booked_by_email TEXT NOT NULL,
            branch TEXT DEFAULT 'ALL',
            year INTEGER DEFAULT 0,
            section TEXT DEFAULT 'ALL',
            expected_students INTEGER NOT NULL,
            status TEXT DEFAULT 'CONFIRMED',
            is_test_data INTEGER DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_id) REFERENCES rooms (id)
        )
    """)

    # 5. Academic Notices / Announcements table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            notice_type TEXT NOT NULL,
            target_branch TEXT DEFAULT 'ALL',
            target_year INTEGER DEFAULT 0,
            target_section TEXT DEFAULT 'ALL',
            room_id TEXT,
            booking_id INTEGER,
            priority TEXT DEFAULT 'NORMAL',
            published_by_user_id INTEGER,
            published_by_name TEXT,
            published_by_email TEXT,
            is_test_data INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_id) REFERENCES rooms (id),
            FOREIGN KEY (booking_id) REFERENCES bookings (id)
        )
    """)

    # 6. Student Conflict / Outdated Info Reports
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            student_name TEXT NOT NULL,
            student_email TEXT NOT NULL,
            booking_id INTEGER,
            room_id TEXT,
            report_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'OPEN',
            admin_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users (id),
            FOREIGN KEY (booking_id) REFERENCES bookings (id),
            FOREIGN KEY (room_id) REFERENCES rooms (id)
        )
    """)

    # 7. Audit Log Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            user_id INTEGER,
            user_name TEXT,
            user_email TEXT,
            user_role TEXT,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            details TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
