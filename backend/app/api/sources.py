from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List
import asyncio

from ..dependencies import get_db
from ..models.source import Source
from ..models.scrape_job import ScrapeJob
from ..schemas.source import SourceCreate, SourceUpdate, SourceResponse, TriggerResponse

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=List[SourceResponse])
async def list_sources(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Source).order_by(Source.id))
    return result.scalars().all()


@router.post("", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def create_source(payload: SourceCreate, db: AsyncSession = Depends(get_db)):
    source = Source(**payload.model_dump())
    db.add(source)
    await db.flush()
    await db.refresh(source)
    return source


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(source_id: int, db: AsyncSession = Depends(get_db)):
    source = await db.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.put("/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: int, payload: SourceUpdate, db: AsyncSession = Depends(get_db)
):
    source = await db.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(source, field, value)
    await db.flush()
    await db.refresh(source)
    return source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(source_id: int, db: AsyncSession = Depends(get_db)):
    source = await db.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    # Delete related jobs first to avoid FK constraint violation
    await db.execute(delete(ScrapeJob).where(ScrapeJob.source_id == source_id))
    await db.delete(source)


@router.post("/{source_id}/trigger", response_model=TriggerResponse)
async def trigger_source(source_id: int, db: AsyncSession = Depends(get_db)):
    source = await db.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    # Import here to avoid circular imports
    from ..scheduler.scheduler import run_scrape_job
    job_id = await run_scrape_job(source_id, triggered_by="manual", create_task=True)
    return TriggerResponse(job_id=job_id, message="Scrape job started")


@router.patch("/{source_id}/toggle", response_model=SourceResponse)
async def toggle_source(source_id: int, db: AsyncSession = Depends(get_db)):
    source = await db.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    source.is_active = not source.is_active
    await db.flush()
    await db.refresh(source)
    return source
