"""
Tool handlers — these are the functions VAPI calls during a live call.
When Aria decides to save a message, VAPI sends a tool call request here.
We execute the action and return a result back to VAPI.
VAPI then tells the caller what happened based on our response.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import crud
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


async def handle_save_message(db: AsyncSession, vapi_call_id: str,
                               caller_number: str, args: dict) -> str:
    """
    Called when Aria has collected a message and wants to save it.
    Args come directly from the AI — it extracts them from the conversation.
    """
    try:
        caller_name    = args.get("caller_name", "Unknown")
        message        = args.get("message", "No message provided")
        is_urgent      = args.get("is_urgent", False)
        callback_time  = args.get("callback_time", None)

        await crud.save_message(
            db=db,
            vapi_call_id=vapi_call_id,
            caller_number=caller_number,
            caller_name=caller_name,
            message_content=message,
            is_urgent=is_urgent,
            callback_time=callback_time
        )

        logger.info(f"Message saved | call={vapi_call_id} | name={caller_name}")
        return f"Message from {caller_name} saved successfully."

    except Exception as e:
        logger.error(f"Failed to save message: {e}", exc_info=True)
        return "I'm sorry, I couldn't save the message. Please try again."


async def handle_tool_call(db: AsyncSession, vapi_call_id: str,
                            caller_number: str, tool_name: str,
                            tool_args: dict) -> str:
    """
    Central router — dispatches tool calls to the right handler.
    As we add more tools (book_appointment etc), we add them here.
    """
    logger.info(f"Tool call received | tool={tool_name} | call={vapi_call_id}")

    if tool_name == "save_message":
        return await handle_save_message(db, vapi_call_id, caller_number, tool_args)

    else:
        logger.warning(f"Unknown tool called: {tool_name}")
        return f"Tool {tool_name} is not yet implemented."