from fastapi import APIRouter
from ..models import AIQueryRequest, AIQueryResponse
from ..engine import solve_ai_scheduling

router = APIRouter(prefix="/ai", tags=["Intelligent Assistance"])

@router.post("/assist", response_model=AIQueryResponse)
def intelligent_schedule_assistant(req: AIQueryRequest):
    """
    Challenge 8: Intelligent Assistance.
    Accepts natural language queries or parameters (e.g. 'Need a room for 75 students tomorrow at 10 AM',
    'Where to conduct Minor exam for 3rd year CSE?', 'Find a lab for 40 students').
    Uses optimization algorithms and constraint satisfaction to return the best rooms.
    """
    response_data = solve_ai_scheduling(
        query=req.query,
        preferred_building=req.preferred_building
    )
    return AIQueryResponse(**response_data)

