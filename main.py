from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, engine
from app.models import User, Train, Inventory, Booking

from app.routes.auth import router as auth_router
from app.routes.trains import router as trains_router
from app.routes.inventory import router as inventory_router
from app.routes.bookings import router as bookings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Mini Railway Booking System",
    description="Railway Reservation Backend API",
    version="1.0.0",
    lifespan=lifespan,
)


# Register API routers
app.include_router(auth_router)
app.include_router(trains_router)
app.include_router(inventory_router)
app.include_router(bookings_router)


# HOME API
@app.get("/", tags=["Home"])
def home():
    return {"message": "Welcome to Mini Railway Booking System", "status": "Running"}


# HEALTH CHECK API
@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


# DATABASE STATUS API
@app.get("/database", tags=["Database"])
def database_status():
    return {"database": "connected", "tables": list(Base.metadata.tables.keys())}
