"""
COSME Midline Report — Full PDF Generator
Generates a professional multi-section PDF report from extracted midline data.
"""
import os, io, math
from datetime import datetime

# --- ReportLab imports ---
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm, inch
from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether, HRFlowable, Frame, PageTemplate
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

# --- Matplotlib for advanced charts saved as images ---
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

# ============================================================
# CONFIGURATION
# ============================================================
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(OUTPUT_DIR, "COSME_Midline_Report.pdf")
CHART_DIR = os.path.join(OUTPUT_DIR, "_report_charts")
os.makedirs(CHART_DIR, exist_ok=True)

# Color Palette
PRIMARY    = HexColor("#0072CE")
SECONDARY  = HexColor("#1B5E20")
ACCENT     = HexColor("#FF6F00")
DARK       = HexColor("#1A237E")
LIGHT_BG   = HexColor("#F5F7FA")
TABLE_HEAD = HexColor("#0D47A1")
EXCEEDED_C = HexColor("#2E7D32")
ON_TRACK_C = HexColor("#FF8F00")
NEGATIVE_C = HexColor("#C62828")
ROW_ALT    = HexColor("#E3F2FD")
BORDER_C   = HexColor("#BBDEFB")

PAGE_W, PAGE_H = A4
MARGIN = 20 * mm

# Logo path
LOGO_SVG = os.path.join(OUTPUT_DIR, "trackers", "static", "logo.svg")

def _get_logo_drawing(width=None, height=None):
    """Load Plan International SVG logo and scale it."""
    try:
        drawing = svg2rlg(LOGO_SVG)
        if drawing is None:
            return None
        if width and height:
            sx = width / drawing.width
            sy = height / drawing.height
            s = min(sx, sy)
            drawing.width = drawing.width * s
            drawing.height = drawing.height * s
            drawing.scale(s, s)
        elif width:
            s = width / drawing.width
            drawing.width = drawing.width * s
            drawing.height = drawing.height * s
            drawing.scale(s, s)
        return drawing
    except Exception:
        return None

# ============================================================
# STYLES
# ============================================================
styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    'CoverTitle', parent=styles['Title'],
    fontSize=32, leading=38, textColor=white,
    alignment=TA_CENTER, fontName='Helvetica-Bold',
    spaceAfter=12
))
styles.add(ParagraphStyle(
    'CoverSubtitle', parent=styles['Normal'],
    fontSize=16, leading=20, textColor=HexColor("#B3E5FC"),
    alignment=TA_CENTER, fontName='Helvetica',
    spaceAfter=8
))
styles.add(ParagraphStyle(
    'SectionTitle', parent=styles['Heading1'],
    fontSize=20, leading=24, textColor=PRIMARY,
    fontName='Helvetica-Bold', spaceBefore=18, spaceAfter=10,
    borderWidth=0, borderColor=PRIMARY, borderPadding=0,
))
styles.add(ParagraphStyle(
    'SubSection', parent=styles['Heading2'],
    fontSize=14, leading=17, textColor=DARK,
    fontName='Helvetica-Bold', spaceBefore=12, spaceAfter=6,
))
styles.add(ParagraphStyle(
    'SubSubSection', parent=styles['Heading3'],
    fontSize=12, leading=15, textColor=HexColor("#37474F"),
    fontName='Helvetica-Bold', spaceBefore=8, spaceAfter=4,
))
styles.add(ParagraphStyle(
    'BodyText2', parent=styles['Normal'],
    fontSize=10, leading=14, textColor=HexColor("#333333"),
    fontName='Helvetica', alignment=TA_JUSTIFY,
    spaceAfter=6
))
styles.add(ParagraphStyle(
    'SmallItalic', parent=styles['Normal'],
    fontSize=8.5, leading=11, textColor=HexColor("#666666"),
    fontName='Helvetica-Oblique', alignment=TA_LEFT,
))
styles.add(ParagraphStyle(
    'KPI_Label', parent=styles['Normal'],
    fontSize=9, leading=12, textColor=HexColor("#555555"),
    fontName='Helvetica', alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    'KPI_Value', parent=styles['Normal'],
    fontSize=22, leading=26, textColor=PRIMARY,
    fontName='Helvetica-Bold', alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    'TOCEntry', parent=styles['Normal'],
    fontSize=11, leading=16, textColor=HexColor("#1A237E"),
    fontName='Helvetica', spaceBefore=3, spaceAfter=3,
    leftIndent=10,
))
styles.add(ParagraphStyle(
    'TOCSection', parent=styles['Normal'],
    fontSize=12, leading=18, textColor=PRIMARY,
    fontName='Helvetica-Bold', spaceBefore=6, spaceAfter=2,
))
styles.add(ParagraphStyle(
    'FooterStyle', parent=styles['Normal'],
    fontSize=7.5, leading=9, textColor=HexColor("#888888"),
    fontName='Helvetica', alignment=TA_CENTER,
))

# ============================================================
# CHART GENERATORS  (matplotlib → PNG → reportlab Image)
# ============================================================
def _save_chart(fig, name):
    path = os.path.join(CHART_DIR, f"{name}.png")
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return path

def chart_bar_comparison(categories, baseline, midline, title, fname, colors=None):
    """Side-by-side bar chart for baseline vs midline."""
    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    x = np.arange(len(categories))
    w = 0.35
    c1 = colors[0] if colors else '#90CAF9'
    c2 = colors[1] if colors else '#1565C0'
    bars1 = ax.bar(x - w/2, baseline, w, label='Baseline', color=c1, edgecolor='white', linewidth=0.5)
    bars2 = ax.bar(x + w/2, midline, w, label='Midline', color=c2, edgecolor='white', linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=7.5, rotation=25, ha='right')
    ax.set_title(title, fontsize=11, fontweight='bold', color='#1A237E', pad=10)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.legend(fontsize=8, loc='upper left')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylim(0, max(max(midline), max(baseline)) * 1.18)
    for b in bars1:
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+1, f'{b.get_height():.0f}%', ha='center', va='bottom', fontsize=6.5, color='#555')
    for b in bars2:
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+1, f'{b.get_height():.0f}%', ha='center', va='bottom', fontsize=6.5, color='#0D47A1', fontweight='bold')
    fig.tight_layout()
    return _save_chart(fig, fname)

def chart_horizontal_bar(categories, values, title, fname, color='#1565C0'):
    fig, ax = plt.subplots(figsize=(7.5, max(2.0, len(categories)*0.42)))
    y = np.arange(len(categories))
    bars = ax.barh(y, values, color=color, height=0.55, edgecolor='white')
    ax.set_yticks(y)
    ax.set_yticklabels(categories, fontsize=8)
    ax.set_title(title, fontsize=11, fontweight='bold', color='#1A237E', pad=10)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlim(0, max(values)*1.22)
    for bar, v in zip(bars, values):
        ax.text(bar.get_width()+0.8, bar.get_y()+bar.get_height()/2, f'{v:.1f}%', va='center', fontsize=7.5, fontweight='bold', color='#0D47A1')
    fig.tight_layout()
    return _save_chart(fig, fname)

def chart_radar(categories, values_list, labels, title, fname):
    """Radar/spider chart."""
    N = len(categories)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    colors_r = ['#90CAF9', '#1565C0', '#FF8F00', '#2E7D32']
    for i, (vals, lbl) in enumerate(zip(values_list, labels)):
        v = vals + vals[:1]
        ax.plot(angles, v, 'o-', linewidth=1.5, label=lbl, color=colors_r[i % len(colors_r)])
        ax.fill(angles, v, alpha=0.12, color=colors_r[i % len(colors_r)])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=7.5)
    ax.set_title(title, fontsize=11, fontweight='bold', color='#1A237E', pad=20)
    ax.legend(fontsize=8, loc='upper right', bbox_to_anchor=(1.25, 1.1))
    fig.tight_layout()
    return _save_chart(fig, fname)

def chart_logframe_achievement(indicators, baselines, targets, results, fname):
    """Grouped bar chart for logframe indicators."""
    fig, ax = plt.subplots(figsize=(8, max(3.5, len(indicators)*0.55)))
    y = np.arange(len(indicators))
    h = 0.25
    ax.barh(y + h, baselines, h, label='Baseline', color='#BBDEFB', edgecolor='white')
    ax.barh(y, targets, h, label='Target', color='#FF8F00', edgecolor='white')
    ax.barh(y - h, results, h, label='Result', color='#1565C0', edgecolor='white')
    ax.set_yticks(y)
    ax.set_yticklabels(indicators, fontsize=7)
    ax.set_title('Logframe Indicator Achievement — All Datasets', fontsize=11, fontweight='bold', color='#1A237E', pad=10)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())
    ax.legend(fontsize=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout()
    return _save_chart(fig, fname)

def chart_pie(labels, sizes, title, fname, colors=None):
    fig, ax = plt.subplots(figsize=(4.5, 3.5))
    c = colors or ['#1565C0','#42A5F5','#90CAF9','#E3F2FD','#FF8F00','#FFB74D']
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
        colors=c[:len(labels)], startangle=90, textprops={'fontsize':8})
    for t in autotexts:
        t.set_fontsize(7.5)
        t.set_fontweight('bold')
    ax.set_title(title, fontsize=11, fontweight='bold', color='#1A237E', pad=10)
    fig.tight_layout()
    return _save_chart(fig, fname)

# ============================================================
# TABLE HELPER
# ============================================================
def make_table(data, col_widths=None, has_header=True):
    """Create a styled table flowable."""
    avail = PAGE_W - 2*MARGIN
    if col_widths is None:
        ncols = len(data[0]) if data else 1
        col_widths = [avail / ncols] * ncols
    else:
        total = sum(col_widths)
        col_widths = [w / total * avail for w in col_widths]

    wrapped = []
    for ri, row in enumerate(data):
        new_row = []
        for ci, cell in enumerate(row):
            if ri == 0 and has_header:
                st = ParagraphStyle('th', parent=styles['Normal'],
                    fontSize=8.5, leading=11, fontName='Helvetica-Bold',
                    textColor=white, alignment=TA_CENTER)
            else:
                st = ParagraphStyle('td', parent=styles['Normal'],
                    fontSize=8.5, leading=11, fontName='Helvetica',
                    textColor=HexColor("#333333"), alignment=TA_LEFT if ci == 0 else TA_CENTER)
            new_row.append(Paragraph(str(cell), st))
        wrapped.append(new_row)

    t = Table(wrapped, colWidths=col_widths, repeatRows=1 if has_header else 0)
    style_cmds = [
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.4, BORDER_C),
    ]
    if has_header:
        style_cmds.append(('BACKGROUND', (0, 0), (-1, 0), TABLE_HEAD))
        style_cmds.append(('TEXTCOLOR', (0, 0), (-1, 0), white))
    # Alternate row colors
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(('BACKGROUND', (0, i), (-1, i), ROW_ALT))
    t.setStyle(TableStyle(style_cmds))
    return t

def status_color(status_text):
    s = status_text.upper()
    if 'EXCEEDED' in s:
        return f'<font color="#2E7D32"><b>{status_text}</b></font>'
    elif 'ON TRACK' in s:
        return f'<font color="#FF8F00"><b>{status_text}</b></font>'
    elif 'NEGATIVE' in s or 'CONCERN' in s:
        return f'<font color="#C62828"><b>{status_text}</b></font>'
    return status_text

def kpi_card_table(kpis):
    """Create a row of KPI cards. kpis: list of (label, value, change)"""
    ncols = min(len(kpis), 4)
    card_w = (PAGE_W - 2*MARGIN) / ncols
    cells = []
    for label, value, change in kpis:
        change_color = '#2E7D32' if change.startswith('+') or change.startswith('↑') else '#C62828'
        cell_content = (
            f'<para alignment="center"><font size="8" color="#888888">{label}</font><br/>'
            f'<font size="20" color="#0072CE"><b>{value}</b></font><br/>'
            f'<font size="9" color="{change_color}"><b>{change}</b></font></para>'
        )
        cells.append(Paragraph(cell_content, styles['Normal']))
    t = Table([cells], colWidths=[card_w]*ncols)
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_C),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_C),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,0), (-1,-1), HexColor("#FAFAFA")),
    ]))
    return t

# ============================================================
# PAGE TEMPLATE — Header / Footer
# ============================================================
def header_footer(canvas, doc):
    canvas.saveState()
    # --- Plan Logo in header (small) ---
    logo = _get_logo_drawing(width=60)
    if logo:
        renderPDF.draw(logo, canvas, PAGE_W - MARGIN - logo.width, PAGE_H - MARGIN + 3*mm)
    # Header line
    canvas.setStrokeColor(PRIMARY)
    canvas.setLineWidth(1.5)
    canvas.line(MARGIN, PAGE_H - MARGIN + 5*mm, PAGE_W - MARGIN, PAGE_H - MARGIN + 5*mm)
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(HexColor("#888888"))
    canvas.drawString(MARGIN, PAGE_H - MARGIN + 7*mm, "COSME Midline Report — Kilifi & Kwale Counties, Kenya")
    # Footer
    canvas.setStrokeColor(BORDER_C)
    canvas.line(MARGIN, MARGIN - 5*mm, PAGE_W - MARGIN, MARGIN - 5*mm)
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(HexColor("#AAAAAA"))
    canvas.drawCentredString(PAGE_W/2, MARGIN - 10*mm, f"Page {doc.page}")
    canvas.drawString(MARGIN, MARGIN - 10*mm, "CONFIDENTIAL")
    canvas.drawRightString(PAGE_W - MARGIN, MARGIN - 10*mm, f"Generated: {datetime.now().strftime('%d %B %Y')}")
    canvas.restoreState()

def cover_page(canvas, doc):
    """Custom cover page drawn directly on the canvas."""
    canvas.saveState()
    # Background gradient box
    canvas.setFillColor(HexColor("#0D47A1"))
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=True)
    # Accent stripe
    canvas.setFillColor(HexColor("#1565C0"))
    canvas.rect(0, PAGE_H*0.35, PAGE_W, PAGE_H*0.35, fill=True)
    # Top accent bar
    canvas.setFillColor(HexColor("#FF6F00"))
    canvas.rect(0, PAGE_H - 8*mm, PAGE_W, 8*mm, fill=True)
    # Bottom accent bar
    canvas.rect(0, 0, PAGE_W, 5*mm, fill=True)
    # --- Plan International Logo ---
    logo = _get_logo_drawing(width=160)
    if logo:
        logo_x = (PAGE_W - logo.width) / 2
        logo_y = PAGE_H * 0.78
        renderPDF.draw(logo, canvas, logo_x, logo_y)
    # Title
    canvas.setFont('Helvetica-Bold', 36)
    canvas.setFillColor(white)
    canvas.drawCentredString(PAGE_W/2, PAGE_H*0.62, "COSME")
    canvas.drawCentredString(PAGE_W/2, PAGE_H*0.55, "Midline Report")
    # Subtitle
    canvas.setFont('Helvetica', 16)
    canvas.setFillColor(HexColor("#B3E5FC"))
    canvas.drawCentredString(PAGE_W/2, PAGE_H*0.48, "Comprehensive Analysis of Project Impact")
    canvas.drawCentredString(PAGE_W/2, PAGE_H*0.44, "Kilifi & Kwale Counties, Kenya")
    # Date
    canvas.setFont('Helvetica-Bold', 14)
    canvas.setFillColor(HexColor("#FFB74D"))
    canvas.drawCentredString(PAGE_W/2, PAGE_H*0.37, f"Report Date: {datetime.now().strftime('%B %Y')}")
    # Key stats boxes
    box_y = PAGE_H * 0.16
    box_h = 55
    box_w = 120
    gap = 20
    total_w = 4*box_w + 3*gap
    start_x = (PAGE_W - total_w) / 2
    stats = [
        ("345", "Women\nSurveyed"),
        ("267", "Men\nSurveyed"),
        ("65", "Schools\nAssessed"),
        ("12/13", "Indicators\nExceeded"),
    ]
    for i, (val, lbl) in enumerate(stats):
        x = start_x + i*(box_w + gap)
        canvas.setFillColor(HexColor("#1A237E"))
        canvas.roundRect(x, box_y, box_w, box_h, 8, fill=True, stroke=False)
        canvas.setFillColor(HexColor("#FFB74D"))
        canvas.setFont('Helvetica-Bold', 20)
        canvas.drawCentredString(x + box_w/2, box_y + 32, val)
        canvas.setFillColor(HexColor("#B3E5FC"))
        canvas.setFont('Helvetica', 8)
        for li, line in enumerate(lbl.split('\n')):
            canvas.drawCentredString(x + box_w/2, box_y + 15 - li*10, line)
    # Organization
    canvas.setFont('Helvetica', 10)
    canvas.setFillColor(HexColor("#90CAF9"))
    canvas.drawCentredString(PAGE_W/2, PAGE_H*0.08, "Plan International Kenya — COSME & Gender Just & Justice Programme")
    canvas.drawCentredString(PAGE_W/2, PAGE_H*0.05, "Survey Data: Women COSME (n=345) | Men COSME (n=267) | GJJ Women KAP (n=312) | GJJ Men KAP (n=289)")
    canvas.restoreState()

# ============================================================
# BUILD DOCUMENT
# ============================================================
def build_report():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN + 8*mm, bottomMargin=MARGIN + 5*mm,
        title="COSME Midline Report",
        author="Plan International Kenya",
    )

    story = []

    # ---- COVER PAGE (drawn by onFirstPage callback, just skip to next page) ----
    story.append(Spacer(1, 1))
    story.append(PageBreak())

    # ---- TABLE OF CONTENTS ----
    story.append(Paragraph("Table of Contents", styles['SectionTitle']))
    story.append(Spacer(1, 4*mm))
    toc_items = [
        ("1", "Executive Summary & Key Findings"),
        ("2", "Women COSME Survey (n=345)"),
        ("3", "Men COSME Survey (n=267)"),
        ("4", "GJJ KAP Women (n=312)"),
        ("5", "GJJ KAP Men (n=289)"),
        ("6", "Forestry Groups (28 groups)"),
        ("7", "Pre/Post Tests — Forest & Mangrove"),
        ("8", "Schools Dashboard (65 schools)"),
        ("9", "Seaweed Assessment (19 groups, 610 women)"),
        ("10", "VSLA Monitoring (211 assessments)"),
        ("11", "Project Outputs — Training Completion"),
        ("12", "Logframe Indicators Summary"),
        ("13", "Cross-Dataset Synthesis"),
        ("14", "Theory of Change & Impact Evidence"),
        ("15", "Recommendations"),
        ("A", "Appendix: Sample Sizes & Methodology"),
    ]
    for num, title in toc_items:
        if num.isdigit():
            story.append(Paragraph(f"<b>{num}.</b>  {title}", styles['TOCSection']))
        else:
            story.append(Paragraph(f"<b>Appendix {num}.</b>  {title}", styles['TOCEntry']))
    story.append(PageBreak())

    # ==============================================================
    # 1. EXECUTIVE SUMMARY
    # ==============================================================
    story.append(Paragraph("1. Executive Summary", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph(
        "This midline report presents findings from the COSME (Conservation of Seascapes and Mangrove Ecosystems) "
        "and GJJ (Gender Just & Justice) programme operating across Kilifi and Kwale counties in coastal Kenya. "
        "The report synthesizes data from multiple survey instruments covering women's empowerment, men's engagement, "
        "climate and nature-based solutions (NbS), financial inclusion, disaster preparedness, forestry conservation, "
        "school WASH infrastructure, seaweed value chains, and VSLA group performance.",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "<b>Overall Performance:</b> 12 of 13 quantitative logframe indicators have <b>EXCEEDED</b> their midline targets, "
        "with 1 indicator <b>ON TRACK</b>. The programme demonstrates transformative impact across savings (+63pp VSLA participation), "
        "climate awareness (+36pp), women's decision-making (+38pp), and NbS participation (+45% average improvement).",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 5*mm))

    # KPI Cards
    story.append(Paragraph("<b>Programme-Wide Key Performance Indicators</b>", styles['SubSection']))
    story.append(kpi_card_table([
        ("Women VSLA Participation", "98.0%", "+54.4pp"),
        ("Climate Awareness", "96.3%", "+35.8pp"),
        ("Women Taking Loans", "79.1%", "+51.1pp"),
        ("Indicators Exceeded", "12/13", "92%"),
    ]))
    story.append(Spacer(1, 3*mm))
    story.append(kpi_card_table([
        ("Women Decision Involvement", "95.9%", "+38.3pp"),
        ("NbS Knowledge (Women)", "80.9%", "+60.2pp"),
        ("Men's CC Awareness", "100%", "+22.2pp"),
        ("Functional CFC Groups", "85.7%", "+32.2pp"),
    ]))
    story.append(Spacer(1, 5*mm))

    # Executive Summary Table — Key Highlights
    story.append(Paragraph("<b>Key Highlights Across All Surveys</b>", styles['SubSubSection']))
    exec_data = [
        ["Domain", "Key Finding", "Change", "Status"],
        ["Savings & Financial", "VSLA Participation: 43.6% → 98.0%", "+54.4pp", status_color("EXCEEDED")],
        ["Climate & NbS", "Climate awareness: 60.5% → 96.3%", "+35.8pp", status_color("EXCEEDED")],
        ["Women Empowerment", "HH decision involvement: 57.6% → 95.9%", "+38.3pp", status_color("EXCEEDED")],
        ["Men's Engagement", "Support female NbS: avg +60pp", "+60pp", status_color("EXCEEDED")],
        ["Disaster Preparedness", "Early warning access: 8.9% → 45.0%", "+36.1pp", status_color("EXCEEDED")],
        ["Forestry Groups", "Functional groups ≥70%: 53.5% → 85.7%", "+32.2pp", status_color("EXCEEDED")],
        ["Schools WASH", "Clean water access: 23.4% → 62.5%", "+39.1pp", status_color("EXCEEDED")],
        ["Training Knowledge", "Forest knowledge ≥70%: 50% → 94.7%", "+44.7pp", status_color("EXCEEDED")],
        ["Personal Skills", "Women skills & confidence: 32.7% → 46.3%", "+13.6pp", status_color("ON TRACK")],
    ]
    story.append(make_table(exec_data, [2.5, 5, 1.5, 1.5]))
    story.append(PageBreak())

    # ==============================================================
    # 2. WOMEN COSME SURVEY
    # ==============================================================
    story.append(Paragraph("2. Women COSME Survey", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph(
        "<b>Sample Size:</b> 345 Women  |  <b>Survey Type:</b> Midline  |  <b>Location:</b> Kilifi & Kwale Counties, Kenya",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 3*mm))

    # Women KPI Cards
    story.append(kpi_card_table([
        ("Women Taking Loans", "79.1%", "↑ 51.1pp from 28.0%"),
        ("VSLA Participation", "98.0%", "↑ 54.4pp from 43.6%"),
        ("Climate Knowledge", "96.3%", "↑ 35.8pp from 60.5%"),
        ("Joint Decisions", "58.8%", "↑ 13.8pp from 45.0%"),
    ]))
    story.append(Spacer(1, 5*mm))

    # 2.1 Logframe Indicators 
    story.append(Paragraph("2.1 Logframe Indicator Performance", styles['SubSection']))
    lf_women = [
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
    story.append(make_table(lf_women, [4, 1.2, 1.2, 1.2, 1.2, 1.5]))
    story.append(Spacer(1, 5*mm))

    # 2.2 Household Characteristics
    story.append(Paragraph("2.2 Household Characteristics", styles['SubSection']))
    hh_data = [
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
    story.append(make_table(hh_data, [4, 1.5, 1.5, 1.5]))
    story.append(Spacer(1, 5*mm))

    # Chart: Savings mechanisms
    p_savings = chart_bar_comparison(
        ['VSLA', 'Bank', 'MPESA', 'Informal\nGroup', 'Home'],
        [43.6, 14.5, 8.3, 6.9, 12.9],
        [98.0, 2.7, 1.7, 3.7, 0.0],
        'Women Savings Mechanisms — Baseline vs Midline',
        'women_savings'
    )
    story.append(Image(p_savings, width=420, height=180))
    story.append(Spacer(1, 5*mm))

    # 2.3 Shocks & Coping
    story.append(Paragraph("2.3 Shocks, Stresses & Coping Strategies", styles['SubSection']))
    shock_data = [
        ["Shock/Coping", "Baseline", "Midline", "Change"],
        ["Drought", "69.1%", "63.4%", "-5.7pp"],
        ["Heat/Cold Waves", "8.6%", "22.8%", "+14.2pp"],
        ["Flooding", "4.7%", "10.0%", "+5.3pp"],
        ["Very Large Impact", "32.7%", "20.0%", "-12.7pp"],
        ["Took Loan to Cope", "4.7%", "25.8%", "+21.1pp"],
        ["Used Savings", "11.2%", "15.8%", "+4.6pp"],
        ["Skipped Meals", "41.6%", "43.8%", "+2.2pp"],
    ]
    story.append(make_table(shock_data, [4, 1.5, 1.5, 1.5]))
    story.append(Spacer(1, 5*mm))

    # 2.4 Disaster Preparedness
    story.append(Paragraph("2.4 Disaster Preparedness", styles['SubSection']))
    dp_data = [
        ["Indicator", "Baseline", "Midline", "Change"],
        ["Know Disaster Plans", "4.7%", "37.8%", "+33.1pp"],
        ["Weather Access", "15.7%", "46.2%", "+30.5pp"],
        ["Early Warnings", "8.9%", "45.0%", "+36.1pp"],
        ["Tidal Forecasts", "10.3%", "33.1%", "+22.8pp"],
        ["Preparedness Training", "11.8%", "80.6%", "+68.8pp"],
    ]
    story.append(make_table(dp_data, [4, 1.5, 1.5, 1.5]))
    story.append(Spacer(1, 5*mm))

    # Chart: Disaster Preparedness
    p_dp = chart_bar_comparison(
        ['Know Plans', 'Weather\nAccess', 'Early\nWarnings', 'Tidal\nForecasts'],
        [4.7, 15.7, 8.9, 10.3],
        [37.8, 46.2, 45.0, 33.1],
        'Women — Disaster Preparedness Improvement',
        'women_disaster_prep'
    )
    story.append(Image(p_dp, width=420, height=180))
    story.append(Spacer(1, 5*mm))

    # 2.5 Asset Ownership
    story.append(Paragraph("2.5 Asset Ownership & Resources", styles['SubSection']))
    asset_data = [
        ["Asset", "Baseline", "Midline", "Change"],
        ["Cellphones", "47.0%", "62.5%", "+15.5pp"],
        ["Solar Panels", "9.2%", "31.6%", "+22.4pp"],
        ["Cooking Stoves", "3.5%", "39.7%", "+36.2pp"],
        ["Furniture", "17.3%", "23.1%", "+5.8pp"],
        ["Land Owned", "92.7%", "73.4%", "-19.3pp"],
        ["Land Leased", "6.0%", "19.6%", "+13.6pp"],
        ["Fertilizer Purchased", "84.7%", "98.4%", "+13.7pp"],
    ]
    story.append(make_table(asset_data, [4, 1.5, 1.5, 1.5]))
    story.append(Spacer(1, 5*mm))

    # 2.6 Time Use
    story.append(Paragraph("2.6 Time Use & Household Responsibilities", styles['SubSection']))
    time_data = [
        ["Activity", "Baseline", "Midline", "Change"],
        ["Unpaid Care (hrs/day)", "9.3", "7.7", "-1.6 hrs"],
        ["Productive Work (hrs/day)", "4.2", "4.9", "+0.7 hrs"],
        ["Community Work (hrs/day)", "0.4", "1.8", "+1.4 hrs"],
        ["Women Cooking Alone", "87.0%", "28.8%", "-58.2pp"],
        ["Women Cleaning Alone", "85.3%", "32.5%", "-52.8pp"],
        ["Women Fetching Water Alone", "76.6%", "22.2%", "-54.4pp"],
        ["Women Childcare Alone", "70.7%", "25.3%", "-45.4pp"],
    ]
    story.append(make_table(time_data, [4, 1.5, 1.5, 1.5]))
    story.append(Spacer(1, 3*mm))

    # Chart: Joint task beliefs
    p_joint = chart_bar_comparison(
        ['Cooking', 'Cleaning', 'Water\nFetch', 'Firewood', 'Childcare'],
        [12.5, 13.5, 21.4, 14.4, 26.5],
        [71.3, 66.9, 77.8, 60.6, 72.2],
        'Belief That Tasks Should Be Joint — % Agreeing',
        'women_joint_tasks'
    )
    story.append(Image(p_joint, width=420, height=180))
    story.append(Spacer(1, 5*mm))

    # 2.7 Decision Making
    story.append(Paragraph("2.7 Decision Making", styles['SubSection']))
    decision_data = [
        ["Decision Type", "Baseline", "Midline", "Change"],
        ["Market Access (Joint)", "13.5%", "48.1%", "+34.6pp"],
        ["Mangrove/Seaweed Work (Joint)", "9.8%", "49.1%", "+39.3pp"],
        ["Routine Purchases (Joint)", "25.6%", "50.6%", "+25.0pp"],
        ["Business/Loans (Joint)", "40.2%", "59.4%", "+19.2pp"],
        ["Child Education (Joint)", "58.1%", "59.7%", "+1.6pp"],
    ]
    story.append(make_table(decision_data, [4, 1.5, 1.5, 1.5]))
    story.append(Spacer(1, 5*mm))

    # 2.8 Climate & NbS
    story.append(Paragraph("2.8 Climate Change & Nature-Based Solutions", styles['SubSection']))
    climate_data = [
        ["Indicator", "Baseline", "Midline", "Change"],
        ["Climate Change Awareness", "60.5%", "96.3%", "+35.8pp"],
        ["NbS Knowledge", "23.1%", "77.8%", "+54.7pp"],
        ["Mangrove Active", "36.9%", "86.5%", "+49.6pp"],
        ["Seaweed Active", "19.8%", "74.7%", "+54.9pp"],
        ["Forest Management", "67.4%", "98.4%", "+31.0pp"],
        ["Increased Drought Knowledge", "54.7%", "75.9%", "+21.2pp"],
        ["Carbon Capture Knowledge", "2.8%", "33.1%", "+30.3pp"],
    ]
    story.append(make_table(climate_data, [4, 1.5, 1.5, 1.5]))
    story.append(Spacer(1, 3*mm))

    # Chart: NbS participation
    p_nbs = chart_bar_comparison(
        ['Mangrove', 'Seaweed', 'Forest\nMgmt', 'NbS\nKnowledge'],
        [36.9, 19.8, 67.4, 23.1],
        [86.5, 74.7, 98.4, 77.8],
        'Women — NbS Participation & Knowledge',
        'women_nbs'
    )
    story.append(Image(p_nbs, width=420, height=180))
    story.append(Spacer(1, 5*mm))

    # 2.9 Life Skills
    story.append(Paragraph("2.9 Life Skills & Psychosocial Empowerment", styles['SubSection']))
    life_skills_data = [
        ["Area", "Baseline", "Midline", "Change"],
        ["Positive Qualities (agree)", "88.5%", "97.2%", "+8.7pp"],
        ["Respected", "78.2%", "97.8%", "+19.6pp"],
        ["Life Meaning", "93.5%", "99.4%", "+5.9pp"],
        ["Can Lead", "59.1%", "94.1%", "+35.0pp"],
        ["Express with Community", "52.5%", "87.2%", "+34.7pp"],
        ["Convince Others", "61.5%", "92.5%", "+31.0pp"],
    ]
    story.append(make_table(life_skills_data, [4, 1.5, 1.5, 1.5]))
    story.append(Spacer(1, 5*mm))

    # 2.10 Social Norms
    story.append(Paragraph("2.10 Social Norms & Gender Attitudes", styles['SubSection']))
    story.append(Paragraph(
        "<i><b>Note:</b> Higher agreement with gendered norms indicates persistence of harmful attitudes. "
        "Some increases require further investigation and represent areas of concern.</i>",
        styles['SmallItalic']
    ))
    story.append(Spacer(1, 2*mm))
    norms_data = [
        ["Norm", "Baseline", "Midline", "Direction"],
        ["Man Provides Income", "40.2%", "75.4%", "⚠ Concerning increase"],
        ["Only Men Drive Boats", "23.5%", "88.1%", "⚠ Concerning increase"],
        ["Better Business Ideas (Men)", "64.4%", "74.1%", "Modest increase"],
        ["Harassment Victim Fault", "36.8%", "55.3%", "⚠ Concerning increase"],
        ["Mangrove = Women's Work", "73.7%", "89.1%", "Positive shift"],
        ["Seaweed = Women's Work", "70.5%", "91.3%", "Positive shift"],
    ]
    story.append(make_table(norms_data, [4, 1.5, 1.5, 2]))
    story.append(PageBreak())

    # ==============================================================
    # 3. MEN COSME SURVEY
    # ==============================================================
    story.append(Paragraph("3. Men COSME Survey", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph(
        "<b>Sample Size:</b> 267 Male Household Members  |  <b>Survey Type:</b> Midline  |  <b>Location:</b> Kilifi & Kwale Counties",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 3*mm))

    # KPI Cards
    story.append(kpi_card_table([
        ("CC Awareness", "100%", "↑ 22.2pp from 77.8%"),
        ("NbS Knowledge", "89.8%", "↑ 47.4pp from 42.4%"),
        ("Support Women NbS", "86.8%", "↑ 60.4pp avg"),
        ("Harmful Norms ↓", "-36.4pp", "Only men drive boats"),
    ]))
    story.append(Spacer(1, 5*mm))

    # 3.1 Logframe
    story.append(Paragraph("3.1 Logframe Indicator Performance", styles['SubSection']))
    lf_men = [
        ["Indicator", "Baseline", "Target", "Midline", "Change", "Status"],
        ["1230a. Male NbS/economic rights knowledge", "54.7%", "65.0%", "80.3%", "+25.6pp", status_color("EXCEEDED")],
        ["1230b. Women perceived equal by men (score)", "41.2/100", "55/100", "71/100", "+29.8 pts", status_color("EXCEEDED")],
    ]
    story.append(make_table(lf_men, [4, 1.2, 1.2, 1.2, 1.2, 1.5]))
    story.append(Spacer(1, 5*mm))

    # 3.2 Key Findings
    story.append(Paragraph("3.2 Key Findings Summary", styles['SubSection']))
    men_findings = [
        ["Domain", "Key Metric", "Change"],
        ["Climate & NbS", "CC awareness 77.8% → 100%, NbS 42.4% → 89.8%", "+22.2pp / +47.4pp"],
        ["Support Female Conservation", "Mangrove +51pp, Seaweed +68pp, Forest +62pp", "Avg +60pp"],
        ["Household Responsibility", "Joint cooking belief +50.5pp, cleaning +59.6pp", "+82.6% care time"],
        ["Joint Decision-Making", "Large purchases: 59.6% → 89.8%", "+30.2pp"],
        ["Harmful Norms Reduction", "Harassment victim fault: 67.6% → 30.7%", "-36.9pp"],
        ["Time Investment", "Unpaid care: 2.3 → 4.2 hrs/day", "+82.6%"],
        ["Savings", "Personally saving: 31.4% → 68.2%", "+36.8pp"],
    ]
    story.append(make_table(men_findings, [3, 5, 2]))
    story.append(Spacer(1, 5*mm))

    # Chart: Men's support for women's NbS
    p_men_nbs = chart_bar_comparison(
        ['Mangrove\nRestoration', 'Seaweed\nFarming', 'Forest\nManagement'],
        [29.7, 15.7, 33.7],
        [80.7, 83.9, 95.8],
        "Men's Support for Women's NbS Participation",
        'men_support_nbs',
        colors=['#FFCC80', '#FF6F00']
    )
    story.append(Image(p_men_nbs, width=420, height=180))
    story.append(Spacer(1, 5*mm))

    # 3.3 Harmful Norms Reduction
    story.append(Paragraph("3.3 Harmful Norms Reduction (Men)", styles['SubSection']))
    norms_men = [
        ["Norm", "Baseline", "Midline", "Change"],
        ["Only men earn income", "63.1%", "28.4%", "-34.7pp ✓"],
        ["Only men drive boats", "59.2%", "22.7%", "-36.4pp ✓"],
        ["Harassment victim fault", "67.6%", "30.7%", "-36.9pp ✓"],
        ["Husband controls woman income", "41.9%", "19.3%", "-22.6pp ✓"],
        ["Men should do domestic work", "42.1%", "71.8%", "+29.7pp ✓"],
        ["Women should participate in decisions", "48.3%", "82.6%", "+34.3pp ✓"],
    ]
    story.append(make_table(norms_men, [4, 1.5, 1.5, 2]))
    story.append(Spacer(1, 5*mm))

    # Chart: Men harmful norms decrease
    p_norms = chart_bar_comparison(
        ['Men earn\nincome', 'Men drive\nboats', 'Harassment\nvictim fault', 'Husband\ncontrols $'],
        [63.1, 59.2, 67.6, 41.9],
        [28.4, 22.7, 30.7, 19.3],
        "Men — Harmful Norms Reduction (Lower = Better)",
        'men_harmful_norms',
        colors=['#EF9A9A', '#C62828']
    )
    story.append(Image(p_norms, width=420, height=180))
    story.append(PageBreak())

    # ==============================================================
    # 4. GJJ KAP WOMEN
    # ==============================================================
    story.append(Paragraph("4. GJJ KAP Women Survey", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph(
        "<b>Sample Size:</b> 312 Women  |  <b>Survey Type:</b> Endline (Knowledge, Attitudes & Practices)",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 3*mm))

    story.append(kpi_card_table([
        ("Self-Esteem (SA)", "52.6%", "↑ 19.1pp from 33.5%"),
        ("Equal Perception", "48.2%", "↑ 27.8pp from 20.4%"),
        ("HH Chore Support", "64.7%", "↑ 23.3pp from 41.4%"),
        ("Decision Talk", "81.7%", "↑ 21.5pp from 60.2%"),
    ]))
    story.append(Spacer(1, 5*mm))

    # Domain findings
    gjj_w_data = [
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
    story.append(make_table(gjj_w_data, [2, 4, 1.3, 1.3, 1.5]))
    story.append(Spacer(1, 3*mm))

    # Household Decision Types
    story.append(Paragraph("Household Decision Types", styles['SubSubSection']))
    hh_dec = [
        ["Decision Type", "Baseline", "Endline", "Change"],
        ["Purchase household assets", "17.6%", "22.0%", "+4.4pp"],
        ["Send/remove child from school", "39.8%", "50.6%", "+10.8pp"],
        ["Invest in business", "18.4%", "22.1%", "+3.7pp"],
        ["Seek healthcare", "6.6%", "20.3%", "+13.7pp"],
    ]
    story.append(make_table(hh_dec, [4, 1.5, 1.5, 1.5]))
    story.append(PageBreak())

    # ==============================================================
    # 5. GJJ KAP MEN
    # ==============================================================
    story.append(Paragraph("5. GJJ KAP Men Survey", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph(
        "<b>Sample Size:</b> 289 Men  |  <b>Survey Type:</b> Endline (Knowledge, Attitudes & Practices)",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 3*mm))

    story.append(kpi_card_table([
        ("Self-Responsibility", "70.3%", "↑ 20.2pp from 50.1%"),
        ("Respected by Partner", "83.5%", "↑ 53.4pp from 30.1%"),
        ("Always Does Chores", "42.2%", "↑ 24.5pp from 17.7%"),
        ("Decision Conversations", "97.1%", "↑ 9.2pp from 87.9%"),
    ]))
    story.append(Spacer(1, 5*mm))

    gjj_m_data = [
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
    story.append(make_table(gjj_m_data, [2, 4, 1.3, 1.3, 1.5]))
    story.append(PageBreak())

    # ==============================================================
    # 6. FORESTRY GROUPS
    # ==============================================================
    story.append(Paragraph("6. Forestry Groups Assessment", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph(
        "<b>Scope:</b> 28 Community Forest Conservation Groups assessed (Baseline: 43 groups)  |  <b>Survey Type:</b> Midline",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 3*mm))

    story.append(kpi_card_table([
        ("Functionality ≥70%", "85.7%", "↑ 32.2pp from 53.5%"),
        ("Gender Domain Score", "63.5%", "↑ 20.7pp from 42.8%"),
        ("Income Generating", "62.5%", "↑ 25.0pp from 37.5%"),
        ("Group Registration", "85.0%", "↑ 12.5pp from 72.5%"),
    ]))
    story.append(Spacer(1, 5*mm))

    # Logframe
    story.append(Paragraph("6.1 Logframe Indicator", styles['SubSection']))
    lf_forest = [
        ["Indicator", "Baseline", "Target", "Midline", "Change", "Status"],
        ["1130b. Functional groups (≥70% score)", "53.5%", "70.0%", "85.7%", "+32.2pp", status_color("EXCEEDED")],
    ]
    story.append(make_table(lf_forest, [4, 1.2, 1.2, 1.2, 1.2, 1.5]))
    story.append(Spacer(1, 5*mm))

    # Domain Scores
    story.append(Paragraph("6.2 Domain Scores", styles['SubSection']))
    domain_data = [
        ["Domain", "Baseline", "Midline", "Change"],
        ["Management", "78.6%", "78.0%", "-0.6pp"],
        ["Gender", "32.9%", "85.5%", "+52.6pp"],
        ["Effectiveness", "72.0%", "90.1%", "+18.1pp"],
        ["Overall", "70.6", "84.2", "+13.6pp"],
    ]
    story.append(make_table(domain_data, [3, 1.5, 1.5, 1.5]))
    story.append(Spacer(1, 3*mm))

    # Chart: Forestry Domain Comparison
    p_forest = chart_bar_comparison(
        ['Management', 'Gender', 'Effectiveness', 'Overall'],
        [78.6, 32.9, 72.0, 70.6],
        [78.0, 85.5, 90.1, 84.2],
        'Forestry Group Domain Scores — Baseline vs Midline',
        'forestry_domains',
        colors=['#A5D6A7', '#1B5E20']
    )
    story.append(Image(p_forest, width=420, height=180))
    story.append(Spacer(1, 5*mm))

    # Forest Condition
    story.append(Paragraph("6.3 Forest Condition & Conservation", styles['SubSection']))
    forest_cond = [
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
    story.append(make_table(forest_cond, [3.5, 1.5, 1.5, 2]))
    story.append(PageBreak())

    # ==============================================================
    # 7. PRE/POST TESTS
    # ==============================================================
    story.append(Paragraph("7. Pre/Post Tests — Forest & Mangrove Training", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))

    # Forest Conservation Training
    story.append(Paragraph("7.1 Forest Conservation Training", styles['SubSection']))
    story.append(Paragraph(
        "<b>Pre-Test Participants:</b> 546  |  <b>Post-Test Participants:</b> 909",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 3*mm))

    lf_prepost_forest = [
        ["Indicator", "Pre-Test", "Target", "Post-Test", "Change", "Status"],
        ["1130a. Adequate knowledge (≥70%)", "50.0%", "68.0%", "94.7%", "+44.7pp", status_color("EXCEEDED")],
    ]
    story.append(make_table(lf_prepost_forest, [4, 1.2, 1.2, 1.2, 1.2, 1.5]))
    story.append(Spacer(1, 3*mm))

    prepost_forest = [
        ["Metric", "Pre-Test", "Post-Test", "Change"],
        ["Average Score", "65.2%", "85.4%", "+20.2pp"],
        ["≥70% Threshold", "50.0%", "94.7%", "+44.7pp"],
        ["≥80% Threshold", "32.9%", "85.7%", "+52.8pp"],
        ["Forest Ecosystems", "56.6%", "91.5%", "+34.9pp"],
        ["Ecosystem Services", "—", "99.7%", "Highest"],
        ["Carbon Sequestration", "—", "99.2%", "High"],
    ]
    story.append(make_table(prepost_forest, [4, 1.5, 1.5, 1.5]))
    story.append(Spacer(1, 5*mm))

    # Mangrove Training
    story.append(Paragraph("7.2 Mangrove Restoration Training", styles['SubSection']))
    lf_prepost_mang = [
        ["Indicator", "Pre-Test", "Target", "Post-Test", "Change", "Status"],
        ["1110a. Adequate mangrove knowledge", "36.9%", "57.0%", "81.9%", "+45.0pp", status_color("EXCEEDED")],
    ]
    story.append(make_table(lf_prepost_mang, [4, 1.2, 1.2, 1.2, 1.2, 1.5]))
    story.append(Spacer(1, 3*mm))

    mang_location = [
        ["Metric", "Pre-Test", "Post-Test", "Change"],
        ["Overall Adequate Knowledge", "36.9%", "81.5%", "+44.6pp"],
        ["Kilifi", "21.1%", "80.1%", "+59.0pp"],
        ["Kwale", "53.7%", "83.1%", "+29.4pp"],
        ["Female", "34.7%", "87.4%", "+52.7pp"],
        ["Male", "38.2%", "80.2%", "+42.0pp"],
    ]
    story.append(make_table(mang_location, [4, 1.5, 1.5, 1.5]))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "<b>Key Insight:</b> Women outperformed men by 7.2pp at post-test despite starting 3.5pp below.",
        styles['BodyText2']
    ))

    # Chart: Pre/Post comparison
    p_prepost = chart_bar_comparison(
        ['Forest\n≥70%', 'Forest\n≥80%', 'Mangrove\nOverall', 'Mangrove\nKilifi', 'Mangrove\nKwale'],
        [50.0, 32.9, 36.9, 21.1, 53.7],
        [94.7, 85.7, 81.5, 80.1, 83.1],
        'Pre/Post Test Knowledge Achievement',
        'prepost_tests',
        colors=['#CE93D8', '#6A1B9A']
    )
    story.append(Image(p_prepost, width=420, height=180))
    story.append(PageBreak())

    # ==============================================================
    # 8. SCHOOLS DASHBOARD
    # ==============================================================
    story.append(Paragraph("8. Schools Dashboard", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph(
        "<b>Scope:</b> 65 schools assessed  |  <b>Counties:</b> Kwale (35) & Kilifi (30)  |  <b>Total Students:</b> 44,301",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 3*mm))

    # Logframe
    lf_schools = [
        ["Indicator", "Baseline", "Target", "Midline", "Change", "Status"],
        ["1310c. Schools with clean water access", "23.4%", "60.0%", "62.5%", "+39.1pp", status_color("EXCEEDED")],
    ]
    story.append(make_table(lf_schools, [4, 1.2, 1.2, 1.2, 1.2, 1.5]))
    story.append(Spacer(1, 5*mm))

    # Enrollment
    story.append(Paragraph("8.1 School Enrollment", styles['SubSection']))
    enroll_data = [
        ["County", "Schools", "Boys", "Girls", "Total"],
        ["Kwale", "35", "9,960", "9,433", "19,393"],
        ["Kilifi", "30", "12,739", "12,169", "24,908"],
        ["Total", "65", "22,699", "21,602", "44,301"],
    ]
    story.append(make_table(enroll_data, [2, 1.5, 2, 2, 2]))
    story.append(Spacer(1, 5*mm))

    # Water & WASH
    story.append(Paragraph("8.2 Water Infrastructure & WASH", styles['SubSection']))
    water_data = [
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
    story.append(make_table(water_data, [4, 1.5, 1.5, 2]))
    story.append(Spacer(1, 5*mm))

    # 4K Clubs
    story.append(Paragraph("8.3 4K Clubs", styles['SubSection']))
    clubs_data = [
        ["Metric", "Value"],
        ["Schools with clubs", "97%"],
        ["Total members", "5,065"],
        ["Female members", "2,917 (57.6%)"],
        ["Male members", "2,148 (42.4%)"],
        ["Materials received", "92%"],
        ["Environmental initiatives", "81.5%"],
    ]
    story.append(make_table(clubs_data, [5, 5]))
    story.append(Spacer(1, 3*mm))

    # Chart: School enrollment
    p_enroll = chart_pie(
        ['Boys - Kwale', 'Girls - Kwale', 'Boys - Kilifi', 'Girls - Kilifi'],
        [9960, 9433, 12739, 12169],
        'School Enrollment Distribution (n=44,301)',
        'school_enrollment',
        colors=['#42A5F5', '#90CAF9', '#1565C0', '#64B5F6']
    )
    story.append(Image(p_enroll, width=280, height=220))
    story.append(PageBreak())

    # ==============================================================
    # 9. SEAWEED ASSESSMENT
    # ==============================================================
    story.append(Paragraph("9. Seaweed Assessment", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph(
        "<b>Scope:</b> 19 groups  |  <b>610 active female members</b>  |  <b>Assessment Period:</b> July 2025",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 3*mm))

    seaweed_data = [
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
    story.append(make_table(seaweed_data, [5, 5]))
    story.append(Spacer(1, 3*mm))

    # Logframe
    story.append(Paragraph("Logframe Indicator 1100c", styles['SubSubSection']))
    sea_lf = [
        ["Measure", "Count"],
        ["Groups with regenerative production", "17"],
        ["Groups with value addition", "13"],
        ["Groups with commercialization", "9"],
    ]
    story.append(make_table(sea_lf, [6, 4]))
    story.append(Spacer(1, 3*mm))

    # Chart: Seaweed challenges
    p_sea = chart_horizontal_bar(
        ['Transport', 'Demand', 'Pricing'],
        [90, 80, 60],
        'Seaweed Groups — Top Challenges (% Reporting)',
        'seaweed_challenges',
        color='#00897B'
    )
    story.append(Image(p_sea, width=420, height=140))
    story.append(Spacer(1, 5*mm))

    # ==============================================================
    # 10. VSLA MONITORING
    # ==============================================================
    story.append(Paragraph("10. VSLA Monitoring", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph(
        "<b>Scope:</b> 211 assessments  |  <b>173 unique groups</b>  |  <b>Counties:</b> Kilifi & Kwale",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 3*mm))

    vsla_data = [
        ["Indicator", "Value"],
        ["1220a. % women actively saving", "78.6%"],
        ["Assessments conducted", "211"],
        ["Unique groups", "173"],
        ["Dashboard pages", "6 (Overview, Participation, Savings, Loans, Social Fund, Loan Use)"],
        ["Filters available", "County, Reporting Cycle (1-3), Quarter (Q2-Q4), Group"],
    ]
    story.append(make_table(vsla_data, [5, 5]))
    story.append(PageBreak())

    # ==============================================================
    # 11. PROJECT OUTPUTS — TRAINING COMPLETION
    # ==============================================================
    story.append(Paragraph("11. Project Outputs — Training Completion", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))

    # Mangrove Training
    story.append(Paragraph("11.1 Mangrove Training (Output 1112)", styles['SubSection']))
    mang_train = [
        ["Metric", "Value", "Target", "Achievement"],
        ["Groups formed", "42", "40", "105%"],
        ["Members registered", "1,344", "1,200", "112%"],
        ["Female members", "973 (72%)", "—", "—"],
        ["Male members", "371 (28%)", "—", "—"],
        ["Grand Total Completed", "842", "1,200", "70%"],
    ]
    story.append(make_table(mang_train, [3, 2, 2, 2]))
    story.append(Spacer(1, 3*mm))

    mang_modules = [
        ["Module", "Target", "Completed", "Target %", "Reg %"],
        ["Module 1", "1,200", "1,121", "93%", "83%"],
        ["Module 2", "1,200", "961", "80%", "72%"],
        ["Module 3", "1,200", "842", "70%", "63%"],
        ["Module 4", "1,200", "753", "63%", "56%"],
        ["Module 5", "1,200", "535", "45%", "40%"],
    ]
    story.append(make_table(mang_modules, [2, 1.5, 2, 1.5, 1.5]))
    story.append(Spacer(1, 5*mm))

    # Forestry Training
    story.append(Paragraph("11.2 Forestry Training (Output 1131)", styles['SubSection']))
    forest_train = [
        ["Metric", "Value", "Target", "Achievement"],
        ["Groups formed", "52", "45", "116%"],
        ["Members registered", "1,440", "1,350", "107%"],
        ["Female members", "1,141 (79%)", "—", "—"],
        ["Male members", "299 (21%)", "—", "—"],
        ["Grand Total Completed", "1,030", "1,350", "76%"],
    ]
    story.append(make_table(forest_train, [3, 2, 2, 2]))
    story.append(Spacer(1, 5*mm))

    # Seaweed Training
    story.append(Paragraph("11.3 Seaweed Training (Output 1122)", styles['SubSection']))
    sea_train = [
        ["Metric", "Value", "Target", "Achievement"],
        ["Groups formed", "19", "20", "95%"],
        ["Members registered", "842", "600", "140%"],
        ["Female members", "651 (77%)", "—", "—"],
        ["Grand Total Completed", "462", "600", "77%"],
    ]
    story.append(make_table(sea_train, [3, 2, 2, 2]))
    story.append(Spacer(1, 5*mm))

    # VSLA Training
    story.append(Paragraph("11.4 VSLA Training (20 Modules)", styles['SubSection']))
    vsla_train = [
        ["Metric", "Value"],
        ["Target", "3,000"],
        ["Registered", "2,765"],
        ["Female completion avg", "1,834 (62% target / 67% registered)"],
        ["Module range", "20% – 71% completion"],
        ["Highest module", "Module 7 (2,140 = 71%)"],
        ["Lowest module", "Module 20 (613 = 20%)"],
    ]
    story.append(make_table(vsla_train, [4, 6]))
    story.append(Spacer(1, 3*mm))

    # Chart: Training outputs comparison
    p_training = chart_bar_comparison(
        ['Mangrove\nGroups', 'Forestry\nGroups', 'Seaweed\nGroups', 'Mangrove\nMembers', 'Forestry\nMembers'],
        [40, 45, 20, 100, 100],  # targets normalized to %
        [105, 116, 95, 112, 107],  # achievement %
        'Training Output Achievement (% of Target)',
        'training_outputs',
        colors=['#FFCC80', '#E65100']
    )
    story.append(Image(p_training, width=420, height=180))
    story.append(PageBreak())

    # ==============================================================
    # 12. LOGFRAME INDICATORS SUMMARY
    # ==============================================================
    story.append(Paragraph("12. Logframe Indicators — Complete Summary", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph(
        "<b>Overall: 12 of 13 quantitative indicators EXCEEDED targets. 1 indicator ON TRACK.</b>",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 5*mm))

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
    story.append(Spacer(1, 5*mm))

    # Logframe Achievement Chart
    ind_labels = [
        '1200a', '1200c', '1210a', '1210b', '1210c',
        '1220a', '1220b', '1230a', '1230b', '1130b', '1130a', '1110a', '1310c'
    ]
    baselines = [57.6, 41.2, 20.7, 32.7, 42.1, 28.8, 50.8, 54.7, 41.2, 53.5, 50.0, 36.9, 23.4]
    tgts = [65, 50, 55, 55, 55, 70, 80, 65, 55, 70, 68, 57, 60]
    results = [95.9, 53.8, 80.9, 46.3, 64.7, 91.9, 83.1, 80.3, 71.0, 85.7, 94.7, 81.9, 62.5]

    p_lf = chart_logframe_achievement(ind_labels, baselines, tgts, results, 'logframe_all')
    story.append(Image(p_lf, width=460, height=280))
    story.append(PageBreak())

    # ==============================================================
    # 13. CROSS-DATASET SYNTHESIS
    # ==============================================================
    story.append(Paragraph("13. Cross-Dataset Synthesis", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph(
        "This section provides a comparative analysis across all survey instruments, identifying patterns, "
        "convergences, and areas requiring attention.",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 5*mm))

    # Radar chart: Domain comparison
    radar_cats = ['Savings', 'Climate\nNbS', 'Gender\nEmpowerment', 'Disaster\nPrep', 'Decision\nMaking', 'Life Skills']
    p_radar = chart_radar(
        radar_cats,
        [
            [91.9, 96.3, 95.9, 37.8, 58.8, 46.3],  # Women Midline
            [68.2, 100, 71.0, 42.8, 89.8, 87.3],    # Men Midline
        ],
        ['Women Midline', 'Men Midline'],
        'Domain Performance — Women vs Men (Midline)',
        'synthesis_radar'
    )
    story.append(Image(p_radar, width=320, height=320))
    story.append(Spacer(1, 5*mm))

    synthesis_data = [
        ["Domain", "Women BL", "Women ML", "Men BL", "Men ML", "Convergence"],
        ["Savings/VSLA", "43.6%", "98.0%", "18.5%", "42.7%", "Women lead"],
        ["Climate Awareness", "60.5%", "96.3%", "77.8%", "100%", "Men converged"],
        ["NbS Knowledge", "23.1%", "77.8%", "42.4%", "89.8%", "Men ahead"],
        ["Disaster Prep", "4.7%", "37.8%", "6.2%", "42.8%", "Men slightly ahead"],
        ["Joint Decisions", "30.6%", "48.8%", "59.6%", "89.8%", "Strong convergence"],
        ["Unpaid Care", "9.3 hrs", "7.7 hrs", "2.3 hrs", "4.2 hrs", "Gap narrowing"],
    ]
    story.append(make_table(synthesis_data, [2.5, 1.3, 1.3, 1.3, 1.3, 2.5]))
    story.append(Spacer(1, 5*mm))

    # Key synthesis findings
    story.append(Paragraph("<b>Key Cross-Dataset Findings:</b>", styles['SubSection']))
    findings_text = [
        "• <b>Financial Inclusion Transformation:</b> Women's VSLA participation (98%) far exceeds men's group saving (42.7%), indicating women lead household financial inclusion.",
        "• <b>Climate Knowledge Convergence:</b> Men's climate awareness reached 100% (from 77.8%), while women reached 96.3% (from 60.5%), showing effective training for both genders.",
        "• <b>Decision-Making Progress:</b> Joint decisions increased for both genders, with men reporting 89.8% support for joint large purchases — higher than women's self-reported 48.8%, suggesting attitudinal shift may precede behavioral change.",
        "• <b>Care Work Redistribution:</b> Women's unpaid care dropped 1.6 hrs/day while men's increased by 1.9 hrs/day — a significant structural shift.",
        "• <b>Social Norms Tension:</b> Women's survey shows concerning increases in some gendered norms (men as providers: 40.2%→75.4%), while men's survey shows decreases. This discrepancy warrants investigation.",
        "• <b>NbS Participation:</b> Both genders show strong uptake in conservation activities, with forest management near universal participation (98.4% women, 95.8% men support).",
    ]
    for f in findings_text:
        story.append(Paragraph(f, styles['BodyText2']))
    story.append(PageBreak())

    # ==============================================================
    # 14. THEORY OF CHANGE & IMPACT EVIDENCE
    # ==============================================================
    story.append(Paragraph("14. Theory of Change & Impact Evidence", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph(
        "The programme's Theory of Change posits three intermediate outcomes validated through the midline data:",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 3*mm))

    toc_evidence = [
        ["Outcome", "Description", "Evidence Strength"],
        ["1100 — NbS Adoption", "Community adoption of nature-based solutions through mangrove, seaweed, and forest conservation", "Strong — 89.5% regenerative practices, 86.5% mangrove active"],
        ["1200 — Women's Agency", "Economic empowerment, decision-making, and resource access for women", "Strong — 95.9% decision involvement, 91.9% saving actively"],
        ["1300 — Governance", "Institutional structures supporting gender-responsive NbS", "Moderate — 85.7% functional groups, 62.5% schools WASH"],
    ]
    story.append(make_table(toc_evidence, [2.5, 5, 3]))
    story.append(Spacer(1, 5*mm))

    # Endline Projections
    story.append(Paragraph("14.1 Endline Projections (3 Scenarios)", styles['SubSection']))
    proj_data = [
        ["Scenario", "Assumption", "Projection"],
        ["Maintained", "Current trajectory sustained", "50% of midline gains maintained at endline"],
        ["Accelerated", "Intensified programming & engagement", "80% achievement of all targets"],
        ["Regression", "Programme disruption / external shocks", "20% loss from midline values"],
    ]
    story.append(make_table(proj_data, [2, 4, 4]))
    story.append(Spacer(1, 5*mm))

    # Methodology
    story.append(Paragraph("14.2 Methodology Notes", styles['SubSection']))
    method_text = [
        "• Theory of Change framework used for cross-outcome validation",
        "• Projection model based on baseline-midline trajectory analysis",
        "• Data sources: Household surveys, group assessments, training records, school evaluations",
        "• <b>Limitations:</b> Self-reported data, seasonal variation, attribution challenges",
        "• <b>Tension detected:</b> Social norms data (Women Tab J) shows concerning increases in some gendered norms that require further investigation",
    ]
    for m in method_text:
        story.append(Paragraph(m, styles['BodyText2']))
    story.append(PageBreak())

    # ==============================================================
    # 15. RECOMMENDATIONS
    # ==============================================================
    story.append(Paragraph("15. Recommendations", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))

    recs = [
        ("<b>1. Address Social Norms Paradox:</b>", 
         "The increase in gendered norms among women (e.g., 'Man Provides Income' +35.2pp) despite programme interventions requires urgent investigation. Consider focus group discussions to understand if this reflects awareness of the norm vs. endorsement."),
        ("<b>2. Accelerate Personal Skills & Confidence (Indicator 1210b):</b>",
         "The only ON TRACK indicator (46.3% vs 55% target) needs intensified life skills programming. Consider peer mentoring, success storytelling, and confidence-building workshops."),
        ("<b>3. Strengthen Seaweed Value Chain:</b>",
         "Only 47.4% of groups are selling, 5.3% have formal agreements, and 90% report transport as a challenge. Prioritize market linkages, buyer agreements, and transport solutions."),
        ("<b>4. Sustain Men's Engagement:</b>",
         "Men's transformation is remarkable (+82.6% care time increase, -36pp harmful norms). Institutionalize men's engagement through peer networks and community champions."),
        ("<b>5. Scale VSLA Success:</b>",
         "98% participation and 79.1% loan access demonstrate transformative financial inclusion. Expand to remaining communities and link to formal financial services."),
        ("<b>6. Address Training Attrition:</b>",
         "Module completion drops significantly (Mangrove M1:93% → M5:45%). Investigate reasons for dropout and implement retention strategies especially for later modules."),
        ("<b>7. School WASH Sustainability:</b>",
         "Only 20% of schools have maintenance budgets. Develop school-community partnerships for infrastructure sustainability."),
        ("<b>8. Disaster Preparedness Deepening:</b>",
         "While knowledge improved significantly (+33pp), only 26.9% directly participate in disaster planning. Move from awareness to actionable preparedness."),
    ]
    for title, body in recs:
        story.append(Paragraph(title, styles['SubSubSection']))
        story.append(Paragraph(body, styles['BodyText2']))
        story.append(Spacer(1, 3*mm))
    story.append(PageBreak())

    # ==============================================================
    # APPENDIX A: SAMPLE SIZES & METHODOLOGY
    # ==============================================================
    story.append(Paragraph("Appendix A: Sample Sizes & Methodology", styles['SectionTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))

    sample_data = [
        ["Dataset", "Sample Size", "Type"],
        ["Women COSME", "345 women", "Midline household survey"],
        ["Men COSME", "267 men", "Midline household survey"],
        ["GJJ Women KAP", "312 women", "Endline KAP survey"],
        ["GJJ Men KAP", "289 men", "Endline KAP survey"],
        ["Forestry Groups", "28 groups (BL: 43)", "Group functionality assessment"],
        ["Pre/Post Forest", "546 pre / 909 post", "Knowledge test"],
        ["Pre/Post Mangrove", "By location/gender", "Knowledge test"],
        ["VSLA Monitoring", "211 assessments / 173 groups", "Group monitoring"],
        ["Seaweed Assessment", "19 groups / 610 women", "Group assessment"],
        ["Schools Dashboard", "65 schools / 44,301 students", "School assessment"],
        ["4K Clubs", "5,065 members (F:2,917 M:2,148)", "Club monitoring"],
    ]
    story.append(make_table(sample_data, [3, 3.5, 4]))
    story.append(Spacer(1, 10*mm))

    story.append(Paragraph(
        "<i>Data extracted from: Women_Survey_Professional_Dashboard.html & Men_Survey_Professional_Dashboard.html</i>",
        styles['SmallItalic']
    ))
    story.append(Paragraph(
        f"<i>Report generated: {datetime.now().strftime('%d %B %Y, %H:%M')}</i>",
        styles['SmallItalic']
    ))
    story.append(Paragraph(
        "<i>Programme: Plan International Kenya — COSME & Gender Just & Justice Programme</i>",
        styles['SmallItalic']
    ))
    story.append(Paragraph(
        "<i>Counties: Kilifi & Kwale, Coastal Kenya</i>",
        styles['SmallItalic']
    ))

    # ---- BUILD ----
    doc.build(
        story,
        onFirstPage=cover_page,
        onLaterPages=header_footer,
    )
    print(f"\n{'='*60}")
    print(f"  PDF REPORT GENERATED SUCCESSFULLY")
    print(f"  Path: {PDF_PATH}")
    print(f"  Pages: ~{len(story)//15 + 2} pages (estimated)")
    print(f"{'='*60}\n")

    # Cleanup chart images
    import shutil
    try:
        shutil.rmtree(CHART_DIR)
    except:
        pass

if __name__ == "__main__":
    build_report()
