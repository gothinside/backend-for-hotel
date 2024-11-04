from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import PaymentUpdate
from ..models import Payment
from fastapi import HTTPException, status
from sqlalchemy import update
from .utils import _get_payment_by_id


async def get_payment_by_id(db: AsyncSession, payment_id: int):
    payment = await _get_payment_by_id(db,  payment_id)
    if payment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            "Payment not found")
    return payment


async def update_payment(db: AsyncSession, patched_data: PaymentUpdate, payment_id: int):
    await get_payment_by_id(db, payment_id)
    update_data = {key: value
                   for key, value in patched_data.model_dump().items()
                   if value is not None
                   }
    if update_data == {}:
        HTTPException(status.HTTP_400_BAD_REQUEST,
                      "No  fields")
    await db.execute(
        update(Payment)
        .where(Payment.id == payment_id)
        .values(**update_data)
    )
    await db.commit()
    return await get_payment_by_id(db, payment_id)


async def delete_payment(db: AsyncSession, payment_id):
    payment = await get_payment_by_id(db, payment_id)
    try:
        await db.delete(payment)
        await db.commit()
    except Exception:
        await db.rollback()

    return {"Message": "Payment deleted"}
