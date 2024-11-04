import pytest

from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from hotel_app.database import get_db, Base
from fastapi.testclient import TestClient
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from redis import asyncio as aioredis
from httpx import AsyncClient
import asyncio
import asyncpg
from sqlalchemy import text
from hotel_app.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from hotel_app.schemas import BookingCreate, UserCreate, CategoryCreate, ServiceCreate
from hotel_app.services.crud import create_service
from hotel_app.users.crud import create_user, get_user_by_id, get_user_by_email
from hotel_app.admin.crud import create_admin_user
from hotel_app.security import create_access_token
from hotel_app.categories.crud import create_category
from hotel_app.bookings.crud import create_booking
from hotel_app.redis_cache import lifespan
from unittest import mock


def mock_cache(*args, **kwargs):
    def wrapper(func):
        async def inner(*args, **kwargs):
            return await func(*args, **kwargs)
        return inner
    return wrapper


mock.patch("fastapi_cache.decorator.cache", mock_cache).start()


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


async def override_get_async_session():
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:123@localhost/test_hotel_db",
        future=True
    )

    TestSessionLocal = sessionmaker(
        bind=engine, expire_on_commit=True, class_=AsyncSession)
    Base.metadata.bind = engine
    async with TestSessionLocal() as session:
        yield session


def get_sessionmaker():
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:123@localhost/test_hotel_db",
        future=True
    )

    TestSessionLocal = sessionmaker(
        bind=engine, expire_on_commit=True, class_=AsyncSession)
    return TestSessionLocal


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:123@localhost/test_hotel_db",
        future=True
    )
    Base.metadata.bind = engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True, scope="function")
def fastapi_cache():
    from redis import asyncio as aioredis
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


@pytest.fixture(scope="session")
async def client():
    from hotel_app.main import app
    app.dependency_overrides[get_db] = override_get_async_session
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
async def create_new_role_user(prepare_database):
    async_session = get_sessionmaker()
    async with async_session() as session:
        async with session.begin():
            await session.execute(
                text("""INSERT INTO roles values (1, 'ROLE_USER')
                                on conflict do nothing;""")
            )
            await session.commit()


@pytest.fixture(scope="session", autouse=True)
async def create_new_role_admin(prepare_database):
    TestSessionLocal = get_sessionmaker()
    async with TestSessionLocal() as session:
        async with session.begin():
            await session.execute(
                text("""INSERT INTO roles values (2, 'ROLE_ADMIN')
                             ON CONFLICT DO NOTHING;""")
            )
            await session.commit()


@pytest.fixture
async def create_new_category_id_100(create_new_role_admin):
    TestSessionLocal = get_sessionmaker()
    async with TestSessionLocal() as session:
        async with session.begin():
            await session.execute(
                text(
                    "INSERT INTO categories VALUES(100, 'eco', 2000, 2, 2, True, True) ON CONFLICT DO NOTHING")
            )
            await session.commit()
            return 100


@pytest.fixture
async def create_new_category_id_101(create_new_role_admin):
    TestSessionLocal = get_sessionmaker()
    async with TestSessionLocal() as session:
        async with session.begin():
            await session.execute(
                text(
                    "INSERT INTO categories VALUES(101, 'test', 2000, 2, 2, True, True) ON CONFLICT DO NOTHING")
            )
            await session.commit()
            return 101


@pytest.fixture
async def create_new_category_id_102(create_new_role_admin):
    TestSessionLocal = get_sessionmaker()
    async with TestSessionLocal() as session:
        async with session.begin():
            await session.execute(
                text(
                    "INSERT INTO categories VALUES(102, 'test2', 2000, 2, 2, True, True) ON CONFLICT DO NOTHING")
            )
            await session.commit()
            return 101


async def create_new_user():
    session = await get_sessionmaker()
    new_user = {"email": "1@m.ru",
                "password_hash": "12345",
                "is_active": True}
    new_user = UserCreate(
        **new_user
    )
    try:
        user = await create_user(session, new_user)
        return user
    except Exception as e:
        return await get_user_by_email(session, user.email)


@pytest.fixture
async def create_new_admin_id_100(create_new_role_admin):
    TestSessionLocal = get_sessionmaker()
    async with TestSessionLocal() as session:
        await session.execute(
            text(
                """INSERT INTO users VALUES(100, 'admin@example.com', 'secret', True) ON CONFLICT DO NOTHING RETURNING email
                      """
            ))
        await session.execute(
            text("INSERT INTO user_role values(100, 2) ON CONFLICT DO NOTHING")
        )
        await session.commit()
        return (
            await session.execute(
                text("select email from users where id = 100")
            )
        ).scalar_one_or_none()


@pytest.fixture
async def create_new_user_id_101(create_new_role_user):
    TestSessionLocal = get_sessionmaker()
    async with TestSessionLocal() as session:
        await session.execute(
            text(
                """INSERT INTO users VALUES(101, '1@example.com', 'secret', True) ON CONFLICT DO NOTHING RETURNING email
                      """
            ))
        await session.execute(
            text("INSERT INTO user_role values(101, 1) ON CONFLICT DO NOTHING")
        )
        await session.commit()
        return (
            await session.execute(
                text("select email from users where id = 101")
            )
        ).scalar_one_or_none()


@pytest.fixture
async def create_new_user_id_102(create_new_role_user):
    TestSessionLocal = get_sessionmaker()
    async with TestSessionLocal() as session:
        await session.execute(
            text(
                """INSERT INTO users VALUES(102, '2@example.com', 'secret', True) ON CONFLICT DO NOTHING RETURNING email
                      """
            ))
        await session.execute(
            text("INSERT INTO user_role values(102, 1) ON CONFLICT DO NOTHING")
        )
        await session.commit()
        return (
            await session.execute(
                text("select email from users where id = 102")
            )
        ).scalar_one_or_none()


@pytest.fixture
async def create_new_payment_id_100(create_new_role_admin):
    TestSessionLocal = get_sessionmaker()
    async with TestSessionLocal() as session:
        async with session.begin():
            await session.execute(
                text(
                    "INSERT INTO payments VALUES(100, 6000, '2024-08-10') ON CONFLICT DO NOTHING")
            )
            await session.commit()
            return 100


async def get_some_admin():
    some_admin = {
        "email": "adm@mail.ru",
        "password_hash": "123456",
        "is_active": True
    }
    new_admin = UserCreate(
        **some_admin
    )
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:123@localhost/test_hotel_db",
        echo=True,
        future=True
    )

    TestSessionLocal = sessionmaker(
        bind=engine, expire_on_commit=True, class_=AsyncSession)
    Base.metadata.bind = engine
    async with TestSessionLocal() as session:
        try:
            admin = await create_admin_user(session, new_admin)
            return admin
        except Exception as e:
            return new_admin


def create_test_auth_headers_for_user(email: str) -> dict[str, str]:
    access_token = create_access_token(
        data={"sub": email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def create_new_room_id_100(create_new_category_id_101):
    TestSessionLocal = get_sessionmaker()
    async with TestSessionLocal() as session:
        async with session.begin():
            await session.execute(
                text("""INSERT INTO rooms values (100, 101, True)
                             ON CONFLICT DO NOTHING""")
            )
            await session.commit()


@pytest.fixture
async def create_new_room_id_101(create_new_category_id_101):
    TestSessionLocal = get_sessionmaker()
    async with TestSessionLocal() as session:
        async with session.begin():
            await session.execute(
                text("""INSERT INTO rooms values (101, 101, True)
                             ON CONFLICT DO NOTHING""")
            )
            await session.commit()


@pytest.fixture
async def create_new_room_id_102(create_new_category_id_101):
    TestSessionLocal = get_sessionmaker()
    async with TestSessionLocal() as session:
        async with session.begin():
            await session.execute(
                text("""INSERT INTO rooms values (102, 101, True)
                             ON CONFLICT DO NOTHING""")
            )
            await session.commit()


@pytest.fixture
async def create_new_room_id_103(create_new_category_id_101):
    TestSessionLocal = get_sessionmaker()
    async with TestSessionLocal() as session:
        async with session.begin():
            await session.execute(
                text("""INSERT INTO rooms values (103, 101, False)
                             ON CONFLICT DO NOTHING""")
            )
            await session.commit()


@pytest.fixture
async def create_new_room_id_104(create_new_category_id_101):
    TestSessionLocal = get_sessionmaker()
    async with TestSessionLocal() as session:
        async with session.begin():
            await session.execute(
                text("""INSERT INTO rooms values (104, 101, True)
                             ON CONFLICT DO NOTHING""")
            )
            await session.commit()


@pytest.fixture
async def create_service_id_100():
    TestSessionLocal = get_sessionmaker()
    async with TestSessionLocal() as session:
        async with session.begin():
            await session.execute(
                text("""INSERT INTO services values (100, 'Test1', 0, True)
                             ON CONFLICT DO NOTHING""")
            )
            await session.commit()


@pytest.fixture
async def create_service_id_101():
    TestSessionLocal = get_sessionmaker()
    async with TestSessionLocal() as session:
        async with session.begin():
            await session.execute(
                text("""INSERT INTO services values (101, 'Test5', 0, True)
                             ON CONFLICT DO NOTHING""")
            )
            await session.commit()


@pytest.fixture
async def create_service_id_102():
    TestSessionLocal = get_sessionmaker()
    async with TestSessionLocal() as session:
        async with session.begin():
            await session.execute(
                text("""INSERT INTO services values (102, 'Test6', 0, False)
                             ON CONFLICT DO NOTHING""")
            )
            await session.commit()


# @pytest.fixture
# async def create_new_serivce():
#     service = {
#         "service_name": "hotel_room",
#     }
# #     session = await get_session()
# #     engine = create_async_engine(
# #     "postgresql+asyncpg://postgres:123@localhost/test_hotel_db",
# #     echo=True,
# #     future = True
# # )

# #     TestSessionLocal = sessionmaker(bind=engine, expire_on_commit=True, class_= AsyncSession)
# #     Base.metadata.bind = engine
#     session = await get_sessionmaker()
#     async with session.begin():
#         try:
#             await create_service(session, ServiceCreate(**service))
#         except Exception as e:
#             pass


# @pytest.fixture
# async def create_new_serivce_2():

#     service = {
#         "service_name": "help_with_1",
#     }
#     session = await get_sessionmaker()
#     async with session.begin():
#         try:
#             await create_service(session, ServiceCreate(**service))
#         except Exception as e:
#             pass


# @pytest.fixture
# async def create_new_room_id_5(create_new_category):
#     session = await get_sessionmaker()
#     if 1:
#         async with session.begin():
#             await session.execute(
#                 text("""INSERT INTO rooms values (7, 1, True)
#                              ON CONFLICT DO NOTHING""")
#             )
#             await session.commit()


# @pytest.fixture()
# async def create_new_category_2():
#     category = {
#         "category_name": "econom+",
#         "price": 2000,
#         "beds": 2
#     }
#     session = await get_sessionmaker()
#     if 1:
#         try:
#             await create_category(session,
#                                   CategoryCreate(**category))
#         except Exception as e:
#             pass


# async def create_some_booking():
#     #   pass
#     booking = {
#         "booking_data": {
#             "join_date": "2024-07-27T18:41:23.244000Z",
#             "out_date": "2024-08-27T18:41:23.244000Z",
#             "room_num": 2
#         },
#         "services_ids": [],
#         "clients": [
#             {
#                 "first_name": "Name",
#                 "last_name": "Lastname",
#                 "phone_number": "8-000-000-00-00"
#             }
#         ]
#     }
#     new_booking = BookingCreate(**booking)
#     admin = await get_some_admin()
#     session = await get_sessionmaker()

#     return await create_booking(session, new_booking, 1)
