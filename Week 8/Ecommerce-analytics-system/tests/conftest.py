import pytest
from pathlib import Path
import pandas as pd
from src.database.connection import DatabaseManager
from src.database.loader import DatabaseLoader

@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path

@pytest.fixture
def sample_db(tmp_path):
    db_path = tmp_path / "test.db"
    sql_dir = Path("sql")
    with DatabaseManager(db_path) as db:
        db.initialize_schema(sql_dir)
        # Using the actually generated cleaned data for ease
        loader = DatabaseLoader(db)
        loader.load_tables(Path("data/cleaned"))
    return db_path
