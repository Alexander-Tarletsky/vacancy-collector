from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.v1.api import api_router
from core.config import settings, STATIC_ROOT
from routes.template_router import template_router

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     await run_migrations()
#     yield
#     # Shutdown
#     await engine.dispose()
#
# async def run_migrations():
#     from alembic.config import Config
#     from alembic import command
#     alembic_cfg = Config("alembic.ini")
#     alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
#     command.upgrade(alembic_cfg, "head")


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
app.include_router(api_router, prefix="/api/v1")
app.include_router(template_router)


# Error handlers
# @app.exception_handler(404)
# async def not_found_exception_handler(request: Request, exc):
#     return templates.TemplateResponse(TEMPLATES_ROOT / "errors/404.html", {"request": request})
#
# @app.exception_handler(500)
# async def server_error_exception_handler(request: Request, exc):
#     return templates.TemplateResponse(TEMPLATES_ROOT / "errors/500.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        workers=1
    )
