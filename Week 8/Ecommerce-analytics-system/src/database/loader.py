import sqlite3
import pandas as pd
from pathlib import Path
import logging
from typing import Dict, Any
from .connection import DatabaseManager

class DatabaseLoader:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
    def _insert_dataframe(self, df: pd.DataFrame, table_name: str) -> int:
        try:
            df.to_sql(table_name, self.db_manager.connection, if_exists='append', index=False)
            return len(df)
        except sqlite3.Error as e:
            self.logger.error(f"Failed to insert into {table_name}: {e}")
            return 0
    
    def load_tables(self, cleaned_data_path: Path) -> Dict[str, Any]:
        """Load cleaned CSVs and return insertion statistics"""
        stats = {}
        for table_name, csv_file in {
            'customers': 'customers_clean.csv',
            'products': 'products_clean.csv',
            'orders': 'orders_clean.csv',
            'order_items': 'order_items_clean.csv'
        }.items():
            file_path = cleaned_data_path / csv_file
            if not file_path.exists():
                self.logger.error(f"File not found: {file_path}")
                continue
                
            df = pd.read_csv(file_path)
            rows_inserted = self._insert_dataframe(df, table_name)
            stats[table_name] = {
                'expected': len(df),
                'inserted': rows_inserted,
                'status': 'SUCCESS' if len(df) == rows_inserted else 'PARTIAL_FAILURE'
            }
        return stats
    
    def verify_integrity(self) -> Dict[str, Any]:
        """Check referential integrity and return report"""
        report = {}
        
        # Check orphaned orders
        query_orders = """
            SELECT COUNT(*) as cnt FROM orders 
            WHERE customer_id NOT IN (SELECT customer_id FROM customers)
        """
        res_orders = self.db_manager.execute_query(query_orders)
        orphaned_orders = int(res_orders['cnt'].iloc[0])
        report['orphaned_orders'] = orphaned_orders
        
        # Check orphaned order_items
        query_items = """
            SELECT COUNT(*) as cnt FROM order_items 
            WHERE order_id NOT IN (SELECT order_id FROM orders)
               OR product_id NOT IN (SELECT product_id FROM products)
        """
        res_items = self.db_manager.execute_query(query_items)
        orphaned_items = int(res_items['cnt'].iloc[0])
        report['orphaned_items'] = orphaned_items
        
        report['pass'] = (orphaned_orders == 0 and orphaned_items == 0)
        return report

def setup_database(db_path: Path, sql_dir: Path, cleaned_data_dir: Path) -> Dict[str, Any]:
    with DatabaseManager(db_path) as db:
        db.initialize_schema(sql_dir)
        loader = DatabaseLoader(db)
        stats = loader.load_tables(cleaned_data_dir)
        integrity = loader.verify_integrity()
        return {'load_stats': stats, 'integrity': integrity}
