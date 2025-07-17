from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from services.tasks import update_devices_data
from middleware.logger import logger
import os
from dotenv import load_dotenv
load_dotenv()
async def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        update_devices_data,
        trigger=IntervalTrigger(minutes=int(os.getenv("SCHEDULER_INTERVAL"))),
        id="atualizacao_ip_coletores",
        replace_existing=True
    )
    scheduler.start()
    logger.info("[SCHEDULER_SERVICE] | Starting scheduler...")
    return scheduler