import re
import pandas as pd
from datetime import datetime

def is_valid_email(email: str) -> bool:
    """Validates an email address format."""
    if pd.isna(email):
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, str(email)))

def is_valid_date(date_str: str) -> bool:
    """Validates that a date is valid and not in the future."""
    try:
        dt = pd.to_datetime(date_str)
        if pd.isna(dt):
            return False
        if dt > pd.Timestamp.now():
            return False
        return True
    except Exception:
        return False
