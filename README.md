# Smart Campus Classroom Management System (SCCS)
### Deen Dayal Upadhyaya Gorakhpur University (DDUGU)
*Institute of Engineering and Technology (IET) & Deeksha Bhawan*  
*Build With AI: DevOps 2026 Problem Statement Solution*

[![CI/CD Pipeline](https://github.com/ayushsrivastav9598-glitch/sccs/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/ayushsrivastav9598-glitch/sccs/actions)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-11%2F11%20Passing%20(100%25)-success.svg)](tests/test_api.py)
[![Design](https://img.shields.io/badge/Design-Minimalist%20Monochrome-111827.svg)](static/css/style.css)
[![Swagger UI](https://img.shields.io/badge/API%20Docs-Swagger%20%26%20ReDoc-black.svg)](http://localhost:8000/docs)

🔗 **GitHub Repository:** [https://github.com/ayushsrivastav9598-glitch/sccs.git](https://github.com/ayushsrivastav9598-glitch/sccs.git)

---

## 🏛️ Executive Summary & Problem Context

At **Deen Dayal Upadhyaya Gorakhpur University (DDUGU)**, the **Institute of Engineering and Technology (IET)** and nearby **Deeksha Bhawan** (~100m walking distance) accommodate six engineering branches across four academic years:
* **CSE** (Computer Science & Engineering) &bull; ~150 students (Sections A & B)
* **AI ML** (Artificial Intelligence & Machine Learning) &bull; ~150 students (Sections A & B)
* **AI DS** (Artificial Intelligence & Data Science) &bull; ~75 students (Section A)
* **ECE** (Electronics & Communication Engineering) &bull; ~75 students (Section A)
* **ME** (Mechanical Engineering) &bull; ~75 students (Section A)
* **IT** (Information Technology) &bull; ~75 students (Section A)

### The Real-World Incident Solved
During the **NSS Minor Examination**, conflicting informal notices and verbal room allocations led multiple faculty members to simultaneously claim Room G-01 and LH-04. Students arrived to find two concurrent exams scheduled in the same hall, forcing emergency relocations across the 100-meter corridor between IET and Deeksha Bhawan, causing severe delay, panic, and miscommunication.

The **Smart Campus Classroom Management System (SCCS)** eliminates classroom collisions, prevents double-booking at the database level, automatically recommends distance-aware alternative venues, synchronizes branch timetables, broadcasts urgent notices, and maintains an immutable audit ledger.

---

## ✨ Key Architectural Highlights

* **🎨 Minimalist Monochrome Aesthetic:** Pure black, white, and neutral grey palette (#111827 / #ffffff / #f3f4f6). Zero distracting gradients or flashy neon fills for maximum contrast, clarity, and institutional professionalism.
* **📂 Left Sidebar Navigation:** All 9 core campus modules arranged cleanly in a structured left navigation bar, accompanied by live quick links to Swagger UI (`/docs`) and ReDoc (`/redoc`).
* **📱 100% Mobile Responsive:** Adapts seamlessly across desktops, tablets, and smartphones (sticky touch-scrolling tab bar, iOS auto-zoom fix on inputs, dynamic grid cards, touch-optimized modals).
* **⚡ Interval Overlap Conflict Engine:** Evaluates temporal overlap mathematically ($\max(S_1, S_2) < \min(E_1, E_2)$) and enforces atomic booking blocks (HTTP 409 Conflict).
* **🧠 Distance-Aware Heuristic Suggester:** Automatically scores and recommends vacant alternative venues across IET and Deeksha Bhawan, penalizing Deeksha Bhawan by 15 points due to the 100m walking distance.
* **📖 In-App "Docs & Architecture" Tab:** Direct, in-browser architectural specifications, mathematical formulations, workflow diagrams, and complete REST API tables.
* **🛡️ Role-Based Access Control (RBAC):** Distinct privileges for Students, Faculty, and System Administrators with one-click header persona switching.
* **📑 Timetable Discovery & CSV Export:** Search academic schedules filtered by branch and year with one-click offline CSV spreadsheet export.
* **📢 Urgent Exam Notices & Broadcast:** High-priority pinned notice banners for NSS minor examinations and emergency room reallocations.
* **🚨 Student Grievance & Clash Reporting:** Students submit conflict and facility reports, and coordinators resolve them with published staff notes.
* **🔒 Immutable Audit Trail:** Chronological log tracking every booking, rescheduling, cancellation, and notice publication with timestamps and actor details.
* **🤖 Natural Language AI Assistant:** Heuristic natural language parsing to query room availability and campus guidance.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+ / 3.14 compatible), [Uvicorn](https://www.uvicorn.org/) ASGI Server |
| **Data Persistence** | SQLite 3 (WAL mode enabled, automated schema migration, transactional integrity) |
| **Data Validation** | [Pydantic v2](https://docs.pydantic.dev/) schemas with strict typing and input sanitization |
| **Security & Auth** | PBKDF2-HMAC-SHA256 password hashing (100,000 iterations), Bearer tokens, RBAC dependencies |
| **Frontend UI** | HTML5, Vanilla JavaScript (ES6+), Minimalist Monochrome CSS3 (zero external CSS frameworks) |
| **API Documentation** | Interactive Swagger UI (`/docs`), ReDoc (`/redoc`), OpenAPI 3.1.0 specification |
| **DevOps & Containers** | Multi-stage `Dockerfile`, `docker-compose.yml`, automated healthchecks |
| **CI/CD Automation** | GitHub Actions (`.github/workflows/ci-cd.yml`) for automated unit testing & container build |
| **Cloud Deployment** | Native [Render.com](https://render.com/) web service configuration via `render.yaml` |

---

## 🔑 Pre-Seeded Demo Personas

The system auto-initializes and pre-seeds a comprehensive campus dataset on first run. You can test different roles directly via credentials or by clicking the quick persona switcher in the web UI header:

| Role | Persona Name | Department / Branch | Email | Password |
|---|---|---|---|---|
| **Faculty** | Dr. R. K. Sharma | CSE Department | `prof.sharma@ddugu.ac.in` | `faculty123` |
| **Faculty** | Dr. Sunita Verma | AI ML Department | `prof.verma@ddugu.ac.in` | `faculty123` |
| **Faculty** | Prof. Alok Singh | ECE / ME Department | `prof.singh@ddugu.ac.in` | `faculty123` |
| **Student** | Rahul Gupta | CSE (3rd Year, Sec A) | `student.cse@ddugu.ac.in` | `student123` |
| **Student** | Priya Maurya | AI ML (2nd Year, Sec B) | `student.aiml@ddugu.ac.in` | `student123` |
| **Admin** | System Administrator | Campus Administration | `admin@ddugu.ac.in` | `admin123` |

---

## 📋 Role-Based Access Control (RBAC) Matrix

| Action / Capability | Student | Faculty | System Administrator |
|---|:---:|:---:|:---:|
| **View Live 2D Floor Blueprints & Vacancy** | ✅ Allowed | ✅ Allowed | ✅ Allowed |
| **Search Timetable & Download CSV Schedule** | ✅ Allowed | ✅ Allowed | ✅ Allowed |
| **Read Announcements & NSS Minor Exam Notices** | ✅ Allowed | ✅ Allowed | ✅ Allowed |
| **File Classroom Conflict / Equipment Grievance** | ✅ Allowed | ✅ Allowed | ✅ Allowed |
| **Reserve Rooms & Classrooms** | ❌ Blocked | ✅ Allowed | ✅ Allowed |
| **Cancel or Reschedule Bookings** | ❌ Blocked | ✅ Own Only | ✅ Campus-wide Any |
| **Broadcast Urgent Examination Notices** | ❌ Blocked | ✅ Allowed | ✅ Allowed |
| **Resolve Student Conflict Reports with Notes** | ❌ Blocked | ✅ Allowed | ✅ Allowed |
| **Inspect Chronological Immutable Audit Trail** | ❌ Blocked | ✅ Allowed | ✅ Allowed |
| **Campus-Wide Capacity & Venue Overrides** | ❌ Blocked | ❌ Blocked | ✅ Allowed |

---

## 🏃 Quick Start Guide

### Option 1: Run Locally (Python 3.10+)

```powershell
# 1. Clone the repository
git clone https://github.com/ayushsrivastav9598-glitch/sccs.git
cd sccs

# 2. Set up virtual environment (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the application server
uvicorn main:app --reload --port 8000
```

Once running, access the application in your browser:
* **Web Application UI:** [http://localhost:8000](http://localhost:8000) (or `/ui`)
* **Interactive Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc Specification:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### Option 2: Run with Docker & Docker Compose

```bash
# Build and run containerized application in background
docker-compose up --build -d

# View live service logs
docker-compose logs -f

# Stop container service
docker-compose down
```

---

### Option 3: Run the Automated 10-Step Problem Statement Walkthrough

To view a terminal-based simulation executing all 10 core problem statement requirements (booking, collision detection, alternative fit scoring, notice publishing, student timetable sync, grievance reporting, AI queries, and audit logging):

```powershell
.\venv\Scripts\python.exe scripts/demo_walkthrough.py
```

---

## 🧪 Automated Testing

The repository includes a comprehensive automated test suite covering all operational and edge cases:

```powershell
# Run the test suite
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

**Test Coverage Summary (11/11 Passing, 100% OK):**
* `test_01_health_and_seed_data`: Database connectivity, IET & Deeksha Bhawan room verification.
* `test_02_student_legacy_compatibility`: Backwards compatibility for student registration & login.
* `test_03_modular_auth_flow`: PBKDF2 authentication, token generation, and user validation.
* `test_04_room_listing_and_blueprints`: 2D spatial vacancy queries for IET and Deeksha Bhawan.
* `test_05_booking_and_conflict_prevention`: Interval overlap detection and HTTP 409 conflict blocking.
* `test_06_smart_alternative_recommendations`: Distance-aware heuristic fit scoring.
* `test_07_academic_schedules_and_csv_export`: Multi-branch timetable filtering and CSV export.
* `test_08_notices_and_announcements`: High-priority exam notice broadcasting.
* `test_09_student_conflict_reporting_workflow`: Grievance submission and staff resolution workflow.
* `test_10_immutable_audit_trail`: Chronological security ledger verification.
* `test_11_ai_scheduling_assistant`: Natural language prompt parsing and room recommendation.

---

## 🌐 Cloud Deployment (Render.com)

SCCS requires a persistent Python ASGI server with SQLite read/write database access. **Render.com** is the recommended host (unlike GitHub Pages, which is static-only).

The repository includes a pre-configured `render.yaml`:

1. Sign in to [Render.com](https://render.com) and click **New + > Web Service**.
2. Connect your GitHub repository: `https://github.com/ayushsrivastav9598-glitch/sccs.git`.
3. Set the following build and start settings:
   * **Runtime:** Python 3
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Click **Deploy Web Service**. Your application will be live at `https://<your-service-name>.onrender.com`.

---

## 📂 Project Structure

```text
sccs/
├── app/
│   ├── __init__.py
│   ├── config.py              # Environment configuration & DB path fallback
│   ├── database.py            # SQLite connection, migrations, WAL mode
│   ├── models.py              # Pydantic schemas (Request/Response models)
│   ├── auth.py                # PBKDF2 hashing, bearer tokens, RBAC dependencies
│   ├── engine.py              # Conflict engine, heuristic fit scoring, audit logger, NLP parser
│   ├── seed_data.py           # Pre-seeded IET & Deeksha Bhawan campus dataset
│   └── routes/
│       ├── auth_routes.py     # Login, register, profile, user listing
│       ├── room_routes.py     # Room queries, live 2D blueprints, availability search
│       ├── booking_routes.py  # Conflict-proof atomic reservations & cancellations
│       ├── schedule_routes.py # Branch timetable queries & dynamic CSV download
│       ├── notice_routes.py   # Exam notices & announcements
│       ├── report_routes.py   # Student grievances & staff resolution
│       ├── audit_routes.py    # Immutable audit ledger
│       └── ai_routes.py       # Heuristic natural language campus assistant
├── static/
│   ├── css/
│   │   └── style.css          # Minimalist monochrome black/white/grey responsive stylesheet
│   ├── js/
│   │   └── app.js             # Client controller for blueprints, bookings, CSV, notices, reports
│   └── index.html             # Left-sidebar web application layout with in-app Docs tab
├── tests/
│   ├── __init__.py
│   └── test_api.py            # 11 automated test suites covering all requirements
├── scripts/
│   └── demo_walkthrough.py    # Interactive 10-step simulation script
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # GitHub Actions automated test & Docker build workflow
├── Dockerfile                 # Multi-stage container definition with non-root security user
├── docker-compose.yml         # Containerized local orchestration
├── render.yaml                # Native Render.com cloud deployment configuration
├── vercel.json                # Vercel serverless configuration
├── requirements.txt           # Python dependencies
├── DOCS.md                    # Exhaustive architectural documentation & mathematical models
└── README.md                  # Project overview, quickstart & operational manual
```

---

## 📄 License & Institutional Credits

Developed for the **Build With AI: DevOps Problem Statement**  
**Institution:** Institute of Engineering and Technology (IET) & Deeksha Bhawan  
**University:** Deen Dayal Upadhyaya Gorakhpur University (DDUGU), Gorakhpur, UP, India.
