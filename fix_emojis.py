"""Script to remove all emojis from forestry_dashboard.py and improve visibility."""
import re

with open('forestry_dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# PHASE 1: Exact string replacements for emoji-containing text
# ============================================================
exact_replacements = {
    # Theme dict keys
    '"🌲 Forest Green"': '"Forest Green"',
    '"🌊 Ocean Blue"': '"Ocean Blue"',
    '"🌅 Sunset"': '"Sunset"',
    '"🏔️ Earth Tones"': '"Earth Tones"',
    '"💼 Professional"': '"Professional"',

    # Error messages
    'f"❌ Forestry Excel not found:': 'f"Forestry Excel not found:',
    'f"❌ Women Survey Excel not found:': 'f"Women Survey Excel not found:',

    # Section header calls - remove icon arg
    "_section_header('💼', 'Economic Activities'": "_section_header('Economic Activities'",
    "_section_header('🏠', 'Access to Basic Services'": "_section_header('Access to Basic Services'",
    "_section_header('🛡️', 'Coping Strategies'": "_section_header('Coping Strategies'",
    "_section_header('📋', 'Disaster Preparedness'": "_section_header('Disaster Preparedness'",
    "_section_header('🏡', 'Household Assets'": "_section_header('Household Assets'",
    "_section_header('🌾', 'Land'": "_section_header('Land'",
    "_section_header('💰', 'Savings'": "_section_header('Savings'",
    "_section_header('🏦', 'Loans'": "_section_header('Loans'",
    "_section_header('👥', 'Roles & Responsibilities: Norms vs. Experience'": "_section_header('Roles & Responsibilities: Norms vs. Experience'",
    "_section_header('⏰', 'Time Use (Average Hours per Day)'": "_section_header('Time Use (Average Hours per Day)'",
    "_section_header('🗳️', 'Decision-Making'": "_section_header('Decision-Making'",
    "_section_header('💪', \"Influence on HH Decisions": "_section_header(\"Influence on HH Decisions",
    "_section_header('🌿', 'Nature-based Solutions'": "_section_header('Nature-based Solutions'",
    "_section_header('🌟', 'Life Skills": "_section_header('Life Skills",
    "_section_header('💬', 'Communication & Conflict Resolution'": "_section_header('Communication & Conflict Resolution'",
    "_section_header('⚖️', 'Social Norms'": "_section_header('Social Norms'",

    # NbS module icons
    "('Mangrove Restoration', 'mangrove', '🌊')": "('Mangrove Restoration', 'mangrove')",
    "('Seaweed Farming', 'seaweed', '🌿')": "('Seaweed Farming', 'seaweed')",
    "('Forest Management', 'forest', '🌲')": "('Forest Management', 'forest')",
    "_section_header(icon, module, 'NbS Module')": "_section_header(module, 'NbS Module')",
    "for module, prefix, icon in [": "for module, prefix in [",

    # Forestry tabs
    '"📊 Overview"': '"Overview"',
    '"👥 Group Characteristics"': '"Group Characteristics"',
    '"🏛️ Governance & Gender"': '"Governance & Gender"',
    '"📚 Training & Assets"': '"Training & Assets"',
    '"🌳 Forest Condition & Threats"': '"Forest Condition & Threats"',
    '"💰 Income & Agroforestry"': '"Income & Agroforestry"',

    # Women tabs
    '"🏠 Household Profile & Services"': '"Household Profile & Services"',
    '"⚡ Shocks, Coping & Preparedness"': '"Shocks, Coping & Preparedness"',
    '"💰 Assets, Land, Savings & Loans"': '"Assets, Land, Savings & Loans"',
    '"👥 Roles, Time Use & Decisions"': '"Roles, Time Use & Decisions"',
    '"🌍 Climate Change & NbS"': '"Climate Change & NbS"',
    '"🌟 Life Skills & Social Norms"': '"Life Skills & Social Norms"',

    # Subheader
    'st.subheader("📈 Score Statistics")': 'st.subheader("Score Statistics")',

    # Dataset selector
    '"📂 Dataset View"': '"Dataset View"',
    '"🔄 Combined Overview"': '"Combined Overview"',
    '"🌲 Forestry Groups"': '"Forestry Groups"',
    '"👩 Women Survey"': '"Women Survey"',

    # Show change toggle
    '"📊 Show Change (pp) Charts"': '"Show Change (pp) Charts"',

    # Quick Navigate sidebar
    '"**🧭 Quick Navigate**"': '"**Quick Navigate**"',
    '"**📋 Dataset Summary**"': '"**Dataset Summary**"',
    '"**📋 Datasets Loaded**"': '"**Datasets Loaded**"',

    # Theme selector
    '"🎨 Dashboard Theme"': '"Dashboard Theme"',

    # Page icon
    'page_icon="🌍"': 'page_icon="bar_chart"',

    # Sidebar header
    '<span style="font-size:2.5rem;">🌍</span>': '',

    # Sidebar nav links
    '<span class="sidebar-nav-link">📊 Overview & KPIs</span>': '<span class="sidebar-nav-link">Overview & KPIs</span>',
    '<span class="sidebar-nav-link">👥 Group Characteristics</span>': '<span class="sidebar-nav-link">Group Characteristics</span>',
    '<span class="sidebar-nav-link">🏛️ Governance & Gender</span>': '<span class="sidebar-nav-link">Governance & Gender</span>',
    '<span class="sidebar-nav-link">📚 Training & Assets</span>': '<span class="sidebar-nav-link">Training & Assets</span>',
    '<span class="sidebar-nav-link">🌳 Forest Condition</span>': '<span class="sidebar-nav-link">Forest Condition</span>',
    '<span class="sidebar-nav-link">💰 Income & Agroforestry</span>': '<span class="sidebar-nav-link">Income & Agroforestry</span>',
    '<span class="sidebar-nav-link">🏠 Household Profile</span>': '<span class="sidebar-nav-link">Household Profile</span>',
    '<span class="sidebar-nav-link">⚡ Shocks & Preparedness</span>': '<span class="sidebar-nav-link">Shocks & Preparedness</span>',
    '<span class="sidebar-nav-link">💰 Assets & Savings</span>': '<span class="sidebar-nav-link">Assets & Savings</span>',
    '<span class="sidebar-nav-link">👥 Roles & Decisions</span>': '<span class="sidebar-nav-link">Roles & Decisions</span>',
    '<span class="sidebar-nav-link">🌍 Climate & NbS</span>': '<span class="sidebar-nav-link">Climate & NbS</span>',
    '<span class="sidebar-nav-link">🌟 Life Skills & Norms</span>': '<span class="sidebar-nav-link">Life Skills & Norms</span>',
    '<span class="sidebar-nav-link">🌲 Forestry Headlines</span>': '<span class="sidebar-nav-link">Forestry Headlines</span>',
    '<span class="sidebar-nav-link">👩 Women Survey Headlines</span>': '<span class="sidebar-nav-link">Women Survey Headlines</span>',
    '<span class="sidebar-nav-link">📊 Comparative Snapshots</span>': '<span class="sidebar-nav-link">Comparative Snapshots</span>',

    # Headers
    '<h1>🌲 Community Forest Conservation Dashboard</h1>': '<h1>Community Forest Conservation Dashboard</h1>',
    "<h1>👩 Women's Survey Dashboard</h1>": "<h1>Women's Survey Dashboard</h1>",
    '<h1>🌍 COSME Baseline\u2013Midline Dashboard</h1>': '<h1>COSME Baseline\u2013Midline Dashboard</h1>',

    # Breadcrumbs
    '<span>🌍 COSME</span>': '<span>COSME</span>',
    '<span class="active">🌲 Forestry Groups</span>': '<span class="active">Forestry Groups</span>',
    "<span class=\"active\">👩 Women Survey</span>": '<span class="active">Women Survey</span>',
    '<span class="active">🌍 COSME \u2014 Combined Overview</span>': '<span class="active">COSME \u2014 Combined Overview</span>',

    # Synthesis view
    '<strong>📊 Cross-Dataset Synthesis:</strong>': '<strong>Cross-Dataset Synthesis:</strong>',
    '<h3 style="margin-top:0.5rem;">🌲 Forestry Conservation Groups \u2014 Headlines</h3>': '<h3 style="margin-top:0.5rem;">Forestry Conservation Groups \u2014 Headlines</h3>',
    "<h3>👩 Women\\'s Survey \\u2014 Headlines</h3>": "<h3>Women\\'s Survey \\u2014 Headlines</h3>",
    '<h3>📊 Comparative Snapshots</h3>': '<h3>Comparative Snapshots</h3>',
    '<strong>💡 Navigate deeper:</strong>': '<strong>Navigate deeper:</strong>',

    # Footer
    '🌍 <strong>COSME Baseline\u2013Midline Dashboard</strong>': '<strong>COSME Baseline\u2013Midline Dashboard</strong>',

    # Datasets loaded
    '✅ Forestry Groups': 'Forestry Groups',
    '✅ Women Survey': 'Women Survey',

    # Back to top
    '>⬆</a>': '>&#9650;</a>',
}

for old, new in exact_replacements.items():
    content = content.replace(old, new)

print("Phase 1 complete - exact replacements done")

# ============================================================
# PHASE 2: Fix the Women's Survey headline (tricky quotes)
# ============================================================
content = content.replace("<h3>👩 Women's Survey", "<h3>Women's Survey")
content = content.replace("👩", "")
content = content.replace("🌲", "")
content = content.replace("📊", "")
content = content.replace("🌍", "")

# ============================================================
# PHASE 3: Catch remaining emojis with regex
# ============================================================
# Remove any remaining Unicode emojis
emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"  # dingbats
    "\U000024C2-\U0001F251"
    "\U0001f926-\U0001f937"
    "\U00010000-\U0010ffff"
    "\u2600-\u26FF"
    "\u2700-\u27BF"
    "\u200d"
    "\ufe0f"
    "\u2640-\u2642"
    "\u23cf"
    "\u23e9"
    "\u231a"
    "\u3030"
    "\ufe0f"
    "\u2716"
    "\u274c"
    "\u274e"
    "\u2714"
    "\u2795-\u2797"
    "\u27a1"
    "\u27b0"
    "\u2934-\u2935"
    "\u2b05-\u2b07"
    "\u2b1b-\u2b1c"
    "\u2b50"
    "\u2b55"
    "\u23f0-\u23f3"
    "\u2696"
    "\u2697"
    "\u2699"
    "\u269b-\u269c"
    "]+", flags=re.UNICODE)

content = emoji_pattern.sub('', content)
print("Phase 3 complete - remaining emojis removed")

# ============================================================
# PHASE 4: Fix _section_header function signature
# The function used to take (icon, title, badge) now takes (title, badge)
# ============================================================
old_func = '''def _section_header(icon, title, badge_text=None):
    """Render a styled section header with optional badge."""
    badge = f'<span class="badge">{badge_text}</span>' if badge_text else ''
    st.markdown(f'<div class="section-header"><h2>{icon} {title}</h2>{badge}</div>',
                unsafe_allow_html=True)'''

new_func = '''def _section_header(title, badge_text=None):
    """Render a styled section header with optional badge."""
    badge = f'<span class="badge">{badge_text}</span>' if badge_text else ''
    st.markdown(f'<div class="section-header"><h2>{title}</h2>{badge}</div>',
                unsafe_allow_html=True)'''

content = content.replace(old_func, new_func)
print("Phase 4 complete - _section_header signature fixed")

# ============================================================
# PHASE 5: IMPROVE VISIBILITY & FORMATTING
# ============================================================

# 5a. Improve header sizing and padding
content = content.replace(
    ".main-header h1 {{ margin: 0; font-size: 2.2rem; font-weight: 700; letter-spacing: -0.02em;\n        text-shadow: 0 2px 4px rgba(0,0,0,0.15); position: relative; }}",
    ".main-header h1 {{ margin: 0; font-size: 2.6rem; font-weight: 800; letter-spacing: -0.02em;\n        text-shadow: 0 2px 4px rgba(0,0,0,0.15); position: relative; }}"
)
content = content.replace(
    ".main-header p {{ margin: 0.4rem 0 0; opacity: 0.92; font-size: 1.05rem; position: relative; }}",
    ".main-header p {{ margin: 0.4rem 0 0; opacity: 0.95; font-size: 1.15rem; position: relative; font-weight: 500; }}"
)

# 5b. Make KPI cards more visible
content = content.replace(
    ".kpi-card h3 {{ font-size: 0.78rem; color: #888; margin: 0 0 0.4rem;\n        text-transform: uppercase; letter-spacing: 0.04em; font-weight: 600; }}",
    ".kpi-card h3 {{ font-size: 0.88rem; color: #555; margin: 0 0 0.5rem;\n        text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; }}"
)
content = content.replace(
    ".kpi-card .value {{ font-size: 2rem; font-weight: 800; color: {COLORS['card_value']};\n        line-height: 1.1; }}",
    ".kpi-card .value {{ font-size: 2.4rem; font-weight: 800; color: {COLORS['card_value']};\n        line-height: 1.2; }}"
)
content = content.replace(
    ".kpi-card {{\n        background: white; border-radius: 12px; padding: 1.3rem 1rem;",
    ".kpi-card {{\n        background: white; border-radius: 12px; padding: 1.5rem 1.2rem;"
)

# 5c. Improve section narrative readability
content = content.replace(
    """    .section-narrative {{
        background: {COLORS['narrative_bg']};
        border-left: 5px solid {COLORS['narrative_border']};
        padding: 1rem 1.4rem; border-radius: 0 10px 10px 0;
        margin-bottom: 1.2rem; font-size: 0.95rem;
        color: {COLORS['narrative_text']};
        box-shadow: 0 1px 6px rgba(0,0,0,0.04);
    }}""",
    """    .section-narrative {{
        background: {COLORS['narrative_bg']};
        border-left: 5px solid {COLORS['narrative_border']};
        padding: 1.2rem 1.6rem; border-radius: 0 10px 10px 0;
        margin-bottom: 1.4rem; font-size: 1.05rem;
        color: {COLORS['narrative_text']};
        line-height: 1.7;
        box-shadow: 0 1px 6px rgba(0,0,0,0.04);
    }}"""
)

# 5d. Improve section header sizing
content = content.replace(
    ".section-header h2 {{ margin: 0; font-size: 1.3rem; color: {COLORS['card_value']}; }}",
    ".section-header h2 {{ margin: 0; font-size: 1.5rem; color: {COLORS['card_value']}; font-weight: 700; }}"
)

# 5e. Improve tab button formatting
content = content.replace(
    """    button[data-baseweb="tab"] {{
        font-size: 0.92rem !important; font-weight: 600 !important;
        padding: 0.6rem 1.1rem !important;
    }}""",
    """    button[data-baseweb="tab"] {{
        font-size: 1rem !important; font-weight: 700 !important;
        padding: 0.7rem 1.3rem !important;
        letter-spacing: 0.01em !important;
    }}"""
)

# 5f. Improve breadcrumb visibility
content = content.replace(
    """    .nav-breadcrumb {{
        display: flex; align-items: center; gap: 0.5rem;
        padding: 0.6rem 1rem; background: rgba(0,0,0,0.03);
        border-radius: 8px; margin-bottom: 1rem;
        font-size: 0.88rem; color: #555;
        border: 1px solid rgba(0,0,0,0.06);
    }}""",
    """    .nav-breadcrumb {{
        display: flex; align-items: center; gap: 0.5rem;
        padding: 0.7rem 1.2rem; background: rgba(0,0,0,0.04);
        border-radius: 8px; margin-bottom: 1.2rem;
        font-size: 0.95rem; color: #444;
        border: 1px solid rgba(0,0,0,0.08);
    }}"""
)

# 5g. Improve quick nav pills
content = content.replace(
    """    .quick-nav-pill {{
        display: inline-block; padding: 0.35rem 0.9rem;
        background: {COLORS['narrative_bg']}; border: 1px solid {COLORS['narrative_border']};
        border-radius: 20px; font-size: 0.8rem; color: {COLORS['narrative_text']};
        cursor: pointer; transition: all 0.2s ease; text-decoration: none;
    }}""",
    """    .quick-nav-pill {{
        display: inline-block; padding: 0.4rem 1rem;
        background: {COLORS['narrative_bg']}; border: 1px solid {COLORS['narrative_border']};
        border-radius: 20px; font-size: 0.88rem; color: {COLORS['narrative_text']};
        font-weight: 600;
        cursor: pointer; transition: all 0.2s ease; text-decoration: none;
    }}"""
)

# 5h. Improve data table text size
content = content.replace(
    """    .styled-table {{
        width: 100%; border-collapse: collapse; font-size: 0.88rem;""",
    """    .styled-table {{
        width: 100%; border-collapse: collapse; font-size: 0.95rem;"""
)
content = content.replace(
    ".styled-table th {{\n        background: {COLORS['card_border']}; color: white;\n        padding: 0.6rem 0.8rem; text-align: left; font-weight: 600;\n    }}",
    ".styled-table th {{\n        background: {COLORS['card_border']}; color: white;\n        padding: 0.7rem 1rem; text-align: left; font-weight: 700;\n        font-size: 0.95rem;\n    }}"
)

# 5i. Improve metric value sizing
content = content.replace(
    "div[data-testid=\"stMetricValue\"] {{ font-size: 1.5rem; font-weight: 700; }}",
    "div[data-testid=\"stMetricValue\"] {{ font-size: 1.8rem; font-weight: 800; }}"
)

# 5j. Improve footer
content = content.replace(
    """    .dashboard-footer {{
        text-align: center; color: #999; font-size: 0.82rem;
        padding: 1.5rem 0 0.5rem; border-top: 1px solid #eee;
        margin-top: 1.5rem;
    }}""",
    """    .dashboard-footer {{
        text-align: center; color: #777; font-size: 0.9rem;
        padding: 2rem 0 1rem; border-top: 2px solid #e0e0e0;
        margin-top: 2rem;
    }}"""
)

# 5k. Improve sidebar nav link font
content = content.replace(
    """    .sidebar-nav-link {{
        display: block; padding: 0.4rem 0.6rem; margin: 0.15rem 0;
        border-radius: 6px; font-size: 0.82rem; color: #444;
        text-decoration: none; transition: all 0.15s ease;
    }}""",
    """    .sidebar-nav-link {{
        display: block; padding: 0.5rem 0.8rem; margin: 0.2rem 0;
        border-radius: 6px; font-size: 0.9rem; color: #333;
        font-weight: 500;
        text-decoration: none; transition: all 0.15s ease;
    }}"""
)

# 5l. Add global font size boost  
content = content.replace(
    '    <a href="#top" class="back-to-top" title="Back to top">&#9650;</a>',
    """    /* ---------- GLOBAL READABILITY ---------- */
    .main .block-container {{ padding: 1rem 2rem 2rem; max-width: 1200px; }}
    [data-testid="stMarkdownContainer"] p {{ font-size: 1rem; line-height: 1.6; color: #333; }}
    [data-testid="stMarkdownContainer"] h3 {{ font-size: 1.35rem; font-weight: 700; color: #222; margin-top: 1.5rem; }}
    [data-testid="stMarkdownContainer"] strong {{ color: #222; }}

    /* ---------- CHART IMPROVEMENTS ---------- */
    .js-plotly-plot .plotly .gtitle {{ font-size: 16px !important; font-weight: 700 !important; }}
    .js-plotly-plot .plotly .xtick text, .js-plotly-plot .plotly .ytick text {{ font-size: 13px !important; }}

    </style>

    <a href="#top" class="back-to-top" title="Back to top">&#9650;</a>"""
)

# 5m. Improve delta text visibility
content = content.replace(
    ".delta-positive {{ color: {COLORS['good']}; font-weight: 600; font-size: 0.85rem; margin-top: 0.2rem; }}",
    ".delta-positive {{ color: {COLORS['good']}; font-weight: 700; font-size: 0.95rem; margin-top: 0.3rem; }}"
)
content = content.replace(
    ".delta-negative {{ color: {COLORS['danger']}; font-weight: 600; font-size: 0.85rem; margin-top: 0.2rem; }}",
    ".delta-negative {{ color: {COLORS['danger']}; font-weight: 700; font-size: 0.95rem; margin-top: 0.3rem; }}"
)

print("Phase 5 complete - visibility improvements done")

# ============================================================
# Write the final file
# ============================================================
with open('forestry_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Quick verify - count remaining emoji-like characters
remaining = re.findall(emoji_pattern, content)
print(f"\nDone! Remaining emoji-like chars: {len(remaining)}")
if remaining:
    for r in set(remaining):
        print(f"  Found: {repr(r)}")
print(f"\nTotal file length: {len(content)} chars")
