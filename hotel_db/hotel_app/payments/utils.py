from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import PaymentCreate
from ..models import Payment, booking_payment
from sqlalchemy import insert, select


async def _get_payment_by_id(db: AsyncSession, payment_id):
    payment = (await db.execute(
        select(Payment)
        .where(Payment.id == payment_id)
    )).scalar_one_or_none()
    return payment


async def create_payment(db: AsyncSession, payment: PaymentCreate, booking_id: int):

    payment_id = (await db.execute(
        insert(Payment)
        .returning(Payment.id)
        .values(**payment.model_dump())
    )).scalar_one_or_none()
    await db.execute(
        booking_payment.insert().values(booking_id=booking_id,
                                        payment_id=payment_id)
    )
    await db.commit()
