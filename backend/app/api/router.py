from fastapi import APIRouter
from .sources import router as sources_router
from .jobs import router as jobs_router
from .properties import router as properties_router
from .land_records import router as land_records_router
from .businesses import router as businesses_router
from .open_data import router as open_data_router
from .exports import router as exports_router
from .dashboard import router as dashboard_router
from .court_records import router as court_records_router
from .tax_records import router as tax_records_router
from .municipal_records import router as municipal_records_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(sources_router)
api_router.include_router(jobs_router)
api_router.include_router(properties_router)
api_router.include_router(land_records_router)
api_router.include_router(businesses_router)
api_router.include_router(open_data_router)
api_router.include_router(exports_router)
api_router.include_router(dashboard_router)
api_router.include_router(court_records_router)
api_router.include_router(tax_records_router)
api_router.include_router(municipal_records_router)
