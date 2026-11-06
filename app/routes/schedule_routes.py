from typing import List, Optional
import datetime
from fastapi import APIRouter, Query
from ..database import get_db
from ..models import BookingOut

router = APIRouter(prefix="/schedules", tags=["Academic Schedules & Student Access"])

@router.get("/timetable", response_model=List[BookingOut])
def get_academic_timetable(
    branch: Optional[str] = Query("CSE", description="CSE, AI ML, AI DS, ECE, ME, IT, or ALL"),
    year: Optional[int] = Query(3, description="Academic year: 1, 2, 3, 4, or 0 for all"),
    section: Optional[str] = Query("A", description="Section: A, B, or ALL"),
    date: Optional[str] = None
):
    """
    Core Challenge 5: Student Access.
    Allows students to look up official schedules for their branch, year, and section.
    """
    conn = get_db()
    query = """
        SELECT b.*, r.code as room_code, r.name as room_name, r.building_id, r.floor
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        WHERE b.status = 'CONFIRMED'
    """
    params = []

    if branch and branch != "ALL":
        query += " AND (b.branch = ? OR b.branch = 'ALL')"
        params.append(branch)
    if year and year != 0:
        query += " AND (b.year = ? OR b.year = 0)"
        params.append(year)
    if section and section != "ALL":
        query += " AND (b.section = ? OR b.section = 'ALL')"
        params.append(section)
    if date:
        query += " AND b.date = ?"
        params.append(date)

    query += " ORDER BY b.date ASC, b.start_time ASC"
    rows = conn.execute(query, params).fetchall()
    conn.close()

    return [BookingOut(**dict(r)) for r in rows]

@router.get("/export")
def export_academic_timetable(
    branch: Optional[str] = "ALL",
    year: Optional[int] = 0,
    section: Optional[str] = "ALL",
    export_format: str = Query("csv", pattern="^(csv|json)$")
):
    """Exports academic timetable and examination schedule in CSV or JSON format."""
    conn = get_db()
    query = """
        SELECT b.date, b.start_time, b.end_time, b.room_id, r.code as room_code,
               r.name as room_name, r.building_id, r.floor, b.title, b.purpose,
               b.branch, b.year, b.section, b.expected_students, b.booked_by_name
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        WHERE b.status = 'CONFIRMED'
    """
    params = []
    if branch and branch != "ALL":
        query += " AND (b.branch = ? OR b.branch = 'ALL')"
        params.append(branch)
    if year and year != 0:
        query += " AND (b.year = ? OR b.year = 0)"
        params.append(year)
    if section and section != "ALL":
        query += " AND (b.section = ? OR b.section = 'ALL')"
        params.append(section)

    query += " ORDER BY b.date ASC, b.start_time ASC"
    rows = conn.execute(query, params).fetchall()
    conn.close()

    data = [dict(r) for r in rows]

    if export_format == "json":
        return data

    import io
    import csv
    from fastapi.responses import Response

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Date", "Start Time", "End Time", "Room Code", "Room Name",
        "Building", "Floor", "Title", "Purpose", "Branch", "Year",
        "Section", "Expected Students", "Faculty In-Charge"
    ])

    for item in data:
        writer.writerow([
            item["date"], item["start_time"], item["end_time"], item["room_code"],
            item["room_name"], item["building_id"], item["floor"], item["title"],
            item["purpose"], item["branch"], item["year"], item["section"],
            item["expected_students"], item["booked_by_name"]
        ])

    csv_data = output.getvalue()
    filename = f"schedule_{branch}_Year{year}.csv"
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/branches")
def get_branch_metadata():
    """Returns official branch, year, and section breakdowns from the DDUGU IET dataset."""
    return {
        "institution": "Institute of Engineering and Technology (IET) & Deeksha Bhawan",
        "university": "Deen Dayal Upadhyaya Gorakhpur University (DDUGU)",
        "branches": [
            {"code": "CSE", "name": "Computer Science & Engineering", "approx_students_per_year": 150, "sections": ["A", "B"]},
            {"code": "AI ML", "name": "Artificial Intelligence & Machine Learning", "approx_students_per_year": 150, "sections": ["A", "B"]},
            {"code": "AI DS", "name": "Artificial Intelligence & Data Science", "approx_students_per_year": 75, "sections": ["A"]},
            {"code": "ECE", "name": "Electronics & Communication Engineering", "approx_students_per_year": 75, "sections": ["A"]},
            {"code": "ME", "name": "Mechanical Engineering", "approx_students_per_year": 75, "sections": ["A"]},
            {"code": "IT", "name": "Information Technology", "approx_students_per_year": 75, "sections": ["A"]}
        ],
        "years": [1, 2, 3, 4]
    }

