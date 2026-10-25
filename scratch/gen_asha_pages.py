# -*- coding: utf-8 -*-
import os

OUT_DIR = r"c:\Users\HP\PycharmProjects\maatricaree\code-documentation"

pages = {}

# 23. asha_home.md
pages["asha_home.md"] = """# Page Documentation: ASHA Worker Home Dashboard (`asha_home.md`)

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
"""

# 24. verify_mother.md
pages["verify_mother.md"] = """# Page Documentation: Beneficiary Mother Verification (`verify_mother.md`)

## 1. PAGE OVERVIEW
The **Beneficiary Mother Verification Page** is the clinical onboarding queue for ASHA health workers. In MaatriCare, newly registered mothers cannot access internal health portal features until their identity, residential address, and pregnancy status are verified by their assigned ward ASHA worker. This page allows the worker to inspect registration details, approve/verify the mother (linking her account to the worker), or reject/delete fraudulent entries.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Pending Verification Roster: Mothers residing in the worker's ward with `ASHA_id IS NULL`. Displays full name, husband's name, age, phone number, address, blood group, EDD, and registration timestamp.
  - Verified Mothers Roster: Previously approved mothers in this ward with action to unverify or review.
  - Active ASHA Workers Dropdown: Enables delegating or assigning mother to a colleague in the same ward.
- **Data Collected (Action POST):**
  - `mother_id`: ID of target mother.
  - `action_type`: 'verify_mother', 'unverify_mother', or 'delete_mother'.
  - `asha_id`: ID of the assigned ASHA worker.
- **Data Format Example (JSON):**
```json
{
  "mother_id": 19,
  "name": "Deepa Thomas",
  "husband_name": "Thomas Mathew",
  "phone": 9847112244,
  "area": "Ward 01 - Main Community Center",
  "blood_group": "B+",
  "expected_delivery_date": "2026-10-05",
  "status": "Pending Verification"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoints:**
  - Verification Queue View: `/myapp/verify_mother/` (`GET`)
  - Verification Action: `/myapp/verify_mother/` (`POST`) or `/myapp/verify_mother_action/<int:id>/<str:action>/`
  - Remove Invalid Mother: `/myapp/delete_mother/<int:id>/` (`POST` or `GET`)
- **HTTP Methods:** `GET`, `POST`
- **Request Details:** Form-encoded POST body with `mother_id` and `action_type=verify_mother`.
- **Response Details:** Redirects to `/myapp/verify_mother/` with green success notification.
- **When API is Called:** When ASHA worker clicks "Verify & Assign" or "Reject".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def verify_mother(request):
    worker = get_current_asha_worker(request)
    area_q = get_area_filter_q(worker.Area_assigned) if worker else Q()
    base_area_mothers = user_table.objects.filter(area_q)
    
    if request.method == "POST":
        action_type = request.POST.get("action_type")
        if action_type == "verify_mother":
            mother = get_object_or_404(base_area_mothers, id=request.POST.get("mother_id"))
            mother.ASHA = worker  # Links mother to ASHA worker, unlocking her portal
            mother.save()
            messages.success(request, f"Mother '{mother.name}' has been verified and assigned to you!")
            return redirect('/myapp/verify_mother/')
    
    pending_mothers = base_area_mothers.filter(ASHA__isnull=True).order_by('-id')
    verified_mothers = base_area_mothers.filter(ASHA__isnull=False).order_by('-id')
    return render(request, 'ashawoker/verify_mother.html', {
        'pending_mothers': pending_mothers,
        'verified_mothers': verified_mothers,
        'worker': worker
    })
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def verify_mother()`, `def verify_mother_action()`, `def delete_mother()`
- **Step-by-Step Processing:**
  1. Resolves logged-in ASHA worker and identifies their assigned ward.
  2. Queries `myapp_user_table` splitting into `pending_mothers` (`ASHA__isnull=True`) and `verified_mothers` (`ASHA__isnull=False`).
  3. On POST `verify_mother`: Sets `mother.ASHA = worker` and saves to MySQL. This state change immediately unlocks the mother's account to log in and access maternal services.
  4. On POST `delete_mother`: Deletes `user_table` record and linked `auth_user` credentials.
- **Database Interaction:** `UPDATE myapp_user_table SET ASHA_id = ... WHERE id = ...`.

---

## 5. CODE FLOW
1. Mother registers online; her account is marked as unverified (`ASHA=None`).
2. ASHA worker opens `/myapp/verify_mother/` on her phone or tablet.
3. Pending list shows mother's name, phone, and home address.
4. ASHA worker visits mother or calls her to verify pregnancy details.
5. Worker clicks "Verify & Approve" button.
6. Server assigns `mother.ASHA = worker`.
7. Mother can now log in to the portal and view her health profile.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **a physical home inspection and identity check by a village nurse**. When a pregnant woman signs up on the app, her account is locked until the nurse in her neighborhood checks her details, confirms she lives in that village, and presses the "Verify" button. Once verified, the mother is officially under that nurse's care!

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Verification Queue Header** | Displays count of pending verifications and ward area. | Header displaying queue volume and location. |
| **Pending Mothers Cards** | Information cards showing new mothers awaiting approval. | Displays applicant identity, phone, and due date. |
| **Verification Action Buttons**| "Verify & Assign" button and "Reject / Delete" button. | Commits verification approval or rejects entry. |
| **Verified Beneficiaries Table**| List of currently verified mothers under this worker's supervision. | Roster of active verified mothers in this ward. |
| **Unverify / Reassign Action** | Allows transferring a mother to another worker or resetting status. | Administrative controls to reallocate patients. |
"""

# 25. manage_pregnancy_record.md
pages["manage_pregnancy_record.md"] = """# Page Documentation: Maternal Antenatal Health Records (`manage_pregnancy_record.md`)

## 1. PAGE OVERVIEW
The **Maternal Antenatal Health Records Page** is the clinical examination and Antenatal Care (ANC) logging module. ASHA health workers use this interface to record physiological checkup metrics during maternal home visits: maternal body weight, height, systolic/diastolic blood pressure, hemoglobin count, clinical risk status, and scheduled next checkup dates. It maintains a chronological clinical history and dispatches automated checkup reminders to the mother.

---

## 2. DATA USED IN THIS PAGE
- **Data Collected (Form Submission):**
  - `mother_id`: Beneficiary mother being examined.
  - `checkup_date`: Date of clinical visit.
  - `weight`: Maternal weight in kg.
  - `height`: Maternal height in cm.
  - `blood_pressure`: Blood pressure reading string (e.g., "120/80 mmHg").
  - `hemoglobin`: Hemoglobin count in g/dL.
  - `health_status`: Clinical classification ('Normal', 'High Risk', 'Anemic', 'Hypertensive').
  - `remarks`: Clinical observations and dietary advice.
  - `next_checkup_date`: Scheduled date for next antenatal visit.
- **Data Displayed:**
  - Complete chronological timeline of past checkup records with vital signs and ASHA notes.
- **Data Format Example (JSON):**
```json
{
  "mother_id": 14,
  "checkup_date": "2026-03-15",
  "weight": 64.5,
  "height": 160.0,
  "blood_pressure": "122/82 mmHg",
  "hemoglobin": 11.4,
  "health_status": "Normal",
  "remarks": "Fetal heartbeat regular. Prescribed IFA iron tablets. Nutrition adequate.",
  "next_checkup_date": "2026-04-15"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/manage_pregnancy/` (also `/myapp/manage_pregenecy_record/`, `/myapp/view_pregnancy_records/`)
- **HTTP Method:** `GET` (view checkup logs & form), `POST` (save checkup or delete)
- **Request Details:** Form-encoded POST body containing vital signs and mother ID.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/manage_pregnancy/?tab=list` with success toast.
  - Failure: Re-renders form with validation alert.
- **When API is Called:** When worker clicks "Save Antenatal Record".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def manage_pregnancy(request):
    worker = get_current_asha_worker(request)
    area_q = get_area_filter_q(worker.Area_assigned) if worker else Q()
    all_mothers_qs = user_table.objects.filter(area_q, ASHA__isnull=False).order_by('name')
    
    if request.method == "POST" and request.POST.get("action_type") != "delete_pregnancy_record":
        mother = get_object_or_404(all_mothers_qs, id=request.POST.get("mother_id"))
        rec = pregnancy_record.objects.create(
            USER=mother,
            ASHA=worker,
            previous_pregnency_count=int(request.POST.get("previous_pregnency_count", 0)),
            expected_delivery_date=mother.expected_delivery_date or date.today(),
            checkup_date=request.POST.get("checkup_date"),
            weight=float(request.POST.get("weight", 60.0)),
            height=float(request.POST.get("height", 160.0)),
            blood_pressure=request.POST.get("blood_pressure", "120/80"),
            hemoglobin=float(request.POST.get("hemoglobin", 11.0)),
            health_status=request.POST.get("health_status", "Normal"),
            additional_report=request.POST.get("remarks", ""),
            next_checkup_date=request.POST.get("next_checkup_date")
        )
        # Sends notification to mother
        notification.objects.create(
            USER=mother,
            message=f"Antenatal checkup logged: Blood Pressure {rec.blood_pressure}, Hb {rec.hemoglobin} g/dL. Next visit: {rec.next_checkup_date}.",
            notification_date=date.today()
        )
        messages.success(request, f"Checkup record for '{mother.name}' saved successfully!")
        return redirect('/myapp/manage_pregnancy/?tab=list')
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def manage_pregnancy(request)`
- **Step-by-Step Processing:**
  1. Authenticates current ASHA worker.
  2. Queries verified mothers in this worker's ward.
  3. Parses float values for weight, height, and hemoglobin.
  4. Evaluates clinical thresholds (hemoglobin < 10 marks 'Anemic / High Risk').
  5. Inserts record into `myapp_pregnancy_record`.
  6. Dispatches notification to mother's account.
  7. Redirects to checkup history list.
- **Database Interaction:** Executes SQL `INSERT INTO myapp_pregnancy_record` and `INSERT INTO myapp_notification`.

---

## 5. CODE FLOW
1. ASHA worker visits mother at home with blood pressure cuff and weighing scale.
2. Worker opens `/myapp/manage_pregnancy/` on her phone.
3. She selects the mother from the dropdown and enters vitals.
4. She submits the checkup form.
5. Server saves clinical measurements in MySQL.
6. Mother receives an automatic health alert on her portal.
7. Record appears immediately in the mother's timeline and admin high-risk reports.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **the Doctor's Clinical Chart during a routine pregnancy visit**. The health nurse measures the mother's weight, tests her blood pressure, and tests her blood iron (hemoglobin). She writes these numbers down in the app. If the numbers look good, she marks "Normal". If blood pressure is too high or iron is too low, the system raises a yellow or red flag to protect the mother.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Checkup Navigation Tabs** | Toggles between "Record New Checkup" and "Past Checkup History". | Navigation tabs for logging and viewing checkups. |
| **Mother Selection Dropdown** | Dropdown displaying verified pregnant mothers in this worker's ward. | Selects patient for clinical logging. |
| **Vitals & Clinical Inputs** | Fields for Weight (kg), Height (cm), Blood Pressure, and Hemoglobin (g/dL). | Captures physiological and laboratory vitals. |
| **Risk Status & Remarks** | Dropdown for health condition and textarea for clinical advice. | Classifies maternal risk and records medical notes. |
| **Next Checkup Scheduler** | Date picker to schedule next home visit appointment. | Sets upcoming appointment date for mother. |
| **Checkup History Table** | Chronological table of past clinical visits with vitals and delete action. | Complete antenatal history audit log. |
"""

# 26. register_newborn.md
pages["register_newborn.md"] = """# Page Documentation: Newborn Infant Birth Registration (`register_newborn.md`)

## 1. PAGE OVERVIEW
The **Newborn Infant Birth Registration Page** is the official birth logging module. When a beneficiary mother delivers her baby, the ASHA worker uses this page to register the newborn. It captures the infant's name, gender, exact birth date, birth weight, length/height, blood group, delivery type (Normal/Cesarean), birth hospital, and initial neonatal health status. It creates the child's official identity and establishes baseline growth records.

---

## 2. DATA USED IN THIS PAGE
- **Data Collected (Form Submission):**
  - Mother: `mother_id` (Eligible mothers who reached 3rd trimester / 180+ days).
  - Baby Demographics: `child_name`, `gender` ('Male', 'Female'), `dob` (Birth date).
  - Anthropometric Vitals: `birth_weight` (kg), `birth_height` (cm), `blood_group`.
  - Delivery Circumstances: `place_of_birth` ('Hospital', 'Home', 'PHC'), `delivery_type` ('Normal Delivery', 'Cesarean Section'), `hospital` (Hospital name).
  - Neonatal Health: `health_status` ('Healthy', 'Under Observation', 'Low Birth Weight'), `observations`.
- **Data Displayed:**
  - Registered Newborns Table: List of infants registered in this ward with mother names and birth stats.
- **Data Format Example (JSON):**
```json
{
  "mother_id": 14,
  "child_name": "Aarav Nair",
  "gender": "Male",
  "dob": "2026-03-01",
  "birth_weight": 3.2,
  "birth_height": 50.0,
  "blood_group": "O+",
  "place_of_birth": "Hospital",
  "delivery_type": "Normal Delivery",
  "hospital": "Government Taluk Hospital, Aluva",
  "health_status": "Healthy"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/register_newborn/`
- **HTTP Method:** `GET` (render birth form & registry), `POST` (register infant)
- **Request Details:** Form-encoded POST body containing infant birth vitals.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/register_newborn/` with green celebration notification.
  - Validation Failure: Re-renders form with error message.
- **When API is Called:** When ASHA worker clicks "Register Newborn Baby".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def register_newborn(request):
    worker = get_current_asha_worker(request)
    area_q = get_area_filter_q(worker.Area_assigned) if worker else Q()
    all_area_mothers = user_table.objects.filter(area_q, ASHA__isnull=False)
    
    if request.method == "POST":
        mother = get_object_or_404(all_area_mothers, id=request.POST.get("mother_id"))
        baby = child.objects.create(
            USER=mother,
            ASHA=worker,
            child_name=request.POST.get("child_name"),
            gender=request.POST.get("gender", "Male"),
            date_of_birth=request.POST.get("dob"),
            birth_weight=float(request.POST.get("birth_weight", 3.0)),
            birth_height=float(request.POST.get("birth_height", 50.0)),
            blood_group=request.POST.get("blood_group", "O+"),
            place_of_birth=request.POST.get("place_of_birth", "Hospital"),
            delivery_type=request.POST.get("delivery_type", "Normal Delivery"),
            hospital=request.POST.get("hospital", "General Hospital"),
            health_status=request.POST.get("health_status", "Healthy")
        )
        # Create baseline Day-0 growth record
        child_growth_record.objects.create(
            CHILD=baby,
            height=baby.birth_height,
            weight=baby.birth_weight,
            growth_date=baby.date_of_birth,
            health_condition=baby.health_status,
            report_details="Initial baseline birth measurement recorded by ASHA worker."
        )
        messages.success(request, f"Newborn baby '{baby.child_name}' registered successfully!")
        return redirect('/myapp/register_newborn/')
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def register_newborn(request)`
- **Step-by-Step Processing:**
  1. Identifies eligible mothers in the worker's ward who have completed at least 180 days of gestation or have 6+ checkups.
  2. On POST, creates new record in `myapp_child` linked to `USER=mother` and `ASHA=worker`.
  3. Automatically creates a baseline Day-0 measurement in `myapp_child_growth_record`.
  4. Dispatches celebratory notification alert to mother.
  5. Redirects with success banner.
- **Database Interaction:** Executes SQL `INSERT INTO myapp_child` and `INSERT INTO myapp_child_growth_record`.

---

## 5. CODE FLOW
1. Mother gives birth and informs ASHA worker.
2. ASHA worker opens `/myapp/register_newborn/`.
3. Worker selects mother from eligible list and inputs baby's birth weight and date of birth.
4. Server inserts child profile into database.
5. Server creates starting growth record point (Day 0) for child's future growth chart.
6. Baby is now visible on mother's child profile page and vaccination scheduler.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **issuing a digital Birth Certificate and first medical card for a newborn baby**. When a baby is born, the nurse enters the baby's name, whether it is a boy or a girl, how much the baby weighed at birth, and which hospital delivered the baby. This opens a brand new health file for the baby so the team can monitor its growth and vaccines.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Birth Registration Header** | Displays page title, description, and registered baby counters. | Header introducing birth registration. |
| **Mother Selection Dropdown** | Filters mothers eligible for delivery in this ward. | Selects new mother for birth registration. |
| **Infant Demographics Form** | Fields for Child Name, Gender radio buttons, and Date of Birth. | Captures baby's identity and date of birth. |
| **Birth Anthropometrics** | Inputs for Birth Weight (kg), Birth Length (cm), and Blood Group. | Records physical measurements at birth. |
| **Delivery Details Section** | Inputs for Hospital Name, Place of Birth, and Delivery Method. | Captures medical delivery circumstances. |
| **Registered Infants Table** | Table of all children registered in this ward with birth vitals. | Roster of registered infants in the ward. |
"""

# 27. child_growth_record.md
pages["child_growth_record.md"] = """# Page Documentation: Child Growth & Development Monitoring (`child_growth_record.md`)

## 1. PAGE OVERVIEW
The **Child Growth & Development Monitoring Page** enables ASHA health workers to record pediatric developmental measurements over time. Health workers record periodic weight and height measurements during routine community visits, evaluate nutritional classifications (Normal, Moderately Underweight, Severely Underweight, Stunted), log dietary advice, and inspect developmental trends against WHO child growth standards.

---

## 2. DATA USED IN THIS PAGE
- **Data Collected (Form Submission):**
  - `child_id`: ID of target registered child.
  - `growth_date`: Date on which measurement was taken.
  - `weight`: Current measured body weight in kilograms (kg).
  - `height`: Current measured height / recumbent length in centimeters (cm).
  - `health_condition`: Assessment ('Normal Growth', 'Underweight', 'Severely Underweight', 'Stunted', 'Overweight').
  - `report_details`: Nutritional recommendations, feeding practices, and clinical remarks.
- **Data Displayed:**
  - Chronological growth logs table for selected child.
  - Interactive Chart.js Weight-for-Age and Height-for-Age trend curve.
- **Data Format Example (JSON):**
```json
{
  "child_id": 8,
  "growth_date": "2026-03-10",
  "weight": 8.4,
  "height": 71.5,
  "health_condition": "Normal Growth",
  "report_details": "Weight velocity is normal. Exclusive breastfeeding continued. Alert and active."
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/child_growth_record/` (also `/myapp/child_growth/`, `/myapp/view_child_growth/`)
- **HTTP Method:** `GET` (view growth logs & chart), `POST` (save measurement)
- **Request Details:** Form-encoded POST body with child ID, weight, height, and date.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/child_growth_record/?child_id=<id>` with success toast.
  - Failure: Re-renders form with validation alert.
- **When API is Called:** When ASHA worker clicks "Save Growth Record".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def child_growth_record_view(request):
    worker = get_current_asha_worker(request)
    area_q = get_area_filter_q(worker.Area_assigned) if worker else Q()
    children = child.objects.filter(area_q).select_related('USER')
    
    if request.method == "POST":
        target_child = get_object_or_404(children, id=request.POST.get("child_id"))
        rec = child_growth_record.objects.create(
            CHILD=target_child,
            height=float(request.POST.get("height", 65.0)),
            weight=float(request.POST.get("weight", 7.0)),
            growth_date=request.POST.get("growth_date"),
            health_condition=request.POST.get("health_condition", "Normal"),
            report_details=request.POST.get("report_details", "")
        )
        # Notify mother
        notification.objects.create(
            USER=target_child.USER,
            message=f"Growth record logged for '{target_child.child_name}': Weight {rec.weight} kg, Height {rec.height} cm ({rec.health_condition}).",
            notification_date=date.today()
        )
        messages.success(request, f"Growth record for '{target_child.child_name}' recorded successfully!")
        return redirect(f'/myapp/child_growth_record/?child_id={target_child.id}')
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def child_growth_record_view(request)`
- **Step-by-Step Processing:**
  1. Filters registered children in worker's assigned ward.
  2. On POST, parses height and weight measurements.
  3. Inserts growth datapoint into `myapp_child_growth_record`.
  4. Logs an in-app notification for the mother.
  5. Assembles historical chronological coordinates (dates, weights, heights) for Chart.js rendering.
  6. Renders template `ashawoker/child_growth_record.html`.
- **Database Interaction:** Executes SQL `INSERT INTO myapp_child_growth_record` and `INSERT INTO myapp_notification`.

---

## 5. CODE FLOW
1. ASHA worker visits child's home with portable infant hanging scale and measuring tape.
2. Worker opens `/myapp/child_growth_record/` on smartphone.
3. She selects child's name and enters current weight and height.
4. She clicks "Save Growth Record".
5. Backend writes measurement to database and computes growth velocity.
6. The interactive growth curve updates automatically showing if the child is gaining weight properly.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **marking a child's height and weight on the doorframe every few months**. When the health sister visits the baby, she weighs the baby on a scale and measures how tall the baby has grown. If the baby is growing healthy and chubby, the graph goes up green! If the baby lost weight, the graph warns the nurse that the baby might need extra nutrition food.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Child Selector Card** | Dropdown listing children in worker's ward with age and mother details. | Selects child for growth measurement. |
| **Measurement Logging Form** | Inputs for Growth Date, Weight (kg), Height (cm), and Nutritional Status. | Captures physical growth measurements. |
| **Clinical Notes & Diet** | Textarea for feeding recommendations and nutritional remarks. | Records feeding practices and advice. |
| **Interactive Growth Chart** | Chart.js visual canvas displaying Weight and Height progression curves. | Visual graph comparing child growth over time. |
| **Chronological Records Table**| Historical measurement log showing dates, numbers, and delete action. | Complete tabular history of all growth checkups. |
"""

# 28. asha_profile.md
pages["asha_profile.md"] = """# Page Documentation: ASHA Worker Profile (`asha_profile.md`)

## 1. PAGE OVERVIEW
The **ASHA Worker Profile Page** allows the logged-in field worker to inspect her official registration details, review her assigned Grama Panchayat ward, update personal contact numbers and residential address, refresh her profile photograph, and change her account password.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Official Profile: Full Name (`Full_name`), Ward Assignment (`Area_assigned`), Official Contact Phone (`Phone`), Email (`Email`), Qualification (`Qualification`), Service Joining Date (`Joining_date`), Profile Picture (`image`), and Username.
- **Data Collected (Form POST):**
  - Updated phone, email, address, new profile image file, and new password with confirmation.
- **Data Format Example (JSON):**
```json
{
  "full_name": "Kavitha Menon",
  "area_assigned": "Ward 01 - Main Community Center",
  "phone": 9876543210,
  "email": "kavitha.asha@gmail.com",
  "qualification": "GNM Nursing",
  "address": "House 12, Ward 01 Grama Colony"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/ashaworker_profile/`
- **HTTP Method:** `GET` (view profile), `POST` (save updates & password)
- **Request Details:** `multipart/form-data` containing contact fields and optional image binary.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/ashaworker_profile/` with success toast.
  - Failure: Re-renders form with error message.
- **When API is Called:** On loading profile page or submitting updates.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def ashaworker_profile_view(request):
    worker = get_current_asha_worker(request)
    if request.method == "POST":
        worker.Phone = request.POST.get('phone', worker.Phone)
        worker.Email = request.POST.get('email', worker.Email)
        worker.Address = request.POST.get('address', worker.Address)
        if 'image' in request.FILES:
            worker.image = FileSystemStorage().save(request.FILES['image'].name, request.FILES['image'])
        worker.save()
        
        # Handle password reset
        new_pw = request.POST.get('new_password')
        if new_pw and len(new_pw) >= 6:
            request.user.set_password(new_pw)
            request.user.save()
            messages.success(request, "Profile & password updated successfully! Please re-login.")
            return redirect('/myapp/login/')
        messages.success(request, "Profile details updated successfully!")
        return redirect('/myapp/ashaworker_profile/')
    return render(request, 'ashawoker/asha_profile.html', {'worker': worker})
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def ashaworker_profile_view(request)`
- **Step-by-Step Processing:**
  1. Resolves logged-in ASHA worker from `request.user`.
  2. Renders profile details on GET.
  3. On POST, updates contact phone, email, and address.
  4. Saves uploaded profile photo to `media/`.
  5. If password was changed, re-hashes password via `request.user.set_password()`.
  6. Commits updates to database.
- **Database Interaction:** Executes SQL `UPDATE myapp_asha_worker` and `UPDATE auth_user`.

---

## 5. CODE FLOW
1. ASHA worker clicks on profile photo or "My Profile" in sidebar.
2. Page displays official details, photo, and assigned ward.
3. Worker modifies contact number or password and clicks "Update Profile".
4. Server validates data and updates MySQL tables.
5. Confirmation alert appears on screen.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
This page is the **ASHA Health Worker's Official Identity and Account Settings**. It shows her photo, her assigned village area, and her phone number. If she buys a new SIM card or gets a new mobile number, she can update it here so that mothers and the hospital can always reach her.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Worker Identity Card** | Displays photo, full name, assigned ward, and active status badge. | Visual summary of worker credentials. |
| **Official Qualifications** | Read-only display of Qualifications, Joining Date, and Username. | Official service and employment records. |
| **Contact Edit Fields** | Form inputs for Mobile Phone, Email, and Residential Address. | Allows modifying personal contact info. |
| **Password Security Form** | Inputs for new password and password confirmation. | Updates portal login password. |
| **Update Commit Action** | Submit button executing profile changes. | Saves updates to database. |
"""

for fname, text in pages.items():
    with open(os.path.join(OUT_DIR, fname), "w", encoding="utf-8") as f:
        f.write(text.strip())
    print(f"Generated {fname}")

print("ASHA worker pages generated successfully.")
