# Architecture Guide

The E-Commerce Order Analytics System is designed around several modular phases.

## 1. Data Generation (`src/data_generation/`)
- **`faker_config.py`**: Custom Faker providers for e-commerce specific domains (categories, order status).
- **`generator.py`**: Classes to create realistic datasets for `customers`, `products`, `orders`, and `order_items` with dynamically injected data quality issues (e.g., duplicated IDs, invalid emails, negative prices).

## 2. Data Cleaning (`src/data_cleaning/`)
- **`validators.py`**: Reusable regex validation functions (email parsing, timestamp bounds checking).
- **`cleaner.py`**: Sequential pandas operations dropping invalid rows, imputing missing categories, fixing whitespace issues, and enforcing referential integrity.
- **Reporting**: Collects dropped row metrics and generates `data_quality_report.json`.

## 3. Database Layer (`src/database/` & `sql/`)
- **Schema & Constraints**: Strict SQLite constraints applied via `00_schema.sql` (PRIMARY KEYs, CHECKs for numerics) and `01_constraints.sql` (indexes).
- **Connection Management**: A context manager in `connection.py` reliably ensures transactions are committed or rolled back and explicitly enables `PRAGMA foreign_keys = ON`.
- **Loader**: Loads pandas DataFrames sequentially using `.to_sql(if_exists='append')`. 

## 4. Analytics Engine (`src/analytics/`)
- **Executor**: Connects `report_cli.py` to the saved SQL queries by parsing the `.sql` files on disk, injecting filters/limits, and executing using pandas `read_sql_query`.
- **Models**: Defines supported `ReportType` enums mapping reports to their underlying SQL script and index.
