# Page Documentation: Healthcare Analytics & Reports (`admin_report.md`)

## 1. PAGE OVERVIEW
The **Healthcare Analytics & Reports Page** is the central intelligence and reporting suite for the MaatriCare platform. It compiles data across maternal health, high-risk pregnancies, pediatric development, vaccination compliance, and supplementary nutrition supplies. It includes interactive Chart.js visualizations, high-risk patient watchlists, Panchayath-level performance tables, 1-click demo data generation, and downloadable publication-grade PDF/text reports.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Executive KPIs: Total Mothers, Active Pregnancies, High-Risk Cases, Total Children, Immunization Coverage Rate (%), Kits Supplied, Kits in Stock.
  - High-Risk Pregnancy Watchlist: Mothers with severe anemia (Hb < 10 g/dL), hypertension (BP >= 140/90), or advanced maternal age.
  - Missed Immunization Watchlist: Children overdue for critical vaccines.
  - Panchayath Performance Table: Comparative statistics by local administrative area.
  - Nutrition Kit Supply Chain Breakdown: Kit inventory by category.
- **Data Export Options:**
  - PDF Generation via ReportLab engine (`/myapp/export_report_pdf/`).
  - Formatted Text Summary Report (`/myapp/export_report_text/`).
- **Data Format Example (Analytics JSON Context):**
```json
{
  "summary_kpis": {
    "total_registered": 142,
    "total_pregnant": 68,
    "high_risk_count": 9,
    "vax_coverage_pct": 91.2,
    "kits_supplied": 480
  },
  "high_risk_watchlist": [
    {"name": "Meera Das", "age": 36, "hb": 8.4, "bp": "145/95", "ward": "Ward 01"}
  ]
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoints:**
  - Analytics Dashboard: `/myapp/report/` (`GET`)
  - Export PDF Report: `/myapp/export_report_pdf/` (`GET`)
  - Export Text Report: `/myapp/export_report_text/` (`GET`)
  - 1-Click Demo Data Refresh: `/myapp/seed_demo_data/` (`GET`)
- **HTTP Method:** `GET`
- **Request Details:** Query parameters for filtering `?applied=1&panchayath=all&report_type=all&date_range=all` (supports filtering by specific Ward or All Wards, and filtering by Report Type: `all`, `charts`, `wards`, `vax`, `kits`, `highrisk`).
- **On-Demand Generation:** The dashboard loads initially in an awaiting-filter state without showing report cards/charts. Metrics and reports are rendered only after the user applies filters (`applied=1`).
- **Response Details:**
  - `/myapp/report/`: Returns rendered HTML report page with Chart.js canvas payloads when filtered, or interactive prompt state when not yet filtered.
  - `/myapp/export_report_pdf/`: Streams binary PDF document (`application/pdf`) with `Content-Disposition: attachment; filename="MaatriCare_Report.pdf"`.
- **When API is Called:** On page load or when clicking export/demo buttons.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def admin_report(request):
    analytics = get_report_analytics_data(request)
    return render(request, 'admin/report.html', {
        'analytics': analytics,
        'kpis': analytics['summary_kpis'],
        'high_risk': analytics['high_risk_watchlist'],
        'charts_json': analytics['charts_json'],
        'panchayaths': analytics['panchayath_stats']
    })

def export_report_pdf(request):
    analytics = get_report_analytics_data(request)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    # Builds ReportLab Story with TableStyle, Paragraphs, Charts
    doc.build(story)
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def admin_report()`, `def export_report_pdf()`, `def export_report_text()`, `def seed_demo_data_view()`
- **Step-by-Step Processing:**
  1. `get_report_analytics_data()` aggregates data across 7 database models.
  2. Evaluates clinical thresholds for maternal risk and missed child vaccine dates.
  3. Prepares JSON serialization strings for Chart.js graphics.
  4. For PDF export: Constructs ReportLab flowable elements (headers, tables, color-coded risk alerts) and streams compiled PDF binary.
  5. For Demo Seed: Invokes `seed_all_demo_data()` to populate realistic testing records.
- **Database Interaction:** Runs multi-table relational aggregations (`Sum`, `Count`, `filter`, `Q`).

---

## 5. CODE FLOW
1. Admin navigates to `/myapp/report/`.
2. Analytics engine queries all maternal, child, vaccine, and nutrition kit tables.
3. Server calculates percentages, identifies high-risk cases, and prepares chart datasets.
4. Browser renders analytics dashboard with interactive charts and data tables.
5. Admin can click "Download PDF Report" to download a publication-ready PDF summary.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page as the **Executive Health Audit and Report Card of the whole district**. It shows healthcare directors whether pregnant mothers are healthy, if children are receiving their vaccines on time, and if nutrition food supplies are reaching families. If an emergency arises—like a mother having very low blood iron—she is placed on the red High-Risk Watchlist so doctors can take immediate action.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Report Header & Controls** | Displays title, generation timestamp, and PDF/Text export buttons. | Header controls for report filtering and document download. |
| **Executive KPI Grid** | Cards showing summary metrics for mothers, risk cases, and vaccines. | Key performance indicators summarizing program reach. |
| **High-Risk Maternal Watchlist**| Red-flagged table of mothers with severe anemia, hypertension, or high risk. | Highlights urgent maternal cases needing medical intervention. |
| **Panchayath Breakdown** | Table showing performance and coverage metrics by local ward. | Comparative geographic performance across wards. |
| **Interactive Analytics Charts**| Chart.js graphs displaying monthly trends and vaccine coverage. | Visual charts showing maternal and infant health trends. |
| **Demo Data Refresh Button** | 1-Click button calling `seed_demo_data` for demonstration testing. | Populates realistic sample data for demonstrations. |