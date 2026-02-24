"""
=============================================================================
FORESTRY CONSERVATION GROUP DASHBOARD
Baseline vs Midline Assessment | Community Forest Conservation Project
=============================================================================
A Streamlit + Plotly interactive dashboard for M&E analysis of Community
Forestry Conservation Groups.

Excel file: 'Forest Functionality Basline_midline results.xlsx'
Sheet: 'Results' (single sheet with all data sections)

Run with:  streamlit run forestry_dashboard.py
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ============================================================================
# CONFIGURATION — Change these values if your Excel/sheet names differ
# ============================================================================
# Path to your Excel file (relative to this script's location)
EXCEL_FILE = "Forest Functionality Basline_midline results.xlsx"
SHEET_NAME = "Results"  # The sheet containing all data

# ============================================================================
# THEMES — Multiple color palettes selectable from the sidebar
# ============================================================================
THEMES = {
    "🌲 Forest Green": {
        "baseline": "#5B8DB8",       "midline": "#2E7D32",
        "baseline_light": "#A3C4DC", "midline_light": "#81C784",
        "accent": "#FF8F00",         "danger": "#E53935",
        "good": "#43A047",           "medium": "#FB8C00",
        "poor": "#E53935",           "low": "#43A047",
        "high": "#E53935",           "decrease": "#43A047",
        "increase": "#E53935",       "no_change": "#78909C",
        # UI chrome
        "header_gradient": "linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #388E3C 100%)",
        "card_border": "#2E7D32",
        "card_value": "#1B5E20",
        "narrative_bg": "#E8F5E9",
        "narrative_border": "#2E7D32",
        "narrative_text": "#1B5E20",
        "radar_bl_fill": "rgba(91,141,184,0.3)",
        "radar_ml_fill": "rgba(46,125,50,0.3)",
    },
    "🌊 Ocean Blue": {
        "baseline": "#1565C0",       "midline": "#00838F",
        "baseline_light": "#90CAF9", "midline_light": "#80DEEA",
        "accent": "#FF6F00",         "danger": "#D32F2F",
        "good": "#00897B",           "medium": "#F9A825",
        "poor": "#D32F2F",           "low": "#00897B",
        "high": "#D32F2F",           "decrease": "#00897B",
        "increase": "#D32F2F",       "no_change": "#78909C",
        "header_gradient": "linear-gradient(135deg, #0D47A1 0%, #1565C0 50%, #1976D2 100%)",
        "card_border": "#1565C0",
        "card_value": "#0D47A1",
        "narrative_bg": "#E3F2FD",
        "narrative_border": "#1565C0",
        "narrative_text": "#0D47A1",
        "radar_bl_fill": "rgba(21,101,192,0.3)",
        "radar_ml_fill": "rgba(0,131,143,0.3)",
    },
    "🌅 Sunset": {
        "baseline": "#E65100",       "midline": "#AD1457",
        "baseline_light": "#FFB74D", "midline_light": "#F48FB1",
        "accent": "#FDD835",         "danger": "#B71C1C",
        "good": "#388E3C",           "medium": "#F9A825",
        "poor": "#B71C1C",           "low": "#388E3C",
        "high": "#B71C1C",           "decrease": "#388E3C",
        "increase": "#B71C1C",       "no_change": "#78909C",
        "header_gradient": "linear-gradient(135deg, #BF360C 0%, #E65100 50%, #F4511E 100%)",
        "card_border": "#E65100",
        "card_value": "#BF360C",
        "narrative_bg": "#FBE9E7",
        "narrative_border": "#E65100",
        "narrative_text": "#BF360C",
        "radar_bl_fill": "rgba(230,81,0,0.3)",
        "radar_ml_fill": "rgba(173,20,87,0.3)",
    },
    "🏔️ Earth Tones": {
        "baseline": "#6D4C41",       "midline": "#33691E",
        "baseline_light": "#BCAAA4", "midline_light": "#A5D6A7",
        "accent": "#FF8F00",         "danger": "#C62828",
        "good": "#558B2F",           "medium": "#F9A825",
        "poor": "#C62828",           "low": "#558B2F",
        "high": "#C62828",           "decrease": "#558B2F",
        "increase": "#C62828",       "no_change": "#8D6E63",
        "header_gradient": "linear-gradient(135deg, #3E2723 0%, #5D4037 50%, #6D4C41 100%)",
        "card_border": "#6D4C41",
        "card_value": "#3E2723",
        "narrative_bg": "#EFEBE9",
        "narrative_border": "#6D4C41",
        "narrative_text": "#3E2723",
        "radar_bl_fill": "rgba(109,76,65,0.3)",
        "radar_ml_fill": "rgba(51,105,30,0.3)",
    },
    "💼 Professional": {
        "baseline": "#37474F",       "midline": "#1565C0",
        "baseline_light": "#B0BEC5", "midline_light": "#90CAF9",
        "accent": "#FF6F00",         "danger": "#C62828",
        "good": "#2E7D32",           "medium": "#EF6C00",
        "poor": "#C62828",           "low": "#2E7D32",
        "high": "#C62828",           "decrease": "#2E7D32",
        "increase": "#C62828",       "no_change": "#78909C",
        "header_gradient": "linear-gradient(135deg, #263238 0%, #37474F 50%, #455A64 100%)",
        "card_border": "#37474F",
        "card_value": "#263238",
        "narrative_bg": "#ECEFF1",
        "narrative_border": "#37474F",
        "narrative_text": "#263238",
        "radar_bl_fill": "rgba(55,71,79,0.3)",
        "radar_ml_fill": "rgba(21,101,192,0.3)",
    },
}

# Default — will be overridden per session by the sidebar selector
COLORS = THEMES["🌲 Forest Green"]

# ============================================================================
# DATA LOADING — Reads raw data from specific rows/columns in the Excel sheet
# ============================================================================

@st.cache_data
def load_all_data(filepath):
    """
    Load all data sections from the single 'Results' sheet.
    The Excel file has a non-standard layout with different sections
    at different row positions with varying column structures.
    We parse each section individually.
    """
    # Read the entire sheet once as raw values
    try:
        raw = pd.read_excel(filepath, sheet_name=SHEET_NAME, header=None)
    except FileNotFoundError:
        st.error(f"❌ Excel file not found: {filepath}")
        st.info("Please place the Excel file in the same folder as this script.")
        st.stop()

    data = {}

    # --- 1. FUNCTIONALITY THRESHOLD (Rows 7-9, 0-indexed: 6-8) ---
    data['functionality_threshold'] = pd.DataFrame({
        'Timepoint': ['Baseline', 'Midline'],
        'Functional_60_pct': [_val(raw, 7, 2), _val(raw, 8, 2)],
        'Functional_70_pct': [_val(raw, 7, 3), _val(raw, 8, 3)],
    })

    # --- 2. OVERALL FUNCTIONALITY SCORES (Rows 13-15) ---
    data['functionality_scores'] = pd.DataFrame({
        'Timepoint': ['Baseline', 'Midline'],
        'Respondents': [_val(raw, 13, 2), _val(raw, 14, 2)],
        'Average': [_val(raw, 13, 3), _val(raw, 14, 3)],
        'Max': [_val(raw, 13, 4), _val(raw, 14, 4)],
        'Min': [_val(raw, 13, 5), _val(raw, 14, 5)],
    })

    # --- 3. FUNCTIONALITY BY DOMAIN (Rows 19-21) ---
    data['functionality_domain'] = pd.DataFrame({
        'Timepoint': ['Baseline', 'Midline'],
        'Management': [_val(raw, 19, 2), _val(raw, 20, 2)],
        'Gender': [_val(raw, 19, 3), _val(raw, 20, 3)],
        'Effectiveness': [_val(raw, 19, 4), _val(raw, 20, 4)],
        'Overall': [_val(raw, 19, 5), _val(raw, 20, 5)],
    })

    # --- 4. GROUP CHARACTERISTICS ---
    data['num_groups'] = pd.DataFrame({
        'Timepoint': ['Baseline', 'Midline'],
        'Groups_Assessed': [_val(raw, 27, 2), _val(raw, 27, 3)],
    })

    # Average membership (Rows 32-35)
    data['avg_membership'] = pd.DataFrame({
        'Category': ['Male', 'Female', 'All'],
        'Baseline': [_val(raw, 32, 2), _val(raw, 33, 2), _val(raw, 34, 2)],
        'Midline': [_val(raw, 32, 3), _val(raw, 33, 3), _val(raw, 34, 3)],
    })

    # Max membership (Rows 39-42)
    data['max_membership'] = pd.DataFrame({
        'Category': ['Male', 'Female', 'All'],
        'Baseline': [_val(raw, 39, 2), _val(raw, 40, 2), _val(raw, 41, 2)],
        'Midline': [_val(raw, 39, 3), _val(raw, 40, 3), _val(raw, 41, 3)],
    })

    # Min membership (Rows 46-49)
    data['min_membership'] = pd.DataFrame({
        'Category': ['Male', 'Female', 'All'],
        'Baseline': [_val(raw, 46, 2), _val(raw, 47, 2), _val(raw, 48, 2)],
        'Midline': [_val(raw, 46, 3), _val(raw, 47, 3), _val(raw, 48, 3)],
    })

    # Years of operation stats (Rows 53-56)
    data['years_stats'] = pd.DataFrame({
        'Stat': ['Average', 'Maximum', 'Minimum'],
        'Baseline': [_val(raw, 53, 2), _val(raw, 54, 2), _val(raw, 55, 2)],
        'Midline': [_val(raw, 53, 3), _val(raw, 54, 3), _val(raw, 55, 3)],
    })

    # Years distribution (Rows 57-61)
    data['years_dist'] = pd.DataFrame({
        'Category': ['0-3 years', '4-5 years', '6-10 years', '11+ years'],
        'Baseline': [_val(raw, 57, 2), _val(raw, 58, 2), _val(raw, 59, 2), _val(raw, 60, 2)],
        'Midline': [_val(raw, 57, 3), _val(raw, 58, 3), _val(raw, 59, 3), _val(raw, 60, 3)],
    })

    # Land tenure (Rows 65-70)
    data['tenure'] = pd.DataFrame({
        'Category': ['Community', 'Government', 'Govt Devolved', 'Individual', 'Other'],
        'Baseline': [_val(raw, 65, 2), _val(raw, 66, 2), _val(raw, 67, 2), _val(raw, 68, 2), _val(raw, 69, 2)],
        'Midline': [_val(raw, 65, 3), _val(raw, 66, 3), _val(raw, 67, 3), _val(raw, 68, 3), _val(raw, 69, 3)],
    })

    # Forest size stats (Rows 74-77)
    data['forest_size_stats'] = pd.DataFrame({
        'Stat': ['Average', 'Maximum', 'Minimum'],
        'Baseline': [_val(raw, 74, 2), _val(raw, 75, 2), _val(raw, 76, 2)],
        'Midline': [_val(raw, 74, 3), _val(raw, 75, 3), _val(raw, 76, 3)],
    })

    # Forest size distribution (Rows 78-84)
    data['forest_size_dist'] = pd.DataFrame({
        'Category': ['0 ha', '1-5 ha', '6-10 ha', '11-100 ha', '101-999 ha', '1000+ ha'],
        'Baseline': [_val(raw, 78, 2), _val(raw, 79, 2), _val(raw, 80, 2), _val(raw, 81, 2), _val(raw, 82, 2), _val(raw, 83, 2)],
        'Midline': [_val(raw, 78, 3), _val(raw, 79, 3), _val(raw, 80, 3), _val(raw, 81, 3), _val(raw, 82, 3), _val(raw, 83, 3)],
    })

    # --- 5. OBJECTIVES, RIGHTS, RESPONSIBILITIES ---
    # Defined goals (Rows 91-94)
    data['goals_defined'] = pd.DataFrame({
        'Category': ['No', 'Partially', 'Yes'],
        'Baseline': [_val(raw, 91, 2), _val(raw, 92, 2), _val(raw, 93, 2)],
        'Midline': [_val(raw, 91, 3), _val(raw, 92, 3), _val(raw, 93, 3)],
    })

    # Goals stated (Rows 98-103, cols 9-10)
    data['goals_stated'] = pd.DataFrame({
        'Goal': [
            'Sustain Forest Resources',
            'Local Livelihoods/Poverty',
            'Protect Local Rights',
            'Public Rights/State Control',
            'Other'
        ],
        'Baseline': [_val(raw, 98, 9), _val(raw, 99, 9), _val(raw, 100, 9), _val(raw, 101, 9), _val(raw, 102, 9)],
        'Midline': [_val(raw, 98, 10), _val(raw, 99, 10), _val(raw, 100, 10), _val(raw, 101, 10), _val(raw, 102, 10)],
    })

    # Rights (Rows 107-115, cols 9-10)
    data['rights'] = pd.DataFrame({
        'Right': [
            'Access', 'Withdrawal (Subsistence)', 'Withdrawal (Commercial)',
            'Management', 'Exclusion', 'Alienation', 'Compensation', "Don't Know"
        ],
        'Baseline': [_val(raw, 107, 9), _val(raw, 108, 9), _val(raw, 109, 9), _val(raw, 110, 9),
                     _val(raw, 111, 9), _val(raw, 112, 9), _val(raw, 113, 9), _val(raw, 114, 9)],
        'Midline': [_val(raw, 107, 10), _val(raw, 108, 10), _val(raw, 109, 10), _val(raw, 110, 10),
                    _val(raw, 111, 10), _val(raw, 112, 10), _val(raw, 113, 10), _val(raw, 114, 10)],
    })

    # Responsibilities (Rows 119-133, cols 8-9)
    resp_labels = [
        'Register Group', 'EIA', 'Management Plan', 'Forestry Inventory',
        'Approval NWFP', 'Approval Grazing', 'Approval Fuelwood', 'Approval Timber',
        'Approval Transport/Sale', 'Pay Tax', 'Certification',
        'Monitor Restrictions', 'Other', "Don't Know"
    ]
    resp_bl = [_val(raw, r, 8) for r in range(119, 133)]
    resp_ml = [_val(raw, r, 9) for r in range(119, 133)]
    data['responsibilities'] = pd.DataFrame({
        'Responsibility': resp_labels,
        'Baseline': resp_bl,
        'Midline': resp_ml,
    })

    # --- 6. GROUP MANAGEMENT ---
    # Board roles (Rows 140-144, cols 11-12)
    data['board_roles'] = pd.DataFrame({
        'Category': ['Well Defined & Understood', 'Well Defined, Not All Understand',
                      'Not Defined at All', 'Not Well Defined, Not Understood'],
        'Baseline': [_val(raw, 140, 11), _val(raw, 141, 11), _val(raw, 142, 11), _val(raw, 143, 11)],
        'Midline': [_val(raw, 140, 12), _val(raw, 141, 12), _val(raw, 142, 12), _val(raw, 143, 12)],
    })

    # Guidelines (Rows 148-152, cols 5-6)
    data['guidelines'] = pd.DataFrame({
        'Category': ['Adopted & Known Most', 'Approved & Known Some',
                      'Drafted & Known Few', 'No Guidelines'],
        'Baseline': [_val(raw, 148, 5), _val(raw, 149, 5), _val(raw, 150, 5), _val(raw, 151, 5)],
        'Midline': [_val(raw, 148, 6), _val(raw, 149, 6), _val(raw, 150, 6), _val(raw, 151, 6)],
    })

    # Meetings (Rows 156-159, cols 11-12)
    data['meetings'] = pd.DataFrame({
        'Category': ['Occasional / Low Attendance', 'Often / Moderate Attendance',
                      'Regular / Full Quorum'],
        'Baseline': [_val(raw, 156, 11), _val(raw, 157, 11), _val(raw, 158, 11)],
        'Midline': [_val(raw, 156, 12), _val(raw, 157, 12), _val(raw, 158, 12)],
    })

    # Women leadership (Rows 163-167, cols 12-13)
    data['women_leadership'] = pd.DataFrame({
        'Category': ['No Leadership, No Voice', 'No Leadership, Occasional Voice',
                      'Some Leadership', 'Significant Leadership'],
        'Baseline': [_val(raw, 163, 12), _val(raw, 164, 12), _val(raw, 165, 12), _val(raw, 166, 12)],
        'Midline': [_val(raw, 163, 13), _val(raw, 164, 13), _val(raw, 165, 13), _val(raw, 166, 13)],
    })

    # Management practices (Rows 173-179, cols 8-11)
    mgmt_labels = [
        'Transparent Elections', 'Inclusive Decisions',
        'Clear Procedures', 'Grievance Mechanism',
        'Benefit Sharing Rules', 'Decisions Communicated'
    ]
    data['mgmt_practices'] = pd.DataFrame({
        'Practice': mgmt_labels,
        'Agree_Baseline': [_val(raw, r, 8) for r in range(173, 179)],
        'Agree_Midline': [_val(raw, r, 9) for r in range(173, 179)],
        'StronglyAgree_Baseline': [_val(raw, r, 10) for r in range(173, 179)],
        'StronglyAgree_Midline': [_val(raw, r, 11) for r in range(173, 179)],
    })

    # --- 7. TRAINING AND ASSETS ---
    # Training coverage (Rows 186-190, cols 4-5)
    data['training_coverage'] = pd.DataFrame({
        'Category': ['None', 'A Few Members', 'Many Members', 'Most Members'],
        'Baseline': [_val(raw, 186, 4), _val(raw, 187, 4), _val(raw, 188, 4), _val(raw, 189, 4)],
        'Midline': [_val(raw, 186, 5), _val(raw, 187, 5), _val(raw, 188, 5), _val(raw, 189, 5)],
    })

    # Training topics (Rows 194-214, cols 6-7)
    topic_labels = [
        'Climate Change & Forests', 'People & Forests', 'CFM Concepts',
        'Policy & Regulatory', 'Group Establishment', 'Participation',
        'Leadership', 'Forest Assessment', 'Socioeconomic Assessment',
        'Visioning & Objectives', 'Group Management', 'Group Registration',
        'Environmental Impact Assessment', 'Management Plan',
        'Forest Livelihoods', 'Forest Enterprises',
        'Gender & Governance', 'Gender & Environment',
        'Disaster Risk Management', 'Other'
    ]
    data['training_topics'] = pd.DataFrame({
        'Topic': topic_labels,
        'Baseline': [_val(raw, r, 6) for r in range(194, 214)],
        'Midline': [_val(raw, r, 7) for r in range(194, 214)],
    })

    # Assets received (Rows 218-220, cols 2-3)
    data['assets_received'] = pd.DataFrame({
        'Category': ['No', 'Yes'],
        'Baseline': [_val(raw, 218, 2), _val(raw, 219, 2)],
        'Midline': [_val(raw, 218, 3), _val(raw, 219, 3)],
    })

    # Asset types (Rows 224-231, cols 2-3)
    data['asset_types'] = pd.DataFrame({
        'Asset': ['Seedlings/Nursery', 'Agricultural Inputs', 'Energy (Solar/Stoves)',
                  'Water & Irrigation', 'Tools & Equipment', 'Beekeeping Inputs', 'Infrastructure'],
        'Baseline': [_val(raw, 224, 2), _val(raw, 225, 2), _val(raw, 226, 2), _val(raw, 227, 2),
                     _val(raw, 228, 2), _val(raw, 229, 2), _val(raw, 230, 2)],
        'Midline': [_val(raw, 224, 3), _val(raw, 225, 3), _val(raw, 226, 3), _val(raw, 227, 3),
                     _val(raw, 228, 3), _val(raw, 229, 3), _val(raw, 230, 3)],
    })

    # --- 8. GENDER EQUALITY ---
    # Discussion (Rows 238-240, cols 2-3)
    data['ge_discussion'] = pd.DataFrame({
        'Category': ['No', 'Yes'],
        'Baseline': [_val(raw, 238, 2), _val(raw, 239, 2)],
        'Midline': [_val(raw, 238, 3), _val(raw, 239, 3)],
    })

    # Topics discussed (Rows 244-248, cols 6-7)
    data['ge_topics'] = pd.DataFrame({
        'Topic': ['Equitable Roles/Responsibilities', 'Resource Sharing',
                  'Women Leadership & Voice', 'Other'],
        'Baseline': [_val(raw, 244, 6), _val(raw, 245, 6), _val(raw, 246, 6), _val(raw, 247, 6)],
        'Midline': [_val(raw, 244, 7), _val(raw, 245, 7), _val(raw, 246, 7), _val(raw, 247, 7)],
    })

    # Actions agreed (Rows 252-255, cols 2-3)
    data['ge_actions'] = pd.DataFrame({
        'Category': ['No', 'Partially', 'Yes'],
        'Baseline': [_val(raw, 252, 2), _val(raw, 253, 2), _val(raw, 254, 2)],
        'Midline': [_val(raw, 252, 3), _val(raw, 253, 3), _val(raw, 254, 3)],
    })

    # Actions completion (Rows 259-263, cols 2-3)
    data['ge_completion'] = pd.DataFrame({
        'Category': ['None', 'A Few', 'Many', 'All'],
        'Baseline': [_val(raw, 259, 2), _val(raw, 260, 2), _val(raw, 261, 2), _val(raw, 262, 2)],
        'Midline': [_val(raw, 259, 3), _val(raw, 260, 3), _val(raw, 261, 3), _val(raw, 262, 3)],
    })

    # --- 9. FOREST CONDITION & THREATS ---
    # Condition (Rows 271-276, cols 2-7: Baseline Good/Med/Poor, Midline Good/Med/Poor)
    cond_labels = ['Area', 'Volume/Biomass', 'Regeneration', 'Biodiversity', 'Ecosystem Services']
    data['forest_condition'] = pd.DataFrame({
        'Characteristic': cond_labels,
        'Baseline_Good': [_val(raw, r, 2) for r in range(271, 276)],
        'Baseline_Medium': [_val(raw, r, 3) for r in range(271, 276)],
        'Baseline_Poor': [_val(raw, r, 4) for r in range(271, 276)],
        'Midline_Good': [_val(raw, r, 5) for r in range(271, 276)],
        'Midline_Medium': [_val(raw, r, 6) for r in range(271, 276)],
        'Midline_Poor': [_val(raw, r, 7) for r in range(271, 276)],
    })

    # Perceived changes (Rows 280-285, cols 2-7)
    data['forest_change'] = pd.DataFrame({
        'Characteristic': cond_labels,
        'Baseline_Decrease': [_val(raw, r, 2) for r in range(280, 285)],
        'Baseline_Increase': [_val(raw, r, 3) for r in range(280, 285)],
        'Baseline_NoChange': [_val(raw, r, 4) for r in range(280, 285)],
        'Midline_Decrease': [_val(raw, r, 5) for r in range(280, 285)],
        'Midline_Increase': [_val(raw, r, 6) for r in range(280, 285)],
        'Midline_NoChange': [_val(raw, r, 7) for r in range(280, 285)],
    })

    # Threat levels (Rows 290-298, cols 2-7)
    threat_labels = ['Fire', 'Fuelwood', 'Charcoal', 'Other Wood', 'Poaching',
                     'Encroachment', 'Land Grabbing', 'Poles']
    data['threats'] = pd.DataFrame({
        'Threat': threat_labels,
        'Baseline_Low': [_val(raw, r, 2) for r in range(290, 298)],
        'Baseline_Medium': [_val(raw, r, 3) for r in range(290, 298)],
        'Baseline_High': [_val(raw, r, 4) for r in range(290, 298)],
        'Midline_Low': [_val(raw, r, 5) for r in range(290, 298)],
        'Midline_Medium': [_val(raw, r, 6) for r in range(290, 298)],
        'Midline_High': [_val(raw, r, 7) for r in range(290, 298)],
    })

    # Threat changes (Rows 302-310, cols 2-7)
    data['threat_changes'] = pd.DataFrame({
        'Threat': threat_labels,
        'Baseline_Decrease': [_val(raw, r, 2) for r in range(302, 310)],
        'Baseline_Increase': [_val(raw, r, 3) for r in range(302, 310)],
        'Baseline_NoChange': [_val(raw, r, 4) for r in range(302, 310)],
        'Midline_Decrease': [_val(raw, r, 5) for r in range(302, 310)],
        'Midline_Increase': [_val(raw, r, 6) for r in range(302, 310)],
        'Midline_NoChange': [_val(raw, r, 7) for r in range(302, 310)],
    })

    # Harvest amount (Rows 314-322, cols 2-7)
    harvest_labels = ['Timber', 'Woodfuel', 'Poles', 'Fodder', 'Leaf Mulch',
                      'Wildlife', 'Food', 'NWFPs']
    data['harvest_amount'] = pd.DataFrame({
        'Product': harvest_labels,
        'Baseline_None': [_val(raw, r, 2) for r in range(314, 322)],
        'Baseline_Medium': [_val(raw, r, 3) for r in range(314, 322)],
        'Baseline_Substantial': [_val(raw, r, 4) for r in range(314, 322)],
        'Midline_None': [_val(raw, r, 5) for r in range(314, 322)],
        'Midline_Medium': [_val(raw, r, 6) for r in range(314, 322)],
        'Midline_Substantial': [_val(raw, r, 7) for r in range(314, 322)],
    })

    # Harvest changes (Rows 326-334, cols 2-9)
    data['harvest_changes'] = pd.DataFrame({
        'Product': harvest_labels,
        'Baseline_Decrease': [_val(raw, r, 2) for r in range(326, 334)],
        'Baseline_NoChange': [_val(raw, r, 3) for r in range(326, 334)],
        'Baseline_Increase': [_val(raw, r, 4) for r in range(326, 334)],
        'Baseline_DontKnow': [_val(raw, r, 5) for r in range(326, 334)],
        'Midline_Decrease': [_val(raw, r, 6) for r in range(326, 334)],
        'Midline_NoChange': [_val(raw, r, 7) for r in range(326, 334)],
        'Midline_Increase': [_val(raw, r, 8) for r in range(326, 334)],
        'Midline_DontKnow': [_val(raw, r, 9) for r in range(326, 334)],
    })

    # --- 10. INCOME & AGROFORESTRY ---
    # Income generated (Rows 337-339, cols 2-3)
    data['income_gen'] = pd.DataFrame({
        'Category': ['Yes', 'No'],
        'Baseline': [_val(raw, 337, 2), _val(raw, 338, 2)],
        'Midline': [_val(raw, 337, 3), _val(raw, 338, 3)],
    })

    # Income sources (Rows 342-349, cols 2-3)
    data['income_sources'] = pd.DataFrame({
        'Source': ['Timber', 'Fuelwood', 'Wildlife', 'NWFPs', 'PES', 'Poles', 'Other'],
        'Baseline': [_val(raw, r, 2) for r in range(342, 349)],
        'Midline': [_val(raw, r, 3) for r in range(342, 349)],
    })

    # Income use (Rows 352-359, cols 2-3)
    data['income_use'] = pd.DataFrame({
        'Use': ['HH Needs', 'Vulnerable Support', 'Reinvest Forest',
                'Community Initiatives', 'Individual Enterprises',
                'Community Enterprises', 'Other'],
        'Baseline': [_val(raw, r, 2) for r in range(352, 359)],
        'Midline': [_val(raw, r, 3) for r in range(352, 359)],
    })

    # Agroforestry practice (Rows 362-364, cols 2-3)
    data['agroforestry'] = pd.DataFrame({
        'Category': ['Yes', 'No'],
        'Baseline': [_val(raw, 362, 2), _val(raw, 363, 2)],
        'Midline': [_val(raw, 362, 3), _val(raw, 363, 3)],
    })

    # AF types (Rows 367-372, cols 2-3)
    data['af_types'] = pd.DataFrame({
        'Practice': ['Intercropping', 'Silvopasture', 'Alley Cropping',
                     'Forest Farming', 'Beekeeping'],
        'Baseline': [_val(raw, r, 2) for r in range(367, 372)],
        'Midline': [_val(raw, r, 3) for r in range(367, 372)],
    })

    # AF objectives (Rows 375-381, cols 2-3)
    data['af_objectives'] = pd.DataFrame({
        'Objective': ['Biodiversity', 'Soil Fertility', 'Income',
                      'Water Retention', 'Reduce Deforestation', 'Food Security'],
        'Baseline': [_val(raw, r, 2) for r in range(375, 381)],
        'Midline': [_val(raw, r, 3) for r in range(375, 381)],
    })

    # AF training received (Rows 384-386, cols 2-3)
    data['af_training'] = pd.DataFrame({
        'Category': ['Yes', 'No'],
        'Baseline': [_val(raw, 384, 2), _val(raw, 385, 2)],
        'Midline': [_val(raw, 384, 3), _val(raw, 385, 3)],
    })

    # AF support types (Rows 389-395, cols 2-3)
    data['af_support'] = pd.DataFrame({
        'Support': ['On-site Workshops', 'Materials/Seedlings', 'Market Access',
                    'Financial Assistance', 'Technical Support', 'Online Resources'],
        'Baseline': [_val(raw, r, 2) for r in range(389, 395)],
        'Midline': [_val(raw, r, 3) for r in range(389, 395)],
    })

    # AF challenges (Rows 398-405, cols 2-3)
    data['af_challenges'] = pd.DataFrame({
        'Challenge': ['Lack of Knowledge', 'Insufficient Funding', 'Market Access',
                      'Land/Property Rights', 'Environmental Constraints',
                      'Policy/Regulatory', 'Cultural Resistance'],
        'Baseline': [_val(raw, r, 2) for r in range(398, 405)],
        'Midline': [_val(raw, r, 3) for r in range(398, 405)],
    })

    # AF reinvestment (Rows 408-412, cols 2-3)
    data['af_reinvest'] = pd.DataFrame({
        'Category': ['Education & Training', 'Not Applicable', 'Land Purchase', 'Conservation Projects'],
        'Baseline': [_val(raw, r, 2) for r in range(408, 412)],
        'Midline': [_val(raw, r, 3) for r in range(408, 412)],
    })

    # AF livelihood potential (Rows 415-418, cols 2-3)
    data['af_potential'] = pd.DataFrame({
        'Category': ['Moderate', 'Significant', 'Unsure'],
        'Baseline': [_val(raw, 415, 2), _val(raw, 416, 2), _val(raw, 417, 2)],
        'Midline': [_val(raw, 415, 3), _val(raw, 416, 3), _val(raw, 417, 3)],
    })

    return data


def _val(df, row_0based, col_0based):
    """
    Safely extract a value from the raw DataFrame.
    Row and column are 0-based (matching iloc positions directly).
    Returns 0 if the value is None or NaN.
    """
    try:
        v = df.iloc[row_0based, col_0based]
        if v is None or (isinstance(v, float) and np.isnan(v)):
            return 0
        return v
    except (IndexError, KeyError):
        return 0


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def pct(value):
    """Format a decimal (0-1) as percentage string."""
    if isinstance(value, (int, float)):
        return f"{value * 100:.1f}%"
    return str(value)


def pp_change(baseline, midline):
    """Calculate percentage point change between baseline and midline (both as decimals 0-1)."""
    if isinstance(baseline, (int, float)) and isinstance(midline, (int, float)):
        return (midline - baseline) * 100
    return 0


def score_change(baseline, midline):
    """Calculate point change for scores (already in 0-100 scale)."""
    if isinstance(baseline, (int, float)) and isinstance(midline, (int, float)):
        return midline - baseline
    return 0


def make_comparison_bar(df, category_col, title, y_label="Percentage (%)",
                        multiply=True, height=450, orientation='v',
                        color_baseline=None, color_midline=None):
    """
    Create a grouped bar chart comparing Baseline vs Midline.
    
    Args:
        df: DataFrame with columns [category_col, 'Baseline', 'Midline']
        category_col: Name of the label column
        title: Chart title
        multiply: If True, multiply values by 100 (convert 0-1 to %)
        height: Chart height
    """
    cb = color_baseline or COLORS["baseline"]
    cm = color_midline or COLORS["midline"]

    plot_df = df.copy()
    if multiply:
        plot_df['Baseline'] = plot_df['Baseline'].apply(lambda x: x * 100 if isinstance(x, (int, float)) else 0)
        plot_df['Midline'] = plot_df['Midline'].apply(lambda x: x * 100 if isinstance(x, (int, float)) else 0)

    if orientation == 'h':
        fig = go.Figure()
        fig.add_trace(go.Bar(y=plot_df[category_col], x=plot_df['Baseline'],
                             name='Baseline', orientation='h',
                             marker_color=cb, text=plot_df['Baseline'].apply(lambda x: f"{x:.1f}%"),
                             textposition='auto'))
        fig.add_trace(go.Bar(y=plot_df[category_col], x=plot_df['Midline'],
                             name='Midline', orientation='h',
                             marker_color=cm, text=plot_df['Midline'].apply(lambda x: f"{x:.1f}%"),
                             textposition='auto'))
        fig.update_layout(title=title, barmode='group', height=height,
                          xaxis_title=y_label, yaxis_title='',
                          legend=dict(orientation='h', yanchor='bottom', y=1.02))
    else:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=plot_df[category_col], y=plot_df['Baseline'],
                             name='Baseline', marker_color=cb,
                             text=plot_df['Baseline'].apply(lambda x: f"{x:.1f}%"),
                             textposition='auto'))
        fig.add_trace(go.Bar(x=plot_df[category_col], y=plot_df['Midline'],
                             name='Midline', marker_color=cm,
                             text=plot_df['Midline'].apply(lambda x: f"{x:.1f}%"),
                             textposition='auto'))
        fig.update_layout(title=title, barmode='group', height=height,
                          yaxis_title=y_label, xaxis_title='',
                          legend=dict(orientation='h', yanchor='bottom', y=1.02))

    fig.update_layout(
        font=dict(size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    return fig


def make_stacked_bar(df, category_col, columns, colors_list, title,
                     y_label="Percentage (%)", height=400, multiply=True,
                     orientation='v'):
    """Create a stacked bar chart for multi-category data."""
    plot_df = df.copy()
    if multiply:
        for c in columns:
            plot_df[c] = plot_df[c].apply(lambda x: x * 100 if isinstance(x, (int, float)) else 0)

    fig = go.Figure()
    for col, color in zip(columns, colors_list):
        label = col.replace('Baseline_', '').replace('Midline_', '')
        if orientation == 'h':
            fig.add_trace(go.Bar(y=plot_df[category_col], x=plot_df[col],
                                 name=label, orientation='h', marker_color=color,
                                 text=plot_df[col].apply(lambda x: f"{x:.1f}%" if x > 3 else ""),
                                 textposition='inside'))
        else:
            fig.add_trace(go.Bar(x=plot_df[category_col], y=plot_df[col],
                                 name=label, marker_color=color,
                                 text=plot_df[col].apply(lambda x: f"{x:.1f}%" if x > 3 else ""),
                                 textposition='inside'))

    fig.update_layout(title=title, barmode='stack', height=height,
                      yaxis_title=y_label if orientation == 'v' else '',
                      xaxis_title=y_label if orientation == 'h' else '',
                      legend=dict(orientation='h', yanchor='bottom', y=1.02),
                      font=dict(size=12),
                      plot_bgcolor='rgba(0,0,0,0)',
                      paper_bgcolor='rgba(0,0,0,0)')
    return fig


def make_delta_bar(df, category_col, title, multiply=True, height=400):
    """Create a horizontal bar chart showing change (Midline - Baseline) in pp."""
    plot_df = df.copy()
    factor = 100 if multiply else 1
    plot_df['Change'] = (plot_df['Midline'] - plot_df['Baseline']) * factor
    plot_df = plot_df.sort_values('Change')

    colors = [COLORS['good'] if v >= 0 else COLORS['danger'] for v in plot_df['Change']]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=plot_df[category_col], x=plot_df['Change'],
        orientation='h', marker_color=colors,
        text=plot_df['Change'].apply(lambda x: f"{x:+.1f}pp"),
        textposition='auto'
    ))
    fig.update_layout(title=title, height=height,
                      xaxis_title="Change (percentage points)",
                      font=dict(size=12),
                      plot_bgcolor='rgba(0,0,0,0)',
                      paper_bgcolor='rgba(0,0,0,0)')
    return fig


# ============================================================================
# STREAMLIT APP — MAIN FUNCTION
# ============================================================================

def main():
    st.set_page_config(
        page_title="Forestry Conservation Dashboard",
        page_icon="🌲",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # ---- THEME SELECTOR (must come before CSS injection) ----
    theme_name = st.sidebar.selectbox(
        "🎨 Dashboard Theme",
        list(THEMES.keys()),
        index=0,
        help="Choose a color palette for all charts and UI elements"
    )
    # Apply selected theme globally
    global COLORS
    COLORS = THEMES[theme_name]

    # Custom CSS — driven by the active theme
    st.markdown(f"""
    <style>
    .main-header {{
        background: {COLORS['header_gradient']};
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
    }}
    .main-header h1 {{ margin: 0; font-size: 2rem; }}
    .main-header p {{ margin: 0.3rem 0 0; opacity: 0.9; font-size: 1rem; }}
    .kpi-card {{
        background: white;
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
        border-left: 4px solid {COLORS['card_border']};
    }}
    .kpi-card h3 {{ font-size: 0.85rem; color: #666; margin: 0 0 0.3rem; }}
    .kpi-card .value {{ font-size: 2rem; font-weight: 700; color: {COLORS['card_value']}; }}
    .kpi-card .delta {{ font-size: 0.9rem; margin-top: 0.2rem; }}
    .delta-positive {{ color: {COLORS['good']}; }}
    .delta-negative {{ color: {COLORS['danger']}; }}
    .section-narrative {{
        background: {COLORS['narrative_bg']};
        border-left: 4px solid {COLORS['narrative_border']};
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1rem;
        font-size: 0.95rem;
        color: {COLORS['narrative_text']};
    }}
    div[data-testid="stMetricValue"] {{ font-size: 1.4rem; }}
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌲 Community Forest Conservation Dashboard</h1>
        <p>Baseline vs Midline Assessment | Forestry Conservation Groups Functionality</p>
    </div>
    """, unsafe_allow_html=True)

    # ---- SIDEBAR ----
    st.sidebar.image("https://img.icons8.com/color/96/forest.png", width=80)
    st.sidebar.title("🌿 Dashboard Controls")
    st.sidebar.markdown("---")

    # Resolve Excel file path (same folder as script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(script_dir, EXCEL_FILE)

    # Load data
    data = load_all_data(excel_path)

    # Sidebar controls
    timepoint_filter = st.sidebar.radio(
        "📅 Timepoint View",
        ["Both", "Baseline", "Midline"],
        index=0,
        help="Filter charts to show Baseline, Midline, or both"
    )

    show_change = st.sidebar.toggle(
        "📊 Show Change (pp) Charts",
        value=False,
        help="Toggle to show percentage point change charts instead of side-by-side"
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("**📋 Data Summary**")
    bl_groups = data['num_groups'].loc[data['num_groups']['Timepoint'] == 'Baseline', 'Groups_Assessed'].values[0]
    ml_groups = data['num_groups'].loc[data['num_groups']['Timepoint'] == 'Midline', 'Groups_Assessed'].values[0]
    st.sidebar.metric("Baseline Groups", int(bl_groups))
    st.sidebar.metric("Midline Groups", int(ml_groups))

    # ---- TABS ----
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview",
        "👥 Group Characteristics",
        "🏛️ Governance & Gender",
        "📚 Training & Assets",
        "🌳 Forest Condition & Threats",
        "💰 Income & Agroforestry"
    ])

    # ===========================================================================
    # TAB 1: OVERVIEW
    # ===========================================================================
    with tab1:
        st.markdown("""
        <div class="section-narrative">
        <strong>Overview:</strong> This section presents the key performance indicators (KPIs) for Community 
        Forestry Conservation Groups, comparing baseline and midline assessments. The functionality 
        threshold shows the percentage of groups meeting minimum performance standards, while domain 
        scores break down performance across Management, Gender, and Effectiveness dimensions.
        </div>
        """, unsafe_allow_html=True)

        # KPI Cards
        ft = data['functionality_threshold']
        fs = data['functionality_scores']
        fd = data['functionality_domain']

        bl_60 = ft.loc[ft['Timepoint'] == 'Baseline', 'Functional_60_pct'].values[0]
        ml_60 = ft.loc[ft['Timepoint'] == 'Midline', 'Functional_60_pct'].values[0]
        bl_70 = ft.loc[ft['Timepoint'] == 'Baseline', 'Functional_70_pct'].values[0]
        ml_70 = ft.loc[ft['Timepoint'] == 'Midline', 'Functional_70_pct'].values[0]
        bl_avg = fs.loc[fs['Timepoint'] == 'Baseline', 'Average'].values[0]
        ml_avg = fs.loc[fs['Timepoint'] == 'Midline', 'Average'].values[0]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Functional ≥60%",
                f"{ml_60 * 100:.1f}%",
                delta=f"{(ml_60 - bl_60) * 100:+.1f}pp from {bl_60 * 100:.1f}%"
            )
        with col2:
            st.metric(
                "Functional ≥70%",
                f"{ml_70 * 100:.1f}%",
                delta=f"{(ml_70 - bl_70) * 100:+.1f}pp from {bl_70 * 100:.1f}%"
            )
        with col3:
            st.metric(
                "Overall Score",
                f"{ml_avg:.1f}/100",
                delta=f"{ml_avg - bl_avg:+.1f} pts from {bl_avg:.1f}"
            )
        with col4:
            st.metric(
                "Groups Assessed",
                f"{int(ml_groups)}",
                delta=f"{int(ml_groups - bl_groups)} from {int(bl_groups)}"
            )

        st.markdown("---")

        # Domain scores chart
        col_l, col_r = st.columns([3, 2])
        with col_l:
            domain_df = pd.DataFrame({
                'Domain': ['Management', 'Gender', 'Effectiveness', 'Overall'],
                'Baseline': fd[['Management', 'Gender', 'Effectiveness', 'Overall']].iloc[0].values,
                'Midline': fd[['Management', 'Gender', 'Effectiveness', 'Overall']].iloc[1].values,
            })

            fig_domain = go.Figure()
            fig_domain.add_trace(go.Bar(
                x=domain_df['Domain'], y=domain_df['Baseline'],
                name='Baseline', marker_color=COLORS['baseline'],
                text=domain_df['Baseline'].apply(lambda x: f"{x:.1f}"),
                textposition='auto'
            ))
            fig_domain.add_trace(go.Bar(
                x=domain_df['Domain'], y=domain_df['Midline'],
                name='Midline', marker_color=COLORS['midline'],
                text=domain_df['Midline'].apply(lambda x: f"{x:.1f}"),
                textposition='auto'
            ))
            fig_domain.update_layout(
                title="Functionality Scores by Domain (0-100)",
                barmode='group', height=450,
                yaxis=dict(title='Score', range=[0, 105]),
                legend=dict(orientation='h', yanchor='bottom', y=1.02),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_domain, width='stretch')

        with col_r:
            # Delta radar chart
            change_data = domain_df.copy()
            change_data['Change'] = change_data['Midline'] - change_data['Baseline']

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=list(domain_df['Baseline']) + [domain_df['Baseline'].iloc[0]],
                theta=list(domain_df['Domain']) + [domain_df['Domain'].iloc[0]],
                fill='toself', name='Baseline',
                fillcolor=COLORS['radar_bl_fill'], line=dict(color=COLORS['baseline'])
            ))
            fig_radar.add_trace(go.Scatterpolar(
                r=list(domain_df['Midline']) + [domain_df['Midline'].iloc[0]],
                theta=list(domain_df['Domain']) + [domain_df['Domain'].iloc[0]],
                fill='toself', name='Midline',
                fillcolor=COLORS['radar_ml_fill'], line=dict(color=COLORS['midline'])
            ))
            fig_radar.update_layout(
                title="Domain Performance Radar",
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                height=450,
                legend=dict(orientation='h', yanchor='bottom', y=-0.15)
            )
            st.plotly_chart(fig_radar, width='stretch')

        # Score distributions
        st.subheader("📈 Functionality Score Statistics")
        col_stats1, col_stats2 = st.columns(2)
        with col_stats1:
            st.markdown("**Baseline**")
            stats_bl = fs[fs['Timepoint'] == 'Baseline'].iloc[0]
            st.markdown(f"- Respondents: **{int(stats_bl['Respondents'])}**")
            st.markdown(f"- Average: **{stats_bl['Average']:.1f}** | Max: **{stats_bl['Max']:.1f}** | Min: **{stats_bl['Min']:.1f}**")
        with col_stats2:
            st.markdown("**Midline**")
            stats_ml = fs[fs['Timepoint'] == 'Midline'].iloc[0]
            st.markdown(f"- Respondents: **{int(stats_ml['Respondents'])}**")
            st.markdown(f"- Average: **{stats_ml['Average']:.1f}** | Max: **{stats_ml['Max']:.1f}** | Min: **{stats_ml['Min']:.1f}**")

    # ===========================================================================
    # TAB 2: GROUP CHARACTERISTICS
    # ===========================================================================
    with tab2:
        st.markdown("""
        <div class="section-narrative">
        <strong>Group Characteristics:</strong> This section profiles the surveyed Community Forestry 
        Conservation Groups including membership composition (by sex), years of operation, type of 
        land tenure, and size of forest managed. Understanding these characteristics helps 
        contextualize performance differences between baseline and midline.
        </div>
        """, unsafe_allow_html=True)

        # Membership table
        st.subheader("👥 Group Membership Statistics")
        col_m1, col_m2, col_m3 = st.columns(3)

        with col_m1:
            st.markdown("**Average Membership**")
            avg_m = data['avg_membership']
            fig_avg = make_comparison_bar(avg_m, 'Category', 'Average Members per Group',
                                          y_label='Members', multiply=False, height=350)
            st.plotly_chart(fig_avg, width='stretch')

        with col_m2:
            st.markdown("**Maximum Membership**")
            max_m = data['max_membership']
            fig_max = make_comparison_bar(max_m, 'Category', 'Maximum Members per Group',
                                          y_label='Members', multiply=False, height=350)
            st.plotly_chart(fig_max, width='stretch')

        with col_m3:
            st.markdown("**Minimum Membership**")
            min_m = data['min_membership']
            fig_min = make_comparison_bar(min_m, 'Category', 'Minimum Members per Group',
                                          y_label='Members', multiply=False, height=350)
            st.plotly_chart(fig_min, width='stretch')

        st.markdown("---")

        # Years, Tenure, Forest Size
        col_y, col_t, col_f = st.columns(3)

        with col_y:
            st.subheader("📅 Years of Operation")
            if show_change:
                st.plotly_chart(make_delta_bar(data['years_dist'], 'Category',
                                              'Change in Years Distribution'), width='stretch')
            else:
                st.plotly_chart(make_comparison_bar(data['years_dist'], 'Category',
                                                    'Years of Operation Distribution',
                                                    height=400), width='stretch')

        with col_t:
            st.subheader("🏛️ Land Tenure")
            if show_change:
                st.plotly_chart(make_delta_bar(data['tenure'], 'Category',
                                              'Change in Tenure Distribution'), width='stretch')
            else:
                st.plotly_chart(make_comparison_bar(data['tenure'], 'Category',
                                                    'Land Tenure Type',
                                                    height=400), width='stretch')

        with col_f:
            st.subheader("🌲 Forest Size")
            if show_change:
                st.plotly_chart(make_delta_bar(data['forest_size_dist'], 'Category',
                                              'Change in Forest Size Distribution'), width='stretch')
            else:
                st.plotly_chart(make_comparison_bar(data['forest_size_dist'], 'Category',
                                                    'Forest Size Distribution (ha)',
                                                    height=400), width='stretch')

        # Forest size stats
        st.subheader("📏 Forest Size Statistics (hectares)")
        fss = data['forest_size_stats']
        cfss1, cfss2 = st.columns(2)
        with cfss1:
            st.metric("Average Forest Size (Baseline)", f"{fss.loc[fss['Stat']=='Average', 'Baseline'].values[0]:.1f} ha")
            st.metric("Average Forest Size (Midline)", f"{fss.loc[fss['Stat']=='Average', 'Midline'].values[0]:.1f} ha")
        with cfss2:
            st.metric("Max (Baseline → Midline)",
                      f"{fss.loc[fss['Stat']=='Maximum', 'Baseline'].values[0]:.0f} → {fss.loc[fss['Stat']=='Maximum', 'Midline'].values[0]:.0f} ha")
            st.metric("Min (Baseline → Midline)",
                      f"{fss.loc[fss['Stat']=='Minimum', 'Baseline'].values[0]:.1f} → {fss.loc[fss['Stat']=='Minimum', 'Midline'].values[0]:.1f} ha")

    # ===========================================================================
    # TAB 3: GOVERNANCE & GENDER
    # ===========================================================================
    with tab3:
        st.markdown("""
        <div class="section-narrative">
        <strong>Governance & Gender:</strong> This section assesses the internal governance quality of 
        Conservation Groups — including board clarity, guidelines, meeting regularity, management 
        practices, and women's leadership. It also examines gender equality discussions, agreed 
        actions, and their completion rates.
        </div>
        """, unsafe_allow_html=True)

        # Objectives & Goals
        st.subheader("🎯 Objectives, Rights & Responsibilities")
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.plotly_chart(make_comparison_bar(
                data['goals_defined'], 'Category',
                'Groups with Defined Goals/Objectives', height=350
            ), width='stretch')

        with col_g2:
            st.plotly_chart(make_comparison_bar(
                data['goals_stated'], 'Goal',
                'Stated Goals & Objectives', height=350,
                orientation='h'
            ), width='stretch')

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.plotly_chart(make_comparison_bar(
                data['rights'], 'Right',
                'Right Entitlements', height=400, orientation='h'
            ), width='stretch')

        with col_r2:
            st.plotly_chart(make_comparison_bar(
                data['responsibilities'], 'Responsibility',
                'Government Responsibilities', height=400, orientation='h'
            ), width='stretch')

        st.markdown("---")

        # Governance
        st.subheader("🏛️ Group Governance")
        col_gov1, col_gov2 = st.columns(2)

        with col_gov1:
            st.plotly_chart(make_comparison_bar(
                data['board_roles'], 'Category',
                'Management Board Role Clarity', height=380, orientation='h'
            ), width='stretch')

        with col_gov2:
            st.plotly_chart(make_comparison_bar(
                data['guidelines'], 'Category',
                'Group Guidelines Status', height=380, orientation='h'
            ), width='stretch')

        col_gov3, col_gov4 = st.columns(2)
        with col_gov3:
            st.plotly_chart(make_comparison_bar(
                data['meetings'], 'Category',
                'Meeting Frequency & Attendance', height=350, orientation='h'
            ), width='stretch')

        with col_gov4:
            st.plotly_chart(make_comparison_bar(
                data['women_leadership'], 'Category',
                "Women's Leadership Roles", height=350, orientation='h'
            ), width='stretch')

        # Management practices
        st.subheader("📋 Management Practices (% Agree/Strongly Agree)")
        mp = data['mgmt_practices']
        fig_mp = go.Figure()
        fig_mp.add_trace(go.Bar(y=mp['Practice'], x=mp['Agree_Baseline'].apply(lambda x: x*100),
                                name='Agree+SA (Baseline)', orientation='h',
                                marker_color=COLORS['baseline'],
                                text=mp['Agree_Baseline'].apply(lambda x: f"{x*100:.1f}%"),
                                textposition='auto'))
        fig_mp.add_trace(go.Bar(y=mp['Practice'], x=mp['Agree_Midline'].apply(lambda x: x*100),
                                name='Agree+SA (Midline)', orientation='h',
                                marker_color=COLORS['midline'],
                                text=mp['Agree_Midline'].apply(lambda x: f"{x*100:.1f}%"),
                                textposition='auto'))
        fig_mp.add_trace(go.Bar(y=mp['Practice'], x=mp['StronglyAgree_Baseline'].apply(lambda x: x*100),
                                name='Strongly Agree (Baseline)', orientation='h',
                                marker_color=COLORS['baseline_light'],
                                text=mp['StronglyAgree_Baseline'].apply(lambda x: f"{x*100:.1f}%"),
                                textposition='auto'))
        fig_mp.add_trace(go.Bar(y=mp['Practice'], x=mp['StronglyAgree_Midline'].apply(lambda x: x*100),
                                name='Strongly Agree (Midline)', orientation='h',
                                marker_color=COLORS['midline_light'],
                                text=mp['StronglyAgree_Midline'].apply(lambda x: f"{x*100:.1f}%"),
                                textposition='auto'))
        fig_mp.update_layout(barmode='group', height=500, xaxis_title="Percentage (%)",
                             legend=dict(orientation='h', yanchor='bottom', y=1.02),
                             plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_mp, width='stretch')

        st.markdown("---")

        # Gender equality section
        st.subheader("⚖️ Gender Equality")
        col_ge1, col_ge2 = st.columns(2)

        with col_ge1:
            st.plotly_chart(make_comparison_bar(
                data['ge_discussion'], 'Category',
                'Groups Discussing Gender Equality', height=350
            ), width='stretch')
            st.plotly_chart(make_comparison_bar(
                data['ge_actions'], 'Category',
                'Agreement on Gender Actions', height=350
            ), width='stretch')

        with col_ge2:
            st.plotly_chart(make_comparison_bar(
                data['ge_topics'], 'Topic',
                'Gender Topics Discussed', height=350, orientation='h'
            ), width='stretch')
            st.plotly_chart(make_comparison_bar(
                data['ge_completion'], 'Category',
                'Completion of Gender Actions', height=350
            ), width='stretch')

    # ===========================================================================
    # TAB 4: TRAINING & ASSETS
    # ===========================================================================
    with tab4:
        st.markdown("""
        <div class="section-narrative">
        <strong>Training & Assets:</strong> This section examines the training and capacity building 
        received by Conservation Group members, including coverage levels, specific training topics, 
        and types of assets or inputs provided to support forest management and conservation activities.
        </div>
        """, unsafe_allow_html=True)

        # Training coverage
        st.subheader("📚 Training Coverage")
        col_t1, col_t2 = st.columns(2)

        with col_t1:
            st.plotly_chart(make_comparison_bar(
                data['training_coverage'], 'Category',
                'Member Training Coverage', height=400
            ), width='stretch')

        with col_t2:
            # Stacked bar for coverage categories
            tc = data['training_coverage'].copy()
            tc['Baseline'] = tc['Baseline'] * 100
            tc['Midline'] = tc['Midline'] * 100

            fig_tc_stack = go.Figure()
            colors_stack = ['#E53935', '#FB8C00', '#FDD835', '#43A047']
            for i, (_, row) in enumerate(tc.iterrows()):
                fig_tc_stack.add_trace(go.Bar(
                    x=['Baseline', 'Midline'],
                    y=[row['Baseline'], row['Midline']],
                    name=row['Category'],
                    marker_color=colors_stack[i],
                    text=[f"{row['Baseline']:.1f}%", f"{row['Midline']:.1f}%"],
                    textposition='inside'
                ))
            fig_tc_stack.update_layout(
                title="Training Coverage (Stacked)",
                barmode='stack', height=400,
                yaxis_title="Percentage (%)",
                legend=dict(orientation='h', yanchor='bottom', y=1.02),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_tc_stack, width='stretch')

        # Training topics — with sidebar multi-select
        st.subheader("📖 Training Topics Received")

        # Sidebar filter for training topics
        all_topics = data['training_topics']['Topic'].tolist()
        selected_topics = st.sidebar.multiselect(
            "🔍 Filter Training Topics",
            all_topics,
            default=all_topics,
            help="Select which training topics to display"
        )

        filtered_topics = data['training_topics'][data['training_topics']['Topic'].isin(selected_topics)]

        if show_change:
            st.plotly_chart(make_delta_bar(filtered_topics, 'Topic',
                                           'Change in Training Topic Coverage (pp)',
                                           height=500), width='stretch')
        else:
            st.plotly_chart(make_comparison_bar(
                filtered_topics, 'Topic',
                'Training Topics Received by Groups', height=600, orientation='h'
            ), width='stretch')

        st.markdown("---")

        # Assets
        st.subheader("🧰 Assets & Inputs Received")
        col_a1, col_a2 = st.columns(2)

        with col_a1:
            st.plotly_chart(make_comparison_bar(
                data['assets_received'], 'Category',
                '% Groups Receiving Assets', height=350
            ), width='stretch')

        with col_a2:
            st.plotly_chart(make_comparison_bar(
                data['asset_types'], 'Asset',
                'Type of Asset Received', height=400, orientation='h'
            ), width='stretch')

    # ===========================================================================
    # TAB 5: FOREST CONDITION & THREATS
    # ===========================================================================
    with tab5:
        st.markdown("""
        <div class="section-narrative">
        <strong>Forest Condition & Threats:</strong> This section presents groups' perceived condition 
        of forest characteristics (area, biomass, regeneration, biodiversity, ecosystem services), 
        changes over time, threat levels, and sustainable harvesting patterns. Green tones indicate 
        improvements; red tones indicate deterioration.
        </div>
        """, unsafe_allow_html=True)

        # Forest condition heatmap-style views
        st.subheader("🌲 Perceived Forest Condition")

        tp_cond = st.radio("Select Timepoint for Condition", ["Baseline", "Midline"], 
                           horizontal=True, key="cond_tp")

        fc = data['forest_condition']
        if tp_cond == "Baseline":
            cols_show = ['Baseline_Good', 'Baseline_Medium', 'Baseline_Poor']
            col_labels = ['Good', 'Medium', 'Poor']
        else:
            cols_show = ['Midline_Good', 'Midline_Medium', 'Midline_Poor']
            col_labels = ['Good', 'Medium', 'Poor']

        fig_cond = make_stacked_bar(fc, 'Characteristic', cols_show,
                                     [COLORS['good'], COLORS['medium'], COLORS['poor']],
                                     f'Forest Condition — {tp_cond}', height=400)
        # Rename legend labels
        for i, trace in enumerate(fig_cond.data):
            trace.name = col_labels[i]
        st.plotly_chart(fig_cond, width='stretch')

        st.markdown("---")

        # Perceived changes
        st.subheader("📈 Perceived Changes in Forest Characteristics")
        tp_change = st.radio("Select Timepoint for Changes", ["Baseline", "Midline"],
                             horizontal=True, key="change_tp")

        fch = data['forest_change']
        if tp_change == "Baseline":
            ch_cols = ['Baseline_Decrease', 'Baseline_NoChange', 'Baseline_Increase']
        else:
            ch_cols = ['Midline_Decrease', 'Midline_NoChange', 'Midline_Increase']

        fig_change = make_stacked_bar(fch, 'Characteristic', ch_cols,
                                       [COLORS['danger'], COLORS['no_change'], COLORS['good']],
                                       f'Perceived Changes — {tp_change}', height=400)
        for i, lbl in enumerate(['Decrease', 'No Change', 'Increase']):
            fig_change.data[i].name = lbl
        st.plotly_chart(fig_change, width='stretch')

        st.markdown("---")

        # Threat levels
        st.subheader("⚠️ Threat Levels")
        col_thr1, col_thr2 = st.columns(2)

        threats = data['threats']
        with col_thr1:
            fig_thr_bl = make_stacked_bar(threats, 'Threat',
                                           ['Baseline_Low', 'Baseline_Medium', 'Baseline_High'],
                                           [COLORS['good'], COLORS['medium'], COLORS['danger']],
                                           'Threat Levels — Baseline', height=450,
                                           orientation='h')
            for i, lbl in enumerate(['Low', 'Medium', 'High']):
                fig_thr_bl.data[i].name = lbl
            st.plotly_chart(fig_thr_bl, width='stretch')

        with col_thr2:
            fig_thr_ml = make_stacked_bar(threats, 'Threat',
                                           ['Midline_Low', 'Midline_Medium', 'Midline_High'],
                                           [COLORS['good'], COLORS['medium'], COLORS['danger']],
                                           'Threat Levels — Midline', height=450,
                                           orientation='h')
            for i, lbl in enumerate(['Low', 'Medium', 'High']):
                fig_thr_ml.data[i].name = lbl
            st.plotly_chart(fig_thr_ml, width='stretch')

        # Threat changes
        st.subheader("📉 Changes in Threat Levels")
        tc_data = data['threat_changes']
        col_tc1, col_tc2 = st.columns(2)

        with col_tc1:
            fig_tc_bl = make_stacked_bar(tc_data, 'Threat',
                                          ['Baseline_Decrease', 'Baseline_NoChange', 'Baseline_Increase'],
                                          [COLORS['good'], COLORS['no_change'], COLORS['danger']],
                                          'Threat Changes — Baseline', height=450,
                                          orientation='h')
            for i, lbl in enumerate(['Decrease', 'No Change', 'Increase']):
                fig_tc_bl.data[i].name = lbl
            st.plotly_chart(fig_tc_bl, width='stretch')

        with col_tc2:
            fig_tc_ml = make_stacked_bar(tc_data, 'Threat',
                                          ['Midline_Decrease', 'Midline_NoChange', 'Midline_Increase'],
                                          [COLORS['good'], COLORS['no_change'], COLORS['danger']],
                                          'Threat Changes — Midline', height=450,
                                          orientation='h')
            for i, lbl in enumerate(['Decrease', 'No Change', 'Increase']):
                fig_tc_ml.data[i].name = lbl
            st.plotly_chart(fig_tc_ml, width='stretch')

        st.markdown("---")

        # Harvest data
        st.subheader("🪵 Sustainable Harvesting")
        tp_harv = st.radio("Select Timepoint for Harvest", ["Baseline", "Midline"],
                           horizontal=True, key="harv_tp")

        ha = data['harvest_amount']
        if tp_harv == "Baseline":
            h_cols = ['Baseline_None', 'Baseline_Medium', 'Baseline_Substantial']
        else:
            h_cols = ['Midline_None', 'Midline_Medium', 'Midline_Substantial']

        fig_harv = make_stacked_bar(ha, 'Product', h_cols,
                                     ['#78909C', '#FB8C00', '#43A047'],
                                     f'Harvest Amount — {tp_harv}', height=450,
                                     orientation='h')
        for i, lbl in enumerate(['None', 'Medium', 'Substantial']):
            fig_harv.data[i].name = lbl
        st.plotly_chart(fig_harv, width='stretch')

    # ===========================================================================
    # TAB 6: INCOME & AGROFORESTRY
    # ===========================================================================
    with tab6:
        st.markdown("""
        <div class="section-narrative">
        <strong>Income & Agroforestry:</strong> This section examines whether Conservation Groups 
        generate income from forest resources, their income sources and uses, agroforestry practices 
        adopted, training received, challenges faced, and the perceived potential of agroforestry 
        for community livelihoods.
        </div>
        """, unsafe_allow_html=True)

        # Income generation
        st.subheader("💰 Income Generation")
        col_i1, col_i2, col_i3 = st.columns(3)

        with col_i1:
            st.plotly_chart(make_comparison_bar(
                data['income_gen'], 'Category',
                'Groups Generating Income', height=350
            ), width='stretch')

        with col_i2:
            st.plotly_chart(make_comparison_bar(
                data['income_sources'], 'Source',
                'Sources of Income', height=400, orientation='h'
            ), width='stretch')

        with col_i3:
            st.plotly_chart(make_comparison_bar(
                data['income_use'], 'Use',
                'Use of Income', height=400, orientation='h'
            ), width='stretch')

        st.markdown("---")

        # Agroforestry
        st.subheader("🌾 Agroforestry Practices")
        col_af1, col_af2 = st.columns(2)

        with col_af1:
            st.plotly_chart(make_comparison_bar(
                data['agroforestry'], 'Category',
                'Groups Practicing Agroforestry', height=350
            ), width='stretch')

        with col_af2:
            st.plotly_chart(make_comparison_bar(
                data['af_types'], 'Practice',
                'Type of Agroforestry Practices', height=350, orientation='h'
            ), width='stretch')

        col_af3, col_af4 = st.columns(2)

        with col_af3:
            st.plotly_chart(make_comparison_bar(
                data['af_objectives'], 'Objective',
                'Objectives of Agroforestry', height=400, orientation='h'
            ), width='stretch')

        with col_af4:
            st.plotly_chart(make_comparison_bar(
                data['af_training'], 'Category',
                'AF Training Received', height=350
            ), width='stretch')

        st.markdown("---")

        # Support, Challenges, Reinvestment, Potential
        st.subheader("🤝 Support, Challenges & Potential")
        col_s1, col_s2 = st.columns(2)

        with col_s1:
            if show_change:
                st.plotly_chart(make_delta_bar(
                    data['af_support'], 'Support',
                    'Change in AF Support Types (pp)', height=380
                ), width='stretch')
            else:
                st.plotly_chart(make_comparison_bar(
                    data['af_support'], 'Support',
                    'AF Support Types Received', height=380, orientation='h'
                ), width='stretch')

        with col_s2:
            if show_change:
                st.plotly_chart(make_delta_bar(
                    data['af_challenges'], 'Challenge',
                    'Change in AF Challenges (pp)', height=380
                ), width='stretch')
            else:
                st.plotly_chart(make_comparison_bar(
                    data['af_challenges'], 'Challenge',
                    'Challenges in Agroforestry', height=380, orientation='h'
                ), width='stretch')

        col_s3, col_s4 = st.columns(2)

        with col_s3:
            st.plotly_chart(make_comparison_bar(
                data['af_reinvest'], 'Category',
                'AF Income Reinvestment', height=380, orientation='h'
            ), width='stretch')

        with col_s4:
            st.plotly_chart(make_comparison_bar(
                data['af_potential'], 'Category',
                'Perceived Livelihood Potential', height=350
            ), width='stretch')

    # ---- Footer ----
    st.markdown("---")
    st.markdown(
        """<div style='text-align:center; color:#888; font-size:0.85rem;'>
        🌲 Community Forest Conservation Dashboard | Baseline vs Midline Assessment<br>
        Data Source: Forest Functionality Assessment Surveys | Generated with Streamlit + Plotly
        </div>""",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

# ============================================================================
# INSTRUCTIONS:
# Run with:  streamlit run forestry_dashboard.py
#
# Requirements:
#   pip install streamlit pandas numpy plotly openpyxl
#
# To change the Excel file:
#   - Update EXCEL_FILE variable at the top of this script
#   - Update SHEET_NAME if your sheet has a different name
#
# To adjust column mappings:
#   - Each data section in load_all_data() reads from specific row/column
#     positions in the Excel sheet. Adjust _val(raw, row, col) calls if
#     your Excel layout differs.
#
# To add a new indicator to a chart:
#   - Add the new data reading in load_all_data()
#   - Use make_comparison_bar() or make_stacked_bar() to create a chart
#   - Place the chart in the appropriate tab section
# ============================================================================
