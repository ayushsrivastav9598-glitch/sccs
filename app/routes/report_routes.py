import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from ..database import get_db
from ..models import StudentReportCreate, StudentReportResolve, StudentReportOut
from ..auth import get_current_user, require_faculty_or_admin, require_student_or_higher
from ..engine import log_audit

router = APIRouter(prefix="/reports", tags=["Student Grievance & Conflict Reporting"])

@router.post("", response_model=StudentReportOut, status_code=status.HTTP_201_CREATED)
def file_student_report(
    report: StudentReportCreate,
    current_user: dict = Depends(require_student_or_higher)
):
    """
    Challenge 5: Students submit comments or report conflicting or outdated information
    without modifying official bookings.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO student_reports (
            student_id, student_name, student_email, booking_id, room_id,
            report_type, title, description, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'OPEN')
    """, (
        current_user["id"], current_user["name"], current_user["email"],
        report.booking_id, report.room_id, report.report_type,
        report.title, report.description
    ))
    report_id = cursor.lastrowid
    conn.commit()

    created = conn.execute("SELECT * FROM student_reports WHERE id = ?", (report_id,)).fetchone()
    conn.close()

    log_audit(
        action="REPORT_FILED",
        entity_type="REPORT",
        entity_id=str(report_id),
        details=f"Student {current_user['name']} filed conflict report: '{report.title}' [{report.report_type}]",
        user=current_user
    )

    return StudentReportOut(**dict(created))

@router.get("", response_model=List[StudentReportOut])
def list_reports(
    status: Optional[str] = None,
    current_user: dict = Depends(require_student_or_higher)
):
    conn = get_db()
    query = "SELECT * FROM student_reports WHERE 1=1"
    params = []

    # If student, show their own reports; faculty and admin can see all
    if current_user["role"] == "student":
        query += " AND student_id = ?"
        params.append(current_user["id"])

    if status:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY created_at DESC"
    reports = conn.execute(query, params).fetchall()
    conn.close()

    return [StudentReportOut(**dict(r)) for r in reports]

@router.put("/{report_id}/resolve", response_model=StudentReportOut)
def resolve_report(
    report_id: int,
    resolution: StudentReportResolve,
    current_user: dict = Depends(require_faculty_or_admin)
):
    conn = get_db()
    report = conn.execute("SELECT * FROM student_reports WHERE id = ?", (report_id,)).fetchone()
    if not report:
        conn.close()
        raise HTTPException(status_code=404, detail="Report not found")

    resolved_at = datetime.datetime.now().isoformat() if resolution.status in ["RESOLVED", "DISMISSED"] else None

    conn.execute("""
        UPDATE student_reports
        SET status = ?, admin_notes = ?, resolved_at = ?
        WHERE id = ?
    """, (resolution.status, resolution.admin_notes, resolved_at, report_id))
    conn.commit()

    updated = conn.execute("SELECT * FROM student_reports WHERE id = ?", (report_id,)).fetchone()
    conn.close()

    log_audit(
        action="REPORT_RESOLVED",
        entity_type="REPORT",
        entity_id=str(report_id),
        details=f"Report '{report['title']}' updated to '{resolution.status}' by {current_user['name']}. Notes: {resolution.admin_notes}",
        user=current_user
    )

    return StudentReportOut(**dict(updated))

