import pandas as pd
import numpy as np
import random
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timedelta
from .faker_config import get_faker

class DataGenerator:
    def __init__(self, seed: int = 42):
        self.fake = get_faker(seed)
        np.random.seed(seed)
        self.quality_metrics: Dict[str, int] = {
            'invalid_emails': 0,
            'duplicate_records': 0,
            'null_values': 0,
            'referential_violations': 0
        }
        self.logger = logging.getLogger(__name__)

    def generate_customers(self, count: int = 500) -> pd.DataFrame:
        self.logger.info(f"Generating {count} customers...")
        data: List[Dict[str, Any]] = []
        for i in range(1, count + 1):
            name = self.fake.name()
            # 3% mixed case in names? The spec says mixed case in customer_name, let's just make 3% lowercase or uppercase
            if random.random() < 0.03:
                name = name.lower() if random.random() < 0.5 else name.upper()

            email = self.fake.email()
            # 2% invalid email formats
            if random.random() < 0.02:
                email = email.replace('@', '') if random.random() < 0.5 else f"{email.split('@')[0]}@.com"
                self.quality_metrics['invalid_emails'] += 1

            reg_date = self.fake.date_time_between(start_date="-2y", end_date="-1d")
            # 3% NULL registration dates
            reg_date_val = reg_date.strftime("%Y-%m-%d %H:%M:%S")
            if random.random() < 0.03:
                reg_date_val = None
                self.quality_metrics['null_values'] += 1

            data.append({
                'customer_id': i,
                'customer_name': name,
                'email': email,
                'registration_date': reg_date_val,
                'customer_type': self.fake.customer_type()
            })

        df = pd.DataFrame(data)
        
        # 1% duplicate customer_ids
        num_duplicates = max(1, int(count * 0.01))
        dup_indices = np.random.choice(df.index, num_duplicates, replace=False)
        duplicates = df.loc[dup_indices].copy()
        df = pd.concat([df, duplicates], ignore_index=True)
        self.quality_metrics['duplicate_records'] += num_duplicates
        
        return df

    def generate_products(self, count: int = 100) -> pd.DataFrame:
        self.logger.info(f"Generating {count} products...")
        data: List[Dict[str, Any]] = []
        for i in range(1, count + 1):
            category = self.fake.product_category()
            subcategory = self.fake.product_subcategory(category)
            
            # 2% NULL subcategory
            if random.random() < 0.02:
                subcategory = None
                self.quality_metrics['null_values'] += 1
                
            name = f"{category} {self.fake.word()}"
            # 3% mixed case
            if random.random() < 0.03:
                name = name.upper() if random.random() < 0.5 else name.lower()
            # 4% extra whitespace
            if random.random() < 0.04:
                name = f"  {name}  "

            cost_price = round(random.uniform(10, 500), 2)
            
            data.append({
                'product_id': i,
                'product_name': name,
                'category': category,
                'subcategory': subcategory,
                'cost_price': cost_price
            })

        df = pd.DataFrame(data)
        
        # 1% duplicate product_ids
        num_duplicates = max(1, int(count * 0.01))
        dup_indices = np.random.choice(df.index, num_duplicates, replace=False)
        duplicates = df.loc[dup_indices].copy()
        df = pd.concat([df, duplicates], ignore_index=True)
        self.quality_metrics['duplicate_records'] += num_duplicates
        
        return df

    def generate_orders(self, count: int = 1000, customers_df: pd.DataFrame = None) -> pd.DataFrame:
        self.logger.info(f"Generating {count} orders...")
        data: List[Dict[str, Any]] = []
        valid_customer_ids = customers_df['customer_id'].dropna().unique().tolist() if customers_df is not None else list(range(1, 501))
        
        for i in range(1, count + 1):
            customer_id = random.choice(valid_customer_ids)
            
            # 5% NULL customer_id
            if random.random() < 0.05:
                customer_id = None
                self.quality_metrics['null_values'] += 1
            # 3% invalid customer_id (referential violation)
            elif random.random() < 0.03:
                customer_id = max(valid_customer_ids) + 1000 + i
                self.quality_metrics['referential_violations'] += 1
                
            order_date = self.fake.date_time_between(start_date="-2y", end_date="-1d")
            # 2% future order dates
            if random.random() < 0.02:
                order_date = datetime.utcnow() + timedelta(days=random.randint(1, 30))
            
            # 8% date format inconsistencies
            date_formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"]
            fmt = date_formats[0]
            if random.random() < 0.08:
                fmt = random.choice(date_formats[1:])
            order_date_str = order_date.strftime(fmt)

            region = self.fake.region_code()
            # 2% NULL region_code
            if random.random() < 0.02:
                region = None
                self.quality_metrics['null_values'] += 1

            data.append({
                'order_id': i,
                'customer_id': customer_id,
                'order_date': order_date_str,
                'status': self.fake.order_status(),
                'region_code': region
            })

        df = pd.DataFrame(data)
        
        # 2% duplicate order_ids
        num_duplicates = max(1, int(count * 0.02))
        dup_indices = np.random.choice(df.index, num_duplicates, replace=False)
        duplicates = df.loc[dup_indices].copy()
        df = pd.concat([df, duplicates], ignore_index=True)
        self.quality_metrics['duplicate_records'] += num_duplicates
        
        return df

    def generate_order_items(self, count: int = 2000, orders_df: pd.DataFrame = None, products_df: pd.DataFrame = None) -> pd.DataFrame:
        self.logger.info(f"Generating {count} order items...")
        data: List[Dict[str, Any]] = []
        
        valid_order_ids = orders_df['order_id'].dropna().unique().tolist() if orders_df is not None else list(range(1, 1001))
        valid_product_ids = products_df['product_id'].dropna().unique().tolist() if products_df is not None else list(range(1, 101))
        product_prices = dict(zip(products_df['product_id'], products_df['cost_price'])) if products_df is not None else {}
        
        for i in range(1, count + 1):
            order_id = random.choice(valid_order_ids)
            # 5% invalid order_id
            if random.random() < 0.05:
                order_id = max(valid_order_ids) + 1000 + i
                self.quality_metrics['referential_violations'] += 1
                
            product_id = random.choice(valid_product_ids)
            # 2% invalid product_id
            if random.random() < 0.02:
                product_id = max(valid_product_ids) + 1000 + i
                self.quality_metrics['referential_violations'] += 1
                
            qty = random.randint(1, 10)
            # 3% negative qty, 2% qty=0
            rand_val = random.random()
            if rand_val < 0.03:
                qty = -qty
            elif rand_val < 0.05:
                qty = 0
                
            base_price = product_prices.get(product_id, round(random.uniform(10, 500), 2))
            unit_price = round(base_price * random.uniform(1.1, 1.5), 2) # selling price markup
            
            discount = round(random.uniform(0, 30), 2)
            # 2% discount > 100 or < 0
            if random.random() < 0.02:
                discount = round(random.choice([random.uniform(-20, -1), random.uniform(101, 150)]), 2)
                
            # 1% NULL values in qty/unit_price
            qty_val = qty
            price_val = unit_price
            if random.random() < 0.01:
                if random.random() < 0.5:
                    qty_val = None
                else:
                    price_val = None
                self.quality_metrics['null_values'] += 1

            data.append({
                'item_id': i,
                'order_id': order_id,
                'product_id': product_id,
                'quantity': qty_val,
                'unit_price': price_val,
                'discount_percent': discount
            })

        return pd.DataFrame(data)

def generate_all_data(output_dir: Path) -> None:
    generator = DataGenerator()
    
    customers = generator.generate_customers(500)
    customers.to_csv(output_dir / 'customers.csv', index=False)
    
    products = generator.generate_products(100)
    products.to_csv(output_dir / 'products.csv', index=False)
    
    orders = generator.generate_orders(1000, customers)
    orders.to_csv(output_dir / 'orders.csv', index=False)
    
    order_items = generator.generate_order_items(2000, orders, products)
    order_items.to_csv(output_dir / 'order_items.csv', index=False)
    
    generator.logger.info(f"Data generation complete. Quality issues injected: {generator.quality_metrics}")
