"""
COSME Individual Topic Report Generator
Generates separate PDF reports for each programme area,
reusing shared infrastructure from generate_midline_report.py.
"""
import os, sys
from datetime import datetime

# Re-use everything from the main report generator
from generate_midline_report import (
    # Constants & config
    OUTPUT_DIR, CHART_DIR, MARGIN, PAGE_W, PAGE_H, A4,
    PRIMARY, SECONDARY, ACCENT, DARK, LIGHT_BG, TABLE_HEAD,
    EXCEEDED_C, ON_TRACK_C, NEGATIVE_C, ROW_ALT, BORDER_C,
    # Styles
    styles,
    # Chart helpers
    chart_bar_comparison, chart_horizontal_bar, chart_radar,
    chart_logframe_achievement, chart_pie,
    # Table helpers
    make_table, status_color, kpi_card_table,
    # Template helpers
    header_footer, _get_logo_drawing,
    # reportlab imports
    mm, cm, inch,
    HexColor, white, black,
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, HRFlowable,
    renderPDF,
)

os.makedirs(CHART_DIR, exist_ok=True)


# ============================================================
# MINI COVER PAGE — used for each individual report
# ============================================================
def mini_cover(canvas, doc, title, subtitle, stats_list):
    """Draw a compact cover page for individual topic reports."""
    canvas.saveState()
    # Background
    canvas.setFillColor(HexColor("#0D47A1"))
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=True)
    # Accent stripes
    canvas.setFillColor(HexColor("#1565C0"))
    canvas.rect(0, PAGE_H * 0.38, PAGE_W, PAGE_H * 0.28, fill=True)
    canvas.setFillColor(HexColor("#FF6F00"))
    canvas.rect(0, PAGE_H - 6 * mm, PAGE_W, 6 * mm, fill=True)
    canvas.rect(0, 0, PAGE_W, 4 * mm, fill=True)
    # Logo
    logo = _get_logo_drawing(width=130)
    if logo:
        renderPDF.draw(logo, canvas, (PAGE_W - logo.width) / 2, PAGE_H * 0.78)
    # Title
    canvas.setFont('Helvetica-Bold', 30)
    canvas.setFillColor(white)
    canvas.drawCentredString(PAGE_W / 2, PAGE_H * 0.62, "COSME")
    canvas.setFont('Helvetica-Bold', 24)
    canvas.drawCentredString(PAGE_W / 2, PAGE_H * 0.55, title)
    # Subtitle
    canvas.setFont('Helvetica', 14)
    canvas.setFillColor(HexColor("#B3E5FC"))
    canvas.drawCentredString(PAGE_W / 2, PAGE_H * 0.48, subtitle)
    # Date
    canvas.setFont('Helvetica-Bold', 12)
    canvas.setFillColor(HexColor("#FFB74D"))
    canvas.drawCentredString(PAGE_W / 2, PAGE_H * 0.40, f"Report Date: {datetime.now().strftime('%B %Y')}")
    # Stats boxes
    if stats_list:
        n = min(len(stats_list), 4)
        box_w, box_h, gap = 120, 50, 15
        total_w = n * box_w + (n - 1) * gap
        start_x = (PAGE_W - total_w) / 2
        for i, (val, lbl) in enumerate(stats_list[:4]):
            x = start_x + i * (box_w + gap)
            canvas.setFillColor(HexColor("#1A237E"))
            canvas.roundRect(x, PAGE_H * 0.18, box_w, box_h, 8, fill=True, stroke=False)
            canvas.setFillColor(HexColor("#FFB74D"))
            canvas.setFont('Helvetica-Bold', 18)
            canvas.drawCentredString(x + box_w / 2, PAGE_H * 0.18 + 28, val)
            canvas.setFillColor(HexColor("#B3E5FC"))
            canvas.setFont('Helvetica', 8)
            for li, line in enumerate(lbl.split('\n')):
                canvas.drawCentredString(x + box_w / 2, PAGE_H * 0.18 + 12 - li * 10, line)
    # Footer
    canvas.setFont('Helvetica', 9)
    canvas.setFillColor(HexColor("#90CAF9"))
    canvas.drawCentredString(PAGE_W / 2, PAGE_H * 0.07,
                             "Plan International Kenya — COSME & Gender Just & Justice Programme")
    canvas.restoreState()


def _build_doc(filename, story_fn, cover_title, cover_subtitle, cover_stats):
    """Build a single-topic PDF."""
    path = os.path.join(OUTPUT_DIR, filename)
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN + 8 * mm, bottomMargin=MARGIN + 5 * mm,
        title=f"COSME — {cover_title}",
        author="Plan International Kenya",
    )
    story = [Spacer(1, 1), PageBreak()]
    story_fn(story)

    def _first_page(c, d):
        mini_cover(c, d, cover_title, cover_subtitle, cover_stats)

    doc.build(story, onFirstPage=_first_page, onLaterPages=header_footer)
    print(f"  ✓  {filename}")
    return path


# ============================================================
#  SECTION BUILDERS — one per topic
# ============================================================

def _sec_women_survey(story):
    story.append(Paragraph("Women COSME Survey", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph(
        "<b>Sample Size:</b> 345 Women  |  <b>Survey Type:</b> Midline  |  <b>Location:</b> Kilifi & Kwale Counties, Kenya",
        styles['BodyText2']))
    story.append(Spacer(1, 3 * mm))
    story.append(kpi_card_table([
        ("Women Taking Loans", "79.1%", "↑ 51.1pp from 28.0%"),
        ("VSLA Participation", "98.0%", "↑ 54.4pp from 43.6%"),
        ("Climate Knowledge", "96.3%", "↑ 35.8pp from 60.5%"),
        ("Joint Decisions", "58.8%", "↑ 13.8pp from 45.0%"),
    ]))
    story.append(Spacer(1, 5 * mm))
    # Logframe
    story.append(Paragraph("Logframe Indicator Performance", styles['SubSection']))
    lf = [
        ["Indicator", "Baseline", "Target", "Midline", "Change", "Status"],
        ["1200a. Women HH/group decision involvement", "57.6%", "65.0%", "95.9%", "+38.3pp", status_color("EXCEEDED")],
        ["1200b. Women unpaid work time", "9.3 hrs", "8.3 hrs", "7.7 hrs", "-1.6 hrs", status_color("EXCEEDED")],
        ["1200c. Women access/control resources", "41.2%", "50.0%", "53.8%", "+12.6pp", status_color("EXCEEDED")],
        ["1210a. Women NbS/Econ Rights knowledge", "20.7%", "55.0%", "80.9%", "+60.2pp", status_color("EXCEEDED")],
        ["1210b. Women personal skills & confidence", "32.7%", "55.0%", "46.3%", "+13.6pp", status_color("ON TRACK")],
        ["1210c. Women perceived equal (score)", "42.1", "55.0", "64.7", "+22.6 pts", status_color("EXCEEDED")],
        ["1220a. Women actively saving in groups", "28.8%", "70.0%", "91.9%", "+63.1pp", status_color("EXCEEDED")],
        ["1220b. Women access time-saving tech", "50.8%", "80.0%", "83.1%", "+32.3pp", status_color("EXCEEDED")],
    ]
    story.append(make_table(lf, [4, 1.2, 1.2, 1.2, 1.2, 1.5]))
    story.append(Spacer(1, 5 * mm))
    # HH
    story.append(Paragraph("Household Characteristics", styles['SubSection']))
    hh = [
        ["Characteristic", "Baseline", "Midline", "Change"],
        ["Female-headed households", "51.0%", "57.7%", "+6.7pp"],
        ["Small Business (main activity)", "17.6%", "30.3%", "+12.7pp"],
        ["Agriculture", "34.8%", "38.8%", "+4.0pp"],
        ["Casual Labour", "25.5%", "11.6%", "-13.9pp"],
        ["Safe Water Access", "84.3%", "79.7%", "-4.6pp"],
        ["Toilet Facility", "70.3%", "72.5%", "+2.2pp"],
        ["Marine Location", "—", "57.2%", "—"],
        ["Terrestrial Location", "—", "42.8%", "—"],
    ]
    story.append(make_table(hh, [4, 1.5, 1.5, 1.5]))
    story.append(Spacer(1, 5 * mm))
    # Savings chart
    p = chart_bar_comparison(
        ['VSLA', 'Bank', 'MPESA', 'Informal\nGroup', 'Home'],
        [43.6, 14.5, 8.3, 6.9, 12.9],
        [98.0, 2.7, 1.7, 3.7, 0.0],
        'Women Savings Mechanisms — Baseline vs Midline', 'ws_savings')
    story.append(Image(p, width=420, height=180))
    story.append(Spacer(1, 5 * mm))
    # Shocks
    story.append(Paragraph("Shocks, Stresses & Coping Strategies", styles['SubSection']))
    shock = [
        ["Shock/Coping", "Baseline", "Midline", "Change"],
        ["Drought", "69.1%", "63.4%", "-5.7pp"],
        ["Heat/Cold Waves", "8.6%", "22.8%", "+14.2pp"],
        ["Flooding", "4.7%", "10.0%", "+5.3pp"],
        ["Very Large Impact", "32.7%", "20.0%", "-12.7pp"],
        ["Took Loan to Cope", "4.7%", "25.8%", "+21.1pp"],
        ["Used Savings", "11.2%", "15.8%", "+4.6pp"],
        ["Skipped Meals", "41.6%", "43.8%", "+2.2pp"],
    ]
    story.append(make_table(shock, [4, 1.5, 1.5, 1.5]))
    story.append(Spacer(1, 5 * mm))
    # Disaster Prep
    story.append(Paragraph("Disaster Preparedness", styles['SubSection']))
    dp = [
        ["Indicator", "Baseline", "Midline", "Change"],
        ["Know Disaster Plans", "4.7%", "37.8%", "+33.1pp"],
        ["Weather Access", "15.7%", "46.2%", "+30.5pp"],
        ["Early Warnings", "8.9%", "45.0%", "+36.1pp"],
        ["Tidal Forecasts", "10.3%", "33.1%", "+22.8pp"],
        ["Preparedness Training", "11.8%", "80.6%", "+68.8pp"],
    ]
    story.append(make_table(dp, [4, 1.5, 1.5, 1.5]))
    story.append(Spacer(1, 5 * mm))
    p_dp = chart_bar_comparison(
        ['Know Plans', 'Weather\nAccess', 'Early\nWarnings', 'Tidal\nForecasts'],
        [4.7, 15.7, 8.9, 10.3],
        [37.8, 46.2, 45.0, 33.1],
        'Women — Disaster Preparedness Improvement', 'ws_disaster')
    story.append(Image(p_dp, width=420, height=180))
    story.append(Spacer(1, 5 * mm))
    # Assets
    story.append(Paragraph("Asset Ownership & Resources", styles['SubSection']))
    assets = [
        ["Asset", "Baseline", "Midline", "Change"],
        ["Cellphones", "47.0%", "62.5%", "+15.5pp"],
        ["Solar Panels", "9.2%", "31.6%", "+22.4pp"],
        ["Cooking Stoves", "3.5%", "39.7%", "+36.2pp"],
        ["Furniture", "17.3%", "23.1%", "+5.8pp"],
        ["Land Owned", "92.7%", "73.4%", "-19.3pp"],
        ["Land Leased", "6.0%", "19.6%", "+13.6pp"],
        ["Fertilizer Purchased", "84.7%", "98.4%", "+13.7pp"],
    ]
    story.append(make_table(assets, [4, 1.5, 1.5, 1.5]))
    story.append(Spacer(1, 5 * mm))
    # Time Use
    story.append(Paragraph("Time Use & Household Responsibilities", styles['SubSection']))
    time_d = [
        ["Activity", "Baseline", "Midline", "Change"],
        ["Unpaid Care (hrs/day)", "9.3", "7.7", "-1.6 hrs"],
        ["Productive Work (hrs/day)", "4.2", "4.9", "+0.7 hrs"],
        ["Community Work (hrs/day)", "0.4", "1.8", "+1.4 hrs"],
        ["Women Cooking Alone", "87.0%", "28.8%", "-58.2pp"],
        ["Women Cleaning Alone", "85.3%", "32.5%", "-52.8pp"],
        ["Women Fetching Water Alone", "76.6%", "22.2%", "-54.4pp"],
        ["Women Childcare Alone", "70.7%", "25.3%", "-45.4pp"],
    ]
    story.append(make_table(time_d, [4, 1.5, 1.5, 1.5]))
    story.append(Spacer(1, 3 * mm))
    p_joint = chart_bar_comparison(
        ['Cooking', 'Cleaning', 'Water\nFetch', 'Firewood', 'Childcare'],
        [12.5, 13.5, 21.4, 14.4, 26.5],
        [71.3, 66.9, 77.8, 60.6, 72.2],
        'Belief That Tasks Should Be Joint — % Agreeing', 'ws_joint')
    story.append(Image(p_joint, width=420, height=180))
    story.append(Spacer(1, 5 * mm))
    # Decisions
    story.append(Paragraph("Decision Making", styles['SubSection']))
    dec = [
        ["Decision Type", "Baseline", "Midline", "Change"],
        ["Market Access (Joint)", "13.5%", "48.1%", "+34.6pp"],
        ["Mangrove/Seaweed Work (Joint)", "9.8%", "49.1%", "+39.3pp"],
        ["Routine Purchases (Joint)", "25.6%", "50.6%", "+25.0pp"],
        ["Business/Loans (Joint)", "40.2%", "59.4%", "+19.2pp"],
        ["Child Education (Joint)", "58.1%", "59.7%", "+1.6pp"],
    ]
    story.append(make_table(dec, [4, 1.5, 1.5, 1.5]))
    story.append(Spacer(1, 5 * mm))
    # Climate & NbS
    story.append(Paragraph("Climate Change & Nature-Based Solutions", styles['SubSection']))
    cc = [
        ["Indicator", "Baseline", "Midline", "Change"],
        ["Climate Change Awareness", "60.5%", "96.3%", "+35.8pp"],
        ["NbS Knowledge", "23.1%", "77.8%", "+54.7pp"],
        ["Mangrove Active", "36.9%", "86.5%", "+49.6pp"],
        ["Seaweed Active", "19.8%", "74.7%", "+54.9pp"],
        ["Forest Management", "67.4%", "98.4%", "+31.0pp"],
        ["Increased Drought Knowledge", "54.7%", "75.9%", "+21.2pp"],
        ["Carbon Capture Knowledge", "2.8%", "33.1%", "+30.3pp"],
    ]
    story.append(make_table(cc, [4, 1.5, 1.5, 1.5]))
    story.append(Spacer(1, 3 * mm))
    p_nbs = chart_bar_comparison(
        ['Mangrove', 'Seaweed', 'Forest\nMgmt', 'NbS\nKnowledge'],
        [36.9, 19.8, 67.4, 23.1],
        [86.5, 74.7, 98.4, 77.8],
        'Women — NbS Participation & Knowledge', 'ws_nbs')
    story.append(Image(p_nbs, width=420, height=180))
    story.append(Spacer(1, 5 * mm))
    # Life Skills
    story.append(Paragraph("Life Skills & Psychosocial Empowerment", styles['SubSection']))
    ls = [
        ["Area", "Baseline", "Midline", "Change"],
        ["Positive Qualities (agree)", "88.5%", "97.2%", "+8.7pp"],
        ["Respected", "78.2%", "97.8%", "+19.6pp"],
        ["Life Meaning", "93.5%", "99.4%", "+5.9pp"],
        ["Can Lead", "59.1%", "94.1%", "+35.0pp"],
        ["Express with Community", "52.5%", "87.2%", "+34.7pp"],
        ["Convince Others", "61.5%", "92.5%", "+31.0pp"],
    ]
    story.append(make_table(ls, [4, 1.5, 1.5, 1.5]))
    story.append(Spacer(1, 5 * mm))
    # Social norms
    story.append(Paragraph("Social Norms & Gender Attitudes", styles['SubSection']))
    story.append(Paragraph(
        "<i><b>Note:</b> Higher agreement with gendered norms indicates persistence of harmful attitudes.</i>",
        styles['SmallItalic']))
    story.append(Spacer(1, 2 * mm))
    norms = [
        ["Norm", "Baseline", "Midline", "Direction"],
        ["Man Provides Income", "40.2%", "75.4%", "⚠ Concerning increase"],
        ["Only Men Drive Boats", "23.5%", "88.1%", "⚠ Concerning increase"],
        ["Better Business Ideas (Men)", "64.4%", "74.1%", "Modest increase"],
        ["Harassment Victim Fault", "36.8%", "55.3%", "⚠ Concerning increase"],
        ["Mangrove = Women's Work", "73.7%", "89.1%", "Positive shift"],
        ["Seaweed = Women's Work", "70.5%", "91.3%", "Positive shift"],
    ]
    story.append(make_table(norms, [4, 1.5, 1.5, 2]))


def _sec_men_survey(story):
    story.append(Paragraph("Men COSME Survey", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph(
        "<b>Sample Size:</b> 267 Male Household Members  |  <b>Survey Type:</b> Midline  |  <b>Location:</b> Kilifi & Kwale Counties",
        styles['BodyText2']))
    story.append(Spacer(1, 3 * mm))
    story.append(kpi_card_table([
        ("CC Awareness", "100%", "↑ 22.2pp from 77.8%"),
        ("NbS Knowledge", "89.8%", "↑ 47.4pp from 42.4%"),
        ("Support Women NbS", "86.8%", "↑ 60.4pp avg"),
        ("Harmful Norms ↓", "-36.4pp", "Only men drive boats"),
    ]))
    story.append(Spacer(1, 5 * mm))
    # Logframe
    story.append(Paragraph("Logframe Indicator Performance", styles['SubSection']))
    lf = [
        ["Indicator", "Baseline", "Target", "Midline", "Change", "Status"],
        ["1230a. Male NbS/economic rights knowledge", "54.7%", "65.0%", "80.3%", "+25.6pp", status_color("EXCEEDED")],
        ["1230b. Women perceived equal by men (score)", "41.2/100", "55/100", "71/100", "+29.8 pts", status_color("EXCEEDED")],
    ]
    story.append(make_table(lf, [4, 1.2, 1.2, 1.2, 1.2, 1.5]))
    story.append(Spacer(1, 5 * mm))
    # Key Findings
    story.append(Paragraph("Key Findings Summary", styles['SubSection']))
    kf = [
        ["Domain", "Key Metric", "Change"],
        ["Climate & NbS", "CC awareness 77.8% → 100%, NbS 42.4% → 89.8%", "+22.2pp / +47.4pp"],
        ["Support Female Conservation", "Mangrove +51pp, Seaweed +68pp, Forest +62pp", "Avg +60pp"],
        ["Household Responsibility", "Joint cooking belief +50.5pp, cleaning +59.6pp", "+82.6% care time"],
        ["Joint Decision-Making", "Large purchases: 59.6% → 89.8%", "+30.2pp"],
        ["Harmful Norms Reduction", "Harassment victim fault: 67.6% → 30.7%", "-36.9pp"],
        ["Time Investment", "Unpaid care: 2.3 → 4.2 hrs/day", "+82.6%"],
        ["Savings", "Personally saving: 31.4% → 68.2%", "+36.8pp"],
    ]
    story.append(make_table(kf, [3, 5, 2]))
    story.append(Spacer(1, 5 * mm))
    # Chart
    p = chart_bar_comparison(
        ['Mangrove\nRestoration', 'Seaweed\nFarming', 'Forest\nManagement'],
        [29.7, 15.7, 33.7], [80.7, 83.9, 95.8],
        "Men's Support for Women's NbS Participation", 'ms_nbs',
        colors=['#FFCC80', '#FF6F00'])
    story.append(Image(p, width=420, height=180))
    story.append(Spacer(1, 5 * mm))
    # Harmful Norms
    story.append(Paragraph("Harmful Norms Reduction", styles['SubSection']))
    norms = [
        ["Norm", "Baseline", "Midline", "Change"],
        ["Only men earn income", "63.1%", "28.4%", "-34.7pp ✓"],
        ["Only men drive boats", "59.2%", "22.7%", "-36.4pp ✓"],
        ["Harassment victim fault", "67.6%", "30.7%", "-36.9pp ✓"],
        ["Husband controls woman income", "41.9%", "19.3%", "-22.6pp ✓"],
        ["Men should do domestic work", "42.1%", "71.8%", "+29.7pp ✓"],
        ["Women should participate in decisions", "48.3%", "82.6%", "+34.3pp ✓"],
    ]
    story.append(make_table(norms, [4, 1.5, 1.5, 2]))
    story.append(Spacer(1, 5 * mm))
    p2 = chart_bar_comparison(
        ['Men earn\nincome', 'Men drive\nboats', 'Harassment\nvictim fault', 'Husband\ncontrols $'],
        [63.1, 59.2, 67.6, 41.9], [28.4, 22.7, 30.7, 19.3],
        "Men — Harmful Norms Reduction (Lower = Better)", 'ms_norms',
        colors=['#EF9A9A', '#C62828'])
    story.append(Image(p2, width=420, height=180))


def _sec_gjj_women(story):
    story.append(Paragraph("GJJ KAP Women Survey", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph(
        "<b>Sample Size:</b> 312 Women  |  <b>Survey Type:</b> Endline (Knowledge, Attitudes & Practices)",
        styles['BodyText2']))
    story.append(Spacer(1, 3 * mm))
    story.append(kpi_card_table([
        ("Self-Esteem (SA)", "52.6%", "↑ 19.1pp from 33.5%"),
        ("Equal Perception", "48.2%", "↑ 27.8pp from 20.4%"),
        ("HH Chore Support", "64.7%", "↑ 23.3pp from 41.4%"),
        ("Decision Talk", "81.7%", "↑ 21.5pp from 60.2%"),
    ]))
    story.append(Spacer(1, 5 * mm))
    d = [
        ["Domain", "Indicator", "Baseline", "Endline", "Change"],
        ["SELF", "Strengths & qualities (SA)", "33.5%", "52.6%", "+19.1pp"],
        ["SELF", "Equal perception (SA)", "20.4%", "48.2%", "+27.8pp"],
        ["SELF", "Voice opinions in community (SA)", "26.7%", "65.9%", "+39.2pp"],
        ["RELATIONAL", "Respected by partner (Always)", "43.1%", "39.1%", "-4.0pp ⚠"],
        ["SHARED RESP.", "Husband supports chores", "41.4%", "64.7%", "+23.3pp"],
        ["SHARED RESP.", "Weekly chore discussion", "63.7%", "94.5%", "+30.8pp"],
        ["SHARED POWER", "Decision conversations", "60.2%", "81.7%", "+21.5pp"],
        ["SHARED POWER", "Husband alone decisions", "8.8%", "2.0%", "-6.8pp ✓"],
        ["AUTONOMY", "Business support (Definitely)", "84.9%", "64.2%", "-20.7pp ⚠"],
        ["AUTONOMY", "Money hiding (Always)", "12.0%", "3.3%", "-8.7pp ✓"],
    ]
    story.append(make_table(d, [2, 4, 1.3, 1.3, 1.5]))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("Household Decision Types", styles['SubSubSection']))
    hh = [
        ["Decision Type", "Baseline", "Endline", "Change"],
        ["Purchase household assets", "17.6%", "22.0%", "+4.4pp"],
        ["Send/remove child from school", "39.8%", "50.6%", "+10.8pp"],
        ["Invest in business", "18.4%", "22.1%", "+3.7pp"],
        ["Seek healthcare", "6.6%", "20.3%", "+13.7pp"],
    ]
    story.append(make_table(hh, [4, 1.5, 1.5, 1.5]))


def _sec_gjj_men(story):
    story.append(Paragraph("GJJ KAP Men Survey", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph(
        "<b>Sample Size:</b> 289 Men  |  <b>Survey Type:</b> Endline (Knowledge, Attitudes & Practices)",
        styles['BodyText2']))
    story.append(Spacer(1, 3 * mm))
    story.append(kpi_card_table([
        ("Self-Responsibility", "70.3%", "↑ 20.2pp from 50.1%"),
        ("Respected by Partner", "83.5%", "↑ 53.4pp from 30.1%"),
        ("Always Does Chores", "42.2%", "↑ 24.5pp from 17.7%"),
        ("Decision Conversations", "97.1%", "↑ 9.2pp from 87.9%"),
    ]))
    story.append(Spacer(1, 5 * mm))
    d = [
        ["Domain", "Indicator", "Baseline", "Endline", "Change"],
        ["SELF", "Responsibility (SA)", "50.1%", "70.3%", "+20.2pp"],
        ["SELF", "Learn & grow (SA)", "47.7%", "71.2%", "+23.5pp"],
        ["SELF", "Equal perception (SA)", "44.0%", "61.1%", "+17.1pp"],
        ["SELF", "Self-compassion (Frequently)", "61.1%", "75.4%", "+14.3pp"],
        ["RELATIONAL", "Respected by partner (Always)", "30.1%", "83.5%", "+53.4pp"],
        ["RELATIONAL", "Laugh together (Always)", "52.2%", "83.5%", "+31.3pp"],
        ["RELATIONAL", "Accept 'No' (Always)", "40.5%", "60.2%", "+19.7pp"],
        ["SHARED RESP.", "Always does chores", "17.7%", "42.2%", "+24.5pp"],
        ["SHARED RESP.", "Support chores (Yes)", "86.9%", "92.7%", "+5.8pp"],
        ["SHARED POWER", "Decision conversations", "87.9%", "97.1%", "+9.2pp"],
        ["SHARED POWER", "Support wife leadership (Always)", "53.1%", "64.9%", "+11.8pp"],
        ["AUTONOMY", "Business support (Definitely)", "53.5%", "67.6%", "+14.1pp"],
        ["AUTONOMY", "Combined strong support", "54.1%", "89.5%", "+35.4pp"],
    ]
    story.append(make_table(d, [2, 4, 1.3, 1.3, 1.5]))


def _sec_forestry(story):
    story.append(Paragraph("Forestry Groups Assessment", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph(
        "<b>Scope:</b> 28 Community Forest Conservation Groups assessed (Baseline: 43 groups)  |  <b>Survey Type:</b> Midline",
        styles['BodyText2']))
    story.append(Spacer(1, 3 * mm))
    story.append(kpi_card_table([
        ("Functionality ≥70%", "85.7%", "↑ 32.2pp from 53.5%"),
        ("Gender Domain Score", "63.5%", "↑ 20.7pp from 42.8%"),
        ("Income Generating", "62.5%", "↑ 25.0pp from 37.5%"),
        ("Group Registration", "85.0%", "↑ 12.5pp from 72.5%"),
    ]))
    story.append(Spacer(1, 5 * mm))
    # Logframe
    story.append(Paragraph("Logframe Indicator", styles['SubSection']))
    lf = [
        ["Indicator", "Baseline", "Target", "Midline", "Change", "Status"],
        ["1130b. Functional groups (≥70% score)", "53.5%", "70.0%", "85.7%", "+32.2pp", status_color("EXCEEDED")],
    ]
    story.append(make_table(lf, [4, 1.2, 1.2, 1.2, 1.2, 1.5]))
    story.append(Spacer(1, 5 * mm))
    # Domain Scores
    story.append(Paragraph("Domain Scores", styles['SubSection']))
    dom = [
        ["Domain", "Baseline", "Midline", "Change"],
        ["Management", "78.6%", "78.0%", "-0.6pp"],
        ["Gender", "32.9%", "85.5%", "+52.6pp"],
        ["Effectiveness", "72.0%", "90.1%", "+18.1pp"],
        ["Overall", "70.6", "84.2", "+13.6pp"],
    ]
    story.append(make_table(dom, [3, 1.5, 1.5, 1.5]))
    story.append(Spacer(1, 3 * mm))
    p = chart_bar_comparison(
        ['Management', 'Gender', 'Effectiveness', 'Overall'],
        [78.6, 32.9, 72.0, 70.6], [78.0, 85.5, 90.1, 84.2],
        'Forestry Group Domain Scores — Baseline vs Midline', 'fr_domains',
        colors=['#A5D6A7', '#1B5E20'])
    story.append(Image(p, width=420, height=180))
    story.append(Spacer(1, 5 * mm))
    # Forest condition
    story.append(Paragraph("Forest Condition & Conservation", styles['SubSection']))
    fc = [
        ["Indicator", "Baseline", "Midline", "Change"],
        ["Area 'Good' Condition", "30.0%", "52.5%", "+22.5pp"],
        ["Biodiversity 'Good'", "25.0%", "47.5%", "+22.5pp"],
        ["Fire Threat 'High'", "35.0%", "15.0%", "-20.0pp ✓"],
        ["Charcoal Threat 'High'", "40.0%", "17.5%", "-22.5pp ✓"],
        ["Encroachment 'High'", "32.5%", "15.0%", "-17.5pp ✓"],
        ["Income-generating", "37.5%", "62.5%", "+25.0pp"],
        ["Agroforestry", "32.5%", "57.5%", "+25.0pp"],
        ["Women in Leadership", "17.5%", "35.0%", "+17.5pp"],
        ["GE Discussions", "40.0%", "72.5%", "+32.5pp"],
    ]
    story.append(make_table(fc, [3.5, 1.5, 1.5, 2]))
    story.append(Spacer(1, 5 * mm))
    # Training output
    story.append(Paragraph("Forestry Training Output (Output 1131)", styles['SubSection']))
    ft = [
        ["Metric", "Value", "Target", "Achievement"],
        ["Groups formed", "52", "45", "116%"],
        ["Members registered", "1,440", "1,350", "107%"],
        ["Female members", "1,141 (79%)", "—", "—"],
        ["Male members", "299 (21%)", "—", "—"],
        ["Grand Total Completed", "1,030", "1,350", "76%"],
    ]
    story.append(make_table(ft, [3, 2, 2, 2]))
    story.append(Spacer(1, 5 * mm))
    # Pre/Post Forest Training
    story.append(Paragraph("Pre/Post Forest Conservation Training", styles['SubSection']))
    story.append(Paragraph(
        "<b>Pre-Test Participants:</b> 546  |  <b>Post-Test Participants:</b> 909",
        styles['BodyText2']))
    story.append(Spacer(1, 3 * mm))
    lf2 = [
        ["Indicator", "Pre-Test", "Target", "Post-Test", "Change", "Status"],
        ["1130a. Adequate knowledge (≥70%)", "50.0%", "68.0%", "94.7%", "+44.7pp", status_color("EXCEEDED")],
    ]
    story.append(make_table(lf2, [4, 1.2, 1.2, 1.2, 1.2, 1.5]))
    story.append(Spacer(1, 3 * mm))
    pp = [
        ["Metric", "Pre-Test", "Post-Test", "Change"],
        ["Average Score", "65.2%", "85.4%", "+20.2pp"],
        ["≥70% Threshold", "50.0%", "94.7%", "+44.7pp"],
        ["≥80% Threshold", "32.9%", "85.7%", "+52.8pp"],
        ["Forest Ecosystems", "56.6%", "91.5%", "+34.9pp"],
        ["Ecosystem Services", "—", "99.7%", "Highest"],
        ["Carbon Sequestration", "—", "99.2%", "High"],
    ]
    story.append(make_table(pp, [4, 1.5, 1.5, 1.5]))


def _sec_mangrove(story):
    story.append(Paragraph("Mangrove & Conservation Training", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph(
        "<b>Scope:</b> 42 mangrove groups  |  <b>1,344 members</b> (973 female, 371 male)  |  <b>5 training modules</b>",
        styles['BodyText2']))
    story.append(Spacer(1, 3 * mm))
    story.append(kpi_card_table([
        ("Groups Formed", "42", "Target: 40 (105%)"),
        ("Members", "1,344", "Target: 1,200 (112%)"),
        ("Female %", "72%", "973 women"),
        ("Knowledge ≥70%", "81.9%", "↑ 45.0pp"),
    ]))
    story.append(Spacer(1, 5 * mm))
    # Logframe
    story.append(Paragraph("Logframe Indicator — Mangrove Knowledge", styles['SubSection']))
    lf = [
        ["Indicator", "Pre-Test", "Target", "Post-Test", "Change", "Status"],
        ["1110a. Adequate mangrove knowledge", "36.9%", "57.0%", "81.9%", "+45.0pp", status_color("EXCEEDED")],
    ]
    story.append(make_table(lf, [4, 1.2, 1.2, 1.2, 1.2, 1.5]))
    story.append(Spacer(1, 5 * mm))
    # Knowledge by location/gender
    story.append(Paragraph("Knowledge by Location & Gender", styles['SubSection']))
    loc = [
        ["Metric", "Pre-Test", "Post-Test", "Change"],
        ["Overall Adequate Knowledge", "36.9%", "81.5%", "+44.6pp"],
        ["Kilifi", "21.1%", "80.1%", "+59.0pp"],
        ["Kwale", "53.7%", "83.1%", "+29.4pp"],
        ["Female", "34.7%", "87.4%", "+52.7pp"],
        ["Male", "38.2%", "80.2%", "+42.0pp"],
    ]
    story.append(make_table(loc, [4, 1.5, 1.5, 1.5]))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(
        "<b>Key Insight:</b> Women outperformed men by 7.2pp at post-test despite starting 3.5pp below.",
        styles['BodyText2']))
    story.append(Spacer(1, 5 * mm))
    # Training output
    story.append(Paragraph("Mangrove Training Output (Output 1112)", styles['SubSection']))
    mt = [
        ["Metric", "Value", "Target", "Achievement"],
        ["Groups formed", "42", "40", "105%"],
        ["Members registered", "1,344", "1,200", "112%"],
        ["Female members", "973 (72%)", "—", "—"],
        ["Male members", "371 (28%)", "—", "—"],
        ["Grand Total Completed", "842", "1,200", "70%"],
    ]
    story.append(make_table(mt, [3, 2, 2, 2]))
    story.append(Spacer(1, 3 * mm))
    # Module completion
    story.append(Paragraph("Module Completion Rates", styles['SubSubSection']))
    mod = [
        ["Module", "Target", "Completed", "Target %", "Reg %"],
        ["Module 1", "1,200", "1,121", "93%", "83%"],
        ["Module 2", "1,200", "961", "80%", "72%"],
        ["Module 3", "1,200", "842", "70%", "63%"],
        ["Module 4", "1,200", "753", "63%", "56%"],
        ["Module 5", "1,200", "535", "45%", "40%"],
    ]
    story.append(make_table(mod, [2, 1.5, 2, 1.5, 1.5]))


def _sec_seaweed(story):
    story.append(Paragraph("Seaweed Assessment", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph(
        "<b>Scope:</b> 19 groups  |  <b>610 active female members</b>  |  <b>Assessment Period:</b> July 2025",
        styles['BodyText2']))
    story.append(Spacer(1, 3 * mm))
    sd = [
        ["Metric", "Value"],
        ["Women-led groups", "94.7%"],
        ["Formal leadership", "100%"],
        ["Meet weekly", "73.7%"],
        ["Production active", "89.5%"],
        ["Total harvest (kg)", "96,086"],
        ["Improved yield after sustainable practices", "78.9%"],
        ["Off-bottom method", "78.9%"],
        ["Regenerative practices", "89.5%"],
        ["Groups selling", "47.4%"],
        ["Average price (KES/kg)", "81.1"],
        ["Training: farming", "100%"],
        ["Training: business", "26.3%"],
        ["Formal buyer agreements", "5.3%"],
    ]
    story.append(make_table(sd, [5, 5]))
    story.append(Spacer(1, 3 * mm))
    # Logframe
    story.append(Paragraph("Logframe Indicator 1100c", styles['SubSubSection']))
    sea_lf = [
        ["Measure", "Count"],
        ["Groups with regenerative production", "17"],
        ["Groups with value addition", "13"],
        ["Groups with commercialization", "9"],
    ]
    story.append(make_table(sea_lf, [6, 4]))
    story.append(Spacer(1, 3 * mm))
    p = chart_horizontal_bar(
        ['Transport', 'Demand', 'Pricing'],
        [90, 80, 60],
        'Seaweed Groups — Top Challenges (% Reporting)', 'sw_challenges',
        color='#00897B')
    story.append(Image(p, width=420, height=140))
    story.append(Spacer(1, 5 * mm))
    # Training output
    story.append(Paragraph("Seaweed Training Output (Output 1122)", styles['SubSection']))
    st = [
        ["Metric", "Value", "Target", "Achievement"],
        ["Groups formed", "19", "20", "95%"],
        ["Members registered", "842", "600", "140%"],
        ["Female members", "651 (77%)", "—", "—"],
        ["Grand Total Completed", "462", "600", "77%"],
    ]
    story.append(make_table(st, [3, 2, 2, 2]))


def _sec_schools(story):
    story.append(Paragraph("Schools Dashboard", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph(
        "<b>Scope:</b> 65 schools assessed  |  <b>Counties:</b> Kwale (35) & Kilifi (30)  |  <b>Total Students:</b> 44,301",
        styles['BodyText2']))
    story.append(Spacer(1, 3 * mm))
    # Logframe
    lf = [
        ["Indicator", "Baseline", "Target", "Midline", "Change", "Status"],
        ["1310c. Schools with clean water access", "23.4%", "60.0%", "62.5%", "+39.1pp", status_color("EXCEEDED")],
    ]
    story.append(make_table(lf, [4, 1.2, 1.2, 1.2, 1.2, 1.5]))
    story.append(Spacer(1, 5 * mm))
    # Enrollment
    story.append(Paragraph("School Enrollment", styles['SubSection']))
    enroll = [
        ["County", "Schools", "Boys", "Girls", "Total"],
        ["Kwale", "35", "9,960", "9,433", "19,393"],
        ["Kilifi", "30", "12,739", "12,169", "24,908"],
        ["Total", "65", "22,699", "21,602", "44,301"],
    ]
    story.append(make_table(enroll, [2, 1.5, 2, 2, 2]))
    story.append(Spacer(1, 5 * mm))
    # WASH
    story.append(Paragraph("Water Infrastructure & WASH", styles['SubSection']))
    water = [
        ["Indicator", "Baseline", "Midline", "Notes"],
        ["Borehole", "44.2%", "52.3%", "+8.1pp"],
        ["Rainwater Collection", "13.0%", "27.7%", "+14.7pp"],
        ["Water Tanks", "2.6%", "9.2%", "+6.6pp"],
        ["Year-round Water", "49.4%", "55.4%", "+6.0pp"],
        ["Schools receiving tanks/gutters", "—", "83%", "—"],
        ["Solvatten kits used", "—", "49%", "—"],
        ["Hygiene training", "—", "74%", "—"],
        ["Maintenance budget", "—", "20%", "Only 20%"],
    ]
    story.append(make_table(water, [4, 1.5, 1.5, 2]))
    story.append(Spacer(1, 5 * mm))
    # 4K Clubs
    story.append(Paragraph("4K Clubs", styles['SubSection']))
    clubs = [
        ["Metric", "Value"],
        ["Schools with clubs", "97%"],
        ["Total members", "5,065"],
        ["Female members", "2,917 (57.6%)"],
        ["Male members", "2,148 (42.4%)"],
        ["Materials received", "92%"],
        ["Environmental initiatives", "81.5%"],
    ]
    story.append(make_table(clubs, [5, 5]))
    story.append(Spacer(1, 3 * mm))
    p = chart_pie(
        ['Boys - Kwale', 'Girls - Kwale', 'Boys - Kilifi', 'Girls - Kilifi'],
        [9960, 9433, 12739, 12169],
        'School Enrollment Distribution (n=44,301)', 'sc_enrollment',
        colors=['#42A5F5', '#90CAF9', '#1565C0', '#64B5F6'])
    story.append(Image(p, width=280, height=220))


def _sec_vsla(story):
    story.append(Paragraph("VSLA Monitoring", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph(
        "<b>Scope:</b> 211 assessments  |  <b>173 unique groups</b>  |  <b>Counties:</b> Kilifi & Kwale",
        styles['BodyText2']))
    story.append(Spacer(1, 3 * mm))
    vd = [
        ["Indicator", "Value"],
        ["1220a. % women actively saving", "78.6%"],
        ["Assessments conducted", "211"],
        ["Unique groups", "173"],
        ["Dashboard pages", "6 (Overview, Participation, Savings, Loans, Social Fund, Loan Use)"],
        ["Filters available", "County, Reporting Cycle (1-3), Quarter (Q2-Q4), Group"],
    ]
    story.append(make_table(vd, [5, 5]))
    story.append(Spacer(1, 5 * mm))
    # VSLA Training output
    story.append(Paragraph("VSLA Training (20 Modules)", styles['SubSection']))
    vt = [
        ["Metric", "Value"],
        ["Target", "3,000"],
        ["Registered", "2,765"],
        ["Female completion avg", "1,834 (62% target / 67% registered)"],
        ["Module range", "20% – 71% completion"],
        ["Highest module", "Module 7 (2,140 = 71%)"],
        ["Lowest module", "Module 20 (613 = 20%)"],
    ]
    story.append(make_table(vt, [4, 6]))


def _sec_logframe(story):
    story.append(Paragraph("Logframe Indicators — Complete Summary", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph(
        "<b>Overall: 12 of 13 quantitative indicators EXCEEDED targets. 1 indicator ON TRACK.</b>",
        styles['BodyText2']))
    story.append(Spacer(1, 5 * mm))
    lf_all = [
        ["ID", "Indicator", "Baseline", "Target", "Result", "Change", "Status"],
        ["1200a", "Women HH/group decision involvement", "57.6%", "65.0%", "95.9%", "+38.3pp", status_color("EXCEEDED")],
        ["1200b", "Women unpaid work time", "9.3 hrs", "8.3 hrs", "7.7 hrs", "-1.6 hrs", status_color("EXCEEDED")],
        ["1200c", "Women access/control resources", "41.2%", "50.0%", "53.8%", "+12.6pp", status_color("EXCEEDED")],
        ["1210a", "Women NbS/Econ Rights knowledge", "20.7%", "55.0%", "80.9%", "+60.2pp", status_color("EXCEEDED")],
        ["1210b", "Women personal skills & confidence", "32.7%", "55.0%", "46.3%", "+13.6pp", status_color("ON TRACK")],
        ["1210c", "Women perceived equal (score)", "42.1", "55.0", "64.7", "+22.6 pts", status_color("EXCEEDED")],
        ["1220a", "Women actively saving in groups", "28.8%", "70.0%", "91.9%", "+63.1pp", status_color("EXCEEDED")],
        ["1220b", "Women access time-saving tech", "50.8%", "80.0%", "83.1%", "+32.3pp", status_color("EXCEEDED")],
        ["1230a", "Male NbS/economic rights knowledge", "54.7%", "65.0%", "80.3%", "+25.6pp", status_color("EXCEEDED")],
        ["1230b", "Women perceived equal by men", "41.2", "55.0", "71.0", "+29.8 pts", status_color("EXCEEDED")],
        ["1130b", "Functional CFC groups (≥70%)", "53.5%", "70.0%", "85.7%", "+32.2pp", status_color("EXCEEDED")],
        ["1130a", "Forest conservation knowledge", "50.0%", "68.0%", "94.7%", "+44.7pp", status_color("EXCEEDED")],
        ["1110a", "Mangrove restoration knowledge", "36.9%", "57.0%", "81.9%", "+45.0pp", status_color("EXCEEDED")],
        ["1310c", "Schools clean water access", "23.4%", "60.0%", "62.5%", "+39.1pp", status_color("EXCEEDED")],
    ]
    story.append(make_table(lf_all, [1, 3.5, 1.1, 1.1, 1.1, 1.1, 1.3]))
    story.append(Spacer(1, 5 * mm))
    ind_labels = [
        '1200a', '1200c', '1210a', '1210b', '1210c',
        '1220a', '1220b', '1230a', '1230b', '1130b', '1130a', '1110a', '1310c'
    ]
    baselines = [57.6, 41.2, 20.7, 32.7, 42.1, 28.8, 50.8, 54.7, 41.2, 53.5, 50.0, 36.9, 23.4]
    tgts = [65, 50, 55, 55, 55, 70, 80, 65, 55, 70, 68, 57, 60]
    results = [95.9, 53.8, 80.9, 46.3, 64.7, 91.9, 83.1, 80.3, 71.0, 85.7, 94.7, 81.9, 62.5]
    p = chart_logframe_achievement(ind_labels, baselines, tgts, results, 'lf_all_ind')
    story.append(Image(p, width=460, height=280))


# ============================================================
# REGISTRY — maps report-id to its builder
# ============================================================
REPORTS = {
    'women-survey': {
        'file': 'COSME_Women_Survey_Report.pdf',
        'cover_title': 'Women Survey Report',
        'cover_sub': 'Midline Analysis — 345 Women, Kilifi & Kwale',
        'cover_stats': [("345", "Women\nSurveyed"), ("98%", "VSLA\nParticipation"), ("96.3%", "Climate\nAwareness"), ("8/8", "Indicators\nExceeded")],
        'builder': _sec_women_survey,
    },
    'men-survey': {
        'file': 'COSME_Men_Survey_Report.pdf',
        'cover_title': 'Men Survey Report',
        'cover_sub': 'Midline Analysis — 267 Men, Kilifi & Kwale',
        'cover_stats': [("267", "Men\nSurveyed"), ("100%", "CC\nAwareness"), ("89.8%", "NbS\nKnowledge"), ("2/2", "Indicators\nExceeded")],
        'builder': _sec_men_survey,
    },
    'gjj-women': {
        'file': 'COSME_GJJ_Women_Report.pdf',
        'cover_title': 'GJJ KAP Women Report',
        'cover_sub': 'Endline KAP Analysis — 312 Women',
        'cover_stats': [("312", "Women\nSurveyed"), ("52.6%", "Self-Esteem\n(SA)"), ("48.2%", "Equal\nPerception"), ("81.7%", "Decision\nTalk")],
        'builder': _sec_gjj_women,
    },
    'gjj-men': {
        'file': 'COSME_GJJ_Men_Report.pdf',
        'cover_title': 'GJJ KAP Men Report',
        'cover_sub': 'Endline KAP Analysis — 289 Men',
        'cover_stats': [("289", "Men\nSurveyed"), ("70.3%", "Self-\nResponsibility"), ("83.5%", "Respected by\nPartner"), ("97.1%", "Decision\nConversations")],
        'builder': _sec_gjj_men,
    },
    'forestry': {
        'file': 'COSME_Forestry_Report.pdf',
        'cover_title': 'Forestry Report',
        'cover_sub': '28 Community Forest Conservation Groups — Midline',
        'cover_stats': [("28", "Forestry\nGroups"), ("85.7%", "Functional\n≥70%"), ("85.5%", "Gender\nDomain"), ("94.7%", "Knowledge\n≥70%")],
        'builder': _sec_forestry,
    },
    'mangrove': {
        'file': 'COSME_Mangrove_Report.pdf',
        'cover_title': 'Mangrove Report',
        'cover_sub': '42 Mangrove Groups — Training & Conservation',
        'cover_stats': [("42", "Mangrove\nGroups"), ("1,344", "Members"), ("72%", "Female"), ("81.9%", "Knowledge\n≥70%")],
        'builder': _sec_mangrove,
    },
    'seaweed': {
        'file': 'COSME_Seaweed_Report.pdf',
        'cover_title': 'Seaweed Report',
        'cover_sub': '19 Groups, 610 Women — Value Chain Assessment',
        'cover_stats': [("19", "Seaweed\nGroups"), ("610", "Women\nFarmers"), ("96,086", "Harvest\n(kg)"), ("89.5%", "Regenerative\nPractices")],
        'builder': _sec_seaweed,
    },
    'schools': {
        'file': 'COSME_Schools_Report.pdf',
        'cover_title': 'Schools Report',
        'cover_sub': '65 Schools — WASH, Eco-Clubs & Environmental Education',
        'cover_stats': [("65", "Schools"), ("44,301", "Students"), ("62.5%", "Clean Water\nAccess"), ("97%", "4K Club\nCoverage")],
        'builder': _sec_schools,
    },
    'vsla': {
        'file': 'COSME_VSLA_Report.pdf',
        'cover_title': 'VSLA Report',
        'cover_sub': '211 Assessments — Savings & Financial Inclusion',
        'cover_stats': [("211", "Assessments"), ("173", "Unique\nGroups"), ("78.6%", "Women\nSaving"), ("20", "Training\nModules")],
        'builder': _sec_vsla,
    },
    'logframe': {
        'file': 'COSME_Logframe_Report.pdf',
        'cover_title': 'Logframe & Indicators',
        'cover_sub': '13 Key Performance Indicators — Achievement Analysis',
        'cover_stats': [("13", "Indicators"), ("12", "Exceeded\nTargets"), ("1", "On Track"), ("0", "Below\nTarget")],
        'builder': _sec_logframe,
    },
}


def generate_all():
    """Generate all individual topic PDFs."""
    print(f"\n{'=' * 60}")
    print("  GENERATING INDIVIDUAL TOPIC REPORTS")
    print(f"{'=' * 60}\n")
    paths = []
    for rid, cfg in REPORTS.items():
        try:
            p = _build_doc(cfg['file'], cfg['builder'],
                           cfg['cover_title'], cfg['cover_sub'], cfg['cover_stats'])
            paths.append(p)
        except Exception as e:
            print(f"  ✗  {cfg['file']} — ERROR: {e}")
    print(f"\n{'=' * 60}")
    print(f"  DONE — {len(paths)}/{len(REPORTS)} reports generated")
    print(f"{'=' * 60}\n")
    # Cleanup charts
    import shutil
    try:
        shutil.rmtree(CHART_DIR)
    except:
        pass
    return paths


def generate_one(report_id):
    """Generate a single topic PDF by report ID."""
    cfg = REPORTS.get(report_id)
    if not cfg:
        print(f"Unknown report ID: {report_id}")
        print(f"Available: {', '.join(REPORTS.keys())}")
        return None
    p = _build_doc(cfg['file'], cfg['builder'],
                   cfg['cover_title'], cfg['cover_sub'], cfg['cover_stats'])
    import shutil
    try:
        shutil.rmtree(CHART_DIR)
    except:
        pass
    return p


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if target == 'all':
            generate_all()
        else:
            generate_one(target)
    else:
        generate_all()
