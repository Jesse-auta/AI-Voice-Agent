from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import get_settings
from app.database.connection import init_db
from app.routes import vapi_webhooks, admin
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    logger.info(f"Starting Voice Agent | Environment: {settings.environment}")
    await init_db()
    logger.info("Database ready. Server is live.")
    yield
    # SHUTDOWN
    logger.info("Shutting down Voice Agent")


app = FastAPI(
    title="AI Voice Receptionist",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.environment == "development" else None,
)

# Register routes
app.include_router(vapi_webhooks.router)
app.include_router(admin.router)


@app.get("/health")
async def health():
    return {"status": "healthy", "environment": settings.environment}