from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from ..database import get_db
from ..models import AuditLogOut
from ..auth import require_faculty_or_admin

router = APIRouter(prefix="/audit", tags=["Accountability & Audit Trail"])

@router.get("", response_model=List[AuditLogOut])
def get_audit_trail(
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(require_faculty_or_admin)
):
    """
    Challenge 7: Accountability & History.
    Full chronological audit logs of all bookings, cancellations, rescheduling,
    and official notices to help resolve disputes and misunderstandings.
    """
    conn = get_db()
    query = "SELECT * FROM audit_logs WHERE 1=1"
    params = []

    if entity_type:
        query += " AND entity_type = ?"
        params.append(entity_type.upper())
    if action:
        query += " AND action = ?"
        params.append(action.upper())

    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    logs = conn.execute(query, params).fetchall()
    conn.close()

    return [AuditLogOut(**dict(l)) for l in logs]

