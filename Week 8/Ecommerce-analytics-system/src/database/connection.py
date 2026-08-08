import sqlite3
import pandas as pd
from pathlib import Path
import logging
from typing import Optional

class DatabaseManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
        self.logger = logging.getLogger(__name__)
    
    def __enter__(self):
        # Create directory if it doesn't exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(str(self.db_path))
        # Enforce foreign keys in SQLite
        self._connection.execute("PRAGMA foreign_keys = ON")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._connection:
            if exc_type is None:
                self._connection.commit()
            else:
                self._connection.rollback()
            self._connection.close()
    
    @property
    def connection(self) -> sqlite3.Connection:
        if not self._connection:
            raise RuntimeError("DatabaseManager must be used as a context manager")
        return self._connection

    def execute_script(self, script_path: Path) -> None:
        with open(script_path, 'r') as f:
            script = f.read()
        self.connection.executescript(script)
        self.logger.info(f"Executed script {script_path}")
        
    def execute_query(self, query: str, params: tuple = ()) -> pd.DataFrame:
        return pd.read_sql_query(query, self.connection, params=params)

    def initialize_schema(self, schema_dir: Path) -> None:
        self.execute_script(schema_dir / '00_schema.sql')
        self.execute_script(schema_dir / '01_constraints.sql')
