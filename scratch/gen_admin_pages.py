# -*- coding: utf-8 -*-
import os

OUT_DIR = r"c:\Users\HP\PycharmProjects\maatricaree\code-documentation"

pages = {}

# 5. admin_home.md
pages["admin_home.md"] = """# Page Documentation: Admin Home Dashboard (`admin_home.md`)

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
    analytics = get_report_analytics_data(request)
    kpis = analytics['summary_kpis']
    active_mothers = user_table.objects.all().order_by('-registration_date', '-id')[:8]
    recent_high_risk = analytics['high_risk_watchlist'][:5]
    recent_kits = nutrition_kit.objects.all().select_related('USER', 'TEACHER').order_by('-distribution_date', '-id')[:5]
    context = {
        'analytics': analytics,
        'kpis': kpis,
        'pregnant_count': kpis['total_pregnant'],
        'newborn_count': kpis['total_children'],
        'growth_count': child_growth_record.objects.count(),
        'total_registered': kpis['total_registered'],
        'vax_coverage_pct': kpis['vax_coverage_pct'],
        'high_risk_count': kpis['high_risk_count'],
        'active_mothers': active_mothers,
        'recent_high_risk': recent_high_risk,
        'recent_kits': recent_kits,
        'charts_json': analytics['charts_json'],
    }
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
"""

# 6. manage_asha.md
pages["manage_asha.md"] = """# Page Documentation: Manage ASHA Workers (`manage_asha.md`)

## 1. PAGE OVERVIEW
The **Manage ASHA Workers Page** serves as the administrative personnel registry for Accredited Social Health Activists (ASHA workers). It enables administrators to review all registered field workers, filter them by operational status (Active/Inactive), search by name or assigned ward, inspect their beneficiary caseloads, navigate to profile editing, or remove inactive workers.

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
| **Workers Table** | Displays photo, name, contact, assigned ward, status badge, and actions. | Main data table listing all ASHA personnel. |
| **Action Modals / Links** | Edit link leading to edit form and delete button with confirmation prompt. | Provides controls to modify or remove worker accounts. |
"""

# 7. add_asha.md
pages["add_asha.md"] = """# Page Documentation: Add ASHA Worker (`add_asha.md`)

## 1. PAGE OVERVIEW
The **Add ASHA Worker Page** provides an administrative registration form to onboard new ASHA community health workers. It captures personal information, nursing qualifications, contact numbers, profile photo, assigned Grama Panchayat ward, and sets up secure system login credentials.

---

## 2. DATA USED IN THIS PAGE
- **Data Collected (Form Submission):**
  - Personal & Contact: `full_name`, `age`, `dob`, `qualification`, `email`, `phone`, `address`, `joining_date`.
  - Administrative: `area_assigned` (Ward 01 to Ward 05), `image` (Profile photo file).
  - Login Credentials: `username`, `password`, `confirm_password`.
- **Data Displayed:**
  - Ward dropdown options and real-time input validation feedback.
- **Data Format Example (Form POST):**
```json
{
  "full_name": "Sunitha Kumari",
  "age": 32,
  "dob": "1994-08-10",
  "qualification": "B.Sc Nursing",
  "email": "sunitha.asha@gmail.com",
  "phone": 9846011223,
  "area_assigned": "Ward 03 - West Gram",
  "joining_date": "2026-03-01",
  "username": "sunitha_ward03",
  "password": "Password@123"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/add_asha/`
- **HTTP Method:** `GET` (render blank form), `POST` (process creation)
- **Request Details:** `multipart/form-data` containing text parameters and image binary.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/manage_asha/` with green success notification.
  - Validation Error: HTTP 200 Re-renders form with error alerts and preserved inputs.
- **When API is Called:** When administrator clicks the "Register ASHA Worker" button.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def add_asha(request):
    if request.method == "POST":
        # Validates username uniqueness, phone regex, email format, password match
        user = User.objects.create_user(username=username, password=password, email=email)
        asha_group, _ = Group.objects.get_or_create(name='ashaworker')
        user.groups.add(asha_group)
        
        fs = FileSystemStorage()
        img_filename = fs.save(img_file.name, img_file)
        
        asha_worker.objects.create(
            LOGIN=user,
            Full_name=full_name,
            Age=age,
            dob=dob,
            Qualification=qualification,
            Email=email,
            Address=address,
            image=img_filename,
            Area_assigned=area_assigned,
            Phone=phone,
            Joining_date=joining_date,
            Current_status='Active'
        )
        messages.success(request, f"ASHA Worker '{full_name}' registered successfully!")
        return redirect('/myapp/manage_asha/')
    return render(request, 'admin/add_asha.html')
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def add_asha(request)`
- **Step-by-Step Processing:**
  1. Validates all required fields and checks regex for phone (10 digits starting 6-9) and email.
  2. Ensures username does not already exist in `auth_user`.
  3. Creates `User` account, encrypts password, and attaches to `ashaworker` permission group.
  4. Saves uploaded profile photo to `media/` folder using `FileSystemStorage`.
  5. Inserts new record into `myapp_asha_worker` table linking `LOGIN=user`.
  6. Redirects administrator to `manage_asha` with confirmation message.
- **Database Interaction:** Executes SQL `INSERT INTO auth_user` and `INSERT INTO myapp_asha_worker`.

---

## 5. CODE FLOW
1. Admin navigates to `/myapp/add_asha/`.
2. Form renders with personal, contact, and ward assignment sections.
3. Admin completes form and uploads worker photo.
4. Admin submits form via POST.
5. Server validates data, saves photo file, and writes user and worker records to database.
6. Admin is redirected to ASHA Directory with a success alert banner.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
This page is like **an employment and onboarding desk for a new village health nurse**. When the health department hires an ASHA worker, the admin enters her name, qualifications, phone number, and assigns her a specific neighborhood (Ward). The system also creates an official username and password so she can log in from her own smartphone or tablet.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Form Header & Back Link** | Displays page title, instructions, and link back to worker directory. | Header providing context and return navigation. |
| **Login Credentials Card** | Input fields for system username, password, and confirmation. | Establishes account credentials for the worker. |
| **Personal Demographics Card** | Inputs for full name, age, date of birth, and qualifications. | Collects identity and educational background. |
| **Contact & Ward Allocation** | Inputs for phone number, email, address, and assigned ward dropdown. | Links worker to contact details and specific ward. |
| **Photo Upload & Joining Date** | File input for profile picture and date picker for start of service. | Captures official photo and date of appointment. |
| **Submission Actions** | Submit button and cancel button triggering form reset. | Dispatches data payload to backend endpoint. |
"""

# 8. edit_asha.md
pages["edit_asha.md"] = """# Page Documentation: Edit ASHA Worker (`edit_asha.md`)

## 1. PAGE OVERVIEW
The **Edit ASHA Worker Page** allows administrators to update existing ASHA health worker profiles. It supports updating phone numbers, email addresses, educational qualifications, operational status (Active/Inactive), profile photographs, and reassigning workers to different Panchayat wards.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed (Prefilled Form):**
  - Current values from `myapp_asha_worker`: `Full_name`, `Age`, `dob`, `Qualification`, `Email`, `Phone`, `Address`, `Area_assigned`, `Current_status`, and current profile image preview.
- **Data Collected (Form POST):**
  - Updated contact details, status selection ('Active' / 'Inactive'), new assigned ward, and optional replacement profile photo.
- **Data Format Example (Form POST Body):**
```json
{
  "full_name": "Kavitha Menon",
  "phone": 9876543210,
  "area_assigned": "Ward 02 - East Sector",
  "current_status": "Active",
  "qualification": "GNM Nursing / Certified Midwife"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/edit_asha/<int:id>/`
- **HTTP Method:** `GET` (fetch and display current worker data), `POST` (save updates)
- **Request Details:** URL parameter `<int:id>` identifies the target worker.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/manage_asha/` with updated confirmation.
  - Validation Failure: Re-renders form displaying field validation errors.
- **When API is Called:** When administrator clicks "Edit" button in ASHA directory and submits changes.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def edit_asha(request, id):
    asha = get_object_or_404(asha_worker, id=id)
    if request.method == "POST":
        # Extracts updated phone, email, qualification, area, status
        asha.Full_name = request.POST.get('full_name')
        asha.Phone = request.POST.get('phone')
        asha.Area_assigned = request.POST.get('area_assigned')
        asha.Current_status = request.POST.get('current_status')
        if 'image' in request.FILES:
            asha.image = FileSystemStorage().save(request.FILES['image'].name, request.FILES['image'])
        asha.save()
        messages.success(request, f"ASHA Worker '{asha.Full_name}' profile updated successfully!")
        return redirect('/myapp/manage_asha/')
    return render(request, 'admin/edit_asha.html', {'asha': asha})
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def edit_asha(request, id)`
- **Step-by-Step Processing:**
  1. Retrieves target `asha_worker` instance using `id` or returns 404.
  2. On GET: Passes existing model record to template to prefill all form fields.
  3. On POST: Validates updated fields (phone length, email regex).
  4. If a new photo file is provided, stores it in `media/` and updates image path.
  5. Updates linked `auth_user` email if changed.
  6. Commits updates to database using `asha.save()`.
- **Database Interaction:** `UPDATE myapp_asha_worker SET ... WHERE id = ...`.

---

## 5. CODE FLOW
1. Admin clicks "Edit" icon next to a worker row on `/myapp/manage_asha/`.
2. Browser issues GET request to `/myapp/edit_asha/<id>/`.
3. Backend fetches worker details from MySQL and renders pre-filled form.
4. Admin modifies details (e.g. changes ward or updates phone number) and clicks "Save Changes".
5. Backend updates database and redirects to the ASHA directory.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **updating an employee's personnel file**. If an ASHA worker gets transferred to a neighboring village ward, gets a new mobile phone number, or takes medical leave, the administrator uses this page to modify her file so the system always has her most up-to-date details.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Profile Summary Banner** | Displays worker's photo thumbnail, name, ID, and current status badge. | Quick visual identity check of worker being edited. |
| **Personal Information Fields** | Pre-populated inputs for Full Name, Age, and Date of Birth. | Allows editing personal demographic details. |
| **Contact & Address Block** | Inputs for Phone Number, Email, and Postal Address. | Modifies contact and physical location records. |
| **Ward Assignment & Status** | Dropdowns to reallocate ward area and toggle Active/Inactive state. | Adjusts geographic responsibility and operational status. |
| **Photo Replacement Field** | File input allowing upload of a newer profile photograph. | Optional upload to refresh employee photograph. |
| **Save / Cancel Actions** | Submit button executing update transaction and cancel button. | Commits modifications to the database or aborts. |
"""

# 9. manage_anganwadi.md
pages["manage_anganwadi.md"] = """# Page Documentation: Manage Anganwadi Teachers (`manage_anganwadi.md`)

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
| **Teachers Data Table** | Lists center name, teacher name, phone, qualifications, and status. | Core table displaying teacher information and actions. |
| **Management Links** | Edit and delete action buttons linked to respective modification routes. | Provides row-level administration options. |
"""

# 10. add_anganwadi.md
pages["add_anganwadi.md"] = """# Page Documentation: Add Anganwadi Teacher (`add_anganwadi.md`)

## 1. PAGE OVERVIEW
The **Add Anganwadi Teacher Page** allows administrators to register a new Anganwadi teacher and link them to a specific child development center. It collects their personal information, educational qualifications, contact numbers, center name, and automatically creates their system user account.

---

## 2. DATA USED IN THIS PAGE
- **Data Collected (Form Submission):**
  - Personal: `name`, `age`, `dob`, `gender` ('Female', 'Male'), `qualification`, `image`.
  - Center & Contact: `center_name` (e.g., Anganwadi Center 01), `phone`, `email`, `address`, `joining_date`.
  - Credentials: `username`, `password`, `confirm_password`.
- **Data Displayed:**
  - Center selection dropdown and form validation instructions.
- **Data Format Example (Form POST):**
```json
{
  "name": "Lakshmi Narayanan",
  "age": 29,
  "gender": "Female",
  "qualification": "Pre-Primary Teaching Diploma",
  "center_name": "Anganwadi Center 04 - North Colony",
  "phone": 9847556677,
  "email": "lakshmi.ang@gmail.com",
  "username": "lakshmi_ang04",
  "password": "Password@2026"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/add_anganwadi/`
- **HTTP Method:** `GET` (render blank registration form), `POST` (process creation)
- **Request Details:** `multipart/form-data` with form fields and optional profile picture.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/manage_anganwadi/` with success toast alert.
  - Validation Failure: Re-renders form with error alerts.
- **When API is Called:** When admin clicks "Register Anganwadi Teacher".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def add_anganwadi(request):
    if request.method == "POST":
        # Validates fields, checks username uniqueness, phone & email formats
        user = User.objects.create_user(username=username, password=password, email=email)
        ang_group, _ = Group.objects.get_or_create(name='angteacher')
        user.groups.add(ang_group)
        
        anganwadi_teacher.objects.create(
            LOGIN=user,
            Name=name,
            Age=age,
            dob=dob,
            Gender=gender,
            Phone=phone,
            Email=email,
            Address=address,
            image=img_filename,
            Qualification=qualification,
            center_name=center_name,
            joining_date=joining_date,
            Current_status='Active'
        )
        messages.success(request, f"Anganwadi Teacher '{name}' registered successfully!")
        return redirect('/myapp/manage_anganwadi/')
    return render(request, 'admin/add_anganwadi.html')
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def add_anganwadi(request)`
- **Step-by-Step Processing:**
  1. Validates inputs, ensuring phone is 10 digits and username is unique.
  2. Creates new `User` record in `auth_user` and assigns group `angteacher`.
  3. Uploads profile image file to `media/` folder.
  4. Inserts `anganwadi_teacher` record into MySQL linking to created `User`.
  5. Redirects to `/myapp/manage_anganwadi/` with success notification.
- **Database Interaction:** Executes SQL `INSERT` into `auth_user` and `myapp_anganwadi_teacher`.

---

## 5. CODE FLOW
1. Admin opens `/myapp/add_anganwadi/`.
2. Form loads with fields for teacher demographics, center name, and login credentials.
3. Admin inputs teacher details and clicks "Submit".
4. Server validates data and creates user account with `angteacher` role.
5. Server saves Anganwadi teacher profile in database.
6. Browser redirects back to Anganwadi Teacher Directory.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
This page is the **Official Appointment Desk for a new Anganwadi Center Teacher**. When the government assigns a teacher to manage a local village day-care and nutrition center, the admin uses this form to register her name, assign her center, and give her a login account so she can order and distribute baby food packets.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Form Banner** | Displays title and navigation link back to directory. | Top navigation and header. |
| **Login Setup Section** | Username, password, and confirmation inputs for teacher portal access. | Establishes portal login credentials. |
| **Personal Demographics** | Name, age, DOB, gender, and educational qualifications. | Records personal and professional details. |
| **Center Assignment Section**| Center name / ward dropdown, contact phone, email, and address. | Assigns teacher to specific Anganwadi center. |
| **Photo Upload & Dates** | File picker for profile picture and joining date selector. | Attaches profile photo and official start date. |
| **Submit Action Buttons** | Submit registration button and cancel link. | Initiates backend account creation. |
"""

# 11. edit_anganwadi.md
pages["edit_anganwadi.md"] = """# Page Documentation: Edit Anganwadi Teacher (`edit_anganwadi.md`)

## 1. PAGE OVERVIEW
The **Edit Anganwadi Teacher Page** enables administrators to modify existing Anganwadi teacher profiles. It allows updating contact numbers, qualifications, center assignments, operational status (Active/Inactive), and profile photos.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed (Prefilled Form):**
  - Pre-populated fields from `myapp_anganwadi_teacher`: `Name`, `Age`, `dob`, `Gender`, `Phone`, `Email`, `Address`, `Qualification`, `center_name`, `Current_status`, and current photo preview.
- **Data Collected (Form Submission):**
  - Updated contact information, reassigned center name, status dropdown, and optional new profile image.
- **Data Format Example (Form POST):**
```json
{
  "name": "Radhika Suresh",
  "phone": 9447123987,
  "center_name": "Anganwadi Center 02 - East Sector",
  "current_status": "Active",
  "qualification": "Diploma in Nutrition & Early Child Care"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/edit_anganwadi/<int:id>/`
- **HTTP Method:** `GET` (fetch and render existing details), `POST` (save updates)
- **Request Details:** URL integer parameter `<int:id>` identifies the teacher record.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/manage_anganwadi/` with green success notification.
  - Validation Failure: Re-renders form with error alert banner.
- **When API is Called:** When admin clicks "Edit" in the Anganwadi directory and submits modifications.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def edit_anganwadi(request, id):
    teacher = get_object_or_404(anganwadi_teacher, id=id)
    if request.method == "POST":
        teacher.Name = request.POST.get('name')
        teacher.Phone = request.POST.get('phone')
        teacher.center_name = request.POST.get('center_name')
        teacher.Current_status = request.POST.get('current_status')
        if 'image' in request.FILES:
            teacher.image = FileSystemStorage().save(request.FILES['image'].name, request.FILES['image'])
        teacher.save()
        messages.success(request, f"Anganwadi Teacher '{teacher.Name}' updated successfully!")
        return redirect('/myapp/manage_anganwadi/')
    return render(request, 'admin/edit_anganwadi.html', {'teacher': teacher})
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def edit_anganwadi(request, id)`
- **Step-by-Step Processing:**
  1. Finds `anganwadi_teacher` instance by primary key `id`.
  2. Renders prefilled HTML form on GET.
  3. Validates submitted form fields on POST.
  4. Saves replacement image file if uploaded.
  5. Commits changes to MySQL database via `teacher.save()`.
  6. Redirects administrator to `/myapp/manage_anganwadi/`.
- **Database Interaction:** Executes SQL `UPDATE myapp_anganwadi_teacher SET ... WHERE id = ...`.

---

## 5. CODE FLOW
1. Admin clicks "Edit" button next to a teacher in the directory.
2. Server loads existing record and displays prefilled edit form.
3. Admin edits center name or phone number and clicks "Save Changes".
4. Server validates modifications and updates database record.
5. Browser redirects back to Anganwadi directory with success message.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
This page is like **updating the center assignment or contact details of an Anganwadi teacher**. If a teacher transfers to another village center or changes her phone number, the administrator opens this page to make sure her contact info and center name stay accurate.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Profile Card Header** | Displays current teacher name, thumbnail photo, and center name. | Visual confirmation of teacher account being modified. |
| **Personal Demographics** | Inputs for Name, Age, and Date of Birth. | Updates personal identifying details. |
| **Contact & Center Info** | Inputs for Mobile Phone, Email, Center Name dropdown, and Address. | Updates contact information and center allocation. |
| **Status & Qualifications** | Dropdown for Active/Inactive status and text input for qualifications. | Modifies operational status and qualifications. |
| **Photo Upload Widget** | Allows uploading a new image to replace current profile photo. | Updates teacher profile photo. |
| **Form Action Buttons** | "Save Changes" submit button and "Cancel" link. | Submits modifications or cancels operation. |
"""

# 12. add_vaccination.md
pages["add_vaccination.md"] = """# Page Documentation: Add Vaccination to Catalog (`add_vaccination.md`)

## 1. PAGE OVERVIEW
The **Add Vaccination Page** is the administrative master catalog manager for childhood immunizations. It allows healthcare administrators to configure standardized vaccines according to national immunization guidelines (such as BCG, OPV, Pentavalent, Rotavirus, Measles-Rubella), set target age milestones in months (from birth to 5 years), and define mandatory clinical descriptions.

---

## 2. DATA USED IN THIS PAGE
- **Data Collected (Form Submission):**
  - `vaccine_code`: Short standardized medical code (e.g., "BCG", "OPV-0", "ROTA-1", "MR-1").
  - `vaccine_name`: Official vaccine name (e.g., "Bacillus Calmette–Guérin", "Oral Polio Vaccine").
  - `vaccine_type`: Category ('Mandatory', 'Recommended', 'Optional').
  - `target_month`: Target child age in months (0 = At Birth, 1.5, 2.5, 3.5, 9, 16-24, 60).
  - `description`: Clinical indications, diseases prevented, and dosage instructions.
- **Data Displayed:**
  - Catalog list of existing master vaccines already configured in the system.
- **Data Format Example (JSON):**
```json
{
  "vaccine_code": "PENTA-1",
  "vaccine_name": "Pentavalent Vaccine Dose 1",
  "vaccine_type": "Mandatory",
  "target_month": 2,
  "description": "Protects against Diphtheria, Pertussis, Tetanus, Hepatitis B, and Hib."
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/add_vaccination/`
- **HTTP Method:** `GET` (view catalog & form), `POST` (add new vaccine)
- **Request Details:** Form-encoded POST body containing vaccine catalog parameters.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/add_vaccination/` with success toast.
  - Failure: Re-renders form with error notice.
- **When API is Called:** When administrator clicks "Add to Master Catalog".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def add_vaccination(request):
    master_vaccines = vaccination.objects.filter(CHILD__isnull=True).order_by('target_month')
    if request.method == "POST":
        vaccine_code = request.POST.get("vaccine_code", "").strip()
        vaccine_name = request.POST.get("vaccine_name", "").strip()
        vaccine_type = request.POST.get("vaccine_type", "Mandatory").strip()
        target_month = int(request.POST.get("target_month", 0))
        description = request.POST.get("description", "").strip()
        
        vaccination.objects.create(
            CHILD=None,  # Master catalog template definition
            vaccine_code=vaccine_code,
            vaccine_name=vaccine_name,
            vaccine_type=vaccine_type,
            target_month=target_month,
            description=description,
            status='Master Template'
        )
        messages.success(request, f"Vaccine '{vaccine_name}' added to Master Schedule!")
        return redirect('/myapp/add_vaccination/')
    return render(request, 'admin/add_vaccination.html', {'master_vaccines': master_vaccines})
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def add_vaccination(request)`
- **Step-by-Step Processing:**
  1. Retrieves all master vaccine templates where `CHILD__isnull=True`.
  2. Validates incoming form fields (non-empty name, non-negative target month).
  3. Creates `vaccination` record with `CHILD=None`, which serves as a master template for child scheduling.
  4. Redirects back to page with success alert.
- **Database Interaction:** `INSERT INTO myapp_vaccination (CHILD_id, vaccine_code, vaccine_name, target_month, ...)` values `(NULL, ...)`.

---

## 5. CODE FLOW
1. Admin navigates to `/myapp/add_vaccination/`.
2. Page displays the vaccine creation form alongside a table of existing master vaccines.
3. Admin fills in vaccine code, name, target month, and description.
4. Admin submits form.
5. Server writes vaccine template into MySQL.
6. Page refreshes and displays the newly added vaccine in the master schedule table.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
This page is like **setting up the official Childhood Vaccination Calendar for the whole hospital**. It tells the system: "At birth, every baby must get BCG. At 6 weeks, every baby must get Pentavalent." Once the admin defines these standard rules here, health workers can schedule these vaccines for individual newborn babies.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Catalog Form Header** | Displays page title and explanation of immunization master schedule. | Header explaining master vaccine setup. |
| **Vaccine Code & Name Fields**| Inputs for medical code (e.g. BCG) and complete vaccine dose name. | Captures standardized medical names. |
| **Target Month & Type** | Input for target milestone in months and type dropdown (Mandatory/Optional). | Sets child age milestone and category. |
| **Clinical Description** | Textarea for indications, diseases prevented, and storage instructions. | Stores clinical background and guidelines. |
| **Master Vaccines Table** | Displays list of all configured master vaccines sorted by target month. | Shows current official immunization catalog. |
"""

# 13. schedule_vaccination.md
pages["schedule_vaccination.md"] = """# Page Documentation: Schedule Child Vaccination (`schedule_vaccination.md`)

## 1. PAGE OVERVIEW
The **Schedule Child Vaccination Page** provides an administrative interface to schedule immunization camps and individual vaccination sessions for registered infants. It links a specific child to a vaccine from the master catalog, assigns a scheduled date, start and end time windows, and automatically issues an alert notification to the mother.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Children Selection List: Child name, mother name, date of birth, age in months.
  - Master Vaccines Catalog: Available vaccines with target milestone months.
  - Active Schedules Table: Recently scheduled upcoming vaccination sessions.
- **Data Collected (Form Submission):**
  - `child_id`: ID of the target registered child.
  - `vaccine_name` / `vaccine_id`: Selected vaccine from catalog.
  - `schedule_date`: Date of the immunization camp session.
  - `time_from`, `time_to`: Session operational hours (e.g. 09:30 AM - 01:00 PM).
- **Data Format Example (Form POST):**
```json
{
  "child_id": 12,
  "vaccine_name": "Pentavalent Dose 1",
  "schedule_date": "2026-04-10",
  "time_from": "09:30",
  "time_to": "12:30"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/schedule_vaccination/`
- **HTTP Method:** `GET` (render schedule interface), `POST` (create schedule)
- **Request Details:** Form-encoded POST body containing child, vaccine, and time slot.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/schedule_vaccination/` with success message.
  - Validation Failure: Re-renders form with alert warning.
- **When API is Called:** When admin clicks "Confirm Vaccination Schedule".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def schedule_vaccination(request):
    if request.method == "POST":
        child_obj = get_object_or_404(child, id=request.POST.get('child_id'))
        vax_record = vaccination.objects.create(
            CHILD=child_obj,
            vaccine_name=request.POST.get('vaccine_name'),
            vaccine_type=request.POST.get('vaccine_type', 'Mandatory'),
            target_month=request.POST.get('target_month', 0),
            vaccination_date=request.POST.get('schedule_date'),
            status='Scheduled'
        )
        schedule = vaccine_schedule.objects.create(
            VACCINATION=vax_record,
            schedule_date=request.POST.get('schedule_date'),
            time_from=request.POST.get('time_from'),
            time_to=request.POST.get('time_to')
        )
        # Dispatch notification to mother
        notification.objects.create(
            USER=child_obj.USER,
            message=f"Vaccination scheduled for child '{child_obj.child_name}': {vax_record.vaccine_name} on {schedule.schedule_date}.",
            notification_date=date.today()
        )
        messages.success(request, f"Vaccination scheduled for '{child_obj.child_name}' successfully!")
        return redirect('/myapp/schedule_vaccination/')
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def schedule_vaccination(request)`
- **Step-by-Step Processing:**
  1. Queries all registered children (`myapp_child`) and master vaccines (`myapp_vaccination`).
  2. On POST, retrieves target `child` instance.
  3. Creates new `vaccination` record linked to `CHILD` with status `'Scheduled'`.
  4. Inserts `vaccine_schedule` record with specific date and time slot.
  5. Inserts automated alert into `myapp_notification` linked to child's mother (`USER`).
  6. Redirects back to page with success alert.
- **Database Interaction:** Executes SQL `INSERT` into `myapp_vaccination`, `myapp_vaccine_schedule`, and `myapp_notification`.

---

## 5. CODE FLOW
1. Admin opens `/myapp/schedule_vaccination/`.
2. Form populates registered children and master vaccine catalog dropdowns.
3. Admin selects baby, chooses required vaccine dose, and picks date/time slot.
4. Admin clicks "Schedule Vaccination".
5. Server writes vaccination appointment and dispatches alert to mother's account.
6. Page reloads showing the new schedule in the upcoming sessions table.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **booking a vaccine appointment at the village clinic for a baby**. The admin picks the baby's name from the list, selects which injection is due (like Polio drops or Hepatitis B), and chooses the date and time. When the appointment is saved, the system automatically sends a reminder message to the mother's phone and portal.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Session Scheduler Form** | Dropdowns for selecting child, vaccine catalog, date picker, and time slots. | Primary form to schedule an immunization appointment. |
| **Child Demographics Preview**| JavaScript dynamic widget showing child DOB and age when selected. | Displays child age and mother info upon selection. |
| **Notification Dispatch Logic**| Backend trigger creating a notification record for the mother. | Sends instant in-app appointment alert to mother. |
| **Upcoming Sessions Table** | Displays scheduled vaccine sessions with child name, vaccine, date, and status. | Lists upcoming immunization appointments across centers. |
"""

# 14. vaccination_records.md
pages["vaccination_records.md"] = """# Page Documentation: Vaccination Records & Status Tracking (`vaccination_records.md`)

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
"""

# 15. admin_report.md
pages["admin_report.md"] = """# Page Documentation: Healthcare Analytics & Reports (`admin_report.md`)

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
- **Request Details:** Query parameters for date filtering `?date_range=month&panchayath=all`
- **Response Details:**
  - `/myapp/report/`: Returns rendered HTML report page with Chart.js canvas payloads.
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
"""

for fname, text in pages.items():
    with open(os.path.join(OUT_DIR, fname), "w", encoding="utf-8") as f:
        f.write(text.strip())
    print(f"Generated {fname}")

print("Admin pages generated successfully.")
