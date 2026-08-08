from enum import Enum

class ReportType(Enum):
    REVENUE = "revenue"
    TOP_CUSTOMERS = "top_customers"
    RETENTION = "retention"
    SEGMENTATION = "segmentation"
    RFM_ANALYSIS = "rfm_analysis"
    PRODUCT_AFFINITY = "product_affinity"
    HEALTH_CHECK = "health_check"
