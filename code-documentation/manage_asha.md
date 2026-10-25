# Page Documentation: Manage ASHA Workers — ASHA Directory (`manage_asha.md`)

## 1. PAGE OVERVIEW
The **Manage ASHA Workers Page (ASHA Directory)** serves as the administrative personnel directory for Accredited Social Health Activists (ASHA workers). It enables administrators to review all registered field workers, filter them by operational status (Active/Inactive), search by name or assigned ward, inspect their beneficiary caseloads, navigate to profile editing, or remove inactive workers.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Total ASHA count (`total_workers`), Active workers count (`active_workers`), and average households per worker (`avg_households`).
  - Worker Table: Profile photo (`image`), Full name (`Full_name`), Contact (`Phone`, `Email`), Qualification (`Qualification`), Assigned Panchayat Area (`Area_assigned`), Joining Date (`Joining_date`), and Status (`Current_status`).
- **Data Collected (Search & Filter Query Params):**
  - `q`: Search keyword (matches name, email, ward, qualification, or phone).
  - `status`: Filter dropdown value ('all', 'active', 'inactive').
- **Data Format Example (JSON):**
```json
{
  "id": 4,
  "Full_name": "Kavitha Menon",
  "Phone": 9876543210,
  "Email": "kavitha.asha@gmail.com",
  "Area_assigned": "Ward 01 - Main Community Center",
  "Qualification": "GNM Nursing / Higher Secondary",
  "Joining_date": "2023-01-15",
  "Current_status": "Active"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoints:**
  - List & Search: `/myapp/manage_asha/` (`GET`)
  - Delete Worker: `/myapp/delete_asha/<int:id>/` (`GET` or `POST`)
- **HTTP Method:** `GET`
- **Request Details:** URL parameters `?q=<search_text>&status=<filter>`
- **Response Details:** Returns rendered HTML table with matching ASHA worker records.
- **When API is Called:** On initial page load or when typing in search input or changing filter dropdown.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def manage_asha(request):
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', 'all').strip()
    workers = asha_worker.objects.all().order_by('-id')
    if status_filter and status_filter.lower() != 'all':
        workers = workers.filter(Current_status__iexact=status_filter)
    if search_query:
        workers = workers.filter(
            Q(Full_name__icontains=search_query) |
            Q(Email__icontains=search_query) |
            Q(Area_assigned__icontains=search_query) |
            Q(Phone__icontains=search_query)
        )
    return render(request, 'admin/manage_asha.html', context)
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def manage_asha(request)`, `def delete_asha(request, id)`
- **Step-by-Step Processing:**
  1. Reads `q` and `status` from `request.GET`.
  2. Constructs Django ORM `Q()` objects for case-insensitive keyword searching across 6 text fields.
  3. Computes active worker counts and average mother-to-worker caseload ratios.
  4. Renders `admin/manage_asha.html` passing filtered worker querysets.
  5. For deletion (`delete_asha`), fetches `asha_worker` and associated `LOGIN` user, deletes records, and displays confirmation message.
- **Database Interaction:** `SELECT * FROM myapp_asha_worker WHERE ... ORDER BY id DESC`.

---

## 5. CODE FLOW
1. Admin clicks "Manage ASHA Workers" in the navigation menu.
2. Browser issues GET request to `/myapp/manage_asha/`.
3. Server filters database records according to any search/filter query parameters.
4. Django template loops through `{% for w in workers %}` and renders table rows.
5. Admin can click "Edit" to modify details or "Delete" to remove a worker.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
This page is the **Official Staff Roster for Community Health Workers**. It is like a digital telephone directory and duty chart for all ASHA workers in the district. It shows their photo, which village ward they are assigned to, how to call them, and whether they are currently active. If a worker leaves or moves, the admin can update their ward or remove them.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Directory Header & Add Button** | Shows page title, worker count, and button to register new ASHA worker. | Header bar with call to action for adding staff. |
| **Search & Filter Bar** | Search box and status dropdown that trigger instant query filtering. | Allows instant keyword search across all worker fields. |
| **Summary Counter Cards** | 3 mini cards showing Total Workers, Active Workers, and Average Caseload. | Displays workforce capacity metrics. |
| **Workers Table (Live Sync)** | Displays live worker data: photo, name, age, DOB, ward, address, contact, qualifications, status. Changes made by workers in their profile are instantly reflected here. | Main data table showing live synchronized worker records. |
| **Action Links (Edit & Delete)** | Direct Edit button leading to edit form and Delete button with confirmation prompt. | Provides controls to modify or remove worker accounts. |