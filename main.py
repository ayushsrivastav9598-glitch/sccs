import os
import sqlite3
import hashlib
import secrets
import hmac
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

from app.database import get_db, init_db
from app.seed_data import seed_database
from app.routes import (
    auth_routes,
    room_routes,
    booking_routes,
    schedule_routes,
    notice_routes,
    report_routes,
    audit_routes,
    ai_routes
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database and seed required campus datasets
    init_db()
    seed_database()
    yield

tags_metadata = [
    {
        "name": "Rooms & Blueprints",
        "description": "Interactive 2D spatial vacancy queries, floor plans, and capacity filtering for IET Main Building (Ground, 1st, 2nd floors) and Deeksha Bhawan (LH01-LH14).",
    },
    {
        "name": "Faculty Booking & Conflict Prevention",
        "description": "Conflict-proof atomic room reservations, interval overlap validation (max(S1,S2) < min(E1,E2)), and heuristic alternative venue recommendations.",
    },
    {
        "name": "Academic Schedules & Student Access",
        "description": "Multi-branch timetable discovery, semester schedule queries, and dynamic CSV/JSON spreadsheet export for 6 engineering branches.",
    },
    {
        "name": "Academic Notices & Schedule Updates",
        "description": "High-priority NSS minor exam announcements, schedule updates, and urgent cancellation alerts.",
    },
    {
        "name": "Student Grievance & Conflict Reporting",
        "description": "Student reporting of classroom clashes, equipment faults, locked halls, and staff resolution workflow.",
    },
    {
        "name": "Intelligent Assistance",
        "description": "Natural language heuristic campus assistant for intelligent room vacancy queries and timetable guidance.",
    },
    {
        "name": "Accountability & Audit Trail",
        "description": "Immutable, chronological audit ledger for reservations, notices, cancellations, and administrative overrides.",
    },
    {
        "name": "Authentication",
        "description": "PBKDF2-based password hashing, bearer tokens, and Role-Based Access Control (Admin, Faculty, Student).",
    },
    {
        "name": "System Health & Web UI",
        "description": "Root web application entry point, status checks, and browser UI serving.",
    },
    {
        "name": "Student Registration & Profile (Legacy)",
        "description": "Original student management endpoints preserved for backwards compatibility.",
    },
]

app = FastAPI(
    title="Smart Campus Classroom Management System",
    description="Official API Documentation & Interactive Swagger Playground for Deen Dayal Upadhyaya Gorakhpur University (DDUGU) — IET & Deeksha Bhawan.",
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include Modular Feature Routers
app.include_router(auth_routes.router)
app.include_router(room_routes.router)
app.include_router(booking_routes.router)
app.include_router(schedule_routes.router)
app.include_router(notice_routes.router)
app.include_router(report_routes.router)
app.include_router(audit_routes.router)
app.include_router(ai_routes.router)

# Models for backwards compatibility with original endpoints
class Student(BaseModel):
    name: str
    email: EmailStr
    password: str

class Login(BaseModel):
    email: EmailStr
    password: str

# Home Endpoint - Serves HTML UI for web browsers and JSON status for API clients
@app.get("/", tags=["System Health & Web UI"], summary="System Status & Web Entrypoint")
def home(request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" in accept and os.path.exists(os.path.join(static_dir, "index.html")):
        return FileResponse(os.path.join(static_dir, "index.html"))
    return {
        "message": "Welcome to Smart Campus Classroom System!",
        "status": "Backend is running successfully",
        "documentation": "/docs",
        "web_ui": "/ui"
    }

@app.get("/ui", tags=["System Health & Web UI"], summary="Web Application UI")
def ui():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "UI assets loading"}

# ==================== Preserved Original Endpoints ====================
@app.post("/students/register", tags=["Student Registration & Profile (Legacy)"], summary="Register New Student")
def register_student(student: Student):
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        student.password.encode(),
        salt.encode(),
        100000
    ).hex()

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO students (name, email, password, role) VALUES (?, ?, ?, 'student')",
            (student.name, student.email, salt + ":" + password_hash)
        )
        conn.execute(
            "INSERT OR IGNORE INTO users (name, email, password, role) VALUES (?, ?, ?, 'student')",
            (student.name, student.email, salt + ":" + password_hash)
        )
        conn.commit()

        return {
            "message": "Student registered successfully!",
            "name": student.name,
            "email": student.email
        }
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    finally:
        conn.close()

@app.post("/students/login", tags=["Student Registration & Profile (Legacy)"], summary="Student Login")
def login_student(login: Login):
    conn = get_db()
    try:
        student = conn.execute(
            "SELECT name, email, password FROM students WHERE email = ?",
            (login.email,)
        ).fetchone()

        if student is None:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        salt, stored_hash = student["password"].split(":", 1)
        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            login.password.encode(),
            salt.encode(),
            100000
        ).hex()

        if not hmac.compare_digest(password_hash, stored_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        return {
            "message": "Login successful!",
            "name": student["name"],
            "email": student["email"]
        }
    finally:
        conn.close()

@app.put("/students/{student_id}", tags=["Student Registration & Profile (Legacy)"], summary="Update Student Details")
def update_student(student_id: int, student: Student):
    conn = get_db()
    try:
        cursor = conn.execute(
            "UPDATE students SET name=?, email=? WHERE id=?",
            (student.name, student.email, student_id)
        )
        conn.execute(
            "UPDATE users SET name=?, email=? WHERE id=?",
            (student.name, student.email, student_id)
        )
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Student not found")

        return {"message": "Student updated successfully"}
    finally:
        conn.close()

@app.get("/students", tags=["Student Registration & Profile (Legacy)"], summary="List All Students")
def get_students():
    conn = get_db()
    students = conn.execute(
        "SELECT id, name, email FROM students"
    ).fetchall()
    conn.close()
    return [dict(student) for student in students]

if __name__ == "__main__":
    import uvicorn
    # Initialize DB before server startup
    init_db()
    seed_database()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
