from typing import List, Optional
import datetime
from fastapi import APIRouter, HTTPException, Query
from ..database import get_db
from ..models import RoomOut, BuildingOut, AvailabilitySearchRequest, RoomAvailabilityItem
from ..engine import calculate_end_time, is_time_overlapping

router = APIRouter(prefix="/rooms", tags=["Rooms & Blueprints"])

@router.get("", response_model=List[RoomOut])
def list_rooms(
    building_id: Optional[str] = None,
    floor: Optional[str] = None,
    room_type: Optional[str] = None,
    min_capacity: Optional[int] = None
):
    conn = get_db()
    query = "SELECT * FROM rooms WHERE is_active = 1"
    params = []

    if building_id:
        query += " AND building_id = ?"
        params.append(building_id.upper())
    if floor:
        query += " AND floor = ?"
        params.append(floor)
    if room_type:
        query += " AND room_type = ?"
        params.append(room_type)
    if min_capacity:
        query += " AND capacity >= ?"
        params.append(min_capacity)

    query += " ORDER BY building_id ASC, floor ASC, code ASC"
    rooms = conn.execute(query, params).fetchall()
    conn.close()
    return [RoomOut(**dict(r)) for r in rooms]

@router.get("/blueprints")
def get_blueprints(date: Optional[str] = None, time_slot: Optional[str] = None):
    """
    Returns full campus blueprint representation for BOTH IET and Deeksha Bhawan
    with live room occupancy states for interactive 2D map rendering.
    """
    if not date:
        date = datetime.date.today().strftime("%Y-%m-%d")
    if not time_slot:
        time_slot = "10:00"

    end_slot = calculate_end_time(time_slot, 60)

    conn = get_db()
    buildings = conn.execute("SELECT * FROM buildings ORDER BY distance_from_iet_meters ASC").fetchall()
    rooms = conn.execute("SELECT * FROM rooms WHERE is_active = 1").fetchall()

    # Get active bookings for the specified date and time window
    bookings = conn.execute("""
        SELECT b.*, r.code as room_code
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        WHERE b.date = ? AND b.status = 'CONFIRMED'
    """, (date,)).fetchall()
    conn.close()

    occupied_map = {}
    for b in bookings:
        if is_time_overlapping(time_slot, end_slot, b["start_time"], b["end_time"]):
            occupied_map[b["room_id"]] = {
                "booking_id": b["id"],
                "title": b["title"],
                "booked_by": b["booked_by_name"],
                "branch": b["branch"],
                "purpose": b["purpose"],
                "time": f"{b['start_time']} - {b['end_time']}",
                "is_test_data": bool(b["is_test_data"])
            }

    blueprint_data = {
        "date": date,
        "time_slot": time_slot,
        "buildings": []
    }

    for b in buildings:
        b_dict = dict(b)
        b_rooms = [r for r in rooms if r["building_id"] == b["id"]]

        floors = {}
        for r in b_rooms:
            r_dict = dict(r)
            r_id = r["id"]
            if r_id in occupied_map:
                r_dict["is_occupied"] = True
                r_dict["current_booking"] = occupied_map[r_id]
            else:
                r_dict["is_occupied"] = False
                r_dict["current_booking"] = None

            fl = r["floor"]
            if fl not in floors:
                floors[fl] = []
            floors[fl].append(r_dict)

        b_dict["floors"] = floors
        blueprint_data["buildings"].append(b_dict)

    return blueprint_data

@router.get("/{room_id}")
def get_room_details(room_id: str, date: Optional[str] = None):
    conn = get_db()
    room = conn.execute("SELECT * FROM rooms WHERE id = ?", (room_id,)).fetchone()
    if not room:
        conn.close()
        raise HTTPException(status_code=404, detail="Room not found")

    if not date:
        date = datetime.date.today().strftime("%Y-%m-%d")

    bookings = conn.execute("""
        SELECT * FROM bookings
        WHERE room_id = ? AND date = ? AND status = 'CONFIRMED'
        ORDER BY start_time ASC
    """, (room_id, date)).fetchall()
    conn.close()

    room_data = dict(room)
    room_data["schedule"] = [dict(b) for b in bookings]
    return room_data

@router.post("/availability")
def search_room_availability(req: AvailabilitySearchRequest):
    """
    Search room availability across buildings, floors, capacities and time slots.
    """
    start_time = req.start_time
    duration = req.duration_minutes or 60
    end_time = req.end_time or calculate_end_time(start_time, duration)

    conn = get_db()
    query = "SELECT * FROM rooms WHERE is_active = 1"
    params = []

    if req.building_id:
        query += " AND building_id = ?"
        params.append(req.building_id)
    if req.floor:
        query += " AND floor = ?"
        params.append(req.floor)
    if req.room_type:
        query += " AND room_type = ?"
        params.append(req.room_type)
    if req.required_capacity:
        query += " AND capacity >= ?"
        params.append(req.required_capacity)

    rooms = conn.execute(query, params).fetchall()

    # Fetch active bookings for that date
    bookings = conn.execute("""
        SELECT * FROM bookings
        WHERE date = ? AND status = 'CONFIRMED'
    """, (req.date,)).fetchall()
    conn.close()

    occupied_rooms = {}
    for b in bookings:
        if is_time_overlapping(start_time, end_time, b["start_time"], b["end_time"]):
            occupied_rooms[b["room_id"]] = b

    results = []
    for r in rooms:
        r_id = r["id"]
        is_free = r_id not in occupied_rooms
        conflict_msg = None
        occupant_info = None

        if not is_free:
            b_info = occupied_rooms[r_id]
            conflict_msg = f"Occupied for '{b_info['title']}' ({b_info['start_time']} - {b_info['end_time']})"
            occupant_info = f"{b_info['booked_by_name']} ({b_info['branch']})"

        results.append({
            "room": RoomOut(**dict(r)),
            "is_available": is_free,
            "conflict_reason": conflict_msg,
            "current_occupant": occupant_info
        })

    # Sort available first, then by capacity
    results.sort(key=lambda x: (not x["is_available"], x["room"].capacity))
    return {
        "date": req.date,
        "time_slot": f"{start_time} - {end_time}",
        "total_rooms_checked": len(rooms),
        "available_rooms_count": sum(1 for item in results if item["is_available"]),
        "results": results
    }

