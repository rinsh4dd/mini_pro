# Page Documentation: Vaccination Records & Status Tracking (`vaccination_records.md`)

## 1. PAGE OVERVIEW
The **Vaccination Records Page** is the master immunization tracking registry across all Panchayaths. It displays comprehensive records of all scheduled, completed, and overdue child vaccinations. Administrators can filter by completion status, search by child or mother name, and update vaccination statuses to "Administered" once immunizations are given.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - KPI Counters: Total Doses Scheduled, Doses Administered, Pending Doses, and Overdue Doses.
  - Records Table: Child name (`CHILD.child_name`), Mother name (`CHILD.USER.name`), Vaccine name (`vaccine_name`), Target Month, Scheduled Date (`vaccination_date`), Administered Date, Time Window, and Status badge ('Scheduled', 'Administered', 'Overdue').
- **Data Collected (Search & Filter Query Params):**
  - `q`: Search keyword (child name, mother name, or vaccine code).
  - `status`: Status filter dropdown ('All', 'Scheduled', 'Administered', 'Overdue').
- **Data Format Example (JSON):**
```json
{
  "id": 18,
  "child_name": "Aarav Nair",
  "mother_name": "Ananya Nair",
  "vaccine_name": "BCG (Bacillus Calmette–Guérin)",
  "target_month": 0,
  "vaccination_date": "2026-03-15",
  "status": "Administered"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/vaccination_records/`
- **HTTP Method:** `GET` (view records), `POST` (update dose status)
- **Request Details:** Form or query parameters `?q=<term>&status=<filter>`
- **Response Details:** Returns compiled HTML table with filtered vaccination logs.
- **When API is Called:** On page load, search form submit, or when clicking "Mark Administered".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def vaccination_records(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', 'all').strip()
    vax_records = vaccination.objects.filter(CHILD__isnull=False).select_related('CHILD', 'CHILD__USER').order_by('-vaccination_date')
    
    if status_filter and status_filter.lower() != 'all':
        vax_records = vax_records.filter(status__iexact=status_filter)
    if query:
        vax_records = vax_records.filter(
            Q(CHILD__child_name__icontains=query) |
            Q(vaccine_name__icontains=query) |
            Q(CHILD__USER__name__icontains=query)
        )
    return render(request, 'admin/vaccination_records.html', context)
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def vaccination_records(request)`
- **Step-by-Step Processing:**
  1. Queries all `myapp_vaccination` records that are linked to actual children (`CHILD__isnull=False`).
  2. Uses `select_related('CHILD', 'CHILD__USER')` to optimize relational lookups.
  3. Evaluates overdue status by comparing `vaccination_date < today` for pending doses.
  4. Computes immunization completion KPIs.
  5. Renders `admin/vaccination_records.html`.
- **Database Interaction:** Performs optimized SQL `JOIN` between `myapp_vaccination`, `myapp_child`, and `myapp_user_table`.

---

## 5. CODE FLOW
1. Admin navigates to `/myapp/vaccination_records/`.
2. Browser sends GET request to server.
3. Server executes SQL query with child and mother relations.
4. Overdue logic evaluates dates and sets status badges.
5. Browser displays records table with search box and action buttons.
6. Admin can mark doses as administered directly from the table.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like the **Master Vaccination Logbook of the entire community**. It lists every injection due for every baby in the area. Health officers can see at a glance: "Which babies got their shots today? Who missed their appointment last week? And who is scheduled for next Monday?"

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Immunization KPIs** | Cards showing Total Doses, Administered, Pending, and Overdue. | High-level summary of vaccination program progress. |
| **Search & Status Filter** | Search bar and status dropdown to filter records. | Multi-parameter filtering for vaccination records. |
| **Vaccination Log Table** | Table listing Child, Mother, Vaccine, Target Month, Date, and Status. | Core data grid tracking every child's vaccine dose. |
| **Status Update Actions** | One-click button to mark a dose as "Administered". | Updates vaccine fulfillment status in database. |
| **Pagination & Print Controls**| Controls to export or print current filtered vaccination list. | Enables hard-copy generation for field camps. |