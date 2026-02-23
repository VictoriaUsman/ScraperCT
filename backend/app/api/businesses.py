from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct
from typing import List, Optional

from ..dependencies import get_db
from ..models.business_record import BusinessRecord
from ..schemas.business_record import BusinessRecordResponse, BusinessStatsResponse

router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.get("/stats", response_model=BusinessStatsResponse)
async def business_stats(db: AsyncSession = Depends(get_db)):
    total = (await db.execute(select(func.count(BusinessRecord.id)))).scalar_one()
    by_type_result = await db.execute(
        select(BusinessRecord.business_type, func.count(BusinessRecord.id)).group_by(
            BusinessRecord.business_type
        )
    )
    by_type = {str(r[0]): r[1] for r in by_type_result.all() if r[0] is not None}
    by_status_result = await db.execute(
        select(BusinessRecord.status, func.count(BusinessRecord.id)).group_by(
            BusinessRecord.status
        )
    )
    by_status = {str(r[0]): r[1] for r in by_status_result.all() if r[0] is not None}
    return BusinessStatsResponse(total=total, by_type=by_type, by_status=by_status)


@router.get("", response_model=List[BusinessRecordResponse])
async def list_businesses(
    name: Optional[str] = Query(None),
    business_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    q = select(BusinessRecord)
    if name:
        q = q.where(BusinessRecord.business_name.ilike(f"%{name}%"))
    if business_type:
        q = q.where(BusinessRecord.business_type.ilike(f"%{business_type}%"))
    if status:
        q = q.where(BusinessRecord.status.ilike(f"%{status}%"))
    q = q.order_by(BusinessRecord.id).limit(limit).offset(offset)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{record_id}", response_model=BusinessRecordResponse)
async def get_business(record_id: int, db: AsyncSession = Depends(get_db)):
    record = await db.get(BusinessRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Business record not found")
    return record
