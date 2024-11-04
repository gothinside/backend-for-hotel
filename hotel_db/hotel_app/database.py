
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from .settings import DB_HOST, DB_NAME, DB_PORT, DB_USER, DB_PASSWORD

engine = create_async_engine(
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    future=True,
    echo=True
)

Base = declarative_base()

SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=True,
    class_=AsyncSession)


async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
