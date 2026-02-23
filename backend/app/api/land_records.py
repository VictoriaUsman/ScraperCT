from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct
from typing import List, Optional
from datetime import date

from ..dependencies import get_db
from ..models.land_record import LandRecord, LandRecordType
from ..schemas.land_record import LandRecordResponse, LandRecordStatsResponse

router = APIRouter(prefix="/land-records", tags=["land-records"])


@router.get("/stats", response_model=LandRecordStatsResponse)
async def land_record_stats(db: AsyncSession = Depends(get_db)):
    total = (await db.execute(select(func.count(LandRecord.id)))).scalar_one()
    towns_result = await db.execute(
        select(distinct(LandRecord.town)).where(LandRecord.town.isnot(None))
    )
    towns = sorted([r[0] for r in towns_result.all()])
    types_result = await db.execute(
        select(LandRecord.record_type, func.count(LandRecord.id)).group_by(
            LandRecord.record_type
        )
    )
    record_types = {str(r[0]): r[1] for r in types_result.all() if r[0] is not None}
    return LandRecordStatsResponse(total=total, towns=towns, record_types=record_types)


@router.get("", response_model=List[LandRecordResponse])
async def list_land_records(
    town: Optional[str] = Query(None),
    record_type: Optional[LandRecordType] = Query(None),
    grantor: Optional[str] = Query(None),
    grantee: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    q = select(LandRecord)
    if town:
        q = q.where(LandRecord.town.ilike(f"%{town}%"))
    if record_type:
        q = q.where(LandRecord.record_type == record_type)
    if grantor:
        q = q.where(LandRecord.grantor.ilike(f"%{grantor}%"))
    if grantee:
        q = q.where(LandRecord.grantee.ilike(f"%{grantee}%"))
    if date_from:
        q = q.where(LandRecord.recorded_date >= date_from)
    if date_to:
        q = q.where(LandRecord.recorded_date <= date_to)
    q = q.order_by(LandRecord.id).limit(limit).offset(offset)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{record_id}", response_model=LandRecordResponse)
async def get_land_record(record_id: int, db: AsyncSession = Depends(get_db)):
    record = await db.get(LandRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Land record not found")
    return record
