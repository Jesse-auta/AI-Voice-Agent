from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import get_settings
from app.database.models import Base
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def get_engine():
    settings = get_settings()
    # Force asyncpg driver explicitly
    url = settings.database_url.replace(
        "postgresql://", "postgresql+asyncpg://"
    ).replace(
        "postgresql+postgresql+asyncpg://", "postgresql+asyncpg://"
    )
    return create_async_engine(
        url,
        echo=settings.environment == "development",
        pool_pre_ping=True,
        connect_args={"ssl": "require"}
    )


engine = get_engine()

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()