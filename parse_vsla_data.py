"""Parse VSLA Functionality Excel into vsla-indicators.json for the React dashboard."""
import pandas as pd
import json, sys, os

EXCEL_PATH = r"My Project\My work\VSLA Functionality_(Q1-Q4) 2025.xlsx"
OUTPUT_PATH = r"vsla-dashboard\public\data\vsla-indicators.json"

df = pd.read_excel(EXCEL_PATH, sheet_name="Results (Across Qs)", header=None)

def cell(row, col):
    """Get cell value (1-based row/col like the inspection output)."""
    v = df.iloc[row - 1, col - 1]
    if pd.isna(v):
        return None
    if isinstance(v, float) and v == int(v) and abs(v) < 1e12:
        return int(v)
    return v

def read_county_quarter(start_row):
    """Read a simple county x quarter table (3 cols: Q2, Q3, Q4)."""
    rows = []
    for r in range(start_row, start_row + 3):
        rows.append({
            "county": str(cell(r, 2)),
            "Q2": cell(r, 3),
            "Q3": cell(r, 4),
            "Q4": cell(r, 5),
        })
    return rows

def read_sumavg_table(header_row):
    """Read a county table with Sum/Avg for Q2, Q3, Q4 (starts at header_row+1)."""
    rows = []
    for r in range(header_row + 1, header_row + 4):
        rows.append({
            "county": str(cell(r, 2)),
            "Q2": {"sum": cell(r, 3), "average": cell(r, 4)},
            "Q3": {"sum": cell(r, 5), "average": cell(r, 6)},
            "Q4": {"sum": cell(r, 7), "average": cell(r, 8)},
        })
    return rows

def read_band_table(start_row, end_row):
    """Read a band distribution table."""
    bands = []
    for r in range(start_row, end_row + 1):
        bands.append({
            "band": str(cell(r, 2)),
            "Q2": cell(r, 3),
            "Q3": cell(r, 4),
            "Q4": cell(r, 5),
        })
    return bands

# ═══ Build the full dataset ═══
dataset = {
    "meta": {
        "title": str(cell(2, 2)),
        "date": str(cell(3, 2)),
        "outcome": str(cell(4, 2)),
    },

    # A.1 VSLAs Assessed (R8-R10)
    "vslasAssessed": read_county_quarter(8),

    # A.2 Membership
    "membership": {
        "female": read_sumavg_table(15),    # R16-R18
        "male": read_sumavg_table(21),      # R22-R24
        "all": read_sumavg_table(27),       # R28-R30
    },

    # A.3 Members Left (R34-R36)
    "membersLeft": read_county_quarter(34),

    # A.4 % Left bands (R40-R46)
    "percentLeftBands": read_band_table(40, 46),

    # A.5-6 Meetings & Attendance
    "meetings": {
        "frequency": read_county_quarter(50),   # R50-R52
        "attendance": read_county_quarter(56),   # R56-R58
    },

    # B. SAVINGS
    "savings": {
        "membersSaving": read_sumavg_table(65),       # R66-R68
        "proportionBands": read_band_table(72, 76),    # R72-R76
        "value": read_sumavg_table(80),                # R81-R83
        "valueBands": read_band_table(87, 91),         # R87-R91
    },

    # C. SOCIAL FUND
    "socialFund": {
        "percentageWithFund": read_county_quarter(97),  # R97-R99
        "value": read_sumavg_table(103),                # R104-R106
        "valueBands": read_band_table(110, 115),        # R110-R115
    },

    # D. LOANS
    "loans": {
        "disbursed": {
            "count": read_sumavg_table(122),             # R123-R125
            "countBands": read_band_table(129, 135),     # R129-R135
            "value": read_sumavg_table(139),             # R140-R142
            "valueBands": read_band_table(146, 151),     # R146-R151
        },
        "repaid": {
            "count": read_sumavg_table(155),             # R156-R158
            "countBands": read_band_table(162, 166),     # R162-R166
            "value": read_sumavg_table(170),             # R171-R173
            "valueBands": read_band_table(177, 182),     # R177-R182
        },
        "interest": {
            "value": read_sumavg_table(186),             # R187-R189
            "valueBands": read_band_table(193, 197),     # R193-R197
        },
        "behaviour": [],
        "failingToPay": read_county_quarter(208),        # R208-R210
        "useDistribution": read_band_table(214, 218),    # R214-R218
    },
}

# D.11 Loan behaviour (special layout: 3 metrics x 3 quarters across cols)
for r in range(202, 205):
    dataset["loans"]["behaviour"].append({
        "county": str(cell(r, 2)),
        "avgProportionRepaid": {"Q2": cell(r, 3), "Q3": cell(r, 4), "Q4": cell(r, 5)},
        "avgValueRepaid": {"Q2": cell(r, 6), "Q3": cell(r, 7), "Q4": cell(r, 8)},
        "avgROI": {"Q2": cell(r, 9), "Q3": cell(r, 10), "Q4": cell(r, 11)},
    })

# Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=2, ensure_ascii=False)

print(f"✓ Wrote {OUTPUT_PATH}")
print(f"  VSLAs assessed: {[r['Q2'] for r in dataset['vslasAssessed']]}")
print(f"  Total savings Q2: {dataset['savings']['value'][2]['Q2']['sum']:,} KES")
print(f"  Total loans disbursed Q2: {dataset['loans']['disbursed']['value'][2]['Q2']['sum']:,} KES")
print(f"  Loan uses: {[u['band'] for u in dataset['loans']['useDistribution']]}")
