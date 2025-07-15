from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.tasks import request_devices_data, update_devices_data
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from contextlib import asynccontextmanager
from sqlalchemy import text
from database.oracle_connection import Session
from middleware.middleware import PulsusMiddleware
from middleware.logger import logger
scheduler = AsyncIOScheduler()
orcl_session = Session()


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    scheduler.add_job(
        update_devices_data,
        trigger=IntervalTrigger(hours=2),
        id="atualizacao_ip_coletores",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler iniciado com sucesso")
    yield
    # Fim da aplicação
    scheduler.shutdown()
    logger.info("Scheduler finalizado")

app = FastAPI(
    title="API Integração Pulsus",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
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
