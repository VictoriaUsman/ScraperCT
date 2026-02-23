from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct
from typing import List, Optional

from ..dependencies import get_db
from ..models.open_data_record import OpenDataRecord
from ..schemas.open_data_record import OpenDataRecordResponse, DatasetInfo

router = APIRouter(prefix="/open-data", tags=["open-data"])


@router.get("/datasets", response_model=List[DatasetInfo])
async def list_datasets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            OpenDataRecord.dataset_id,
            OpenDataRecord.dataset_name,
            func.count(OpenDataRecord.id).label("record_count"),
        ).group_by(OpenDataRecord.dataset_id, OpenDataRecord.dataset_name)
    )
    return [
        DatasetInfo(dataset_id=r[0], dataset_name=r[1], record_count=r[2])
        for r in result.all()
    ]


@router.get("", response_model=List[OpenDataRecordResponse])
async def list_open_data(
    dataset_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    q = select(OpenDataRecord)
    if dataset_id:
        q = q.where(OpenDataRecord.dataset_id == dataset_id)
    q = q.order_by(OpenDataRecord.id).limit(limit).offset(offset)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{record_id}", response_model=OpenDataRecordResponse)
async def get_open_data(record_id: int, db: AsyncSession = Depends(get_db)):
    record = await db.get(OpenDataRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Open data record not found")
    return record
