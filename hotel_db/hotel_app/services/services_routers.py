from fastapi import APIRouter, Depends, HTTPException, status
from . import crud
from ..models import User
from ..schemas import ServiceCreate,  ServiceUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..auth import get_current_user_from_token
from ..admin.utils import is_admin
from fastapi_cache.decorator import cache

router = APIRouter(
    prefix="/services",
    tags=["services"]
)


@router.get("/")
@cache(expire=30)
async def get_services(skip: int = 0,
                     limit: int = 100,
                     session: AsyncSession = Depends(get_db)):
    return await crud.get_services(session, skip, limit)


@router.get("/{serivce_id}")
async def get_service(service_id: int,
                      session: AsyncSession = Depends(get_db)):
    return await crud.get_service_by_id(session, service_id)


@router.post("/")
async def create_service(service: ServiceCreate,
                      session: AsyncSession = Depends(get_db),
                      cur_user: User = Depends(get_current_user_from_token)):
    if await is_admin(session, cur_user.id):
        return await crud.create_service(session, service)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@router.patch("/{service_id}")
async def patch_service(service_id: int,
                        patch_category: ServiceUpdate,
                        session: AsyncSession = Depends(get_db),
                        cur_user: User = Depends(get_current_user_from_token)):
    if await is_admin(session, cur_user.id):
        return await crud.update_service(session, service_id, patch_category)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@router.delete("/{service_id}")
async def delete_category(service_id: int,
                          session: AsyncSession = Depends(get_db),
                          cur_user: User = Depends(get_current_user_from_token)):
    if await is_admin(session, cur_user.id):
        return await crud.delete_service(session, service_id)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
