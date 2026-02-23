from .ct_open_data import CTOpenDataScraper
from .vision_assessor import VisionAssessorScraper
from .land_records import LandRecordsScraper
from .sos_business import SoSBusinessScraper
from .iqs_land_records import IQSLandRecordsScraper
from .patriot_assessor import PatriotAssessorScraper
from .arcgis_parcels import ArcGISParcelsScraper
from .ct_courts import CTCourtsScraper
from .ct_tax import CTTaxCollectorScraper
from .municipal_data import MunicipalDataScraper
from ..models.source import SourceType

SCRAPER_REGISTRY = {
    SourceType.ckan_api: CTOpenDataScraper,
    SourceType.vision_gov: VisionAssessorScraper,
    SourceType.land_records: LandRecordsScraper,
    SourceType.ct_sos: SoSBusinessScraper,
    SourceType.iqs_land_records: IQSLandRecordsScraper,
    SourceType.patriot_assessor: PatriotAssessorScraper,
    SourceType.arcgis_parcels: ArcGISParcelsScraper,
    SourceType.ct_courts: CTCourtsScraper,
    SourceType.ct_tax: CTTaxCollectorScraper,
    SourceType.municipal_data: MunicipalDataScraper,
}
