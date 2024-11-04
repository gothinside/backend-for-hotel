from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Client
from sqlalchemy import update
from fastapi import HTTPException, status
from ..schemas import ClientCreate
from sqlalchemy.exc import IntegrityError
from .utils import is_client_unique_by_phone_number, _get_client_by_id, get_clients_by_user_id
from .utils import get_clients_by_user_id


async def get_users_clients(db: AsyncSession, user_id):
    return [await _get_client_by_id(db, id) for id in await get_clients_by_user_id(db, user_id)]


async def get_client_by_id(db: AsyncSession, client_id: int):
    client = await _get_client_by_id(db, client_id)
    if client is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            "Client not found")
    return client


async def update_client(db: AsyncSession, patched_data: ClientCreate, client_id: int):
    updated_data = {key: value for key,
                    value in patched_data.model_dump().items() if value != None}
    if updated_data == {}:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail="You should change one field at least")

    client = await get_client_by_id(db, client_id)

    if patched_data.phone_number != client.phone_number and not await is_client_unique_by_phone_number(db, patched_data.phone_number):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "Phone number already exists")

    query = update(Client).where(Client.id == client_id).values(**updated_data)
    await db.execute(
        query
    )
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    return await _get_client_by_id(db, client_id)
