"""
Streaming CSV export using pandas in chunks.
"""
import csv
import io
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.property_record import PropertyRecord
from ..models.land_record import LandRecord
from ..models.business_record import BusinessRecord
from ..models.open_data_record import OpenDataRecord
from ..models.court_record import CourtRecord
from ..models.tax_record import TaxRecord
from ..models.municipal_record import MunicipalRecord
from ..config import get_settings

settings = get_settings()

MODEL_MAP = {
    "properties": PropertyRecord,
    "land-records": LandRecord,
    "businesses": BusinessRecord,
    "open-data": OpenDataRecord,
    "court-records": CourtRecord,
    "tax-records": TaxRecord,
    "municipal-records": MunicipalRecord,
}


async def stream_csv(record_type: str, db: AsyncSession) -> AsyncIterator[str]:
    Model = MODEL_MAP.get(record_type)
    if not Model:
        yield "error: unknown record type\n"
        return

    # Get column names from the model
    columns = [c.key for c in Model.__mapper__.column_attrs]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    yield buf.getvalue()

    # Stream in chunks
    offset = 0
    chunk = settings.EXPORT_CHUNK_SIZE
    while True:
        result = await db.execute(
            select(Model).order_by(Model.id).limit(chunk).offset(offset)
        )
        rows = result.scalars().all()
        if not rows:
            break
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=columns, extrasaction="ignore")
        for row in rows:
            writer.writerow({c: getattr(row, c, None) for c in columns})
        yield buf.getvalue()
        offset += chunk
