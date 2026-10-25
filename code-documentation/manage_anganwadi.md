# Page Documentation: Manage Anganwadi Teachers (`manage_anganwadi.md`)

## 1. PAGE OVERVIEW
The **Manage Anganwadi Teachers Page** is the administrative directory for all community Anganwadi Child Care Center teachers. It displays center locations, assigned wards, contact details, active status, and provides options to register new teachers, update center assignments, or deactivate accounts.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Teachers Table: Profile image (`image`), Name (`Name`), Center Name (`center_name`), Contact Phone (`Phone`), Email (`Email`), Educational Qualification (`Qualification`), Appointment Date (`joining_date`), and Operational Status (`Current_status`).
  - Summary KPI Metrics: Total Centers / Teachers, Active Centers, and Total Nutrition Kits Managed.
- **Data Collected (Search / Filter Params):**
  - `q`: Search keyword across name, center name, qualification, or contact info.
  - `status`: Operational status filter ('all', 'active', 'inactive').
- **Data Format Example (JSON):**
```json
{
  "id": 2,
  "Name": "Radhika Suresh",
  "center_name": "Anganwadi Center 02 - East Sector",
  "Phone": 9447123987,
  "Email": "radhika.ang@gmail.com",
  "Qualification": "Early Childhood Education Diploma",
  "Current_status": "Active"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoints:**
  - Directory View: `/myapp/manage_anganwadi/` (`GET`)
  - Delete Teacher: `/myapp/delete_anganwadi/<int:id>/` (`GET` or `POST`)
- **HTTP Method:** `GET`
- **Request Details:** URL query parameters `?q=<term>&status=<status>`
- **Response Details:** Renders compiled HTML (`admin/manage_anganwadi.html`) with filtered teacher records.
- **When API is Called:** On page load, search form submit, or status dropdown change.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def manage_anganwadi(request):
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', 'all').strip()
    teachers = anganwadi_teacher.objects.all().order_by('-id')
    if status_filter and status_filter.lower() != 'all':
        teachers = teachers.filter(Current_status__iexact=status_filter)
    if search_query:
        teachers = teachers.filter(
            Q(Name__icontains=search_query) |
            Q(center_name__icontains=search_query) |
            Q(Phone__icontains=search_query)
        )
    return render(request, 'admin/manage_anganwadi.html', context)
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def manage_anganwadi(request)`, `def delete_anganwadi(request, id)`
- **Step-by-Step Processing:**
  1. Reads search and filter queries from `request.GET`.
  2. Queries `myapp_anganwadi_teacher` table using case-insensitive `icontains` filters.
  3. Computes summary metrics for total centers and active personnel.
  4. Returns rendered HTML template with teachers queryset.
- **Database Interaction:** Executes SQL query on `myapp_anganwadi_teacher`.

---

## 5. CODE FLOW
1. Admin selects "Manage Anganwadi" from admin navigation.
2. HTTP GET request dispatched to `/myapp/manage_anganwadi/`.
3. Backend fetches teacher records and active centers from MySQL.
4. Template loops over teachers list and renders information cards and table rows.
5. Admin can search by center name or click "Edit" / "Delete".

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
This page is the **Official Directory of all Anganwadi Child Care and Nutrition Centers**. It lists every teacher in charge of distributing food packets and measuring child nutrition in the community, showing which center they run, their phone number, and whether their center is open and active.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Directory Title & Action** | Header with page title and button to register new Anganwadi teacher. | Header and primary action button for new teacher creation. |
| **Search & Status Filters** | Search input and dropdown to quickly find centers by name or status. | Real-time filtering controls for teacher records. |
| **Center Statistics Cards** | Counters showing Total Centers, Active Teachers, and Kits Managed. | High-level metrics for Anganwadi operations. |
| **Teachers Table (Live Sync)** | Lists teacher name, photo, age, DOB, center, address, phone, email, qualification, and status. Any updates made by teachers in their profile reflect here immediately. | Core table displaying live synchronized teacher records. |
| **Action Links (Edit & Delete)** | Direct Edit and Delete buttons linked to respective modification routes. | Provides row-level administration controls. |