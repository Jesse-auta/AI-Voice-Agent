"""
VAPI Webhook endpoint.
VAPI sends ALL events to a single webhook URL.
We inspect the event type and handle each one appropriately.

Event types we handle:
- call-started:   Log the call in DB
- call-ended:     Save transcript + mark complete
- tool-calls:     Execute tool functions (save_message etc)
- transcript:     Real-time transcript updates (we ignore for now)
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database import crud
from app.services.vapi_tools import handle_tool_call
from app.utils.logger import setup_logger

router = APIRouter(prefix="/vapi", tags=["vapi"])
logger = setup_logger(__name__)


@router.post("/webhook")
async def vapi_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Single endpoint that receives all VAPI events.
    VAPI sends JSON — we parse the message type and route accordingly.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    # VAPI wraps everything in a "message" object
    message = body.get("message", {})
    event_type = message.get("type", "")

    logger.info(f"VAPI event received: {event_type}")

    # ── call-started ────────────────────────────────────────────────────────
    if event_type == "call-started":
        call = message.get("call", {})
        vapi_call_id   = call.get("id", "unknown")
        caller_number  = call.get("customer", {}).get("number", "unknown")
        called_number  = call.get("phoneNumber", {}).get("number", "unknown")

        await crud.create_call(db, vapi_call_id, caller_number, called_number)
        logger.info(f"Call started | id={vapi_call_id} | from={caller_number}")
        return JSONResponse({"status": "ok"})

    # ── call-ended ──────────────────────────────────────────────────────────
    elif event_type == "call-ended" or event_type == "end-of-call-report":
        call      = message.get("call", {})
        vapi_call_id  = call.get("id", "unknown")
        duration      = message.get("durationSeconds", None)

        # Build full transcript from messages array
        transcript_parts = []
        for msg in message.get("transcript", "").split("\n"):
            if msg.strip():
                transcript_parts.append(msg.strip())
        transcript = "\n".join(transcript_parts) if transcript_parts else message.get("transcript", None)

        await crud.complete_call(db, vapi_call_id, duration, transcript)
        logger.info(f"Call ended | id={vapi_call_id} | duration={duration}s")
        return JSONResponse({"status": "ok"})

    # ── tool-calls ──────────────────────────────────────────────────────────
    elif event_type == "tool-calls":
        call         = message.get("call", {})
        vapi_call_id = call.get("id", "unknown")
        caller_number = call.get("customer", {}).get("number", "unknown")
        tool_calls   = message.get("toolCalls", [])

        results = []
        for tool_call in tool_calls:
            tool_id   = tool_call.get("id", "")
            tool_name = tool_call.get("function", {}).get("name", "")
            tool_args = tool_call.get("function", {}).get("arguments", {})

            # Arguments may come as a JSON string — parse if needed
            if isinstance(tool_args, str):
                import json
                try:
                    tool_args = json.loads(tool_args)
                except Exception:
                    tool_args = {}

            result = await handle_tool_call(
                db, vapi_call_id, caller_number, tool_name, tool_args
            )

            results.append({
                "toolCallId": tool_id,
                "result": result
            })

        # VAPI requires this exact response format for tool calls
        return JSONResponse({"results": results})

    # ── all other events ─────────────────────────────────────────────────────
    else:
        logger.debug(f"Unhandled event type: {event_type}")
        return JSONResponse({"status": "ok"})