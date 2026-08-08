import pandas as pd
from pathlib import Path
from src.database.connection import DatabaseManager
from src.analytics.models import ReportType
import logging

class ReportGenerator:
    def __init__(self, db_manager: DatabaseManager, sql_dir: Path):
        self.db_manager = db_manager
        self.sql_dir = sql_dir
        self.logger = logging.getLogger(__name__)

    def _read_query(self, sql_file: str, query_index: int = 0) -> str:
        with open(self.sql_dir / sql_file, 'r') as f:
            queries = [q.strip() for q in f.read().split(';') if q.strip()]
        if query_index >= len(queries):
            raise ValueError(f"Query index {query_index} out of bounds for {sql_file}")
        return queries[query_index]

    def generate_report(self, report_type: ReportType, limit: int = 10) -> pd.DataFrame:
        query_map = {
            ReportType.REVENUE: ('02_basic_analytics.sql', 0),
            ReportType.TOP_CUSTOMERS: ('02_basic_analytics.sql', 1),
            ReportType.RETENTION: ('06_cohort_analysis.sql', 0),
            ReportType.SEGMENTATION: ('05_cte_analysis.sql', 1),
            ReportType.RFM_ANALYSIS: ('07_rfm_analysis.sql', 0),
            ReportType.PRODUCT_AFFINITY: ('08_market_basket.sql', 0),
        }

        if report_type == ReportType.HEALTH_CHECK:
            return self._run_health_check()
            
        sql_file, query_index = query_map[report_type]
        query = self._read_query(sql_file, query_index)
        
        if report_type == ReportType.TOP_CUSTOMERS:
            query = query.replace('LIMIT 10', f'LIMIT {limit}')
            
        df = self.db_manager.execute_query(query)
        if report_type != ReportType.TOP_CUSTOMERS:
            df = df.head(limit)
        return df

    def _run_health_check(self) -> pd.DataFrame:
        tables = ['customers', 'products', 'orders', 'order_items']
        counts = []
        for t in tables:
            res = self.db_manager.execute_query(f"SELECT COUNT(*) as count FROM {t}")
            counts.append({'table': t, 'row_count': res['count'].iloc[0]})
        return pd.DataFrame(counts)
