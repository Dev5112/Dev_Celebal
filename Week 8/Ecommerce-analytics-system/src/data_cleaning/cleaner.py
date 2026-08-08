import pandas as pd
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any
import json
import time
from datetime import datetime

from .validators import is_valid_email

@dataclass
class CleaningResult:
    cleaned_df: pd.DataFrame
    rows_dropped: int
    issues_found: Dict[str, int]
    validation_passed: bool

class DataCleaner:
    def __init__(self, raw_data_path: Path, log_file: Path = None):
        self.raw_path = raw_data_path
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(ch)
            if log_file:
                fh = logging.FileHandler(log_file)
                fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
                self.logger.addHandler(fh)
            
        self.metrics: Dict[str, Any] = {}
        
    def clean_customers(self) -> CleaningResult:
        self.logger.info("Cleaning customers.csv...")
        df = pd.read_csv(self.raw_path / 'customers.csv')
        initial_rows = len(df)
        issues_found = {'invalid_emails': 0, 'duplicate_ids': 0, 'null_dates': 0}
        
        df = df.drop_duplicates(subset=['customer_id'], keep='first')
        issues_found['duplicate_ids'] = initial_rows - len(df)
        
        df['customer_name'] = df['customer_name'].astype(str).str.strip().str.title()
        
        invalid_emails = ~df['email'].apply(is_valid_email)
        issues_found['invalid_emails'] = int(invalid_emails.sum())
        df = df[~invalid_emails]
        
        df['registration_date'] = pd.to_datetime(df['registration_date'], errors='coerce')
        issues_found['null_dates'] = int(df['registration_date'].isna().sum())
        
        df['registration_date'] = df['registration_date'].bfill().ffill()
        df['registration_date'] = df['registration_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        rows_dropped = initial_rows - len(df)
        self.metrics['customers'] = {
            'raw_rows': initial_rows,
            'cleaned_rows': len(df),
            'rows_dropped': rows_dropped,
            'issues_found': issues_found
        }
        
        return CleaningResult(df, rows_dropped, issues_found, True)

    def clean_products(self) -> CleaningResult:
        self.logger.info("Cleaning products.csv...")
        df = pd.read_csv(self.raw_path / 'products.csv')
        initial_rows = len(df)
        issues_found = {'duplicate_ids': 0, 'invalid_cost': 0, 'null_subcategory': 0}
        
        df = df.drop_duplicates(subset=['product_id'], keep='first')
        issues_found['duplicate_ids'] = initial_rows - len(df)
        
        df['product_name'] = df['product_name'].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True).str.title()
        
        invalid_cost = df['cost_price'] <= 0
        issues_found['invalid_cost'] = int(invalid_cost.sum())
        df = df[~invalid_cost]
        
        null_subcat = df['subcategory'].isna()
        issues_found['null_subcategory'] = int(null_subcat.sum())
        df.loc[null_subcat, 'subcategory'] = 'Other'
        
        rows_dropped = initial_rows - len(df)
        self.metrics['products'] = {
            'raw_rows': initial_rows,
            'cleaned_rows': len(df),
            'rows_dropped': rows_dropped,
            'issues_found': issues_found
        }
        
        return CleaningResult(df, rows_dropped, issues_found, True)

    def clean_orders(self, customers_df: pd.DataFrame) -> CleaningResult:
        self.logger.info("Cleaning orders.csv...")
        df = pd.read_csv(self.raw_path / 'orders.csv')
        initial_rows = len(df)
        issues_found = {'duplicate_ids': 0, 'future_dates': 0, 'null_customer_id': 0, 'invalid_status': 0, 'invalid_region': 0, 'referential_violations': 0}
        
        df = df.drop_duplicates(subset=['order_id'], keep='first')
        issues_found['duplicate_ids'] = initial_rows - len(df)
        
        null_cust = df['customer_id'].isna()
        issues_found['null_customer_id'] = int(null_cust.sum())
        df = df[~null_cust]
        
        valid_customers = set(customers_df['customer_id'])
        ref_viol = ~df['customer_id'].isin(valid_customers)
        issues_found['referential_violations'] = int(ref_viol.sum())
        df = df[~ref_viol]
        
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
        future_dates = df['order_date'] > pd.Timestamp.utcnow().tz_localize(None)
        issues_found['future_dates'] = int(future_dates.sum())
        df = df[~future_dates & df['order_date'].notna()]
        df['order_date'] = df['order_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        valid_status = ['PLACED', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED']
        invalid_status = ~df['status'].isin(valid_status)
        issues_found['invalid_status'] = int(invalid_status.sum())
        df = df[~invalid_status]
        
        valid_regions = ['US-EAST', 'US-WEST', 'EU', 'APAC', 'UNKNOWN']
        df['region_code'] = df['region_code'].fillna('UNKNOWN')
        invalid_region = ~df['region_code'].isin(valid_regions)
        issues_found['invalid_region'] = int(invalid_region.sum())
        df = df[~invalid_region]
        
        df['customer_id'] = df['customer_id'].astype(int)
        
        rows_dropped = initial_rows - len(df)
        self.metrics['orders'] = {
            'raw_rows': initial_rows,
            'cleaned_rows': len(df),
            'rows_dropped': rows_dropped,
            'issues_found': issues_found
        }
        
        return CleaningResult(df, rows_dropped, issues_found, True)

    def clean_order_items(self, orders_df: pd.DataFrame, products_df: pd.DataFrame) -> CleaningResult:
        self.logger.info("Cleaning order_items.csv...")
        df = pd.read_csv(self.raw_path / 'order_items.csv')
        initial_rows = len(df)
        issues_found = {'invalid_quantity': 0, 'invalid_price': 0, 'invalid_discount': 0, 'referential_violations': 0, 'duplicate_ids': 0}
        
        df = df.drop_duplicates(subset=['item_id'], keep='first')
        issues_found['duplicate_ids'] = initial_rows - len(df)
        
        invalid_qty = (df['quantity'].isna()) | (df['quantity'] <= 0)
        issues_found['invalid_quantity'] = int(invalid_qty.sum())
        df = df[~invalid_qty]
        
        invalid_price = (df['unit_price'].isna()) | (df['unit_price'] <= 0)
        issues_found['invalid_price'] = int(invalid_price.sum())
        df = df[~invalid_price]
        
        invalid_discount = (df['discount_percent'] < 0) | (df['discount_percent'] > 100)
        issues_found['invalid_discount'] = int(invalid_discount.sum())
        df.loc[df['discount_percent'] > 100, 'discount_percent'] = 100
        df.loc[df['discount_percent'] < 0, 'discount_percent'] = 0
        
        valid_orders = set(orders_df['order_id'])
        valid_products = set(products_df['product_id'])
        
        ref_viol = (~df['order_id'].isin(valid_orders)) | (~df['product_id'].isin(valid_products))
        issues_found['referential_violations'] = int(ref_viol.sum())
        df = df[~ref_viol]
        
        df['quantity'] = df['quantity'].astype(int)
        
        rows_dropped = initial_rows - len(df)
        self.metrics['order_items'] = {
            'raw_rows': initial_rows,
            'cleaned_rows': len(df),
            'rows_dropped': rows_dropped,
            'issues_found': issues_found
        }
        
        return CleaningResult(df, rows_dropped, issues_found, True)

    def generate_quality_report(self, output_path: Path, start_time: float) -> None:
        duration = time.time() - start_time
        
        total_initial = sum(m['raw_rows'] for m in self.metrics.values())
        total_dropped = sum(m['rows_dropped'] for m in self.metrics.values())
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "datasets": self.metrics,
            "referential_integrity": {
                "valid_relationships": self.metrics['order_items']['cleaned_rows'],
                "violations": self.metrics['order_items']['issues_found']['referential_violations'],
                "pass": self.metrics['order_items']['issues_found']['referential_violations'] == 0
            },
            "data_loss_percent": round((total_dropped / total_initial) * 100, 2) if total_initial > 0 else 0,
            "cleaning_duration_seconds": round(duration, 2)
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=4)
        
        self.logger.info(f"Quality report generated at {output_path}")

def run_cleaning_pipeline(raw_dir: Path, clean_dir: Path, report_dir: Path) -> None:
    start_time = time.time()
    cleaner = DataCleaner(raw_dir)
    
    customers_res = cleaner.clean_customers()
    customers_res.cleaned_df.to_csv(clean_dir / 'customers_clean.csv', index=False)
    
    products_res = cleaner.clean_products()
    products_res.cleaned_df.to_csv(clean_dir / 'products_clean.csv', index=False)
    
    orders_res = cleaner.clean_orders(customers_res.cleaned_df)
    orders_res.cleaned_df.to_csv(clean_dir / 'orders_clean.csv', index=False)
    
    order_items_res = cleaner.clean_order_items(orders_res.cleaned_df, products_res.cleaned_df)
    order_items_res.cleaned_df.to_csv(clean_dir / 'order_items_clean.csv', index=False)
    
    cleaner.generate_quality_report(report_dir / 'data_quality_report.json', start_time)
