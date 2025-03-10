from fastapi import APIRouter

from api.v1.endpoints import auth, channel, vacancy, user

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["v1/auth"])
api_router.include_router(user.router, prefix="/users", tags=["v1/users"])
api_router.include_router(channel.router, prefix="/channels", tags=["v1/channels"])
api_router.include_router(vacancy.router, prefix="/vacancies", tags=["v1/vacancies"])
