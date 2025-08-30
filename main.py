from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.v1.api import api_router
from core.config import settings, STATIC_ROOT
from routes.template_router import template_router

app = FastAPI(
    title="Vacancy Collector",
    description="Telegram vacancy collection service",
    version="1.0.0",
    # lifespan=lifespan,
    # openapi_tags=tags_metadata,
    # docs_url=None,
    # redoc_url=None,
    # openapi_url=None,
)

# Middleware
# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Static files
app.mount("/static", StaticFiles(directory=STATIC_ROOT), name="static")

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(template_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        workers=1
    )
