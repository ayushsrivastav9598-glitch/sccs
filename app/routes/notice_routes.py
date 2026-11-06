from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from ..database import get_db
from ..models import NoticeCreate, NoticeOut
from ..auth import require_faculty_or_admin, require_admin
from ..engine import log_audit

router = APIRouter(prefix="/notices", tags=["Academic Notices & Schedule Updates"])

@router.get("", response_model=List[NoticeOut])
def list_notices(
    branch: Optional[str] = None,
    year: Optional[int] = None,
    priority: Optional[str] = None,
    notice_type: Optional[str] = None
):
    conn = get_db()
    query = "SELECT * FROM notices WHERE 1=1"
    params = []

    if branch and branch != "ALL":
        query += " AND (target_branch = ? OR target_branch = 'ALL')"
        params.append(branch)
    if year and year != 0:
        query += " AND (target_year = ? OR target_year = 0)"
        params.append(year)
    if priority:
        query += " AND priority = ?"
        params.append(priority)
    if notice_type:
        query += " AND notice_type = ?"
        params.append(notice_type)

    query += " ORDER BY CASE priority WHEN 'URGENT' THEN 1 WHEN 'HIGH' THEN 2 ELSE 3 END, created_at DESC"
    notices = conn.execute(query, params).fetchall()
    conn.close()

    return [NoticeOut(**dict(n)) for n in notices]

@router.post("", response_model=NoticeOut, status_code=status.HTTP_201_CREATED)
def publish_notice(
    notice: NoticeCreate,
    current_user: dict = Depends(require_faculty_or_admin)
):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO notices (
            title, content, notice_type, target_branch, target_year, target_section,
            room_id, booking_id, priority, published_by_user_id, published_by_name,
            published_by_email, is_test_data
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (
        notice.title, notice.content, notice.notice_type, notice.target_branch or "ALL",
        notice.target_year or 0, notice.target_section or "ALL", notice.room_id,
        notice.booking_id, notice.priority or "NORMAL", current_user["id"],
        current_user["name"], current_user["email"]
    ))
    notice_id = cursor.lastrowid
    conn.commit()

    created_notice = conn.execute("SELECT * FROM notices WHERE id = ?", (notice_id,)).fetchone()
    conn.close()

    log_audit(
        action="NOTICE_PUBLISHED",
        entity_type="NOTICE",
        entity_id=str(notice_id),
        details=f"Published {notice.priority} notice: '{notice.title}' for {notice.target_branch} Year {notice.target_year}",
        user=current_user
    )

    return NoticeOut(**dict(created_notice))

@router.delete("/{notice_id}")
def delete_notice(
    notice_id: int,
    current_user: dict = Depends(require_admin)
):
    conn = get_db()
    notice = conn.execute("SELECT * FROM notices WHERE id = ?", (notice_id,)).fetchone()
    if not notice:
        conn.close()
        raise HTTPException(status_code=404, detail="Notice not found")

    conn.execute("DELETE FROM notices WHERE id = ?", (notice_id,))
    conn.commit()
    conn.close()

    log_audit(
        action="NOTICE_DELETED",
        entity_type="NOTICE",
        entity_id=str(notice_id),
        details=f"Deleted notice '{notice['title']}'",
        user=current_user
    )

    return {"message": "Notice deleted successfully"}

