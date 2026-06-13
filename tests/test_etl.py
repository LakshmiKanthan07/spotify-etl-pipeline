import pandas as pd
import numpy as np
from unittest.mock import patch
from src.validate import check_nulls, check_duplicates, validate_ranges
from src.transform import extract_year_month

# 1. Validation Layer Tests
def test_check_nulls():
    df = pd.DataFrame({
        "id": [1, 2, None],
        "name": ["A", "B", "C"]
    })
    # 'id' has a null, should fail
    failed_df, report = check_nulls(df, ["id"])
    assert len(failed_df) == 1
    assert "Null values found in critical columns" in report
    
    # 'name' has no null, should pass
    failed_df_pass, report_pass = check_nulls(df, ["name"])
    assert len(failed_df_pass) == 0
    assert report_pass == ""

def test_check_duplicates():
    df = pd.DataFrame({
        "id": [1, 2, 2],
        "name": ["A", "B", "C"]
    })
    # 'id' has duplicate values
    failed_df, report = check_duplicates(df, "id")
    assert len(failed_df) == 2  # both duplicate rows returned
    assert "Duplicates found for key column" in report

def test_validate_ranges():
    df = pd.DataFrame({
        "popularity": [10, 50, 110, -5]
    })
    # 110 and -5 are out of range [0, 100]
    failed_df, report = validate_ranges(df, "popularity", 0, 100)
    assert len(failed_df) == 2
    assert "Out of bounds values" in report

# 2. Transformation Layer Helper Tests
def test_extract_year_month():
    # Full date YYYY-MM-DD
    year, month = extract_year_month("2020-05-15")
    assert year == 2020
    assert month == 5
    
    # Year-Month YYYY-MM
    year, month = extract_year_month("2018-11")
    assert year == 2018
    assert month == 11
    
    # Year only YYYY
    year, month = extract_year_month("1995")
    assert year == 1995
    assert month == 1
    
    # Invalid date format
    year, month = extract_year_month(None)
    assert year == 1900
    assert month == 1
