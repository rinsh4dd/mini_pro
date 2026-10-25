# -*- coding: utf-8 -*-
import os

OUT_DIR = r"c:\Users\HP\PycharmProjects\maatricaree\code-documentation"

pages = {}

# 16. anganwadi_home.md
pages["anganwadi_home.md"] = """# Page Documentation: Anganwadi Teacher Home Dashboard (`anganwadi_home.md`)

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
"""

# 17. manage_kit.md
pages["manage_kit.md"] = """# Page Documentation: Nutrition Kit Inventory Management (`manage_kit.md`)

## 1. PAGE OVERVIEW
The **Nutrition Kit Inventory Management Page** gives Anganwadi teachers complete oversight over food supply inventory. It displays stock levels across standard kit categories (Maternal Nutrition Kits, Lactation Kits, Infant Weaning Kits), indicates safety thresholds, lists item composition details, and provides quick shortcuts to restock supplies.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Inventory Overview: Available stock units, safety buffer alert levels, total distributed packages.
  - Kit Catalog Cards: Kit type (`kit_type`), Product name (`product_name`), Contents and nutrition specs (`product_details`), Current quantity in stock (`quantity`), Batch date (`date`).
- **Data Source:** `myapp_nutrition_kit` where records represent center inventory reserves.
- **Data Format Example (JSON):**
```json
{
  "kit_type": "Maternal Nutrition Support Kit",
  "product_name": "Amrutham Nutri-Mix (Pregnancy)",
  "product_details": "Fortified wheat flour, roasted gram, soya flour, jaggery, iron & folic acid packets.",
  "quantity": 85,
  "status": "In Stock"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/manage_kit/`
- **HTTP Method:** `GET`
- **Request Details:** Authenticated GET request with session credentials.
- **Response Details:** Returns compiled HTML (`anganwadi_teacher/manage_kit.html`) with inventory tables.
- **When API is Called:** When teacher clicks "Manage Kit Inventory" in navigation.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def manage_kit(request):
    teacher = get_current_anganwadi_teacher(request)
    kits = nutrition_kit.objects.filter(TEACHER=teacher).order_by('-date')
    total_stock = sum(k.quantity for k in kits)
    return render(request, 'anganwadi_teacher/manage_kit.html', {
        'kits': kits,
        'teacher': teacher,
        'total_stock': total_stock
    })
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def manage_kit(request)`
- **Step-by-Step Processing:**
  1. Authenticates current teacher.
  2. Queries `myapp_nutrition_kit` records managed by this teacher.
  3. Evaluates stock counts and highlights low-stock items (< 10 units).
  4. Passes inventory list to `anganwadi_teacher/manage_kit.html`.
- **Database Interaction:** `SELECT * FROM myapp_nutrition_kit WHERE TEACHER_id = ...`.

---

## 5. CODE FLOW
1. Teacher clicks "Manage Stock" on teacher portal.
2. Server loads all inventory batches linked to teacher's center.
3. Page displays cards for each nutrition kit product with current stock count.
4. If stock is low, a red warning badge indicates restocking is needed.
5. Teacher can click "Add / Restock Kit" to add more units.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **checking the pantry and inventory shelves of the Anganwadi store**. It lists all the different food boxes in stock—like nutritious cereal mix, iron capsules, and baby food—and counts how many packets are left. If any box is nearly empty, the screen displays a warning to order more supplies.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Inventory Header & Restock**| Displays title and button to add/restock new nutrition kits. | Header with action to add new inventory. |
| **Stock Summary Metric Cards** | Cards displaying Total Inventory Units, Active Kit Types, and Low Stock Alerts. | High-level inventory capacity counters. |
| **Kit Catalog Cards / Table** | Detailed listing showing product name, nutrition ingredients, and available count. | Product breakdown with ingredients and quantities. |
| **Stock Level Indicator** | Color-coded badges: Green for healthy stock, Red for low stock warning. | Visual threshold indicator for supplies. |
"""

# 18. add_nutrition_kit.md
pages["add_nutrition_kit.md"] = """# Page Documentation: Add / Restock Nutrition Kit (`add_nutrition_kit.md`)

## 1. PAGE OVERVIEW
The **Add Nutrition Kit Page** is the supply replenishment form used by Anganwadi teachers. It allows teachers to log incoming shipments of supplementary nutrition food supplies, select standardized kit categories, enter product ingredients, and update stock counts for their center.

---

## 2. DATA USED IN THIS PAGE
- **Data Collected (Form Submission):**
  - `kit_type`: Category ('Maternal Nutrition Kit', 'Lactating Mother Kit', 'Infant Weaning Food').
  - `product_name`: Name of supplementary product (e.g., 'Amrutham Nutri-Mix Phase 1').
  - `product_details`: Nutritional breakdown (iron, folic acid, calcium, proteins, calories).
  - `quantity`: Number of units received in shipment.
  - `date`: Date of stock arrival.
- **Data Displayed:**
  - Standard kit type presets and stock input guidelines.
- **Data Format Example (Form POST):**
```json
{
  "kit_type": "Maternal Nutrition Kit",
  "product_name": "Nutri-Care Pregnancy Pack",
  "product_details": "500g Roasted cereal mix, Iron tablets, Folic acid, Calcium supplements, Iodine salt",
  "quantity": 50,
  "date": "2026-03-10"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/add_nutrition_kit/`
- **HTTP Method:** `GET` (display form), `POST` (save stock entry)
- **Request Details:** Form-encoded POST body with kit details and quantity.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/manage_kit/` with success toast.
  - Validation Failure: Re-renders form with field error alert.
- **When API is Called:** When teacher clicks "Add to Center Stock".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def add_nutrition_kit(request):
    teacher = get_current_anganwadi_teacher(request)
    if request.method == "POST":
        kit_type = request.POST.get('kit_type')
        product_name = request.POST.get('product_name')
        product_details = request.POST.get('product_details')
        quantity = int(request.POST.get('quantity', 0))
        arrival_date = request.POST.get('date') or date.today()
        
        # Save inventory record
        nutrition_kit.objects.create(
            TEACHER=teacher,
            USER=None,  # Center inventory reserve
            kit_type=kit_type,
            product_name=product_name,
            product_details=product_details,
            date=arrival_date,
            distribution_date=arrival_date,
            quantity=quantity,
            status='In Stock'
        )
        messages.success(request, f"Successfully stocked {quantity} units of '{product_name}'!")
        return redirect('/myapp/manage_kit/')
    return render(request, 'anganwadi_teacher/add_nutrition_kit.html', {'teacher': teacher})
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def add_nutrition_kit(request)`
- **Step-by-Step Processing:**
  1. Identifies logged-in Anganwadi teacher.
  2. Parses and validates input fields on POST.
  3. Inserts a new `myapp_nutrition_kit` record linked to `TEACHER=teacher` with `USER=None` (representing central center stock).
  4. Dispatches confirmation message and redirects to inventory manager.
- **Database Interaction:** Executes SQL `INSERT INTO myapp_nutrition_kit`.

---

## 5. CODE FLOW
1. Teacher clicks "Add New Kit" on the inventory page.
2. Form loads with category selectors, product name inputs, and quantity field.
3. Teacher enters arrival shipment details and submits form.
4. Server validates data and creates new inventory batch record in MySQL.
5. Teacher is redirected to stock manager showing updated totals.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **logging a new shipment of food boxes received at the Anganwadi center**. When the delivery van arrives with 50 packets of nutrition flour and vitamins, the teacher opens this form, types in "50 packets arrived today," and clicks save so the system knows the pantry is restocked.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Form Header** | Shows page title and breadcrumb link to inventory. | Navigation header and form introduction. |
| **Category & Product Name** | Dropdown for kit category and text input for brand/product name. | Classifies product type and records official title. |
| **Nutritional Contents Field** | Textarea describing ingredients, vitamins, and minerals. | Logs dietary details and ingredients. |
| **Quantity & Date Inputs** | Numeric input for packet count and date picker for arrival date. | Captures batch volume and arrival timestamp. |
| **Submit Action Buttons** | Submit button to commit stock and cancel link. | Dispatches data to backend database. |
"""

# 19. kit_distribution.md
pages["kit_distribution.md"] = """# Page Documentation: Nutrition Kit Distribution (`kit_distribution.md`)

## 1. PAGE OVERVIEW
The **Nutrition Kit Distribution Page** is the fulfillment interface where Anganwadi teachers allocate supplementary nutrition kits to verified mothers in their ward. It displays eligible beneficiaries, allows selecting available kits from inventory, automatically deducts stock upon issuance, and dispatches collection notification reminders to the recipient mother.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Eligible Beneficiaries List: Verified mothers residing in the teacher's ward (`user_table` filtered by `area_q`).
  - Available Stock Kits: Current inventory units available for distribution.
  - Active Allocations Table: List of distributions scheduled or completed this month.
- **Data Collected (Form Submission):**
  - `user_id`: ID of the recipient beneficiary mother.
  - `kit_name` / `kit_type`: Selected nutrition kit product.
  - `distribution_date`: Scheduled pickup/distribution date.
  - `quantity`: Number of units allocated (usually 1 or 2).
- **Data Format Example (Form POST):**
```json
{
  "user_id": 15,
  "product_name": "Maternal Nutrition Kit",
  "distribution_date": "2026-03-18",
  "quantity": 1
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/kit_distribution/`
- **HTTP Method:** `GET` (render distribution dashboard), `POST` (execute kit allocation)
- **Request Details:** Form-encoded POST body containing mother ID, kit choice, and date.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/kit_distribution/` with confirmation notice.
  - Validation Failure: Re-renders form with error alert (e.g. "Insufficient Stock").
- **When API is Called:** When teacher clicks "Allocate & Distribute Kit".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def kit_distribution(request):
    teacher = get_current_anganwadi_teacher(request)
    if request.method == "POST":
        mother = get_object_or_404(user_table, id=request.POST.get('user_id'))
        qty = int(request.POST.get('quantity', 1))
        # Deducts center inventory stock
        decrease_stock(request.POST.get('product_name'), qty)
        
        kit = nutrition_kit.objects.create(
            TEACHER=teacher,
            USER=mother,
            kit_type=request.POST.get('kit_type'),
            product_name=request.POST.get('product_name'),
            product_details=request.POST.get('product_details'),
            date=date.today(),
            distribution_date=request.POST.get('distribution_date'),
            quantity=qty,
            status='Pending'
        )
        # Dispatches notification to mother
        kit_notification.objects.create(
            NUTRITION=kit,
            USER=mother,
            notification_message=f"Nutrition Kit allocated: {kit.product_name}. Please collect it from your Anganwadi center on {kit.distribution_date}.",
            notification_date=date.today()
        )
        messages.success(request, f"Kit successfully allocated to '{mother.name}'!")
        return redirect('/myapp/kit_distribution/')
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def kit_distribution(request)`, `def decrease_stock(kit_name, qty)`
- **Step-by-Step Processing:**
  1. Filters eligible mothers using `get_area_filter_q(teacher.center_name)` to maintain strict ward isolation.
  2. On POST, calls `decrease_stock()` to atomically deduct quantity from center reserve records.
  3. Inserts a new `myapp_nutrition_kit` entry linking `USER=mother` and `TEACHER=teacher`.
  4. Creates a `myapp_kit_notification` record notifying the mother of the pickup date.
  5. Redirects to distribution view with confirmation toast.
- **Database Interaction:** Updates `myapp_nutrition_kit` (stock decrease), inserts allocation record, and inserts `myapp_kit_notification`.

---

## 5. CODE FLOW
1. Teacher navigates to `/myapp/kit_distribution/`.
2. Page lists verified mothers in the teacher's ward alongside available food kits.
3. Teacher selects mother's name, chooses kit, sets collection date, and clicks Submit.
4. Backend checks stock availability, deducts inventory, and records allocation.
5. Automated pickup notification is logged for the mother.
6. Page refreshes displaying the newly scheduled kit distribution.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **giving a food parcel to a registered mother at the Anganwadi center**. The teacher picks the mother's name from her village list, chooses which food packet to give her, and marks the collection date. The system automatically reduces the count on the center's shelf by 1 and sends a message to the mother saying: "Your nutrition packet is ready for pickup!"

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Distribution Form** | Selectors for Beneficiary Mother, Kit Product, Quantity, and Pickup Date. | Form to allocate a kit to a specific mother. |
| **Ward Beneficiaries Dropdown**| Displays verified mothers filtered strictly by the teacher's center ward. | Ensures kits are given to eligible local mothers. |
| **Inventory Stock Auto-Deduct**| Backend routine reducing central inventory when a kit is issued. | Prevents over-distribution of physical stock. |
| **Alert Notification Trigger** | Creates in-app pickup alert in `kit_notification` for the mother. | Automatically informs mother of collection date. |
| **Recent Distributions Grid** | Table showing kits allocated this month with delivery status badges. | Audit table tracking current distribution rounds. |
"""

# 20. kit_history.md
pages["kit_history.md"] = """# Page Documentation: Kit Distribution History (`kit_history.md`)

## 1. PAGE OVERVIEW
The **Kit Distribution History Page** is the audit log of all supplementary nutrition kit handovers. It provides Anganwadi teachers with a filterable history of kits issued, collected, pending, or rescheduled. It allows teachers to mark pending kits as "Distributed", reschedule delivery dates if a mother was unable to visit, or cancel allocations.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Distribution Audit Table: Recipient mother name (`USER.name`), Mother contact phone (`USER.phone`), Kit product name (`product_name`), Kit category (`kit_type`), Quantity, Allocation Date (`date`), Scheduled Distribution Date (`distribution_date`), and Status badge ('Distributed', 'Pending', 'Rescheduled', 'Missed').
  - Filter Controls: Status filter dropdown ('All', 'Distributed', 'Pending', 'Rescheduled').
- **Data Format Example (JSON):**
```json
{
  "id": 24,
  "mother_name": "Ananya Nair",
  "phone": 9847123456,
  "product_name": "Maternal Care Kit Phase 2",
  "distribution_date": "2026-03-12",
  "status": "Distributed"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoints:**
  - View History: `/myapp/kit_history/` (`GET`)
  - Update Delivery Status: `/myapp/update_kit_status/<int:kit_id>/` (`POST` or `GET`)
  - Reschedule Pickup Date: `/myapp/reschedule_kit/` (`POST`)
- **HTTP Methods:** `GET`, `POST`
- **Request Details:** Form parameters or URL kit ID for status changes.
- **Response Details:** Returns updated HTML history table or redirects to `/myapp/kit_history/`.
- **When API is Called:** On page load or when clicking "Mark Collected" or submitting reschedule form.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def update_kit_status(request, kit_id):
    kit = get_object_or_404(nutrition_kit, id=kit_id)
    new_status = request.POST.get('status') or request.GET.get('status', 'Distributed')
    kit.status = new_status
    kit.save()
    messages.success(request, f"Kit #{kit.id} marked as '{new_status}'!")
    return redirect('/myapp/kit_history/')

def reschedule_kit(request):
    if request.method == "POST":
        kit = get_object_or_404(nutrition_kit, id=request.POST.get('kit_id'))
        kit.distribution_date = request.POST.get('new_date')
        kit.status = 'Rescheduled'
        kit.save()
        messages.success(request, f"Kit distribution rescheduled to {kit.distribution_date}!")
        return redirect('/myapp/kit_history/')
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def kit_history(request)`, `def update_kit_status()`, `def reschedule_kit()`
- **Step-by-Step Processing:**
  1. Queries all `myapp_nutrition_kit` entries linked to verified mothers (`USER__ASHA__isnull=False`) under current center.
  2. Applies search and status filters from `request.GET`.
  3. Handles status transitions ('Pending' -> 'Distributed' or 'Rescheduled').
  4. Renders `anganwadi_teacher/kit_history.html`.
- **Database Interaction:** `SELECT * FROM myapp_nutrition_kit JOIN myapp_user_table ...` and `UPDATE myapp_nutrition_kit SET status = ...`.

---

## 5. CODE FLOW
1. Teacher opens `/myapp/kit_history/`.
2. Page displays complete history of past kit allocations.
3. When a mother collects her kit, teacher clicks "Mark Distributed".
4. If a mother misses her date, teacher clicks "Reschedule" and enters a new date.
5. Server updates database record and refreshes the audit table.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like the **Official Delivery Receipt Book of the Anganwadi center**. When mothers come to collect their food packets, the teacher flips to this page and marks them as "Delivered". If a mother was sick and couldn't come on her scheduled day, the teacher can give her a new date next week so she doesn't miss her nutrition kit.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **History Log Header** | Shows page title, total count, and filter dropdowns. | Header controls for filtering delivery history. |
| **Audit Data Table** | Displays Mother, Kit Name, Quantity, Scheduled Date, and Status Badge. | Main historical record table of kit distributions. |
| **Status Update Controls** | Quick buttons to mark kit as "Distributed" or "Missed". | Changes delivery fulfillment status in database. |
| **Reschedule Modal Dialog** | Pop-up modal allowing teacher to set a new pickup date. | Reschedules missed collection appointments. |
"""

# 21. teacher_beneficiaries.md
pages["teacher_beneficiaries.md"] = """# Page Documentation: Center Beneficiaries Directory (`teacher_beneficiaries.md`)

## 1. PAGE OVERVIEW
The **Center Beneficiaries Directory Page** lists all expectant and lactating mothers registered within the Anganwadi teacher's assigned ward. It provides teachers with beneficiary contact details, gestational status, child count, last kit collection date, and features a one-click SMS/in-app reminder dispatch to remind mothers to collect their kits.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Beneficiary Roster: Mother full name (`name`), Husband's name (`husband_name`), Contact phone (`phone`), Residential address (`Address`), Ward area (`area`), Due date / Gestation status (`pregnancy_status_display`), Number of registered children, Last kit received date.
- **Data Collected (Search & Reminder Trigger):**
  - `q`: Search keyword (mother name or phone).
  - `mother_id`: Target mother ID for sending collection reminder.
- **Data Format Example (JSON):**
```json
{
  "mother_id": 14,
  "name": "Pooja Verma",
  "phone": 9846112233,
  "area": "Ward 01 - Main Community Center",
  "status": "Pregnant — Month 7 (28 Weeks)",
  "last_kit_date": "2026-02-20"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoints:**
  - Beneficiaries List: `/myapp/teacher_beneficiaries/` (`GET`)
  - Dispatch Kit Reminder: `/myapp/send_kit_reminder/` (`POST`)
- **HTTP Methods:** `GET`, `POST`
- **Request Details:** `POST` body with `mother_id` and reminder message text.
- **Response Details:** Redirects to `/myapp/teacher_beneficiaries/` with confirmation banner.
- **When API is Called:** On page load or when teacher clicks "Send Collection Reminder".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def teacher_beneficiaries(request):
    teacher = get_current_anganwadi_teacher(request)
    area_q = get_area_filter_q(teacher.center_name) if teacher else Q()
    mothers = user_table.objects.filter(area_q, ASHA__isnull=False).order_by('name')
    return render(request, 'anganwadi_teacher/teacher_beneficiaries.html', {'mothers': mothers, 'teacher': teacher})

def send_kit_reminder(request):
    if request.method == "POST":
        mother = get_object_or_404(user_table, id=request.POST.get('mother_id'))
        notification.objects.create(
            USER=mother,
            message="Friendly Reminder: Your supplementary nutrition kit is ready for pickup at your Anganwadi Center.",
            notification_date=date.today()
        )
        messages.success(request, f"Reminder dispatched to '{mother.name}' successfully!")
        return redirect('/myapp/teacher_beneficiaries/')
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def teacher_beneficiaries()`, `def send_kit_reminder()`
- **Step-by-Step Processing:**
  1. Evaluates teacher's assigned center ward using `get_area_filter_q()`.
  2. Queries verified mothers (`ASHA__isnull=False`) matching the ward criteria.
  3. Prepares gestational stage indicators.
  4. On POST, creates `myapp_notification` alert for the recipient mother.
  5. Renders `anganwadi_teacher/teacher_beneficiaries.html`.
- **Database Interaction:** `SELECT * FROM myapp_user_table WHERE area = ... AND ASHA_id IS NOT NULL` and `INSERT INTO myapp_notification`.

---

## 5. CODE FLOW
1. Teacher clicks "Ward Beneficiaries" on navigation menu.
2. Server fetches all verified pregnant women and new mothers in her center's ward.
3. Roster displays contact details and gestational progress for each mother.
4. Teacher can click "Send Reminder" next to any mother.
5. Server writes an alert to the mother's notification inbox.
6. Success message confirms the reminder was sent.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
This page is the **Village Mother Roster for the Anganwadi teacher**. It is a list of all pregnant women and mothers with newborn babies who live in the teacher's neighborhood. If a mother hasn't come to pick up her food kit for a while, the teacher can press one button to send a friendly reminder message to her phone.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Beneficiaries Header** | Displays ward title, total mother count, and search input. | Header with beneficiary count and search box. |
| **Mothers Roster Table** | Lists mother name, husband, phone, gestational stage, and last kit date. | Table of all verified mothers in the teacher's ward. |
| **Gestational Stage Badge** | Shows current pregnancy month and week (e.g. Month 7, 28 Weeks). | Displays pregnancy progress for each beneficiary. |
| **Send Reminder Action** | One-click button dispatching automated nutrition kit collection notice. | Sends pickup alert directly to mother's account. |
"""

# 22. teacher_profile.md
pages["teacher_profile.md"] = """# Page Documentation: Anganwadi Teacher Profile (`teacher_profile.md`)

## 1. PAGE OVERVIEW
The **Anganwadi Teacher Profile Page** allows the logged-in Anganwadi teacher to review her official center credentials, inspect assigned ward information, update her personal contact phone and address, upload a refreshed profile photograph, and update her account password.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Teacher Credentials: Name (`Name`), Center Name (`center_name`), Educational Qualifications (`Qualification`), Joining Date (`joining_date`), Contact Phone (`Phone`), Email (`Email`), Residential Address (`Address`), Profile Image (`image`), and Account Username.
- **Data Collected (Form POST):**
  - Updated phone, email, address, new profile photo file, and new password with confirmation.
- **Data Format Example (JSON):**
```json
{
  "name": "Radhika Suresh",
  "center_name": "Anganwadi Center 02 - East Sector",
  "phone": 9447123987,
  "email": "radhika.ang@gmail.com",
  "address": "45 Temple Road, Ward 02",
  "qualification": "Early Childhood Education"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/teacher_profile/`
- **HTTP Method:** `GET` (view profile), `POST` (update profile & password)
- **Request Details:** `multipart/form-data` containing contact fields and optional image file.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/teacher_profile/` with success message.
  - Failure: Re-renders profile with error alert.
- **When API is Called:** On loading profile page or clicking "Update Profile".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def teacher_profile_view(request):
    teacher = get_current_anganwadi_teacher(request)
    if request.method == "POST":
        teacher.Phone = request.POST.get('phone', teacher.Phone)
        teacher.Email = request.POST.get('email', teacher.Email)
        teacher.Address = request.POST.get('address', teacher.Address)
        if 'image' in request.FILES:
            teacher.image = FileSystemStorage().save(request.FILES['image'].name, request.FILES['image'])
        teacher.save()
        
        # Optional password update
        new_pw = request.POST.get('new_password')
        if new_pw and len(new_pw) >= 6:
            request.user.set_password(new_pw)
            request.user.save()
            messages.success(request, "Profile and password updated successfully! Please re-login.")
            return redirect('/myapp/login/')
        messages.success(request, "Profile updated successfully!")
        return redirect('/myapp/teacher_profile/')
    return render(request, 'anganwadi_teacher/teacher_profile.html', {'teacher': teacher})
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def teacher_profile_view(request)`
- **Step-by-Step Processing:**
  1. Resolves logged-in teacher using `request.user`.
  2. Renders profile cards on GET.
  3. Validates submitted contact details and image on POST.
  4. Commits changes to `myapp_anganwadi_teacher` and `auth_user`.
  5. Redirects with success notification.
- **Database Interaction:** Executes SQL `UPDATE myapp_anganwadi_teacher` and `UPDATE auth_user`.

---

## 5. CODE FLOW
1. Teacher clicks on profile avatar or "My Profile" in navigation.
2. Page displays current personal and center details.
3. Teacher modifies phone number or uploads a new photo.
4. Teacher clicks "Save Changes".
5. Backend updates database and reloads profile with success notice.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
This page is the **Teacher's Personal Identity & Settings Card**. Just like an employee ID card, it shows the teacher's photo, which Anganwadi center she works at, her phone number, and address. She can come here anytime to update her phone number or change her password.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Profile Card & Photo** | Displays teacher photo, center badge, and account status. | Visual profile banner and center assignment. |
| **Official Center Credentials**| Read-only display of Center Name, Joining Date, and Qualifications. | Shows official appointment details. |
| **Editable Contact Form** | Form inputs for Phone Number, Email, and Address. | Allows teacher to update contact details. |
| **Security & Password Update** | Inputs for new password and password confirmation. | Allows changing portal login password. |
| **Submit Action Button** | Button committing updates to database. | Triggers profile update transaction. |
"""

for fname, text in pages.items():
    with open(os.path.join(OUT_DIR, fname), "w", encoding="utf-8") as f:
        f.write(text.strip())
    print(f"Generated {fname}")

print("Anganwadi pages generated successfully.")
