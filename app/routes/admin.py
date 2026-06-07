"""
Admin endpoints — for the business owner to view messages and calls.
No auth for now (we add it in production).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.database import crud
from app.utils.logger import setup_logger

router = APIRouter(prefix="/admin", tags=["admin"])
logger = setup_logger(__name__)


@router.get("/messages")
async def get_messages(db: AsyncSession = Depends(get_db)):
    """Get all messages left by callers."""
    messages = await crud.get_all_messages(db)
    return [   
        {
            "id": str(m.id),
            "caller_name": m.caller_name,
            "caller_number": m.caller_number,
            "message": m.message_content,
            "is_urgent": m.is_urgent,
            "callback_time": m.callback_time,
            "is_read": m.is_read,
            "created_at": str(m.created_at),
            "call_id": m.vapi_call_id
        }
        for m in messages
    ]


@router.get("/calls")
async def get_calls(db: AsyncSession = Depends(get_db)):
    """Get all call records."""
    calls = await crud.get_all_calls(db)
    return [
        {
            "id": str(c.id),
            "vapi_call_id": c.vapi_call_id,
            "caller_number": c.caller_number,
            "called_number": c.called_number,
            "status": c.status,
            "duration_seconds": c.duration_seconds,
            "started_at": str(c.started_at),
            "ended_at": str(c.ended_at),
        }
        for c in calls
    ]


@router.get("/calls/{vapi_call_id}/transcript")
async def get_transcript(vapi_call_id: str,
                          db: AsyncSession = Depends(get_db)):
    """Get full transcript for a specific call."""
    calls = await crud.get_all_calls(db)
    call = next((c for c in calls if c.vapi_call_id == vapi_call_id), None)
    if not call:
        return {"error": "Call not found"}
    return {
        "vapi_call_id": vapi_call_id,
        "transcript": call.transcript,
        "duration_seconds": call.duration_seconds
    }