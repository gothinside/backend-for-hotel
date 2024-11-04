from fastapi import APIRouter, Depends
from ..auth import get_current_user_from_token
from ..database import get_db
from .crud import *
from ..schemas import PaymentUpdate
from ..admin.utils import is_admin
from fastapi import status, HTTPException


router = APIRouter(
    prefix="/payments",
    tags=["payments"]
)


@router.get("/{payment_id}")
async def get_payment(payment_id: int,
                      session=Depends(get_db),
                      cur_user=Depends(get_current_user_from_token)):
    if await is_admin(session, cur_user.id):
        return await get_payment_by_id(session, payment_id)
    raise HTTPException(status.HTTP_403_FORBIDDEN)


@router.patch("/{payment_id}")
async def patch_payment(payment_id: int,
                        update_data: PaymentUpdate,
                        session=Depends(get_db),
                        cur_user=Depends(get_current_user_from_token)):
    if await is_admin(session, cur_user.id):
        return await update_payment(session, update_data, payment_id)
    raise HTTPException(status.HTTP_403_FORBIDDEN)


@router.delete("/{payment_id}")
async def delete_payment_by_id(
        payment_id: int,
        session=Depends(get_db),
        cur_user=Depends(get_current_user_from_token)):
    if await is_admin(session, cur_user.id):
        return await delete_payment(session, payment_id)
    raise HTTPException(status.HTTP_403_FORBIDDEN)
