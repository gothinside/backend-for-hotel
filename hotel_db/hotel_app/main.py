
from fastapi import FastAPI
import uvicorn
#from .services import routers as serv_routers
from hotel_app.categories import category_routers
from hotel_app.users import users_routers
from hotel_app.login import login_router
from hotel_app.admin import admin_router
from hotel_app.rooms import rooms_routers
from hotel_app.services import services_routers
from hotel_app.clients import client_routers
from hotel_app.bookings import booking_routers
from hotel_app.payments import payment_routers
from hotel_app.redis_cache import lifespan
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(lifespan = lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

app.include_router(category_routers.router)
app.include_router(users_routers.router)
app.include_router(login_router)
app.include_router(admin_router.router)
app.include_router(rooms_routers.router)
app.include_router(services_routers.router)
app.include_router(client_routers.router)
app.include_router(booking_routers.router)
app.include_router(payment_routers.router)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port="8000")

