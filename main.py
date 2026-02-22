from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from src.routes.auth import router as auth_router
from src.routes.dashboard import router as dashboard_router
from src.routes.vendor import router as vendor_router
from src.routes.booking import router as booking_router

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="supersecret")

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(vendor_router)
app.include_router(booking_router)

