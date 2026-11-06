from typing import List, Optional
import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import JSONResponse
from ..database import get_db
from ..models import BookingCreate, BookingReschedule, BookingOut, AlternativeRoom
from ..auth import get_current_user, require_faculty_or_admin
from ..engine import (
    calculate_end_time,
    check_room_conflict,
    find_smart_alternatives,
    log_audit
)

router = APIRouter(prefix="/bookings", tags=["Faculty Booking & Conflict Prevention"])

@router.post("", status_code=status.HTTP_201_CREATED)
def create_booking(
    booking: BookingCreate,
    current_user: dict = Depends(require_faculty_or_admin)
):
    """
    Core Challenge 2 & 3: Faculty Booking & Conflict Prevention.
    Validates room, checks overlapping bookings, prevents collisions,
    and returns intelligent alternative recommendations across IET & Deeksha Bhawan if blocked.
    """
    conn = get_db()
    room = conn.execute("SELECT * FROM rooms WHERE id = ?", (booking.room_id,)).fetchone()
    if not room:
        conn.close()
        raise HTTPException(status_code=404, detail="Selected room does not exist")

    start_time = booking.start_time
    duration = booking.duration_minutes or 60
    end_time = booking.end_time or calculate_end_time(start_time, duration)

    # 1. Capacity validation
    if booking.expected_students > room["capacity"]:
        conn.close()
        # Find larger alternatives
        alternatives = find_smart_alternatives(
            date=booking.date,
            start_time=start_time,
            end_time=end_time,
            required_capacity=booking.expected_students,
            purpose=booking.purpose,
            preferred_building=room["building_id"]
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "CAPACITY_EXCEEDED",
                "detail": f"Room '{room['name']}' capacity is {room['capacity']}, but expected students is {booking.expected_students}.",
                "alternative_rooms": alternatives
            }
        )

    # 2. Overlap / Conflict Check
    has_conflict, conflicting_booking = check_room_conflict(
        room_id=booking.room_id,
        date=booking.date,
        start_time=start_time,
        end_time=end_time
    )

    if has_conflict:
        conn.close()
        # Intelligent conflict recovery: Suggest suitable alternative rooms in IET or Deeksha Bhawan
        alternatives = find_smart_alternatives(
            date=booking.date,
            start_time=start_time,
            end_time=end_time,
            required_capacity=booking.expected_students,
            purpose=booking.purpose,
            preferred_building=room["building_id"],
            exclude_room_id=booking.room_id
        )

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "ROOM_CONFLICT",
                "detail": f"Conflict detected! Room '{room['name']}' is already booked from {conflicting_booking['start_time']} to {conflicting_booking['end_time']} for '{conflicting_booking['title']}' by {conflicting_booking['booked_by_name']}.",
                "conflicting_booking": conflicting_booking,
                "alternative_rooms": alternatives
            }
        )

    # 3. Create the confirmed booking
    is_test = 1 if booking.is_test_data else 0
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO bookings (
            room_id, title, purpose, date, start_time, end_time, duration_minutes,
            booked_by_user_id, booked_by_name, booked_by_email, branch, year, section,
            expected_students, status, is_test_data, notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'CONFIRMED', ?, ?)
    """, (
        booking.room_id, booking.title, booking.purpose, booking.date, start_time, end_time,
        duration, current_user["id"], current_user["name"], current_user["email"],
        booking.branch or "ALL", booking.year or 0, booking.section or "ALL",
        booking.expected_students, is_test, booking.notes or ""
    ))
    booking_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Log audit entry
    log_audit(
        action="BOOKING_CREATED",
        entity_type="BOOKING",
        entity_id=str(booking_id),
        details=f"Booked room {room['name']} ({room['code']}) on {booking.date} from {start_time} to {end_time} for '{booking.title}'",
        user=current_user
    )

    return {
        "message": "Room booked successfully!",
        "booking_id": booking_id,
        "room_name": room["name"],
        "date": booking.date,
        "time": f"{start_time} - {end_time}",
        "status": "CONFIRMED",
        "is_test_data": bool(is_test)
    }

@router.get("", response_model=List[BookingOut])
def list_bookings(
    date: Optional[str] = None,
    room_id: Optional[str] = None,
    building_id: Optional[str] = None,
    branch: Optional[str] = None,
    year: Optional[int] = None,
    status: Optional[str] = None,
    include_test_data: bool = True
):
    conn = get_db()
    query = """
        SELECT b.*, r.code as room_code, r.name as room_name, r.building_id, r.floor
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        WHERE 1=1
    """
    params = []

    if date:
        query += " AND b.date = ?"
        params.append(date)
    if room_id:
        query += " AND b.room_id = ?"
        params.append(room_id)
    if building_id:
        query += " AND r.building_id = ?"
        params.append(building_id)
    if branch and branch != "ALL":
        query += " AND (b.branch = ? OR b.branch = 'ALL')"
        params.append(branch)
    if year and year != 0:
        query += " AND (b.year = ? OR b.year = 0)"
        params.append(year)
    if status:
        query += " AND b.status = ?"
        params.append(status)
    if not include_test_data:
        query += " AND b.is_test_data = 0"

    query += " ORDER BY b.date DESC, b.start_time ASC"
    rows = conn.execute(query, params).fetchall()
    conn.close()

    return [BookingOut(**dict(r)) for r in rows]

@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: int):
    conn = get_db()
    row = conn.execute("""
        SELECT b.*, r.code as room_code, r.name as room_name, r.building_id, r.floor
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        WHERE b.id = ?
    """, (booking_id,)).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Booking not found")
    return BookingOut(**dict(row))

@router.put("/{booking_id}/reschedule")
def reschedule_booking(
    booking_id: int,
    reschedule: BookingReschedule,
    current_user: dict = Depends(require_faculty_or_admin)
):
    """
    Requirement 4 & 7: Reschedule booking with conflict prevention and audit logging.
    """
    conn = get_db()
    booking = conn.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
    if not booking:
        conn.close()
        raise HTTPException(status_code=404, detail="Booking not found")

    # Only booking owner or admin can reschedule
    if current_user["role"] != "admin" and booking["booked_by_user_id"] != current_user["id"]:
        conn.close()
        raise HTTPException(status_code=403, detail="You can only reschedule your own bookings")

    new_start = reschedule.new_start_time
    duration = reschedule.duration_minutes or booking["duration_minutes"] or 60
    new_end = reschedule.new_end_time or calculate_end_time(new_start, duration)

    # Check for conflicts on the new time slot
    has_conflict, conflicting = check_room_conflict(
        room_id=booking["room_id"],
        date=reschedule.new_date,
        start_time=new_start,
        end_time=new_end,
        exclude_booking_id=booking_id
    )

    if has_conflict:
        conn.close()
        alternatives = find_smart_alternatives(
            date=reschedule.new_date,
            start_time=new_start,
            end_time=new_end,
            required_capacity=booking["expected_students"],
            purpose=booking["purpose"],
            exclude_room_id=booking["room_id"]
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "RESCHEDULE_CONFLICT",
                "detail": f"Cannot reschedule: Room is already booked on {reschedule.new_date} from {conflicting['start_time']} to {conflicting['end_time']}.",
                "conflicting_booking": conflicting,
                "alternative_rooms": alternatives
            }
        )

    # Update booking
    now_str = datetime.datetime.now().isoformat()
    conn.execute("""
        UPDATE bookings
        SET date = ?, start_time = ?, end_time = ?, duration_minutes = ?,
            status = 'RESCHEDULED', notes = ?, updated_at = ?
        WHERE id = ?
    """, (
        reschedule.new_date, new_start, new_end, duration,
        f"{booking['notes'] or ''} [Rescheduled: {reschedule.reason}]".strip(),
        now_str, booking_id
    ))
    conn.commit()
    conn.close()

    # Log to audit trail
    log_audit(
        action="BOOKING_RESCHEDULED",
        entity_type="BOOKING",
        entity_id=str(booking_id),
        details=f"Rescheduled '{booking['title']}' from {booking['date']} {booking['start_time']} to {reschedule.new_date} {new_start}-{new_end}. Reason: {reschedule.reason}",
        user=current_user
    )

    return {
        "message": "Booking rescheduled successfully!",
        "booking_id": booking_id,
        "new_date": reschedule.new_date,
        "new_time": f"{new_start} - {new_end}",
        "status": "RESCHEDULED"
    }

@router.delete("/{booking_id}")
def cancel_booking(
    booking_id: int,
    reason: Optional[str] = "Class cancelled by faculty",
    current_user: dict = Depends(require_faculty_or_admin)
):
    """
    Requirement 4 & 7: Cancel booking and log to audit trail.
    """
    conn = get_db()
    booking = conn.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
    if not booking:
        conn.close()
        raise HTTPException(status_code=404, detail="Booking not found")

    if current_user["role"] != "admin" and booking["booked_by_user_id"] != current_user["id"]:
        conn.close()
        raise HTTPException(status_code=403, detail="You can only cancel your own bookings")

    now_str = datetime.datetime.now().isoformat()
    conn.execute("""
        UPDATE bookings
        SET status = 'CANCELLED', notes = ?, updated_at = ?
        WHERE id = ?
    """, (f"{booking['notes'] or ''} [Cancelled: {reason}]".strip(), now_str, booking_id))
    conn.commit()
    conn.close()

    # Log to audit trail
    log_audit(
        action="BOOKING_CANCELLED",
        entity_type="BOOKING",
        entity_id=str(booking_id),
        details=f"Cancelled booking '{booking['title']}' for {booking['date']} {booking['start_time']}. Reason: {reason}",
        user=current_user
    )

    return {
        "message": "Booking cancelled successfully",
        "booking_id": booking_id,
        "status": "CANCELLED"
    }

