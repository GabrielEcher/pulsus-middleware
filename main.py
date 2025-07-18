from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from middleware.middleware import PulsusMiddleware
from middleware.logger import logger
from services.scheduler import start_scheduler
from routes.devices_router import router as router_devices
from routes.export_router import router as router_export
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = await start_scheduler()
    yield
    scheduler.shutdown()
    logger.info("Scheduler finalizado")

app = FastAPI(
    title="API Integração Pulsus",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/api/openapi.json",
    root_path="/api/pulsus",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(PulsusMiddleware)

app.include_router(router_devices)
app.include_router(router_export)