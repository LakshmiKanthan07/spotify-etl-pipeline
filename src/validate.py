import pandas as pd
import os

def check_nulls(df, critical_cols):
    """Checks for null values in critical columns. Returns (failed_df, report_str)."""
    failed_rows = df[df[critical_cols].isnull().any(axis=1)]
    report = []
    if not failed_rows.empty:
        report.append(f"Null values found in critical columns {critical_cols}: {len(failed_rows)} rows.")
    return failed_rows, "\n".join(report)

def check_duplicates(df, key_col):
    """Checks for duplicate records based on primary key. Returns (failed_df, report_str)."""
    failed_rows = df[df.duplicated(subset=[key_col], keep=False)]
    report = []
    if not failed_rows.empty:
        report.append(f"Duplicates found for key column '{key_col}': {df.duplicated(subset=[key_col]).sum()} duplicate records.")
    return failed_rows, "\n".join(report)

def validate_ranges(df, col, min_val, max_val):
    """Checks if numeric column values are within a specific range. Returns (failed_df, report_str)."""
    if col not in df.columns:
        return pd.DataFrame(), ""
    # Filter non-null rows that are out of bounds
    out_of_bounds = df[df[col].notnull() & ((df[col] < min_val) | (df[col] > max_val))]
    report = []
    if not out_of_bounds.empty:
        report.append(f"Out of bounds values for '{col}' (expected {min_val} to {max_val}): {len(out_of_bounds)} rows.")
    return out_of_bounds, "\n".join(report)

def generate_report(results_dict, filepath):
    """Generates a text report of all validation checks and writes it to file."""
    dir_name = os.path.dirname(filepath)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
        
    passed = True
    report_lines = ["=== DATA VALIDATION REPORT ===", ""]
    
    for check_name, (failed_df, report_str) in results_dict.items():
        if report_str:
            passed = False
            report_lines.append(f"[FAIL] {check_name}:")
            report_lines.append(report_str)
            # Log sample of failed rows
            report_lines.append(f"Sample failed rows:\n{failed_df.head(5).to_string()}\n")
        else:
            report_lines.append(f"[PASS] {check_name}")
            
    report_lines.append("")
    if passed:
        report_lines.append("OVERALL STATUS: PASSED")
    else:
        report_lines.append("OVERALL STATUS: FAILED")
        
    full_report = "\n".join(report_lines)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_report)
        
    return passed
