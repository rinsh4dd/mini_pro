# Page Documentation: Admin Home Dashboard (`admin_home.md`)

## 1. PAGE OVERVIEW
The **Admin Home Dashboard** is the command and control interface for supervising health officers and program administrators. It provides a real-time, consolidated overview of maternal and child healthcare telemetry across all Panchayath wards. It visualizes high-level Key Performance Indicators (KPIs), immunization coverage percentages, supplementary nutrition kit supply levels, high-risk pregnancy watchlists, and recent field health activities.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - KPI Counters: Total Registered Mothers (`total_registered`), Active Pregnancies (`pregnant_count`), Newborns Registered (`newborn_count`), Child Growth Checkups (`growth_count`), High-Risk Pregnancies (`high_risk_count`), Vaccination Coverage Rate (`vax_coverage_pct`), Kits Distributed (`kits_supplied`), and Kits in Reserve (`kits_stock_reserve`).
  - Lists: Recent Registered Mothers (last 8), Urgent High-Risk Watchlist (top 5), Recent Kit Allocations (last 5).
  - Geographic Statistics: Ward/Panchayath-level performance breakdown table.
  - Interactive Analytics: Chart.js data objects (`charts_json`).
- **Data Source:** Aggregated directly from database tables: `myapp_user_table`, `myapp_asha_worker`, `myapp_anganwadi_teacher`, `myapp_child`, `myapp_vaccination`, `myapp_nutrition_kit`, `myapp_pregnancy_record`.
- **Data Format Example (Context JSON):**
```json
{
  "total_registered": 142,
  "pregnant_count": 68,
  "newborn_count": 45,
  "vax_coverage_pct": 89.5,
  "high_risk_count": 8,
  "kits_supplied": 320,
  "high_risk_watchlist": [
    {"name": "Meera Das", "panchayath": "Nedumbassery", "reason": "Hemoglobin 8.2 g/dL (Severe Anemia)", "edd": "2026-10-12"}
  ]
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/adminhome/`
- **HTTP Method:** `GET`
- **Request Details:**
  - Headers: Standard HTTP GET headers with session authentication cookie.
  - Parameters: None.
  - Body: None.
- **Response Details:** Returns compiled HTML (`admin/admin_home.html`) populated with comprehensive analytics context dictionary.
- **When API is Called:** On page load when the admin navigates to the dashboard or logs in.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def adminhome(request):
    all_ashas = asha_worker.objects.all().order_by('Full_name')
    all_teachers = anganwadi_teacher.objects.all().order_by('Name')

    total_ashas = all_ashas.count()
    active_ashas = all_ashas.filter(Current_status='Active').count()
    inactive_ashas = total_ashas - active_ashas

    total_teachers = all_teachers.count()
    active_teachers = all_teachers.filter(Current_status='Active').count()
    inactive_teachers = total_teachers - active_teachers

    total_workers = total_ashas + total_teachers
    total_active_workers = active_ashas + active_teachers

    # Group workers by each designated Panchayath Ward
    ward_data = []
    ...
    return render(request, 'admin/admin_home.html', context)
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def adminhome(request)`, `def get_report_analytics_data(request)`
- **Step-by-Step Backend Execution:**
  1. Checks administrator session permissions.
  2. Executes `get_report_analytics_data(request)` which queries all relational tables to calculate aggregate KPIs.
  3. Evaluates high-risk clinical conditions (hemoglobin < 10, systolic BP >= 140, age >= 35).
  4. Formulates serialization dictionary for Chart.js graphics (trimester distribution, monthly registrations, vaccine compliance).
  5. Renders `admin/admin_home.html` passing the assembled context.
- **Database Interaction:** Runs multiple aggregate SQL queries: `COUNT(*)`, `AVG()`, `select_related('USER', 'TEACHER')`.

---

## 5. CODE FLOW
1. Admin logs in or opens `/myapp/adminhome/`.
2. Server validates admin group membership.
3. Backend controller gathers database metrics across mothers, children, vaccines, and nutrition kits.
4. Aggregates are computed into percentage KPIs and risk lists.
5. Django template merges data and renders dashboard cards, tables, and charts.
6. Browser displays real-time health metrics, warning badges, and interactive graphs.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of the Admin Home Dashboard as the **Air Traffic Control Tower of the entire healthcare project**. From one big control screen, the head medical officer can look out and see everything happening in the region: how many women are currently pregnant, how many babies were born this month, what percentage of babies received their vaccines, and if any mother is in danger because of very low iron or high blood pressure.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Top Navigation Bar** | Displays administrative profile, branding, and logout link. | Standard header across admin portal pages. |
| **KPI Metrics Cards** | 8 summary metric cards displaying mothers, children, vaccines, and kits. | Instant statistical snapshot of program performance. |
| **High-Risk Alert Banner** | Visual alert box highlighting vulnerable mothers needing intervention. | Flags emergency antenatal cases for priority care. |
| **Analytics Charts Row** | Chart.js canvas containers plotting monthly registrations & vaccines. | Graphical trend analysis of maternal health metrics. |
| **Recent Activity Tables** | Tabular display of latest registered mothers and kit distributions. | Shows recent database records with direct review links. |
| **Quick Action Shortcuts** | Direct links to add ASHA workers, schedule vaccines, or print reports. | One-click navigation to primary administrative tasks. |