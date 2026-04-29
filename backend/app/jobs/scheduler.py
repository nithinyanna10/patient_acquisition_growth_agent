import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def _heartbeat_job() -> None:
    logger.info("background_job=heartbeat status=ok")


def start_scheduler() -> None:
    if not settings.scheduler_enabled:
        return
    if not scheduler.running:
        scheduler.add_job(_heartbeat_job, "interval", minutes=10, id="heartbeat")
        scheduler.start()
        logger.info("scheduler_started=true")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown()
        logger.info("scheduler_stopped=true")
