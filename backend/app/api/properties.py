from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct
from typing import List, Optional

from ..dependencies import get_db
from ..models.property_record import PropertyRecord
from ..schemas.property_record import PropertyRecordResponse, PropertyStatsResponse

router = APIRouter(prefix="/properties", tags=["properties"])


@router.get("/stats", response_model=PropertyStatsResponse)
async def property_stats(db: AsyncSession = Depends(get_db)):
    total = (await db.execute(select(func.count(PropertyRecord.id)))).scalar_one()
    towns_result = await db.execute(
        select(distinct(PropertyRecord.town)).where(PropertyRecord.town.isnot(None))
    )
    towns = sorted([r[0] for r in towns_result.all()])
    years_result = await db.execute(
        select(distinct(PropertyRecord.assessment_year)).where(
            PropertyRecord.assessment_year.isnot(None)
        )
    )
    years = sorted([r[0] for r in years_result.all()])
    agg = await db.execute(
        select(
            func.avg(PropertyRecord.assessed_value),
            func.min(PropertyRecord.assessed_value),
            func.max(PropertyRecord.assessed_value),
        )
    )
    row = agg.one()
    return PropertyStatsResponse(
        total=total,
        towns=towns,
        years=years,
        avg_assessed_value=row[0],
        min_assessed_value=row[1],
        max_assessed_value=row[2],
    )


@router.get("", response_model=List[PropertyRecordResponse])
async def list_properties(
    town: Optional[str] = Query(None),
    owner: Optional[str] = Query(None),
    parcel_id: Optional[str] = Query(None),
    min_value: Optional[float] = Query(None),
    max_value: Optional[float] = Query(None),
    year: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    q = select(PropertyRecord)
    if town:
        q = q.where(PropertyRecord.town.ilike(f"%{town}%"))
    if owner:
        q = q.where(PropertyRecord.owner_name.ilike(f"%{owner}%"))
    if parcel_id:
        q = q.where(PropertyRecord.parcel_id.ilike(f"%{parcel_id}%"))
    if min_value is not None:
        q = q.where(PropertyRecord.assessed_value >= min_value)
    if max_value is not None:
        q = q.where(PropertyRecord.assessed_value <= max_value)
    if year:
        q = q.where(PropertyRecord.assessment_year == year)
    q = q.order_by(PropertyRecord.id).limit(limit).offset(offset)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{record_id}", response_model=PropertyRecordResponse)
async def get_property(record_id: int, db: AsyncSession = Depends(get_db)):
    record = await db.get(PropertyRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Property record not found")
    return record
