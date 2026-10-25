# Page Documentation: ASHA Worker Home Dashboard (`asha_home.md`)

## 1. PAGE OVERVIEW
The **ASHA Worker Home Dashboard** is the primary mobile and desktop workspace for Accredited Social Health Activists (field health workers). It provides field workers with immediate situational awareness of their assigned village ward: pending mother verifications requiring home visits, active pregnant mothers under care, high-risk cases (low hemoglobin, gestational hypertension), upcoming antenatal checkup dates, and newborn babies registered.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - ASHA Profile Banner: Worker name (`worker.Full_name`), Assigned Ward (`worker.Area_assigned`), Phone, and Status badge.
  - Quick Counters: Pending Mother Verifications (`pending_verification_count`), Total Verified Mothers in Ward (`verified_count`), Active Pregnancies (`pregnant_mothers_count`), High-Risk Pregnancies (`high_risk_count`), Total Newborns (`children_count`).
  - Upcoming Checkups List: Mothers with checkups scheduled in the next 7 days.
  - Ward Beneficiaries Roster: List of mothers under this worker's direct clinical care.
- **Data Source:** Relational queries isolated strictly to worker's assigned ward: `myapp_user_table`, `myapp_pregnancy_record`, `myapp_child`, `myapp_asha_worker`.
- **Data Format Example (Context JSON):**
```json
{
  "worker_name": "Kavitha Menon",
  "area_assigned": "Ward 01 - Main Community Center",
  "pending_verifications": 4,
  "active_pregnancies": 22,
  "high_risk_count": 3,
  "newborns_count": 15
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/ashaworker_home/`
- **HTTP Method:** `GET` (render dashboard), `POST` (quick add mother modal)
- **Request Details:** Authenticated GET request with active worker session.
- **Response Details:** Returns compiled HTML (`ashawoker/asha_home.html`) with ward clinical context.
- **When API is Called:** On login or navigation to ASHA portal home.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def ashaworker_home(request):
    worker = get_current_asha_worker(request)
    area_q = get_area_filter_q(worker.Area_assigned) if worker else Q()
    area_mothers = user_table.objects.filter(area_q) if worker else user_table.objects.all()
    pending_verifications = area_mothers.filter(ASHA__isnull=True).count()
    verified_mothers = area_mothers.filter(ASHA__isnull=False)
    pregnant_count = sum(1 for m in verified_mothers if m.expected_delivery_date and m.expected_delivery_date >= date.today())
    return render(request, 'ashawoker/asha_home.html', context)
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def ashaworker_home(request)`, `def get_current_asha_worker(request)`
- **Step-by-Step Processing:**
  1. Retrieves active ASHA worker profile from session or `auth_user`.
  2. Runs `get_area_filter_q(worker.Area_assigned)` to enforce data boundaries.
  3. Queries mothers with `ASHA__isnull=True` in this ward to compute pending verification count.
  4. Queries clinical checkup records to isolate mothers with hemoglobin < 10 g/dL or high BP.
  5. Assembles context and renders `ashawoker/asha_home.html`.
- **Database Interaction:** Executes SQL `SELECT` queries on `myapp_user_table`, `myapp_pregnancy_record`, and `myapp_child`.

---

## 5. CODE FLOW
1. ASHA worker logs in and lands on `/myapp/ashaworker_home/`.
2. Backend filters all records to match worker's assigned ward.
3. Dashboard renders urgent notification badges (e.g. "4 New Mothers Pending Verification").
4. High-risk mothers are highlighted in an alert section for priority home visits.
5. Worker can click "Verify Mothers", "Record Checkup", or "Register Baby" to navigate.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like the **Daily Clipboard and Duty Notebook of a Village Health Nurse**. When she starts her work, the screen tells her: "You have 4 new pregnant mothers who just signed up in your village and need a home visit, 2 mothers have low blood iron and need urgent medicines, and baby Rahul is due for a checkup tomorrow."

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Worker Identity Banner** | Shows worker's photo, name, assigned ward, and quick action buttons. | Visual header identifying worker and ward area. |
| **Ward Health Metric Cards** | 4 cards showing Pending Verifications, Active Mothers, High-Risk, and Babies. | Immediate statistical summary of ward caseload. |
| **High-Risk Maternal Alert** | Red alert card listing mothers with dangerous vitals needing urgent visits. | Prioritizes critical maternal health cases. |
| **Upcoming Checkup Schedule** | Table displaying upcoming antenatal checkup dates for mothers in her care. | Calendar of upcoming maternal clinical visits. |
| **Quick Action Modals** | Shortcut modals to quickly register a mother or record vitals. | Enables fast data capture from mobile devices. |