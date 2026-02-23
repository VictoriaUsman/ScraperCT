from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional

from ..dependencies import get_db
from ..models.scrape_job import ScrapeJob, JobStatus
from ..schemas.scrape_job import ScrapeJobResponse, ScrapeJobListResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=List[ScrapeJobListResponse])
async def list_jobs(
    source_id: Optional[int] = Query(None),
    status: Optional[JobStatus] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    q = select(ScrapeJob).order_by(desc(ScrapeJob.created_at))
    if source_id is not None:
        q = q.where(ScrapeJob.source_id == source_id)
    if status is not None:
        q = q.where(ScrapeJob.status == status)
    q = q.limit(limit).offset(offset)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{job_id}", response_model=ScrapeJobResponse)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    job = await db.get(ScrapeJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: int, db: AsyncSession = Depends(get_db)):
    job = await db.get(ScrapeJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    await db.delete(job)


@router.post("/{job_id}/cancel", response_model=ScrapeJobResponse)
async def cancel_job(job_id: int, db: AsyncSession = Depends(get_db)):
    job = await db.get(ScrapeJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status not in (JobStatus.pending, JobStatus.running):
        raise HTTPException(status_code=400, detail="Job cannot be cancelled")
    from ..scheduler.scheduler import cancel_job_task
    await cancel_job_task(job_id)  # actually stop the asyncio task
    job.status = JobStatus.cancelled
    from datetime import datetime, timezone
    job.finished_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(job)
    return job
