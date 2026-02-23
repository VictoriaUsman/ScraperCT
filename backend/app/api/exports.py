from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Literal

from ..dependencies import get_db
from ..exports.csv_exporter import stream_csv
from ..exports.excel_exporter import export_excel

router = APIRouter(prefix="/exports", tags=["exports"])

RecordType = Literal["properties", "land-records", "businesses", "open-data"]


@router.get("/{record_type}.csv")
async def export_csv(record_type: RecordType, db: AsyncSession = Depends(get_db)):
    return StreamingResponse(
        stream_csv(record_type, db),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={record_type}.csv"},
    )


@router.get("/{record_type}.xlsx")
async def export_xlsx(record_type: RecordType, db: AsyncSession = Depends(get_db)):
    data = await export_excel(record_type, db)
    return StreamingResponse(
        iter([data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={record_type}.xlsx"},
    )
