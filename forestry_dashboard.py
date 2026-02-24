"""
=============================================================================
COSME INTEGRATED DASHBOARD
Baseline vs Midline Assessment
  1. Community Forest Conservation Groups (Group-level)
  2. Women's Survey (Household-level)
=============================================================================
A Streamlit + Plotly interactive dashboard for M&E analysis of the COSME
project, combining Forestry Conservation Groups and Women Survey datasets.

Excel files (place in the same folder as this script):
  • Forest Functionality Basline_midline results.xlsx (sheet "Results")
  • Women Survey Basline_midline results.xlsx (sheet "Results Women")

Run with: streamlit run cosme_dashboard.py
Requirements: pip install streamlit pandas numpy plotly openpyxl
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, re

# ============================================================================
# CONFIGURATION
# ============================================================================
FORESTRY_EXCEL = "Forest Functionality Basline_midline results.xlsx"
FORESTRY_SHEET = "Results"

WOMEN_EXCEL = "Women Survey Basline_midline results.xlsx"
WOMEN_SHEET = "Results Women"

# ============================================================================
# THEMES
# ============================================================================
THEMES = {
    "Forest Green": {
        "baseline": "#5B8DB8", "midline": "#2E7D32",
        "baseline_light": "#A3C4DC", "midline_light": "#81C784",
        "accent": "#FF8F00", "danger": "#E53935",
        "good": "#43A047", "medium": "#FB8C00",
        "poor": "#E53935", "low": "#43A047",
        "high": "#E53935", "decrease": "#43A047",
        "increase": "#E53935", "no_change": "#78909C",
        "header_gradient": "linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #388E3C 100%)",
        "card_border": "#2E7D32", "card_value": "#1B5E20",
        "narrative_bg": "#E8F5E9", "narrative_border": "#2E7D32",
        "narrative_text": "#1B5E20",
        "radar_bl_fill": "rgba(91,141,184,0.3)",
        "radar_ml_fill": "rgba(46,125,50,0.3)",
    },
    "Ocean Blue": {
        "baseline": "#1565C0", "midline": "#00838F",
        "baseline_light": "#90CAF9", "midline_light": "#80DEEA",
        "accent": "#FF6F00", "danger": "#D32F2F",
        "good": "#00897B", "medium": "#F9A825",
        "poor": "#D32F2F", "low": "#00897B",
        "high": "#D32F2F", "decrease": "#00897B",
        "increase": "#D32F2F", "no_change": "#78909C",
        "header_gradient": "linear-gradient(135deg, #0D47A1 0%, #1565C0 50%, #1976D2 100%)",
        "card_border": "#1565C0", "card_value": "#0D47A1",
        "narrative_bg": "#E3F2FD", "narrative_border": "#1565C0",
        "narrative_text": "#0D47A1",
        "radar_bl_fill": "rgba(21,101,192,0.3)",
        "radar_ml_fill": "rgba(0,131,143,0.3)",
    },
    "Sunset": {
        "baseline": "#E65100", "midline": "#AD1457",
        "baseline_light": "#FFB74D", "midline_light": "#F48FB1",
        "accent": "#FDD835", "danger": "#B71C1C",
        "good": "#388E3C", "medium": "#F9A825",
        "poor": "#B71C1C", "low": "#388E3C",
        "high": "#B71C1C", "decrease": "#388E3C",
        "increase": "#B71C1C", "no_change": "#78909C",
        "header_gradient": "linear-gradient(135deg, #BF360C 0%, #E65100 50%, #F4511E 100%)",
        "card_border": "#E65100", "card_value": "#BF360C",
        "narrative_bg": "#FBE9E7", "narrative_border": "#E65100",
        "narrative_text": "#BF360C",
        "radar_bl_fill": "rgba(230,81,0,0.3)",
        "radar_ml_fill": "rgba(173,20,87,0.3)",
    },
    "Earth Tones": {
        "baseline": "#6D4C41", "midline": "#33691E",
        "baseline_light": "#BCAAA4", "midline_light": "#A5D6A7",
        "accent": "#FF8F00", "danger": "#C62828",
        "good": "#558B2F", "medium": "#F9A825",
        "poor": "#C62828", "low": "#558B2F",
        "high": "#C62828", "decrease": "#558B2F",
        "increase": "#C62828", "no_change": "#8D6E63",
        "header_gradient": "linear-gradient(135deg, #3E2723 0%, #5D4037 50%, #6D4C41 100%)",
        "card_border": "#6D4C41", "card_value": "#3E2723",
        "narrative_bg": "#EFEBE9", "narrative_border": "#6D4C41",
        "narrative_text": "#3E2723",
        "radar_bl_fill": "rgba(109,76,65,0.3)",
        "radar_ml_fill": "rgba(51,105,30,0.3)",
    },
    "Professional": {
        "baseline": "#37474F", "midline": "#1565C0",
        "baseline_light": "#B0BEC5", "midline_light": "#90CAF9",
        "accent": "#FF6F00", "danger": "#C62828",
        "good": "#2E7D32", "medium": "#EF6C00",
        "poor": "#C62828", "low": "#2E7D32",
        "high": "#C62828", "decrease": "#2E7D32",
        "increase": "#C62828", "no_change": "#78909C",
        "header_gradient": "linear-gradient(135deg, #263238 0%, #37474F 50%, #455A64 100%)",
        "card_border": "#37474F", "card_value": "#263238",
        "narrative_bg": "#ECEFF1", "narrative_border": "#37474F",
        "narrative_text": "#263238",
        "radar_bl_fill": "rgba(55,71,79,0.3)",
        "radar_ml_fill": "rgba(21,101,192,0.3)",
    },
}

COLORS = THEMES["Forest Green"]

# ============================================================================
# UTILITY helpers
# ============================================================================

def _val(df, row, col):
    """Safely extract a value from the raw DataFrame (0-based row/col)."""
    try:
        v = df.iloc[row, col]
        if v is None or (isinstance(v, float) and np.isnan(v)):
            return 0
        return v
    except (IndexError, KeyError):
        return 0


def _clean_label(s):
    """Strip trailing tabs/whitespace and normalise asset/indicator labels."""
    if isinstance(s, str):
        s = re.sub(r'[\t]+', '', s).strip().rstrip('-')
        # Title-case and replace underscores
        s = s.replace('_', ' ').strip()
        if s and s[0].islower():
            s = s.title()
        return s
    return str(s)


def pct(value):
    if isinstance(value, (int, float)):
        return f"{value * 100:.1f}%"
    return str(value)


def pp_change(bl, ml):
    if isinstance(bl, (int, float)) and isinstance(ml, (int, float)):
        return (ml - bl) * 100
    return 0


# ============================================================================
# FORESTRY DATA LOADER (unchanged from forestry_dashboard.py)
# ============================================================================

@st.cache_data
def load_forestry_data(filepath):
    try:
        raw = pd.read_excel(filepath, sheet_name=FORESTRY_SHEET, header=None)
    except FileNotFoundError:
        st.error(f"Forestry Excel not found: {filepath}")
        st.stop()

    data = {}

    data['functionality_threshold'] = pd.DataFrame({
        'Timepoint': ['Baseline', 'Midline'],
        'Functional_60_pct': [_val(raw, 7, 2), _val(raw, 8, 2)],
        'Functional_70_pct': [_val(raw, 7, 3), _val(raw, 8, 3)],
    })
    data['functionality_scores'] = pd.DataFrame({
        'Timepoint': ['Baseline', 'Midline'],
        'Respondents': [_val(raw, 13, 2), _val(raw, 14, 2)],
        'Average': [_val(raw, 13, 3), _val(raw, 14, 3)],
        'Max': [_val(raw, 13, 4), _val(raw, 14, 4)],
        'Min': [_val(raw, 13, 5), _val(raw, 14, 5)],
    })
    data['functionality_domain'] = pd.DataFrame({
        'Timepoint': ['Baseline', 'Midline'],
        'Management': [_val(raw, 19, 2), _val(raw, 20, 2)],
        'Gender': [_val(raw, 19, 3), _val(raw, 20, 3)],
        'Effectiveness': [_val(raw, 19, 4), _val(raw, 20, 4)],
        'Overall': [_val(raw, 19, 5), _val(raw, 20, 5)],
    })
    data['num_groups'] = pd.DataFrame({
        'Timepoint': ['Baseline', 'Midline'],
        'Groups_Assessed': [_val(raw, 27, 2), _val(raw, 27, 3)],
    })
    data['avg_membership'] = pd.DataFrame({
        'Category': ['Male', 'Female', 'All'],
        'Baseline': [_val(raw, 32, 2), _val(raw, 33, 2), _val(raw, 34, 2)],
        'Midline': [_val(raw, 32, 3), _val(raw, 33, 3), _val(raw, 34, 3)],
    })
    data['max_membership'] = pd.DataFrame({
        'Category': ['Male', 'Female', 'All'],
        'Baseline': [_val(raw, 39, 2), _val(raw, 40, 2), _val(raw, 41, 2)],
        'Midline': [_val(raw, 39, 3), _val(raw, 40, 3), _val(raw, 41, 3)],
    })
    data['min_membership'] = pd.DataFrame({
        'Category': ['Male', 'Female', 'All'],
        'Baseline': [_val(raw, 46, 2), _val(raw, 47, 2), _val(raw, 48, 2)],
        'Midline': [_val(raw, 46, 3), _val(raw, 47, 3), _val(raw, 48, 3)],
    })
    data['years_stats'] = pd.DataFrame({
        'Stat': ['Average', 'Maximum', 'Minimum'],
        'Baseline': [_val(raw, 53, 2), _val(raw, 54, 2), _val(raw, 55, 2)],
        'Midline': [_val(raw, 53, 3), _val(raw, 54, 3), _val(raw, 55, 3)],
    })
    data['years_dist'] = pd.DataFrame({
        'Category': ['0-3 years', '4-5 years', '6-10 years', '11+ years'],
        'Baseline': [_val(raw, 57, 2), _val(raw, 58, 2), _val(raw, 59, 2), _val(raw, 60, 2)],
        'Midline': [_val(raw, 57, 3), _val(raw, 58, 3), _val(raw, 59, 3), _val(raw, 60, 3)],
    })
    data['tenure'] = pd.DataFrame({
        'Category': ['Community', 'Government', 'Govt Devolved', 'Individual', 'Other'],
        'Baseline': [_val(raw, 65, 2), _val(raw, 66, 2), _val(raw, 67, 2), _val(raw, 68, 2), _val(raw, 69, 2)],
        'Midline': [_val(raw, 65, 3), _val(raw, 66, 3), _val(raw, 67, 3), _val(raw, 68, 3), _val(raw, 69, 3)],
    })
    data['forest_size_stats'] = pd.DataFrame({
        'Stat': ['Average', 'Maximum', 'Minimum'],
        'Baseline': [_val(raw, 74, 2), _val(raw, 75, 2), _val(raw, 76, 2)],
        'Midline': [_val(raw, 74, 3), _val(raw, 75, 3), _val(raw, 76, 3)],
    })
    data['forest_size_dist'] = pd.DataFrame({
        'Category': ['0 ha', '1-5 ha', '6-10 ha', '11-100 ha', '101-999 ha', '1000+ ha'],
        'Baseline': [_val(raw, 78, 2), _val(raw, 79, 2), _val(raw, 80, 2), _val(raw, 81, 2), _val(raw, 82, 2), _val(raw, 83, 2)],
        'Midline': [_val(raw, 78, 3), _val(raw, 79, 3), _val(raw, 80, 3), _val(raw, 81, 3), _val(raw, 82, 3), _val(raw, 83, 3)],
    })
    data['goals_defined'] = pd.DataFrame({
        'Category': ['No', 'Partially', 'Yes'],
        'Baseline': [_val(raw, 91, 2), _val(raw, 92, 2), _val(raw, 93, 2)],
        'Midline': [_val(raw, 91, 3), _val(raw, 92, 3), _val(raw, 93, 3)],
    })
    data['goals_stated'] = pd.DataFrame({
        'Goal': ['Sustain Forest Resources', 'Local Livelihoods/Poverty',
                 'Protect Local Rights', 'Public Rights/State Control', 'Other'],
        'Baseline': [_val(raw, 98, 9), _val(raw, 99, 9), _val(raw, 100, 9), _val(raw, 101, 9), _val(raw, 102, 9)],
        'Midline': [_val(raw, 98, 10), _val(raw, 99, 10), _val(raw, 100, 10), _val(raw, 101, 10), _val(raw, 102, 10)],
    })
    data['rights'] = pd.DataFrame({
        'Right': ['Access', 'Withdrawal (Subsistence)', 'Withdrawal (Commercial)',
                  'Management', 'Exclusion', 'Alienation', 'Compensation', "Don't Know"],
        'Baseline': [_val(raw, r, 9) for r in range(107, 115)],
        'Midline': [_val(raw, r, 10) for r in range(107, 115)],
    })
    resp_labels = ['Register Group', 'EIA', 'Management Plan', 'Forestry Inventory',
                   'Approval NWFP', 'Approval Grazing', 'Approval Fuelwood', 'Approval Timber',
                   'Approval Transport/Sale', 'Pay Tax', 'Certification',
                   'Monitor Restrictions', 'Other', "Don't Know"]
    data['responsibilities'] = pd.DataFrame({
        'Responsibility': resp_labels,
        'Baseline': [_val(raw, r, 8) for r in range(119, 133)],
        'Midline': [_val(raw, r, 9) for r in range(119, 133)],
    })
    data['board_roles'] = pd.DataFrame({
        'Category': ['Well Defined & Understood', 'Well Defined, Not All Understand',
                      'Not Defined at All', 'Not Well Defined, Not Understood'],
        'Baseline': [_val(raw, 140, 11), _val(raw, 141, 11), _val(raw, 142, 11), _val(raw, 143, 11)],
        'Midline': [_val(raw, 140, 12), _val(raw, 141, 12), _val(raw, 142, 12), _val(raw, 143, 12)],
    })
    data['guidelines'] = pd.DataFrame({
        'Category': ['Adopted & Known Most', 'Approved & Known Some',
                      'Drafted & Known Few', 'No Guidelines'],
        'Baseline': [_val(raw, 148, 5), _val(raw, 149, 5), _val(raw, 150, 5), _val(raw, 151, 5)],
        'Midline': [_val(raw, 148, 6), _val(raw, 149, 6), _val(raw, 150, 6), _val(raw, 151, 6)],
    })
    data['meetings'] = pd.DataFrame({
        'Category': ['Occasional / Low Attendance', 'Often / Moderate Attendance',
                      'Regular / Full Quorum'],
        'Baseline': [_val(raw, 156, 11), _val(raw, 157, 11), _val(raw, 158, 11)],
        'Midline': [_val(raw, 156, 12), _val(raw, 157, 12), _val(raw, 158, 12)],
    })
    data['women_leadership'] = pd.DataFrame({
        'Category': ['No Leadership, No Voice', 'No Leadership, Occasional Voice',
                      'Some Leadership', 'Significant Leadership'],
        'Baseline': [_val(raw, 163, 12), _val(raw, 164, 12), _val(raw, 165, 12), _val(raw, 166, 12)],
        'Midline': [_val(raw, 163, 13), _val(raw, 164, 13), _val(raw, 165, 13), _val(raw, 166, 13)],
    })
    mgmt_labels = ['Transparent Elections', 'Inclusive Decisions', 'Clear Procedures',
                   'Grievance Mechanism', 'Benefit Sharing Rules', 'Decisions Communicated']
    data['mgmt_practices'] = pd.DataFrame({
        'Practice': mgmt_labels,
        'Agree_Baseline': [_val(raw, r, 8) for r in range(173, 179)],
        'Agree_Midline': [_val(raw, r, 9) for r in range(173, 179)],
        'StronglyAgree_Baseline': [_val(raw, r, 10) for r in range(173, 179)],
        'StronglyAgree_Midline': [_val(raw, r, 11) for r in range(173, 179)],
    })
    data['training_coverage'] = pd.DataFrame({
        'Category': ['None', 'A Few Members', 'Many Members', 'Most Members'],
        'Baseline': [_val(raw, 186, 4), _val(raw, 187, 4), _val(raw, 188, 4), _val(raw, 189, 4)],
        'Midline': [_val(raw, 186, 5), _val(raw, 187, 5), _val(raw, 188, 5), _val(raw, 189, 5)],
    })
    topic_labels = ['Climate Change & Forests', 'People & Forests', 'CFM Concepts',
                    'Policy & Regulatory', 'Group Establishment', 'Participation',
                    'Leadership', 'Forest Assessment', 'Socioeconomic Assessment',
                    'Visioning & Objectives', 'Group Management', 'Group Registration',
                    'Environmental Impact Assessment', 'Management Plan',
                    'Forest Livelihoods', 'Forest Enterprises',
                    'Gender & Governance', 'Gender & Environment',
                    'Disaster Risk Management', 'Other']
    data['training_topics'] = pd.DataFrame({
        'Topic': topic_labels,
        'Baseline': [_val(raw, r, 6) for r in range(194, 214)],
        'Midline': [_val(raw, r, 7) for r in range(194, 214)],
    })
    data['assets_received'] = pd.DataFrame({
        'Category': ['No', 'Yes'],
        'Baseline': [_val(raw, 218, 2), _val(raw, 219, 2)],
        'Midline': [_val(raw, 218, 3), _val(raw, 219, 3)],
    })
    data['asset_types'] = pd.DataFrame({
        'Asset': ['Seedlings/Nursery', 'Agricultural Inputs', 'Energy (Solar/Stoves)',
                  'Water & Irrigation', 'Tools & Equipment', 'Beekeeping Inputs', 'Infrastructure'],
        'Baseline': [_val(raw, 224, 2), _val(raw, 225, 2), _val(raw, 226, 2), _val(raw, 227, 2),
                     _val(raw, 228, 2), _val(raw, 229, 2), _val(raw, 230, 2)],
        'Midline': [_val(raw, 224, 3), _val(raw, 225, 3), _val(raw, 226, 3), _val(raw, 227, 3),
                     _val(raw, 228, 3), _val(raw, 229, 3), _val(raw, 230, 3)],
    })
    data['ge_discussion'] = pd.DataFrame({
        'Category': ['No', 'Yes'],
        'Baseline': [_val(raw, 238, 2), _val(raw, 239, 2)],
        'Midline': [_val(raw, 238, 3), _val(raw, 239, 3)],
    })
    data['ge_topics'] = pd.DataFrame({
        'Topic': ['Equitable Roles/Responsibilities', 'Resource Sharing',
                  'Women Leadership & Voice', 'Other'],
        'Baseline': [_val(raw, 244, 6), _val(raw, 245, 6), _val(raw, 246, 6), _val(raw, 247, 6)],
        'Midline': [_val(raw, 244, 7), _val(raw, 245, 7), _val(raw, 246, 7), _val(raw, 247, 7)],
    })
    data['ge_actions'] = pd.DataFrame({
        'Category': ['No', 'Partially', 'Yes'],
        'Baseline': [_val(raw, 252, 2), _val(raw, 253, 2), _val(raw, 254, 2)],
        'Midline': [_val(raw, 252, 3), _val(raw, 253, 3), _val(raw, 254, 3)],
    })
    data['ge_completion'] = pd.DataFrame({
        'Category': ['None', 'A Few', 'Many', 'All'],
        'Baseline': [_val(raw, 259, 2), _val(raw, 260, 2), _val(raw, 261, 2), _val(raw, 262, 2)],
        'Midline': [_val(raw, 259, 3), _val(raw, 260, 3), _val(raw, 261, 3), _val(raw, 262, 3)],
    })
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
    data['forest_change'] = pd.DataFrame({
        'Characteristic': cond_labels,
        'Baseline_Decrease': [_val(raw, r, 2) for r in range(280, 285)],
        'Baseline_Increase': [_val(raw, r, 3) for r in range(280, 285)],
        'Baseline_NoChange': [_val(raw, r, 4) for r in range(280, 285)],
        'Midline_Decrease': [_val(raw, r, 5) for r in range(280, 285)],
        'Midline_Increase': [_val(raw, r, 6) for r in range(280, 285)],
        'Midline_NoChange': [_val(raw, r, 7) for r in range(280, 285)],
    })
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
    data['threat_changes'] = pd.DataFrame({
        'Threat': threat_labels,
        'Baseline_Decrease': [_val(raw, r, 2) for r in range(302, 310)],
        'Baseline_Increase': [_val(raw, r, 3) for r in range(302, 310)],
        'Baseline_NoChange': [_val(raw, r, 4) for r in range(302, 310)],
        'Midline_Decrease': [_val(raw, r, 5) for r in range(302, 310)],
        'Midline_Increase': [_val(raw, r, 6) for r in range(302, 310)],
        'Midline_NoChange': [_val(raw, r, 7) for r in range(302, 310)],
    })
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
    data['income_gen'] = pd.DataFrame({
        'Category': ['Yes', 'No'],
        'Baseline': [_val(raw, 337, 2), _val(raw, 338, 2)],
        'Midline': [_val(raw, 337, 3), _val(raw, 338, 3)],
    })
    data['income_sources'] = pd.DataFrame({
        'Source': ['Timber', 'Fuelwood', 'Wildlife', 'NWFPs', 'PES', 'Poles', 'Other'],
        'Baseline': [_val(raw, r, 2) for r in range(342, 349)],
        'Midline': [_val(raw, r, 3) for r in range(342, 349)],
    })
    data['income_use'] = pd.DataFrame({
        'Use': ['HH Needs', 'Vulnerable Support', 'Reinvest Forest',
                'Community Initiatives', 'Individual Enterprises',
                'Community Enterprises', 'Other'],
        'Baseline': [_val(raw, r, 2) for r in range(352, 359)],
        'Midline': [_val(raw, r, 3) for r in range(352, 359)],
    })
    data['agroforestry'] = pd.DataFrame({
        'Category': ['Yes', 'No'],
        'Baseline': [_val(raw, 362, 2), _val(raw, 363, 2)],
        'Midline': [_val(raw, 362, 3), _val(raw, 363, 3)],
    })
    data['af_types'] = pd.DataFrame({
        'Practice': ['Intercropping', 'Silvopasture', 'Alley Cropping', 'Forest Farming', 'Beekeeping'],
        'Baseline': [_val(raw, r, 2) for r in range(367, 372)],
        'Midline': [_val(raw, r, 3) for r in range(367, 372)],
    })
    data['af_objectives'] = pd.DataFrame({
        'Objective': ['Biodiversity', 'Soil Fertility', 'Income', 'Water Retention', 'Reduce Deforestation', 'Food Security'],
        'Baseline': [_val(raw, r, 2) for r in range(375, 381)],
        'Midline': [_val(raw, r, 3) for r in range(375, 381)],
    })
    data['af_training'] = pd.DataFrame({
        'Category': ['Yes', 'No'],
        'Baseline': [_val(raw, 384, 2), _val(raw, 385, 2)],
        'Midline': [_val(raw, 384, 3), _val(raw, 385, 3)],
    })
    data['af_support'] = pd.DataFrame({
        'Support': ['On-site Workshops', 'Materials/Seedlings', 'Market Access',
                    'Financial Assistance', 'Technical Support', 'Online Resources'],
        'Baseline': [_val(raw, r, 2) for r in range(389, 395)],
        'Midline': [_val(raw, r, 3) for r in range(389, 395)],
    })
    data['af_challenges'] = pd.DataFrame({
        'Challenge': ['Lack of Knowledge', 'Insufficient Funding', 'Market Access',
                      'Land/Property Rights', 'Environmental Constraints',
                      'Policy/Regulatory', 'Cultural Resistance'],
        'Baseline': [_val(raw, r, 2) for r in range(398, 405)],
        'Midline': [_val(raw, r, 3) for r in range(398, 405)],
    })
    data['af_reinvest'] = pd.DataFrame({
        'Category': ['Education & Training', 'Not Applicable', 'Land Purchase', 'Conservation Projects'],
        'Baseline': [_val(raw, r, 2) for r in range(408, 412)],
        'Midline': [_val(raw, r, 3) for r in range(408, 412)],
    })
    data['af_potential'] = pd.DataFrame({
        'Category': ['Moderate', 'Significant', 'Unsure'],
        'Baseline': [_val(raw, 415, 2), _val(raw, 416, 2), _val(raw, 417, 2)],
        'Midline': [_val(raw, 415, 3), _val(raw, 416, 3), _val(raw, 417, 3)],
    })
    return data


# ============================================================================
# WOMEN SURVEY DATA LOADER
# ============================================================================

@st.cache_data
def load_women_data(filepath):
    """
    Parse the Women Survey Excel file.
    Sheet 'Results Women' — 516 rows × 21 columns, non-standard layout.
    Each section is parsed from specific row/col positions.
    """
    try:
        raw = pd.read_excel(filepath, sheet_name=WOMEN_SHEET, header=None)
    except FileNotFoundError:
        st.error(f"Women Survey Excel not found: {filepath}")
        st.stop()

    w = {}

    # ---- A. HOUSEHOLD CHARACTERISTICS ----
    # Location (rows 11-12, cols 1-3)
    w['location'] = pd.DataFrame({
        'Category': ['Marine', 'Terrestrial'],
        'Baseline': [_val(raw, 11, 2), _val(raw, 12, 2)],
        'Midline': [_val(raw, 11, 3), _val(raw, 12, 3)],
    })
    # HH type (rows 11-12, cols 10-12)
    w['hh_type'] = pd.DataFrame({
        'Category': ['Female-Headed', 'Male-Headed'],
        'Baseline': [_val(raw, 11, 11), _val(raw, 12, 11)],
        'Midline': [_val(raw, 11, 12), _val(raw, 12, 12)],
    })
    # Marital status (rows 16-22, cols 1-3)
    w['marital'] = pd.DataFrame({
        'Category': ['Monogamously Married', 'Widowed', 'Polygamously Married',
                     'Separated', 'Single', 'Divorced'],
        'Baseline': [_val(raw, r, 2) for r in range(16, 22)],
        'Midline': [_val(raw, r, 3) for r in range(16, 22)],
    })
    # Education (rows 16-19, cols 10-12)
    w['education'] = pd.DataFrame({
        'Category': ['Primary', 'Pre-primary/None/Other', 'Secondary/Vocational', 'College+'],
        'Baseline': [_val(raw, r, 11) for r in range(16, 20)],
        'Midline': [_val(raw, r, 12) for r in range(16, 20)],
    })
    # Main economic activity (rows 26-39, cols 1-3)
    main_econ_labels = [_clean_label(_val(raw, r, 1)) for r in range(26, 40)
                        if _val(raw, r, 1) != 0]
    main_econ_bl = [_val(raw, r, 2) for r in range(26, 40) if _val(raw, r, 1) != 0]
    main_econ_ml = [_val(raw, r, 3) for r in range(26, 40) if _val(raw, r, 1) != 0]
    w['main_econ'] = pd.DataFrame({
        'Activity': main_econ_labels, 'Baseline': main_econ_bl, 'Midline': main_econ_ml})

    # Secondary economic activity (rows 26-39, cols 10-12)
    sec_econ_labels = [_clean_label(_val(raw, r, 10)) for r in range(26, 40)
                       if _val(raw, r, 10) != 0]
    sec_econ_bl = [_val(raw, r, 11) for r in range(26, 40) if _val(raw, r, 10) != 0]
    sec_econ_ml = [_val(raw, r, 12) for r in range(26, 40) if _val(raw, r, 10) != 0]
    w['sec_econ'] = pd.DataFrame({
        'Activity': sec_econ_labels, 'Baseline': sec_econ_bl, 'Midline': sec_econ_ml})

    # Drinking water (rows 44-45, cols 1-3)
    w['water'] = pd.DataFrame({
        'Category': ['Yes', 'No'],
        'Baseline': [_val(raw, 44, 2), _val(raw, 45, 2)],
        'Midline': [_val(raw, 44, 3), _val(raw, 45, 3)],
    })
    # Toilet (rows 44-45, cols 10-12)
    w['toilet'] = pd.DataFrame({
        'Category': ['Yes', 'No'],
        'Baseline': [_val(raw, 44, 11), _val(raw, 45, 11)],
        'Midline': [_val(raw, 44, 12), _val(raw, 45, 12)],
    })
    # Electricity (rows 49-50, cols 1-3)
    w['electricity'] = pd.DataFrame({
        'Category': ['Yes', 'No'],
        'Baseline': [_val(raw, 49, 2), _val(raw, 50, 2)],
        'Midline': [_val(raw, 49, 3), _val(raw, 50, 3)],
    })
    # Wall materials (rows 54-56, cols 1-3)
    w['walls'] = pd.DataFrame({
        'Category': ['Natural/Mud', 'Finished (Cement/Brick)', 'Uncovered/Iron'],
        'Baseline': [_val(raw, 54, 2), _val(raw, 55, 2), _val(raw, 56, 2)],
        'Midline': [_val(raw, 54, 3), _val(raw, 55, 3), _val(raw, 56, 3)],
    })
    # Floor materials (rows 54-55, cols 10-12)
    w['floors'] = pd.DataFrame({
        'Category': ['Natural (Earth/Sand)', 'Other (Wood/Tiles/Cement)'],
        'Baseline': [_val(raw, 54, 11), _val(raw, 55, 11)],
        'Midline': [_val(raw, 54, 12), _val(raw, 55, 12)],
    })

    # ---- B. SHOCKS AND STRESSES ----
    # Shocks experienced (rows 64-74, cols 1-3) - row 65 has no label (continuation of drought)
    shock_labels = ['Drought', 'Heat/Cold Waves', 'Flooding', 'Climate Variability',
                    'Typhoons/Hurricanes', 'Wildfires', 'Severe Thunderstorms',
                    'Land Degradation', 'Tornadoes', 'Landslides']
    shock_rows = [64, 66, 67, 68, 69, 70, 71, 72, 73, 74]
    w['shocks'] = pd.DataFrame({
        'Shock': shock_labels,
        'Baseline': [_val(raw, r, 2) for r in shock_rows],
        'Midline': [_val(raw, r, 3) for r in shock_rows],
    })
    # Shock impact extent (rows 64-69, cols 10-12)
    w['shock_impact'] = pd.DataFrame({
        'Extent': ['Very Large', 'Large', 'Moderate', 'Small', 'Very Small', 'Not at All'],
        'Baseline': [_val(raw, r, 11) for r in range(64, 70)],
        'Midline': [_val(raw, r, 12) for r in range(64, 70)],
    })
    # Coping strategies (rows 78-90, cols 1-3)
    coping_labels = ['Skipped Meals', 'Took a Loan', 'Sold Small Livestock',
                     'Engaged in Wage Labour', 'Used Savings',
                     'Replaced Food with Less Preferred', 'Additional Livelihood Activities',
                     'Sold Large Livestock', 'Sold Household Assets', 'No Strategies',
                     'Informal Transfers', 'Formal Transfers (Govt/NGO)', 'Reduced Caloric Intake']
    w['coping'] = pd.DataFrame({
        'Strategy': coping_labels,
        'Baseline': [_val(raw, r, 2) for r in range(78, 91)],
        'Midline': [_val(raw, r, 3) for r in range(78, 91)],
    })

    # ---- C. ACCESS TO PREPAREDNESS INFO ----
    # Knowledge of plans (rows 98-101, cols 1-3)
    w['prep_knowledge'] = pd.DataFrame({
        'Response': ['Yes', 'No', "I Don't Know", 'Not Applicable'],
        'Baseline': [_val(raw, r, 2) for r in range(98, 102)],
        'Midline': [_val(raw, r, 3) for r in range(98, 102)],
    })
    # Participation in plan development (rows 98-101, cols 10-12)
    w['prep_participation'] = pd.DataFrame({
        'Response': ['Yes, I did', 'Yes, HH member', 'No', 'Not Applicable'],
        'Baseline': [_val(raw, 98, 11), _val(raw, 99, 11), _val(raw, 100, 11), _val(raw, 101, 11)],
        'Midline': [_val(raw, 98, 12), _val(raw, 99, 12), _val(raw, 100, 12), _val(raw, 101, 12)],
    })
    # Awareness of plan actions (rows 104-110, cols 1-3)
    w['prep_awareness'] = pd.DataFrame({
        'Extent': ['Not at All', 'Large Extent', 'Moderate Extent',
                   'Small Extent', 'Very Large Extent', 'Very Small Extent', 'Not Applicable'],
        'Baseline': [_val(raw, r, 2) for r in range(104, 111)],
        'Midline': [_val(raw, r, 3) for r in range(104, 111)],
    })
    # Know what to do in disaster (rows 105-107, cols 10-12)
    w['prep_know_action'] = pd.DataFrame({
        'Response': ['Yes', 'Partially', 'No'],
        'Baseline': [_val(raw, 105, 11), _val(raw, 106, 11), _val(raw, 107, 11)],
        'Midline': [_val(raw, 105, 12), _val(raw, 106, 12), _val(raw, 107, 12)],
    })
    # Weather forecast access (rows 114-116, cols 1-3)
    w['weather_forecast'] = pd.DataFrame({
        'Response': ['No', 'Yes, I do', 'Yes, HH member'],
        'Baseline': [_val(raw, 114, 2), _val(raw, 115, 2), _val(raw, 116, 2)],
        'Midline': [_val(raw, 114, 3), _val(raw, 115, 3), _val(raw, 116, 3)],
    })
    # Tidal forecast (rows 114-116, cols 10-12)
    w['tidal_forecast'] = pd.DataFrame({
        'Response': ['No', 'Yes, I do', 'Yes, HH member'],
        'Baseline': [_val(raw, 114, 11), _val(raw, 115, 11), _val(raw, 116, 11)],
        'Midline': [_val(raw, 114, 12), _val(raw, 115, 12), _val(raw, 116, 12)],
    })
    # Early warning (rows 120-122, cols 1-3)
    w['early_warning'] = pd.DataFrame({
        'Response': ['No', 'Yes, I do', 'Yes, HH member'],
        'Baseline': [_val(raw, 120, 2), _val(raw, 121, 2), _val(raw, 122, 2)],
        'Midline': [_val(raw, 120, 3), _val(raw, 121, 3), _val(raw, 122, 3)],
    })

    # ---- D. ACCESS & CONTROL OVER RESOURCES ----
    # Assets in HH (rows 129-148, cols 1-3)
    asset_names_raw = [_val(raw, r, 1) for r in range(129, 149)]
    asset_rows_valid = [(r, _clean_label(asset_names_raw[r-129]))
                        for r in range(129, 149) if asset_names_raw[r-129] != 0]
    w['hh_assets'] = pd.DataFrame({
        'Asset': [a[1] for a in asset_rows_valid],
        'Baseline': [_val(raw, a[0], 2) for a in asset_rows_valid],
        'Midline': [_val(raw, a[0], 3) for a in asset_rows_valid],
    })
    # Asset ownership — jointly (rows 130-149, cols 10-12)
    own_names_raw = [_val(raw, r, 10) for r in range(130, 149)]
    own_rows_valid = [(r, _clean_label(own_names_raw[r-130]))
                      for r in range(130, 149) if own_names_raw[r-130] != 0]
    w['asset_ownership'] = pd.DataFrame({
        'Asset': [a[1] for a in own_rows_valid],
        'Joint_BL': [_val(raw, a[0], 11) for a in own_rows_valid],
        'Joint_ML': [_val(raw, a[0], 12) for a in own_rows_valid],
        'Sole_BL': [_val(raw, a[0], 13) for a in own_rows_valid],
        'Sole_ML': [_val(raw, a[0], 14) for a in own_rows_valid],
        'All_BL': [_val(raw, a[0], 15) for a in own_rows_valid],
        'All_ML': [_val(raw, a[0], 16) for a in own_rows_valid],
    })
    # Use/Sell assets (rows 154-173, cols 1-5)
    usesell_names = [_val(raw, r, 1) for r in range(154, 174)]
    usesell_valid = [(r, _clean_label(usesell_names[r-154]))
                     for r in range(154, 174) if usesell_names[r-154] != 0]
    w['asset_use_sell'] = pd.DataFrame({
        'Asset': [a[1] for a in usesell_valid],
        'Use_BL': [_val(raw, a[0], 2) for a in usesell_valid],
        'Use_ML': [_val(raw, a[0], 3) for a in usesell_valid],
        'Sell_BL': [_val(raw, a[0], 4) for a in usesell_valid],
        'Sell_ML': [_val(raw, a[0], 5) for a in usesell_valid],
    })
    # Inputs (rows 154-161, cols 10-14)
    input_names = [_val(raw, r, 10) for r in range(154, 162)]
    input_valid = [(r, _clean_label(input_names[r-154]))
                   for r in range(154, 162) if input_names[r-154] != 0]
    w['inputs'] = pd.DataFrame({
        'Input': [a[1] for a in input_valid],
        'Access_BL': [_val(raw, a[0], 11) for a in input_valid],
        'Access_ML': [_val(raw, a[0], 12) for a in input_valid],
        'PersonalUse_BL': [_val(raw, a[0], 13) for a in input_valid],
        'PersonalUse_ML': [_val(raw, a[0], 14) for a in input_valid],
    })
    # Land size (rows 177-182, cols 1-3)
    w['land_size'] = pd.DataFrame({
        'Category': ['0 ha', '1 ha', '2 ha', '3-5 ha', '6-10 ha', '11+ ha'],
        'Baseline': [_val(raw, r, 2) for r in range(177, 183)],
        'Midline': [_val(raw, r, 3) for r in range(177, 183)],
    })
    # Land status (rows 177-179, cols 10-12)
    w['land_status'] = pd.DataFrame({
        'Category': ['Owned', 'Leased', 'Both'],
        'Baseline': [_val(raw, 177, 11), _val(raw, 178, 11), _val(raw, 179, 11)],
        'Midline': [_val(raw, 177, 12), _val(raw, 178, 12), _val(raw, 179, 12)],
    })
    # Land use (rows 186-187, cols 1-3)
    w['land_use'] = pd.DataFrame({
        'Category': ['Yes', 'No'],
        'Baseline': [_val(raw, 186, 2), _val(raw, 187, 2)],
        'Midline': [_val(raw, 186, 3), _val(raw, 187, 3)],
    })

    # ---- E. SAVINGS AND LOANS ----
    # Family saving (rows 195-197, cols 1-3)
    w['family_saving'] = pd.DataFrame({
        'Response': ['Yes', 'No', "I Don't Know"],
        'Baseline': [_val(raw, 195, 2), _val(raw, 196, 2), _val(raw, 197, 2)],
        'Midline': [_val(raw, 195, 3), _val(raw, 196, 3), _val(raw, 197, 3)],
    })
    # Personal saving (rows 195-196, cols 10-12)
    w['personal_saving'] = pd.DataFrame({
        'Response': ['Yes', 'No'],
        'Baseline': [_val(raw, 195, 11), _val(raw, 196, 11)],
        'Midline': [_val(raw, 195, 12), _val(raw, 196, 12)],
    })
    # Saving frequency (rows 201-205, cols 1-3)
    w['saving_freq'] = pd.DataFrame({
        'Frequency': ['Daily', 'Weekly', 'Monthly', 'Every 3+ Months', 'Varies'],
        'Baseline': [_val(raw, r, 2) for r in range(201, 206)],
        'Midline': [_val(raw, r, 3) for r in range(201, 206)],
    })
    # Saving amount (rows 201-204, cols 10-12)
    w['saving_amount'] = pd.DataFrame({
        'Amount': ['0-100 KES', '101-500 KES', '501-1000 KES', 'Above 1000 KES'],
        'Baseline': [_val(raw, r, 11) for r in range(201, 205)],
        'Midline': [_val(raw, r, 12) for r in range(201, 205)],
    })
    # Saving mechanism (rows 209-214, cols 1-3)
    w['saving_mechanism'] = pd.DataFrame({
        'Mechanism': ['At Home', 'Bank', 'Informal Lender', 'Informal Savings Group', 'MPESA', 'VSLA'],
        'Baseline': [_val(raw, r, 2) for r in range(209, 215)],
        'Midline': [_val(raw, r, 3) for r in range(209, 215)],
    })
    # Saving balance (rows 209-212, cols 10-12)
    w['saving_balance'] = pd.DataFrame({
        'Balance': ['0-100 KES', '101-500 KES', '501-1000 KES', 'Above 1000 KES'],
        'Baseline': [_val(raw, r, 11) for r in range(209, 213)],
        'Midline': [_val(raw, r, 12) for r in range(209, 213)],
    })
    # Intended use (rows 218-224, cols 1-3)
    w['saving_use'] = pd.DataFrame({
        'Use': ['Pay Debts', 'Purchase Food', 'Education Children',
                'Small HH Assets', 'Large HH Assets', 'Agriculture/Fishing', 'Productive Business'],
        'Baseline': [_val(raw, r, 2) for r in range(218, 225)],
        'Midline': [_val(raw, r, 3) for r in range(218, 225)],
    })
    # Family loan (rows 218-220, cols 10-12)
    w['family_loan'] = pd.DataFrame({
        'Response': ['Yes', 'No', "I Don't Know"],
        'Baseline': [_val(raw, 218, 11), _val(raw, 219, 11), _val(raw, 220, 11)],
        'Midline': [_val(raw, 218, 12), _val(raw, 219, 12), _val(raw, 220, 12)],
    })
    # Average loan size (family) — row 222, col 10-12
    w['family_loan_size'] = pd.DataFrame({
        'Metric': ['Average Loan Size (KES)'],
        'Baseline': [_val(raw, 222, 11)],
        'Midline': [_val(raw, 222, 12)],
    })
    # Personal loan (rows 228-229, cols 1-3)
    w['personal_loan'] = pd.DataFrame({
        'Response': ['Yes', 'No'],
        'Baseline': [_val(raw, 228, 2), _val(raw, 229, 2)],
        'Midline': [_val(raw, 228, 3), _val(raw, 229, 3)],
    })
    # Personal loan size — row 231
    w['personal_loan_size'] = pd.DataFrame({
        'Metric': ['Average Loan Size (KES)'],
        'Baseline': [_val(raw, 231, 2)],
        'Midline': [_val(raw, 231, 3)],
    })
    # Loan source (rows 228-232, cols 10-12)
    w['loan_source'] = pd.DataFrame({
        'Source': ['Bank', 'Informal Lender', 'Informal Credit/Savings Group', 'MPESA', 'VSLA'],
        'Baseline': [_val(raw, r, 11) for r in range(228, 233)],
        'Midline': [_val(raw, r, 12) for r in range(228, 233)],
    })

    # ---- F. ROLES, RESPONSIBILITIES & TIME USE ----
    # Who SHOULD do (norms) — rows 238-247, cols 1-3 (joint %)
    role_labels = ['Fetch Firewood', 'Income Provider', 'Clean/Sweep', 'Look After Livestock',
                   'Care for Ill/Elderly', 'Maintain Garden', 'Cook Food',
                   'Care for Children', 'Fetch Water', 'Wash Clothes']
    w['roles_should_joint'] = pd.DataFrame({
        'Role': role_labels,
        'Baseline': [_val(raw, r, 2) for r in range(238, 248)],
        'Midline': [_val(raw, r, 3) for r in range(238, 248)],
    })
    # Who SHOULD do — women only (rows 239-248, cols 10-12)
    w['roles_should_women'] = pd.DataFrame({
        'Role': role_labels,
        'Baseline': [_val(raw, r, 11) for r in range(239, 249)],
        'Midline': [_val(raw, r, 12) for r in range(239, 249)],
    })
    # Who DOES — Joint (rows 252-261, cols 1-3)
    w['roles_does_joint'] = pd.DataFrame({
        'Role': role_labels,
        'Baseline': [_val(raw, r, 2) for r in range(252, 262)],
        'Midline': [_val(raw, r, 3) for r in range(252, 262)],
    })
    # Who DOES — Self/Spouse only (rows 253-262, cols 10-12)
    w['roles_does_self'] = pd.DataFrame({
        'Role': role_labels,
        'Baseline': [_val(raw, r, 11) for r in range(253, 263)],
        'Midline': [_val(raw, r, 12) for r in range(253, 263)],
    })

    # Time use (rows 267-300, cols 0-3 for hours, cols 9-12 for participation %)
    # Unpaid care work
    unpaid_labels = ['Child/Elderly Care', 'Cooking/Dishes', 'Cleaning/Washing', 'Fetching Water', 'Fetching Firewood']
    w['time_unpaid'] = pd.DataFrame({
        'Activity': unpaid_labels,
        'Hours_BL': [_val(raw, r, 2) for r in range(267, 272)],
        'Hours_ML': [_val(raw, r, 3) for r in range(267, 272)],
        'Pct_BL': [_val(raw, r, 11) for r in range(267, 272)],
        'Pct_ML': [_val(raw, r, 12) for r in range(267, 272)],
    })
    # Total unpaid care
    w['time_unpaid_total'] = pd.DataFrame({
        'Category': ['Unpaid Care Work'],
        'Baseline': [_val(raw, 273, 2)], 'Midline': [_val(raw, 273, 3)]})

    # Productive work
    prod_labels = ['Farm Work (Others)', 'Farm Work (Own)', 'Fishing', 'Seaweed Farming',
                   'Tending Livestock', 'Selling at Market', 'Formal Employment']
    w['time_productive'] = pd.DataFrame({
        'Activity': prod_labels,
        'Hours_BL': [_val(raw, r, 2) for r in range(275, 282)],
        'Hours_ML': [_val(raw, r, 3) for r in range(275, 282)],
    })
    w['time_productive_total'] = pd.DataFrame({
        'Category': ['Productive Work'],
        'Baseline': [_val(raw, 283, 2)], 'Midline': [_val(raw, 283, 3)]})

    # Community conservation
    conservation_labels = ['Mangrove Restoration', 'Seaweed Farming', 'Forest Mgmt & Conservation']
    w['time_conservation'] = pd.DataFrame({
        'Activity': conservation_labels,
        'Hours_BL': [_val(raw, r, 2) for r in range(285, 288)],
        'Hours_ML': [_val(raw, r, 3) for r in range(285, 288)],
    })
    w['time_conservation_total'] = pd.DataFrame({
        'Category': ['Community Conservation'],
        'Baseline': [_val(raw, 289, 2)], 'Midline': [_val(raw, 289, 3)]})

    # Time summary
    w['time_summary'] = pd.DataFrame({
        'Category': ['Unpaid Care Work', 'Productive Work', 'Community Conservation',
                     'Personal Development', 'Personal Care', 'Leisure', 'Other'],
        'Baseline': [_val(raw, 273, 2), _val(raw, 283, 2), _val(raw, 289, 2),
                     _val(raw, 291, 2), _val(raw, 296, 2), _val(raw, 298, 2), _val(raw, 300, 2)],
        'Midline': [_val(raw, 273, 3), _val(raw, 283, 3), _val(raw, 289, 3),
                    _val(raw, 291, 3), _val(raw, 296, 3), _val(raw, 298, 3), _val(raw, 300, 3)],
    })

    # ---- G. DECISION MAKING ----
    decision_labels = ['Routine HH Purchases', 'Women Work on Farm', 'Use of HH Income',
                       'Women Go to Market', 'Mangrove/Seaweed/Forest Work',
                       'Using HH Savings', 'Invest Borrowed/Saved Money',
                       'Children Education', 'Large HH Purchases',
                       'Small Business', 'Taking Out Loans']
    # Should be Joint (rows 308-318, cols 1-3)
    w['decision_should_joint'] = pd.DataFrame({
        'Decision': decision_labels,
        'Baseline': [_val(raw, r, 2) for r in range(308, 319)],
        'Midline': [_val(raw, r, 3) for r in range(308, 319)],
    })
    # Should be — Men/Women only (rows 309-319, cols 10-12)
    w['decision_should_women'] = pd.DataFrame({
        'Decision': decision_labels,
        'Baseline': [_val(raw, r, 11) for r in range(309, 320)],
        'Midline': [_val(raw, r, 12) for r in range(309, 320)],
    })
    # Does — Joint (rows 323-333, cols 1-3)
    w['decision_does_joint'] = pd.DataFrame({
        'Decision': decision_labels,
        'Baseline': [_val(raw, r, 2) for r in range(323, 334)],
        'Midline': [_val(raw, r, 3) for r in range(323, 334)],
    })
    # Does — Self/Spouse (rows 324-334, cols 10-12)
    w['decision_does_self'] = pd.DataFrame({
        'Decision': decision_labels,
        'Baseline': [_val(raw, r, 11) for r in range(324, 335)],
        'Midline': [_val(raw, r, 12) for r in range(324, 335)],
    })
    # Can influence to a large extent (rows 338-348, cols 1-3)
    w['decision_influence'] = pd.DataFrame({
        'Decision': decision_labels,
        'Baseline': [_val(raw, r, 2) for r in range(338, 349)],
        'Midline': [_val(raw, r, 3) for r in range(338, 349)],
    })

    # ---- H. CLIMATE CHANGE & NBS ----
    # Heard of CC (rows 356-357, cols 1-3)
    w['cc_heard'] = pd.DataFrame({
        'Response': ['Yes', 'No'],
        'Baseline': [_val(raw, 356, 2), _val(raw, 357, 2)],
        'Midline': [_val(raw, 356, 3), _val(raw, 357, 3)],
    })
    # Adequately define CC (rows 361-364, cols 1-3)
    w['cc_define'] = pd.DataFrame({
        'Response': ['Completely Acceptable', 'Somewhat Acceptable', 'Not Acceptable', "Doesn't Know"],
        'Baseline': [_val(raw, r, 2) for r in range(361, 365)],
        'Midline': [_val(raw, r, 3) for r in range(361, 365)],
    })
    # CC effects on environment (rows 368-379, cols 1-3)
    env_effect_labels = ['Hotter Temperatures', 'Extreme Weather Events', 'Increased Drought',
                         'Warming Oceans', 'Sea Level Rise', 'Loss of Species',
                         'Migration of Species', 'Animal Migration Changes',
                         'Spread of Disease', 'Ocean Acidification',
                         'Increased Invasive Species', "I Don't Know"]
    w['cc_env_effects'] = pd.DataFrame({
        'Effect': env_effect_labels,
        'Baseline': [_val(raw, r, 2) for r in range(368, 380)],
        'Midline': [_val(raw, r, 3) for r in range(368, 380)],
    })
    # CC effects on livelihoods (rows 356-367, cols 10-12)
    livelihood_labels = ['Increased Food Insecurity', 'Increased Water Insecurity',
                         'Personal Risk from Extremes', 'Forced Migration',
                         'Changes in Livelihood', 'Reduced Livelihood Activities',
                         'Extreme Weather on Infrastructure', 'Reduced Ag Productivity',
                         'Crop Loss', 'Loss of Livestock', 'Reduced Livestock Productivity',
                         'Loss of Savings/Assets', "I Don't Know"]
    w['cc_livelihood_effects'] = pd.DataFrame({
        'Effect': livelihood_labels,
        'Baseline': [_val(raw, r, 11) for r in range(356, 369)],
        'Midline': [_val(raw, r, 12) for r in range(356, 369)],
    })
    # Heard of NbS (rows 383-384, cols 1-3)
    w['nbs_heard'] = pd.DataFrame({
        'Response': ['Yes', 'No'],
        'Baseline': [_val(raw, 383, 2), _val(raw, 384, 2)],
        'Midline': [_val(raw, 383, 3), _val(raw, 384, 3)],
    })
    # Define NbS (rows 372-375, cols 10-12)
    w['nbs_define'] = pd.DataFrame({
        'Response': ['Completely Acceptable', 'Somewhat Acceptable', 'Not Acceptable', "Doesn't Know"],
        'Baseline': [_val(raw, r, 11) for r in range(372, 376)],
        'Midline': [_val(raw, r, 12) for r in range(372, 376)],
    })
    # NbS examples (rows 388-396, cols 1-3)
    nbs_example_labels = ['Mangrove Restoration', 'Coral Reef Restoration', 'Reforestation',
                          'Sustainable Seaweed Farming', "I Don't Know",
                          'Rainwater Harvesting', 'Sustainable Agriculture', 'Solar Energy',
                          'Rainwater Harvesting 2']
    w['nbs_examples'] = pd.DataFrame({
        'Example': nbs_example_labels,
        'Baseline': [_val(raw, r, 2) for r in range(388, 397)],
        'Midline': [_val(raw, r, 3) for r in range(388, 397)],
    })
    # NbS benefits (rows 379-390, cols 10-12)
    nbs_benefit_labels = ['Carbon Capture', 'Reduce Storm Surges', 'Defense Against Salination',
                          'Improve Air Quality', 'Water Conservation', 'Soil Health',
                          'Support Pollinators', 'Local Biodiversity', 'Fish Diversity',
                          'Seawater Quality', 'Improved Livelihoods', "I Don't Know"]
    w['nbs_benefits'] = pd.DataFrame({
        'Benefit': nbs_benefit_labels,
        'Baseline': [_val(raw, r, 11) for r in range(379, 391)],
        'Midline': [_val(raw, r, 12) for r in range(379, 391)],
    })

    # ---- H1. MANGROVE RESTORATION ----
    w['mangrove_heard'] = pd.DataFrame({
        'Response': ['Heard & Importance', 'Heard Only', 'Not Heard'],
        'Baseline': [_val(raw, 403, 2), _val(raw, 404, 2), _val(raw, 405, 2)],
        'Midline': [_val(raw, 403, 3), _val(raw, 404, 3), _val(raw, 405, 3)],
    })
    w['mangrove_ever'] = pd.DataFrame({
        'Response': ['Yes', 'No'],
        'Baseline': [_val(raw, 403, 11), _val(raw, 404, 11)],
        'Midline': [_val(raw, 403, 12), _val(raw, 404, 12)],
    })
    w['mangrove_current'] = pd.DataFrame({
        'Response': ['Yes', 'No'],
        'Baseline': [_val(raw, 410, 2), _val(raw, 411, 2)],
        'Midline': [_val(raw, 410, 3), _val(raw, 411, 3)],
    })
    w['mangrove_modality'] = pd.DataFrame({
        'Modality': ['Individually', 'As a Group', 'As a Family'],
        'Baseline': [_val(raw, 408, 11), _val(raw, 409, 11), _val(raw, 410, 11)],
        'Midline': [_val(raw, 408, 12), _val(raw, 409, 12), _val(raw, 410, 12)],
    })
    w['mangrove_training'] = pd.DataFrame({
        'Response': ['Yes', 'Partially', 'No'],
        'Baseline': [_val(raw, 415, 2), _val(raw, 416, 2), _val(raw, 417, 2)],
        'Midline': [_val(raw, 415, 3), _val(raw, 416, 3), _val(raw, 417, 3)],
    })
    w['mangrove_assets'] = pd.DataFrame({
        'Response': ['Yes', 'Partially', 'No'],
        'Baseline': [_val(raw, 414, 11), _val(raw, 415, 11), _val(raw, 416, 11)],
        'Midline': [_val(raw, 414, 12), _val(raw, 415, 12), _val(raw, 416, 12)],
    })
    w['mangrove_interest'] = pd.DataFrame({
        'Response': ['Yes, Definitely', 'Yes, Maybe', 'No, Not Really'],
        'Baseline': [_val(raw, 421, 2), _val(raw, 422, 2), _val(raw, 423, 2)],
        'Midline': [_val(raw, 421, 3), _val(raw, 422, 3), _val(raw, 423, 3)],
    })

    # ---- H2. SEAWEED FARMING ----
    w['seaweed_heard'] = pd.DataFrame({
        'Response': ['Heard & Importance', 'Heard Only', 'Not Heard'],
        'Baseline': [_val(raw, 430, 2), _val(raw, 431, 2), _val(raw, 432, 2)],
        'Midline': [_val(raw, 430, 3), _val(raw, 431, 3), _val(raw, 432, 3)],
    })
    w['seaweed_ever'] = pd.DataFrame({
        'Response': ['Yes', "Don't Know", 'No'],
        'Baseline': [_val(raw, 430, 11), _val(raw, 431, 11), _val(raw, 432, 11)],
        'Midline': [_val(raw, 430, 12), _val(raw, 431, 12), _val(raw, 432, 12)],
    })
    w['seaweed_current'] = pd.DataFrame({
        'Response': ['Yes', 'No'],
        'Baseline': [_val(raw, 436, 2), _val(raw, 437, 2)],
        'Midline': [_val(raw, 436, 3), _val(raw, 437, 3)],
    })
    w['seaweed_modality'] = pd.DataFrame({
        'Modality': ['Individually', 'As a Group', 'As a Family'],
        'Baseline': [_val(raw, 436, 11), _val(raw, 437, 11), _val(raw, 438, 11)],
        'Midline': [_val(raw, 436, 12), _val(raw, 437, 12), _val(raw, 438, 12)],
    })
    w['seaweed_training'] = pd.DataFrame({
        'Response': ['Yes', 'Partially', 'No'],
        'Baseline': [_val(raw, 441, 2), _val(raw, 442, 2), _val(raw, 443, 2)],
        'Midline': [_val(raw, 441, 3), _val(raw, 442, 3), _val(raw, 443, 3)],
    })
    w['seaweed_assets'] = pd.DataFrame({
        'Response': ['Yes', 'No', 'Partially'],
        'Baseline': [_val(raw, 442, 11), _val(raw, 443, 11), _val(raw, 444, 11)],
        'Midline': [_val(raw, 442, 12), _val(raw, 443, 12), _val(raw, 444, 12)],
    })
    w['seaweed_interest'] = pd.DataFrame({
        'Response': ['Yes, Definitely', 'Yes, Maybe', 'No, Not Really'],
        'Baseline': [_val(raw, 447, 2), _val(raw, 448, 2), _val(raw, 449, 2)],
        'Midline': [_val(raw, 447, 3), _val(raw, 448, 3), _val(raw, 449, 3)],
    })

    # ---- H3. FOREST MANAGEMENT ----
    w['forest_heard'] = pd.DataFrame({
        'Response': ['Heard & Importance', 'Not Heard'],
        'Baseline': [_val(raw, 456, 2), _val(raw, 457, 2)],
        'Midline': [_val(raw, 456, 3), _val(raw, 457, 3)],
    })
    w['forest_ever'] = pd.DataFrame({
        'Response': ['Yes', 'No'],
        'Baseline': [_val(raw, 456, 11), _val(raw, 457, 11)],
        'Midline': [_val(raw, 456, 12), _val(raw, 457, 12)],
    })
    w['forest_current'] = pd.DataFrame({
        'Response': ['Yes', 'No'],
        'Baseline': [_val(raw, 462, 2), _val(raw, 463, 2)],
        'Midline': [_val(raw, 462, 3), _val(raw, 463, 3)],
    })
    w['forest_modality'] = pd.DataFrame({
        'Modality': ['Individually', 'As a Group', 'As a Family'],
        'Baseline': [_val(raw, 462, 11), _val(raw, 463, 11), _val(raw, 464, 11)],
        'Midline': [_val(raw, 462, 12), _val(raw, 463, 12), _val(raw, 464, 12)],
    })
    w['forest_training'] = pd.DataFrame({
        'Response': ['Yes', 'Partially', 'No'],
        'Baseline': [_val(raw, 467, 2), _val(raw, 468, 2), _val(raw, 469, 2)],
        'Midline': [_val(raw, 467, 3), _val(raw, 468, 3), _val(raw, 469, 3)],
    })
    w['forest_assets'] = pd.DataFrame({
        'Response': ['Yes', 'Partially', 'No'],
        'Baseline': [_val(raw, 468, 11), _val(raw, 469, 11), _val(raw, 470, 11)],
        'Midline': [_val(raw, 468, 12), _val(raw, 469, 12), _val(raw, 470, 12)],
    })

    # ---- I. LIFE SKILLS ----
    # Agree or Strongly Agree (rows 476-499, cols 1-3)
    # Strongly Agree (rows 476-499, cols 10-12)
    ls_labels = [
        'I have many positive qualities',
        'Respected in community',
        'Life has meaning',
        'Think about future',
        'Specific goals',
        'Know what to do for goals',
        'Confident to achieve goals',
        'Ability to lead',
        'Bring people together',
        'People seek my advice',
        'Prioritize tasks',
        'Convince others to join cause',
    ]
    ls_domains = ['Self Esteem']*3 + ['Aspirations']*4 + ['Leadership']*5
    ls_rows = list(range(476, 488))
    w['lifeskills_agree'] = pd.DataFrame({
        'Domain': ls_domains, 'Statement': ls_labels,
        'Baseline': [_val(raw, r, 2) for r in ls_rows],
        'Midline': [_val(raw, r, 3) for r in ls_rows],
    })
    w['lifeskills_strong'] = pd.DataFrame({
        'Domain': ls_domains, 'Statement': ls_labels,
        'Baseline': [_val(raw, r, 11) for r in ls_rows],
        'Midline': [_val(raw, r, 12) for r in ls_rows],
    })
    # Communication & Conflict Resolution
    comm_labels = ['Express Opinion (Family)', 'Express Opinion (Community)',
                   'Express What I Think', 'Listen Carefully', 'Easy to Understand Ideas']
    cr_labels = ['Seek Advice/Opinions', 'Understand Other POV',
                 'Not Offended by Disagreement', 'Think Long-Term Before Deciding']
    comm_rows = list(range(491, 496))
    cr_rows = list(range(496, 500))
    w['communication_agree'] = pd.DataFrame({
        'Statement': comm_labels,
        'Baseline': [_val(raw, r, 2) for r in comm_rows],
        'Midline': [_val(raw, r, 3) for r in comm_rows],
    })
    w['communication_strong'] = pd.DataFrame({
        'Statement': comm_labels,
        'Baseline': [_val(raw, r, 11) for r in comm_rows],
        'Midline': [_val(raw, r, 12) for r in comm_rows],
    })
    w['conflict_agree'] = pd.DataFrame({
        'Statement': cr_labels,
        'Baseline': [_val(raw, r, 2) for r in cr_rows],
        'Midline': [_val(raw, r, 3) for r in cr_rows],
    })
    w['conflict_strong'] = pd.DataFrame({
        'Statement': cr_labels,
        'Baseline': [_val(raw, r, 11) for r in cr_rows],
        'Midline': [_val(raw, r, 12) for r in cr_rows],
    })

    # ---- J. SOCIAL NORMS ----
    sn_labels = ['Income → Husband Controls', 'Men Better Business Ideas',
                 "Men Earn, Women Look After Home", 'Inappropriate Dress → Her Fault',
                 'Cook & Clean → Good Marriage', 'Embarrassing for Men to Do Chores',
                 'Planting Crops (Family Food)', 'Restoring Ecosystems (Mangrove/Forest)',
                 'Only Men Drive Boats', 'Ok for Women to Express Emotions']
    sn_rows = list(range(506, 516))
    w['socialnorms_agree'] = pd.DataFrame({
        'Norm': sn_labels,
        'Baseline': [_val(raw, r, 2) for r in sn_rows],
        'Midline': [_val(raw, r, 3) for r in sn_rows],
    })
    w['socialnorms_strong'] = pd.DataFrame({
        'Norm': sn_labels,
        'Baseline': [_val(raw, r, 11) for r in sn_rows],
        'Midline': [_val(raw, r, 12) for r in sn_rows],
    })

    return w


# ============================================================================
# CHART HELPERS
# ============================================================================

def make_comparison_bar(df, cat_col, title, y_label="Percentage (%)",
                        multiply=True, height=450, orientation='v',
                        color_baseline=None, color_midline=None):
    cb = color_baseline or COLORS["baseline"]
    cm = color_midline or COLORS["midline"]
    plot_df = df.copy()
    if multiply:
        plot_df['Baseline'] = plot_df['Baseline'].apply(lambda x: x*100 if isinstance(x,(int,float)) else 0)
        plot_df['Midline'] = plot_df['Midline'].apply(lambda x: x*100 if isinstance(x,(int,float)) else 0)
    if orientation == 'h':
        fig = go.Figure()
        fig.add_trace(go.Bar(y=plot_df[cat_col], x=plot_df['Baseline'], name='Baseline',
                             orientation='h', marker_color=cb,
                             text=plot_df['Baseline'].apply(lambda x: f"{x:.1f}%"), textposition='auto'))
        fig.add_trace(go.Bar(y=plot_df[cat_col], x=plot_df['Midline'], name='Midline',
                             orientation='h', marker_color=cm,
                             text=plot_df['Midline'].apply(lambda x: f"{x:.1f}%"), textposition='auto'))
        fig.update_layout(title=title, barmode='group', height=height,
                          xaxis_title=y_label, legend=dict(orientation='h', yanchor='bottom', y=1.02))
    else:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=plot_df[cat_col], y=plot_df['Baseline'], name='Baseline',
                             marker_color=cb, text=plot_df['Baseline'].apply(lambda x: f"{x:.1f}%"),
                             textposition='auto'))
        fig.add_trace(go.Bar(x=plot_df[cat_col], y=plot_df['Midline'], name='Midline',
                             marker_color=cm, text=plot_df['Midline'].apply(lambda x: f"{x:.1f}%"),
                             textposition='auto'))
        fig.update_layout(title=title, barmode='group', height=height, yaxis_title=y_label,
                          legend=dict(orientation='h', yanchor='bottom', y=1.02))
    fig.update_layout(
        font=dict(size=13, color='#333'),
        title_font=dict(size=16, color='#222'),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return fig


def make_stacked_bar(df, cat_col, columns, colors_list, title,
                     y_label="Percentage (%)", height=400, multiply=True, orientation='v'):
    plot_df = df.copy()
    if multiply:
        for c in columns:
            plot_df[c] = plot_df[c].apply(lambda x: x*100 if isinstance(x,(int,float)) else 0)
    fig = go.Figure()
    for col, color in zip(columns, colors_list):
        label = col.replace('Baseline_','').replace('Midline_','')
        if orientation == 'h':
            fig.add_trace(go.Bar(y=plot_df[cat_col], x=plot_df[col], name=label, orientation='h',
                                 marker_color=color,
                                 text=plot_df[col].apply(lambda x: f"{x:.1f}%" if x > 3 else ""),
                                 textposition='inside'))
        else:
            fig.add_trace(go.Bar(x=plot_df[cat_col], y=plot_df[col], name=label, marker_color=color,
                                 text=plot_df[col].apply(lambda x: f"{x:.1f}%" if x > 3 else ""),
                                 textposition='inside'))
    fig.update_layout(title=title, barmode='stack', height=height,
                      yaxis_title=y_label if orientation=='v' else '',
                      xaxis_title=y_label if orientation=='h' else '',
                      legend=dict(orientation='h', yanchor='bottom', y=1.02),
                      font=dict(size=13, color='#333'),
                      title_font=dict(size=16, color='#222'),
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                      margin=dict(l=20, r=20, t=60, b=20))
    return fig


def make_delta_bar(df, cat_col, title, multiply=True, height=400):
    plot_df = df.copy()
    factor = 100 if multiply else 1
    plot_df['Change'] = (plot_df['Midline'] - plot_df['Baseline']) * factor
    plot_df = plot_df.sort_values('Change')
    colors = [COLORS['good'] if v >= 0 else COLORS['danger'] for v in plot_df['Change']]
    fig = go.Figure()
    fig.add_trace(go.Bar(y=plot_df[cat_col], x=plot_df['Change'], orientation='h',
                         marker_color=colors,
                         text=plot_df['Change'].apply(lambda x: f"{x:+.1f}pp"), textposition='auto'))
    fig.update_layout(title=title, height=height, xaxis_title="Change (pp)",
                      font=dict(size=13, color='#333'),
                      title_font=dict(size=16, color='#222'),
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                      margin=dict(l=20, r=20, t=60, b=20))
    return fig


def make_two_col_bar(df1, df2, col1_name, col2_name, cat_col, title, height=450):
    """Side-by-side comparison of two related dataframes (e.g., norms vs experience)."""
    fig = go.Figure()
    fig.add_trace(go.Bar(y=df1[cat_col], x=df1['Baseline']*100, name=f'{col1_name} (BL)',
                         orientation='h', marker_color=COLORS['baseline_light'],
                         text=df1['Baseline'].apply(lambda x: f"{x*100:.0f}%"), textposition='auto'))
    fig.add_trace(go.Bar(y=df1[cat_col], x=df1['Midline']*100, name=f'{col1_name} (ML)',
                         orientation='h', marker_color=COLORS['baseline'],
                         text=df1['Midline'].apply(lambda x: f"{x*100:.0f}%"), textposition='auto'))
    fig.add_trace(go.Bar(y=df2[cat_col], x=df2['Baseline']*100, name=f'{col2_name} (BL)',
                         orientation='h', marker_color=COLORS['midline_light'],
                         text=df2['Baseline'].apply(lambda x: f"{x*100:.0f}%"), textposition='auto'))
    fig.add_trace(go.Bar(y=df2[cat_col], x=df2['Midline']*100, name=f'{col2_name} (ML)',
                         orientation='h', marker_color=COLORS['midline'],
                         text=df2['Midline'].apply(lambda x: f"{x*100:.0f}%"), textposition='auto'))
    fig.update_layout(title=title, barmode='group', height=height, xaxis_title='%',
                      legend=dict(orientation='h', yanchor='bottom', y=1.02),
                      font=dict(size=13, color='#333'),
                      title_font=dict(size=16, color='#222'),
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                      margin=dict(l=20, r=20, t=60, b=20))
    return fig


# ============================================================================
# WOMEN SURVEY TAB RENDERERS
# ============================================================================

def _section_header(icon, title, badge_text=None):
    """Render a styled section header with optional badge."""
    badge = f'<span class="badge">{badge_text}</span>' if badge_text else ''
    heading = f'{icon} {title}' if icon else title
    st.markdown(f'<div class="section-header"><h2>{heading}</h2>{badge}</div>',
                unsafe_allow_html=True)


def _quick_nav_pills(items):
    """Render quick navigation pills for in-tab section jumping."""
    pills = ''.join([f'<span class="quick-nav-pill">{item}</span>' for item in items])
    st.markdown(f'<div class="quick-nav">{pills}</div>', unsafe_allow_html=True)


def render_women_tab1(w):
    """Tab 1: Household Profile & Services."""
    st.markdown("""<div class="section-narrative">
    <strong>Household Profile:</strong> Demographics of surveyed women — location type, household
    headship, marital status, education levels, economic activities, and access to basic services
    (water, sanitation, electricity, housing materials).
    </div>""", unsafe_allow_html=True)

    _quick_nav_pills(['Demographics', 'Economic Activities', 'Basic Services'])

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(make_comparison_bar(w['location'], 'Category',
                        'Women by Location Type', height=300), width='stretch')
    with c2:
        st.plotly_chart(make_comparison_bar(w['hh_type'], 'Category',
                        'Household Type', height=300), width='stretch')

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(make_comparison_bar(w['marital'], 'Category',
                        'Marital Status', height=380, orientation='h'), width='stretch')
    with c4:
        st.plotly_chart(make_comparison_bar(w['education'], 'Category',
                        'Education Level', height=380, orientation='h'), width='stretch')

    st.markdown("---")
    _section_header('', 'Economic Activities', 'Section A')
    c5, c6 = st.columns(2)
    with c5:
        st.plotly_chart(make_comparison_bar(w['main_econ'], 'Activity',
                        'Main HH Economic Activity', height=500, orientation='h'), width='stretch')
    with c6:
        st.plotly_chart(make_comparison_bar(w['sec_econ'], 'Activity',
                        'Secondary HH Economic Activities', height=500, orientation='h'), width='stretch')

    st.markdown("---")
    _section_header('', 'Access to Basic Services', 'Section A')
    c7, c8, c9 = st.columns(3)
    with c7:
        st.plotly_chart(make_comparison_bar(w['water'], 'Category',
                        'Access to Safe Drinking Water', height=300), width='stretch')
    with c8:
        st.plotly_chart(make_comparison_bar(w['toilet'], 'Category',
                        'Access to Improved Toilet', height=300), width='stretch')
    with c9:
        st.plotly_chart(make_comparison_bar(w['electricity'], 'Category',
                        'Access to Electricity', height=300), width='stretch')

    c10, c11 = st.columns(2)
    with c10:
        st.plotly_chart(make_comparison_bar(w['walls'], 'Category',
                        'Wall Material', height=350), width='stretch')
    with c11:
        st.plotly_chart(make_comparison_bar(w['floors'], 'Category',
                        'Floor Material', height=350), width='stretch')


def render_women_tab2(w):
    """Tab 2: Shocks, Coping & Preparedness."""
    st.markdown("""<div class="section-narrative">
    <strong>Shocks & Preparedness:</strong> Shocks and stresses experienced by women's households,
    their perceived impact, coping strategies employed, and access to disaster preparedness information
    including weather/tidal forecasts and early warning systems.
    </div>""", unsafe_allow_html=True)

    _quick_nav_pills(['Shocks & Impact', 'Coping Strategies', 'Disaster Preparedness'])

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(make_comparison_bar(w['shocks'], 'Shock',
                        'Shocks Experienced (Past 12 Months)', height=450, orientation='h'),
                        width='stretch')
    with c2:
        st.plotly_chart(make_comparison_bar(w['shock_impact'], 'Extent',
                        'Perceived Impact on Wellbeing', height=400, orientation='h'),
                        width='stretch')

    _section_header('', 'Coping Strategies', 'Section B')
    st.plotly_chart(make_comparison_bar(w['coping'], 'Strategy',
                    'Coping Strategies Used', height=500, orientation='h'), width='stretch')

    st.markdown("---")
    _section_header('', 'Disaster Preparedness', 'Section C')
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(make_comparison_bar(w['prep_knowledge'], 'Response',
                        'Knowledge of Preparedness Plans', height=350), width='stretch')
    with c4:
        st.plotly_chart(make_comparison_bar(w['prep_participation'], 'Response',
                        'Participation in Plan Development', height=350), width='stretch')

    c5, c6 = st.columns(2)
    with c5:
        st.plotly_chart(make_comparison_bar(w['prep_know_action'], 'Response',
                        'Know What to Do in Disaster', height=300), width='stretch')
    with c6:
        st.plotly_chart(make_comparison_bar(w['early_warning'], 'Response',
                        'Access to Early Warning Info', height=300), width='stretch')

    c7, c8 = st.columns(2)
    with c7:
        st.plotly_chart(make_comparison_bar(w['weather_forecast'], 'Response',
                        'Access to Weather Forecasts', height=300), width='stretch')
    with c8:
        st.plotly_chart(make_comparison_bar(w['tidal_forecast'], 'Response',
                        'Access to Tidal Forecasts', height=300), width='stretch')


def render_women_tab3(w):
    """Tab 3: Assets, Land, Savings & Loans."""
    st.markdown("""<div class="section-narrative">
    <strong>Assets & Financial Inclusion:</strong> Household assets, ownership patterns (joint/sole/all),
    ability to use or sell assets, access to productive inputs, land size and tenure, savings behaviour,
    and borrowing patterns.
    </div>""", unsafe_allow_html=True)

    _quick_nav_pills(['Household Assets', 'Land', 'Savings', 'Loans'])

    _section_header('', 'Household Assets', 'Section D')
    st.plotly_chart(make_comparison_bar(w['hh_assets'], 'Asset',
                    'Assets Present in Household', height=600, orientation='h'), width='stretch')

    st.markdown("---")
    _section_header('', 'Land', 'Section D')
    c1, c2, c3 = st.columns(3)
    with c1:
        st.plotly_chart(make_comparison_bar(w['land_size'], 'Category',
                        'Agricultural Land Size', height=350), width='stretch')
    with c2:
        st.plotly_chart(make_comparison_bar(w['land_status'], 'Category',
                        'Land Tenure Status', height=350), width='stretch')
    with c3:
        st.plotly_chart(make_comparison_bar(w['land_use'], 'Category',
                        'Currently Using Land for Agriculture', height=300), width='stretch')

    st.markdown("---")
    _section_header('', 'Savings', 'Section E')
    c4, c5 = st.columns(2)
    with c4:
        st.plotly_chart(make_comparison_bar(w['personal_saving'], 'Response',
                        'Women Personally Saving', height=300), width='stretch')
    with c5:
        st.plotly_chart(make_comparison_bar(w['family_saving'], 'Response',
                        'Family Members Saving', height=300), width='stretch')

    c6, c7 = st.columns(2)
    with c6:
        st.plotly_chart(make_comparison_bar(w['saving_freq'], 'Frequency',
                        'Saving Frequency', height=350, orientation='h'), width='stretch')
    with c7:
        st.plotly_chart(make_comparison_bar(w['saving_amount'], 'Amount',
                        'Amount Saved per Period', height=350, orientation='h'), width='stretch')

    c8, c9 = st.columns(2)
    with c8:
        st.plotly_chart(make_comparison_bar(w['saving_mechanism'], 'Mechanism',
                        'Saving Mechanism', height=380, orientation='h'), width='stretch')
    with c9:
        st.plotly_chart(make_comparison_bar(w['saving_use'], 'Use',
                        'Intended Use of Savings', height=380, orientation='h'), width='stretch')

    st.markdown("---")
    _section_header('', 'Loans', 'Section E')
    c10, c11 = st.columns(2)
    with c10:
        st.plotly_chart(make_comparison_bar(w['personal_loan'], 'Response',
                        'Women Personally Taking a Loan', height=300), width='stretch')
        pl = w['personal_loan_size']
        st.metric("Avg Personal Loan (BL → ML)",
                  f"KES {pl['Baseline'].values[0]:,.0f} → {pl['Midline'].values[0]:,.0f}")
    with c11:
        st.plotly_chart(make_comparison_bar(w['loan_source'], 'Source',
                        'Loan Sources', height=380, orientation='h'), width='stretch')


def render_women_tab4(w):
    """Tab 4: Roles, Time Use & Decision-Making."""
    st.markdown("""<div class="section-narrative">
    <strong>Roles & Decisions:</strong> Gender norms around household roles (who SHOULD do tasks vs.
    who DOES them), women's time use across categories (unpaid care, productive work, community
    conservation, personal development), and decision-making power including influence on key
    household decisions.
    </div>""", unsafe_allow_html=True)

    _quick_nav_pills(['Roles & Norms', 'Time Use', 'Decision-Making'])

    _section_header('', 'Roles & Responsibilities: Norms vs. Experience', 'Section F')
    st.plotly_chart(make_two_col_bar(w['roles_should_joint'], w['roles_does_joint'],
                    'Should be Joint', 'Actually Joint', 'Role',
                    'Roles: Should be Joint vs. Actually Joint', height=500), width='stretch')

    st.markdown("---")
    _section_header('', 'Time Use (Average Hours per Day)', 'Section G')
    ts = w['time_summary']
    fig_time = go.Figure()
    fig_time.add_trace(go.Bar(x=ts['Category'], y=ts['Baseline'], name='Baseline',
                              marker_color=COLORS['baseline'],
                              text=ts['Baseline'].apply(lambda x: f"{x:.1f}h"), textposition='auto'))
    fig_time.add_trace(go.Bar(x=ts['Category'], y=ts['Midline'], name='Midline',
                              marker_color=COLORS['midline'],
                              text=ts['Midline'].apply(lambda x: f"{x:.1f}h"), textposition='auto'))
    fig_time.update_layout(title="Average Hours per Day by Activity Category",
                           barmode='group', height=450, yaxis_title='Hours',
                           legend=dict(orientation='h', yanchor='bottom', y=1.02),
                           font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'),
                           plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_time, width='stretch')

    c1, c2 = st.columns(2)
    with c1:
        tu = w['time_unpaid']
        fig_uc = go.Figure()
        fig_uc.add_trace(go.Bar(y=tu['Activity'], x=tu['Hours_BL'], name='Baseline',
                                orientation='h', marker_color=COLORS['baseline']))
        fig_uc.add_trace(go.Bar(y=tu['Activity'], x=tu['Hours_ML'], name='Midline',
                                orientation='h', marker_color=COLORS['midline']))
        fig_uc.update_layout(title='Unpaid Care Work (Hours/Day)', barmode='group', height=350,
                             xaxis_title='Hours', legend=dict(orientation='h', yanchor='bottom', y=1.02),
                             font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'),
                             plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_uc, width='stretch')
    with c2:
        tp = w['time_productive']
        fig_pw = go.Figure()
        fig_pw.add_trace(go.Bar(y=tp['Activity'], x=tp['Hours_BL'], name='Baseline',
                                orientation='h', marker_color=COLORS['baseline']))
        fig_pw.add_trace(go.Bar(y=tp['Activity'], x=tp['Hours_ML'], name='Midline',
                                orientation='h', marker_color=COLORS['midline']))
        fig_pw.update_layout(title='Productive Work (Hours/Day)', barmode='group', height=350,
                             xaxis_title='Hours', legend=dict(orientation='h', yanchor='bottom', y=1.02),
                             font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'),
                             plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pw, width='stretch')

    st.markdown("---")
    _section_header('', 'Decision-Making', 'Section H')
    st.plotly_chart(make_two_col_bar(w['decision_should_joint'], w['decision_does_joint'],
                    'Should be Joint', 'Actually Joint', 'Decision',
                    'Decision-Making: Norms vs. Experience (Joint %)', height=550), width='stretch')

    _section_header('', "Influence on HH Decisions ('To a Large Extent')", 'Section H')
    st.plotly_chart(make_comparison_bar(w['decision_influence'], 'Decision',
                    'Women Who Can Influence Decisions to a Large Extent',
                    height=500, orientation='h'), width='stretch')


def render_women_tab5(w):
    """Tab 5: Climate Change & NbS."""
    st.markdown("""<div class="section-narrative">
    <strong>Climate & Nature-based Solutions:</strong> Women's awareness of climate change, ability to
    define it, perceived effects on livelihoods and environment, knowledge of Nature-based Solutions
    (NbS), and participation in mangrove restoration, seaweed farming, and forest management.
    </div>""", unsafe_allow_html=True)

    _quick_nav_pills(['Climate Awareness', 'NbS Knowledge', 'Mangrove', 'Seaweed', 'Forest'])

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(make_comparison_bar(w['cc_heard'], 'Response',
                        'Heard of Climate Change', height=300), width='stretch')
    with c2:
        st.plotly_chart(make_comparison_bar(w['cc_define'], 'Response',
                        'Ability to Define Climate Change', height=350), width='stretch')

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(make_comparison_bar(w['cc_env_effects'], 'Effect',
                        'Perceived Environmental Effects of CC', height=500, orientation='h'),
                        width='stretch')
    with c4:
        st.plotly_chart(make_comparison_bar(w['cc_livelihood_effects'], 'Effect',
                        'Perceived Livelihood Effects of CC', height=500, orientation='h'),
                        width='stretch')

    st.markdown("---")
    _section_header('', 'Nature-based Solutions', 'Section H')
    c5, c6 = st.columns(2)
    with c5:
        st.plotly_chart(make_comparison_bar(w['nbs_heard'], 'Response',
                        'Heard of NbS', height=300), width='stretch')
    with c6:
        st.plotly_chart(make_comparison_bar(w['nbs_define'], 'Response',
                        'Ability to Define NbS', height=350), width='stretch')

    c7, c8 = st.columns(2)
    with c7:
        st.plotly_chart(make_comparison_bar(w['nbs_examples'], 'Example',
                        'NbS Examples Women Can Cite', height=450, orientation='h'), width='stretch')
    with c8:
        st.plotly_chart(make_comparison_bar(w['nbs_benefits'], 'Benefit',
                        'Perceived Benefits of NbS', height=500, orientation='h'), width='stretch')

    st.markdown("---")
    # NbS Modules
    for module, prefix, icon in [('Mangrove Restoration', 'mangrove', ''),
                                  ('Seaweed Farming', 'seaweed', ''),
                                  ('Forest Management', 'forest', '')]:
        _section_header(icon, module, 'NbS Module')
        ca, cb = st.columns(2)
        with ca:
            st.plotly_chart(make_comparison_bar(w[f'{prefix}_heard'], 'Response',
                            f'Awareness of {module}', height=300), width='stretch')
            st.plotly_chart(make_comparison_bar(w[f'{prefix}_current'], 'Response',
                            f'Currently Involved', height=280), width='stretch')
        with cb:
            st.plotly_chart(make_comparison_bar(w[f'{prefix}_ever'], 'Response',
                            f'Ever Participated', height=300), width='stretch')
            st.plotly_chart(make_comparison_bar(w[f'{prefix}_modality'], 'Modality',
                            f'Participation Modality', height=300), width='stretch')

        cc, cd = st.columns(2)
        with cc:
            st.plotly_chart(make_comparison_bar(w[f'{prefix}_training'], 'Response',
                            f'Training Received', height=300), width='stretch')
        with cd:
            st.plotly_chart(make_comparison_bar(w[f'{prefix}_assets'], 'Response',
                            f'Assets/Inputs Received', height=300), width='stretch')

        if f'{prefix}_interest' in w:
            st.plotly_chart(make_comparison_bar(w[f'{prefix}_interest'], 'Response',
                            f'Interest in Participating', height=280), width='stretch')
        st.markdown("---")


def render_women_tab6(w):
    """Tab 6: Life Skills & Social Norms."""
    st.markdown("""<div class="section-narrative">
    <strong>Life Skills & Social Norms:</strong> Women's self-assessed life skills (self-esteem,
    aspirations, leadership, communication, conflict resolution) and prevailing social norms around
    gender roles, economic control, domestic work, ecosystem participation, and emotional expression.
    </div>""", unsafe_allow_html=True)

    _quick_nav_pills(['Life Skills Radar', 'Communication', 'Social Norms'])

    # Life skills radar
    _section_header('', 'Life Skills — Agree/Strongly Agree', 'Section I')
    ls_a = w['lifeskills_agree'].copy()
    ls_s = w['lifeskills_strong'].copy()

    # Aggregate by domain
    ls_domain = ls_a.groupby('Domain')[['Baseline','Midline']].mean().reset_index()
    ls_domain_s = ls_s.groupby('Domain')[['Baseline','Midline']].mean().reset_index()

    fig_radar = go.Figure()
    domains = list(ls_domain['Domain']) + [ls_domain['Domain'].iloc[0]]
    bl_vals = list(ls_domain['Baseline']*100) + [ls_domain['Baseline'].iloc[0]*100]
    ml_vals = list(ls_domain['Midline']*100) + [ls_domain['Midline'].iloc[0]*100]
    fig_radar.add_trace(go.Scatterpolar(r=bl_vals, theta=domains, fill='toself',
                                         name='Baseline', fillcolor=COLORS['radar_bl_fill'],
                                         line=dict(color=COLORS['baseline'])))
    fig_radar.add_trace(go.Scatterpolar(r=ml_vals, theta=domains, fill='toself',
                                         name='Midline', fillcolor=COLORS['radar_ml_fill'],
                                         line=dict(color=COLORS['midline'])))
    fig_radar.update_layout(title='Life Skills by Domain (Agree/SA %)',
                            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                            height=450, legend=dict(orientation='h', yanchor='bottom', y=-0.15),
                            font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'))
    st.plotly_chart(fig_radar, width='stretch')

    # Detailed bars
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(make_comparison_bar(ls_a, 'Statement',
                        'Life Skills — Agree/SA %', height=550, orientation='h'), width='stretch')
    with c2:
        st.plotly_chart(make_comparison_bar(ls_s, 'Statement',
                        'Life Skills — Strongly Agree %', height=550, orientation='h'), width='stretch')

    st.markdown("---")
    _section_header('', 'Communication & Conflict Resolution', 'Section I')
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(make_comparison_bar(w['communication_agree'], 'Statement',
                        'Communication — Agree/SA', height=350, orientation='h'), width='stretch')
    with c4:
        st.plotly_chart(make_comparison_bar(w['conflict_agree'], 'Statement',
                        'Conflict Resolution — Agree/SA', height=350, orientation='h'), width='stretch')

    st.markdown("---")
    _section_header('', 'Social Norms', 'Section J')
    c5, c6 = st.columns(2)
    with c5:
        st.plotly_chart(make_comparison_bar(w['socialnorms_agree'], 'Norm',
                        'Social Norms — Agree/SA %', height=500, orientation='h'), width='stretch')
    with c6:
        st.plotly_chart(make_comparison_bar(w['socialnorms_strong'], 'Norm',
                        'Social Norms — Strongly Agree %', height=500, orientation='h'), width='stretch')


# ============================================================================
# FORESTRY TAB RENDERERS (extracted from forestry_dashboard.py main())
# ============================================================================

def render_forestry_tabs(data, show_change):
    """Render all 6 forestry tabs exactly as the original forestry_dashboard.py."""
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        " Overview", " Group Characteristics", " Governance & Gender",
        " Training & Assets", " Forest Condition & Threats", " Income & Agroforestry"
    ])

    # ---- TAB 1: OVERVIEW ----
    with tab1:
        st.markdown("""<div class="section-narrative">
        <strong>Overview:</strong> Key performance indicators for Community Forestry Conservation Groups,
        comparing baseline and midline. Functionality thresholds and domain scores (Management, Gender, Effectiveness).
        </div>""", unsafe_allow_html=True)

        ft = data['functionality_threshold']
        fs = data['functionality_scores']
        fd = data['functionality_domain']
        bl_60 = ft.loc[ft['Timepoint']=='Baseline','Functional_60_pct'].values[0]
        ml_60 = ft.loc[ft['Timepoint']=='Midline','Functional_60_pct'].values[0]
        bl_70 = ft.loc[ft['Timepoint']=='Baseline','Functional_70_pct'].values[0]
        ml_70 = ft.loc[ft['Timepoint']=='Midline','Functional_70_pct'].values[0]
        bl_avg = fs.loc[fs['Timepoint']=='Baseline','Average'].values[0]
        ml_avg = fs.loc[fs['Timepoint']=='Midline','Average'].values[0]
        bl_grp = data['num_groups'].loc[data['num_groups']['Timepoint']=='Baseline','Groups_Assessed'].values[0]
        ml_grp = data['num_groups'].loc[data['num_groups']['Timepoint']=='Midline','Groups_Assessed'].values[0]

        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("Functional ≥60%", f"{ml_60*100:.1f}%", delta=f"{(ml_60-bl_60)*100:+.1f}pp")
        with c2: st.metric("Functional ≥70%", f"{ml_70*100:.1f}%", delta=f"{(ml_70-bl_70)*100:+.1f}pp")
        with c3: st.metric("Overall Score", f"{ml_avg:.1f}/100", delta=f"{ml_avg-bl_avg:+.1f} pts")
        with c4: st.metric("Groups Assessed", f"{int(ml_grp)}", delta=f"{int(ml_grp-bl_grp)}")
        st.markdown("---")

        col_l, col_r = st.columns([3,2])
        with col_l:
            domain_df = pd.DataFrame({
                'Domain': ['Management','Gender','Effectiveness','Overall'],
                'Baseline': fd[['Management','Gender','Effectiveness','Overall']].iloc[0].values,
                'Midline': fd[['Management','Gender','Effectiveness','Overall']].iloc[1].values,
            })
            fig = go.Figure()
            fig.add_trace(go.Bar(x=domain_df['Domain'], y=domain_df['Baseline'], name='Baseline',
                                 marker_color=COLORS['baseline'],
                                 text=domain_df['Baseline'].apply(lambda x: f"{x:.1f}"), textposition='auto'))
            fig.add_trace(go.Bar(x=domain_df['Domain'], y=domain_df['Midline'], name='Midline',
                                 marker_color=COLORS['midline'],
                                 text=domain_df['Midline'].apply(lambda x: f"{x:.1f}"), textposition='auto'))
            fig.update_layout(title="Functionality Scores by Domain (0-100)", barmode='group', height=450,
                              yaxis=dict(title='Score', range=[0,105]),
                              legend=dict(orientation='h', yanchor='bottom', y=1.02),
                              font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'),
                              plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, width='stretch')
        with col_r:
            fig_r = go.Figure()
            fig_r.add_trace(go.Scatterpolar(
                r=list(domain_df['Baseline'])+[domain_df['Baseline'].iloc[0]],
                theta=list(domain_df['Domain'])+[domain_df['Domain'].iloc[0]],
                fill='toself', name='Baseline',
                fillcolor=COLORS['radar_bl_fill'], line=dict(color=COLORS['baseline'])))
            fig_r.add_trace(go.Scatterpolar(
                r=list(domain_df['Midline'])+[domain_df['Midline'].iloc[0]],
                theta=list(domain_df['Domain'])+[domain_df['Domain'].iloc[0]],
                fill='toself', name='Midline',
                fillcolor=COLORS['radar_ml_fill'], line=dict(color=COLORS['midline'])))
            fig_r.update_layout(title="Domain Performance Radar",
                                polar=dict(radialaxis=dict(visible=True, range=[0,100])),
                                height=450, legend=dict(orientation='h', yanchor='bottom', y=-0.15),
                                font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'))
            st.plotly_chart(fig_r, width='stretch')

        st.subheader("Score Statistics")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            s = fs[fs['Timepoint']=='Baseline'].iloc[0]
            st.markdown(f"**Baseline** — N={int(s['Respondents'])} | Avg={s['Average']:.1f} | Max={s['Max']:.1f} | Min={s['Min']:.1f}")
        with col_s2:
            s = fs[fs['Timepoint']=='Midline'].iloc[0]
            st.markdown(f"**Midline** — N={int(s['Respondents'])} | Avg={s['Average']:.1f} | Max={s['Max']:.1f} | Min={s['Min']:.1f}")

    # ---- TAB 2: GROUP CHARACTERISTICS ----
    with tab2:
        st.markdown("""<div class="section-narrative">
        <strong>Group Characteristics:</strong> Membership composition, years of operation, land tenure, and forest size.
        </div>""", unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        with c1:
            st.plotly_chart(make_comparison_bar(data['avg_membership'],'Category','Avg Members',
                            y_label='Members', multiply=False, height=350), width='stretch')
        with c2:
            st.plotly_chart(make_comparison_bar(data['max_membership'],'Category','Max Members',
                            y_label='Members', multiply=False, height=350), width='stretch')
        with c3:
            st.plotly_chart(make_comparison_bar(data['min_membership'],'Category','Min Members',
                            y_label='Members', multiply=False, height=350), width='stretch')
        st.markdown("---")
        c4,c5,c6 = st.columns(3)
        with c4:
            fn = make_delta_bar if show_change else make_comparison_bar
            kw = {'title':'Change in Years Dist'} if show_change else {'title':'Years of Operation', 'height':400}
            st.plotly_chart(fn(data['years_dist'],'Category',**kw), width='stretch')
        with c5:
            fn = make_delta_bar if show_change else make_comparison_bar
            kw = {'title':'Change in Tenure'} if show_change else {'title':'Land Tenure Type', 'height':400}
            st.plotly_chart(fn(data['tenure'],'Category',**kw), width='stretch')
        with c6:
            fn = make_delta_bar if show_change else make_comparison_bar
            kw = {'title':'Change in Forest Size'} if show_change else {'title':'Forest Size (ha)', 'height':400}
            st.plotly_chart(fn(data['forest_size_dist'],'Category',**kw), width='stretch')

    # ---- TAB 3: GOVERNANCE & GENDER ----
    with tab3:
        st.markdown("""<div class="section-narrative">
        <strong>Governance & Gender:</strong> Board clarity, guidelines, meetings, women's leadership,
        management practices, gender equality discussions and actions.
        </div>""", unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1: st.plotly_chart(make_comparison_bar(data['goals_defined'],'Category','Defined Goals', height=350), width='stretch')
        with c2: st.plotly_chart(make_comparison_bar(data['goals_stated'],'Goal','Stated Goals', height=350, orientation='h'), width='stretch')
        c3,c4 = st.columns(2)
        with c3: st.plotly_chart(make_comparison_bar(data['rights'],'Right','Right Entitlements', height=400, orientation='h'), width='stretch')
        with c4: st.plotly_chart(make_comparison_bar(data['responsibilities'],'Responsibility','Govt Responsibilities', height=400, orientation='h'), width='stretch')
        st.markdown("---")
        c5,c6 = st.columns(2)
        with c5: st.plotly_chart(make_comparison_bar(data['board_roles'],'Category','Board Role Clarity', height=380, orientation='h'), width='stretch')
        with c6: st.plotly_chart(make_comparison_bar(data['guidelines'],'Category','Guidelines Status', height=380, orientation='h'), width='stretch')
        c7,c8 = st.columns(2)
        with c7: st.plotly_chart(make_comparison_bar(data['meetings'],'Category','Meeting Frequency', height=350, orientation='h'), width='stretch')
        with c8: st.plotly_chart(make_comparison_bar(data['women_leadership'],'Category',"Women's Leadership", height=350, orientation='h'), width='stretch')

        # Management practices
        mp = data['mgmt_practices']
        fig_mp = go.Figure()
        fig_mp.add_trace(go.Bar(y=mp['Practice'], x=mp['Agree_Baseline']*100, name='Agree+SA (BL)', orientation='h', marker_color=COLORS['baseline']))
        fig_mp.add_trace(go.Bar(y=mp['Practice'], x=mp['Agree_Midline']*100, name='Agree+SA (ML)', orientation='h', marker_color=COLORS['midline']))
        fig_mp.add_trace(go.Bar(y=mp['Practice'], x=mp['StronglyAgree_Baseline']*100, name='SA (BL)', orientation='h', marker_color=COLORS['baseline_light']))
        fig_mp.add_trace(go.Bar(y=mp['Practice'], x=mp['StronglyAgree_Midline']*100, name='SA (ML)', orientation='h', marker_color=COLORS['midline_light']))
        fig_mp.update_layout(barmode='group', height=500, xaxis_title="%",
                             legend=dict(orientation='h', yanchor='bottom', y=1.02),
                             font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'),
                             plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_mp, width='stretch')
        st.markdown("---")
        c9,c10 = st.columns(2)
        with c9:
            st.plotly_chart(make_comparison_bar(data['ge_discussion'],'Category','GE Discussion', height=350), width='stretch')
            st.plotly_chart(make_comparison_bar(data['ge_actions'],'Category','GE Actions Agreed', height=350), width='stretch')
        with c10:
            st.plotly_chart(make_comparison_bar(data['ge_topics'],'Topic','GE Topics', height=350, orientation='h'), width='stretch')
            st.plotly_chart(make_comparison_bar(data['ge_completion'],'Category','GE Action Completion', height=350), width='stretch')

    # ---- TAB 4: TRAINING & ASSETS ----
    with tab4:
        st.markdown("""<div class="section-narrative">
        <strong>Training & Assets:</strong> Training coverage, topics, and assets/inputs received.
        </div>""", unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1: st.plotly_chart(make_comparison_bar(data['training_coverage'],'Category','Training Coverage', height=400), width='stretch')
        with c2:
            tc = data['training_coverage'].copy(); tc['Baseline']*=100; tc['Midline']*=100
            fig_tc = go.Figure()
            for i,(_,row) in enumerate(tc.iterrows()):
                fig_tc.add_trace(go.Bar(x=['Baseline','Midline'], y=[row['Baseline'],row['Midline']],
                                        name=row['Category'], marker_color=['#E53935','#FB8C00','#FDD835','#43A047'][i],
                                        text=[f"{row['Baseline']:.1f}%",f"{row['Midline']:.1f}%"], textposition='inside'))
            fig_tc.update_layout(title="Coverage (Stacked)", barmode='stack', height=400, yaxis_title="%",
                                 legend=dict(orientation='h', yanchor='bottom', y=1.02),
                                 font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'),
                                 plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_tc, width='stretch')

        if show_change:
            st.plotly_chart(make_delta_bar(data['training_topics'],'Topic','Training Topics Change (pp)', height=500), width='stretch')
        else:
            st.plotly_chart(make_comparison_bar(data['training_topics'],'Topic','Training Topics', height=600, orientation='h'), width='stretch')
        st.markdown("---")
        c3,c4 = st.columns(2)
        with c3: st.plotly_chart(make_comparison_bar(data['assets_received'],'Category','Assets Received', height=350), width='stretch')
        with c4: st.plotly_chart(make_comparison_bar(data['asset_types'],'Asset','Asset Types', height=400, orientation='h'), width='stretch')

    # ---- TAB 5: FOREST CONDITION & THREATS ----
    with tab5:
        st.markdown("""<div class="section-narrative">
        <strong>Forest Condition & Threats:</strong> Perceived condition, changes, threat levels, harvesting patterns.
        </div>""", unsafe_allow_html=True)
        tp = st.radio("Timepoint", ["Baseline","Midline"], horizontal=True, key="fc_tp")
        fc = data['forest_condition']
        cols = [f'{tp}_Good',f'{tp}_Medium',f'{tp}_Poor']
        fig = make_stacked_bar(fc,'Characteristic', cols, [COLORS['good'],COLORS['medium'],COLORS['poor']],
                               f'Forest Condition — {tp}', height=400)
        for i,l in enumerate(['Good','Medium','Poor']): fig.data[i].name = l
        st.plotly_chart(fig, width='stretch')
        st.markdown("---")
        tp2 = st.radio("Timepoint", ["Baseline","Midline"], horizontal=True, key="fch_tp")
        fch = data['forest_change']
        cols2 = [f'{tp2}_Decrease',f'{tp2}_NoChange',f'{tp2}_Increase']
        fig2 = make_stacked_bar(fch,'Characteristic', cols2, [COLORS['danger'],COLORS['no_change'],COLORS['good']],
                                f'Perceived Changes — {tp2}', height=400)
        for i,l in enumerate(['Decrease','No Change','Increase']): fig2.data[i].name = l
        st.plotly_chart(fig2, width='stretch')
        st.markdown("---")
        c1,c2 = st.columns(2)
        with c1:
            fig_t = make_stacked_bar(data['threats'],'Threat', ['Baseline_Low','Baseline_Medium','Baseline_High'],
                                     [COLORS['good'],COLORS['medium'],COLORS['danger']], 'Threats — Baseline', height=450, orientation='h')
            for i,l in enumerate(['Low','Medium','High']): fig_t.data[i].name = l
            st.plotly_chart(fig_t, width='stretch')
        with c2:
            fig_t2 = make_stacked_bar(data['threats'],'Threat', ['Midline_Low','Midline_Medium','Midline_High'],
                                      [COLORS['good'],COLORS['medium'],COLORS['danger']], 'Threats — Midline', height=450, orientation='h')
            for i,l in enumerate(['Low','Medium','High']): fig_t2.data[i].name = l
            st.plotly_chart(fig_t2, width='stretch')

    # ---- TAB 6: INCOME & AGROFORESTRY ----
    with tab6:
        st.markdown("""<div class="section-narrative">
        <strong>Income & Agroforestry:</strong> Income generation, sources, uses, agroforestry practices, support, and challenges.
        </div>""", unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        with c1: st.plotly_chart(make_comparison_bar(data['income_gen'],'Category','Income Generation', height=350), width='stretch')
        with c2: st.plotly_chart(make_comparison_bar(data['income_sources'],'Source','Income Sources', height=400, orientation='h'), width='stretch')
        with c3: st.plotly_chart(make_comparison_bar(data['income_use'],'Use','Income Use', height=400, orientation='h'), width='stretch')
        st.markdown("---")
        c4,c5 = st.columns(2)
        with c4: st.plotly_chart(make_comparison_bar(data['agroforestry'],'Category','Agroforestry Practice', height=350), width='stretch')
        with c5: st.plotly_chart(make_comparison_bar(data['af_types'],'Practice','AF Types', height=350, orientation='h'), width='stretch')
        c6,c7 = st.columns(2)
        with c6: st.plotly_chart(make_comparison_bar(data['af_objectives'],'Objective','AF Objectives', height=400, orientation='h'), width='stretch')
        with c7: st.plotly_chart(make_comparison_bar(data['af_training'],'Category','AF Training', height=350), width='stretch')
        st.markdown("---")
        c8,c9 = st.columns(2)
        with c8:
            fn = make_delta_bar if show_change else make_comparison_bar
            kw = {'title':'Change in AF Support (pp)'} if show_change else {'title':'AF Support Types', 'height':380, 'orientation':'h'}
            st.plotly_chart(fn(data['af_support'],'Support',**kw), width='stretch')
        with c9:
            fn = make_delta_bar if show_change else make_comparison_bar
            kw = {'title':'Change in AF Challenges (pp)'} if show_change else {'title':'AF Challenges', 'height':380, 'orientation':'h'}
            st.plotly_chart(fn(data['af_challenges'],'Challenge',**kw), width='stretch')
        c10,c11 = st.columns(2)
        with c10: st.plotly_chart(make_comparison_bar(data['af_reinvest'],'Category','AF Reinvestment', height=380, orientation='h'), width='stretch')
        with c11: st.plotly_chart(make_comparison_bar(data['af_potential'],'Category','Livelihood Potential', height=350), width='stretch')


# ============================================================================
# MAIN
# ============================================================================

# ============================================================================
# CROSS-DATASET SYNTHESIS VIEW
# ============================================================================

def render_synthesis_view(f_data, w_data):
    """Combined overview of both datasets — key headline indicators."""
    st.markdown("""<div class="section-narrative">
    <strong> Cross-Dataset Synthesis:</strong> A combined overview comparing headline indicators
    from both the Forestry Conservation Groups (community-level) and Women's Survey (household-level)
    datasets. This view highlights key programme-wide trends.
    </div>""", unsafe_allow_html=True)

    # ---- Forestry Headline KPIs ----
    st.markdown('<h3 style="margin-top:0.5rem;"> Forestry Conservation Groups — Headlines</h3>',
                unsafe_allow_html=True)
    ft = f_data['functionality_threshold']
    fs = f_data['functionality_scores']
    bl_60 = ft.loc[ft['Timepoint']=='Baseline','Functional_60_pct'].values[0]
    ml_60 = ft.loc[ft['Timepoint']=='Midline','Functional_60_pct'].values[0]
    bl_avg = fs.loc[fs['Timepoint']=='Baseline','Average'].values[0]
    ml_avg = fs.loc[fs['Timepoint']=='Midline','Average'].values[0]
    bl_grp = f_data['num_groups'].loc[f_data['num_groups']['Timepoint']=='Baseline','Groups_Assessed'].values[0]
    ml_grp = f_data['num_groups'].loc[f_data['num_groups']['Timepoint']=='Midline','Groups_Assessed'].values[0]

    fc1, fc2, fc3, fc4 = st.columns(4)
    fc1.markdown(f"""<div class="kpi-card">
        <h3>Groups Assessed</h3>
        <div class="value">{int(ml_grp)}</div>
        <div class="delta-{'positive' if ml_grp>=bl_grp else 'negative'}">{int(ml_grp-bl_grp):+d} from BL</div>
    </div>""", unsafe_allow_html=True)
    fc2.markdown(f"""<div class="kpi-card">
        <h3>Functional ≥60%</h3>
        <div class="value">{ml_60*100:.1f}%</div>
        <div class="delta-{'positive' if ml_60>=bl_60 else 'negative'}">{(ml_60-bl_60)*100:+.1f}pp</div>
    </div>""", unsafe_allow_html=True)
    fc3.markdown(f"""<div class="kpi-card">
        <h3>Overall Score</h3>
        <div class="value">{ml_avg:.1f}/100</div>
        <div class="delta-{'positive' if ml_avg>=bl_avg else 'negative'}">{ml_avg-bl_avg:+.1f} pts</div>
    </div>""", unsafe_allow_html=True)
    # Agroforestry uptake
    af_bl = f_data['agroforestry'].loc[f_data['agroforestry']['Category']=='Yes','Baseline'].values[0]
    af_ml = f_data['agroforestry'].loc[f_data['agroforestry']['Category']=='Yes','Midline'].values[0]
    fc4.markdown(f"""<div class="kpi-card">
        <h3>Agroforestry Yes</h3>
        <div class="value">{af_ml*100:.0f}%</div>
        <div class="delta-{'positive' if af_ml>=af_bl else 'negative'}">{(af_ml-af_bl)*100:+.1f}pp</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- Women Survey Headline KPIs ----
    st.markdown('<h3> Women\'s Survey — Headlines</h3>', unsafe_allow_html=True)

    # CC heard
    cc_bl = w_data['cc_heard'].loc[w_data['cc_heard']['Response']=='Yes','Baseline'].values[0] if len(w_data['cc_heard'][w_data['cc_heard']['Response']=='Yes']) else 0
    cc_ml = w_data['cc_heard'].loc[w_data['cc_heard']['Response']=='Yes','Midline'].values[0] if len(w_data['cc_heard'][w_data['cc_heard']['Response']=='Yes']) else 0
    # NbS heard
    nbs_bl = w_data['nbs_heard'].loc[w_data['nbs_heard']['Response']=='Yes','Baseline'].values[0] if len(w_data['nbs_heard'][w_data['nbs_heard']['Response']=='Yes']) else 0
    nbs_ml = w_data['nbs_heard'].loc[w_data['nbs_heard']['Response']=='Yes','Midline'].values[0] if len(w_data['nbs_heard'][w_data['nbs_heard']['Response']=='Yes']) else 0
    # Personal saving
    sav_bl = w_data['personal_saving'].loc[w_data['personal_saving']['Response']=='Yes','Baseline'].values[0] if len(w_data['personal_saving'][w_data['personal_saving']['Response']=='Yes']) else 0
    sav_ml = w_data['personal_saving'].loc[w_data['personal_saving']['Response']=='Yes','Midline'].values[0] if len(w_data['personal_saving'][w_data['personal_saving']['Response']=='Yes']) else 0
    # Life skills average
    ls_bl = w_data['lifeskills_agree']['Baseline'].mean()
    ls_ml = w_data['lifeskills_agree']['Midline'].mean()

    wc1, wc2, wc3, wc4 = st.columns(4)
    wc1.markdown(f"""<div class="kpi-card">
        <h3>CC Awareness</h3>
        <div class="value">{cc_ml*100:.0f}%</div>
        <div class="delta-{'positive' if cc_ml>=cc_bl else 'negative'}">{(cc_ml-cc_bl)*100:+.1f}pp</div>
    </div>""", unsafe_allow_html=True)
    wc2.markdown(f"""<div class="kpi-card">
        <h3>NbS Awareness</h3>
        <div class="value">{nbs_ml*100:.0f}%</div>
        <div class="delta-{'positive' if nbs_ml>=nbs_bl else 'negative'}">{(nbs_ml-nbs_bl)*100:+.1f}pp</div>
    </div>""", unsafe_allow_html=True)
    wc3.markdown(f"""<div class="kpi-card">
        <h3>Women Saving</h3>
        <div class="value">{sav_ml*100:.0f}%</div>
        <div class="delta-{'positive' if sav_ml>=sav_bl else 'negative'}">{(sav_ml-sav_bl)*100:+.1f}pp</div>
    </div>""", unsafe_allow_html=True)
    wc4.markdown(f"""<div class="kpi-card">
        <h3>Life Skills (Avg)</h3>
        <div class="value">{ls_ml*100:.0f}%</div>
        <div class="delta-{'positive' if ls_ml>=ls_bl else 'negative'}">{(ls_ml-ls_bl)*100:+.1f}pp</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Side-by-side mini charts
    st.markdown('<h3>Comparative Snapshots</h3>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        # Forestry domains radar
        fd = f_data['functionality_domain']
        domain_df = pd.DataFrame({
            'Domain': ['Management','Gender','Effectiveness','Overall'],
            'Baseline': fd[['Management','Gender','Effectiveness','Overall']].iloc[0].values,
            'Midline': fd[['Management','Gender','Effectiveness','Overall']].iloc[1].values,
        })
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(
            r=list(domain_df['Baseline'])+[domain_df['Baseline'].iloc[0]],
            theta=list(domain_df['Domain'])+[domain_df['Domain'].iloc[0]],
            fill='toself', name='Baseline',
            fillcolor=COLORS['radar_bl_fill'], line=dict(color=COLORS['baseline'])))
        fig_r.add_trace(go.Scatterpolar(
            r=list(domain_df['Midline'])+[domain_df['Midline'].iloc[0]],
            theta=list(domain_df['Domain'])+[domain_df['Domain'].iloc[0]],
            fill='toself', name='Midline',
            fillcolor=COLORS['radar_ml_fill'], line=dict(color=COLORS['midline'])))
        fig_r.update_layout(title="Forestry Domain Performance",
                            polar=dict(radialaxis=dict(visible=True, range=[0,100])),
                            height=380, legend=dict(orientation='h', yanchor='bottom', y=-0.15),
                            font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'))
        st.plotly_chart(fig_r, width='stretch')
    with c2:
        # Women's life-skills radar
        ls_a = w_data['lifeskills_agree']
        ls_domain = ls_a.groupby('Domain')[['Baseline','Midline']].mean().reset_index()
        domains_l = list(ls_domain['Domain']) + [ls_domain['Domain'].iloc[0]]
        bl_v = list(ls_domain['Baseline']*100) + [ls_domain['Baseline'].iloc[0]*100]
        ml_v = list(ls_domain['Midline']*100) + [ls_domain['Midline'].iloc[0]*100]
        fig_ls = go.Figure()
        fig_ls.add_trace(go.Scatterpolar(
            r=bl_v, theta=domains_l, fill='toself', name='Baseline',
            fillcolor=COLORS['radar_bl_fill'], line=dict(color=COLORS['baseline'])))
        fig_ls.add_trace(go.Scatterpolar(
            r=ml_v, theta=domains_l, fill='toself', name='Midline',
            fillcolor=COLORS['radar_ml_fill'], line=dict(color=COLORS['midline'])))
        fig_ls.update_layout(title="Women's Life Skills Domains",
                             polar=dict(radialaxis=dict(visible=True, range=[0,100])),
                             height=380, legend=dict(orientation='h', yanchor='bottom', y=-0.15),
                             font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'))
        st.plotly_chart(fig_ls, width='stretch')

    # Social norms mini-bar
    c3, c4 = st.columns(2)
    with c3:
        sn = w_data['socialnorms_agree'].copy()
        sn['Change'] = (sn['Midline'] - sn['Baseline'])*100
        sn_sorted = sn.sort_values('Change')
        colors_sn = [COLORS['good'] if v <= 0 else COLORS['danger'] for v in sn_sorted['Change']]
        fig_sn = go.Figure()
        fig_sn.add_trace(go.Bar(y=sn_sorted['Norm'], x=sn_sorted['Change'], orientation='h',
                                marker_color=colors_sn,
                                text=sn_sorted['Change'].apply(lambda x: f"{x:+.1f}pp"), textposition='auto'))
        fig_sn.update_layout(title="Social Norms Change (↓ = positive)", height=400,
                             xaxis_title="Change (pp)",
                             font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'),
                             plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_sn, width='stretch')
    with c4:
        ts = w_data['time_summary'].copy()
        fig_ts = go.Figure()
        fig_ts.add_trace(go.Bar(x=ts['Category'], y=ts['Baseline'], name='Baseline',
                                marker_color=COLORS['baseline'],
                                text=ts['Baseline'].apply(lambda x: f"{x:.1f}h"), textposition='auto'))
        fig_ts.add_trace(go.Bar(x=ts['Category'], y=ts['Midline'], name='Midline',
                                marker_color=COLORS['midline'],
                                text=ts['Midline'].apply(lambda x: f"{x:.1f}h"), textposition='auto'))
        fig_ts.update_layout(title="Women's Time Use (hrs/day)", barmode='group', height=400,
                             yaxis_title='Hours',
                             legend=dict(orientation='h', yanchor='bottom', y=1.02),
                             font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'),
                             plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_ts, width='stretch')

    st.markdown("""<div class="section-narrative" style="margin-top:1rem;">
    <strong>Navigate deeper:</strong> Use the sidebar to select either <em>Forestry Groups</em>
    or <em>Women Survey</em> for detailed breakdowns across all thematic areas.
    </div>""", unsafe_allow_html=True)


# ============================================================================
# MAIN
# ============================================================================

def main():
    st.set_page_config(
        page_title="COSME M&E Dashboard",
        page_icon="bar_chart",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # ---- THEME ----
    theme_name = st.sidebar.selectbox("Dashboard Theme", list(THEMES.keys()), index=0,
                                       help="Color palette for all charts and UI elements")
    global COLORS
    COLORS = THEMES[theme_name]

    # ---- ENHANCED CSS ----
    st.markdown(f"""
    <style>
    /* ---------- GLOBAL TYPOGRAPHY ---------- */
    html, body, [class*="css"] {{
        font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    .block-container {{
        max-width: 1200px;
        padding: 1rem 2rem 2rem;
    }}

    /* ---------- HEADER ---------- */
    .main-header {{
        background: {COLORS['header_gradient']};
        color: white; padding: 2rem 2.5rem; border-radius: 14px;
        margin-bottom: 2rem; text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.18);
        position: relative; overflow: hidden;
    }}
    .main-header::before {{
        content: ''; position: absolute; top: -50%; left: -50%;
        width: 200%; height: 200%; background:
            radial-gradient(circle at 20% 50%, rgba(255,255,255,0.08) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255,255,255,0.05) 0%, transparent 40%);
        pointer-events: none;
    }}
    .main-header h1 {{ margin: 0; font-size: 2.4rem; font-weight: 800; letter-spacing: -0.02em;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2); position: relative; }}
    .main-header p {{ margin: 0.5rem 0 0; opacity: 0.95; font-size: 1.1rem; font-weight: 500;
        position: relative; letter-spacing: 0.01em; }}

    /* ---------- KPI CARDS ---------- */
    .kpi-card {{
        background: white; border-radius: 12px; padding: 1.5rem 1.2rem;
        box-shadow: 0 2px 14px rgba(0,0,0,0.08); text-align: center;
        border-left: 5px solid {COLORS['card_border']};
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 1rem;
    }}
    .kpi-card:hover {{ transform: translateY(-3px); box-shadow: 0 6px 24px rgba(0,0,0,0.14); }}
    .kpi-card h3 {{ font-size: 0.85rem; color: #555; margin: 0 0 0.5rem;
        text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; }}
    .kpi-card .value {{ font-size: 2.2rem; font-weight: 800; color: {COLORS['card_value']};
        line-height: 1.15; }}
    .delta-positive {{ color: {COLORS['good']}; font-weight: 700; font-size: 0.9rem; margin-top: 0.3rem; }}
    .delta-negative {{ color: {COLORS['danger']}; font-weight: 700; font-size: 0.9rem; margin-top: 0.3rem; }}

    /* ---------- SECTION NARRATIVE ---------- */
    .section-narrative {{
        background: {COLORS['narrative_bg']};
        border-left: 5px solid {COLORS['narrative_border']};
        padding: 1.2rem 1.5rem; border-radius: 0 10px 10px 0;
        margin-bottom: 1.4rem; font-size: 1rem;
        color: {COLORS['narrative_text']};
        line-height: 1.65;
        box-shadow: 0 1px 6px rgba(0,0,0,0.05);
    }}
    .section-narrative strong {{ font-size: 1.05rem; }}

    /* ---------- BREADCRUMB / NAV BAR ---------- */
    .nav-breadcrumb {{
        display: flex; align-items: center; gap: 0.5rem;
        padding: 0.7rem 1.2rem; background: rgba(0,0,0,0.035);
        border-radius: 8px; margin-bottom: 1.2rem;
        font-size: 0.92rem; color: #444; font-weight: 500;
        border: 1px solid rgba(0,0,0,0.07);
    }}
    .nav-breadcrumb .sep {{ color: #aaa; font-weight: 400; }}
    .nav-breadcrumb .active {{ font-weight: 700; color: {COLORS['card_value']}; }}

    /* ---------- QUICK NAV PILLS ---------- */
    .quick-nav {{
        display: flex; flex-wrap: wrap; gap: 0.5rem;
        margin-bottom: 1.2rem;
    }}
    .quick-nav-pill {{
        display: inline-block; padding: 0.4rem 1rem;
        background: {COLORS['narrative_bg']}; border: 1px solid {COLORS['narrative_border']};
        border-radius: 20px; font-size: 0.85rem; color: {COLORS['narrative_text']};
        font-weight: 600;
        cursor: pointer; transition: all 0.2s ease; text-decoration: none;
    }}
    .quick-nav-pill:hover {{ background: {COLORS['card_border']}; color: white; }}

    /* ---------- SECTION HEADER ---------- */
    .section-header {{
        display: flex; align-items: center; gap: 0.6rem;
        padding: 0.8rem 0; margin: 1.5rem 0 0.8rem;
        border-bottom: 3px solid {COLORS['card_border']};
    }}
    .section-header h2 {{ margin: 0; font-size: 1.45rem; font-weight: 700; color: {COLORS['card_value']}; }}
    .section-header .badge {{
        background: {COLORS['card_border']}; color: white;
        padding: 0.2rem 0.7rem; border-radius: 10px;
        font-size: 0.75rem; font-weight: 700; letter-spacing: 0.02em;
    }}

    /* ---------- DATA TABLE STYLING ---------- */
    .styled-table {{
        width: 100%; border-collapse: collapse; font-size: 0.92rem;
        border-radius: 8px; overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    }}
    .styled-table th {{
        background: {COLORS['card_border']}; color: white;
        padding: 0.7rem 1rem; text-align: left; font-weight: 700;
        font-size: 0.9rem; letter-spacing: 0.02em;
    }}
    .styled-table td {{ padding: 0.6rem 1rem; border-bottom: 1px solid #e0e0e0; color: #333; font-weight: 500; }}
    .styled-table tr:hover td {{ background: {COLORS['narrative_bg']}; }}
    .styled-table tr:nth-child(even) td {{ background: rgba(0,0,0,0.015); }}

    /* ---------- DATAFRAME STYLING ---------- */
    div[data-testid="stDataFrame"] {{
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 8px;
        overflow: hidden;
    }}
    div[data-testid="stDataFrame"] table {{
        font-size: 0.9rem !important;
    }}

    /* ---------- EXPANDER STYLING ---------- */
    div[data-testid="stExpander"] {{
        border: 1px solid rgba(0,0,0,0.1); border-radius: 10px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.05); margin-bottom: 0.8rem;
    }}
    div[data-testid="stExpander"] summary {{
        font-weight: 600 !important; font-size: 0.95rem !important;
        color: #333 !important;
    }}

    /* ---------- METRIC STYLING ---------- */
    div[data-testid="stMetricValue"] {{ font-size: 1.8rem !important; font-weight: 800 !important; color: #222 !important; }}
    div[data-testid="stMetricDelta"] {{ font-size: 0.9rem !important; font-weight: 600 !important; }}
    div[data-testid="stMetricLabel"] {{ font-size: 0.9rem !important; font-weight: 600 !important; color: #555 !important; }}

    /* ---------- TAB STYLING ---------- */
    button[data-baseweb="tab"] {{
        font-size: 0.95rem !important; font-weight: 700 !important;
        padding: 0.7rem 1.2rem !important;
        color: #444 !important;
    }}
    button[data-baseweb="tab"]:hover {{
        background: {COLORS['narrative_bg']} !important;
        color: {COLORS['card_value']} !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {COLORS['card_value']} !important;
        border-bottom: 3px solid {COLORS['card_border']} !important;
    }}

    /* ---------- PLOTLY CHART CONTAINER ---------- */
    div[data-testid="stPlotlyChart"] {{
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 10px;
        padding: 0.5rem;
        margin-bottom: 1rem;
        background: white;
        box-shadow: 0 1px 6px rgba(0,0,0,0.04);
    }}

    /* ---------- SIDEBAR STYLING ---------- */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #fafafa 0%, #f0f2f6 100%);
    }}
    section[data-testid="stSidebar"] .block-container {{ padding-top: 1rem; }}
    section[data-testid="stSidebar"] label {{
        font-weight: 600 !important; color: #333 !important; font-size: 0.9rem !important;
    }}
    .sidebar-section {{
        background: white; border-radius: 10px; padding: 1rem 1.2rem;
        margin-bottom: 0.8rem; box-shadow: 0 1px 6px rgba(0,0,0,0.06);
        border: 1px solid rgba(0,0,0,0.07);
    }}
    .sidebar-nav-link {{
        display: block; padding: 0.45rem 0.7rem; margin: 0.2rem 0;
        border-radius: 6px; font-size: 0.88rem; color: #333; font-weight: 500;
        text-decoration: none; transition: all 0.15s ease;
    }}
    .sidebar-nav-link:hover {{ background: {COLORS['narrative_bg']}; color: {COLORS['card_value']}; font-weight: 600; }}

    /* ---------- MARKDOWN TEXT ---------- */
    .stMarkdown p {{ font-size: 0.95rem; color: #333; line-height: 1.65; }}
    .stMarkdown h1 {{ font-size: 1.8rem !important; font-weight: 800 !important; color: #222 !important; }}
    .stMarkdown h2 {{ font-size: 1.4rem !important; font-weight: 700 !important; color: #333 !important; }}
    .stMarkdown h3 {{ font-size: 1.15rem !important; font-weight: 700 !important; color: #444 !important; }}
    .stMarkdown strong {{ color: #222; }}

    /* ---------- HORIZONTAL RULE ---------- */
    hr {{ border: none; border-top: 2px solid rgba(0,0,0,0.08); margin: 1.5rem 0; }}

    /* ---------- FOOTER ---------- */
    .dashboard-footer {{
        text-align: center; color: #777; font-size: 0.88rem;
        padding: 2rem 0 1rem; border-top: 2px solid #e0e0e0;
        margin-top: 2rem;
    }}
    .dashboard-footer strong {{ color: #444; }}
    .dashboard-footer a {{ color: {COLORS['card_border']}; text-decoration: none; font-weight: 600; }}

    /* ---------- BACK TO TOP ---------- */
    .back-to-top {{
        position: fixed; bottom: 2rem; right: 2rem;
        background: {COLORS['card_border']}; color: white;
        width: 44px; height: 44px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.3rem; font-weight: 700;
        box-shadow: 0 3px 14px rgba(0,0,0,0.25);
        cursor: pointer; z-index: 999; text-decoration: none;
        transition: transform 0.2s ease, opacity 0.2s ease;
        opacity: 0.9;
    }}
    .back-to-top:hover {{ transform: scale(1.1); opacity: 1; }}

    /* ---------- ANIMATIONS ---------- */
    @keyframes fadeInUp {{ from {{ opacity:0; transform:translateY(12px); }} to {{ opacity:1; transform:translateY(0); }} }}
    .stTabs [data-baseweb="tab-panel"] {{ animation: fadeInUp 0.35s ease-out; }}
    </style>

    <a href="#top" class="back-to-top" title="Back to top"></a>
    <div id="top"></div>
    """, unsafe_allow_html=True)

    # ---- SIDEBAR ----
    st.sidebar.markdown("""
    <div style="text-align:center; margin-bottom:0.8rem;">
        <span style="font-size:2.5rem;"></span>
        <h2 style="margin:0.2rem 0 0; font-size:1.15rem; color:#333;">COSME Dashboard</h2>
        <p style="margin:0; font-size:0.78rem; color:#888;">Baseline–Midline M&amp;E</p>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")

    # Dataset selector
    dataset = st.sidebar.radio(
        "Dataset View",
        ["Combined Overview", "Forestry Groups", "Women Survey"],
        index=0,
        help="Combined Overview shows headline KPIs from both datasets side by side."
    )

    show_change = st.sidebar.toggle("Show Change (pp) Charts", value=False,
                                     help="Toggle percentage-point change visualisation")

    st.sidebar.markdown("---")

    # ---- QUICK NAVIGATION in sidebar ----
    if dataset == "Forestry Groups":
        st.sidebar.markdown("**Quick Navigate**")
        st.sidebar.markdown("""
        <div class="sidebar-section">
            <span class="sidebar-nav-link">Overview & KPIs</span>
            <span class="sidebar-nav-link">Group Characteristics</span>
            <span class="sidebar-nav-link">Governance & Gender</span>
            <span class="sidebar-nav-link">Training & Assets</span>
            <span class="sidebar-nav-link">Forest Condition</span>
            <span class="sidebar-nav-link">Income & Agroforestry</span>
        </div>
        """, unsafe_allow_html=True)
    elif dataset == "Women Survey":
        st.sidebar.markdown("**Quick Navigate**")
        st.sidebar.markdown("""
        <div class="sidebar-section">
            <span class="sidebar-nav-link">Household Profile</span>
            <span class="sidebar-nav-link">Shocks & Preparedness</span>
            <span class="sidebar-nav-link">Assets & Savings</span>
            <span class="sidebar-nav-link">Roles & Decisions</span>
            <span class="sidebar-nav-link">Climate & NbS</span>
            <span class="sidebar-nav-link">Life Skills & Norms</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("**Quick Navigate**")
        st.sidebar.markdown("""
        <div class="sidebar-section">
            <span class="sidebar-nav-link">Forestry Headlines</span>
            <span class="sidebar-nav-link">Women Survey Headlines</span>
            <span class="sidebar-nav-link">Comparative Snapshots</span>
        </div>
        """, unsafe_allow_html=True)

    st.sidebar.markdown("---")

    # ---- LOAD DATA ----
    script_dir = os.path.dirname(os.path.abspath(__file__))
    forestry_path = os.path.join(script_dir, FORESTRY_EXCEL)
    women_path = os.path.join(script_dir, WOMEN_EXCEL)

    # ---- HEADER ----
    if dataset == "Forestry Groups":
        st.markdown("""<div class="main-header">
            <h1>Community Forest Conservation Dashboard</h1>
            <p>Baseline vs Midline Assessment | Forestry Conservation Groups Functionality</p>
        </div>""", unsafe_allow_html=True)

        # Breadcrumb
        st.markdown('<div class="nav-breadcrumb"><span>COSME</span><span class="sep">›</span>'
                    '<span class="active">Forestry Groups</span></div>', unsafe_allow_html=True)

        data = load_forestry_data(forestry_path)

        # Sidebar KPI summary
        bl_grp = data['num_groups'].loc[data['num_groups']['Timepoint']=='Baseline','Groups_Assessed'].values[0]
        ml_grp = data['num_groups'].loc[data['num_groups']['Timepoint']=='Midline','Groups_Assessed'].values[0]
        st.sidebar.markdown("**Dataset Summary**")
        st.sidebar.markdown(f"""
        <div class="sidebar-section">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.3rem;">
                <span style="font-size:0.82rem; color:#666;">Baseline Groups</span>
                <strong>{int(bl_grp)}</strong>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:0.3rem;">
                <span style="font-size:0.82rem; color:#666;">Midline Groups</span>
                <strong>{int(ml_grp)}</strong>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span style="font-size:0.82rem; color:#666;">Source File</span>
                <span style="font-size:0.75rem; color:#999;">Forestry Excel</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        render_forestry_tabs(data, show_change)

    elif dataset == "Women Survey":
        st.markdown("""<div class="main-header">
            <h1>Women's Survey Dashboard</h1>
            <p>Baseline vs Midline Assessment | Household-Level Women's Empowerment &amp; Climate Resilience</p>
        </div>""", unsafe_allow_html=True)

        # Breadcrumb
        st.markdown('<div class="nav-breadcrumb"><span>COSME</span><span class="sep">›</span>'
                    '<span class="active">Women Survey</span></div>', unsafe_allow_html=True)

        w = load_women_data(women_path)

        # Sidebar sample size
        st.sidebar.markdown("**Dataset Summary**")
        st.sidebar.markdown("""
        <div class="sidebar-section">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.3rem;">
                <span style="font-size:0.82rem; color:#666;">Baseline N</span>
                <strong>707 women</strong>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:0.3rem;">
                <span style="font-size:0.82rem; color:#666;">Midline N</span>
                <strong>320 women</strong>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span style="font-size:0.82rem; color:#666;">Source File</span>
                <span style="font-size:0.75rem; color:#999;">Women Survey Excel</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        wt1, wt2, wt3, wt4, wt5, wt6 = st.tabs([
            "Household Profile & Services",
            "Shocks, Coping & Preparedness",
            "Assets, Land, Savings & Loans",
            "Roles, Time Use & Decisions",
            "Climate Change & NbS",
            "Life Skills & Social Norms"
        ])
        with wt1: render_women_tab1(w)
        with wt2: render_women_tab2(w)
        with wt3: render_women_tab3(w)
        with wt4: render_women_tab4(w)
        with wt5: render_women_tab5(w)
        with wt6: render_women_tab6(w)

    else:
        # Combined Overview
        st.markdown("""<div class="main-header">
            <h1>COSME Baseline–Midline Dashboard</h1>
            <p>Integrated M&amp;E Analysis | Community Forest Conservation &amp; Women's Survey</p>
        </div>""", unsafe_allow_html=True)

        # Breadcrumb
        st.markdown('<div class="nav-breadcrumb"><span class="active">COSME — Combined Overview</span></div>',
                    unsafe_allow_html=True)

        f_data = load_forestry_data(forestry_path)
        w_data = load_women_data(women_path)

        st.sidebar.markdown("**Datasets Loaded**")
        st.sidebar.markdown("""
        <div class="sidebar-section">
            <div style="margin-bottom:0.3rem;">Forestry Groups</div>
            <div>Women Survey</div>
        </div>
        """, unsafe_allow_html=True)

        render_synthesis_view(f_data, w_data)

    # ---- FOOTER ----
    st.markdown(f"""
    <div class="dashboard-footer">
        <strong>COSME Baseline–Midline Dashboard</strong><br>
        Community Forest Conservation Groups &amp; Women's Survey | Built with Streamlit + Plotly<br>
        <span style="font-size:0.75rem;">Last updated: February 2026</span>
    </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()

# ============================================================================
# HOW TO RUN:
# streamlit run cosme_dashboard.py
#
# Requirements:
# pip install streamlit pandas numpy plotly openpyxl
#
# Data files (same folder as this script):
# 1. Forest Functionality Basline_midline results.xlsx (sheet: Results)
# 2. Women Survey Basline_midline results.xlsx (sheet: Results Women)
#
# To adjust data mappings:
# - load_forestry_data(): row/col positions for forestry indicators
# - load_women_data(): row/col positions for women survey indicators
# - Each uses _val(raw, row_0based, col_0based)
#
# To add/remove indicators:
# - Add new DataFrame in the appropriate loader function
# - Add chart call in the corresponding render function
# ============================================================================
