import pandas as pd
from src.data_generation.generator import DataGenerator

def test_customer_generation_volume():
    gen = DataGenerator(seed=42)
    df = gen.generate_customers(100)
    assert len(df) > 100 # duplicates injected
    assert 'email' in df.columns

def test_quality_issues_injected():
    gen = DataGenerator(seed=42)
    gen.generate_customers(100)
    assert gen.quality_metrics['invalid_emails'] >= 0
