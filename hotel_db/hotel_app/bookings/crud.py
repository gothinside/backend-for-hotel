from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from ..schemas import BookingCreate,  PaymentCreate
from sqlalchemy.exc import IntegrityError
from ..rooms.utils import get_beds_by_room_num
from ..rooms.crud import get_room
from ..services.crud import get_service_by_id
from ..clients.utils import (
    create_client, create_client_user,
    _get_client_by_phone_numner)
from ..categories.crud import get_cateogry_by_id
from .utils import *
from .utils import _get_booking_by_id
from ..payments.utils import create_payment
from datetime import date


async def get_booking_by_id(db: AsyncSession, id: int):
    # Можно и одним запросом
    booking = await _get_booking_by_id(db, id)
    clients = await get_clients_by_booking_id(db, id)
    services = await get_service_booking_id(db, id)
    if not booking:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            "Booking not found")
    if services is not None:
        return [booking, clients, services]
    return [booking, clients]


async def get_clients_bookings(db: AsyncSession, user_id: int):
    bookings = await get_client_bookings_by_user_id(db, user_id)
    return [await get_booking_by_id(db, booking) for booking in bookings]


async def get_clients_booking(db: AsyncSession, booking_id: int, user_id: int):
    bookings = await get_client_bookings_by_user_id(db, user_id)
    if booking_id in bookings:
        return await get_booking_by_id(db, booking_id)
    return HTTPException(status.HTTP_403_FORBIDDEN)


async def create_booking(db: AsyncSession, booking: BookingCreate, user_id: int):
    room = await get_room(db, booking.booking_data.room_num)
    beds = await get_beds_by_room_num(db, room.room_num)
    amount = (await get_cateogry_by_id(db, room.category_id)).price
    if room.is_active == False:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "This toom is not active")
    if beds < len(booking.clients):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "Beds should be more then clients or equal")
    if not await validate_date(db, room.room_num, booking.booking_data.join_date, booking.booking_data.out_date):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "Wrong date")
    booking_id = await create_booking_data(db, booking.booking_data)
    for client in booking.clients:
        client_from_db = await _get_client_by_phone_numner(db, client.phone_number)
        if client_from_db is None:
            client_id = await create_client(db, client)
            await create_client_booking(db, client_id, booking_id)
            await create_client_user(db, client_id, user_id)
        else:
            client_id = client_from_db.id
            await create_client_booking(db, client_id, booking_id)
            await create_client_user(db, client_id, user_id)

    for service_id in booking.services_ids:
        service = await get_service_by_id(db, service_id)
        await create_booking_service(db, service_id, booking_id)
        amount += service.service_price
    payment = PaymentCreate(
        amount=amount,
        payment_date=date.today()
    )
    await create_payment(db, payment, booking_id)
    await db.commit()

    booking_data = await get_booking_by_id(db, booking_id)
    return booking_data


async def delete_booking_by_id(db: AsyncSession, booking_id: int):
    booking = await _get_booking_by_id(db, booking_id)
    try:
        await db.delete(booking)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            "Server error"
                            )
    return {"message: Booking deleted"}


async def put_booking(db: AsyncSession,
                      user_id: int,
                      booking_id: int,
                      booking: BookingCreate):
    await get_booking_by_id(db, booking_id)
    room = await get_room(db, booking.booking_data.room_num)
    beds = await get_beds_by_room_num(db, room.room_num)
    amount = (await get_cateogry_by_id(db, room.category_id)).price

    if room.is_active == False:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "This toom is not active")

    if beds < len(booking.clients):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "Beds should be more then clients or equal")

    if not await validate_date(db, room.room_num, booking.booking_data.join_date, booking.booking_data.out_date):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "Wrong date")
    await update_booking_data(db, booking_id, booking.booking_data)
    await delete_client_booking(db, booking_id)

    for client in booking.clients:
        client_from_db = await _get_client_by_phone_numner(db, client.phone_number)
        if client_from_db is None:
            client_id = await create_client(db, client)
            await create_client_booking(db, client_id, booking_id)
            await create_client_user(db, client_id, user_id)
        else:
            client_id = client_from_db.id
            await create_client_booking(db, client_id, booking_id)
    await delete_booking_service(db, booking_id)
    for service_id in booking.services_ids:
        service = await get_service_by_id(db, service_id)
        await create_booking_service(db, service_id, booking_id)
        amount += service.service_price
    payment = PaymentCreate(
        amount=amount,
        payment_date=date.today()
    )
    await create_payment(db, payment, booking_id)
    await db.commit()
    return await get_booking_by_id(db, booking_id)
