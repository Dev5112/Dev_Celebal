from src.data_cleaning.validators import is_valid_email, is_valid_date
from src.data_cleaning.cleaner import DataCleaner
from pathlib import Path
import pandas as pd

def test_email_validation():
    assert is_valid_email("test@example.com")
    assert not is_valid_email("test@.com")
    assert not is_valid_email("invalid-email")

def test_date_validation():
    assert is_valid_date("2023-01-01 12:00:00")
    # Using a future date
    assert not is_valid_date("2100-01-01")

def test_cleaner_integration():
    if Path("data/raw/customers.csv").exists():
        cleaner = DataCleaner(Path("data/raw"))
        res = cleaner.clean_customers()
        assert res.validation_passed
        assert res.rows_dropped >= 0
