from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime
from app.database.models import Call, Message, Appointment
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


async def create_call(db: AsyncSession, vapi_call_id: str,
                      caller_number: str, called_number: str) -> Call:
    call = Call(
        vapi_call_id=vapi_call_id,
        caller_number=caller_number,
        called_number=called_number,
        status="in_progress"
    )
    db.add(call)
    await db.flush()
    logger.info(f"Call created: {vapi_call_id}")
    return call


async def complete_call(db: AsyncSession, vapi_call_id: str,
                        duration: int = None, transcript: str = None):
    await db.execute(
        update(Call)
        .where(Call.vapi_call_id == vapi_call_id)
        .values(
            status="completed",
            ended_at=datetime.utcnow(),
            duration_seconds=duration,
            transcript=transcript
        )
    )
    logger.info(f"Call completed: {vapi_call_id}")


async def save_message(db: AsyncSession, vapi_call_id: str,
                       caller_number: str, caller_name: str,
                       message_content: str, is_urgent: bool = False,
                       callback_time: str = None) -> Message:
    message = Message(
        vapi_call_id=vapi_call_id,
        caller_number=caller_number,
        caller_name=caller_name,
        message_content=message_content,
        is_urgent=is_urgent,
        callback_time=callback_time
    )
    db.add(message)
    await db.flush()
    logger.info(f"Message saved for call: {vapi_call_id}")
    return message


async def get_all_messages(db: AsyncSession) -> list[Message]:
    result = await db.execute(
        select(Message).order_by(Message.created_at.desc())
    )
    return list(result.scalars().all())


async def get_all_calls(db: AsyncSession) -> list[Call]:
    result = await db.execute(
        select(Call).order_by(Call.started_at.desc())
    )
    return list(result.scalars().all())


async def mark_message_read(db: AsyncSession, message_id: str):
    await db.execute(
        update(Message)
        .where(Message.id == message_id)
        .values(is_read=True)
    )