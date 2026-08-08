# E-Commerce Order Analytics System

Build a production-grade, end-to-end data analytics pipeline demonstrating enterprise-level data engineering practices. This system ingests messy e-commerce data, applies rigorous data cleaning and validation, stores normalized data in a relational database, performs sophisticated SQL analytics, and exposes insights via a CLI reporting tool.

## Architecture & Data Flow

```text
  CSV Generation (Faker/Pandas)
        │
        ▼
  Data Cleaning & Validation (Regex/Pandas) ─► Data Quality Reports
        │
        ▼
  SQLite Database Load (Referential Integrity Check)
        │
        ▼
  SQL Analytics (CTEs, Window Functions, Group By)
        │
        ▼
  CLI Reporting Tool (Argparse, Tabulate) ─► CSV/JSON/Table Output
```

## Quick Start

1. Install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```
2. Run the entire ETL pipeline (Generation, Cleaning, DB Load):
   ```bash
   chmod +x scripts/run_pipeline.sh
   ./scripts/run_pipeline.sh
   ```
3. Generate a CLI report:
   ```bash
   python report_cli.py --report health_check
   python report_cli.py --report top_customers --limit 5
   python report_cli.py --report revenue
   ```

## Documentation
- [Architecture Guide](docs/architecture.md)
- [Data Dictionary](docs/data_dictionary.md)
- [SQL Guide](docs/sql_guide.md)

## Key Concepts Demonstrated
- Data generation with intentional quality issues using `Faker`.
- Robust data cleaning strategies for missing values, referential violations, and invalid formats.
- SQLite schema design with foreign key constraints, check constraints, and indexing.
- Advanced SQL Analytics: Window Functions, CTEs, Cohort Retention, RFM Segmentation, Market Basket Analysis.
- CLI application design with multiple output formats and error handling.
- Unit Testing using `pytest` and `pytest-cov`.
