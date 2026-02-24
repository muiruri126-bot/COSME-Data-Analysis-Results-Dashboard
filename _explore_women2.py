"""Deep exploration of Women Survey Excel — dump all non-null cells with row/col."""
import pandas as pd

fp = "Women Survey Basline_midline results.xlsx"
raw = pd.read_excel(fp, sheet_name="Results Women", header=None)
print(f"Shape: {raw.shape}\n")

# Print every row that has section headings or labels (col 1 or col 10)
# We'll print col 0, 1, 2, 3, 10, 11, 12 for every row that has a non-null in col 1 or col 10
print(f"{'Row':>4}  {'Col0':>20}  {'Col1':>55}  {'Col2':>12}  {'Col3':>12}  {'Col10':>55}  {'Col11':>12}  {'Col12':>12}")
print("-" * 220)

for r in range(raw.shape[0]):
    c0 = raw.iloc[r, 0] if pd.notna(raw.iloc[r, 0]) else ""
    c1 = raw.iloc[r, 1] if pd.notna(raw.iloc[r, 1]) else ""
    c2 = raw.iloc[r, 2] if pd.notna(raw.iloc[r, 2]) else ""
    c3 = raw.iloc[r, 3] if pd.notna(raw.iloc[r, 3]) else ""
    c10 = raw.iloc[r, 10] if raw.shape[1] > 10 and pd.notna(raw.iloc[r, 10]) else ""
    c11 = raw.iloc[r, 11] if raw.shape[1] > 11 and pd.notna(raw.iloc[r, 11]) else ""
    c12 = raw.iloc[r, 12] if raw.shape[1] > 12 and pd.notna(raw.iloc[r, 12]) else ""
    
    if c0 or c1 or c10:
        # Truncate for readability
        c0s = str(c0)[:20]
        c1s = str(c1)[:55]
        c2s = str(c2)[:12]
        c3s = str(c3)[:12]
        c10s = str(c10)[:55]
        c11s = str(c11)[:12]
        c12s = str(c12)[:12]
        print(f"{r:4d}  {c0s:>20}  {c1s:>55}  {c2s:>12}  {c3s:>12}  {c10s:>55}  {c11s:>12}  {c12s:>12}")
