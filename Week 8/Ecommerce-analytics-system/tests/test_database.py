import sqlite3
import pytest
from pathlib import Path
from src.database.connection import DatabaseManager

def test_schema_creation(tmp_path):
    db_path = tmp_path / "test.db"
    with DatabaseManager(db_path) as db:
        db.initialize_schema(Path("sql"))
        res = db.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
        tables = res['name'].tolist()
        assert 'customers' in tables
        assert 'orders' in tables
