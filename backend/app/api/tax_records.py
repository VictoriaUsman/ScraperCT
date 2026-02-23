from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from ..dependencies import get_db
from ..models.tax_record import TaxRecord
from ..schemas.tax_record import TaxRecordResponse, TaxRecordStatsResponse

router = APIRouter(prefix="/tax-records", tags=["tax-records"])


@router.get("/stats", response_model=TaxRecordStatsResponse)
async def tax_record_stats(db: AsyncSession = Depends(get_db)):
    total = (await db.execute(select(func.count(TaxRecord.id)))).scalar_one()

    town_result = await db.execute(
        select(TaxRecord.town, func.count(TaxRecord.id)).group_by(TaxRecord.town)
    )
    by_town = {str(r[0]): r[1] for r in town_result.all() if r[0] is not None}

    status_result = await db.execute(
        select(TaxRecord.status, func.count(TaxRecord.id)).group_by(TaxRecord.status)
    )
    by_status = {str(r[0]): r[1] for r in status_result.all() if r[0] is not None}

    delinquent_sum = (
        await db.execute(
            select(func.sum(TaxRecord.total_due)).where(
                TaxRecord.status.ilike("%delinquent%")
            )
        )
    ).scalar_one()

    return TaxRecordStatsResponse(
        total=total,
        by_town=by_town,
        by_status=by_status,
        total_delinquent_amount=delinquent_sum,
    )


@router.get("", response_model=List[TaxRecordResponse])
async def list_tax_records(
    town: Optional[str] = Query(None),
    owner_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    levy_year: Optional[int] = Query(None),
    bill_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    q = select(TaxRecord)
    if town:
        q = q.where(TaxRecord.town.ilike(f"%{town}%"))
    if owner_name:
        q = q.where(TaxRecord.owner_name.ilike(f"%{owner_name}%"))
    if status:
        q = q.where(TaxRecord.status.ilike(f"%{status}%"))
    if levy_year is not None:
        q = q.where(TaxRecord.levy_year == levy_year)
    if bill_type:
        q = q.where(TaxRecord.bill_type.ilike(f"%{bill_type}%"))
    q = q.order_by(TaxRecord.id).limit(limit).offset(offset)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{record_id}", response_model=TaxRecordResponse)
async def get_tax_record(record_id: int, db: AsyncSession = Depends(get_db)):
    record = await db.get(TaxRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Tax record not found")
    return record
