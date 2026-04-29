from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.auth_routes import router as auth_router
from app.api.crud_routes import router as crud_router
from app.api.intelligence_routes import router as intelligence_router
from app.api.ops_routes import router as ops_router
from app.api.routes import router
from app.core.config import settings
from app.jobs.scheduler import start_scheduler, stop_scheduler
from app.observability.logging import configure_logging

configure_logging()

app = FastAPI(
    title=settings.app_name,
    docs_url="/docs" if settings.openapi_enabled else None,
    redoc_url="/redoc" if settings.openapi_enabled else None,
    openapi_url="/openapi.json" if settings.openapi_enabled else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(auth_router)
app.include_router(crud_router)
app.include_router(intelligence_router)
app.include_router(ops_router)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.on_event("startup")
def on_startup() -> None:
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown() -> None:
    stop_scheduler()
