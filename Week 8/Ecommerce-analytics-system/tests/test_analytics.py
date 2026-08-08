from src.analytics.executor import ReportGenerator
from src.analytics.models import ReportType
from src.database.connection import DatabaseManager
from pathlib import Path

def test_health_check_report(sample_db):
    with DatabaseManager(sample_db) as db:
        gen = ReportGenerator(db, Path("sql"))
        df = gen.generate_report(ReportType.HEALTH_CHECK)
        assert len(df) == 4
        assert 'table' in df.columns
