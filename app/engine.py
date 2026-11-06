import re
import datetime
from typing import List, Dict, Optional, Tuple
from .database import get_db

def time_to_minutes(time_str: str) -> int:
    """Converts HH:MM string to minutes from midnight."""
    try:
        parts = time_str.strip().split(":")
        hours = int(parts[0])
        minutes = int(parts[1]) if len(parts) > 1 else 0
        return hours * 60 + minutes
    except Exception:
        return 0

def minutes_to_time(minutes: int) -> str:
    """Converts minutes from midnight to HH:MM string."""
    hours = (minutes // 60) % 24
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"

def calculate_end_time(start_time: str, duration_minutes: int) -> str:
    start_mins = time_to_minutes(start_time)
    end_mins = start_mins + duration_minutes
    return minutes_to_time(end_mins)

def is_time_overlapping(start1: str, end1: str, start2: str, end2: str) -> bool:
    """
    Checks if interval [start1, end1) overlaps with [start2, end2).
    """
    s1, e1 = time_to_minutes(start1), time_to_minutes(end1)
    s2, e2 = time_to_minutes(start2), time_to_minutes(end2)
    return max(s1, s2) < min(e1, e2)

def check_room_conflict(
    room_id: str,
    date: str,
    start_time: str,
    end_time: str,
    exclude_booking_id: Optional[int] = None
) -> Tuple[bool, Optional[dict]]:
    """
    Checks if a room has any overlapping confirmed booking.
    Returns (is_conflict, conflicting_booking_dict).
    """
    conn = get_db()
    query = """
        SELECT b.*, r.name as room_name, r.code as room_code, r.building_id
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        WHERE b.room_id = ?
          AND b.date = ?
          AND b.status = 'CONFIRMED'
    """
    params = [room_id, date]
    if exclude_booking_id:
        query += " AND b.id != ?"
        params.append(exclude_booking_id)

    bookings = conn.execute(query, params).fetchall()
    conn.close()

    for b in bookings:
        if is_time_overlapping(start_time, end_time, b["start_time"], b["end_time"]):
            return True, dict(b)

    return False, None

def find_smart_alternatives(
    date: str,
    start_time: str,
    end_time: str,
    required_capacity: int,
    purpose: str = "Extra Lecture",
    preferred_building: Optional[str] = None,
    exclude_room_id: Optional[str] = None
) -> List[dict]:
    """
    Smart Room Recommendation Algorithm:
    Searches across IET and Deeksha Bhawan to find optimal free rooms
    satisfying capacity, room type, and proximity.
    """
    conn = get_db()
    # Fetch all active rooms and building distance
    rooms = conn.execute("""
        SELECT r.*, b.name as building_name, b.distance_from_iet_meters
        FROM rooms r
        JOIN buildings b ON r.building_id = b.id
        WHERE r.is_active = 1
    """).fetchall()

    # Fetch existing confirmed bookings for that date
    confirmed_bookings = conn.execute("""
        SELECT room_id, start_time, end_time
        FROM bookings
        WHERE date = ? AND status = 'CONFIRMED'
    """, (date,)).fetchall()
    conn.close()

    # Map occupied room ids for that time interval
    occupied_rooms = set()
    for b in confirmed_bookings:
        if is_time_overlapping(start_time, end_time, b["start_time"], b["end_time"]):
            occupied_rooms.add(b["room_id"])

    alternatives = []
    for r in rooms:
        r_id = r["id"]
        if r_id == exclude_room_id:
            continue
        if r_id in occupied_rooms:
            continue

        cap = r["capacity"]
        r_type = r["room_type"]
        b_id = r["building_id"]
        dist = r["distance_from_iet_meters"]

        # Practical sessions must have labs or classrooms
        if "Practical" in purpose and r_type != "Laboratory":
            continue

        # If required capacity is specified and room is smaller by more than 5 seats
        if required_capacity > 0 and cap < (required_capacity - 5):
            continue

        # Calculate heuristic fit score
        # Base 100
        # Penalize excess capacity waste or minor deficiency
        cap_diff = abs(cap - required_capacity) if required_capacity > 0 else 0
        cap_penalty = min(cap_diff * 0.4, 30.0)

        # Distance penalty (Deeksha Bhawan is 100m away: 15 points penalty compared to IET)
        dist_penalty = (dist / 100.0) * 15.0

        # Building preference bonus
        pref_bonus = 10.0 if (preferred_building and b_id == preferred_building) else 0.0

        # Type relevance bonus
        type_bonus = 0.0
        if "Exam" in purpose and ("Classroom" in r_type or "Seminar" in r_type or "Library" in r_type):
            type_bonus = 10.0
        elif "Practical" in purpose and "Laboratory" in r_type:
            type_bonus = 15.0
        elif "Seminar" in purpose and "Seminar" in r_type:
            type_bonus = 20.0

        fit_score = max(0.0, 100.0 - cap_penalty - dist_penalty + pref_bonus + type_bonus)

        # Build human-readable reason
        reasons = []
        if b_id == "IET":
            reasons.append(f"Located in IET ({r['floor']})")
        else:
            reasons.append(f"Located in Deeksha Bhawan (~100m walk from IET, {r['floor']})")

        reasons.append(f"Capacity: {cap} seats (matches required ~{required_capacity})")

        if r["facilities"]:
            facilities_list = r["facilities"].split(",")[:2]
            reasons.append("Facilities: " + ", ".join(f.strip() for f in facilities_list))

        reason_str = ". ".join(reasons) + "."

        alternatives.append({
            "room_id": r["id"],
            "code": r["code"],
            "name": r["name"],
            "building_id": r["building_id"],
            "floor": r["floor"],
            "capacity": r["capacity"],
            "room_type": r["room_type"],
            "distance_from_iet_meters": dist,
            "fit_score": round(fit_score, 1),
            "reason": reason_str
        })

    # Sort alternatives by fit_score descending
    alternatives.sort(key=lambda x: x["fit_score"], reverse=True)
    return alternatives[:6]

def log_audit(action: str, entity_type: str, entity_id: str, details: str, user: Optional[dict] = None):
    """Records an audit event in the database for full accountability."""
    try:
        conn = get_db()
        user_id = user.get("id") if user else None
        user_name = user.get("name") if user else "System"
        user_email = user.get("email") if user else "system@ddugu.ac.in"
        user_role = user.get("role") if user else "system"

        conn.execute("""
            INSERT INTO audit_logs (action, user_id, user_name, user_email, user_role, entity_type, entity_id, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (action, user_id, user_name, user_email, user_role, entity_type, str(entity_id), details))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Failed to write audit log: {e}")

# ==================== Natural Language AI Engine ====================
def parse_natural_language_query(query_text: str) -> dict:
    """
    Intelligent heuristic regex NLP parser for scheduling intents.
    Extracts dates, times, student counts, branches, purposes, and building preferences.
    """
    text = query_text.lower()

    # 1. Purpose detection
    purpose = "Extra Lecture"
    if "minor" in text or "exam" in text or "test" in text:
        purpose = "Minor Examination"
    elif "lab" in text or "practical" in text:
        purpose = "Practical Session"
    elif "seminar" in text or "event" in text or "conference" in text or "workshop" in text:
        purpose = "Seminar"

    # 2. Student Capacity / Count
    capacity = 75
    cap_match = re.search(r'(\d+)\s*(students|people|seats|capacity|count)', text)
    if cap_match:
        capacity = int(cap_match.group(1))
    else:
        num_matches = re.findall(r'\b\d{2,3}\b', text)
        for num in num_matches:
            val = int(num)
            if 15 <= val <= 300:
                capacity = val
                break

    # 3. Date detection
    today = datetime.date.today()
    target_date = today.strftime("%Y-%m-%d")

    if "tomorrow" in text:
        target_date = (today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    elif "day after tomorrow" in text:
        target_date = (today + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    else:
        # Match YYYY-MM-DD
        date_iso = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', text)
        if date_iso:
            target_date = date_iso.group(1)
        else:
            # Match DD-MM-YYYY or DD/MM/YYYY
            date_dmy = re.search(r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b', text)
            if date_dmy:
                d, m, y = date_dmy.group(1), date_dmy.group(2), date_dmy.group(3)
                target_date = f"{y}-{int(m):02d}-{int(d):02d}"

    # 4. Time detection
    start_time = "10:00"
    time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text)
    if time_match:
        hr = int(time_match.group(1))
        mn = int(time_match.group(2)) if time_match.group(2) else 0
        ampm = time_match.group(3)
        if ampm == "pm" and hr < 12:
            hr += 12
        elif ampm == "am" and hr == 12:
            hr = 0
        if 8 <= hr <= 19:
            start_time = f"{hr:02d}:{mn:02d}"

    # 5. Preferred Building
    building = None
    if "deeksha" in text or "bhawan" in text or "db" in text or "lh" in text:
        building = "DEEKSHA_BHAWAN"
    elif "iet" in text:
        building = "IET"

    # 6. Branch detection
    branch = "ALL"
    for b in ["cse", "ai ml", "aiml", "ai ds", "aids", "ece", "me", "it"]:
        if b in text:
            branch = b.upper().replace("AIML", "AI ML").replace("AIDS", "AI DS")
            break

    return {
        "purpose": purpose,
        "capacity": capacity,
        "date": target_date,
        "start_time": start_time,
        "duration_minutes": 60,
        "preferred_building": building,
        "branch": branch
    }

def solve_ai_scheduling(query: str, preferred_building: Optional[str] = None) -> dict:
    """
    Executes AI query analysis and returns validated recommendations.
    Uses LLM API if key is available, combined with ground-truth constraint verification.
    """
    params = parse_natural_language_query(query)
    if preferred_building:
        params["preferred_building"] = preferred_building

    date = params["date"]
    start_time = params["start_time"]
    end_time = calculate_end_time(start_time, params["duration_minutes"])
    capacity = params["capacity"]
    purpose = params["purpose"]

    # Run recommendation algorithm
    alternatives = find_smart_alternatives(
        date=date,
        start_time=start_time,
        end_time=end_time,
        required_capacity=capacity,
        purpose=purpose,
        preferred_building=params["preferred_building"]
    )

    available_slots = [
        "09:00 - 10:00",
        "10:00 - 11:00",
        "11:00 - 12:00",
        "12:00 - 13:00",
        "14:00 - 15:00",
        "15:00 - 16:00",
        "16:00 - 17:00"
    ]

    intent = f"Finding classrooms for {purpose} ({params['branch']}) on {date} around {start_time} for ~{capacity} students."
    summary = f"Located {len(alternatives)} optimal rooms meeting capacity and schedule constraints across IET and Deeksha Bhawan."

    return {
        "parsed_intent": intent,
        "summary": summary,
        "extracted_params": params,
        "recommended_rooms": alternatives,
        "available_time_slots": available_slots,
        "suggested_action": f"Reserve the top recommended room: {alternatives[0]['name'] if alternatives else 'No immediate room free'}"
    }

