from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import date

from ..dependencies import get_db
from ..models.municipal_record import MunicipalRecord
from ..schemas.municipal_record import MunicipalRecordResponse, MunicipalRecordStatsResponse

router = APIRouter(prefix="/municipal-records", tags=["municipal-records"])


@router.get("/stats", response_model=MunicipalRecordStatsResponse)
async def municipal_record_stats(db: AsyncSession = Depends(get_db)):
    total = (await db.execute(select(func.count(MunicipalRecord.id)))).scalar_one()

    town_result = await db.execute(
        select(MunicipalRecord.town, func.count(MunicipalRecord.id)).group_by(MunicipalRecord.town)
    )
    by_town = {str(r[0]): r[1] for r in town_result.all() if r[0] is not None}

    type_result = await db.execute(
        select(MunicipalRecord.document_type, func.count(MunicipalRecord.id)).group_by(
            MunicipalRecord.document_type
        )
    )
    by_document_type = {str(r[0]): r[1] for r in type_result.all() if r[0] is not None}

    return MunicipalRecordStatsResponse(
        total=total,
        by_town=by_town,
        by_document_type=by_document_type,
    )


@router.get("", response_model=List[MunicipalRecordResponse])
async def list_municipal_records(
    town: Optional[str] = Query(None),
    document_type: Optional[str] = Query(None),
    body_name: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    q = select(MunicipalRecord)
    if town:
        q = q.where(MunicipalRecord.town.ilike(f"%{town}%"))
    if document_type:
        q = q.where(MunicipalRecord.document_type == document_type)
    if body_name:
        q = q.where(MunicipalRecord.body_name.ilike(f"%{body_name}%"))
    if date_from:
        q = q.where(MunicipalRecord.meeting_date >= date_from)
    if date_to:
        q = q.where(MunicipalRecord.meeting_date <= date_to)
    q = q.order_by(MunicipalRecord.id).limit(limit).offset(offset)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{record_id}", response_model=MunicipalRecordResponse)
async def get_municipal_record(record_id: int, db: AsyncSession = Depends(get_db)):
    record = await db.get(MunicipalRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Municipal record not found")
    return record
