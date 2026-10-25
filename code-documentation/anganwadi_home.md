# Page Documentation: Anganwadi Teacher Home Dashboard (`anganwadi_home.md`)

## 1. PAGE OVERVIEW
The **Anganwadi Teacher Home Dashboard** is the daily operational workspace for community Anganwadi teachers. It displays center-level metrics including total verified beneficiaries in the teacher's ward, available nutrition kit stock, kits distributed today, pending distributions, collection rate percentage, and recent distribution logs.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Teacher Profile Widget: Teacher name (`teacher.Name`), Center name (`teacher.center_name`), Contact info.
  - Operational KPIs: Total Beneficiaries in Ward (`total_beneficiaries`), Kits Stock in Reserve (`stock_available`), Distributed Today (`today_distribution`), Pending Distributions (`pending_distribution`), and Collection Rate % (`collection_rate_pct`).
  - Recent Distribution Table: Recent kit issuances (Mother name, Kit type, Date, Status).
  - Kit Breakdown Chart: Distribution breakdown between Pregnant Care Kits and Lactating Care Kits.
- **Data Source:** Relational data filtered by teacher's center ward: `myapp_anganwadi_teacher`, `myapp_nutrition_kit`, `myapp_user_table`.
- **Data Format Example (Context JSON):**
```json
{
  "center_name": "Anganwadi Center 01 - Main Community Center",
  "total_beneficiaries": 38,
  "stock_available": 145,
  "today_distribution": 6,
  "pending_distribution": 12,
  "collection_rate_pct": 82.5
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/teacher_home/`
- **HTTP Method:** `GET`
- **Request Details:** HTTP GET request with authenticated session cookie.
- **Response Details:** Returns compiled HTML (`anganwadi_teacher/anganwadi_home.html`) with teacher metrics.
- **When API is Called:** On login or navigation to Teacher Dashboard.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def teacher_home(request):
    teacher = get_current_anganwadi_teacher(request)
    area_q = get_area_filter_q(teacher.center_name) if teacher else Q()
    total_beneficiaries = user_table.objects.filter(area_q, ASHA__isnull=False).count()
    distribution_kits = nutrition_kit.objects.filter(USER__ASHA__isnull=False).select_related('USER', 'TEACHER').order_by('-distribution_date', '-id')
    recent_distributions = distribution_kits[:6]
    stock_kits = nutrition_kit.objects.exclude(USER__ASHA__isnull=False)
    stock_available = sum(k.quantity for k in stock_kits) if stock_kits.exists() else 0
    return render(request, 'anganwadi_teacher/anganwadi_home.html', context)
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def teacher_home(request)`, `def get_current_anganwadi_teacher(request)`
- **Step-by-Step Processing:**
  1. Identifies logged-in user and matches against `anganwadi_teacher` table.
  2. Applies `get_area_filter_q(teacher.center_name)` to enforce ward-level data isolation.
  3. Computes beneficiary counts, stock inventory in reserve, and monthly collection percentages.
  4. Prepares Chart.js data arrays for Pregnant vs Lactating care kits.
  5. Renders template `anganwadi_teacher/anganwadi_home.html`.
- **Database Interaction:** Executes SQL queries filtering `myapp_nutrition_kit` and `myapp_user_table`.

---

## 5. CODE FLOW
1. Anganwadi teacher signs in and is redirected to `/myapp/teacher_home/`.
2. Server matches teacher's login to their assigned Anganwadi center.
3. Server calculates current stock and lists upcoming distribution appointments.
4. Dashboard displays KPI metric cards, stock alerts, and distribution activity.
5. Teacher can click "Distribute Kit" or "Manage Stock" for next actions.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
This page is the **front desk and stock control monitor of an Anganwadi Food & Nutrition Center**. When the teacher opens her computer in the morning, she immediately sees how many nutrition boxes are left on her shelves, how many pregnant mothers from her village are coming today to pick up food packets, and how many are still pending.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Welcome Banner** | Displays teacher name, center ward name, and current date. | Welcomes teacher and displays center assignment. |
| **Operational KPI Cards** | 4 cards showing Ward Beneficiaries, Available Stock, Today's Distributions, and Pending. | Core daily distribution statistics. |
| **Stock Health Alert** | Visual badge indicating whether inventory is sufficient or running low. | Warns teacher when stock needs replenishment. |
| **Kit Breakdown Graph** | Chart.js graphic showing distribution balance between pregnant and nursing mothers. | Visual ratio of maternal vs infant kit demand. |
| **Recent Distribution Table**| Lists latest 6 kit handovers with beneficiary name, date, and status. | Quick audit log of recent kit collections. |