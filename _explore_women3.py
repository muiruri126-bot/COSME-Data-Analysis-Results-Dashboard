"""Explore rows 20-92 and other column structures in detail."""
import pandas as pd

fp = "Women Survey Basline_midline results.xlsx"
raw = pd.read_excel(fp, sheet_name="Results Women", header=None)

# Print rows 20-92 with all columns that have data
print("=== ROWS 20-92 (HH Characteristics continued + Shocks) ===\n")
for r in range(20, 93):
    parts = []
    for c in range(min(raw.shape[1], 21)):
        v = raw.iloc[r, c]
        if pd.notna(v):
            parts.append(f"c{c}={v!r}")
    if parts:
        print(f"Row {r:3d}: {' | '.join(parts)}")

# Also check the assets ownership columns (cols 13-20) around rows 127-174
print("\n\n=== ROWS 127-175 COLS 4-20 (Assets ownership structure) ===\n")
for r in range(127, 176):
    parts = []
    for c in range(4, 21):
        v = raw.iloc[r, c]
        if pd.notna(v):
            parts.append(f"c{c}={v!r}")
    if parts:
        print(f"Row {r:3d}: {' | '.join(parts)}")

# Check rows 150-175 for use/sell + inputs
print("\n\n=== ROWS 150-190 COLS 4-20 ===\n")
for r in range(150, 191):
    parts = []
    for c in range(4, 21):
        v = raw.iloc[r, c]
        if pd.notna(v):
            parts.append(f"c{c}={v!r}")
    if parts:
        print(f"Row {r:3d}: {' | '.join(parts)}")
