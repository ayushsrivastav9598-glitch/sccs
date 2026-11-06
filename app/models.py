from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

# ==================== User Models ====================
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field(default="student", description="'student', 'faculty', or 'admin'")
    branch: Optional[str] = "CSE"  # CSE, AI ML, AI DS, ECE, ME, IT
    year: Optional[int] = 1        # 1, 2, 3, 4
    section: Optional[str] = "A"   # A, B
    department: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    branch: Optional[str] = None
    year: Optional[int] = None
    section: Optional[str] = None
    department: Optional[str] = None
    created_at: Optional[str] = None

class AuthResponse(BaseModel):
    message: str
    token: str
    user: UserOut

# ==================== Room Models ====================
class RoomBase(BaseModel):
    id: str
    code: str
    name: str
    building_id: str
    floor: str
    room_type: str
    capacity: int
    facilities: Optional[str] = ""
    permitted_uses: Optional[str] = ""
    is_active: int = 1
    x_coord: int = 0
    y_coord: int = 0
    width: int = 100
    height: int = 60

class RoomOut(RoomBase):
    pass

class BuildingOut(BaseModel):
    id: str
    name: str
    code: str
    description: Optional[str] = ""
    distance_from_iet_meters: int = 0
    rooms: List[RoomOut] = []

# ==================== Availability Models ====================
class AvailabilitySearchRequest(BaseModel):
    date: str                          # YYYY-MM-DD
    start_time: str                    # HH:MM
    end_time: Optional[str] = None      # HH:MM
    duration_minutes: Optional[int] = 60
    building_id: Optional[str] = None  # 'IET' or 'DEEKSHA_BHAWAN'
    floor: Optional[str] = None
    room_type: Optional[str] = None
    required_capacity: Optional[int] = None
    purpose: Optional[str] = None

class AlternativeRoom(BaseModel):
    room_id: str
    code: str
    name: str
    building_id: str
    floor: str
    capacity: int
    room_type: str
    distance_from_iet_meters: int
    fit_score: float
    reason: str

class RoomAvailabilityItem(BaseModel):
    room: RoomOut
    is_available: bool
    conflict_reason: Optional[str] = None
    current_occupant: Optional[str] = None

# ==================== Booking Models ====================
class BookingCreate(BaseModel):
    room_id: str
    title: str = Field(..., min_length=3)
    purpose: str = Field(default="Extra Lecture", description="Minor Examination, Extra Lecture, Practical Session, Seminar, Event")
    date: str
    start_time: str
    end_time: Optional[str] = None
    duration_minutes: Optional[int] = 60
    branch: Optional[str] = "ALL"
    year: Optional[int] = 0
    section: Optional[str] = "ALL"
    expected_students: int = Field(default=75, gt=0)
    notes: Optional[str] = ""
    is_test_data: Optional[bool] = False

class BookingReschedule(BaseModel):
    new_date: str
    new_start_time: str
    new_end_time: Optional[str] = None
    duration_minutes: Optional[int] = 60
    reason: Optional[str] = "Faculty schedule modification"

class BookingOut(BaseModel):
    id: int
    room_id: str
    room_code: Optional[str] = None
    room_name: Optional[str] = None
    building_id: Optional[str] = None
    floor: Optional[str] = None
    title: str
    purpose: str
    date: str
    start_time: str
    end_time: str
    duration_minutes: int
    booked_by_user_id: int
    booked_by_name: str
    booked_by_email: str
    branch: str
    year: int
    section: str
    expected_students: int
    status: str
    is_test_data: int
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# ==================== Notice Models ====================
class NoticeCreate(BaseModel):
    title: str = Field(..., min_length=3)
    content: str = Field(..., min_length=5)
    notice_type: str = Field(default="GENERAL", description="EXAM_SCHEDULE, CANCELLATION, RESCHEDULING, GENERAL, URGENT")
    target_branch: Optional[str] = "ALL"
    target_year: Optional[int] = 0
    target_section: Optional[str] = "ALL"
    room_id: Optional[str] = None
    booking_id: Optional[int] = None
    priority: Optional[str] = "NORMAL"

class NoticeOut(BaseModel):
    id: int
    title: str
    content: str
    notice_type: str
    target_branch: str
    target_year: int
    target_section: str
    room_id: Optional[str] = None
    booking_id: Optional[int] = None
    priority: str
    published_by_user_id: Optional[int] = None
    published_by_name: Optional[str] = None
    published_by_email: Optional[str] = None
    is_test_data: int
    created_at: Optional[str] = None

# ==================== Student Report Models ====================
class StudentReportCreate(BaseModel):
    booking_id: Optional[int] = None
    room_id: Optional[str] = None
    report_type: str = Field(..., description="OVERLAPPING_SCHEDULE, OUTDATED_NOTICE, ROOM_UNAVAILABLE, EXAM_CLASH, OTHER")
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=5)

class StudentReportResolve(BaseModel):
    status: str = Field(..., description="RESOLVED, DISMISSED, UNDER_REVIEW")
    admin_notes: Optional[str] = ""

class StudentReportOut(BaseModel):
    id: int
    student_id: int
    student_name: str
    student_email: str
    booking_id: Optional[int] = None
    room_id: Optional[str] = None
    report_type: str
    title: str
    description: str
    status: str
    admin_notes: Optional[str] = None
    created_at: Optional[str] = None
    resolved_at: Optional[str] = None

# ==================== Audit Log Models ====================
class AuditLogOut(BaseModel):
    id: int
    action: str
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user_role: Optional[str] = None
    entity_type: str
    entity_id: str
    details: str
    timestamp: str

# ==================== AI Assistant Models ====================
class AIQueryRequest(BaseModel):
    query: str
    preferred_building: Optional[str] = None
    branch: Optional[str] = None
    year: Optional[int] = None

class AIQueryResponse(BaseModel):
    parsed_intent: str
    summary: str
    extracted_params: dict
    recommended_rooms: List[AlternativeRoom]
    available_time_slots: List[str]
    suggested_action: str

