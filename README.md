# Smart Campus Classroom Management System (SCCS)
### Deen Dayal Upadhyaya Gorakhpur University (DDUGU)
*Institute of Engineering and Technology (IET) & Deeksha Bhawan*  
*Build With AI: DevOps 2026 Problem Statement Solution*

---

## 🚀 Overview

The **Smart Campus Classroom Management System (SCCS)** is a centralised platform for academic schedule coordination, room discovery, conflict prevention, and student notifications across **IET** and **Deeksha Bhawan** at DDUGU.

It prevents classroom scheduling conflicts, addresses the incident where students missed their NSS minor exams by publishing clear room allotments, provides role-based access, maintains an immutable audit trail, and features an intelligent AI scheduling assistant.

---

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python), Uvicorn, SQLite3, Pydantic v2
- **Frontend**: Responsive Web Dashboard (HTML5, CSS3, Modern JavaScript) with interactive campus floor blueprints
- **Algorithms**: Interval overlap constraint satisfaction, Multi-criteria Room Recommendation Engine
- **DevOps**: Docker, Docker Compose, GitHub Actions CI/CD pipeline
- **Testing**: Python `unittest` test suite & FastAPI `TestClient`

---

## 🔑 Pre-Seeded Demo Credentials

The system comes pre-populated with campus buildings, classrooms, laboratories, and users across all roles:

| Role | Name | Email | Password |
|---|---|---|---|
| **Faculty** | Dr. R. K. Sharma (CSE Dept) | `prof.sharma@ddugu.ac.in` | `faculty123` |
| **Faculty** | Dr. Sunita Verma (AI ML Dept) | `prof.verma@ddugu.ac.in` | `faculty123` |
| **Faculty** | Prof. Alok Singh (ECE/ME Dept) | `prof.singh@ddugu.ac.in` | `faculty123` |
| **Student** | Rahul Gupta (CSE 3rd Yr Sec A) | `student.cse@ddugu.ac.in` | `student123` |
| **Student** | Priya Maurya (AI ML 2nd Yr Sec B)| `student.aiml@ddugu.ac.in` | `student123` |
| **Admin** | System Administrator | `admin@ddugu.ac.in` | `admin123` |

*(Tip: In the web UI, you can also switch between Student, Faculty, and Admin in one click using the quick switcher in the header!)*

---

## 🏃 Quick Start Instructions

### Option 1: Run Locally with Python

```powershell
# 1. Activate virtual environment (if using Windows PowerShell)
.\venv\Scripts\Activate.ps1

# 2. Run the application
python main.py
```
Then navigate to **`http://localhost:8000`** in your browser.

- **Web Dashboard**: `http://localhost:8000/` or `http://localhost:8000/ui`
- **Interactive Swagger API Docs**: `http://localhost:8000/docs`
- **ReDoc API Documentation**: `http://localhost:8000/redoc`

---

### Option 2: Run with Docker Compose

```bash
# Build and spin up container
docker-compose up --build -d

# Check logs
docker-compose logs -f

# Teardown
docker-compose down
```

---

## 🧪 Running Automated Tests

Run the full automated test suite covering authentication, conflict prevention, capacity validation, timetable lookup, notices, student grievance reports, audit logging, and AI assistant:

```powershell
.\venv\Scripts\python.exe -m unittest tests/test_api.py
```

---

## 📚 Complete Architectural Documentation

For full architectural diagrams, component breakdown, mathematical formulation of the room recommendation engine, and operational workflows, please refer to:
👉 **[DOCS.md](DOCS.md)**

