"""
APScheduler-based job scheduler.
Loads active sources on startup and registers their cron schedules.
"""
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from ..database import AsyncSessionLocal
from ..models.source import Source, SourceType
from ..models.scrape_job import ScrapeJob, JobStatus
from ..scrapers import SCRAPER_REGISTRY
from ..quality.validator import validate_record
from ..quality.deduplicator import upsert_record
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_scheduler: Optional[AsyncIOScheduler] = None

# job_id → asyncio.Task, so cancel() can actually stop the task
_running_tasks: dict[int, asyncio.Task] = {}


async def start_scheduler() -> None:
    global _scheduler
    _scheduler = AsyncIOScheduler(timezone=settings.SCHEDULER_TIMEZONE)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Source).where(Source.is_active == True, Source.cron_schedule.isnot(None))
        )
        sources = result.scalars().all()
        for source in sources:
            _register_source(_scheduler, source.id, source.cron_schedule)
            logger.info(f"Scheduled source {source.name!r} → {source.cron_schedule}")

    _scheduler.start()
    logger.info("Scheduler started")


async def stop_scheduler() -> None:
    global _scheduler
    for task in _running_tasks.values():
        task.cancel()
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")


def _register_source(scheduler: AsyncIOScheduler, source_id: int, cron: str) -> None:
    try:
        trigger = CronTrigger.from_crontab(cron, timezone=settings.SCHEDULER_TIMEZONE)
        scheduler.add_job(
            _scheduled_wrapper,
            trigger=trigger,
            id=f"source_{source_id}",
            args=[source_id],
            replace_existing=True,
        )
    except Exception as exc:
        logger.error(f"Failed to register source {source_id}: {exc}")


async def _scheduled_wrapper(source_id: int) -> None:
    await run_scrape_job(source_id, triggered_by="scheduler")


async def cancel_job_task(job_id: int) -> bool:
    """Cancel a running asyncio task by job_id. Returns True if cancelled."""
    task = _running_tasks.get(job_id)
    if task and not task.done():
        task.cancel()
        return True
    return False


async def run_scrape_job(
    source_id: int,
    triggered_by: str = "manual",
    create_task: bool = False,
) -> int:
    async with AsyncSessionLocal() as db:
        source = await db.get(Source, source_id)
        if not source:
            raise ValueError(f"Source {source_id} not found")

        job = ScrapeJob(
            source_id=source_id,
            status=JobStatus.pending,
            triggered_by=triggered_by,
        )
        db.add(job)
        await db.flush()
        await db.refresh(job)
        job_id = job.id
        await db.commit()

    if create_task:
        task = asyncio.create_task(_execute_job(job_id, source_id))
        _running_tasks[job_id] = task
        task.add_done_callback(lambda _: _running_tasks.pop(job_id, None))
    else:
        await _execute_job(job_id, source_id)

    return job_id


async def _execute_job(job_id: int, source_id: int) -> None:
    async with AsyncSessionLocal() as db:
        job = await db.get(ScrapeJob, job_id)
        source = await db.get(Source, source_id)
        if not job or not source:
            return

        config = {}
        if source.config_json:
            try:
                config = json.loads(source.config_json)
            except Exception as exc:
                job.status = JobStatus.failed
                job.error_message = f"Invalid config_json — {exc}"
                job.finished_at = datetime.now(timezone.utc)
                await db.commit()
                return

        ScraperClass = SCRAPER_REGISTRY.get(source.source_type)
        if not ScraperClass:
            job.status = JobStatus.failed
            job.error_message = f"No scraper for type {source.source_type}"
            await db.commit()
            return

        job.status = JobStatus.running
        job.started_at = datetime.now(timezone.utc)
        await db.commit()

    try:
        async with ScraperClass(source_id, config, source.base_url) as scraper:
            result = await scraper.run()
    except asyncio.CancelledError:
        async with AsyncSessionLocal() as db:
            job = await db.get(ScrapeJob, job_id)
            if job:
                job.status = JobStatus.cancelled
                job.finished_at = datetime.now(timezone.utc)
                job.error_message = "Cancelled by user"
                await db.commit()
        return
    except Exception as exc:
        logger.exception(f"Scraper {source.source_type} raised: {exc}")
        async with AsyncSessionLocal() as db:
            job = await db.get(ScrapeJob, job_id)
            if job:
                job.status = JobStatus.failed
                job.finished_at = datetime.now(timezone.utc)
                job.error_message = str(exc)
                await db.commit()
        return

    # Validate + deduplicate
    n_new = n_updated = n_skipped = 0
    async with AsyncSessionLocal() as db:
        for raw in result.records:
            quality_score, flags = validate_record(raw, source.source_type)
            raw["quality_score"] = quality_score
            raw["completeness_flags"] = flags
            status = await upsert_record(raw, source.source_type, source_id, job_id, db)
            if status == "new":
                n_new += 1
            elif status == "updated":
                n_updated += 1
            else:
                n_skipped += 1

        source_obj = await db.get(Source, source_id)
        if source_obj:
            source_obj.last_scraped_at = datetime.now(timezone.utc)

        job = await db.get(ScrapeJob, job_id)
        job.status = JobStatus.failed if result.error_message else JobStatus.success
        job.finished_at = datetime.now(timezone.utc)
        job.records_found = result.records_found
        job.records_new = n_new
        job.records_updated = n_updated
        job.records_skipped = n_skipped
        job.error_message = result.error_message
        job.log_text = result.log_text
        await db.commit()

    logger.info(f"Job {job_id} finished: {n_new} new, {n_updated} updated, {n_skipped} skipped")
