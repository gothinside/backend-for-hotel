
from fastapi import APIRouter, Depends
from ..schemas import ClientBase, ClientUpdate
from ..auth import get_current_user_from_token
from ..database import get_db
from .crud import *

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
)

# @router.post("/")
# async def create_new_client(client: Client,
#                             cur_user = Depends(get_current_user_from_token)):
#     return 1


@router.get("/")
async def get_client(
        session=Depends(get_db),
        cur_user=Depends(get_current_user_from_token)):
    return await get_users_clients(session, cur_user.id)


@router.patch("/{client_id}", response_model=ClientBase)
async def patch_client(client_id: int,
                       client: ClientUpdate,
                       session=Depends(get_db),
                       cur_user=Depends(get_current_user_from_token)):
    return await update_client(session, client, client_id)
