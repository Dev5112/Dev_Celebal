#!/usr/bin/env bash
set -e

echo "Starting E-Commerce Analytics Pipeline"

# Generate Data
echo "Generating raw data..."
.venv/bin/python3 -c "
import sys
from pathlib import Path
sys.path.append('.')
from src.data_generation.generator import generate_all_data
generate_all_data(Path('data/raw'))
"

# Clean Data
echo "Cleaning data..."
.venv/bin/python3 -c "
import sys
from pathlib import Path
sys.path.append('.')
from src.data_cleaning.cleaner import run_cleaning_pipeline
run_cleaning_pipeline(Path('data/raw'), Path('data/cleaned'), Path('data/reports'))
"

# Setup Database
echo "Setting up database..."
.venv/bin/python3 -c "
import sys
from pathlib import Path
sys.path.append('.')
from src.database.loader import setup_database
stats = setup_database(Path('database/ecommerce.db'), Path('sql'), Path('data/cleaned'))
print(stats)
"

echo "Phase 1, 2, and 3 complete!"
