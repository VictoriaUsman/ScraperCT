from .ct_open_data import CTOpenDataScraper
from .vision_assessor import VisionAssessorScraper
from .land_records import LandRecordsScraper
from .sos_business import SoSBusinessScraper
from ..models.source import SourceType

SCRAPER_REGISTRY = {
    SourceType.ckan_api: CTOpenDataScraper,
    SourceType.vision_gov: VisionAssessorScraper,
    SourceType.land_records: LandRecordsScraper,
    SourceType.ct_sos: SoSBusinessScraper,
}
