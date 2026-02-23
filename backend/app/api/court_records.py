from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct
from typing import List, Optional
from datetime import date

from ..dependencies import get_db
from ..models.court_record import CourtRecord
from ..schemas.court_record import CourtRecordResponse, CourtRecordStatsResponse

router = APIRouter(prefix="/court-records", tags=["court-records"])


@router.get("/stats", response_model=CourtRecordStatsResponse)
async def court_record_stats(db: AsyncSession = Depends(get_db)):
    total = (await db.execute(select(func.count(CourtRecord.id)))).scalar_one()

    type_result = await db.execute(
        select(CourtRecord.case_type, func.count(CourtRecord.id)).group_by(CourtRecord.case_type)
    )
    by_case_type = {str(r[0]): r[1] for r in type_result.all() if r[0] is not None}

    loc_result = await db.execute(
        select(CourtRecord.court_location, func.count(CourtRecord.id)).group_by(CourtRecord.court_location)
    )
    by_court_location = {str(r[0]): r[1] for r in loc_result.all() if r[0] is not None}

    return CourtRecordStatsResponse(
        total=total,
        by_case_type=by_case_type,
        by_court_location=by_court_location,
    )


@router.get("", response_model=List[CourtRecordResponse])
async def list_court_records(
    case_type: Optional[str] = Query(None),
    court_location: Optional[str] = Query(None),
    plaintiff: Optional[str] = Query(None),
    defendant: Optional[str] = Query(None),
    disposition: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    q = select(CourtRecord)
    if case_type:
        q = q.where(CourtRecord.case_type == case_type)
    if court_location:
        q = q.where(CourtRecord.court_location.ilike(f"%{court_location}%"))
    if plaintiff:
        q = q.where(CourtRecord.plaintiff.ilike(f"%{plaintiff}%"))
    if defendant:
        q = q.where(CourtRecord.defendant.ilike(f"%{defendant}%"))
    if disposition:
        q = q.where(CourtRecord.disposition.ilike(f"%{disposition}%"))
    if date_from:
        q = q.where(CourtRecord.filing_date >= date_from)
    if date_to:
        q = q.where(CourtRecord.filing_date <= date_to)
    q = q.order_by(CourtRecord.id).limit(limit).offset(offset)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{record_id}", response_model=CourtRecordResponse)
async def get_court_record(record_id: int, db: AsyncSession = Depends(get_db)):
    record = await db.get(CourtRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Court record not found")
    return record
