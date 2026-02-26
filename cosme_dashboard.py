"""
=============================================================================
COSME INTEGRATED DASHBOARD
Baseline vs Midline Assessment
  1. Community Forest Conservation Groups (Group-level)
  2. Women's Survey (Household-level)
  3. Men's Survey (Household-level)
=============================================================================
A Streamlit + Plotly interactive dashboard for M&E analysis of the COSME
project, combining Forestry Conservation Groups, Women Survey, and Men Survey
datasets.

Excel files (place in the same folder as this script):
  • Forest Functionality Basline_midline results.xlsx (sheet "Results")
  • Women Survey Basline_midline results.xlsx (sheet "Results Women")
  • Men Survey Basline_midline results.xlsx (sheet "Results Men")

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

MEN_EXCEL = "Men Survey Basline_midline results.xlsx"
MEN_SHEET = "Results Men"

GJJ_KAP_WOMEN_EXCEL = "GJJ KAP Women Basline_endline results.xlsx"
GJJ_KAP_WOMEN_SHEET = "Results KAP Women Endline"

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
# MEN SURVEY DATA LOADER
# ============================================================================

@st.cache_data
def load_men_data(filepath):
    """
    Parse the Men Survey Excel file.
    Sheet 'Results Men' — 263 rows × 19 columns, non-standard dual-table layout.
    Left table cols 1-3 (label / BL / ML), right table cols 11-13 (label / BL / ML).
    All proportions are 0-1 scale; charts multiply ×100 for display.
    """
    try:
        raw = pd.read_excel(filepath, sheet_name=MEN_SHEET, header=None)
    except FileNotFoundError:
        st.error(f"Men Survey Excel not found: {filepath}")
        st.stop()

    m = {}

    # ---- A. HOUSEHOLD CHARACTERISTICS ----
    # Location type (Excel R12-13, _val rows 11-12, BL=col2, ML=col3)
    m['location'] = pd.DataFrame({
        'Category': ['Marine', 'Terrestrial'],
        'Baseline': [_val(raw, 11, 2), _val(raw, 12, 2)],
        'Midline': [_val(raw, 11, 3), _val(raw, 12, 3)],
    })

    # Education level (Excel R12-15 right, _val rows 11-14, cols 11-12)
    m['education'] = pd.DataFrame({
        'Category': ['College Level or Higher', 'Pre-primary/None/Other',
                     'Primary', 'Secondary/Vocational'],
        'Baseline': [_val(raw, 11, 11), _val(raw, 12, 11),
                     _val(raw, 13, 11), _val(raw, 14, 11)],
        'Midline': [_val(raw, 11, 12), _val(raw, 12, 12),
                    _val(raw, 13, 12), _val(raw, 14, 12)],
    })

    # Main HH economic activity (Excel R17-28, _val rows 16-27, labels=col1, BL=col2, ML=col3)
    econ_labels = [_clean_label(_val(raw, r, 1)) for r in range(16, 28)
                   if _val(raw, r, 1) != 0]
    econ_bl = [_val(raw, r, 2) for r in range(16, 28) if _val(raw, r, 1) != 0]
    econ_ml = [_val(raw, r, 3) for r in range(16, 28) if _val(raw, r, 1) != 0]
    m['main_econ'] = pd.DataFrame({
        'Activity': econ_labels, 'Baseline': econ_bl, 'Midline': econ_ml})

    # ---- B. CLIMATE CHANGE & NBS KNOWLEDGE ----
    # CC heard (Excel R36-37, _val rows 35-36, col 2-3)
    m['cc_heard'] = pd.DataFrame({
        'Response': ['Yes', 'No'],
        'Baseline': [_val(raw, 35, 2), _val(raw, 36, 2)],
        'Midline': [_val(raw, 35, 3), _val(raw, 36, 3)],
    })

    # CC define adequacy (Excel R41-44, _val rows 40-43, col 2-3)
    m['cc_define'] = pd.DataFrame({
        'Response': ['Completely Acceptable', 'Somewhat Acceptable',
                     'Not Acceptable', "Doesn't Know/Answer"],
        'Baseline': [_val(raw, r, 2) for r in range(40, 44)],
        'Midline': [_val(raw, r, 3) for r in range(40, 44)],
    })

    # CC environmental effects (Excel R48-59, _val rows 47-58, col 2-3)
    cc_env_labels = ['Hotter Temperatures', 'More Extreme Weather Events',
                     'Increased Drought', 'Warming Oceans/Water Bodies',
                     'Sea Level Rise', 'Loss of Species', 'Migration of Species',
                     'Animal Migration Pattern Changes', 'Spread of Disease/Algal Blooms',
                     'Ocean Acidification (Coral Reefs)',
                     'Increased Species Invasions', "I Don't Know"]
    m['cc_env_effects'] = pd.DataFrame({
        'Effect': cc_env_labels,
        'Baseline': [_val(raw, r, 2) for r in range(47, 59)],
        'Midline': [_val(raw, r, 3) for r in range(47, 59)],
    })

    # CC livelihood effects (Excel R36-48 right, _val rows 35-47, cols 11-12)
    cc_live_labels = ['Increased Food Insecurity', 'Increased Water Insecurity',
                      'Personal Risk from Extremes', 'Forced Migration (Disaster)',
                      'Changes in Livelihood Activities', 'Reduced Livelihood Activities',
                      'Extreme Weather on Infrastructure', 'Reduced Agricultural Productivity',
                      'Crop Loss', 'Loss of Livestock', 'Reduced Livestock Productivity',
                      'Loss of Savings/Assets', "I Don't Know"]
    m['cc_livelihood_effects'] = pd.DataFrame({
        'Effect': cc_live_labels,
        'Baseline': [_val(raw, r, 11) for r in range(35, 48)],
        'Midline': [_val(raw, r, 12) for r in range(35, 48)],
    })

    # NbS heard (Excel R63-64, _val rows 62-63, col 2-3)
    m['nbs_heard'] = pd.DataFrame({
        'Response': ['Yes', 'No'],
        'Baseline': [_val(raw, 62, 2), _val(raw, 63, 2)],
        'Midline': [_val(raw, 62, 3), _val(raw, 63, 3)],
    })

    # NbS define (Excel R52-55 right, _val rows 51-54, cols 11-12)
    m['nbs_define'] = pd.DataFrame({
        'Response': ['Completely Acceptable', 'Somewhat Acceptable',
                     'Not Acceptable', "Doesn't Know/Answer"],
        'Baseline': [_val(raw, r, 11) for r in range(51, 55)],
        'Midline': [_val(raw, r, 12) for r in range(51, 55)],
    })

    # NbS examples cited (Excel R68-75, _val rows 67-74, col 2-3)
    nbs_ex_labels = ['Mangrove Restoration', 'Coral Reef Restoration',
                     'Reforestation/Prevention of Deforestation',
                     'Sustainable Seaweed Farming', "I Don't Know",
                     'Rainwater Harvesting', 'Sustainable Agriculture',
                     'Solar Energy']
    m['nbs_examples'] = pd.DataFrame({
        'Example': nbs_ex_labels,
        'Baseline': [_val(raw, r, 2) for r in range(67, 75)],
        'Midline': [_val(raw, r, 3) for r in range(67, 75)],
    })

    # NbS benefits (Excel R59-70 right, _val rows 58-69, cols 11-12)
    nbs_ben_labels = ['Carbon Capture', 'Reduce Storm Surges/Flooding',
                      'Defense Against Salination', 'Improve Air Quality',
                      'Water Conservation', 'Soil Health & Fertility',
                      'Support Pollinators/Biodiversity',
                      'Local Biodiversity/Ecosystem', 'Fish Diversity & Quantity',
                      'Seawater Quality & Clarity',
                      'Improved/Diversified Livelihoods', "I Don't Know"]
    m['nbs_benefits'] = pd.DataFrame({
        'Benefit': nbs_ben_labels,
        'Baseline': [_val(raw, r, 11) for r in range(58, 70)],
        'Midline': [_val(raw, r, 12) for r in range(58, 70)],
    })

    # ---- B1. MANGROVE RESTORATION ----
    # Heard of mangrove (Excel R81-83, _val rows 80-82, col 2-3)
    m['mangrove_heard'] = pd.DataFrame({
        'Response': ['Heard & Importance', 'Heard Only', 'Not Heard'],
        'Baseline': [_val(raw, 80, 2), _val(raw, 81, 2), _val(raw, 82, 2)],
        'Midline': [_val(raw, 80, 3), _val(raw, 81, 3), _val(raw, 82, 3)],
    })
    # Female HH ever participated (Excel R81-82 right, _val rows 80-81, cols 11-12)
    m['mangrove_ever'] = pd.DataFrame({
        'Response': ['Yes', 'No'],
        'Baseline': [_val(raw, 80, 11), _val(raw, 81, 11)],
        'Midline': [_val(raw, 80, 12), _val(raw, 81, 12)],
    })
    # Female HH currently involved (Excel R87-88, _val rows 86-87, col 2-3)
    m['mangrove_current'] = pd.DataFrame({
        'Response': ['Yes', 'No'],
        'Baseline': [_val(raw, 86, 2), _val(raw, 87, 2)],
        'Midline': [_val(raw, 86, 3), _val(raw, 87, 3)],
    })
    # Men supporting (Excel R86-88 right, _val rows 85-87, cols 11-12)
    m['mangrove_support'] = pd.DataFrame({
        'Response': ['Yes', 'No', 'Somehow'],
        'Baseline': [_val(raw, 85, 11), _val(raw, 86, 11), _val(raw, 87, 11)],
        'Midline': [_val(raw, 85, 12), _val(raw, 86, 12), _val(raw, 87, 12)],
    })
    # Type of support (Excel R92-98, _val rows 91-97, col 2-3)
    support_labels = ['Encouraged Participation', 'Sought Community Support',
                      'Supported with HH Chores', 'Supported with Restoration Work',
                      'Supported with Materials Purchase', 'None', 'Other']
    m['mangrove_support_type'] = pd.DataFrame({
        'Type': support_labels,
        'Baseline': [_val(raw, r, 2) for r in range(91, 98)],
        'Midline': [_val(raw, r, 3) for r in range(91, 98)],
    })

    # ---- B2. SEAWEED FARMING ----
    m['seaweed_heard'] = pd.DataFrame({
        'Response': ['Heard & Importance', 'Heard Only', 'Not Heard'],
        'Baseline': [_val(raw, 103, 2), _val(raw, 104, 2), _val(raw, 105, 2)],
        'Midline': [_val(raw, 103, 3), _val(raw, 104, 3), _val(raw, 105, 3)],
    })
    m['seaweed_ever'] = pd.DataFrame({
        'Response': ['Yes', 'No'],
        'Baseline': [_val(raw, 103, 11), _val(raw, 104, 11)],
        'Midline': [_val(raw, 103, 12), _val(raw, 104, 12)],
    })
    m['seaweed_current'] = pd.DataFrame({
        'Response': ['Yes', 'No'],
        'Baseline': [_val(raw, 109, 2), _val(raw, 110, 2)],
        'Midline': [_val(raw, 109, 3), _val(raw, 110, 3)],
    })
    m['seaweed_support'] = pd.DataFrame({
        'Response': ['Yes', 'No', 'Somehow'],
        'Baseline': [_val(raw, 108, 11), _val(raw, 109, 11), _val(raw, 110, 11)],
        'Midline': [_val(raw, 108, 12), _val(raw, 109, 12), _val(raw, 110, 12)],
    })
    m['seaweed_support_type'] = pd.DataFrame({
        'Type': support_labels,
        'Baseline': [_val(raw, r, 2) for r in range(114, 121)],
        'Midline': [_val(raw, r, 3) for r in range(114, 121)],
    })

    # ---- B3. FOREST MANAGEMENT ----
    m['forest_heard'] = pd.DataFrame({
        'Response': ['Yes', 'Not Heard'],
        'Baseline': [_val(raw, 126, 2), _val(raw, 127, 2)],
        'Midline': [_val(raw, 126, 3), _val(raw, 127, 3)],
    })
    m['forest_ever'] = pd.DataFrame({
        'Response': ['Yes', 'No'],
        'Baseline': [_val(raw, 126, 11), _val(raw, 127, 11)],
        'Midline': [_val(raw, 126, 12), _val(raw, 127, 12)],
    })
    m['forest_current'] = pd.DataFrame({
        'Response': ['Yes', 'No'],
        'Baseline': [_val(raw, 132, 2), _val(raw, 133, 2)],
        'Midline': [_val(raw, 132, 3), _val(raw, 133, 3)],
    })
    m['forest_support'] = pd.DataFrame({
        'Response': ['Yes', 'No', 'Somehow'],
        'Baseline': [_val(raw, 132, 11), _val(raw, 133, 11), _val(raw, 134, 11)],
        'Midline': [_val(raw, 132, 12), _val(raw, 133, 12), _val(raw, 134, 12)],
    })
    m['forest_support_type'] = pd.DataFrame({
        'Type': support_labels,
        'Baseline': [_val(raw, r, 2) for r in range(137, 144)],
        'Midline': [_val(raw, r, 3) for r in range(137, 144)],
    })

    # ---- C. ROLES, RESPONSIBILITIES & TIME POVERTY ----
    role_labels = ['Cook Food', 'Clean/Sweep House', 'Look After Livestock',
                   'Maintain Garden', 'Care for Ill/Elderly/Disabled',
                   'Fetch Firewood', 'Fetch Water', 'Wash Clothes',
                   'Main Income Provider', 'Care for Children']

    # Roles SHOULD — Joint % (Excel R152-161, _val rows 151-160, col 2-3)
    m['roles_should_joint'] = pd.DataFrame({
        'Role': role_labels,
        'Baseline': [_val(raw, r, 2) for r in range(151, 161)],
        'Midline': [_val(raw, r, 3) for r in range(151, 161)],
    })
    # Roles SHOULD — Women only (Excel R152-161 right, _val rows 151-160, cols 11-12)
    m['roles_should_women'] = pd.DataFrame({
        'Role': role_labels,
        'Baseline': [_val(raw, r, 11) for r in range(151, 161)],
        'Midline': [_val(raw, r, 12) for r in range(151, 161)],
    })
    # Roles SHOULD — Men only (Excel R152-161 right, _val rows 151-160, cols 13-14)
    m['roles_should_men'] = pd.DataFrame({
        'Role': role_labels,
        'Baseline': [_val(raw, r, 13) for r in range(151, 161)],
        'Midline': [_val(raw, r, 14) for r in range(151, 161)],
    })

    # Roles DOES — Joint % (Excel R166-175, _val rows 165-174, col 2-3)
    m['roles_does_joint'] = pd.DataFrame({
        'Role': role_labels,
        'Baseline': [_val(raw, r, 2) for r in range(165, 175)],
        'Midline': [_val(raw, r, 3) for r in range(165, 175)],
    })
    # Roles DOES — Men(Myself) (Excel R166-175 right, _val rows 165-174, cols 11-12)
    m['roles_does_men'] = pd.DataFrame({
        'Role': role_labels,
        'Baseline': [_val(raw, r, 11) for r in range(165, 175)],
        'Midline': [_val(raw, r, 12) for r in range(165, 175)],
    })
    # Roles DOES — Women(MySpouse) (Excel R166-175 right, _val rows 165-174, cols 13-14)
    m['roles_does_women'] = pd.DataFrame({
        'Role': role_labels,
        'Baseline': [_val(raw, r, 13) for r in range(165, 175)],
        'Midline': [_val(raw, r, 14) for r in range(165, 175)],
    })

    # Time use (hours per day)
    # Unpaid care activities (Excel R178-182, _val rows 177-181, col 2-3)
    unpaid_labels = ['Child/Elderly/Disabled Care', 'Cooking/Dishes',
                     'Cleaning/Washing', 'Fetching Water', 'Fetching Firewood']
    m['time_unpaid'] = pd.DataFrame({
        'Activity': unpaid_labels,
        'Baseline': [_val(raw, r, 2) for r in range(177, 182)],
        'Midline': [_val(raw, r, 3) for r in range(177, 182)],
    })
    m['time_unpaid_total'] = pd.DataFrame({
        'Category': ['Unpaid Care Work'],
        'Baseline': [_val(raw, 183, 2)], 'Midline': [_val(raw, 183, 3)]})

    # Productive work (Excel R186-191, _val rows 185-190, col 2-3)
    prod_labels = ['Farm Work (Others)', 'Farm Work (Own)', 'Fishing',
                   'Seaweed Farming', 'Selling at Market', 'Formal Employment']
    m['time_productive'] = pd.DataFrame({
        'Activity': prod_labels,
        'Baseline': [_val(raw, r, 2) for r in range(185, 191)],
        'Midline': [_val(raw, r, 3) for r in range(185, 191)],
    })
    m['time_productive_total'] = pd.DataFrame({
        'Category': ['Productive Work'],
        'Baseline': [_val(raw, 192, 2)], 'Midline': [_val(raw, 192, 3)]})

    # Community conservation (Excel R195-197, _val rows 194-196, col 2-3)
    cons_labels = ['Mangrove Restoration', 'Seaweed Farming', 'Forest Mgmt & Conservation']
    m['time_conservation'] = pd.DataFrame({
        'Activity': cons_labels,
        'Baseline': [_val(raw, r, 2) for r in range(194, 197)],
        'Midline': [_val(raw, r, 3) for r in range(194, 197)],
    })
    m['time_conservation_total'] = pd.DataFrame({
        'Category': ['Community Conservation Work'],
        'Baseline': [_val(raw, 198, 2)], 'Midline': [_val(raw, 198, 3)]})

    # Time summary (all categories)
    m['time_summary'] = pd.DataFrame({
        'Category': ['Unpaid Care Work', 'Productive Work', 'Community Conservation',
                     'Personal Development', 'Personal Care', 'Leisure', 'Other'],
        'Baseline': [_val(raw, 183, 2), _val(raw, 192, 2), _val(raw, 198, 2),
                     _val(raw, 200, 2), _val(raw, 205, 2), _val(raw, 207, 2), _val(raw, 209, 2)],
        'Midline': [_val(raw, 183, 3), _val(raw, 192, 3), _val(raw, 198, 3),
                    _val(raw, 200, 3), _val(raw, 205, 3), _val(raw, 207, 3), _val(raw, 209, 3)],
    })

    # ---- D. DECISION-MAKING ----
    decision_labels = ['Start Small Business', 'Large HH Purchases',
                       'Using HH Savings', 'Taking Out Loans',
                       'Children Education', 'Routine HH Purchases',
                       'Women Go to Mangrove/Seaweed/Forest',
                       'Use of HH Income', 'Women Go to Market',
                       'Women Go to Farm', 'Invest Borrowed/Saved Money']

    # Decision SHOULD — Joint (Excel R218-228, _val rows 217-227, col 2-3)
    m['decision_should_joint'] = pd.DataFrame({
        'Decision': decision_labels,
        'Baseline': [_val(raw, r, 2) for r in range(217, 228)],
        'Midline': [_val(raw, r, 3) for r in range(217, 228)],
    })
    # Decision SHOULD — Women only (Excel R219-229 right, _val rows 218-228, cols 11-12)
    m['decision_should_women'] = pd.DataFrame({
        'Decision': decision_labels,
        'Baseline': [_val(raw, r, 11) for r in range(218, 229)],
        'Midline': [_val(raw, r, 12) for r in range(218, 229)],
    })
    # Decision SHOULD — Men only (Excel R219-229 right, _val rows 218-228, cols 13-14)
    m['decision_should_men'] = pd.DataFrame({
        'Decision': decision_labels,
        'Baseline': [_val(raw, r, 13) for r in range(218, 229)],
        'Midline': [_val(raw, r, 14) for r in range(218, 229)],
    })

    # Decision DOES — Joint (Excel R234-244, _val rows 233-243, col 2-3)
    m['decision_does_joint'] = pd.DataFrame({
        'Decision': decision_labels,
        'Baseline': [_val(raw, r, 2) for r in range(233, 244)],
        'Midline': [_val(raw, r, 3) for r in range(233, 244)],
    })
    # Decision DOES — Men(Myself) (Excel R234-244 right, _val rows 233-243, cols 11-12)
    m['decision_does_men'] = pd.DataFrame({
        'Decision': decision_labels,
        'Baseline': [_val(raw, r, 11) for r in range(233, 244)],
        'Midline': [_val(raw, r, 12) for r in range(233, 244)],
    })
    # Decision DOES — Women(MySpouse) (Excel R234-244 right, _val rows 233-243, cols 13-14)
    m['decision_does_women'] = pd.DataFrame({
        'Decision': decision_labels,
        'Baseline': [_val(raw, r, 13) for r in range(233, 244)],
        'Midline': [_val(raw, r, 14) for r in range(233, 244)],
    })

    # ---- E. SOCIAL NORMS ----
    sn_labels = [
        'Income -> Husband Controls', 'Men Better Business Ideas',
        "Men Earn, Women Look After Home", 'Inappropriate Dress -> Her Fault',
        'Cook & Clean -> Good Marriage', 'Embarrassing for Men to Do Chores',
        'Planting Crops (Family Food)', 'Restoring Ecosystems (Mangrove/Forest)',
        'Only Men Drive Boats', 'Ok for Women to Express Emotions',
        'Supportive of Diverse People', 'Women Gain Rights -> Men Lose',
        'Stronger Women -> Stronger Families',
    ]
    sn_rows = list(range(250, 263))

    # Agree or Strongly Agree (Excel R251-263, _val rows 250-262, col 2-3)
    m['socialnorms_agree'] = pd.DataFrame({
        'Norm': sn_labels,
        'Baseline': [_val(raw, r, 2) for r in sn_rows],
        'Midline': [_val(raw, r, 3) for r in sn_rows],
    })
    # Strongly Agree only (Excel R251-263 right, _val rows 250-262, cols 11-12)
    m['socialnorms_strong'] = pd.DataFrame({
        'Norm': sn_labels,
        'Baseline': [_val(raw, r, 11) for r in sn_rows],
        'Midline': [_val(raw, r, 12) for r in sn_rows],
    })

    return m


# ============================================================================
# GJJ KAP WOMEN (BASELINE / ENDLINE) DATA LOADER
# ============================================================================

@st.cache_data
def load_gjj_kap_women_data(filepath):
    """
    Parse the GJJ KAP Women Survey Excel file.
    Sheet 'Results KAP Women Endline' — 228 rows x 9 columns.
    All data lives in Column B (labels) + Columns C-H (values).
    Proportions are 0-1 scale; charts multiply x100 for display.
    Row references below are 1-based Excel rows; _val() uses 0-based.
    """
    try:
        raw = pd.read_excel(filepath, sheet_name=GJJ_KAP_WOMEN_SHEET, header=None)
    except FileNotFoundError:
        st.error(f"GJJ KAP Women Excel not found: {filepath}")
        st.stop()

    g = {}

    # ---- A. SELF — Self-Esteem, Self-Compassion, Confidence ----
    # 3 statements: R10-R12 (0-based 9-11), Baseline Likert: StronglyAgree(c3) Agree(c4) Disagree(c5) StronglyDisagree(c6)
    self_statements = [
        _clean_label(_val(raw, 9, 1)),   # "I have many strengths and qualities"
        _clean_label(_val(raw, 10, 1)),  # "I believe my feelings and opinions are important"
        _clean_label(_val(raw, 11, 1)),  # "I see myself as an equal..."
    ]

    g['self_baseline_likert'] = pd.DataFrame({
        'Statement': self_statements,
        'Strongly agree': [_val(raw, r, 2) for r in range(9, 12)],
        'Agree': [_val(raw, r, 3) for r in range(9, 12)],
        'Disagree': [_val(raw, r, 4) for r in range(9, 12)],
        'Strongly disagree': [_val(raw, r, 5) for r in range(9, 12)],
    })

    # Endline Likert: R24-R26 (0-based 23-25)
    g['self_endline_likert'] = pd.DataFrame({
        'Statement': self_statements,
        'Strongly agree': [_val(raw, r, 2) for r in range(23, 26)],
        'Agree': [_val(raw, r, 3) for r in range(23, 26)],
        'Disagree': [_val(raw, r, 4) for r in range(23, 26)],
        'Strongly disagree': [_val(raw, r, 5) for r in range(23, 26)],
    })

    # Strongly Agree comparison: R17-R19 (0-based 16-18), BL=c3, EL=c4
    g['self_strongly_agree'] = pd.DataFrame({
        'Statement': self_statements,
        'Baseline': [_val(raw, r, 2) for r in range(16, 19)],
        'Endline': [_val(raw, r, 3) for r in range(16, 19)],
    })

    # Agreement vs Disagreement: R31-R33 (0-based 30-32)
    g['self_agreement'] = pd.DataFrame({
        'Statement': self_statements,
        'Agreement_BL': [_val(raw, r, 2) for r in range(30, 33)],
        'Agreement_EL': [_val(raw, r, 3) for r in range(30, 33)],
        'Disagreement_BL': [_val(raw, r, 4) for r in range(30, 33)],
        'Disagreement_EL': [_val(raw, r, 5) for r in range(30, 33)],
    })

    # Self-compassion frequency: R38-R41 (0-based 37-40), BL=c3, EL=c4
    compassion_cats = [
        _clean_label(_val(raw, r, 1)) for r in range(37, 41)
    ]
    g['self_compassion'] = pd.DataFrame({
        'Category': compassion_cats,
        'Baseline': [_val(raw, r, 2) for r in range(37, 41)],
        'Endline': [_val(raw, r, 3) for r in range(37, 41)],
    })

    # ---- B. RELATIONAL WELLBEING ----
    rel_statements = [
        _clean_label(_val(raw, r, 1)) for r in range(47, 54)
    ]

    # Baseline frequency: R48-R54 (0-based 47-53), 6 cols: Always(c3) Frequently(c4) Sometimes(c5) Rarely(c6) Never(c7) NA(c8)
    g['rel_baseline_freq'] = pd.DataFrame({
        'Statement': rel_statements,
        'Always': [_val(raw, r, 2) for r in range(47, 54)],
        'Frequently': [_val(raw, r, 3) for r in range(47, 54)],
        'Sometimes': [_val(raw, r, 4) for r in range(47, 54)],
        'Rarely': [_val(raw, r, 5) for r in range(47, 54)],
        'Never': [_val(raw, r, 6) for r in range(47, 54)],
        'NA': [_val(raw, r, 7) for r in range(47, 54)],
    })

    # Endline frequency: R59-R65 (0-based 58-64)
    g['rel_endline_freq'] = pd.DataFrame({
        'Statement': rel_statements,
        'Always': [_val(raw, r, 2) for r in range(58, 65)],
        'Frequently': [_val(raw, r, 3) for r in range(58, 65)],
        'Sometimes': [_val(raw, r, 4) for r in range(58, 65)],
        'Rarely': [_val(raw, r, 5) for r in range(58, 65)],
        'Never': [_val(raw, r, 6) for r in range(58, 65)],
        'NA': [_val(raw, r, 7) for r in range(58, 65)],
    })

    # Always/Frequently vs Rarely/Never comparison: R70-R76 (0-based 69-75)
    # Cols: AF_BL(c3) AF_EL(c4) RN_BL(c5) RN_EL(c6) DIF_AF(c8) DIF_RN(c9)
    g['rel_af_rn'] = pd.DataFrame({
        'Statement': rel_statements,
        'AF_Baseline': [_val(raw, r, 2) for r in range(69, 76)],
        'AF_Endline': [_val(raw, r, 3) for r in range(69, 76)],
        'RN_Baseline': [_val(raw, r, 4) for r in range(69, 76)],
        'RN_Endline': [_val(raw, r, 5) for r in range(69, 76)],
        'DIF_AF': [_val(raw, r, 7) for r in range(69, 76)],
        'DIF_RN': [_val(raw, r, 8) for r in range(69, 76)],
    })

    # Relational agreement statements — Baseline: R81-R82 (0-based 80-81)
    rel_agree_stmts = [
        _clean_label(_val(raw, 80, 1)),
        _clean_label(_val(raw, 81, 1)),
    ]
    g['rel_agree_baseline'] = pd.DataFrame({
        'Statement': rel_agree_stmts,
        'Strongly agree': [_val(raw, r, 2) for r in range(80, 82)],
        'Agree': [_val(raw, r, 3) for r in range(80, 82)],
        'Disagree': [_val(raw, r, 4) for r in range(80, 82)],
        'Strongly disagree': [_val(raw, r, 5) for r in range(80, 82)],
    })

    # Endline: R87-R88 (0-based 86-87)
    g['rel_agree_endline'] = pd.DataFrame({
        'Statement': rel_agree_stmts,
        'Strongly agree': [_val(raw, r, 2) for r in range(86, 88)],
        'Agree': [_val(raw, r, 3) for r in range(86, 88)],
        'Disagree': [_val(raw, r, 4) for r in range(86, 88)],
        'Strongly disagree': [_val(raw, r, 5) for r in range(86, 88)],
    })

    # Agreement vs Disagreement: R93-R94 (0-based 92-93)
    rel_agree_summary_stmts = [
        _clean_label(_val(raw, 92, 1)),
        _clean_label(_val(raw, 93, 1)),
    ]
    g['rel_agreement_summary'] = pd.DataFrame({
        'Statement': rel_agree_summary_stmts,
        'Agreement_BL': [_val(raw, r, 2) for r in range(92, 94)],
        'Agreement_EL': [_val(raw, r, 3) for r in range(92, 94)],
        'Disagreement_BL': [_val(raw, r, 4) for r in range(92, 94)],
        'Disagreement_EL': [_val(raw, r, 5) for r in range(92, 94)],
    })

    # ---- C. GENDER TRANSFORMATION: SHARED RESPONSIBILITY ----
    # Husband supports household chores: R100-R101 (0-based 99-100), BL=c3, EL=c4
    g['shared_chores_yn'] = pd.DataFrame({
        'Response': [_clean_label(_val(raw, r, 1)) for r in range(99, 101)],
        'Baseline': [_val(raw, r, 2) for r in range(99, 101)],
        'Endline': [_val(raw, r, 3) for r in range(99, 101)],
    })

    # Time since husband supporting: R105-R111 (0-based 104-110)
    g['chore_duration'] = pd.DataFrame({
        'Category': [_clean_label(_val(raw, r, 1)) for r in range(104, 111)],
        'Baseline': [_val(raw, r, 2) for r in range(104, 111)],
        'Endline': [_val(raw, r, 3) for r in range(104, 111)],
    })

    # Frequency of husband chores: R115-R119 (0-based 114-118)
    g['chore_frequency'] = pd.DataFrame({
        'Category': [_clean_label(_val(raw, r, 1)) for r in range(114, 119)],
        'Baseline': [_val(raw, r, 2) for r in range(114, 119)],
        'Endline': [_val(raw, r, 3) for r in range(114, 119)],
    })

    # Discussed sharing unpaid chores: R123-R124 (0-based 122-123)
    g['chore_discussed'] = pd.DataFrame({
        'Response': [_clean_label(_val(raw, r, 1)) for r in range(122, 124)],
        'Baseline': [_val(raw, r, 2) for r in range(122, 124)],
        'Endline': [_val(raw, r, 3) for r in range(122, 124)],
    })

    # Person who started conversation: R128-R130 (0-based 127-129)
    g['chore_initiator'] = pd.DataFrame({
        'Person': [_clean_label(_val(raw, r, 1)) for r in range(127, 130)],
        'Baseline': [_val(raw, r, 2) for r in range(127, 130)],
        'Endline': [_val(raw, r, 3) for r in range(127, 130)],
    })

    # Husband completed significant chore: R134-R135 (0-based 133-134)
    g['chore_completed'] = pd.DataFrame({
        'Response': [_clean_label(_val(raw, r, 1)) for r in range(133, 135)],
        'Baseline': [_val(raw, r, 2) for r in range(133, 135)],
        'Endline': [_val(raw, r, 3) for r in range(133, 135)],
    })

    # Type of chore: R139-R143 (0-based 138-142)
    g['chore_type'] = pd.DataFrame({
        'Chore': [_clean_label(_val(raw, r, 1)) for r in range(138, 143)],
        'Baseline': [_val(raw, r, 2) for r in range(138, 143)],
        'Endline': [_val(raw, r, 3) for r in range(138, 143)],
    })

    # Hours saved: R147-R152 (0-based 146-151)
    g['hours_saved'] = pd.DataFrame({
        'Hours': [_clean_label(_val(raw, r, 1)) for r in range(146, 152)],
        'Baseline': [_val(raw, r, 2) for r in range(146, 152)],
        'Endline': [_val(raw, r, 3) for r in range(146, 152)],
    })

    # Frequency husband supports women's self-time: R156-R161 (0-based 155-160)
    g['support_self_time'] = pd.DataFrame({
        'Category': [_clean_label(_val(raw, r, 1)) for r in range(155, 161)],
        'Baseline': [_val(raw, r, 2) for r in range(155, 161)],
        'Endline': [_val(raw, r, 3) for r in range(155, 161)],
    })

    # ---- D. GENDER TRANSFORMATION: SHARED POWER ----
    # Conversations to change decisions: R168-R169 (0-based 167-168)
    g['decision_conversations'] = pd.DataFrame({
        'Response': [_clean_label(_val(raw, r, 1)) for r in range(167, 169)],
        'Baseline': [_val(raw, r, 2) for r in range(167, 169)],
        'Endline': [_val(raw, r, 3) for r in range(167, 169)],
    })

    # Made important decisions: R173-R174 (0-based 172-173)
    g['decisions_made'] = pd.DataFrame({
        'Response': [_clean_label(_val(raw, r, 1)) for r in range(172, 174)],
        'Baseline': [_val(raw, r, 2) for r in range(172, 174)],
        'Endline': [_val(raw, r, 3) for r in range(172, 174)],
    })

    # Type of decision: R178-R188 (0-based 177-187)
    g['decision_types'] = pd.DataFrame({
        'Decision': [_clean_label(_val(raw, r, 1)) for r in range(177, 188)],
        'Baseline': [_val(raw, r, 2) for r in range(177, 188)],
        'Endline': [_val(raw, r, 3) for r in range(177, 188)],
    })

    # Person making decision: R192-R194 (0-based 191-193)
    g['decision_maker'] = pd.DataFrame({
        'Person': [_clean_label(_val(raw, r, 1)) for r in range(191, 194)],
        'Baseline': [_val(raw, r, 2) for r in range(191, 194)],
        'Endline': [_val(raw, r, 3) for r in range(191, 194)],
    })

    # Equal say in joint decisions: R198-R199 (0-based 197-198)
    g['equal_say'] = pd.DataFrame({
        'Response': [_clean_label(_val(raw, r, 1)) for r in range(197, 199)],
        'Baseline': [_val(raw, r, 2) for r in range(197, 199)],
        'Endline': [_val(raw, r, 3) for r in range(197, 199)],
    })

    # ---- E. GENDER TRANSFORMATION: AUTONOMY & LEADERSHIP ----
    # Hide money to save: R205-R210 (0-based 204-209)
    g['hide_money'] = pd.DataFrame({
        'Category': [_clean_label(_val(raw, r, 1)) for r in range(204, 210)],
        'Baseline': [_val(raw, r, 2) for r in range(204, 210)],
        'Endline': [_val(raw, r, 3) for r in range(204, 210)],
    })

    # Husband support for women becoming community leader: R214-R219 (0-based 213-218)
    g['support_leader'] = pd.DataFrame({
        'Category': [_clean_label(_val(raw, r, 1)) for r in range(213, 219)],
        'Baseline': [_val(raw, r, 2) for r in range(213, 219)],
        'Endline': [_val(raw, r, 3) for r in range(213, 219)],
    })

    # Husband support if started/grew own business: R223-R228 (0-based 222-227)
    g['support_business'] = pd.DataFrame({
        'Category': [_clean_label(_val(raw, r, 1)) for r in range(222, 228)],
        'Baseline': [_val(raw, r, 2) for r in range(222, 228)],
        'Endline': [_val(raw, r, 3) for r in range(222, 228)],
    })

    return g


# ============================================================================
# CHART HELPERS
# ============================================================================

def _export_data_csv(data_dict, prefix='data'):
    """Combine all DataFrames in a dict into a single CSV for download."""
    import io
    buf = io.StringIO()
    first = True
    for key, df in data_dict.items():
        if not isinstance(df, pd.DataFrame) or df.empty:
            continue
        if not first:
            buf.write('\n')
        buf.write(f'--- {key} ---\n')
        df.to_csv(buf, index=False)
        first = False
    return buf.getvalue()


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
        # Sort so longest bars appear at top (Plotly renders bottom-to-top)
        plot_df['_sort'] = plot_df[['Baseline', 'Midline']].max(axis=1)
        plot_df = plot_df.sort_values('_sort', ascending=True).drop(columns='_sort')
        fig = go.Figure()
        fig.add_trace(go.Bar(y=plot_df[cat_col], x=plot_df['Baseline'], name='Baseline',
                             orientation='h', marker_color=cb,
                             text=plot_df['Baseline'].apply(lambda x: f"{x:.1f}%"), textposition='auto'))
        fig.add_trace(go.Bar(y=plot_df[cat_col], x=plot_df['Midline'], name='Midline',
                             orientation='h', marker_color=cm,
                             text=plot_df['Midline'].apply(lambda x: f"{x:.1f}%"), textposition='auto'))
        fig.update_layout(title=title, barmode='group', height=height,
                          xaxis_title=y_label, legend=dict(orientation='h', yanchor='bottom', y=1.02),
                          yaxis=dict(categoryorder='trace'))
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
                      yaxis=dict(categoryorder='trace'),
                      font=dict(size=13, color='#333'),
                      title_font=dict(size=16, color='#222'),
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                      margin=dict(l=20, r=20, t=60, b=20))
    return fig


def make_two_col_bar(df1, df2, col1_name, col2_name, cat_col, title, height=450):
    """Side-by-side comparison of two related dataframes (e.g., norms vs experience)."""
    # Sort so longest bars appear at top (Plotly renders bottom-to-top)
    sort_vals = (df1[['Baseline','Midline']].max(axis=1)*100 + df2[['Baseline','Midline']].max(axis=1)*100) / 2
    sort_order = sort_vals.sort_values(ascending=True).index
    df1 = df1.loc[sort_order]
    df2 = df2.loc[sort_order]
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
                      yaxis=dict(categoryorder='trace'),
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
    anchor_id = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    st.markdown(f'<div class="section-header" id="{anchor_id}"><h2>{heading}</h2>{badge}</div>',
                unsafe_allow_html=True)


def _quick_nav_pills(items):
    """Render quick navigation pills for in-tab section jumping."""
    pills = ''.join([
        f'<a href="#{re.sub(r"[^a-z0-9]+", "-", item.lower()).strip("-")}" '
        f'class="quick-nav-pill" style="text-decoration:none;color:inherit;">{item}</a>'
        for item in items
    ])
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
                        'Women by Location Type', height=300), use_container_width=True)
    with c2:
        st.plotly_chart(make_comparison_bar(w['hh_type'], 'Category',
                        'Household Type', height=300), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(make_comparison_bar(w['marital'], 'Category',
                        'Marital Status', height=380, orientation='h'), use_container_width=True)
    with c4:
        st.plotly_chart(make_comparison_bar(w['education'], 'Category',
                        'Education Level', height=380, orientation='h'), use_container_width=True)

    st.markdown("---")
    _section_header('', 'Economic Activities', 'Section A')
    c5, c6 = st.columns(2)
    with c5:
        st.plotly_chart(make_comparison_bar(w['main_econ'], 'Activity',
                        'Main HH Economic Activity', height=500, orientation='h'), use_container_width=True)
    with c6:
        st.plotly_chart(make_comparison_bar(w['sec_econ'], 'Activity',
                        'Secondary HH Economic Activities', height=500, orientation='h'), use_container_width=True)

    st.markdown("---")
    _section_header('', 'Access to Basic Services', 'Section A')
    c7, c8, c9 = st.columns(3)
    with c7:
        st.plotly_chart(make_comparison_bar(w['water'], 'Category',
                        'Access to Safe Drinking Water', height=300), use_container_width=True)
    with c8:
        st.plotly_chart(make_comparison_bar(w['toilet'], 'Category',
                        'Access to Improved Toilet', height=300), use_container_width=True)
    with c9:
        st.plotly_chart(make_comparison_bar(w['electricity'], 'Category',
                        'Access to Electricity', height=300), use_container_width=True)

    c10, c11 = st.columns(2)
    with c10:
        st.plotly_chart(make_comparison_bar(w['walls'], 'Category',
                        'Wall Material', height=350), use_container_width=True)
    with c11:
        st.plotly_chart(make_comparison_bar(w['floors'], 'Category',
                        'Floor Material', height=350), use_container_width=True)


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
                        use_container_width=True)
    with c2:
        st.plotly_chart(make_comparison_bar(w['shock_impact'], 'Extent',
                        'Perceived Impact on Wellbeing', height=400, orientation='h'),
                        use_container_width=True)

    _section_header('', 'Coping Strategies', 'Section B')
    st.plotly_chart(make_comparison_bar(w['coping'], 'Strategy',
                    'Coping Strategies Used', height=500, orientation='h'), use_container_width=True)

    st.markdown("---")
    _section_header('', 'Disaster Preparedness', 'Section C')
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(make_comparison_bar(w['prep_knowledge'], 'Response',
                        'Knowledge of Preparedness Plans', height=350), use_container_width=True)
    with c4:
        st.plotly_chart(make_comparison_bar(w['prep_participation'], 'Response',
                        'Participation in Plan Development', height=350), use_container_width=True)

    c5, c6 = st.columns(2)
    with c5:
        st.plotly_chart(make_comparison_bar(w['prep_know_action'], 'Response',
                        'Know What to Do in Disaster', height=300), use_container_width=True)
    with c6:
        st.plotly_chart(make_comparison_bar(w['early_warning'], 'Response',
                        'Access to Early Warning Info', height=300), use_container_width=True)

    c7, c8 = st.columns(2)
    with c7:
        st.plotly_chart(make_comparison_bar(w['weather_forecast'], 'Response',
                        'Access to Weather Forecasts', height=300), use_container_width=True)
    with c8:
        st.plotly_chart(make_comparison_bar(w['tidal_forecast'], 'Response',
                        'Access to Tidal Forecasts', height=300), use_container_width=True)

    # Awareness of plan actions
    _section_header('', 'Awareness of Preparedness Plan Actions', 'Section C')
    st.plotly_chart(make_comparison_bar(w['prep_awareness'], 'Extent',
                    'Awareness of Plan Actions (by Extent)', height=400, orientation='h'),
                    use_container_width=True)


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
                    'Assets Present in Household', height=600, orientation='h'), use_container_width=True)

    # Asset ownership breakdown
    _section_header('', 'Asset Ownership (Joint vs Sole)', 'Section D')
    ao = w['asset_ownership']
    fig_ao = go.Figure()
    fig_ao.add_trace(go.Bar(y=ao['Asset'], x=ao['Joint_BL'].apply(lambda x: x*100 if isinstance(x,(int,float)) and x<=1 else x),
                            name='Joint (BL)', orientation='h', marker_color=COLORS['baseline_light']))
    fig_ao.add_trace(go.Bar(y=ao['Asset'], x=ao['Joint_ML'].apply(lambda x: x*100 if isinstance(x,(int,float)) and x<=1 else x),
                            name='Joint (ML)', orientation='h', marker_color=COLORS['baseline']))
    fig_ao.add_trace(go.Bar(y=ao['Asset'], x=ao['Sole_BL'].apply(lambda x: x*100 if isinstance(x,(int,float)) and x<=1 else x),
                            name='Sole (BL)', orientation='h', marker_color=COLORS['midline_light']))
    fig_ao.add_trace(go.Bar(y=ao['Asset'], x=ao['Sole_ML'].apply(lambda x: x*100 if isinstance(x,(int,float)) and x<=1 else x),
                            name='Sole (ML)', orientation='h', marker_color=COLORS['midline']))
    fig_ao.update_layout(title='Asset Ownership: Joint vs Sole', barmode='group', height=550,
                         xaxis_title='%', legend=dict(orientation='h', yanchor='bottom', y=1.02),
                         font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'),
                         plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                         margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig_ao, use_container_width=True)

    # Ability to use/sell assets
    aus = w['asset_use_sell']
    aus_c1, aus_c2 = st.columns(2)
    with aus_c1:
        fig_use = go.Figure()
        fig_use.add_trace(go.Bar(y=aus['Asset'], x=aus['Use_BL'].apply(lambda x: x*100 if isinstance(x,(int,float)) and x<=1 else x),
                                 name='BL', orientation='h', marker_color=COLORS['baseline']))
        fig_use.add_trace(go.Bar(y=aus['Asset'], x=aus['Use_ML'].apply(lambda x: x*100 if isinstance(x,(int,float)) and x<=1 else x),
                                 name='ML', orientation='h', marker_color=COLORS['midline']))
        fig_use.update_layout(title='Ability to Use Assets', barmode='group', height=500,
                              xaxis_title='%', legend=dict(orientation='h', yanchor='bottom', y=1.02),
                              font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'),
                              plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')  
        st.plotly_chart(fig_use, use_container_width=True)
    with aus_c2:
        fig_sell = go.Figure()
        fig_sell.add_trace(go.Bar(y=aus['Asset'], x=aus['Sell_BL'].apply(lambda x: x*100 if isinstance(x,(int,float)) and x<=1 else x),
                                  name='BL', orientation='h', marker_color=COLORS['baseline']))
        fig_sell.add_trace(go.Bar(y=aus['Asset'], x=aus['Sell_ML'].apply(lambda x: x*100 if isinstance(x,(int,float)) and x<=1 else x),
                                  name='ML', orientation='h', marker_color=COLORS['midline']))
        fig_sell.update_layout(title='Ability to Sell Assets', barmode='group', height=500,
                               xaxis_title='%', legend=dict(orientation='h', yanchor='bottom', y=1.02),
                               font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'),
                               plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)') 
        st.plotly_chart(fig_sell, use_container_width=True)

    # Access to productive inputs
    _section_header('', 'Access to Productive Inputs', 'Section D')
    inp = w['inputs']
    inp_c1, inp_c2 = st.columns(2)
    with inp_c1:
        fig_inp_a = go.Figure()
        fig_inp_a.add_trace(go.Bar(y=inp['Input'], x=inp['Access_BL'].apply(lambda x: x*100 if isinstance(x,(int,float)) and x<=1 else x),
                                   name='BL', orientation='h', marker_color=COLORS['baseline']))
        fig_inp_a.add_trace(go.Bar(y=inp['Input'], x=inp['Access_ML'].apply(lambda x: x*100 if isinstance(x,(int,float)) and x<=1 else x),
                                   name='ML', orientation='h', marker_color=COLORS['midline']))
        fig_inp_a.update_layout(title='Access to Inputs', barmode='group', height=400,
                                xaxis_title='%', legend=dict(orientation='h', yanchor='bottom', y=1.02),
                                font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'),
                                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')  
        st.plotly_chart(fig_inp_a, use_container_width=True)
    with inp_c2:
        fig_inp_p = go.Figure()
        fig_inp_p.add_trace(go.Bar(y=inp['Input'], x=inp['PersonalUse_BL'].apply(lambda x: x*100 if isinstance(x,(int,float)) and x<=1 else x),
                                   name='BL', orientation='h', marker_color=COLORS['baseline']))
        fig_inp_p.add_trace(go.Bar(y=inp['Input'], x=inp['PersonalUse_ML'].apply(lambda x: x*100 if isinstance(x,(int,float)) and x<=1 else x),
                                   name='ML', orientation='h', marker_color=COLORS['midline']))
        fig_inp_p.update_layout(title='Personal Use of Inputs', barmode='group', height=400,
                                xaxis_title='%', legend=dict(orientation='h', yanchor='bottom', y=1.02),
                                font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'),
                                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')  
        st.plotly_chart(fig_inp_p, use_container_width=True)

    st.markdown("---")
    _section_header('', 'Land', 'Section D')
    c1, c2, c3 = st.columns(3)
    with c1:
        st.plotly_chart(make_comparison_bar(w['land_size'], 'Category',
                        'Agricultural Land Size', height=350), use_container_width=True)
    with c2:
        st.plotly_chart(make_comparison_bar(w['land_status'], 'Category',
                        'Land Tenure Status', height=350), use_container_width=True)
    with c3:
        st.plotly_chart(make_comparison_bar(w['land_use'], 'Category',
                        'Currently Using Land for Agriculture', height=300), use_container_width=True)

    st.markdown("---")
    _section_header('', 'Savings', 'Section E')
    c4, c5 = st.columns(2)
    with c4:
        st.plotly_chart(make_comparison_bar(w['personal_saving'], 'Response',
                        'Women Personally Saving', height=300), use_container_width=True)
    with c5:
        st.plotly_chart(make_comparison_bar(w['family_saving'], 'Response',
                        'Family Members Saving', height=300), use_container_width=True)

    c6, c7 = st.columns(2)
    with c6:
        st.plotly_chart(make_comparison_bar(w['saving_freq'], 'Frequency',
                        'Saving Frequency', height=350, orientation='h'), use_container_width=True)
    with c7:
        st.plotly_chart(make_comparison_bar(w['saving_amount'], 'Amount',
                        'Amount Saved per Period', height=350, orientation='h'), use_container_width=True)

    c8, c9 = st.columns(2)
    with c8:
        st.plotly_chart(make_comparison_bar(w['saving_mechanism'], 'Mechanism',
                        'Saving Mechanism', height=380, orientation='h'), use_container_width=True)
    with c9:
        st.plotly_chart(make_comparison_bar(w['saving_use'], 'Use',
                        'Intended Use of Savings', height=380, orientation='h'), use_container_width=True)

    # Savings balance distribution
    st.plotly_chart(make_comparison_bar(w['saving_balance'], 'Balance',
                    'Savings Balance Distribution', height=350, orientation='h'),
                    use_container_width=True)

    st.markdown('---')
    _section_header('', 'Loans', 'Section E')
    c10, c11 = st.columns(2)
    with c10:
        st.plotly_chart(make_comparison_bar(w['personal_loan'], 'Response',
                        'Women Personally Taking a Loan', height=300), use_container_width=True)
        pl = w['personal_loan_size']
        st.metric('Avg Personal Loan (BL \u2192 ML)',
                  f"KES {pl['Baseline'].values[0]:,.0f} \u2192 {pl['Midline'].values[0]:,.0f}")
    with c11:
        st.plotly_chart(make_comparison_bar(w['loan_source'], 'Source',
                        'Loan Sources', height=380, orientation='h'), use_container_width=True)

    # Family loan data
    fl_c1, fl_c2 = st.columns(2)
    with fl_c1:
        st.plotly_chart(make_comparison_bar(w['family_loan'], 'Response',
                        'Family Members Taking Loans', height=300), use_container_width=True)
    with fl_c2:
        fls = w['family_loan_size']
        st.metric('Avg Family Loan (BL \u2192 ML)',
                  f"KES {fls['Baseline'].values[0]:,.0f} \u2192 {fls['Midline'].values[0]:,.0f}")


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
                    'Roles: Should be Joint vs. Actually Joint', height=500), use_container_width=True)

    # Women-only norms vs actual practice
    rw_c1, rw_c2 = st.columns(2)
    with rw_c1:
        st.plotly_chart(make_comparison_bar(w['roles_should_women'], 'Role',
                        'Roles: Should be Done by Women Only (Norms)', height=500, orientation='h'),
                        use_container_width=True)
    with rw_c2:
        st.plotly_chart(make_comparison_bar(w['roles_does_self'], 'Role',
                        'Roles: Actually Done by Self/Spouse', height=500, orientation='h'),
                        use_container_width=True)

    st.markdown('---')
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
    st.plotly_chart(fig_time, use_container_width=True)

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
        st.plotly_chart(fig_uc, use_container_width=True)
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
        st.plotly_chart(fig_pw, use_container_width=True)

    # Community conservation time breakdown
    tc = w['time_conservation']
    fig_tc = go.Figure()
    fig_tc.add_trace(go.Bar(y=tc['Activity'], x=tc['Hours_BL'], name='Baseline',
                            orientation='h', marker_color=COLORS['baseline']))
    fig_tc.add_trace(go.Bar(y=tc['Activity'], x=tc['Hours_ML'], name='Midline',
                            orientation='h', marker_color=COLORS['midline']))
    fig_tc.update_layout(title='Community Conservation Work (Hours/Day)', barmode='group', height=300,
                         xaxis_title='Hours', legend=dict(orientation='h', yanchor='bottom', y=1.02),
                         font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'),
                         plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_tc, use_container_width=True)

    # Total hours summary metrics
    tt_c1, tt_c2, tt_c3 = st.columns(3)
    tut = w['time_unpaid_total']
    tpt = w['time_productive_total']
    tct = w['time_conservation_total']
    with tt_c1:
        st.metric('Unpaid Care (BL / ML)',
                  f"{tut['Baseline'].values[0]:.1f}h / {tut['Midline'].values[0]:.1f}h")
    with tt_c2:
        st.metric('Productive (BL / ML)',
                  f"{tpt['Baseline'].values[0]:.1f}h / {tpt['Midline'].values[0]:.1f}h")
    with tt_c3:
        st.metric('Conservation (BL / ML)',
                  f"{tct['Baseline'].values[0]:.1f}h / {tct['Midline'].values[0]:.1f}h")

    st.markdown('---')
    _section_header('', 'Decision-Making', 'Section H')
    st.plotly_chart(make_two_col_bar(w['decision_should_joint'], w['decision_does_joint'],
                    'Should be Joint', 'Actually Joint', 'Decision',
                    'Decision-Making: Norms vs. Experience (Joint %)', height=550), use_container_width=True)

    # Women-only decision norms vs actual
    dw_c1, dw_c2 = st.columns(2)
    with dw_c1:
        st.plotly_chart(make_comparison_bar(w['decision_should_women'], 'Decision',
                        'Should be Decided by Women Only', height=550, orientation='h'),
                        use_container_width=True)
    with dw_c2:
        st.plotly_chart(make_comparison_bar(w['decision_does_self'], 'Decision',
                        'Actually Decided by Self/Spouse', height=550, orientation='h'),
                        use_container_width=True)

    _section_header('', "Influence on HH Decisions ('To a Large Extent')", 'Section H')
    st.plotly_chart(make_comparison_bar(w['decision_influence'], 'Decision',
                    'Women Who Can Influence Decisions to a Large Extent',
                    height=500, orientation='h'), use_container_width=True)


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
                        'Heard of Climate Change', height=300), use_container_width=True)
    with c2:
        st.plotly_chart(make_comparison_bar(w['cc_define'], 'Response',
                        'Ability to Define Climate Change', height=350), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(make_comparison_bar(w['cc_env_effects'], 'Effect',
                        'Perceived Environmental Effects of CC', height=500, orientation='h'),
                        use_container_width=True)
    with c4:
        st.plotly_chart(make_comparison_bar(w['cc_livelihood_effects'], 'Effect',
                        'Perceived Livelihood Effects of CC', height=500, orientation='h'),
                        use_container_width=True)

    st.markdown("---")
    _section_header('', 'Nature-based Solutions', 'Section H')
    c5, c6 = st.columns(2)
    with c5:
        st.plotly_chart(make_comparison_bar(w['nbs_heard'], 'Response',
                        'Heard of NbS', height=300), use_container_width=True)
    with c6:
        st.plotly_chart(make_comparison_bar(w['nbs_define'], 'Response',
                        'Ability to Define NbS', height=350), use_container_width=True)

    c7, c8 = st.columns(2)
    with c7:
        st.plotly_chart(make_comparison_bar(w['nbs_examples'], 'Example',
                        'NbS Examples Women Can Cite', height=450, orientation='h'), use_container_width=True)
    with c8:
        st.plotly_chart(make_comparison_bar(w['nbs_benefits'], 'Benefit',
                        'Perceived Benefits of NbS', height=500, orientation='h'), use_container_width=True)

    st.markdown("---")
    # NbS Modules
    for module, prefix, icon in [('Mangrove Restoration', 'mangrove', ''),
                                  ('Seaweed Farming', 'seaweed', ''),
                                  ('Forest Management', 'forest', '')]:
        _section_header(icon, module, 'NbS Module')
        ca, cb = st.columns(2)
        with ca:
            st.plotly_chart(make_comparison_bar(w[f'{prefix}_heard'], 'Response',
                            f'Awareness of {module}', height=300), use_container_width=True)
            st.plotly_chart(make_comparison_bar(w[f'{prefix}_current'], 'Response',
                            f'Currently Involved', height=280), use_container_width=True)
        with cb:
            st.plotly_chart(make_comparison_bar(w[f'{prefix}_ever'], 'Response',
                            f'Ever Participated', height=300), use_container_width=True)
            st.plotly_chart(make_comparison_bar(w[f'{prefix}_modality'], 'Modality',
                            f'Participation Modality', height=300), use_container_width=True)

        cc, cd = st.columns(2)
        with cc:
            st.plotly_chart(make_comparison_bar(w[f'{prefix}_training'], 'Response',
                            f'Training Received', height=300), use_container_width=True)
        with cd:
            st.plotly_chart(make_comparison_bar(w[f'{prefix}_assets'], 'Response',
                            f'Assets/Inputs Received', height=300), use_container_width=True)

        if f'{prefix}_interest' in w:
            st.plotly_chart(make_comparison_bar(w[f'{prefix}_interest'], 'Response',
                            f'Interest in Participating', height=280), use_container_width=True)
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
    st.plotly_chart(fig_radar, use_container_width=True)

    # Detailed bars
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(make_comparison_bar(ls_a, 'Statement',
                        'Life Skills — Agree/SA %', height=550, orientation='h'), use_container_width=True)
    with c2:
        st.plotly_chart(make_comparison_bar(ls_s, 'Statement',
                        'Life Skills — Strongly Agree %', height=550, orientation='h'), use_container_width=True)

    st.markdown("---")
    _section_header('', 'Communication & Conflict Resolution', 'Section I')
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(make_comparison_bar(w['communication_agree'], 'Statement',
                        'Communication — Agree/SA', height=350, orientation='h'), use_container_width=True)
    with c4:
        st.plotly_chart(make_comparison_bar(w['conflict_agree'], 'Statement',
                        'Conflict Resolution — Agree/SA', height=350, orientation='h'), use_container_width=True)

    c3b, c4b = st.columns(2)
    with c3b:
        st.plotly_chart(make_comparison_bar(w['communication_strong'], 'Statement',
                        'Communication — Strongly Agree Only', height=350, orientation='h'),
                        use_container_width=True)
    with c4b:
        st.plotly_chart(make_comparison_bar(w['conflict_strong'], 'Statement',
                        'Conflict Resolution — Strongly Agree Only', height=350, orientation='h'),
                        use_container_width=True)

    st.markdown("---")
    _section_header('', 'Social Norms', 'Section J')
    c5, c6 = st.columns(2)
    with c5:
        st.plotly_chart(make_comparison_bar(w['socialnorms_agree'], 'Norm',
                        'Social Norms — Agree/SA %', height=500, orientation='h'), use_container_width=True)
    with c6:
        st.plotly_chart(make_comparison_bar(w['socialnorms_strong'], 'Norm',
                        'Social Norms — Strongly Agree %', height=500, orientation='h'), use_container_width=True)


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
            st.plotly_chart(fig, use_container_width=True)
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
            st.plotly_chart(fig_r, use_container_width=True)

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

        # Summary statistics metric cards
        ys = data['years_stats']
        fss = data['forest_size_stats']
        sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
        with sc1: st.metric('Avg Years (BL)', f"{ys.loc[ys['Stat']=='Average','Baseline'].values[0]:.1f}")
        with sc2: st.metric('Avg Years (ML)', f"{ys.loc[ys['Stat']=='Average','Midline'].values[0]:.1f}")
        with sc3: st.metric('Max Years (ML)', f"{ys.loc[ys['Stat']=='Maximum','Midline'].values[0]:.0f}")
        with sc4: st.metric('Avg Forest ha (BL)', f"{fss.loc[fss['Stat']=='Average','Baseline'].values[0]:.1f}")
        with sc5: st.metric('Avg Forest ha (ML)', f"{fss.loc[fss['Stat']=='Average','Midline'].values[0]:.1f}")
        with sc6: st.metric('Max Forest ha (ML)', f"{fss.loc[fss['Stat']=='Maximum','Midline'].values[0]:.0f}")
        st.markdown('---')

        c1,c2,c3 = st.columns(3)
        with c1:
            st.plotly_chart(make_comparison_bar(data['avg_membership'],'Category','Avg Members',
                            y_label='Members', multiply=False, height=350), use_container_width=True)
        with c2:
            st.plotly_chart(make_comparison_bar(data['max_membership'],'Category','Max Members',
                            y_label='Members', multiply=False, height=350), use_container_width=True)
        with c3:
            st.plotly_chart(make_comparison_bar(data['min_membership'],'Category','Min Members',
                            y_label='Members', multiply=False, height=350), use_container_width=True)
        st.markdown("---")
        c4,c5,c6 = st.columns(3)
        with c4:
            fn = make_delta_bar if show_change else make_comparison_bar
            kw = {'title':'Change in Years Dist'} if show_change else {'title':'Years of Operation', 'height':400}
            st.plotly_chart(fn(data['years_dist'],'Category',**kw), use_container_width=True)
        with c5:
            fn = make_delta_bar if show_change else make_comparison_bar
            kw = {'title':'Change in Tenure'} if show_change else {'title':'Land Tenure Type', 'height':400}
            st.plotly_chart(fn(data['tenure'],'Category',**kw), use_container_width=True)
        with c6:
            fn = make_delta_bar if show_change else make_comparison_bar
            kw = {'title':'Change in Forest Size'} if show_change else {'title':'Forest Size (ha)', 'height':400}
            st.plotly_chart(fn(data['forest_size_dist'],'Category',**kw), use_container_width=True)

    # ---- TAB 3: GOVERNANCE & GENDER ----
    with tab3:
        st.markdown("""<div class="section-narrative">
        <strong>Governance & Gender:</strong> Board clarity, guidelines, meetings, women's leadership,
        management practices, gender equality discussions and actions.
        </div>""", unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1: st.plotly_chart(make_comparison_bar(data['goals_defined'],'Category','Defined Goals', height=350), use_container_width=True)
        with c2: st.plotly_chart(make_comparison_bar(data['goals_stated'],'Goal','Stated Goals', height=350, orientation='h'), use_container_width=True)
        c3,c4 = st.columns(2)
        with c3: st.plotly_chart(make_comparison_bar(data['rights'],'Right','Right Entitlements', height=400, orientation='h'), use_container_width=True)
        with c4: st.plotly_chart(make_comparison_bar(data['responsibilities'],'Responsibility','Govt Responsibilities', height=400, orientation='h'), use_container_width=True)
        st.markdown("---")
        c5,c6 = st.columns(2)
        with c5: st.plotly_chart(make_comparison_bar(data['board_roles'],'Category','Board Role Clarity', height=380, orientation='h'), use_container_width=True)
        with c6: st.plotly_chart(make_comparison_bar(data['guidelines'],'Category','Guidelines Status', height=380, orientation='h'), use_container_width=True)
        c7,c8 = st.columns(2)
        with c7: st.plotly_chart(make_comparison_bar(data['meetings'],'Category','Meeting Frequency', height=350, orientation='h'), use_container_width=True)
        with c8: st.plotly_chart(make_comparison_bar(data['women_leadership'],'Category',"Women's Leadership", height=350, orientation='h'), use_container_width=True)

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
        st.plotly_chart(fig_mp, use_container_width=True)
        st.markdown("---")
        c9,c10 = st.columns(2)
        with c9:
            st.plotly_chart(make_comparison_bar(data['ge_discussion'],'Category','GE Discussion', height=350), use_container_width=True)
            st.plotly_chart(make_comparison_bar(data['ge_actions'],'Category','GE Actions Agreed', height=350), use_container_width=True)
        with c10:
            st.plotly_chart(make_comparison_bar(data['ge_topics'],'Topic','GE Topics', height=350, orientation='h'), use_container_width=True)
            st.plotly_chart(make_comparison_bar(data['ge_completion'],'Category','GE Action Completion', height=350), use_container_width=True)

    # ---- TAB 4: TRAINING & ASSETS ----
    with tab4:
        st.markdown("""<div class="section-narrative">
        <strong>Training & Assets:</strong> Training coverage, topics, and assets/inputs received.
        </div>""", unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1: st.plotly_chart(make_comparison_bar(data['training_coverage'],'Category','Training Coverage', height=400), use_container_width=True)
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
            st.plotly_chart(fig_tc, use_container_width=True)

        if show_change:
            st.plotly_chart(make_delta_bar(data['training_topics'],'Topic','Training Topics Change (pp)', height=500), use_container_width=True)
        else:
            st.plotly_chart(make_comparison_bar(data['training_topics'],'Topic','Training Topics', height=600, orientation='h'), use_container_width=True)
        st.markdown("---")
        c3,c4 = st.columns(2)
        with c3: st.plotly_chart(make_comparison_bar(data['assets_received'],'Category','Assets Received', height=350), use_container_width=True)
        with c4: st.plotly_chart(make_comparison_bar(data['asset_types'],'Asset','Asset Types', height=400, orientation='h'), use_container_width=True)

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
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("---")
        tp2 = st.radio("Timepoint", ["Baseline","Midline"], horizontal=True, key="fch_tp")
        fch = data['forest_change']
        cols2 = [f'{tp2}_Decrease',f'{tp2}_NoChange',f'{tp2}_Increase']
        fig2 = make_stacked_bar(fch,'Characteristic', cols2, [COLORS['danger'],COLORS['no_change'],COLORS['good']],
                                f'Perceived Changes — {tp2}', height=400)
        for i,l in enumerate(['Decrease','No Change','Increase']): fig2.data[i].name = l
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("---")
        c1,c2 = st.columns(2)
        with c1:
            fig_t = make_stacked_bar(data['threats'],'Threat', ['Baseline_Low','Baseline_Medium','Baseline_High'],
                                     [COLORS['good'],COLORS['medium'],COLORS['danger']], 'Threats — Baseline', height=450, orientation='h')
            for i,l in enumerate(['Low','Medium','High']): fig_t.data[i].name = l
            st.plotly_chart(fig_t, use_container_width=True)
        with c2:
            fig_t2 = make_stacked_bar(data['threats'],'Threat', ['Midline_Low','Midline_Medium','Midline_High'],
                                      [COLORS['good'],COLORS['medium'],COLORS['danger']], 'Threats — Midline', height=450, orientation='h')
            for i,l in enumerate(['Low','Medium','High']): fig_t2.data[i].name = l
            st.plotly_chart(fig_t2, use_container_width=True)

        # Threat change trends
        st.markdown('---')
        _section_header('', 'Threat Change Trends', 'Section E')
        tc1, tc2 = st.columns(2)
        with tc1:
            fig_tc = make_stacked_bar(data['threat_changes'], 'Threat',
                                      ['Baseline_Decrease','Baseline_NoChange','Baseline_Increase'],
                                      [COLORS['good'],'#9E9E9E',COLORS['danger']],
                                      'Threat Changes — Baseline', height=450, orientation='h')
            for i,l in enumerate(['Decrease','No Change','Increase']): fig_tc.data[i].name = l
            st.plotly_chart(fig_tc, use_container_width=True)
        with tc2:
            fig_tc2 = make_stacked_bar(data['threat_changes'], 'Threat',
                                       ['Midline_Decrease','Midline_NoChange','Midline_Increase'],
                                       [COLORS['good'],'#9E9E9E',COLORS['danger']],
                                       'Threat Changes — Midline', height=450, orientation='h')
            for i,l in enumerate(['Decrease','No Change','Increase']): fig_tc2.data[i].name = l
            st.plotly_chart(fig_tc2, use_container_width=True)

        # Harvest amounts
        st.markdown('---')
        _section_header('', 'Harvest Amounts by Product', 'Section E')
        hc1, hc2 = st.columns(2)
        with hc1:
            fig_ha = make_stacked_bar(data['harvest_amount'], 'Product',
                                      ['Baseline_None','Baseline_Medium','Baseline_Substantial'],
                                      ['#9E9E9E',COLORS['medium'],COLORS['good']],
                                      'Harvest Amount — Baseline', height=450, orientation='h')
            for i,l in enumerate(['None','Medium','Substantial']): fig_ha.data[i].name = l
            st.plotly_chart(fig_ha, use_container_width=True)
        with hc2:
            fig_ha2 = make_stacked_bar(data['harvest_amount'], 'Product',
                                       ['Midline_None','Midline_Medium','Midline_Substantial'],
                                       ['#9E9E9E',COLORS['medium'],COLORS['good']],
                                       'Harvest Amount — Midline', height=450, orientation='h')
            for i,l in enumerate(['None','Medium','Substantial']): fig_ha2.data[i].name = l
            st.plotly_chart(fig_ha2, use_container_width=True)

        # Harvest change trends
        _section_header('', 'Harvest Change Trends', 'Section E')
        ht1, ht2 = st.columns(2)
        with ht1:
            fig_hc = make_stacked_bar(data['harvest_changes'], 'Product',
                                      ['Baseline_Decrease','Baseline_NoChange','Baseline_Increase'],
                                      [COLORS['danger'],'#9E9E9E',COLORS['good']],
                                      'Harvest Changes — Baseline', height=450, orientation='h')
            for i,l in enumerate(['Decrease','No Change','Increase']): fig_hc.data[i].name = l
            st.plotly_chart(fig_hc, use_container_width=True)
        with ht2:
            fig_hc2 = make_stacked_bar(data['harvest_changes'], 'Product',
                                       ['Midline_Decrease','Midline_NoChange','Midline_Increase'],
                                       [COLORS['danger'],'#9E9E9E',COLORS['good']],
                                       'Harvest Changes — Midline', height=450, orientation='h')
            for i,l in enumerate(['Decrease','No Change','Increase']): fig_hc2.data[i].name = l
            st.plotly_chart(fig_hc2, use_container_width=True)

    # ---- TAB 6: INCOME & AGROFORESTRY ----
    with tab6:
        st.markdown("""<div class="section-narrative">
        <strong>Income & Agroforestry:</strong> Income generation, sources, uses, agroforestry practices, support, and challenges.
        </div>""", unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        with c1: st.plotly_chart(make_comparison_bar(data['income_gen'],'Category','Income Generation', height=350), use_container_width=True)
        with c2: st.plotly_chart(make_comparison_bar(data['income_sources'],'Source','Income Sources', height=400, orientation='h'), use_container_width=True)
        with c3: st.plotly_chart(make_comparison_bar(data['income_use'],'Use','Income Use', height=400, orientation='h'), use_container_width=True)
        st.markdown("---")
        c4,c5 = st.columns(2)
        with c4: st.plotly_chart(make_comparison_bar(data['agroforestry'],'Category','Agroforestry Practice', height=350), use_container_width=True)
        with c5: st.plotly_chart(make_comparison_bar(data['af_types'],'Practice','AF Types', height=350, orientation='h'), use_container_width=True)
        c6,c7 = st.columns(2)
        with c6: st.plotly_chart(make_comparison_bar(data['af_objectives'],'Objective','AF Objectives', height=400, orientation='h'), use_container_width=True)
        with c7: st.plotly_chart(make_comparison_bar(data['af_training'],'Category','AF Training', height=350), use_container_width=True)
        st.markdown("---")
        c8,c9 = st.columns(2)
        with c8:
            fn = make_delta_bar if show_change else make_comparison_bar
            kw = {'title':'Change in AF Support (pp)'} if show_change else {'title':'AF Support Types', 'height':380, 'orientation':'h'}
            st.plotly_chart(fn(data['af_support'],'Support',**kw), use_container_width=True)
        with c9:
            fn = make_delta_bar if show_change else make_comparison_bar
            kw = {'title':'Change in AF Challenges (pp)'} if show_change else {'title':'AF Challenges', 'height':380, 'orientation':'h'}
            st.plotly_chart(fn(data['af_challenges'],'Challenge',**kw), use_container_width=True)
        c10,c11 = st.columns(2)
        with c10: st.plotly_chart(make_comparison_bar(data['af_reinvest'],'Category','AF Reinvestment', height=380, orientation='h'), use_container_width=True)
        with c11: st.plotly_chart(make_comparison_bar(data['af_potential'],'Category','Livelihood Potential', height=350), use_container_width=True)


# ============================================================================
# MEN SURVEY TAB RENDERERS
# ============================================================================

def render_men_tab1(m):
    """Tab 1: Household Characteristics."""
    st.markdown("""<div class="section-narrative">
    <strong>Household Profile:</strong> Demographics of surveyed men — location type (Marine vs
    Terrestrial), education levels, and main household economic activities such as agriculture,
    fishing, and small business.
    </div>""", unsafe_allow_html=True)

    _quick_nav_pills(['Demographics', 'Economic Activities'])

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(make_comparison_bar(m['location'], 'Category',
                        'Men by Location Type', height=300), use_container_width=True)
    with c2:
        st.plotly_chart(make_comparison_bar(m['education'], 'Category',
                        'Education Level', height=350), use_container_width=True)

    st.markdown("---")
    _section_header('', 'Economic Activities', 'Section A')
    st.plotly_chart(make_comparison_bar(m['main_econ'], 'Activity',
                    'Main HH Economic Activity', height=500, orientation='h'), use_container_width=True)


def render_men_tab2(m):
    """Tab 2: Climate Change & NbS Knowledge."""
    st.markdown("""<div class="section-narrative">
    <strong>Climate & NbS Awareness:</strong> Men's knowledge of climate change, ability to define it,
    perceived environmental and livelihood effects, awareness of Nature-based Solutions (NbS),
    examples cited, and perceived benefits.
    </div>""", unsafe_allow_html=True)

    _quick_nav_pills(['Climate Awareness', 'CC Effects', 'NbS Knowledge', 'NbS Benefits'])

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(make_comparison_bar(m['cc_heard'], 'Response',
                        'Heard of Climate Change', height=300), use_container_width=True)
    with c2:
        st.plotly_chart(make_comparison_bar(m['cc_define'], 'Response',
                        'Ability to Define Climate Change', height=350), use_container_width=True)

    _section_header('', 'CC Effects', 'Section B')
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(make_comparison_bar(m['cc_env_effects'], 'Effect',
                        'Perceived Environmental Effects of CC', height=500, orientation='h'),
                        use_container_width=True)
    with c4:
        st.plotly_chart(make_comparison_bar(m['cc_livelihood_effects'], 'Effect',
                        'Perceived Livelihood Effects of CC', height=500, orientation='h'),
                        use_container_width=True)

    st.markdown("---")
    _section_header('', 'NbS Knowledge', 'Section B')
    c5, c6 = st.columns(2)
    with c5:
        st.plotly_chart(make_comparison_bar(m['nbs_heard'], 'Response',
                        'Heard of NbS', height=300), use_container_width=True)
    with c6:
        st.plotly_chart(make_comparison_bar(m['nbs_define'], 'Response',
                        'Ability to Define NbS', height=350), use_container_width=True)

    c7, c8 = st.columns(2)
    with c7:
        st.plotly_chart(make_comparison_bar(m['nbs_examples'], 'Example',
                        'NbS Examples Men Can Cite', height=450, orientation='h'), use_container_width=True)
    with c8:
        st.plotly_chart(make_comparison_bar(m['nbs_benefits'], 'Benefit',
                        'Perceived Benefits of NbS', height=500, orientation='h'), use_container_width=True)


def render_men_tab3(m):
    """Tab 3: Support for Women in NbS Participation."""
    st.markdown("""<div class="section-narrative">
    <strong>Support for Women in NbS:</strong> Men's awareness of and support for female household
    members' participation in mangrove restoration, seaweed farming, and forest management.
    Includes types of support provided such as encouragement, household chore support, and
    material assistance.
    </div>""", unsafe_allow_html=True)

    _quick_nav_pills(['Mangrove Restoration', 'Seaweed Farming', 'Forest Management'])

    for module, prefix, icon in [('Mangrove Restoration', 'mangrove', ''),
                                  ('Seaweed Farming', 'seaweed', ''),
                                  ('Forest Management', 'forest', '')]:
        _section_header(icon, module, 'NbS Module')
        ca, cb = st.columns(2)
        with ca:
            st.plotly_chart(make_comparison_bar(m[f'{prefix}_heard'], 'Response',
                            f'Awareness of {module}', height=300), use_container_width=True)
            st.plotly_chart(make_comparison_bar(m[f'{prefix}_current'], 'Response',
                            f'Female HH Currently Involved', height=280), use_container_width=True)
        with cb:
            st.plotly_chart(make_comparison_bar(m[f'{prefix}_ever'], 'Response',
                            f'Female HH Ever Participated', height=300), use_container_width=True)
            st.plotly_chart(make_comparison_bar(m[f'{prefix}_support'], 'Response',
                            f'Men Supporting Female HH Members', height=300), use_container_width=True)

        _section_header('', f'Type of Support — {module}', 'Support')
        st.plotly_chart(make_comparison_bar(m[f'{prefix}_support_type'], 'Type',
                        f'Support Type for {module}', height=400, orientation='h'),
                        use_container_width=True)
        st.markdown("---")


def render_men_tab4(m):
    """Tab 4: Roles, Responsibilities & Time Use."""
    st.markdown("""<div class="section-narrative">
    <strong>Roles & Time Use:</strong> Gender norms around household roles as reported by men —
    who SHOULD do tasks vs. who DOES them (joint, men only, women only). Time use patterns
    across unpaid care, productive work, community conservation, personal development, and leisure.
    </div>""", unsafe_allow_html=True)

    _quick_nav_pills(['Roles: Norms vs Practice', 'Gendered Roles', 'Time Use'])

    _section_header('', 'Roles & Responsibilities: Norms vs Practice', 'Section C')
    st.plotly_chart(make_two_col_bar(m['roles_should_joint'], m['roles_does_joint'],
                    'Should be Joint', 'Actually Joint', 'Role',
                    'Roles: Should be Joint vs. Actually Joint (Men Reporting)', height=500),
                    use_container_width=True)

    _section_header('', 'Gendered Roles', 'Section C')
    rw_c1, rw_c2 = st.columns(2)
    with rw_c1:
        st.plotly_chart(make_comparison_bar(m['roles_should_women'], 'Role',
                        'Should be Done by Women Only', height=500, orientation='h'),
                        use_container_width=True)
    with rw_c2:
        st.plotly_chart(make_comparison_bar(m['roles_should_men'], 'Role',
                        'Should be Done by Men Only', height=500, orientation='h'),
                        use_container_width=True)

    rd_c1, rd_c2 = st.columns(2)
    with rd_c1:
        st.plotly_chart(make_comparison_bar(m['roles_does_men'], 'Role',
                        'Actually Done by Myself (Men)', height=500, orientation='h'),
                        use_container_width=True)
    with rd_c2:
        st.plotly_chart(make_comparison_bar(m['roles_does_women'], 'Role',
                        'Actually Done by My Spouse (Women)', height=500, orientation='h'),
                        use_container_width=True)

    st.markdown('---')
    _section_header('', 'Time Use (Average Hours per Day)', 'Section C')
    ts = m['time_summary']
    fig_time = go.Figure()
    fig_time.add_trace(go.Bar(x=ts['Category'], y=ts['Baseline'], name='Baseline',
                              marker_color=COLORS['baseline'],
                              text=ts['Baseline'].apply(lambda x: f"{x:.1f}h"), textposition='auto'))
    fig_time.add_trace(go.Bar(x=ts['Category'], y=ts['Midline'], name='Midline',
                              marker_color=COLORS['midline'],
                              text=ts['Midline'].apply(lambda x: f"{x:.1f}h"), textposition='auto'))
    fig_time.update_layout(title="Average Hours per Day by Category (Men)",
                           barmode='group', height=450, yaxis_title='Hours',
                           legend=dict(orientation='h', yanchor='bottom', y=1.02),
                           font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'),
                           plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_time, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        tu = m['time_unpaid']
        fig_uc = go.Figure()
        fig_uc.add_trace(go.Bar(y=tu['Activity'], x=tu['Baseline'], name='Baseline',
                                orientation='h', marker_color=COLORS['baseline']))
        fig_uc.add_trace(go.Bar(y=tu['Activity'], x=tu['Midline'], name='Midline',
                                orientation='h', marker_color=COLORS['midline']))
        fig_uc.update_layout(title='Unpaid Care Work (Hours/Day)', barmode='group', height=350,
                             xaxis_title='Hours', legend=dict(orientation='h', yanchor='bottom', y=1.02),
                             font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'),
                             plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_uc, use_container_width=True)
    with c2:
        tp = m['time_productive']
        fig_pw = go.Figure()
        fig_pw.add_trace(go.Bar(y=tp['Activity'], x=tp['Baseline'], name='Baseline',
                                orientation='h', marker_color=COLORS['baseline']))
        fig_pw.add_trace(go.Bar(y=tp['Activity'], x=tp['Midline'], name='Midline',
                                orientation='h', marker_color=COLORS['midline']))
        fig_pw.update_layout(title='Productive Work (Hours/Day)', barmode='group', height=350,
                             xaxis_title='Hours', legend=dict(orientation='h', yanchor='bottom', y=1.02),
                             font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'),
                             plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pw, use_container_width=True)

    tc = m['time_conservation']
    fig_tc = go.Figure()
    fig_tc.add_trace(go.Bar(y=tc['Activity'], x=tc['Baseline'], name='Baseline',
                            orientation='h', marker_color=COLORS['baseline']))
    fig_tc.add_trace(go.Bar(y=tc['Activity'], x=tc['Midline'], name='Midline',
                            orientation='h', marker_color=COLORS['midline']))
    fig_tc.update_layout(title='Community Conservation Work (Hours/Day)', barmode='group', height=300,
                         xaxis_title='Hours', legend=dict(orientation='h', yanchor='bottom', y=1.02),
                         font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'),
                         plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_tc, use_container_width=True)

    # Total hours summary metrics
    tt_c1, tt_c2, tt_c3 = st.columns(3)
    tut = m['time_unpaid_total']
    tpt = m['time_productive_total']
    tct = m['time_conservation_total']
    with tt_c1:
        st.metric('Unpaid Care (BL / ML)',
                  f"{tut['Baseline'].values[0]:.1f}h / {tut['Midline'].values[0]:.1f}h")
    with tt_c2:
        st.metric('Productive (BL / ML)',
                  f"{tpt['Baseline'].values[0]:.1f}h / {tpt['Midline'].values[0]:.1f}h")
    with tt_c3:
        st.metric('Conservation (BL / ML)',
                  f"{tct['Baseline'].values[0]:.1f}h / {tct['Midline'].values[0]:.1f}h")


def render_men_tab5(m):
    """Tab 5: Decision-Making."""
    st.markdown("""<div class="section-narrative">
    <strong>Decision-Making:</strong> Men's perspectives on who SHOULD and who DOES make key
    household decisions — joint, men only, or women only. Covers decisions on business, finances,
    education, household purchases, women's mobility and conservation work.
    </div>""", unsafe_allow_html=True)

    _quick_nav_pills(['Norms vs Experience', 'Gendered Decisions'])

    _section_header('', 'Decision-Making: Norms vs Experience', 'Section D')
    st.plotly_chart(make_two_col_bar(m['decision_should_joint'], m['decision_does_joint'],
                    'Should be Joint', 'Actually Joint', 'Decision',
                    'Decision-Making: Norms vs. Experience (Joint %)', height=550),
                    use_container_width=True)

    _section_header('', 'Gendered Decisions', 'Section D')
    dw_c1, dw_c2 = st.columns(2)
    with dw_c1:
        st.plotly_chart(make_comparison_bar(m['decision_should_women'], 'Decision',
                        'Should be Decided by Women Only', height=550, orientation='h'),
                        use_container_width=True)
    with dw_c2:
        st.plotly_chart(make_comparison_bar(m['decision_should_men'], 'Decision',
                        'Should be Decided by Men Only', height=550, orientation='h'),
                        use_container_width=True)

    st.markdown("---")
    _section_header('', 'Actual Decision-Making Practice', 'Section D')
    dm_c1, dm_c2 = st.columns(2)
    with dm_c1:
        st.plotly_chart(make_comparison_bar(m['decision_does_men'], 'Decision',
                        'Actually Decided by Myself (Men)', height=550, orientation='h'),
                        use_container_width=True)
    with dm_c2:
        st.plotly_chart(make_comparison_bar(m['decision_does_women'], 'Decision',
                        'Actually Decided by My Spouse (Women)', height=550, orientation='h'),
                        use_container_width=True)


def render_men_tab6(m):
    """Tab 6: Social Norms."""
    st.markdown("""<div class="section-narrative">
    <strong>Social Norms:</strong> Men's agreement with social norms statements about gender roles,
    economic control, domestic work, ecosystem participation, emotional expression, and attitudes
    toward women's rights and independence. Includes both Agree/StronglyAgree and StronglyAgree
    only proportions.
    </div>""", unsafe_allow_html=True)

    _quick_nav_pills(['Agree/Strongly Agree', 'Strongly Agree Only', 'Change'])

    _section_header('', 'Social Norms — Agree or Strongly Agree', 'Section E')
    st.plotly_chart(make_comparison_bar(m['socialnorms_agree'], 'Norm',
                    'Men Agreeing/Strongly Agreeing with Social Norms',
                    height=600, orientation='h'), use_container_width=True)

    st.markdown("---")
    _section_header('', 'Social Norms — Strongly Agree Only', 'Section E')
    st.plotly_chart(make_comparison_bar(m['socialnorms_strong'], 'Norm',
                    'Men Strongly Agreeing with Social Norms',
                    height=600, orientation='h'), use_container_width=True)

    st.markdown("---")
    _section_header('', 'Change in Social Norms (pp)', 'Section E')
    st.plotly_chart(make_delta_bar(m['socialnorms_agree'], 'Norm',
                    'Change in Agreement (Baseline to Midline)',
                    height=550), use_container_width=True)


# ============================================================================
# GJJ KAP WOMEN — CHART HELPER & TAB RENDERERS
# ============================================================================

def _gjj_bar(df, cat_col, title, y_label="Percentage (%)", multiply=True,
             height=450, orientation='v'):
    """Baseline vs Endline grouped bar chart (uses Endline column instead of Midline)."""
    cb = COLORS["baseline"]
    cm = COLORS["midline"]
    plot_df = df.copy()
    if multiply:
        for c in ['Baseline', 'Endline']:
            plot_df[c] = pd.to_numeric(plot_df[c], errors='coerce').fillna(0) * 100
    if orientation == 'h':
        plot_df['_sort'] = plot_df[['Baseline', 'Endline']].max(axis=1)
        plot_df = plot_df.sort_values('_sort', ascending=True).drop(columns='_sort')
        fig = go.Figure()
        fig.add_trace(go.Bar(y=plot_df[cat_col], x=plot_df['Baseline'], name='Baseline',
                             orientation='h', marker_color=cb,
                             text=plot_df['Baseline'].apply(lambda x: f"{x:.1f}%"), textposition='auto'))
        fig.add_trace(go.Bar(y=plot_df[cat_col], x=plot_df['Endline'], name='Endline',
                             orientation='h', marker_color=cm,
                             text=plot_df['Endline'].apply(lambda x: f"{x:.1f}%"), textposition='auto'))
        fig.update_layout(title=title, barmode='group', height=height,
                          xaxis_title=y_label, legend=dict(orientation='h', yanchor='bottom', y=1.02),
                          yaxis=dict(categoryorder='trace'))
    else:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=plot_df[cat_col], y=plot_df['Baseline'], name='Baseline',
                             marker_color=cb,
                             text=plot_df['Baseline'].apply(lambda x: f"{x:.1f}%"), textposition='auto'))
        fig.add_trace(go.Bar(x=plot_df[cat_col], y=plot_df['Endline'], name='Endline',
                             marker_color=cm,
                             text=plot_df['Endline'].apply(lambda x: f"{x:.1f}%"), textposition='auto'))
        fig.update_layout(title=title, barmode='group', height=height, yaxis_title=y_label,
                          legend=dict(orientation='h', yanchor='bottom', y=1.02))
    fig.update_layout(
        font=dict(size=13, color='#333'),
        title_font=dict(size=16, color='#222'),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return fig


def _gjj_delta_bar(df, cat_col, title, multiply=True, height=400):
    """Baseline to Endline change bar (horizontal, green/red)."""
    plot_df = df.copy()
    factor = 100 if multiply else 1
    plot_df['Change'] = (pd.to_numeric(plot_df['Endline'], errors='coerce').fillna(0)
                         - pd.to_numeric(plot_df['Baseline'], errors='coerce').fillna(0)) * factor
    plot_df = plot_df.sort_values('Change')
    colors = [COLORS['good'] if v >= 0 else COLORS['danger'] for v in plot_df['Change']]
    fig = go.Figure()
    fig.add_trace(go.Bar(y=plot_df[cat_col], x=plot_df['Change'], orientation='h',
                         marker_color=colors,
                         text=plot_df['Change'].apply(lambda x: f"{x:+.1f}pp"), textposition='auto'))
    fig.update_layout(title=title, height=height, xaxis_title="Change (pp)",
                      yaxis=dict(categoryorder='trace'),
                      font=dict(size=13, color='#333'),
                      title_font=dict(size=16, color='#222'),
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                      margin=dict(l=20, r=20, t=60, b=20))
    return fig


def _gjj_stacked_bar(df, cat_col, columns, colors_list, title,
                     y_label="Percentage (%)", height=400, multiply=True):
    """Stacked horizontal bar chart for Likert / frequency distributions."""
    plot_df = df.copy()
    if multiply:
        for c in columns:
            plot_df[c] = pd.to_numeric(plot_df[c], errors='coerce').fillna(0) * 100
    fig = go.Figure()
    for col, color in zip(columns, colors_list):
        fig.add_trace(go.Bar(
            y=plot_df[cat_col], x=plot_df[col], name=col, orientation='h',
            marker_color=color,
            text=plot_df[col].apply(lambda x: f"{x:.1f}%" if x > 3 else ""),
            textposition='inside',
        ))
    fig.update_layout(title=title, barmode='stack', height=height,
                      xaxis_title=y_label,
                      legend=dict(orientation='h', yanchor='bottom', y=1.02),
                      yaxis=dict(categoryorder='array', categoryarray=list(plot_df[cat_col])),
                      font=dict(size=13, color='#333'),
                      title_font=dict(size=16, color='#222'),
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                      margin=dict(l=20, r=20, t=60, b=20))
    return fig


def _short_label(s, max_len=55):
    """Truncate long statement text for chart axis readability."""
    if isinstance(s, str) and len(s) > max_len:
        return s[:max_len].rstrip() + '...'
    return s


# ---- Tab 1: SELF — Confidence, Self-Worth & Compassion ----
def render_gjj_tab1(g):
    """GJJ KAP Women — Tab 1: SELF (Self-Esteem, Self-Compassion, Confidence)."""
    st.markdown("""<div class="section-narrative">
    <strong>Self-Efficacy &amp; Self-Beliefs:</strong> Women's agreement with self-esteem statements
    (strengths, feelings matter, gender equality) across baseline and endline. Tracks shifts in
    <em>Strongly Agree</em> rates and self-compassion frequency to assess programme impact on
    women's confidence and self-worth.
    </div>""", unsafe_allow_html=True)

    _quick_nav_pills(['Likert Breakdown', 'Strongly Agree Shift', 'Agreement vs Disagreement', 'Self-Compassion'])

    # --- KPIs: pp increase in Strongly Agree ---
    sa = g['self_strongly_agree']
    kpi_cols = st.columns(len(sa))
    for i, row in sa.iterrows():
        bl = row['Baseline'] if isinstance(row['Baseline'], (int, float)) else 0
        el = row['Endline'] if isinstance(row['Endline'], (int, float)) else 0
        change = (el - bl) * 100
        label = _short_label(row['Statement'], 40)
        kpi_cols[i].markdown(f"""<div class="kpi-card">
            <h3>{label}</h3>
            <div class="value">{el*100:.1f}%</div>
            <div class="delta-{'positive' if change>=0 else 'negative'}">{change:+.1f}pp Strongly Agree</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Likert stacked bars: Baseline vs Endline side by side ---
    _section_header('', 'Likert Breakdown — Baseline', 'SELF')
    likert_cols = ['Strongly agree', 'Agree', 'Disagree', 'Strongly disagree']
    likert_colors = ['#2E7D32', '#81C784', '#EF9A9A', '#C62828']
    bl_likert = g['self_baseline_likert'].copy()
    bl_likert['Statement'] = bl_likert['Statement'].apply(lambda s: _short_label(s))
    st.plotly_chart(
        _gjj_stacked_bar(bl_likert, 'Statement', likert_cols, likert_colors,
                         'SELF Statements — Baseline Likert', height=300),
        use_container_width=True)

    _section_header('', 'Likert Breakdown — Endline', 'SELF')
    el_likert = g['self_endline_likert'].copy()
    el_likert['Statement'] = el_likert['Statement'].apply(lambda s: _short_label(s))
    st.plotly_chart(
        _gjj_stacked_bar(el_likert, 'Statement', likert_cols, likert_colors,
                         'SELF Statements — Endline Likert', height=300),
        use_container_width=True)

    # --- Strongly Agree change ---
    st.markdown("---")
    _section_header('', 'Strongly Agree Shift (Baseline vs Endline)', 'SELF')
    sa_chart = sa.copy()
    sa_chart['Statement'] = sa_chart['Statement'].apply(lambda s: _short_label(s))
    st.plotly_chart(_gjj_bar(sa_chart, 'Statement', 'Strongly Agree: Baseline vs Endline',
                             height=350, orientation='h'), use_container_width=True)

    # --- Agreement vs Disagreement ---
    st.markdown("---")
    _section_header('', 'Agreement vs Disagreement', 'SELF')
    agr = g['self_agreement'].copy()
    agr['Statement'] = agr['Statement'].apply(lambda s: _short_label(s))
    agr_plot = agr.rename(columns={'Agreement_BL': 'Agree BL', 'Agreement_EL': 'Agree EL',
                                   'Disagreement_BL': 'Disagree BL', 'Disagreement_EL': 'Disagree EL'})
    agr_cols = ['Agree BL', 'Agree EL', 'Disagree BL', 'Disagree EL']
    agr_colors = ['#5B8DB8', '#2E7D32', '#EF9A9A', '#C62828']
    st.plotly_chart(
        _gjj_stacked_bar(agr_plot, 'Statement', agr_cols, agr_colors,
                         'Agreement vs Disagreement (Baseline & Endline)', height=300,
                         multiply=True),
        use_container_width=True)

    # --- Self-compassion frequency ---
    st.markdown("---")
    _section_header('', 'Self-Compassion Frequency', 'SELF')
    st.plotly_chart(_gjj_bar(g['self_compassion'], 'Category',
                             'Self-Compassion: "I nurture myself with kind self-talk..."',
                             height=350), use_container_width=True)


# ---- Tab 2: RELATIONAL WELLBEING ----
def render_gjj_tab2(g):
    """GJJ KAP Women — Tab 2: Relational Wellbeing."""
    st.markdown("""<div class="section-narrative">
    <strong>Relational Dynamics:</strong> Women's experience of partner support, respect, and
    communication — from laughing together to comfort voicing disagreement. Tracks frequency shifts
    (Always/Frequently vs Rarely/Never) from baseline to endline, plus relational equality and
    GJJ community support agreement.
    </div>""", unsafe_allow_html=True)

    _quick_nav_pills(['Frequency (BL)', 'Frequency (EL)', 'Always/Frequently vs Rarely/Never',
                       'Difference', 'Relational Equality'])

    # Short labels for axis readability
    def _shorten_rel(df):
        out = df.copy()
        out['Statement'] = out['Statement'].apply(lambda s: _short_label(s, 50))
        return out

    # --- Baseline frequency ---
    _section_header('', 'Relational Frequency — Baseline', 'Relational')
    freq_cols = ['Always', 'Frequently', 'Sometimes', 'Rarely', 'Never']
    freq_colors = ['#1B5E20', '#43A047', '#FDD835', '#EF9A9A', '#C62828']
    st.plotly_chart(
        _gjj_stacked_bar(_shorten_rel(g['rel_baseline_freq']), 'Statement',
                         freq_cols, freq_colors,
                         'Relational Circumstances — Baseline Frequency', height=450),
        use_container_width=True)

    # --- Endline frequency ---
    _section_header('', 'Relational Frequency — Endline', 'Relational')
    st.plotly_chart(
        _gjj_stacked_bar(_shorten_rel(g['rel_endline_freq']), 'Statement',
                         freq_cols, freq_colors,
                         'Relational Circumstances — Endline Frequency', height=450),
        use_container_width=True)

    # --- Always/Frequently vs Rarely/Never ---
    st.markdown("---")
    _section_header('', 'Always/Frequently vs Rarely/Never', 'Relational')
    af_rn = g['rel_af_rn'].copy()
    af_rn['Statement'] = af_rn['Statement'].apply(lambda s: _short_label(s, 50))

    # Build two side-by-side comparison charts
    c1, c2 = st.columns(2)
    with c1:
        af_df = af_rn[['Statement', 'AF_Baseline', 'AF_Endline']].rename(
            columns={'AF_Baseline': 'Baseline', 'AF_Endline': 'Endline'})
        st.plotly_chart(_gjj_bar(af_df, 'Statement', 'Always / Frequently',
                                 height=450, orientation='h'), use_container_width=True)
    with c2:
        rn_df = af_rn[['Statement', 'RN_Baseline', 'RN_Endline']].rename(
            columns={'RN_Baseline': 'Baseline', 'RN_Endline': 'Endline'})
        st.plotly_chart(_gjj_bar(rn_df, 'Statement', 'Rarely / Never',
                                 height=450, orientation='h'), use_container_width=True)

    # --- Difference chart ---
    st.markdown("---")
    _section_header('', 'Difference: Always/Frequently Change (pp)', 'Relational')
    dif_df = af_rn[['Statement', 'DIF_AF']].copy()
    dif_df['DIF_AF'] = pd.to_numeric(dif_df['DIF_AF'], errors='coerce').fillna(0) * 100
    dif_df = dif_df.sort_values('DIF_AF')
    colors = [COLORS['good'] if v >= 0 else COLORS['danger'] for v in dif_df['DIF_AF']]
    fig_dif = go.Figure()
    fig_dif.add_trace(go.Bar(y=dif_df['Statement'], x=dif_df['DIF_AF'], orientation='h',
                             marker_color=colors,
                             text=dif_df['DIF_AF'].apply(lambda x: f"{x:+.1f}pp"), textposition='auto'))
    fig_dif.update_layout(title='Change in Always/Frequently (Baseline to Endline)', height=400,
                          xaxis_title='Change (pp)', yaxis=dict(categoryorder='trace'),
                          font=dict(size=13, color='#333'), title_font=dict(size=16, color='#222'),
                          plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                          margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig_dif, use_container_width=True)

    # --- Relational equality agreement statements ---
    st.markdown("---")
    _section_header('', 'Relational Equality Statements', 'Relational')
    likert_cols = ['Strongly agree', 'Agree', 'Disagree', 'Strongly disagree']
    likert_colors = ['#2E7D32', '#81C784', '#EF9A9A', '#C62828']

    c3, c4 = st.columns(2)
    with c3:
        bl_agr = g['rel_agree_baseline'].copy()
        bl_agr['Statement'] = bl_agr['Statement'].apply(lambda s: _short_label(s, 45))
        st.plotly_chart(
            _gjj_stacked_bar(bl_agr, 'Statement', likert_cols, likert_colors,
                             'Relational Equality — Baseline', height=280),
            use_container_width=True)
    with c4:
        el_agr = g['rel_agree_endline'].copy()
        el_agr['Statement'] = el_agr['Statement'].apply(lambda s: _short_label(s, 45))
        st.plotly_chart(
            _gjj_stacked_bar(el_agr, 'Statement', likert_cols, likert_colors,
                             'Relational Equality — Endline', height=280),
            use_container_width=True)

    # Agreement summary
    _section_header('', 'Agreement vs Disagreement Summary', 'Relational')
    summ = g['rel_agreement_summary'].copy()
    summ['Statement'] = summ['Statement'].apply(lambda s: _short_label(s, 50))
    summ_plot = summ.rename(columns={'Agreement_BL': 'Agree BL', 'Agreement_EL': 'Agree EL',
                                     'Disagreement_BL': 'Disagree BL', 'Disagreement_EL': 'Disagree EL'})
    st.plotly_chart(
        _gjj_stacked_bar(summ_plot, 'Statement',
                         ['Agree BL', 'Agree EL', 'Disagree BL', 'Disagree EL'],
                         ['#5B8DB8', '#2E7D32', '#EF9A9A', '#C62828'],
                         'Agreement vs Disagreement (Baseline & Endline)', height=280),
        use_container_width=True)


# ---- Tab 3: Gender Transformation — Shared Responsibility ----
def render_gjj_tab3(g):
    """GJJ KAP Women — Tab 3: Shared Responsibility (Household Chores)."""
    st.markdown("""<div class="section-narrative">
    <strong>Shared Responsibility — Gender Transformation:</strong> Tracks husbands' support with
    traditionally female household chores, how long the support has been provided, frequency,
    types of chores completed, hours saved for women, and frequency of husbands enabling women
    time for rest, conservation work, or business.
    </div>""", unsafe_allow_html=True)

    _quick_nav_pills(['Chore Support', 'Duration & Frequency', 'Chore Types',
                       'Hours Saved', 'Women Self-Time'])

    # --- KPIs ---
    yes_bl = g['shared_chores_yn'].loc[g['shared_chores_yn']['Response'] == 'Yes', 'Baseline'].values
    yes_el = g['shared_chores_yn'].loc[g['shared_chores_yn']['Response'] == 'Yes', 'Endline'].values
    yes_bl = float(yes_bl[0]) if len(yes_bl) > 0 else 0
    yes_el = float(yes_el[0]) if len(yes_el) > 0 else 0
    chg = (yes_el - yes_bl) * 100

    disc_yes_bl = g['chore_discussed'].loc[g['chore_discussed']['Response'] == 'Yes', 'Baseline'].values
    disc_yes_el = g['chore_discussed'].loc[g['chore_discussed']['Response'] == 'Yes', 'Endline'].values
    disc_bl = float(disc_yes_bl[0]) if len(disc_yes_bl) > 0 else 0
    disc_el = float(disc_yes_el[0]) if len(disc_yes_el) > 0 else 0
    disc_chg = (disc_el - disc_bl) * 100

    comp_yes_bl = g['chore_completed'].loc[g['chore_completed']['Response'] == 'Yes', 'Baseline'].values
    comp_yes_el = g['chore_completed'].loc[g['chore_completed']['Response'] == 'Yes', 'Endline'].values
    comp_bl = float(comp_yes_bl[0]) if len(comp_yes_bl) > 0 else 0
    comp_el = float(comp_yes_el[0]) if len(comp_yes_el) > 0 else 0
    comp_chg = (comp_el - comp_bl) * 100

    kc1, kc2, kc3 = st.columns(3)
    kc1.markdown(f"""<div class="kpi-card">
        <h3>Husband Supports Chores</h3>
        <div class="value">{yes_el*100:.1f}%</div>
        <div class="delta-{'positive' if chg>=0 else 'negative'}">{chg:+.1f}pp from BL</div>
    </div>""", unsafe_allow_html=True)
    kc2.markdown(f"""<div class="kpi-card">
        <h3>Discussed Sharing Chores</h3>
        <div class="value">{disc_el*100:.1f}%</div>
        <div class="delta-{'positive' if disc_chg>=0 else 'negative'}">{disc_chg:+.1f}pp from BL</div>
    </div>""", unsafe_allow_html=True)
    kc3.markdown(f"""<div class="kpi-card">
        <h3>Completed Significant Chore</h3>
        <div class="value">{comp_el*100:.1f}%</div>
        <div class="delta-{'positive' if comp_chg>=0 else 'negative'}">{comp_chg:+.1f}pp from BL</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Husband supports chores Y/N ---
    _section_header('', 'Husband Supports Household Chores', 'Shared Responsibility')
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(_gjj_bar(g['shared_chores_yn'], 'Response',
                                 'Husband Supports Chores (Yes/No)', height=300),
                        use_container_width=True)
    with c2:
        st.plotly_chart(_gjj_bar(g['chore_discussed'], 'Response',
                                 'Discussed Sharing Unpaid Chores', height=300),
                        use_container_width=True)

    # --- Duration & Frequency ---
    st.markdown("---")
    _section_header('', 'Duration & Frequency of Support', 'Shared Responsibility')
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(_gjj_bar(g['chore_duration'], 'Category',
                                 'Time Since Husband Supporting Chores',
                                 height=400, orientation='h'), use_container_width=True)
    with c4:
        st.plotly_chart(_gjj_bar(g['chore_frequency'], 'Category',
                                 'Frequency Husbands Carry Out Chores',
                                 height=400, orientation='h'), use_container_width=True)

    # --- Who started conversation + completed chore ---
    st.markdown("---")
    c5, c6 = st.columns(2)
    with c5:
        st.plotly_chart(_gjj_bar(g['chore_initiator'], 'Person',
                                 'Person Who Started Conversation', height=300),
                        use_container_width=True)
    with c6:
        st.plotly_chart(_gjj_bar(g['chore_completed'], 'Response',
                                 'Husband Completed Significant Chore', height=300),
                        use_container_width=True)

    # --- Chore types ---
    st.markdown("---")
    _section_header('', 'Types of Chores Completed by Husband', 'Shared Responsibility')
    st.plotly_chart(_gjj_bar(g['chore_type'], 'Chore',
                             'Type of Household Chore Completed', height=350, orientation='h'),
                    use_container_width=True)

    # Change in chore types
    st.plotly_chart(_gjj_delta_bar(g['chore_type'], 'Chore',
                                   'Change in Chore Types (Baseline to Endline)', height=300),
                    use_container_width=True)

    # --- Hours saved ---
    st.markdown("---")
    _section_header('', 'Hours Saved for Women', 'Shared Responsibility')
    st.plotly_chart(_gjj_bar(g['hours_saved'], 'Hours',
                             'Hours Saved Due to Husband Support', height=380),
                    use_container_width=True)

    # --- Husband support for women self-time ---
    st.markdown("---")
    _section_header('', 'Women Self-Time Support', 'Shared Responsibility')
    st.plotly_chart(_gjj_bar(g['support_self_time'], 'Category',
                             'Husband Supports Women Taking Time for Themselves',
                             height=380), use_container_width=True)


# ---- Tab 4: Shared Power & Decision-Making ----
def render_gjj_tab4(g):
    """GJJ KAP Women — Tab 4: Shared Power & Decision-Making."""
    st.markdown("""<div class="section-narrative">
    <strong>Shared Power — Decision-Making:</strong> Household conversations about decision-making,
    types of important decisions taken in the past 6 months, who made them (husband alone, joint,
    wife alone), and whether women report having an equal say in joint decisions.
    </div>""", unsafe_allow_html=True)

    _quick_nav_pills(['Decision Conversations', 'Decision Types', 'Who Decides', 'Equal Say'])

    # --- KPIs ---
    conv_yes_bl = g['decision_conversations'].loc[
        g['decision_conversations']['Response'] == 'Yes', 'Baseline'].values
    conv_yes_el = g['decision_conversations'].loc[
        g['decision_conversations']['Response'] == 'Yes', 'Endline'].values
    conv_bl = float(conv_yes_bl[0]) if len(conv_yes_bl) > 0 else 0
    conv_el = float(conv_yes_el[0]) if len(conv_yes_el) > 0 else 0

    joint_bl = g['decision_maker'].loc[g['decision_maker']['Person'] == 'Joint', 'Baseline'].values
    joint_el = g['decision_maker'].loc[g['decision_maker']['Person'] == 'Joint', 'Endline'].values
    jt_bl = float(joint_bl[0]) if len(joint_bl) > 0 else 0
    jt_el = float(joint_el[0]) if len(joint_el) > 0 else 0

    eq_yes_bl = g['equal_say'].loc[g['equal_say']['Response'] == 'Yes', 'Baseline'].values
    eq_yes_el = g['equal_say'].loc[g['equal_say']['Response'] == 'Yes', 'Endline'].values
    eq_bl = float(eq_yes_bl[0]) if len(eq_yes_bl) > 0 else 0
    eq_el = float(eq_yes_el[0]) if len(eq_yes_el) > 0 else 0

    kc1, kc2, kc3 = st.columns(3)
    kc1.markdown(f"""<div class="kpi-card">
        <h3>Decision Conversations</h3>
        <div class="value">{conv_el*100:.1f}%</div>
        <div class="delta-{'positive' if conv_el>=conv_bl else 'negative'}">{(conv_el-conv_bl)*100:+.1f}pp</div>
    </div>""", unsafe_allow_html=True)
    kc2.markdown(f"""<div class="kpi-card">
        <h3>Joint Decision-Making</h3>
        <div class="value">{jt_el*100:.1f}%</div>
        <div class="delta-{'positive' if jt_el>=jt_bl else 'negative'}">{(jt_el-jt_bl)*100:+.1f}pp</div>
    </div>""", unsafe_allow_html=True)
    kc3.markdown(f"""<div class="kpi-card">
        <h3>Women Equal Say</h3>
        <div class="value">{eq_el*100:.1f}%</div>
        <div class="delta-{'positive' if eq_el>=eq_bl else 'negative'}">{(eq_el-eq_bl)*100:+.1f}pp</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Decision conversations & decisions made ---
    _section_header('', 'Decision Conversations & Decisions Made', 'Shared Power')
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(_gjj_bar(g['decision_conversations'], 'Response',
                                 'Conversations to Change Decision-Making', height=300),
                        use_container_width=True)
    with c2:
        st.plotly_chart(_gjj_bar(g['decisions_made'], 'Response',
                                 'Made Important Decisions (Past 6 Months)', height=300),
                        use_container_width=True)

    # --- Types of decisions ---
    st.markdown("---")
    _section_header('', 'Types of Decisions Taken', 'Shared Power')
    st.plotly_chart(_gjj_bar(g['decision_types'], 'Decision',
                             'Type of Decision Taken (Past 6 Months)',
                             height=500, orientation='h'), use_container_width=True)

    st.plotly_chart(_gjj_delta_bar(g['decision_types'], 'Decision',
                                   'Change in Decision Types (Baseline to Endline)',
                                   height=450), use_container_width=True)

    # --- Who makes decisions ---
    st.markdown("---")
    _section_header('', 'Who Makes Decisions', 'Shared Power')
    st.plotly_chart(_gjj_bar(g['decision_maker'], 'Person',
                             'Person Making the Decision', height=300),
                    use_container_width=True)

    # --- Equal say ---
    st.markdown("---")
    _section_header('', 'Equal Say in Joint Decisions', 'Shared Power')
    st.plotly_chart(_gjj_bar(g['equal_say'], 'Response',
                             'Women Reporting Equal Say in Joint Decisions', height=300),
                    use_container_width=True)


# ---- Tab 5: Autonomy & Leadership Support ----
def render_gjj_tab5(g):
    """GJJ KAP Women — Tab 5: Autonomy & Leadership."""
    st.markdown("""<div class="section-narrative">
    <strong>Autonomy &amp; Leadership:</strong> Whether women hide money to save, and the degree to
    which husbands would support women becoming community leaders or starting/growing their own
    businesses. Tracks shifts from baseline to endline across a 6-point certainty scale (Definitely
    to Definitely Not).
    </div>""", unsafe_allow_html=True)

    _quick_nav_pills(['Hiding Money', 'Leadership Support', 'Business Support'])

    # --- KPIs: Definitely support leadership + Definitely support business ---
    lead_def_bl = g['support_leader'].loc[
        g['support_leader']['Category'].str.strip().str.lower() == 'definitely', 'Baseline'].values
    lead_def_el = g['support_leader'].loc[
        g['support_leader']['Category'].str.strip().str.lower() == 'definitely', 'Endline'].values
    l_bl = float(lead_def_bl[0]) if len(lead_def_bl) > 0 else 0
    l_el = float(lead_def_el[0]) if len(lead_def_el) > 0 else 0

    biz_def_bl = g['support_business'].loc[
        g['support_business']['Category'].str.strip().str.lower() == 'definitely', 'Baseline'].values
    biz_def_el = g['support_business'].loc[
        g['support_business']['Category'].str.strip().str.lower() == 'definitely', 'Endline'].values
    b_bl = float(biz_def_bl[0]) if len(biz_def_bl) > 0 else 0
    b_el = float(biz_def_el[0]) if len(biz_def_el) > 0 else 0

    # Hiding money "Always" — lower is better
    hide_alw_bl = g['hide_money'].loc[
        g['hide_money']['Category'].str.strip().str.lower() == 'always', 'Baseline'].values
    hide_alw_el = g['hide_money'].loc[
        g['hide_money']['Category'].str.strip().str.lower() == 'always', 'Endline'].values
    h_bl = float(hide_alw_bl[0]) if len(hide_alw_bl) > 0 else 0
    h_el = float(hide_alw_el[0]) if len(hide_alw_el) > 0 else 0
    hide_chg = (h_el - h_bl) * 100

    kc1, kc2, kc3 = st.columns(3)
    kc1.markdown(f"""<div class="kpi-card">
        <h3>Hide Money "Always"</h3>
        <div class="value">{h_el*100:.1f}%</div>
        <div class="delta-{'positive' if hide_chg<=0 else 'negative'}">{hide_chg:+.1f}pp (lower = better)</div>
    </div>""", unsafe_allow_html=True)
    kc2.markdown(f"""<div class="kpi-card">
        <h3>Definitely Support Leader</h3>
        <div class="value">{l_el*100:.1f}%</div>
        <div class="delta-{'positive' if l_el>=l_bl else 'negative'}">{(l_el-l_bl)*100:+.1f}pp</div>
    </div>""", unsafe_allow_html=True)
    kc3.markdown(f"""<div class="kpi-card">
        <h3>Definitely Support Business</h3>
        <div class="value">{b_el*100:.1f}%</div>
        <div class="delta-{'positive' if b_el>=b_bl else 'negative'}">{(b_el-b_bl)*100:+.1f}pp</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Hiding money ---
    _section_header('', 'Hiding Money from Husband to Save', 'Autonomy')
    st.plotly_chart(_gjj_bar(g['hide_money'], 'Category',
                             'Women Hiding Money (Frequency)', height=380),
                    use_container_width=True)

    # --- Leadership support ---
    st.markdown("---")
    _section_header('', 'Husband Support for Women Becoming Leaders', 'Leadership')
    st.plotly_chart(_gjj_bar(g['support_leader'], 'Category',
                             'Support if Wife Wanted to Become Community Leader',
                             height=380), use_container_width=True)
    st.plotly_chart(_gjj_delta_bar(g['support_leader'], 'Category',
                                   'Change in Leadership Support (Baseline to Endline)',
                                   height=350), use_container_width=True)

    # --- Business support ---
    st.markdown("---")
    _section_header('', 'Husband Support for Women Starting/Growing Business', 'Leadership')
    st.plotly_chart(_gjj_bar(g['support_business'], 'Category',
                             'Support if Wife Started/Grew Own Business',
                             height=380), use_container_width=True)
    st.plotly_chart(_gjj_delta_bar(g['support_business'], 'Category',
                                   'Change in Business Support (Baseline to Endline)',
                                   height=350), use_container_width=True)


# ============================================================================
# MAIN
# ============================================================================

# ============================================================================
# INSIGHTS TAB — Automated insights across both datasets
# ============================================================================

def _insight_card(title, body, trend="neutral"):
    """Render a styled insight card with optional trend indicator."""
    color_map = {"positive": "#2E7D32", "negative": "#C62828", "neutral": "#37474F", "warning": "#E65100"}
    bg_map = {"positive": "#E8F5E9", "negative": "#FFEBEE", "neutral": "#ECEFF1", "warning": "#FFF3E0"}
    border = color_map.get(trend, color_map["neutral"])
    bg = bg_map.get(trend, bg_map["neutral"])
    st.markdown(f"""
    <div style="background:{bg}; border-left:5px solid {border}; border-radius:0 10px 10px 0;
                padding:1.2rem 1.5rem; margin-bottom:1rem; box-shadow:0 1px 6px rgba(0,0,0,0.06);">
        <h4 style="margin:0 0 0.4rem; color:{border}; font-size:1.05rem; font-weight:700;">{title}</h4>
        <p style="margin:0; color:#333; font-size:0.93rem; line-height:1.6;">{body}</p>
    </div>""", unsafe_allow_html=True)


def _pp(bl, ml, multiply=True):
    """Calculate percentage-point change."""
    factor = 100 if multiply else 1
    if isinstance(bl, (int, float)) and isinstance(ml, (int, float)):
        return round((ml - bl) * factor, 1)
    return 0.0


def _generate_forestry_insights(data):
    """Generate automated insights from forestry data."""
    insights = []
    try:
        _gen_forestry_insights_inner(data, insights)
    except Exception as e:
        insights.append(("Insight Generation Note",
                         f"Some forestry insights could not be generated: {e}",
                         "neutral"))
    return insights


def _gen_forestry_insights_inner(data, insights):
    ft = data['functionality_threshold']
    bl_60 = ft.loc[ft['Timepoint'] == 'Baseline', 'Functional_60_pct'].values[0]
    ml_60 = ft.loc[ft['Timepoint'] == 'Midline', 'Functional_60_pct'].values[0]
    change_60 = _pp(bl_60, ml_60, multiply=isinstance(bl_60, float) and bl_60 <= 1)
    if change_60 > 0:
        insights.append(("Functionality Threshold Improved",
                         f"Groups meeting the 60% functionality threshold increased by {change_60:+.1f} pp "
                         f"(Baseline: {bl_60*100 if bl_60 <= 1 else bl_60:.1f}% to Midline: {ml_60*100 if ml_60 <= 1 else ml_60:.1f}%). "
                         f"This signals stronger institutional capacity at community level.",
                         "positive"))
    elif change_60 < 0:
        insights.append(("Functionality Threshold Declined",
                         f"Groups meeting the 60% functionality threshold dropped by {change_60:+.1f} pp. "
                         f"This may require targeted institutional strengthening.",
                         "negative"))

    # 2. Domain scores
    fd = data['functionality_domain']
    for domain in ['Management', 'Gender', 'Effectiveness']:
        bl_d = fd.loc[fd['Timepoint'] == 'Baseline', domain].values[0]
        ml_d = fd.loc[fd['Timepoint'] == 'Midline', domain].values[0]
        change_d = round(ml_d - bl_d, 1) if isinstance(bl_d, (int, float)) and isinstance(ml_d, (int, float)) else 0
        if abs(change_d) >= 3:
            trend = "positive" if change_d > 0 else "negative"
            insights.append((f"{domain} Domain: {change_d:+.1f} Points",
                             f"The {domain} domain score moved from {bl_d:.1f} to {ml_d:.1f} "
                             f"({change_d:+.1f} pts). "
                             f"{'This is a meaningful improvement.' if change_d > 0 else 'This decline warrants attention.'}",
                             trend))

    # 3. Women leadership
    wl = data['women_leadership']
    sig_bl = wl.loc[wl['Category'] == 'Significant Leadership', 'Baseline'].values[0]
    sig_ml = wl.loc[wl['Category'] == 'Significant Leadership', 'Midline'].values[0]
    wl_change = _pp(sig_bl, sig_ml, multiply=isinstance(sig_bl, float) and sig_bl <= 1)
    if abs(wl_change) >= 2:
        trend = "positive" if wl_change > 0 else "warning"
        insights.append(("Women in Significant Leadership",
                         f"The share of groups with significant women's leadership changed by {wl_change:+.1f} pp "
                         f"({sig_bl*100 if sig_bl <= 1 else sig_bl:.1f}% to {sig_ml*100 if sig_ml <= 1 else sig_ml:.1f}%). "
                         f"Gender equity in forest governance is {'advancing' if wl_change > 0 else 'a continuing challenge'}.",
                         trend))

    # 4. Training coverage
    tc = data['training_coverage']
    most_bl = tc.loc[tc['Category'] == 'Most Members', 'Baseline'].values[0]
    most_ml = tc.loc[tc['Category'] == 'Most Members', 'Midline'].values[0]
    tc_change = _pp(most_bl, most_ml, multiply=isinstance(most_bl, float) and most_bl <= 1)
    insights.append(("Training Coverage (Most Members)",
                     f"Groups where most members received training: "
                     f"{most_bl*100 if most_bl <= 1 else most_bl:.1f}% (BL) to {most_ml*100 if most_ml <= 1 else most_ml:.1f}% (ML), "
                     f"a change of {tc_change:+.1f} pp. "
                     f"{'Capacity building is expanding.' if tc_change > 0 else 'Training outreach needs scaling up.'}",
                     "positive" if tc_change > 0 else "warning"))

    # 5. Income generation
    ig = data['income_gen']
    yes_bl = ig.loc[ig['Category'] == 'Yes', 'Baseline'].values[0]
    yes_ml = ig.loc[ig['Category'] == 'Yes', 'Midline'].values[0]
    ig_change = _pp(yes_bl, yes_ml, multiply=isinstance(yes_bl, float) and yes_bl <= 1)
    insights.append(("Forest-Based Income Generation",
                     f"Groups generating income from forests: "
                     f"{yes_bl*100 if yes_bl <= 1 else yes_bl:.1f}% (BL) to {yes_ml*100 if yes_ml <= 1 else yes_ml:.1f}% (ML) "
                     f"({ig_change:+.1f} pp). "
                     f"{'Economic sustainability is strengthening.' if ig_change > 0 else 'Livelihood diversification needs attention.'}",
                     "positive" if ig_change > 0 else "warning"))

    # 6. Forest condition — good rated
    fc = data['forest_condition']
    good_cols_bl = [c for c in fc.columns if 'Good' in c and 'Baseline' in c]
    good_cols_ml = [c for c in fc.columns if 'Good' in c and 'Midline' in c]
    if good_cols_bl and good_cols_ml:
        avg_good_bl = fc[good_cols_bl[0]].mean()
        avg_good_ml = fc[good_cols_ml[0]].mean()
        fc_change = _pp(avg_good_bl, avg_good_ml, multiply=isinstance(avg_good_bl, float) and avg_good_bl <= 1)
        insights.append(("Forest Condition (Good Rating)",
                         f"Average 'Good' forest condition rating across all characteristics: "
                         f"{avg_good_bl*100 if avg_good_bl <= 1 else avg_good_bl:.1f}% (BL) to "
                         f"{avg_good_ml*100 if avg_good_ml <= 1 else avg_good_ml:.1f}% (ML) ({fc_change:+.1f} pp). "
                         f"{'Forests are perceived as healthier.' if fc_change > 0 else 'Forest health perceptions have not improved.'}",
                         "positive" if fc_change > 0 else "warning"))

    # 7. Agroforestry adoption
    af = data['agroforestry']
    af_yes_bl = af.loc[af['Category'] == 'Yes', 'Baseline'].values[0]
    af_yes_ml = af.loc[af['Category'] == 'Yes', 'Midline'].values[0]
    af_change = _pp(af_yes_bl, af_yes_ml, multiply=isinstance(af_yes_bl, float) and af_yes_bl <= 1)
    insights.append(("Agroforestry Adoption",
                     f"Groups practicing agroforestry: "
                     f"{af_yes_bl*100 if af_yes_bl <= 1 else af_yes_bl:.1f}% (BL) to "
                     f"{af_yes_ml*100 if af_yes_ml <= 1 else af_yes_ml:.1f}% (ML) ({af_change:+.1f} pp). "
                     f"{'Adoption is growing, supporting landscape restoration.' if af_change > 0 else 'More incentives may be needed to drive adoption.'}",
                     "positive" if af_change > 0 else "neutral"))

    return insights


def _generate_women_insights(w):
    """Generate automated insights from women survey data."""
    insights = []
    try:
        _gen_women_insights_inner(w, insights)
    except Exception as e:
        insights.append(("Insight Generation Note",
                         f"Some women survey insights could not be generated: {e}",
                         "neutral"))
    return insights


def _gen_women_insights_inner(w, insights):
    # 1. Climate change awareness
    cc = w['cc_heard']
    cc_yes_bl = cc.loc[cc['Response'] == 'Yes', 'Baseline'].values[0]
    cc_yes_ml = cc.loc[cc['Response'] == 'Yes', 'Midline'].values[0]
    cc_change = _pp(cc_yes_bl, cc_yes_ml)
    insights.append(("Climate Change Awareness",
                     f"Women who have heard of climate change: "
                     f"{cc_yes_bl*100:.1f}% (BL) to {cc_yes_ml*100:.1f}% (ML) ({cc_change:+.1f} pp). "
                     f"{'Awareness is growing across communities.' if cc_change > 0 else 'Additional outreach on climate literacy is needed.'}",
                     "positive" if cc_change > 0 else "warning"))

    # 2. NbS awareness
    nbs = w['nbs_heard']
    nbs_yes_bl = nbs.loc[nbs['Response'] == 'Yes', 'Baseline'].values[0]
    nbs_yes_ml = nbs.loc[nbs['Response'] == 'Yes', 'Midline'].values[0]
    nbs_change = _pp(nbs_yes_bl, nbs_yes_ml)
    insights.append(("Nature-based Solutions Awareness",
                     f"Women aware of NbS: {nbs_yes_bl*100:.1f}% (BL) to {nbs_yes_ml*100:.1f}% (ML) "
                     f"({nbs_change:+.1f} pp). "
                     f"{'NbS concepts are reaching more women.' if nbs_change > 0 else 'NbS messaging needs strengthening.'}",
                     "positive" if nbs_change > 0 else "warning"))

    # 3. Savings behavior
    ps = w['personal_saving']
    ps_yes_bl = ps.loc[ps['Response'] == 'Yes', 'Baseline'].values[0]
    ps_yes_ml = ps.loc[ps['Response'] == 'Yes', 'Midline'].values[0]
    ps_change = _pp(ps_yes_bl, ps_yes_ml)
    insights.append(("Personal Savings",
                     f"Women with personal savings: {ps_yes_bl*100:.1f}% (BL) to {ps_yes_ml*100:.1f}% (ML) "
                     f"({ps_change:+.1f} pp). "
                     f"Financial resilience is {'building' if ps_change > 0 else 'a key area for intervention'}.",
                     "positive" if ps_change > 0 else "warning"))

    # 4. Decision-making influence — average across all decisions
    di = w['decision_influence']
    avg_bl = di['Baseline'].mean()
    avg_ml = di['Midline'].mean()
    di_change = _pp(avg_bl, avg_ml)
    insights.append(("Decision-Making Influence",
                     f"Average share of women reporting 'large extent' influence on HH decisions: "
                     f"{avg_bl*100:.1f}% (BL) to {avg_ml*100:.1f}% (ML) ({di_change:+.1f} pp). "
                     + ("Women's agency is strengthening." if di_change > 0 else "Empowerment efforts need scaling."),
                     "positive" if di_change > 0 else "warning"))

    # 5. Life skills — average agree/strongly agree
    ls = w['lifeskills_agree']
    ls_avg_bl = ls['Baseline'].mean()
    ls_avg_ml = ls['Midline'].mean()
    ls_change = _pp(ls_avg_bl, ls_avg_ml)
    insights.append(("Life Skills Confidence",
                     f"Average agree/strongly agree on life skills statements: "
                     f"{ls_avg_bl*100:.1f}% (BL) to {ls_avg_ml*100:.1f}% (ML) ({ls_change:+.1f} pp). "
                     f"{'Self-esteem and leadership confidence are growing.' if ls_change > 0 else 'Soft skills programming needs reinforcement.'}",
                     "positive" if ls_change > 0 else "neutral"))

    # 6. Social norms — want DECREASES (lower = better for harmful norms)
    sn = w['socialnorms_agree']
    harmful_norms = sn[~sn['Norm'].str.contains('Planting Crops|Restoring Ecosystems|Express Emotions', regex=True)]
    sn_avg_bl = harmful_norms['Baseline'].mean()
    sn_avg_ml = harmful_norms['Midline'].mean()
    sn_change = _pp(sn_avg_bl, sn_avg_ml)
    trend = "positive" if sn_change < 0 else ("negative" if sn_change > 2 else "neutral")
    insights.append(("Harmful Social Norms",
                     f"Average agreement with harmful gender norms: "
                     f"{sn_avg_bl*100:.1f}% (BL) to {sn_avg_ml*100:.1f}% (ML) ({sn_change:+.1f} pp). "
                     f"{'Positive shift — harmful norms are weakening.' if sn_change < 0 else 'Norms remain entrenched; continued dialogue is critical.'}",
                     trend))

    # 7. Coping strategies — top 3 most used at midline
    cop = w['coping'].copy()
    cop['ML_pct'] = cop['Midline'].apply(lambda x: x * 100 if isinstance(x, (int, float)) and x <= 1 else x)
    top3 = cop.nlargest(3, 'ML_pct')
    top3_text = ', '.join([f"{row['Strategy']} ({row['ML_pct']:.1f}%)" for _, row in top3.iterrows()])
    insights.append(("Top Coping Strategies (Midline)",
                     f"The three most common coping strategies at midline are: {top3_text}. "
                     f"High reliance on meal-skipping or asset sales signals food insecurity concerns.",
                     "warning"))

    # 8. Time use
    ts = w['time_summary']
    unpaid_bl = ts.loc[ts['Category'] == 'Unpaid Care Work', 'Baseline'].values[0]
    unpaid_ml = ts.loc[ts['Category'] == 'Unpaid Care Work', 'Midline'].values[0]
    unpaid_diff = round(unpaid_ml - unpaid_bl, 2) if isinstance(unpaid_bl, (int, float)) else 0
    insights.append(("Women's Unpaid Care Work",
                     f"Average daily unpaid care work: {unpaid_bl:.1f}h (BL) to {unpaid_ml:.1f}h (ML) "
                     f"({unpaid_diff:+.1f}h change). "
                     f"{'Care burden is decreasing — more time for productive activities.' if unpaid_diff < 0 else 'Care burden persists; labour-sharing interventions may help.'}",
                     "positive" if unpaid_diff < 0 else "warning"))

    # 9. Disaster preparedness
    pk = w['prep_knowledge']
    pk_yes_bl = pk.loc[pk['Response'] == 'Yes', 'Baseline'].values[0]
    pk_yes_ml = pk.loc[pk['Response'] == 'Yes', 'Midline'].values[0]
    pk_change = _pp(pk_yes_bl, pk_yes_ml)
    insights.append(("Disaster Preparedness Knowledge",
                     f"Women aware of disaster preparedness plans: "
                     f"{pk_yes_bl*100:.1f}% (BL) to {pk_yes_ml*100:.1f}% (ML) ({pk_change:+.1f} pp). "
                     f"{'Communities are becoming better prepared.' if pk_change > 0 else 'DRR awareness remains a gap.'}",
                     "positive" if pk_change > 0 else "warning"))

    return insights


def _generate_men_insights(m):
    """Generate automated insights from men survey data."""
    insights = []
    try:
        _gen_men_insights_inner(m, insights)
    except Exception as e:
        insights.append(("Insight Generation Note",
                         f"Some men survey insights could not be generated: {e}",
                         "neutral"))
    return insights


def _gen_men_insights_inner(m, insights):
    # 1. Climate change awareness
    cc = m['cc_heard']
    cc_yes_bl = cc.loc[cc['Response'] == 'Yes', 'Baseline'].values[0]
    cc_yes_ml = cc.loc[cc['Response'] == 'Yes', 'Midline'].values[0]
    cc_change = _pp(cc_yes_bl, cc_yes_ml)
    insights.append(("Men's CC Awareness",
                     f"Men who have heard of climate change: "
                     f"{cc_yes_bl*100:.1f}% (BL) to {cc_yes_ml*100:.1f}% (ML) ({cc_change:+.1f} pp). "
                     f"{'Awareness is growing among men.' if cc_change > 0 else 'Climate literacy programmes should target men as well.'}",
                     "positive" if cc_change > 0 else "warning"))

    # 2. NbS awareness
    nbs = m['nbs_heard']
    nbs_yes_bl = nbs.loc[nbs['Response'] == 'Yes', 'Baseline'].values[0]
    nbs_yes_ml = nbs.loc[nbs['Response'] == 'Yes', 'Midline'].values[0]
    nbs_change = _pp(nbs_yes_bl, nbs_yes_ml)
    insights.append(("Men's NbS Awareness",
                     f"Men aware of NbS: {nbs_yes_bl*100:.1f}% (BL) to {nbs_yes_ml*100:.1f}% (ML) "
                     f"({nbs_change:+.1f} pp). "
                     f"{'NbS concepts are reaching more men.' if nbs_change > 0 else 'NbS outreach to men needs strengthening.'}",
                     "positive" if nbs_change > 0 else "warning"))

    # 3. Joint roles (should) — average
    rj = m['roles_should_joint']
    rj_avg_bl = rj['Baseline'].mean()
    rj_avg_ml = rj['Midline'].mean()
    rj_change = _pp(rj_avg_bl, rj_avg_ml)
    insights.append(("Men's Attitude: Joint Roles",
                     f"Average share of men saying household roles SHOULD be joint: "
                     f"{rj_avg_bl*100:.1f}% (BL) to {rj_avg_ml*100:.1f}% (ML) ({rj_change:+.1f} pp). "
                     + ("Men increasingly support equitable household labour sharing." if rj_change > 0
                        else "Attitudes toward joint roles remain largely unchanged."),
                     "positive" if rj_change > 0 else "neutral"))

    # 4. Joint decisions (should) — average
    dj = m['decision_should_joint']
    dj_avg_bl = dj['Baseline'].mean()
    dj_avg_ml = dj['Midline'].mean()
    dj_change = _pp(dj_avg_bl, dj_avg_ml)
    insights.append(("Men's Attitude: Joint Decisions",
                     f"Average share of men saying household decisions SHOULD be joint: "
                     f"{dj_avg_bl*100:.1f}% (BL) to {dj_avg_ml*100:.1f}% (ML) ({dj_change:+.1f} pp). "
                     + ("More men are embracing shared decision-making norms." if dj_change > 0
                        else "Further engagement on equitable decision-making is needed."),
                     "positive" if dj_change > 0 else "neutral"))

    # 5. Social norms — harmful norms (want DECREASES)
    sn = m['socialnorms_agree']
    harmful = sn[~sn['Norm'].str.contains('Planting Crops|Restoring Ecosystems|Express Emotions', regex=True)]
    sn_avg_bl = harmful['Baseline'].mean()
    sn_avg_ml = harmful['Midline'].mean()
    sn_change = _pp(sn_avg_bl, sn_avg_ml)
    trend = "positive" if sn_change < 0 else ("negative" if sn_change > 2 else "neutral")
    insights.append(("Men's Harmful Social Norms",
                     f"Average agreement with harmful gender norms among men: "
                     f"{sn_avg_bl*100:.1f}% (BL) to {sn_avg_ml*100:.1f}% (ML) ({sn_change:+.1f} pp). "
                     f"{'Positive shift — harmful norms are weakening among men.' if sn_change < 0 else 'Norms among men remain entrenched; continued dialogue is critical.'}",
                     trend))

    # 6. Support for women in NbS — Mangrove + Seaweed + Forest (Yes)
    support_sum = 0
    support_count = 0
    for key in ['mangrove_support', 'seaweed_support', 'forest_support']:
        df = m[key]
        yes_bl = df.loc[df['Response'] == 'Yes', 'Baseline'].values[0] if len(df[df['Response'] == 'Yes']) else 0
        yes_ml = df.loc[df['Response'] == 'Yes', 'Midline'].values[0] if len(df[df['Response'] == 'Yes']) else 0
        support_sum += _pp(yes_bl, yes_ml)
        support_count += 1
    avg_support_change = support_sum / max(support_count, 1)
    insights.append(("Men's Support for Women in NbS",
                     f"Average change in men saying 'Yes' to supporting women's NbS participation "
                     f"(mangrove, seaweed, forest): {avg_support_change:+.1f} pp. "
                     + ("Men are increasingly supporting women's conservation roles." if avg_support_change > 0
                        else "Men's active support for women's NbS participation needs strengthening."),
                     "positive" if avg_support_change > 0 else "warning"))

    # 7. Time use — men's unpaid care work
    ts = m['time_summary']
    unpaid_bl = ts.loc[ts['Category'] == 'Unpaid Care Work', 'Baseline'].values[0]
    unpaid_ml = ts.loc[ts['Category'] == 'Unpaid Care Work', 'Midline'].values[0]
    unpaid_diff = round(unpaid_ml - unpaid_bl, 2) if isinstance(unpaid_bl, (int, float)) else 0
    care_msg = ("Men are taking on more care responsibilities \u2014 positive for gender equity."
                if unpaid_diff > 0
                else "Men's care contribution remains low; household labour-sharing needs attention.")
    insights.append(("Men's Unpaid Care Work",
                     f"Average daily unpaid care work by men: {unpaid_bl:.1f}h (BL) to {unpaid_ml:.1f}h (ML) "
                     f"({unpaid_diff:+.1f}h change). {care_msg}",
                     "positive" if unpaid_diff > 0 else "warning"))

    return insights


def _generate_cross_cutting_insights(f_data, w_data, m_data=None):
    """Generate insights that span all datasets."""
    insights = []
    try:
        _gen_cross_cutting_inner(f_data, w_data, m_data, insights)
    except Exception as e:
        insights.append(("Insight Generation Note",
                         f"Some cross-cutting insights could not be generated: {e}",
                         "neutral"))
    return insights


def _gen_cross_cutting_inner(f_data, w_data, m_data, insights):
    # 1. Governance + Empowerment linkage
    fd = f_data['functionality_domain']
    gender_bl = fd.loc[fd['Timepoint'] == 'Baseline', 'Gender'].values[0]
    gender_ml = fd.loc[fd['Timepoint'] == 'Midline', 'Gender'].values[0]
    gender_change = round(gender_ml - gender_bl, 1)

    di = w_data['decision_influence']
    avg_infl_bl = di['Baseline'].mean() * 100
    avg_infl_ml = di['Midline'].mean() * 100
    infl_change = round(avg_infl_ml - avg_infl_bl, 1)

    insights.append(("Governance & Empowerment Linkage",
                     f"Forestry gender domain score changed by {gender_change:+.1f} pts while women's "
                     f"decision-making influence shifted by {infl_change:+.1f} pp. "
                     + ("Both are moving in the right direction — community and household empowerment reinforce each other."
                        if gender_change > 0 and infl_change > 0
                        else "Progress at one level has not fully translated to the other — integrated programming may help."),
                     "positive" if gender_change > 0 and infl_change > 0 else "neutral"))

    # 2. Environment + NbS
    nbs_yes_ml = w_data['nbs_heard'].loc[w_data['nbs_heard']['Response'] == 'Yes', 'Midline'].values[0] * 100
    fc = f_data['forest_condition']
    avg_good_ml = fc['Midline_Good'].mean()
    avg_good_ml_pct = avg_good_ml * 100 if avg_good_ml <= 1 else avg_good_ml
    insights.append(("Environmental Knowledge & Forest Health",
                     f"At midline, {nbs_yes_ml:.1f}% of women know about NbS, while {avg_good_ml_pct:.1f}% "
                     f"of forests are rated 'Good' condition. Growing environmental literacy can translate "
                     f"into better community-based conservation outcomes.",
                     "neutral"))

    # 3. Training + Life Skills
    tc = f_data['training_coverage']
    most_ml = tc.loc[tc['Category'] == 'Most Members', 'Midline'].values[0]
    most_ml_pct = most_ml * 100 if most_ml <= 1 else most_ml

    ls = w_data['lifeskills_agree']
    ls_avg_ml = ls['Midline'].mean() * 100
    insights.append(("Training Reach & Life Skills",
                     f"Groups where most members are trained: {most_ml_pct:.1f}%. "
                     f"Average women's life skills confidence: {ls_avg_ml:.1f}%. "
                     f"Investing in both community-level training and individual skills development "
                     f"creates compounding empowerment effects.",
                     "positive" if most_ml_pct > 30 and ls_avg_ml > 50 else "neutral"))

    # 4. Economic resilience
    ig = f_data['income_gen']
    ig_yes_ml = ig.loc[ig['Category'] == 'Yes', 'Midline'].values[0]
    ig_yes_ml_pct = ig_yes_ml * 100 if ig_yes_ml <= 1 else ig_yes_ml

    ps = w_data['personal_saving']
    ps_yes_ml = ps.loc[ps['Response'] == 'Yes', 'Midline'].values[0] * 100
    insights.append(("Economic Resilience Snapshot",
                     f"At midline, {ig_yes_ml_pct:.1f}% of forestry groups generate income and "
                     f"{ps_yes_ml:.1f}% of women have personal savings. Linking group-level income "
                     f"activities with individual savings programs can strengthen household resilience.",
                     "positive" if ig_yes_ml_pct > 50 and ps_yes_ml > 40 else "neutral"))

    # 5. Men-Women alignment on social norms (only if men data is available)
    if m_data is not None:
        w_sn = w_data['socialnorms_agree']
        w_harmful = w_sn[~w_sn['Norm'].str.contains('Planting Crops|Restoring Ecosystems|Express Emotions', regex=True)]
        w_sn_change = _pp(w_harmful['Baseline'].mean(), w_harmful['Midline'].mean())
        m_sn = m_data['socialnorms_agree']
        m_harmful = m_sn[~m_sn['Norm'].str.contains('Planting Crops|Restoring Ecosystems|Express Emotions', regex=True)]
        m_sn_change = _pp(m_harmful['Baseline'].mean(), m_harmful['Midline'].mean())
        both_improving = w_sn_change < 0 and m_sn_change < 0
        insights.append(("Gender Norms: Men vs Women Alignment",
                         f"Harmful norms agreement changed by {w_sn_change:+.1f} pp among women "
                         f"and {m_sn_change:+.1f} pp among men. "
                         + ("Both groups show declining support for harmful norms — a strong signal of programme impact."
                            if both_improving
                            else "Norms are shifting unevenly between men and women — targeted messaging for each group may help."),
                         "positive" if both_improving else "neutral"))

        # 6. Men's support for women + women's actual participation
        m_support_pcts = []
        for key in ['mangrove_support', 'seaweed_support', 'forest_support']:
            df = m_data[key]
            yes_ml = df.loc[df['Response'] == 'Yes', 'Midline'].values[0] if len(df[df['Response'] == 'Yes']) else 0
            m_support_pcts.append(yes_ml * 100)
        avg_support = sum(m_support_pcts) / len(m_support_pcts)
        insights.append(("Men's Support & Women's Conservation Participation",
                         f"On average, {avg_support:.1f}% of men say they support women's NbS participation "
                         f"at midline. Aligning men's declared support with actual resource allocation "
                         f"and time-sharing remains a key programming challenge.",
                         "positive" if avg_support > 50 else "neutral"))

        # 7. Decision-making alignment: who should vs who does
        m_dj_should_avg = m_data['decision_should_joint']['Midline'].mean() * 100
        m_dj_does_avg = m_data['decision_does_joint']['Midline'].mean() * 100
        gap = round(m_dj_should_avg - m_dj_does_avg, 1)
        insights.append(("Decision-Making: Attitudes vs Practice (Men)",
                         f"At midline, {m_dj_should_avg:.1f}% of men say decisions should be joint, "
                         f"but only {m_dj_does_avg:.1f}% report decisions actually being joint "
                         f"(gap: {gap:+.1f} pp). "
                         + ("A gap persists between progressive attitudes and actual behaviour." if gap > 5
                            else "Attitudes and practice are closely aligned — encouraging."),
                         "warning" if gap > 5 else "positive"))

    return insights


def _build_indicator_table(f_data, w_data, m_data=None):
    """Build a master table of key indicators with BL/ML values for trend charts."""
    rows = []

    # Forestry indicators
    ft = f_data['functionality_threshold']
    bl_60 = ft.loc[ft['Timepoint'] == 'Baseline', 'Functional_60_pct'].values[0]
    ml_60 = ft.loc[ft['Timepoint'] == 'Midline', 'Functional_60_pct'].values[0]
    rows.append({'Indicator': 'Functionality >=60%', 'Dataset': 'Forestry',
                 'Baseline': round(bl_60 * 100 if bl_60 <= 1 else bl_60, 1),
                 'Midline': round(ml_60 * 100 if ml_60 <= 1 else ml_60, 1)})

    for domain in ['Management', 'Gender', 'Effectiveness', 'Overall']:
        fd = f_data['functionality_domain']
        b = fd.loc[fd['Timepoint'] == 'Baseline', domain].values[0]
        m = fd.loc[fd['Timepoint'] == 'Midline', domain].values[0]
        rows.append({'Indicator': f'{domain} Score', 'Dataset': 'Forestry',
                     'Baseline': round(b, 1), 'Midline': round(m, 1)})

    ig = f_data['income_gen']
    b_ig = ig.loc[ig['Category'] == 'Yes', 'Baseline'].values[0]
    m_ig = ig.loc[ig['Category'] == 'Yes', 'Midline'].values[0]
    rows.append({'Indicator': 'Income Generation', 'Dataset': 'Forestry',
                 'Baseline': round(b_ig * 100 if b_ig <= 1 else b_ig, 1),
                 'Midline': round(m_ig * 100 if m_ig <= 1 else m_ig, 1)})

    af = f_data['agroforestry']
    b_af = af.loc[af['Category'] == 'Yes', 'Baseline'].values[0]
    m_af = af.loc[af['Category'] == 'Yes', 'Midline'].values[0]
    rows.append({'Indicator': 'Agroforestry', 'Dataset': 'Forestry',
                 'Baseline': round(b_af * 100 if b_af <= 1 else b_af, 1),
                 'Midline': round(m_af * 100 if m_af <= 1 else m_af, 1)})

    # Women indicators
    for label, df_key, resp_col, resp_val in [
        ('CC Awareness', 'cc_heard', 'Response', 'Yes'),
        ('NbS Awareness', 'nbs_heard', 'Response', 'Yes'),
        ('Personal Savings', 'personal_saving', 'Response', 'Yes'),
        ('Prep Knowledge', 'prep_knowledge', 'Response', 'Yes'),
    ]:
        df = w_data[df_key]
        b_w = df.loc[df[resp_col] == resp_val, 'Baseline'].values[0]
        m_w = df.loc[df[resp_col] == resp_val, 'Midline'].values[0]
        rows.append({'Indicator': label, 'Dataset': 'Women',
                     'Baseline': round(b_w * 100, 1), 'Midline': round(m_w * 100, 1)})

    ls = w_data['lifeskills_agree']
    rows.append({'Indicator': 'Life Skills (avg)', 'Dataset': 'Women',
                 'Baseline': round(ls['Baseline'].mean() * 100, 1),
                 'Midline': round(ls['Midline'].mean() * 100, 1)})

    di = w_data['decision_influence']
    rows.append({'Indicator': 'Decision Influence', 'Dataset': 'Women',
                 'Baseline': round(di['Baseline'].mean() * 100, 1),
                 'Midline': round(di['Midline'].mean() * 100, 1)})

    # Men indicators (if available)
    if m_data is not None:
        for label, df_key, resp_col, resp_val in [
            ('CC Awareness (Men)', 'cc_heard', 'Response', 'Yes'),
            ('NbS Awareness (Men)', 'nbs_heard', 'Response', 'Yes'),
        ]:
            df = m_data[df_key]
            b_m = df.loc[df[resp_col] == resp_val, 'Baseline'].values[0]
            m_m = df.loc[df[resp_col] == resp_val, 'Midline'].values[0]
            rows.append({'Indicator': label, 'Dataset': 'Men',
                         'Baseline': round(b_m * 100, 1), 'Midline': round(m_m * 100, 1)})

        rj = m_data['roles_should_joint']
        rows.append({'Indicator': 'Joint Roles (Should)', 'Dataset': 'Men',
                     'Baseline': round(rj['Baseline'].mean() * 100, 1),
                     'Midline': round(rj['Midline'].mean() * 100, 1)})

        dj = m_data['decision_should_joint']
        rows.append({'Indicator': 'Joint Decisions (Should)', 'Dataset': 'Men',
                     'Baseline': round(dj['Baseline'].mean() * 100, 1),
                     'Midline': round(dj['Midline'].mean() * 100, 1)})

        m_sn = m_data['socialnorms_agree']
        m_harmful = m_sn[~m_sn['Norm'].str.contains(
            'Planting Crops|Restoring Ecosystems|Express Emotions', regex=True)]
        rows.append({'Indicator': 'Harmful Norms (Men)', 'Dataset': 'Men',
                     'Baseline': round(m_harmful['Baseline'].mean() * 100, 1),
                     'Midline': round(m_harmful['Midline'].mean() * 100, 1)})

        # Men's support for women in NbS (average across mangrove, seaweed, forest)
        support_bl, support_ml = [], []
        for key in ['mangrove_support', 'seaweed_support', 'forest_support']:
            df = m_data[key]
            yes_rows = df[df['Response'] == 'Yes']
            bl_v = float(yes_rows['Baseline'].values[0]) if len(yes_rows) else 0.0
            ml_v = float(yes_rows['Midline'].values[0]) if len(yes_rows) else 0.0
            support_bl.append(bl_v)
            support_ml.append(ml_v)
        rows.append({'Indicator': 'NbS Support for Women', 'Dataset': 'Men',
                     'Baseline': round(sum(support_bl) / len(support_bl) * 100, 1),
                     'Midline': round(sum(support_ml) / len(support_ml) * 100, 1)})

    return rows


def _make_slope_chart(data_tuples, title):
    """Create a slope / parallel coordinates chart showing BL→ML trends.

    data_tuples: list of (label, baseline_pct, midline_pct)
    """
    fig = go.Figure()
    for label, bl, ml in data_tuples:
        change = ml - bl
        color = COLORS['good'] if change >= 0 else COLORS['danger']
        # Line connecting BL to ML
        fig.add_trace(go.Scatter(
            x=['Baseline', 'Midline'],
            y=[bl, ml],
            mode='lines+markers+text',
            line=dict(color=color, width=2.5),
            marker=dict(size=9, color=color, line=dict(width=1.5, color='white')),
            text=[f"{bl:.1f}%", f"{ml:.1f}%"],
            textposition=['middle left', 'middle right'],
            textfont=dict(size=10, color=color),
            name=label,
            hovertemplate=f'<b>{label}</b><br>%{{x}}: %{{y:.1f}}%<br>Change: {change:+.1f}pp<extra></extra>'
        ))
    fig.update_layout(
        title=title,
        height=380,
        xaxis=dict(tickvals=['Baseline', 'Midline'], tickfont=dict(size=13, color='#333')),
        yaxis_title='Percentage (%)',
        legend=dict(orientation='v', yanchor='top', y=1, x=1.02, font=dict(size=10)),
        font=dict(size=13, color='#333'),
        title_font=dict(size=16, color='#222'),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=50, r=120, t=60, b=20),
    )
    return fig


def render_insights_tab(f_data, w_data, m_data=None):
    """Render the Insights tab with automated analysis across all datasets."""

    st.markdown("""<div class="section-narrative">
    <strong>Automated Insights:</strong> This tab generates data-driven insights by analyzing
    trends, changes, and patterns across the Forestry Conservation Groups, Women's Survey,
    and Men's Survey datasets. Insights are automatically derived from Baseline-to-Midline comparisons.
    </div>""", unsafe_allow_html=True)

    # Summary counters
    f_insights = _generate_forestry_insights(f_data)
    w_insights = _generate_women_insights(w_data)
    m_insights = _generate_men_insights(m_data) if m_data is not None else []
    cc_insights = _generate_cross_cutting_insights(f_data, w_data, m_data)

    all_insights = f_insights + w_insights + m_insights + cc_insights
    positive_count = sum(1 for _, _, t in all_insights if t == "positive")
    warning_count = sum(1 for _, _, t in all_insights if t in ("warning", "negative"))
    neutral_count = sum(1 for _, _, t in all_insights if t == "neutral")
    total = len(all_insights)

    # KPI summary
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Insights", total)
    c2.metric("Positive Trends", positive_count)
    c3.metric("Areas of Concern", warning_count)
    c4.metric("Cross-cutting", len(cc_insights))

    st.markdown("---")
    nav_items = ['Trend Overview', 'Forestry Insights', 'Women Survey Insights']
    if m_data is not None:
        nav_items.append('Men Survey Insights')
    nav_items.extend(['Cross-Cutting Insights', 'Change Heatmap', 'Recommendations'])
    _quick_nav_pills(nav_items)

    # ====================================================================
    # TREND OVERVIEW — Donut + Dumbbell Chart
    # ====================================================================
    _section_header('', 'Trend Overview', 'At a Glance')

    # --- Build master indicator table used across multiple charts ---
    indicator_rows = _build_indicator_table(f_data, w_data, m_data)
    ind_df = pd.DataFrame(indicator_rows)
    ind_df['Change'] = round(ind_df['Midline'] - ind_df['Baseline'], 1)
    ind_df['Direction'] = ind_df['Change'].apply(
        lambda x: 'Improving' if x > 0.5 else ('Declining' if x < -0.5 else 'Stable'))

    # --- Row 1: Donut (trend distribution) + Dumbbell overview ---
    ov_col1, ov_col2 = st.columns([1, 2])

    with ov_col1:
        # Trend classification donut
        trend_counts = ind_df['Direction'].value_counts()
        donut_colors = {'Improving': COLORS['good'], 'Declining': COLORS['danger'], 'Stable': '#9E9E9E'}
        fig_donut = go.Figure(go.Pie(
            labels=trend_counts.index,
            values=trend_counts.values,
            hole=0.55,
            marker=dict(colors=[donut_colors.get(d, '#888') for d in trend_counts.index]),
            textinfo='label+value',
            textfont=dict(size=13),
            hovertemplate='%{label}: %{value} indicators<extra></extra>'
        ))
        fig_donut.update_layout(
            title="Indicator Trend Distribution",
            height=350,
            font=dict(size=13, color='#333'),
            title_font=dict(size=16, color='#222'),
            showlegend=False,
            margin=dict(l=10, r=10, t=50, b=10),
            annotations=[dict(text=f"{len(ind_df)}<br>Indicators", x=0.5, y=0.5,
                               font=dict(size=16, color='#333', family='Arial'),
                               showarrow=False)]
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with ov_col2:
        # Dumbbell / slope chart: Baseline dot → Midline dot with connecting line
        dumb_df = ind_df.sort_values('Change', ascending=True).reset_index(drop=True)
        fig_dumb = go.Figure()

        # Connecting lines (drawn first so dots sit on top)
        for i, row in dumb_df.iterrows():
            line_color = COLORS['good'] if row['Change'] >= 0 else COLORS['danger']
            fig_dumb.add_trace(go.Scatter(
                x=[row['Baseline'], row['Midline']],
                y=[row['Indicator'], row['Indicator']],
                mode='lines',
                line=dict(color=line_color, width=2.5),
                showlegend=False,
                hoverinfo='skip'
            ))
        # Baseline dots
        fig_dumb.add_trace(go.Scatter(
            x=dumb_df['Baseline'], y=dumb_df['Indicator'],
            mode='markers',
            marker=dict(size=10, color=COLORS['baseline'], symbol='circle',
                        line=dict(width=1.5, color='white')),
            name='Baseline',
            hovertemplate='%{y}<br>Baseline: %{x:.1f}%<extra></extra>'
        ))
        # Midline dots
        fig_dumb.add_trace(go.Scatter(
            x=dumb_df['Midline'], y=dumb_df['Indicator'],
            mode='markers',
            marker=dict(size=10, color=COLORS['midline'], symbol='diamond',
                        line=dict(width=1.5, color='white')),
            name='Midline',
            hovertemplate='%{y}<br>Midline: %{x:.1f}%<extra></extra>'
        ))
        fig_dumb.update_layout(
            title="Baseline to Midline Shift (Dumbbell Chart)",
            height=max(420, len(dumb_df) * 30),
            xaxis_title="Percentage (%)",
            yaxis=dict(categoryorder='trace'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, x=0.5, xanchor='center'),
            font=dict(size=13, color='#333'),
            title_font=dict(size=16, color='#222'),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=60, b=20),
        )
        st.plotly_chart(fig_dumb, use_container_width=True)

    st.markdown("---")

    # ====================================================================
    # FORESTRY INSIGHTS + Domain Radar Trend
    # ====================================================================
    _section_header('', 'Forestry Conservation Insights', 'Community Level')

    # Forestry Domain Radar — BL vs ML overlay
    fd = f_data['functionality_domain']
    domains = ['Management', 'Gender', 'Effectiveness', 'Overall']
    bl_vals = [fd.loc[fd['Timepoint'] == 'Baseline', d].values[0] for d in domains]
    ml_vals = [fd.loc[fd['Timepoint'] == 'Midline', d].values[0] for d in domains]

    rad_col1, rad_col2 = st.columns([1, 1])
    with rad_col1:
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=bl_vals + [bl_vals[0]],
            theta=domains + [domains[0]],
            name='Baseline',
            fill='toself',
            fillcolor='rgba(66,133,244,0.12)',
            line=dict(color=COLORS['baseline'], width=2.5),
            marker=dict(size=7)
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=ml_vals + [ml_vals[0]],
            theta=domains + [domains[0]],
            name='Midline',
            fill='toself',
            fillcolor='rgba(52,168,83,0.12)',
            line=dict(color=COLORS['midline'], width=2.5),
            marker=dict(size=7)
        ))
        fig_radar.update_layout(
            title="Domain Score Trend (Radar)",
            polar=dict(radialaxis=dict(visible=True, range=[0, max(max(bl_vals), max(ml_vals)) * 1.15],
                                        tickfont=dict(size=11))),
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=-0.15, x=0.5, xanchor='center'),
            height=380,
            font=dict(size=13, color='#333'),
            title_font=dict(size=16, color='#222'),
            margin=dict(l=60, r=60, t=60, b=40),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with rad_col2:
        # Forestry slope chart — selected key indicators
        f_slope_data = []
        # Functionality threshold
        ft = f_data['functionality_threshold']
        bl_60 = ft.loc[ft['Timepoint'] == 'Baseline', 'Functional_60_pct'].values[0]
        ml_60 = ft.loc[ft['Timepoint'] == 'Midline', 'Functional_60_pct'].values[0]
        f_slope_data.append(('Functionality >=60%', bl_60 * 100 if bl_60 <= 1 else bl_60,
                             ml_60 * 100 if ml_60 <= 1 else ml_60))
        # Women leadership
        wl = f_data['women_leadership']
        sig_bl = wl.loc[wl['Category'] == 'Significant Leadership', 'Baseline'].values[0]
        sig_ml = wl.loc[wl['Category'] == 'Significant Leadership', 'Midline'].values[0]
        f_slope_data.append(('Women Leadership', sig_bl * 100 if sig_bl <= 1 else sig_bl,
                             sig_ml * 100 if sig_ml <= 1 else sig_ml))
        # Training coverage
        tc = f_data['training_coverage']
        tc_bl = tc.loc[tc['Category'] == 'Most Members', 'Baseline'].values[0]
        tc_ml = tc.loc[tc['Category'] == 'Most Members', 'Midline'].values[0]
        f_slope_data.append(('Training (Most)', tc_bl * 100 if tc_bl <= 1 else tc_bl,
                             tc_ml * 100 if tc_ml <= 1 else tc_ml))
        # Income gen
        ig = f_data['income_gen']
        ig_bl = ig.loc[ig['Category'] == 'Yes', 'Baseline'].values[0]
        ig_ml = ig.loc[ig['Category'] == 'Yes', 'Midline'].values[0]
        f_slope_data.append(('Income Gen', ig_bl * 100 if ig_bl <= 1 else ig_bl,
                             ig_ml * 100 if ig_ml <= 1 else ig_ml))
        # Agroforestry
        af = f_data['agroforestry']
        af_bl = af.loc[af['Category'] == 'Yes', 'Baseline'].values[0]
        af_ml = af.loc[af['Category'] == 'Yes', 'Midline'].values[0]
        f_slope_data.append(('Agroforestry', af_bl * 100 if af_bl <= 1 else af_bl,
                             af_ml * 100 if af_ml <= 1 else af_ml))

        fig_fslope = _make_slope_chart(f_slope_data, "Forestry Key Indicator Trends")
        st.plotly_chart(fig_fslope, use_container_width=True)

    # Insight cards
    for title, body, trend in f_insights:
        _insight_card(title, body, trend)

    st.markdown("---")

    # ====================================================================
    # WOMEN SURVEY INSIGHTS + Empowerment Trend Charts
    # ====================================================================
    _section_header('', "Women's Survey Insights", 'Household Level')

    # Women empowerment slope chart + life skills domain trend
    we_col1, we_col2 = st.columns([1, 1])

    with we_col1:
        # Women's key indicators slope chart
        w_slope_data = []
        for label, df_key, resp_col, resp_val in [
            ('CC Awareness', 'cc_heard', 'Response', 'Yes'),
            ('NbS Awareness', 'nbs_heard', 'Response', 'Yes'),
            ('Personal Savings', 'personal_saving', 'Response', 'Yes'),
            ('Prep Knowledge', 'prep_knowledge', 'Response', 'Yes'),
        ]:
            df = w_data[df_key]
            b_w = df.loc[df[resp_col] == resp_val, 'Baseline'].values[0] * 100
            m_w = df.loc[df[resp_col] == resp_val, 'Midline'].values[0] * 100
            w_slope_data.append((label, b_w, m_w))

        # Decision influence avg
        di = w_data['decision_influence']
        w_slope_data.append(('Decision Influence', di['Baseline'].mean() * 100, di['Midline'].mean() * 100))

        # Life skills avg
        ls = w_data['lifeskills_agree']
        w_slope_data.append(('Life Skills', ls['Baseline'].mean() * 100, ls['Midline'].mean() * 100))

        fig_wslope = _make_slope_chart(w_slope_data, "Women's Key Indicator Trends")
        st.plotly_chart(fig_wslope, use_container_width=True)

    with we_col2:
        # Life skills by domain — grouped bar with trend lines
        ls_all = w_data['lifeskills_agree'].copy()
        # Attempt to group by domain if Statement column contains domain hints
        domain_map = {}
        for _, row in ls_all.iterrows():
            stmt = str(row.get('Statement', ''))
            if any(k in stmt.lower() for k in ['confident', 'proud', 'worth', 'self']):
                domain_map[stmt] = 'Self Esteem'
            elif any(k in stmt.lower() for k in ['future', 'plan', 'goal', 'aspir']):
                domain_map[stmt] = 'Aspirations'
            else:
                domain_map[stmt] = 'Leadership'

        # Build domain averages
        ls_all['Domain'] = ls_all['Statement'].map(domain_map)
        domain_avg = ls_all.groupby('Domain')[['Baseline', 'Midline']].mean().reset_index()

        # Add communication and conflict as extra domains
        comm = w_data['communication_agree']
        conf = w_data['conflict_agree']
        extra_domains = [
            {'Domain': 'Communication', 'Baseline': comm['Baseline'].mean(), 'Midline': comm['Midline'].mean()},
            {'Domain': 'Conflict Res.', 'Baseline': conf['Baseline'].mean(), 'Midline': conf['Midline'].mean()},
        ]
        domain_avg = pd.concat([domain_avg, pd.DataFrame(extra_domains)], ignore_index=True)
        domain_avg['BL_pct'] = domain_avg['Baseline'] * 100
        domain_avg['ML_pct'] = domain_avg['Midline'] * 100
        domain_avg['Change'] = round(domain_avg['ML_pct'] - domain_avg['BL_pct'], 1)

        fig_dom = go.Figure()
        fig_dom.add_trace(go.Bar(
            x=domain_avg['Domain'], y=domain_avg['BL_pct'],
            name='Baseline', marker_color=COLORS['baseline'],
            text=domain_avg['BL_pct'].apply(lambda x: f"{x:.1f}%"), textposition='auto'
        ))
        fig_dom.add_trace(go.Bar(
            x=domain_avg['Domain'], y=domain_avg['ML_pct'],
            name='Midline', marker_color=COLORS['midline'],
            text=domain_avg['ML_pct'].apply(lambda x: f"{x:.1f}%"), textposition='auto'
        ))
        # Trend line connecting midline values
        fig_dom.add_trace(go.Scatter(
            x=domain_avg['Domain'], y=domain_avg['ML_pct'],
            mode='lines+markers',
            name='Midline Trend',
            line=dict(color=COLORS['card_value'], width=2.5, dash='dot'),
            marker=dict(size=8, symbol='diamond'),
            yaxis='y'
        ))
        fig_dom.update_layout(
            title="Skills Domain Trends (BL vs ML)",
            barmode='group', height=380,
            yaxis_title='Agree/Strongly Agree (%)',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, x=0.5, xanchor='center'),
            font=dict(size=13, color='#333'),
            title_font=dict(size=16, color='#222'),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=60, b=20),
        )
        st.plotly_chart(fig_dom, use_container_width=True)

    # Insight cards
    for title, body, trend in w_insights:
        _insight_card(title, body, trend)

    st.markdown("---")

    # ====================================================================
    # MEN SURVEY INSIGHTS + Key Indicator Trends
    # ====================================================================
    if m_data is not None and m_insights:
        _section_header('', "Men's Survey Insights", 'Household Level')

        me_col1, me_col2 = st.columns([1, 1])
        with me_col1:
            # Men's key indicators slope chart
            m_slope_data = []
            m_cc = m_data['cc_heard']
            m_slope_data.append(('CC Awareness',
                                m_cc.loc[m_cc['Response']=='Yes','Baseline'].values[0]*100,
                                m_cc.loc[m_cc['Response']=='Yes','Midline'].values[0]*100))
            m_nbs = m_data['nbs_heard']
            m_slope_data.append(('NbS Awareness',
                                m_nbs.loc[m_nbs['Response']=='Yes','Baseline'].values[0]*100,
                                m_nbs.loc[m_nbs['Response']=='Yes','Midline'].values[0]*100))
            m_rj = m_data['roles_should_joint']
            m_slope_data.append(('Joint Roles (Should)',
                                m_rj['Baseline'].mean()*100, m_rj['Midline'].mean()*100))
            m_dj = m_data['decision_should_joint']
            m_slope_data.append(('Joint Decisions (Should)',
                                m_dj['Baseline'].mean()*100, m_dj['Midline'].mean()*100))
            m_sn = m_data['socialnorms_agree']
            m_harmful = m_sn[~m_sn['Norm'].str.contains(
                'Planting Crops|Restoring Ecosystems|Express Emotions', regex=True)]
            m_slope_data.append(('Harmful Norms',
                                m_harmful['Baseline'].mean()*100, m_harmful['Midline'].mean()*100))

            fig_mslope = _make_slope_chart(m_slope_data, "Men's Key Indicator Trends")
            st.plotly_chart(fig_mslope, use_container_width=True)

        with me_col2:
            # Men's NbS support comparison across sectors
            sectors = ['mangrove_support', 'seaweed_support', 'forest_support']
            sector_labels = ['Mangrove', 'Seaweed', 'Forest Mgmt']
            sup_bl_vals, sup_ml_vals = [], []
            for key in sectors:
                df = m_data[key]
                yes_bl = df.loc[df['Response']=='Yes','Baseline'].values[0]*100 if len(df[df['Response']=='Yes']) else 0
                yes_ml = df.loc[df['Response']=='Yes','Midline'].values[0]*100 if len(df[df['Response']=='Yes']) else 0
                sup_bl_vals.append(yes_bl)
                sup_ml_vals.append(yes_ml)

            fig_msup = go.Figure()
            fig_msup.add_trace(go.Bar(x=sector_labels, y=sup_bl_vals, name='Baseline',
                                      marker_color=COLORS['baseline'],
                                      text=[f"{v:.1f}%" for v in sup_bl_vals], textposition='auto'))
            fig_msup.add_trace(go.Bar(x=sector_labels, y=sup_ml_vals, name='Midline',
                                      marker_color=COLORS['midline'],
                                      text=[f"{v:.1f}%" for v in sup_ml_vals], textposition='auto'))
            fig_msup.update_layout(
                title="Men Supporting Women in NbS (% Yes)",
                barmode='group', height=380, yaxis_title='%',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, x=0.5, xanchor='center'),
                font=dict(size=13, color='#333'),
                title_font=dict(size=16, color='#222'),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=60, b=20),
            )
            st.plotly_chart(fig_msup, use_container_width=True)

        for title, body, trend in m_insights:
            _insight_card(title, body, trend)

        st.markdown("---")

    # ====================================================================
    # CROSS-CUTTING INSIGHTS + Performance Quadrant
    # ====================================================================
    _section_header('', 'Cross-Cutting Insights', 'Integrated')

    # Performance Quadrant Scatter — Midline level (x) vs Change (y)
    st.markdown("""<div class="section-narrative">
    <strong>Performance Quadrant:</strong> Each dot is one indicator. The x-axis shows
    the current (Midline) level, the y-axis shows Baseline-to-Midline change. Quadrants
    help identify high performers, rising stars, areas at risk, and stagnating indicators.
    </div>""", unsafe_allow_html=True)

    fig_quad = go.Figure()

    # Separate by dataset for color coding
    for ds, color, symbol in [('Forestry', COLORS['baseline'], 'circle'),
                               ('Women', COLORS['midline'], 'diamond'),
                               ('Men', '#FF9800', 'square')]:
        subset = ind_df[ind_df['Dataset'] == ds]
        fig_quad.add_trace(go.Scatter(
            x=subset['Midline'],
            y=subset['Change'],
            mode='markers+text',
            marker=dict(size=12, color=color, symbol=symbol,
                        line=dict(width=1.5, color='white')),
            text=subset['Indicator'],
            textposition='top center',
            textfont=dict(size=10),
            name=ds,
            hovertemplate='<b>%{text}</b><br>Midline: %{x:.1f}%<br>Change: %{y:+.1f}pp<extra></extra>'
        ))

    # Quadrant reference lines
    median_ml = ind_df['Midline'].median()
    fig_quad.add_hline(y=0, line_dash='dash', line_color='#999', line_width=1)
    fig_quad.add_vline(x=median_ml, line_dash='dash', line_color='#999', line_width=1)

    # Quadrant labels
    y_range = max(abs(ind_df['Change'].min()), abs(ind_df['Change'].max()))
    x_max = ind_df['Midline'].max()
    x_min = ind_df['Midline'].min()
    annotations = [
        dict(x=x_min + (median_ml - x_min) * 0.5, y=y_range * 0.85,
             text="Needs Attention", showarrow=False,
             font=dict(size=11, color='#C62828'), bgcolor='rgba(255,235,238,0.7)'),
        dict(x=median_ml + (x_max - median_ml) * 0.5, y=y_range * 0.85,
             text="High Performers", showarrow=False,
             font=dict(size=11, color='#2E7D32'), bgcolor='rgba(232,245,233,0.7)'),
        dict(x=x_min + (median_ml - x_min) * 0.5, y=-y_range * 0.85,
             text="At Risk", showarrow=False,
             font=dict(size=11, color='#E65100'), bgcolor='rgba(255,243,224,0.7)'),
        dict(x=median_ml + (x_max - median_ml) * 0.5, y=-y_range * 0.85,
             text="Declining Leaders", showarrow=False,
             font=dict(size=11, color='#37474F'), bgcolor='rgba(236,239,241,0.7)'),
    ]
    fig_quad.update_layout(
        title="Performance Quadrant: Current Level vs Change",
        height=480,
        xaxis_title="Midline Level (%)",
        yaxis_title="Change (pp)",
        legend=dict(orientation='h', yanchor='bottom', y=1.02, x=0.5, xanchor='center'),
        font=dict(size=13, color='#333'),
        title_font=dict(size=16, color='#222'),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=60, b=20),
        annotations=annotations,
    )
    st.plotly_chart(fig_quad, use_container_width=True)

    # Insight cards
    for title, body, trend in cc_insights:
        _insight_card(title, body, trend)

    st.markdown("---")

    # ====================================================================
    # CHANGE HEATMAP + Waterfall
    # ====================================================================
    _section_header('', 'Indicator Change Heatmap', 'Overview')
    st.markdown("""<div class="section-narrative">
    A visual summary of percentage-point changes across key indicators from both datasets.
    Green cells indicate positive change; red cells indicate areas that declined.
    </div>""", unsafe_allow_html=True)

    heatmap_df = ind_df.copy()

    # --- Butterfly chart: BL on left, ML on right ---
    hm_sorted = heatmap_df.sort_values('Change')
    hm_col1, hm_col2 = st.columns([1, 1])

    with hm_col1:
        # Diverging bar chart of changes
        colors_bar = [COLORS['good'] if v >= 0 else COLORS['danger'] for v in hm_sorted['Change']]
        fig_hm = go.Figure()
        fig_hm.add_trace(go.Bar(
            y=hm_sorted['Indicator'] + ' (' + hm_sorted['Dataset'] + ')',
            x=hm_sorted['Change'],
            orientation='h',
            marker_color=colors_bar,
            text=hm_sorted['Change'].apply(lambda x: f"{x:+.1f} pp"),
            textposition='auto'
        ))
        fig_hm.update_layout(
            title="Baseline-to-Midline Change",
            height=max(400, len(heatmap_df) * 32),
            xaxis_title="Change (pp)",
            yaxis=dict(categoryorder='trace'),
            font=dict(size=13, color='#333'),
            title_font=dict(size=16, color='#222'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=60, b=20),
        )
        st.plotly_chart(fig_hm, use_container_width=True)

    with hm_col2:
        # Waterfall chart — cumulative gain/loss
        wf_sorted = heatmap_df.sort_values('Change', ascending=False).reset_index(drop=True)
        wf_colors = [COLORS['good'] if v >= 0 else COLORS['danger'] for v in wf_sorted['Change']]
        fig_wf = go.Figure(go.Waterfall(
            x=wf_sorted['Indicator'],
            y=wf_sorted['Change'],
            measure=['relative'] * len(wf_sorted),
            text=wf_sorted['Change'].apply(lambda x: f"{x:+.1f}"),
            textposition='outside',
            increasing=dict(marker=dict(color=COLORS['good'])),
            decreasing=dict(marker=dict(color=COLORS['danger'])),
            connector=dict(line=dict(color='#ccc', width=1)),
        ))
        fig_wf.update_layout(
            title="Cumulative Change Waterfall",
            height=max(400, len(heatmap_df) * 32),
            yaxis_title="Change (pp)",
            font=dict(size=13, color='#333'),
            title_font=dict(size=16, color='#222'),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=60, b=60),
            xaxis=dict(tickangle=-45),
        )
        st.plotly_chart(fig_wf, use_container_width=True)

    # Data table
    with st.expander("View Full Indicator Change Table"):
        display_df = heatmap_df[['Indicator', 'Dataset', 'Baseline', 'Midline', 'Change']].copy()
        display_df.columns = ['Indicator', 'Dataset', 'Baseline', 'Midline', 'Change (pp)']
        st.dataframe(
            display_df.style.map(
                lambda v: 'color: #2E7D32; font-weight: 700' if isinstance(v, (int, float)) and v > 0
                else ('color: #C62828; font-weight: 700' if isinstance(v, (int, float)) and v < 0 else ''),
                subset=['Change (pp)']
            ),
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("---")

    # ====================================================================
    # KEY RECOMMENDATIONS
    # ====================================================================
    _section_header('', 'Key Recommendations', 'Action Items')

    # Auto-generate recommendations based on the insights
    recs = []
    # Check for negative trends
    all_insights_recs = f_insights + w_insights + m_insights + cc_insights
    neg_areas = [title for title, _, trend in all_insights_recs if trend in ('negative', 'warning')]
    pos_areas = [title for title, _, trend in all_insights_recs if trend == 'positive']

    if any('Functionality' in a for a in neg_areas):
        recs.append(("Strengthen Institutional Capacity",
                     "Targeted support for groups below the functionality threshold — mentorship, "
                     "refresher training on governance, and structured follow-up visits."))
    if any('Leadership' in a or 'Gender' in a for a in neg_areas):
        recs.append(("Accelerate Gender Mainstreaming",
                     "Prioritize women's leadership development within forestry groups, and ensure "
                     "gender considerations are embedded in all planning processes."))
    if any('Savings' in a or 'Income' in a or 'Economic' in a for a in neg_areas):
        recs.append(("Expand Financial Inclusion",
                     "Link VSLA/savings groups to the forest-income value chain. Support women's "
                     "personal savings through financial literacy training and digital payment platforms."))
    if any('Norm' in a for a in neg_areas):
        recs.append(("Address Harmful Social Norms",
                     "Continue community dialogues on gender norms, using evidence from this dashboard "
                     "to show how norms affect women's participation and community outcomes."))
    if any('Care Work' in a or 'Time' in a for a in neg_areas):
        recs.append(("Reduce Women's Time Poverty",
                     "Invest in time-saving technologies (water access, energy-efficient stoves) "
                     "and promote equitable household labour-sharing norms."))
    if any('Prepared' in a or 'Climate' in a or 'NbS' in a for a in neg_areas):
        recs.append(("Scale Climate & DRR Programming",
                     "Expand community-based disaster preparedness planning and integrate NbS training "
                     "into both forestry group activities and women's empowerment programs."))
    if any("Men's" in a and ('Norm' in a or 'Support' in a or 'Role' in a) for a in neg_areas):
        recs.append(("Engage Men as Change Agents",
                     "Strengthen male engagement strategies — community dialogues, role-model campaigns, "
                     "and couple-based interventions to shift attitudes on joint roles and NbS support."))
    if any("Decision" in a and "Practice" in a for a in neg_areas):
        recs.append(("Close the Attitudes-Practice Gap",
                     "While men increasingly say decisions should be joint, actual practice lags behind. "
                     "Facilitate structured household visioning exercises to translate norms into behaviour."))

    # Always add these broad recommendations
    recs.append(("Leverage Positive Trends",
                 f"Build on the {len(pos_areas)} positive trends identified — use these as evidence for "
                 f"donor reporting and community motivation. Document success stories in areas "
                 f"showing clear improvement."))
    recs.append(("Integrated M&E Approach",
                 "Continue tracking community-level (forestry), women's, and men's indicators together. "
                 "The cross-cutting insights show that progress at one level supports the other."))

    for title, body in recs:
        _insight_card(title, body, "neutral")


# ============================================================================
# CROSS-DATASET SYNTHESIS VIEW
# ============================================================================

def render_synthesis_view(f_data, w_data, m_data=None):
    """Combined overview of all datasets — key headline indicators."""
    st.markdown("""<div class="section-narrative">
    <strong> Cross-Dataset Synthesis:</strong> A combined overview comparing headline indicators
    from all programme datasets — Forestry Conservation Groups (community-level), Women's Survey,
    and Men's Survey (household-level). This view highlights key programme-wide trends.
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

    # ---- Men Survey Headline KPIs ----
    if m_data is not None:
        st.markdown('<h3> Men\'s Survey — Headlines</h3>', unsafe_allow_html=True)

        # CC heard
        m_cc_bl = m_data['cc_heard'].loc[m_data['cc_heard']['Response']=='Yes','Baseline'].values[0]
        m_cc_ml = m_data['cc_heard'].loc[m_data['cc_heard']['Response']=='Yes','Midline'].values[0]
        # NbS heard
        m_nbs_bl = m_data['nbs_heard'].loc[m_data['nbs_heard']['Response']=='Yes','Baseline'].values[0]
        m_nbs_ml = m_data['nbs_heard'].loc[m_data['nbs_heard']['Response']=='Yes','Midline'].values[0]
        # Roles should joint avg
        m_rj_bl = m_data['roles_should_joint']['Baseline'].mean()
        m_rj_ml = m_data['roles_should_joint']['Midline'].mean()
        # Decision should joint avg
        m_dj_bl = m_data['decision_should_joint']['Baseline'].mean()
        m_dj_ml = m_data['decision_should_joint']['Midline'].mean()

        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.markdown(f"""<div class="kpi-card">
            <h3>CC Awareness (Men)</h3>
            <div class="value">{m_cc_ml*100:.0f}%</div>
            <div class="delta-{'positive' if m_cc_ml>=m_cc_bl else 'negative'}">{(m_cc_ml-m_cc_bl)*100:+.1f}pp</div>
        </div>""", unsafe_allow_html=True)
        mc2.markdown(f"""<div class="kpi-card">
            <h3>NbS Awareness (Men)</h3>
            <div class="value">{m_nbs_ml*100:.0f}%</div>
            <div class="delta-{'positive' if m_nbs_ml>=m_nbs_bl else 'negative'}">{(m_nbs_ml-m_nbs_bl)*100:+.1f}pp</div>
        </div>""", unsafe_allow_html=True)
        mc3.markdown(f"""<div class="kpi-card">
            <h3>Joint Roles (Should)</h3>
            <div class="value">{m_rj_ml*100:.0f}%</div>
            <div class="delta-{'positive' if m_rj_ml>=m_rj_bl else 'negative'}">{(m_rj_ml-m_rj_bl)*100:+.1f}pp</div>
        </div>""", unsafe_allow_html=True)
        mc4.markdown(f"""<div class="kpi-card">
            <h3>Joint Decisions (Should)</h3>
            <div class="value">{m_dj_ml*100:.0f}%</div>
            <div class="delta-{'positive' if m_dj_ml>=m_dj_bl else 'negative'}">{(m_dj_ml-m_dj_bl)*100:+.1f}pp</div>
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
        st.plotly_chart(fig_r, use_container_width=True)
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
        st.plotly_chart(fig_ls, use_container_width=True)

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
        st.plotly_chart(fig_sn, use_container_width=True)
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
        st.plotly_chart(fig_ts, use_container_width=True)

    # ---- Men vs Women comparison charts ----
    if m_data is not None:
        st.markdown('<h3>Men vs Women: Key Comparisons</h3>', unsafe_allow_html=True)
        cmp1, cmp2 = st.columns(2)
        with cmp1:
            # CC awareness comparison
            w_cc_yes_ml = cc_ml  # already computed above
            m_cc_yes_ml = m_data['cc_heard'].loc[m_data['cc_heard']['Response']=='Yes','Midline'].values[0]
            w_nbs_yes_ml = nbs_ml
            m_nbs_yes_ml = m_data['nbs_heard'].loc[m_data['nbs_heard']['Response']=='Yes','Midline'].values[0]
            cmp_df = pd.DataFrame({
                'Indicator': ['CC Awareness', 'NbS Awareness'],
                'Women (Midline)': [w_cc_yes_ml*100, w_nbs_yes_ml*100],
                'Men (Midline)': [m_cc_yes_ml*100, m_nbs_yes_ml*100],
            })
            fig_cmp = go.Figure()
            fig_cmp.add_trace(go.Bar(x=cmp_df['Indicator'], y=cmp_df['Women (Midline)'],
                                     name='Women', marker_color=COLORS['midline'],
                                     text=cmp_df['Women (Midline)'].apply(lambda x: f"{x:.1f}%"),
                                     textposition='auto'))
            fig_cmp.add_trace(go.Bar(x=cmp_df['Indicator'], y=cmp_df['Men (Midline)'],
                                     name='Men', marker_color=COLORS['baseline'],
                                     text=cmp_df['Men (Midline)'].apply(lambda x: f"{x:.1f}%"),
                                     textposition='auto'))
            fig_cmp.update_layout(title="Climate & NbS Awareness (Midline)", barmode='group',
                                  height=380, yaxis_title='%',
                                  legend=dict(orientation='h', yanchor='bottom', y=1.02),
                                  font=dict(size=13, color='#333'),
                                  title_font=dict(size=16, color='#222'),
                                  plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_cmp, use_container_width=True)

        with cmp2:
            # Social norms comparison — harmful norms average
            w_sn = w_data['socialnorms_agree'].copy()
            w_harmful = w_sn[~w_sn['Norm'].str.contains('Planting Crops|Restoring Ecosystems|Express Emotions', regex=True)]
            w_sn_bl = w_harmful['Baseline'].mean() * 100
            w_sn_ml = w_harmful['Midline'].mean() * 100
            m_sn = m_data['socialnorms_agree'].copy()
            m_harmful = m_sn[~m_sn['Norm'].str.contains('Planting Crops|Restoring Ecosystems|Express Emotions', regex=True)]
            m_sn_bl = m_harmful['Baseline'].mean() * 100
            m_sn_ml = m_harmful['Midline'].mean() * 100
            norms_df = pd.DataFrame({
                'Timepoint': ['Baseline', 'Midline'],
                'Women': [w_sn_bl, w_sn_ml],
                'Men': [m_sn_bl, m_sn_ml],
            })
            fig_norms = go.Figure()
            fig_norms.add_trace(go.Bar(x=norms_df['Timepoint'], y=norms_df['Women'],
                                       name='Women', marker_color=COLORS['midline'],
                                       text=norms_df['Women'].apply(lambda x: f"{x:.1f}%"),
                                       textposition='auto'))
            fig_norms.add_trace(go.Bar(x=norms_df['Timepoint'], y=norms_df['Men'],
                                       name='Men', marker_color=COLORS['baseline'],
                                       text=norms_df['Men'].apply(lambda x: f"{x:.1f}%"),
                                       textposition='auto'))
            fig_norms.update_layout(title="Harmful Social Norms (Avg Agree %)", barmode='group',
                                    height=380, yaxis_title='Agree/Strongly Agree (%)',
                                    legend=dict(orientation='h', yanchor='bottom', y=1.02),
                                    font=dict(size=13, color='#333'),
                                    title_font=dict(size=16, color='#222'),
                                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_norms, use_container_width=True)

    st.markdown("""<div class="section-narrative" style="margin-top:1rem;">
    <strong>Navigate deeper:</strong> Use the sidebar to select <em>Forestry Groups</em>,
    <em>Women Survey</em>, or <em>Men Survey</em> for detailed breakdowns across all thematic areas.
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
        ["Combined Overview", "Forestry Groups", "Women Survey", "Men Survey",
         "GJJ KAP \u2013 Women (Baseline/Endline)", "Insights"],
        index=0,
        help="Combined Overview shows headline KPIs from all datasets side by side."
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
    elif dataset == "Insights":
        st.sidebar.markdown("**Quick Navigate**")
        st.sidebar.markdown("""
        <div class="sidebar-section">
            <span class="sidebar-nav-link">Forestry Insights</span>
            <span class="sidebar-nav-link">Women Survey Insights</span>
            <span class="sidebar-nav-link">Men Survey Insights</span>
            <span class="sidebar-nav-link">Cross-Cutting Insights</span>
            <span class="sidebar-nav-link">Indicator Change Heatmap</span>
            <span class="sidebar-nav-link">Recommendations</span>
        </div>
        """, unsafe_allow_html=True)
    elif dataset == "Men Survey":
        st.sidebar.markdown("**Quick Navigate**")
        st.sidebar.markdown("""
        <div class="sidebar-section">
            <span class="sidebar-nav-link">Household Profile</span>
            <span class="sidebar-nav-link">Climate & NbS</span>
            <span class="sidebar-nav-link">Support for Women in NbS</span>
            <span class="sidebar-nav-link">Roles & Time Use</span>
            <span class="sidebar-nav-link">Decision-Making</span>
            <span class="sidebar-nav-link">Social Norms</span>
        </div>
        """, unsafe_allow_html=True)
    elif dataset == "GJJ KAP \u2013 Women (Baseline/Endline)":
        st.sidebar.markdown("**Quick Navigate**")
        st.sidebar.markdown("""
        <div class="sidebar-section">
            <span class="sidebar-nav-link">SELF: Confidence & Compassion</span>
            <span class="sidebar-nav-link">Relational Wellbeing</span>
            <span class="sidebar-nav-link">Shared Responsibility</span>
            <span class="sidebar-nav-link">Shared Power & Decisions</span>
            <span class="sidebar-nav-link">Autonomy & Leadership</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("**Quick Navigate**")
        st.sidebar.markdown("""
        <div class="sidebar-section">
            <span class="sidebar-nav-link">Forestry Headlines</span>
            <span class="sidebar-nav-link">Women Survey Headlines</span>
            <span class="sidebar-nav-link">Men Survey Headlines</span>
            <span class="sidebar-nav-link">Comparative Snapshots</span>
            <span class="sidebar-nav-link">Men vs Women Comparisons</span>
        </div>
        """, unsafe_allow_html=True)

    st.sidebar.markdown("---")

    # ---- LOAD DATA ----
    script_dir = os.path.dirname(os.path.abspath(__file__))
    forestry_path = os.path.join(script_dir, FORESTRY_EXCEL)
    women_path = os.path.join(script_dir, WOMEN_EXCEL)
    men_path = os.path.join(script_dir, MEN_EXCEL)
    gjj_kap_path = os.path.join(script_dir, GJJ_KAP_WOMEN_EXCEL)

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

        # CSV Downloads
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Export Data**")
        st.sidebar.download_button(
            label="Download Forestry Data (CSV)",
            data=_export_data_csv(data, 'forestry'),
            file_name='forestry_data_export.csv',
            mime='text/csv',
            use_container_width=True,
        )

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

        # CSV Downloads
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Export Data**")
        st.sidebar.download_button(
            label="Download Women Survey Data (CSV)",
            data=_export_data_csv(w, 'women'),
            file_name='women_survey_data_export.csv',
            mime='text/csv',
            use_container_width=True,
        )

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

    elif dataset == "Men Survey":
        st.markdown("""<div class="main-header">
            <h1>Men's Survey Dashboard</h1>
            <p>Baseline vs Midline Assessment | Men's Perspectives on Gender, Climate &amp; NbS</p>
        </div>""", unsafe_allow_html=True)

        # Breadcrumb
        st.markdown('<div class="nav-breadcrumb"><span>COSME</span><span class="sep">›</span>'
                    '<span class="active">Men Survey</span></div>', unsafe_allow_html=True)

        m = load_men_data(men_path)

        # Sidebar sample size
        st.sidebar.markdown("**Dataset Summary**")
        st.sidebar.markdown("""
        <div class="sidebar-section">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.3rem;">
                <span style="font-size:0.82rem; color:#666;">Baseline N</span>
                <strong>661 men</strong>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:0.3rem;">
                <span style="font-size:0.82rem; color:#666;">Midline N</span>
                <strong>176 men</strong>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span style="font-size:0.82rem; color:#666;">Source File</span>
                <span style="font-size:0.75rem; color:#999;">Men Survey Excel</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # CSV Downloads
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Export Data**")
        st.sidebar.download_button(
            label="Download Men Survey Data (CSV)",
            data=_export_data_csv(m, 'men'),
            file_name='men_survey_data_export.csv',
            mime='text/csv',
            use_container_width=True,
        )

        mt1, mt2, mt3, mt4, mt5, mt6 = st.tabs([
            "Household Profile",
            "Climate Change & NbS",
            "Support for Women in NbS",
            "Roles & Time Use",
            "Decision-Making",
            "Social Norms"
        ])
        with mt1: render_men_tab1(m)
        with mt2: render_men_tab2(m)
        with mt3: render_men_tab3(m)
        with mt4: render_men_tab4(m)
        with mt5: render_men_tab5(m)
        with mt6: render_men_tab6(m)

    elif dataset == "GJJ KAP \u2013 Women (Baseline/Endline)":
        st.markdown("""<div class="main-header">
            <h1>GJJ KAP Women Dashboard</h1>
            <p>Baseline vs Endline Assessment | Knowledge, Attitudes &amp; Practices — Gender Justice Journey</p>
        </div>""", unsafe_allow_html=True)

        # Breadcrumb
        st.markdown('<div class="nav-breadcrumb"><span>COSME</span><span class="sep">\u203a</span>'
                    '<span class="active">GJJ KAP \u2013 Women</span></div>', unsafe_allow_html=True)

        gjj = load_gjj_kap_women_data(gjj_kap_path)

        # Sidebar dataset summary
        st.sidebar.markdown("**Dataset Summary**")
        st.sidebar.markdown("""
        <div class="sidebar-section">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.3rem;">
                <span style="font-size:0.82rem; color:#666;">Survey Type</span>
                <strong>KAP Women</strong>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:0.3rem;">
                <span style="font-size:0.82rem; color:#666;">Timepoints</span>
                <strong>Baseline &amp; Endline</strong>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span style="font-size:0.82rem; color:#666;">Source File</span>
                <span style="font-size:0.75rem; color:#999;">GJJ KAP Women Excel</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # CSV Download
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Export Data**")
        st.sidebar.download_button(
            label="Download GJJ KAP Women Data (CSV)",
            data=_export_data_csv(gjj, 'gjj_kap_women'),
            file_name='gjj_kap_women_data_export.csv',
            mime='text/csv',
            use_container_width=True,
        )

        gt1, gt2, gt3, gt4, gt5 = st.tabs([
            "SELF: Confidence & Compassion",
            "Relational Wellbeing",
            "Shared Responsibility",
            "Shared Power & Decisions",
            "Autonomy & Leadership"
        ])
        with gt1: render_gjj_tab1(gjj)
        with gt2: render_gjj_tab2(gjj)
        with gt3: render_gjj_tab3(gjj)
        with gt4: render_gjj_tab4(gjj)
        with gt5: render_gjj_tab5(gjj)

    elif dataset == "Insights":
        st.markdown("""<div class="main-header">
            <h1>COSME Dashboard Insights</h1>
            <p>Automated Data-Driven Insights | Forestry, Women's &amp; Men's Survey Analysis</p>
        </div>""", unsafe_allow_html=True)

        # Breadcrumb
        st.markdown('<div class="nav-breadcrumb"><span>COSME</span><span class="sep">›</span>'
                    '<span class="active">Insights</span></div>', unsafe_allow_html=True)

        f_data = load_forestry_data(forestry_path)
        w_data = load_women_data(women_path)
        m_data = load_men_data(men_path)

        st.sidebar.markdown("**Datasets Loaded**")
        st.sidebar.markdown("""
        <div class="sidebar-section">
            <div style="margin-bottom:0.3rem;">Forestry Groups (analysis)</div>
            <div style="margin-bottom:0.3rem;">Women Survey (analysis)</div>
            <div>Men Survey (analysis)</div>
        </div>
        """, unsafe_allow_html=True)

        render_insights_tab(f_data, w_data, m_data)

    else:
        # Combined Overview
        st.markdown("""<div class="main-header">
            <h1>COSME Baseline–Midline Dashboard</h1>
            <p>Integrated M&amp;E Analysis | Forestry Conservation, Women's &amp; Men's Survey</p>
        </div>""", unsafe_allow_html=True)

        # Breadcrumb
        st.markdown('<div class="nav-breadcrumb"><span class="active">COSME — Combined Overview</span></div>',
                    unsafe_allow_html=True)

        f_data = load_forestry_data(forestry_path)
        w_data = load_women_data(women_path)
        m_data = load_men_data(men_path)

        st.sidebar.markdown("**Datasets Loaded**")
        st.sidebar.markdown("""
        <div class="sidebar-section">
            <div style="margin-bottom:0.3rem;">Forestry Groups</div>
            <div style="margin-bottom:0.3rem;">Women Survey</div>
            <div>Men Survey</div>
        </div>
        """, unsafe_allow_html=True)

        render_synthesis_view(f_data, w_data, m_data)

    # ---- FOOTER ----
    st.markdown(f"""
    <div class="dashboard-footer">
        <strong>COSME Baseline–Midline Dashboard</strong><br>
        Community Forest Conservation Groups, Women's Survey, Men's Survey &amp; GJJ KAP Women | Built with Streamlit + Plotly<br>
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
# 3. Men Survey Basline_midline results.xlsx (sheet: Results Men)
# 4. GJJ KAP Women Basline_endline results.xlsx (sheet: Results KAP Women Endline)
#
# To adjust data mappings:
# - load_forestry_data(): row/col positions for forestry indicators
# - load_women_data(): row/col positions for women survey indicators
# - load_men_data(): row/col positions for men survey indicators
# - load_gjj_kap_women_data(): row/col positions for GJJ KAP women indicators
# - Each uses _val(raw, row_0based, col_0based)
#
# To add/remove indicators:
# - Add new DataFrame in the appropriate loader function
# - Add chart call in the corresponding render function
# ============================================================================
