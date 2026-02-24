"""Fix leading spaces and enhance CSS visibility in forestry_dashboard.py"""
import re

filepath = 'forestry_dashboard.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================================
# 1) Fix theme keys - strip leading spaces
# ============================================================================
replacements = [
    # Theme dictionary keys
    ('"\\s+Forest Green"', '"Forest Green"'),
    ('"\\s+Ocean Blue"', '"Ocean Blue"'),
    ('"\\s+Sunset"', '"Sunset"'),
    ('"\\s+Earth Tones"', '"Earth Tones"'),
    ('"\\s+Professional"', '"Professional"'),
    
    # Dataset radio options and comparisons
    ('"\\s+Dataset View"', '"Dataset View"'),
    ('"\\s+Combined Overview"', '"Combined Overview"'),
    ('"\\s+Forestry Groups"', '"Forestry Groups"'),
    ('"\\s+Women Survey"', '"Women Survey"'),
    ('"\\s+Show Change \\(pp\\) Charts"', '"Show Change (pp) Charts"'),
    ('"\\s+Dashboard Theme"', '"Dashboard Theme"'),
    
    # Forestry tab labels
    ('"\\s+Overview"', '"Overview"'),
    ('"\\s+Group Characteristics"', '"Group Characteristics"'),
    ('"\\s+Governance & Gender"', '"Governance & Gender"'),
    ('"\\s+Training & Assets"', '"Training & Assets"'),
    ('"\\s+Forest Condition & Threats"', '"Forest Condition & Threats"'),
    ('"\\s+Income & Agroforestry"', '"Income & Agroforestry"'),
    
    # Women tab labels
    ('"\\s+Household Profile & Services"', '"Household Profile & Services"'),
    ('"\\s+Shocks, Coping & Preparedness"', '"Shocks, Coping & Preparedness"'),
    ('"\\s+Assets, Land, Savings & Loans"', '"Assets, Land, Savings & Loans"'),
    ('"\\s+Roles, Time Use & Decisions"', '"Roles, Time Use & Decisions"'),
    ('"\\s+Climate Change & NbS"', '"Climate Change & NbS"'),
    ('"\\s+Life Skills & Social Norms"', '"Life Skills & Social Norms"'),
    
    # Score Statistics subheader
    ('"\\s+Score Statistics"', '"Score Statistics"'),
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# Also fix st.error messages with leading space
content = re.sub(r'st\.error\(f"\s+', 'st.error(f"', content)

# ============================================================================
# 2) Enhanced CSS for much better visibility
# ============================================================================

old_css = """    /* ---------- HEADER ---------- */
    .main-header {{
        background: {COLORS['header_gradient']};
        color: white; padding: 1.8rem 2.5rem; border-radius: 14px;
        margin-bottom: 1.8rem; text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        position: relative; overflow: hidden;
    }}
    .main-header::before {{
        content: ''; position: absolute; top: -50%; left: -50%;
        width: 200%; height: 200%; background:
            radial-gradient(circle at 20% 50%, rgba(255,255,255,0.08) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255,255,255,0.05) 0%, transparent 40%);
        pointer-events: none;
    }}
    .main-header h1 {{ margin: 0; font-size: 2.2rem; font-weight: 700; letter-spacing: -0.02em;
        text-shadow: 0 2px 4px rgba(0,0,0,0.15); position: relative; }}
    .main-header p {{ margin: 0.4rem 0 0; opacity: 0.92; font-size: 1.05rem; position: relative; }}

    /* ---------- KPI CARDS ---------- */
    .kpi-card {{
        background: white; border-radius: 12px; padding: 1.3rem 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07); text-align: center;
        border-left: 5px solid {COLORS['card_border']};
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 0.8rem;
    }}
    .kpi-card:hover {{ transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,0.12); }}
    .kpi-card h3 {{ font-size: 0.78rem; color: #888; margin: 0 0 0.4rem;
        text-transform: uppercase; letter-spacing: 0.04em; font-weight: 600; }}
    .kpi-card .value {{ font-size: 2rem; font-weight: 800; color: {COLORS['card_value']};
        line-height: 1.1; }}
    .delta-positive {{ color: {COLORS['good']}; font-weight: 600; font-size: 0.85rem; margin-top: 0.2rem; }}
    .delta-negative {{ color: {COLORS['danger']}; font-weight: 600; font-size: 0.85rem; margin-top: 0.2rem; }}

    /* ---------- SECTION NARRATIVE ---------- */
    .section-narrative {{
        background: {COLORS['narrative_bg']};
        border-left: 5px solid {COLORS['narrative_border']};
        padding: 1rem 1.4rem; border-radius: 0 10px 10px 0;
        margin-bottom: 1.2rem; font-size: 0.95rem;
        color: {COLORS['narrative_text']};
        box-shadow: 0 1px 6px rgba(0,0,0,0.04);
    }}

    /* ---------- BREADCRUMB / NAV BAR ---------- */
    .nav-breadcrumb {{
        display: flex; align-items: center; gap: 0.5rem;
        padding: 0.6rem 1rem; background: rgba(0,0,0,0.03);
        border-radius: 8px; margin-bottom: 1rem;
        font-size: 0.88rem; color: #555;
        border: 1px solid rgba(0,0,0,0.06);
    }}
    .nav-breadcrumb .sep {{ color: #bbb; }}
    .nav-breadcrumb .active {{ font-weight: 700; color: {COLORS['card_value']}; }}

    /* ---------- QUICK NAV PILLS ---------- */
    .quick-nav {{
        display: flex; flex-wrap: wrap; gap: 0.4rem;
        margin-bottom: 1rem;
    }}
    .quick-nav-pill {{
        display: inline-block; padding: 0.35rem 0.9rem;
        background: {COLORS['narrative_bg']}; border: 1px solid {COLORS['narrative_border']};
        border-radius: 20px; font-size: 0.8rem; color: {COLORS['narrative_text']};
        cursor: pointer; transition: all 0.2s ease; text-decoration: none;
    }}
    .quick-nav-pill:hover {{ background: {COLORS['card_border']}; color: white; }}

    /* ---------- SECTION HEADER ---------- */
    .section-header {{
        display: flex; align-items: center; gap: 0.6rem;
        padding: 0.6rem 0; margin: 1rem 0 0.5rem;
        border-bottom: 2px solid {COLORS['card_border']};
    }}
    .section-header h2 {{ margin: 0; font-size: 1.3rem; color: {COLORS['card_value']}; }}
    .section-header .badge {{
        background: {COLORS['card_border']}; color: white;
        padding: 0.15rem 0.6rem; border-radius: 10px;
        font-size: 0.7rem; font-weight: 600;
    }}

    /* ---------- DATA TABLE STYLING ---------- */
    .styled-table {{
        width: 100%; border-collapse: collapse; font-size: 0.88rem;
        border-radius: 8px; overflow: hidden;
        box-shadow: 0 1px 6px rgba(0,0,0,0.06);
    }}
    .styled-table th {{
        background: {COLORS['card_border']}; color: white;
        padding: 0.6rem 0.8rem; text-align: left; font-weight: 600;
    }}
    .styled-table td {{ padding: 0.5rem 0.8rem; border-bottom: 1px solid #eee; }}
    .styled-table tr:hover td {{ background: {COLORS['narrative_bg']}; }}

    /* ---------- EXPANDER STYLING ---------- */
    div[data-testid="stExpander"] {{
        border: 1px solid rgba(0,0,0,0.08); border-radius: 10px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04); margin-bottom: 0.6rem;
    }}

    /* ---------- METRIC STYLING ---------- */
    div[data-testid="stMetricValue"] {{ font-size: 1.5rem; font-weight: 700; }}
    div[data-testid="stMetricDelta"] {{ font-size: 0.85rem; }}

    /* ---------- TAB STYLING ---------- */
    button[data-baseweb="tab"] {{
        font-size: 0.92rem !important; font-weight: 600 !important;
        padding: 0.6rem 1.1rem !important;
    }}
    button[data-baseweb="tab"]:hover {{
        background: {COLORS['narrative_bg']} !important;
    }}

    /* ---------- SIDEBAR STYLING ---------- */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #fafafa 0%, #f0f2f6 100%);
    }}
    section[data-testid="stSidebar"] .block-container {{ padding-top: 1rem; }}
    .sidebar-section {{
        background: white; border-radius: 10px; padding: 0.8rem 1rem;
        margin-bottom: 0.8rem; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        border: 1px solid rgba(0,0,0,0.06);
    }}
    .sidebar-nav-link {{
        display: block; padding: 0.4rem 0.6rem; margin: 0.15rem 0;
        border-radius: 6px; font-size: 0.82rem; color: #444;
        text-decoration: none; transition: all 0.15s ease;
    }}
    .sidebar-nav-link:hover {{ background: {COLORS['narrative_bg']}; color: {COLORS['card_value']}; }}

    /* ---------- FOOTER ---------- */
    .dashboard-footer {{
        text-align: center; color: #999; font-size: 0.82rem;
        padding: 1.5rem 0 0.5rem; border-top: 1px solid #eee;
        margin-top: 1.5rem;
    }}
    .dashboard-footer a {{ color: {COLORS['card_border']}; text-decoration: none; }}

    /* ---------- BACK TO TOP ---------- */
    .back-to-top {{
        position: fixed; bottom: 2rem; right: 2rem;
        background: {COLORS['card_border']}; color: white;
        width: 42px; height: 42px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.2rem; box-shadow: 0 3px 12px rgba(0,0,0,0.2);
        cursor: pointer; z-index: 999; text-decoration: none;
        transition: transform 0.2s ease, opacity 0.2s ease;
        opacity: 0.85;
    }}
    .back-to-top:hover {{ transform: scale(1.1); opacity: 1; }}

    /* ---------- ANIMATIONS ---------- */
    @keyframes fadeInUp {{ from {{ opacity:0; transform:translateY(12px); }} to {{ opacity:1; transform:translateY(0); }} }}
    .stTabs [data-baseweb="tab-panel"] {{ animation: fadeInUp 0.35s ease-out; }}"""

new_css = """    /* ===== GLOBAL TYPOGRAPHY ===== */
    html, body, [class*="css"] {{
        font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
    }}
    .block-container {{
        max-width: 1200px;
        padding: 1rem 2rem 3rem;
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: #1a1a2e !important;
        font-weight: 700 !important;
    }}
    p, li, span, div {{
        line-height: 1.65;
    }}

    /* ===== HEADER ===== */
    .main-header {{
        background: {COLORS['header_gradient']};
        color: white; padding: 2.2rem 3rem; border-radius: 16px;
        margin-bottom: 2rem; text-align: center;
        box-shadow: 0 6px 24px rgba(0,0,0,0.18);
        position: relative; overflow: hidden;
    }}
    .main-header::before {{
        content: ''; position: absolute; top: -50%; left: -50%;
        width: 200%; height: 200%; background:
            radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255,255,255,0.06) 0%, transparent 40%);
        pointer-events: none;
    }}
    .main-header h1 {{
        margin: 0; font-size: 2.4rem; font-weight: 800; letter-spacing: -0.02em;
        text-shadow: 0 2px 6px rgba(0,0,0,0.2); position: relative;
        color: white !important;
    }}
    .main-header p {{
        margin: 0.6rem 0 0; opacity: 0.95; font-size: 1.15rem;
        position: relative; font-weight: 400;
    }}

    /* ===== KPI / METRIC CARDS ===== */
    .kpi-card {{
        background: #ffffff; border-radius: 14px; padding: 1.6rem 1.2rem;
        box-shadow: 0 3px 15px rgba(0,0,0,0.08); text-align: center;
        border-left: 6px solid {COLORS['card_border']};
        transition: transform 0.2s ease, box-shadow 0.25s ease;
        margin-bottom: 1rem;
    }}
    .kpi-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 28px rgba(0,0,0,0.14);
    }}
    .kpi-card h3 {{
        font-size: 0.82rem; color: #666 !important; margin: 0 0 0.5rem;
        text-transform: uppercase; letter-spacing: 0.06em; font-weight: 700 !important;
    }}
    .kpi-card .value {{
        font-size: 2.2rem; font-weight: 900; color: {COLORS['card_value']};
        line-height: 1.15;
    }}
    .delta-positive {{
        color: {COLORS['good']}; font-weight: 700; font-size: 0.9rem; margin-top: 0.3rem;
    }}
    .delta-negative {{
        color: {COLORS['danger']}; font-weight: 700; font-size: 0.9rem; margin-top: 0.3rem;
    }}

    /* ===== SECTION NARRATIVE ===== */
    .section-narrative {{
        background: {COLORS['narrative_bg']};
        border-left: 6px solid {COLORS['narrative_border']};
        padding: 1.2rem 1.6rem; border-radius: 0 12px 12px 0;
        margin-bottom: 1.4rem; font-size: 1.02rem;
        color: {COLORS['narrative_text']};
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        line-height: 1.7;
    }}
    .section-narrative strong {{
        font-size: 1.05rem;
    }}

    /* ===== BREADCRUMB / NAV BAR ===== */
    .nav-breadcrumb {{
        display: flex; align-items: center; gap: 0.6rem;
        padding: 0.7rem 1.2rem; background: #f8f9fa;
        border-radius: 10px; margin-bottom: 1.2rem;
        font-size: 0.95rem; color: #444;
        border: 1px solid #e9ecef;
        font-weight: 500;
    }}
    .nav-breadcrumb .sep {{ color: #aaa; font-weight: 300; }}
    .nav-breadcrumb .active {{ font-weight: 700; color: {COLORS['card_value']}; }}

    /* ===== QUICK NAV PILLS ===== */
    .quick-nav {{
        display: flex; flex-wrap: wrap; gap: 0.5rem;
        margin-bottom: 1.2rem;
    }}
    .quick-nav-pill {{
        display: inline-block; padding: 0.4rem 1rem;
        background: {COLORS['narrative_bg']}; border: 1px solid {COLORS['narrative_border']};
        border-radius: 22px; font-size: 0.85rem; color: {COLORS['narrative_text']};
        cursor: pointer; transition: all 0.2s ease; text-decoration: none;
        font-weight: 600;
    }}
    .quick-nav-pill:hover {{
        background: {COLORS['card_border']}; color: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    }}

    /* ===== SECTION HEADER ===== */
    .section-header {{
        display: flex; align-items: center; gap: 0.7rem;
        padding: 0.8rem 0; margin: 1.2rem 0 0.6rem;
        border-bottom: 3px solid {COLORS['card_border']};
    }}
    .section-header h2 {{
        margin: 0; font-size: 1.4rem; color: {COLORS['card_value']} !important;
        font-weight: 700 !important;
    }}
    .section-header .badge {{
        background: {COLORS['card_border']}; color: white;
        padding: 0.2rem 0.7rem; border-radius: 12px;
        font-size: 0.75rem; font-weight: 700;
    }}

    /* ===== DATA TABLE STYLING ===== */
    .styled-table {{
        width: 100%; border-collapse: collapse; font-size: 0.92rem;
        border-radius: 10px; overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    }}
    .styled-table th {{
        background: {COLORS['card_border']}; color: white;
        padding: 0.75rem 1rem; text-align: left; font-weight: 700;
        font-size: 0.9rem; letter-spacing: 0.02em;
    }}
    .styled-table td {{
        padding: 0.65rem 1rem; border-bottom: 1px solid #e9ecef;
        color: #333; font-size: 0.9rem;
    }}
    .styled-table tr:nth-child(even) td {{ background: #fafbfc; }}
    .styled-table tr:hover td {{ background: {COLORS['narrative_bg']}; }}

    /* ===== EXPANDER STYLING ===== */
    div[data-testid="stExpander"] {{
        border: 1px solid #dee2e6; border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04); margin-bottom: 0.8rem;
    }}
    div[data-testid="stExpander"] summary {{
        font-weight: 600; font-size: 1rem; color: #333;
    }}

    /* ===== METRIC STYLING ===== */
    div[data-testid="stMetricValue"] {{
        font-size: 1.8rem !important; font-weight: 800 !important;
        color: {COLORS['card_value']} !important;
    }}
    div[data-testid="stMetricLabel"] {{
        font-size: 0.92rem !important; font-weight: 600 !important;
        color: #555 !important; text-transform: uppercase;
        letter-spacing: 0.03em;
    }}
    div[data-testid="stMetricDelta"] {{
        font-size: 0.9rem !important; font-weight: 600 !important;
    }}

    /* ===== TAB STYLING ===== */
    button[data-baseweb="tab"] {{
        font-size: 1rem !important; font-weight: 700 !important;
        padding: 0.75rem 1.3rem !important;
        color: #444 !important;
        border-bottom: 3px solid transparent !important;
        transition: all 0.2s ease !important;
    }}
    button[data-baseweb="tab"]:hover {{
        background: {COLORS['narrative_bg']} !important;
        color: {COLORS['card_value']} !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {COLORS['card_value']} !important;
        border-bottom: 3px solid {COLORS['card_border']} !important;
        font-weight: 800 !important;
    }}

    /* ===== SIDEBAR STYLING ===== */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }}
    section[data-testid="stSidebar"] .block-container {{ padding-top: 1.2rem; }}
    section[data-testid="stSidebar"] label {{
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        color: #333 !important;
    }}
    .sidebar-section {{
        background: white; border-radius: 12px; padding: 1rem 1.2rem;
        margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e9ecef;
    }}
    .sidebar-nav-link {{
        display: block; padding: 0.5rem 0.8rem; margin: 0.2rem 0;
        border-radius: 8px; font-size: 0.88rem; color: #333;
        text-decoration: none; transition: all 0.15s ease;
        font-weight: 500;
    }}
    .sidebar-nav-link:hover {{
        background: {COLORS['narrative_bg']}; color: {COLORS['card_value']};
        font-weight: 600;
    }}

    /* ===== FOOTER ===== */
    .dashboard-footer {{
        text-align: center; color: #888; font-size: 0.88rem;
        padding: 2rem 0 0.8rem; border-top: 2px solid #e9ecef;
        margin-top: 2rem;
    }}
    .dashboard-footer strong {{ color: #555; }}
    .dashboard-footer a {{ color: {COLORS['card_border']}; text-decoration: none; font-weight: 600; }}

    /* ===== BACK TO TOP ===== */
    .back-to-top {{
        position: fixed; bottom: 2rem; right: 2rem;
        background: {COLORS['card_border']}; color: white;
        width: 46px; height: 46px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.3rem; box-shadow: 0 4px 16px rgba(0,0,0,0.22);
        cursor: pointer; z-index: 999; text-decoration: none;
        transition: transform 0.2s ease, opacity 0.2s ease;
        opacity: 0.9;
    }}
    .back-to-top:hover {{ transform: scale(1.12); opacity: 1; }}

    /* ===== CHART CONTAINERS ===== */
    div[data-testid="stPlotlyChart"] {{
        background: white;
        border-radius: 12px;
        padding: 0.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }}

    /* ===== DATAFRAME STYLING ===== */
    div[data-testid="stDataFrame"] {{
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }}

    /* ===== SUBHEADER STYLING ===== */
    .stSubheader, h2 {{
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        color: #1a1a2e !important;
        padding-bottom: 0.3rem;
        border-bottom: 2px solid #e9ecef;
        margin-bottom: 0.8rem !important;
    }}

    /* ===== MARKDOWN TEXT ===== */
    .stMarkdown {{
        font-size: 0.98rem;
        color: #333;
        line-height: 1.7;
    }}

    /* ===== HORIZONTAL RULES ===== */
    hr {{
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #dee2e6, transparent);
        margin: 1.5rem 0;
    }}

    /* ===== ANIMATIONS ===== */
    @keyframes fadeInUp {{
        from {{ opacity:0; transform:translateY(12px); }}
        to {{ opacity:1; transform:translateY(0); }}
    }}
    .stTabs [data-baseweb="tab-panel"] {{ animation: fadeInUp 0.35s ease-out; }}"""

content = content.replace(old_css, new_css)

# Verify replacement happened
if new_css[:30] not in content:
    print("WARNING: CSS replacement may have failed!")
else:
    print("CSS replacement successful")

# ============================================================================
# 3) Write the result
# ============================================================================
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
import py_compile
py_compile.compile(filepath, doraise=True)
print("Syntax OK")

# Count remaining leading-space issues
import re as re2
lines = content.split('\n')
issues = 0
for line in lines:
    matches = re2.findall(r'["\'](\s[A-Z][^"\']*)["\']', line)
    if matches and not line.strip().startswith('#') and not line.strip().startswith('"""'):
        issues += 1
print(f"Remaining leading-space label issues: {issues}")
print("Done!")
