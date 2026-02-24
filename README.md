# COSME Data Analysis & Results Dashboard

A comprehensive data analysis and visualization platform for the **COSME (Community Oriented Social Monitoring & Evaluation)** project. This repository contains interactive dashboards, data analysis scripts, and reporting tools for community development program monitoring.

---

## 📊 Dashboards

| Dashboard | Description |
|-----------|-------------|
| **COSME Results Dashboard** | Main interactive dashboard with multi-tab views covering overview, gap analysis, production data, rankings, challenges, and projections |
| **Forestry Conservation Dashboard** | Streamlit + Plotly dashboard comparing baseline vs midline assessments for Community Forest Conservation Groups |
| **Women Survey Dashboard** | Professional dashboard for women's baseline/midline survey results |
| **Men Survey Dashboard** | Professional dashboard for men's baseline/midline survey results |
| **MERL Workplan Tracker** | Monitoring, Evaluation, Research & Learning workplan tracking tool |
| **Donor Report** | Donor-facing impact and progress report |
| **Solvatten Impact Dashboard** | Complete impact analysis for the Solvatten water treatment program |
| **VSLA Monitoring** | Village Savings & Loan Association data monitoring and analysis |

## 🛠️ Tech Stack

- **Frontend:** HTML, CSS, JavaScript, Chart.js
- **Backend/Analysis:** Python, Pandas, NumPy
- **Visualization:** Plotly, Chart.js, Streamlit
- **Data Sources:** CSV, Excel (`.xlsx`)

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/muiruri126-bot/COSME-Data-Analysis-Results-Dashboard.git
cd COSME-Data-Analysis-Results-Dashboard

# Install dependencies
pip install -r requirements.txt
```

### Running the Forestry Dashboard (Streamlit)

```bash
streamlit run forestry_dashboard.py
```

### Viewing HTML Dashboards

Open any `.html` dashboard file directly in your browser:

- `result_dashboard (19).html` — Main COSME Results Dashboard
- `Women_Survey_Professional_Dashboard.html` — Women's Survey Dashboard
- `Men_Survey_Professional_Dashboard.html` — Men's Survey Dashboard
- `donor_report.html` — Donor Report
- `merl_workplan_tracker.html` — MERL Workplan Tracker

## 📁 Project Structure

```
├── result_dashboard (19).html       # Main COSME Results Dashboard
├── forestry_dashboard.py            # Streamlit Forestry Dashboard
├── Women_Survey_Professional_Dashboard.html
├── Men_Survey_Professional_Dashboard.html
├── donor_report.html
├── merl_workplan_tracker.html
├── solvatten_impact_complete.html
├── midline.html
├── ranking_335_members.html
├── analyze_csv.py                   # CSV data analysis scripts
├── analyze_latest.py
├── analyze_member_rankings.py
├── member_category_analysis.py
├── member_summary.py
├── requirements.txt                 # Python dependencies
├── Training Manuals/                # Training documentation
└── VSLA Data_Monitoring_06.10.2025.csv
```

## 📈 Features

- **Interactive Charts** — Dynamic visualizations with Chart.js and Plotly
- **Multi-Tab Navigation** — Organized data views across different analysis areas
- **Filter & Drill-Down** — Filter data by region, group, time period, and more
- **Baseline vs Midline Comparison** — Track progress between assessment periods
- **Theme Selector** — Multiple color palettes for the Forestry Dashboard
- **Responsive Design** — Works across desktop and mobile devices
- **Export Capabilities** — Generate reports for donors and stakeholders

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-analysis`)
3. Commit your changes (`git commit -m 'Add new analysis module'`)
4. Push to the branch (`git push origin feature/new-analysis`)
5. Open a Pull Request

## 📄 License

This project is for internal use by the COSME program team.

---

*Built for community impact monitoring and evidence-based decision making.*
