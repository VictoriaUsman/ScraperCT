from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta, timezone
from typing import Any

from ..dependencies import get_db
from ..models.scrape_job import ScrapeJob, JobStatus
from ..models.property_record import PropertyRecord
from ..models.land_record import LandRecord
from ..models.business_record import BusinessRecord
from ..models.open_data_record import OpenDataRecord

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
async def dashboard_summary(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    property_count = (await db.execute(select(func.count(PropertyRecord.id)))).scalar_one()
    land_count = (await db.execute(select(func.count(LandRecord.id)))).scalar_one()
    business_count = (await db.execute(select(func.count(BusinessRecord.id)))).scalar_one()
    open_data_count = (await db.execute(select(func.count(OpenDataRecord.id)))).scalar_one()

    running_jobs = (
        await db.execute(
            select(func.count(ScrapeJob.id)).where(ScrapeJob.status == JobStatus.running)
        )
    ).scalar_one()

    last_job = (
        await db.execute(
            select(ScrapeJob).order_by(desc(ScrapeJob.created_at)).limit(1)
        )
    ).scalar_one_or_none()

    return {
        "record_counts": {
            "properties": property_count,
            "land_records": land_count,
            "businesses": business_count,
            "open_data": open_data_count,
        },
        "running_jobs": running_jobs,
        "last_job_at": last_job.created_at if last_job else None,
        "last_job_status": last_job.status if last_job else None,
    }


@router.get("/job-history")
async def job_history(
    days: int = 30, db: AsyncSession = Depends(get_db)
) -> list[dict[str, Any]]:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(
            func.date(ScrapeJob.created_at).label("date"),
            ScrapeJob.status,
            func.count(ScrapeJob.id).label("count"),
        )
        .where(ScrapeJob.created_at >= since)
        .group_by(func.date(ScrapeJob.created_at), ScrapeJob.status)
        .order_by(func.date(ScrapeJob.created_at))
    )
    rows = result.all()
    # Pivot into [{date, success, failed, ...}, ...]
    pivoted: dict[str, dict] = {}
    for row in rows:
        day = str(row[0])
        if day not in pivoted:
            pivoted[day] = {"date": day, "success": 0, "failed": 0, "running": 0, "pending": 0, "cancelled": 0}
        pivoted[day][row[1]] = row[2]
    return list(pivoted.values())
