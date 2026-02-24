"""Explore the Women Survey Excel file structure."""
import pandas as pd
import sys

fp = "Women Survey Basline_midline results.xlsx"
xls = pd.ExcelFile(fp)
print("Sheet names:", xls.sheet_names)

for sn in xls.sheet_names:
    raw = pd.read_excel(fp, sheet_name=sn, header=None)
    print(f"\n{'='*80}")
    print(f"Sheet: {sn!r}  shape={raw.shape}")
    print(f"{'='*80}")
    # Print first 20 rows to see headers / structure
    print(raw.head(20).to_string())
    print(f"\n--- Columns (by index) ---")
    for c in range(raw.shape[1]):
        non_null = raw.iloc[:, c].dropna()
        if len(non_null) > 0:
            print(f"  Col {c}: first non-null at row {non_null.index[0]}: {non_null.iloc[0]!r}")
