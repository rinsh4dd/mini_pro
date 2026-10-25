# -*- coding: utf-8 -*-
import os

OUT_DIR = r"c:\Users\HP\PycharmProjects\maatricaree\code-documentation"

pages = {}

# 29. user_home.md
pages["user_home.md"] = """# Page Documentation: Beneficiary Mother Dashboard (`user_home.md`)

## 1. PAGE OVERVIEW
The **Beneficiary Mother Dashboard** is the personal maternal and child health command center for registered mothers. It provides expectant mothers with a visual pregnancy journey tracker (gestational week, trimester stage, delivery countdown), clinical vital summaries from their latest checkup, contact information for their assigned ASHA worker, child cards, upcoming immunization session dates, supplementary nutrition kit pickup statuses, and health alert notices.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Maternal Progress: Gestation weeks (`gest_weeks`), Trimester number (`trimester`), Progress percentage (`gest_percent`), Estimated Delivery Date (`edd_str`), Days to Delivery (`days_to_go_str`), and Current Weight.
  - Assigned ASHA Worker Card: ASHA worker name, phone number, and ward.
  - Child Quick Cards: Registered children names, age in months, and latest weight.
  - Upcoming Healthcare Events: Next scheduled vaccine dose and date, pending nutrition kit distribution status, and latest unread notifications.
- **Data Source:** `myapp_user_table`, `myapp_pregnancy_record`, `myapp_child`, `myapp_vaccination`, `myapp_nutrition_kit`, `myapp_notification`.
- **Data Format Example (Context JSON):**
```json
{
  "mother_name": "Ananya Nair",
  "gest_weeks": 26,
  "trimester": 2,
  "days_to_delivery": 98,
  "edd": "Nov 20, 2026",
  "asha_name": "Kavitha Menon",
  "asha_phone": 9876543210,
  "next_vaccine": "Pentavalent Dose 2 (Scheduled: Apr 12)",
  "kit_status": "Ready for Pickup at Center 01"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/userhome/`
- **HTTP Method:** `GET`
- **Request Details:** Authenticated GET request with session cookie for a verified mother.
- **Response Details:** Returns compiled HTML (`user/user_home.html`) with maternal context.
- **When API is Called:** On mother login or clicking "Home" in maternal portal.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def userhome(request):
    mother, err_redirect = get_logged_in_mother(request)
    if err_redirect:
        return err_redirect
    
    today_dt = date.today()
    preg_rec = pregnancy_record.objects.filter(USER=mother).order_by('-checkup_date').first()
    
    if preg_rec and preg_rec.expected_delivery_date:
        edd = preg_rec.expected_delivery_date
        days_left = max((edd - today_dt).days, 0)
        gest_weeks = max(min((280 - days_left) // 7, 40), 1)
        trimester = 1 if gest_weeks <= 13 else (2 if gest_weeks <= 27 else 3)
    
    children_list = child.objects.filter(USER=mother)
    upcoming_vax = vaccination.objects.filter(CHILD__USER=mother, status='Scheduled').order_by('vaccination_date').first()
    latest_kit = nutrition_kit.objects.filter(USER=mother).order_by('-distribution_date').first()
    return render(request, 'user/user_home.html', context)
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def userhome(request)`, `def get_logged_in_mother(request)`
- **Step-by-Step Processing:**
  1. `get_logged_in_mother()` checks if user has an associated `user_table` profile and verifies that `ASHA IS NOT NULL`.
  2. Calculates real-time gestational progress: `(280 - (EDD - today)) // 7`.
  3. Queries children associated with this mother.
  4. Fetches the nearest scheduled vaccination and nutrition kit distribution date.
  5. Renders `user/user_home.html`.
- **Database Interaction:** Multi-table queries on `myapp_user_table`, `myapp_pregnancy_record`, `myapp_child`, `myapp_vaccination`, and `myapp_nutrition_kit`.

---

## 5. CODE FLOW
1. Mother logs in to MaatriCare.
2. Server verifies her account is ASHA-approved and directs her to `/myapp/userhome/`.
3. Server computes her pregnancy calendar and countdown.
4. Screen displays progress bar, due date, assigned ASHA contact, and baby immunization alerts.
5. Mother can click on any card to view detailed records.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like a **personalized Pregnancy and Baby Diary app on a mother's smartphone**. It tells her: "You are in Week 26 of your pregnancy (Trimester 2)! There are 98 days left until you meet your baby. Your local health nurse is Kavitha, and you can call her anytime. Your baby Aarav has a vaccine scheduled for next month, and your nutrition food packet is ready to be collected."

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Welcome & Stage Banner** | Shows mother name, pregnancy trimester badge, and due date countdown. | Header greeting and pregnancy status. |
| **Gestation Progress Bar** | Visual percentage bar displaying weeks completed out of 40 weeks. | Graphic indicator of pregnancy progression. |
| **Assigned ASHA Worker Card** | Displays local ASHA worker's photo, name, phone number, and call button. | Direct emergency contact card for health worker. |
| **Children Quick Summary** | Cards showing registered babies with birth weights and milestone age. | Quick access to baby profiles. |
| **Upcoming Healthcare Events** | Highlights next vaccination appointment and nutrition kit pickup date. | Prompts mother about upcoming health appointments. |
| **Quick Action Shortcuts** | Direct links to Antenatal Records, Child Growth, and Nutrition History. | Fast navigation across maternal portal features. |
"""

# 30. user_profile.md
pages["user_profile.md"] = """# Page Documentation: Mother Profile & Demographics (`user_profile.md`)

## 1. PAGE OVERVIEW
The **Mother Profile Page** provides beneficiary mothers with complete visibility over their registered personal, residential, and medical profile details. It displays their registered blood group, spouse's name, assigned Grama Panchayat ward, assigned ASHA worker, and allows mothers to update their contact telephone number, postal address, and login password.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Personal Demographics: Full Name (`name`), Husband's Name (`husband_name`), Age (`age`), Date of Birth (`dob`), Blood Group (`blood_group`).
  - Residential & Geographic: Address (`Address`), Panchayath (`panchayath`), Ward (`area`), District (`district`), State (`state`), Pincode (`pincode`).
  - Maternal Details: Expected Delivery Date (`expected_delivery_date`), Registration Date (`registration_date`).
  - Healthcare Association: Assigned ASHA Worker Name (`ASHA.Full_name`), Worker Contact Phone (`ASHA.Phone`).
- **Data Collected (Edit Form POST):**
  - Updated phone, address, and new password with confirmation.
- **Data Format Example (JSON):**
```json
{
  "name": "Ananya Nair",
  "husband_name": "Rajesh Nair",
  "age": 26,
  "blood_group": "O+",
  "phone": 9847123456,
  "panchayath": "Nedumbassery",
  "area": "Ward 02 - East Sector",
  "pincode": "683572",
  "asha_worker": "Kavitha Menon (Ph: 9876543210)"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoints:**
  - View Profile: `/myapp/user_profile/` or `/myapp/view_profile/` (`GET`)
  - Edit Profile: `/myapp/edit_user_profile/` (`POST`)
- **HTTP Methods:** `GET`, `POST`
- **Request Details:** Form-encoded POST payload containing updated phone, address, and passwords.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/view_profile/` with green confirmation notice.
  - Failure: Re-renders profile with error alert.
- **When API is Called:** On loading profile page or clicking "Save Changes".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def user_profile_view(request):
    mother, err_redirect = get_logged_in_mother(request)
    if err_redirect:
        return err_redirect
    return render(request, 'user/view_profile.html', {'mother': mother})

def edit_user_profile(request):
    mother, err_redirect = get_logged_in_mother(request)
    if err_redirect:
        return err_redirect
    if request.method == "POST":
        mother.phone = request.POST.get('phone', mother.phone)
        mother.Address = request.POST.get('address', mother.Address)
        mother.save()
        
        new_pw = request.POST.get('new_password')
        if new_pw and len(new_pw) >= 6:
            request.user.set_password(new_pw)
            request.user.save()
            messages.success(request, "Profile and password updated successfully! Please re-login.")
            return redirect('/myapp/login/')
        messages.success(request, "Profile information updated successfully!")
        return redirect('/myapp/view_profile/')
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def user_profile_view()`, `def edit_user_profile()`
- **Step-by-Step Processing:**
  1. Identifies logged-in mother via `get_logged_in_mother()`.
  2. Queries `myapp_user_table` linked to current `request.user`.
  3. Renders pre-filled profile view on GET.
  4. On POST, updates phone and address fields in `myapp_user_table`.
  5. If password was provided, re-encrypts password in `auth_user`.
  6. Commits changes to database.
- **Database Interaction:** `SELECT * FROM myapp_user_table WHERE LOGIN_id = ...` and `UPDATE myapp_user_table SET ...`.

---

## 5. CODE FLOW
1. Mother clicks "Profile" on the top navigation.
2. Server loads her personal and health records from MySQL.
3. Page displays her information cards and assigned ASHA contact.
4. Mother updates her contact phone or password and clicks Save.
5. Server writes changes to the database and reloads with success notice.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
This page is the **Mother's Official Health Identity Card**. It shows her name, blood group, home address, and the name and phone number of her assigned village health sister. If she changes her phone number or wants to create a new password, she can do it here.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Profile Identity Card** | Displays mother name, blood group badge, and due date. | Visual header highlighting patient identity. |
| **Personal Demographics Block**| Shows Husband's Name, Age, DOB, and Registration Date. | Core personal and demographic records. |
| **Address & Ward Block** | Displays postal address, panchayath, ward, and district. | Geographic and residential records. |
| **Assigned ASHA Worker Card** | Displays the dedicated ASHA worker's name and contact number. | Dedicated field healthcare worker connection. |
| **Edit Profile Modal / Form** | Form fields to update phone, address, and account password. | Allows mother to update contact details. |
"""

# 31. user_pregnancy_record.md
pages["user_pregnancy_record.md"] = """# Page Documentation: Antenatal Pregnancy Health Timeline (`user_pregnancy_record.md`)

## 1. PAGE OVERVIEW
The **Antenatal Pregnancy Health Timeline Page** gives mothers transparent access to their clinical examination history. It displays every checkup conducted by their ASHA health worker, including recorded body weight, blood pressure measurements, hemoglobin levels, clinical risk classifications, dietary advice, and upcoming visit appointments.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Clinical Checkups Timeline: Checkup date (`checkup_date`), Maternal Weight (`weight`), Height (`height`), Blood Pressure (`blood_pressure`), Hemoglobin (`hemoglobin`), Health Status (`health_status`), Clinical remarks/advice (`additional_report`), Next scheduled visit (`next_checkup_date`).
  - Latest Vitals Summary: Current BMI, latest BP reading, and hemoglobin anemia status.
- **Data Source:** `myapp_pregnancy_record` filtered by `USER=mother`.
- **Data Format Example (JSON):**
```json
[
  {
    "checkup_date": "2026-03-15",
    "weight": 64.5,
    "blood_pressure": "120/80 mmHg",
    "hemoglobin": 11.4,
    "health_status": "Normal",
    "remarks": "Fetal growth on track. Take iron supplements daily after meals.",
    "next_checkup_date": "2026-04-15"
  }
]
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/user_pregnancy_record/` (also `/myapp/view_pregnency_record/`)
- **HTTP Method:** `GET`
- **Request Details:** Authenticated GET request with mother session.
- **Response Details:** Returns compiled HTML (`user/view_pregnency_record.html`) with clinical records timeline.
- **When API is Called:** On navigation to "Pregnancy Records".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def user_pregnancy_record(request):
    mother, err_redirect = get_logged_in_mother(request)
    if err_redirect:
        return err_redirect
    records = pregnancy_record.objects.filter(USER=mother).order_by('-checkup_date')
    latest_record = records.first()
    return render(request, 'user/view_pregnency_record.html', {
        'records': records,
        'latest_record': latest_record,
        'mother': mother
    })
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def user_pregnancy_record(request)`
- **Step-by-Step Processing:**
  1. Identifies logged-in mother.
  2. Queries all `myapp_pregnancy_record` entries where `USER=mother`.
  3. Sorts records in reverse chronological order (newest checkup first).
  4. Renders `user/view_pregnency_record.html`.
- **Database Interaction:** `SELECT * FROM myapp_pregnancy_record WHERE USER_id = ... ORDER BY checkup_date DESC`.

---

## 5. CODE FLOW
1. Mother clicks "Pregnancy Records" in her dashboard menu.
2. Server retrieves all medical checkup logs recorded by her ASHA worker.
3. Page displays a clean clinical timeline with weight and blood pressure badges.
4. Mother can review her doctor/nurse remarks and see when her next visit is due.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
This page is the **Mother's Digital Antenatal Hospital Book**. Instead of carrying a paper notebook to every hospital checkup that might get lost, all her medical readings—her weight gain, blood pressure, blood iron test, and the nurse's dietary advice—are safely saved here in date order.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Maternal Timeline Banner** | Displays mother name, gestation week, and summary vital badges. | Header summarizing latest maternal vitals. |
| **Latest Checkup Card** | Prominently displays the most recent clinical examination results. | Highlights latest health checkup vitals. |
| **Chronological Timeline Cards**| Cards for each past checkup with date, vitals, and health status badge. | Historical timeline of past medical visits. |
| **Nurse Notes & Dietary Advice**| Text section displaying instructions and nutrition advice from ASHA worker. | Clinical notes and advice from health worker. |
| **Next Checkup Reminder** | Date banner showing next scheduled home visit appointment. | Informs mother of next scheduled visit. |
"""

# 32. user_child_profile.md
pages["user_child_profile.md"] = """# Page Documentation: Registered Children Profiles (`user_child_profile.md`)

## 1. PAGE OVERVIEW
The **Registered Children Profiles Page** displays comprehensive birth and medical profiles for all children registered under the beneficiary mother. It presents each child's name, gender, date of birth, age (computed in months and years), birth weight, birth height, blood group, delivery circumstances, birth hospital, and provides direct navigation buttons to inspect the child's growth curve and vaccination schedule.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Child Demographics: Full name (`child_name`), Gender (`gender`), Date of Birth (`date_of_birth`), Computed age in months.
  - Birth Anthropometrics: Birth weight (`birth_weight`), Birth length/height (`birth_height`), Blood Group (`blood_group`).
  - Birth Records: Facility type (`place_of_birth`), Delivery method (`delivery_type`), Hospital name (`hospital`), Neonatal health status (`health_status`).
  - Action Links: Direct links to Child Growth Tracker and Child Vaccination Schedule.
- **Data Source:** `myapp_child` where `USER=mother`.
- **Data Format Example (JSON):**
```json
{
  "child_name": "Aarav Nair",
  "gender": "Male",
  "date_of_birth": "2025-06-10",
  "age_display": "9 Months",
  "birth_weight": 3.2,
  "birth_height": 50.0,
  "blood_group": "O+",
  "delivery_type": "Normal Delivery",
  "hospital": "Government Taluk Hospital, Aluva",
  "health_status": "Healthy"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/user_child_profile/`
- **HTTP Method:** `GET`
- **Request Details:** Authenticated GET request with mother session.
- **Response Details:** Returns compiled HTML (`user/user_child_profile.html`) with children profiles.
- **When API is Called:** On navigation to "Child Profiles".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def user_child_profile(request):
    mother, err_redirect = get_logged_in_mother(request)
    if err_redirect:
        return err_redirect
    children = child.objects.filter(USER=mother).order_by('-date_of_birth')
    return render(request, 'user/user_child_profile.html', {
        'children': children,
        'mother': mother
    })
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def user_child_profile(request)`
- **Step-by-Step Processing:**
  1. Authenticates mother account.
  2. Queries `myapp_child` table for records belonging to `USER=mother`.
  3. Computes each child's current age from `date_of_birth`.
  4. Renders `user/user_child_profile.html`.
- **Database Interaction:** `SELECT * FROM myapp_child WHERE USER_id = ...`.

---

## 5. CODE FLOW
1. Mother clicks "Child Profiles" in portal menu.
2. Server queries registered children linked to mother.
3. Page displays child identity cards with birth statistics.
4. Mother can click "View Growth Chart" or "View Vaccination Schedule" to navigate.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
This page is the **Official Health Profile of a Mother's Babies**. If a mother has one or two children registered in the system, each child gets their own card showing their date of birth, how much they weighed when born, which hospital they were delivered in, and quick buttons to check their vaccine card or growth chart.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Children Roster Header** | Shows title and total count of registered children. | Header introducing child profiles. |
| **Child Profile Cards** | Detailed cards displaying child photo/icon, name, age, and gender. | Individual identification cards for each child. |
| **Birth Anthropometrics Grid** | Grid showing birth weight, length, blood group, and health rating. | Displays physical measurements at birth. |
| **Delivery Information** | Displays hospital name, delivery method, and place of birth. | Records medical circumstances of delivery. |
| **Portal Feature Shortcuts** | Action buttons linking to Growth Tracker and Vaccination Schedule. | Direct shortcuts to child's vaccines and growth charts. |
"""

# 33. user_child_growth.md
pages["user_child_growth.md"] = """# Page Documentation: Child Growth & Development Charts (`user_child_growth.md`)

## 1. PAGE OVERVIEW
The **Child Growth & Development Charts Page** provides mothers with an interactive visual tracking tool for their child's physical development. It plots the child's weight-for-age and height-for-age progression against healthy developmental reference curves using Chart.js, displays nutritional status assessments from ASHA visits, and lists chronological measurement logs.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Selected Child Details: Child name, date of birth, current age in months, current weight, and latest height.
  - Interactive Growth Curves: Chart.js visualization plotting measured weight (kg) and height (cm) over chronological time.
  - Growth Measurements Table: Date of measurement (`growth_date`), Recorded Weight (`weight`), Recorded Height (`height`), Nutritional Condition (`health_condition`), and ASHA Dietary Guidance (`report_details`).
- **Data Source:** `myapp_child_growth_record` linked to `myapp_child` where `USER=mother`.
- **Data Format Example (JSON):**
```json
{
  "child_name": "Aarav Nair",
  "current_weight": 8.4,
  "current_height": 71.5,
  "records": [
    {"date": "2025-06-10", "weight": 3.2, "height": 50.0, "status": "Birth Baseline"},
    {"date": "2025-09-15", "weight": 5.8, "height": 60.5, "status": "Normal Growth"},
    {"date": "2026-03-10", "weight": 8.4, "height": 71.5, "status": "Normal Growth"}
  ]
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/user_child_growth/` (also `/myapp/view_child_growth_user/`)
- **HTTP Method:** `GET`
- **Request Details:** Query parameter `?child_id=<id>` (defaults to mother's first child).
- **Response Details:** Returns compiled HTML (`user/view_child_growth.html`) with growth dataset and Chart.js payload.
- **When API is Called:** On navigation to "Growth Charts" or when selecting a child.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def user_child_growth(request):
    mother, err_redirect = get_logged_in_mother(request)
    if err_redirect:
        return err_redirect
    children = child.objects.filter(USER=mother)
    selected_child = children.filter(id=request.GET.get('child_id')).first() or children.first()
    
    growth_records = child_growth_record.objects.filter(CHILD=selected_child).order_by('growth_date')
    dates = [r.growth_date.strftime('%b %d, %Y') for r in growth_records]
    weights = [r.weight for r in growth_records]
    heights = [r.height for r in growth_records]
    return render(request, 'user/view_child_growth.html', {
        'children': children,
        'selected_child': selected_child,
        'records': growth_records,
        'dates_json': json.dumps(dates),
        'weights_json': json.dumps(weights),
        'heights_json': json.dumps(heights)
    })
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def user_child_growth(request)`
- **Step-by-Step Processing:**
  1. Identifies logged-in mother and retrieves her children.
  2. Resolves selected child from `request.GET.get('child_id')`.
  3. Queries chronological growth measurements from `myapp_child_growth_record`.
  4. Formats dates, weights, and heights into JSON arrays for Chart.js.
  5. Renders `user/view_child_growth.html`.
- **Database Interaction:** `SELECT * FROM myapp_child_growth_record WHERE CHILD_id = ... ORDER BY growth_date ASC`.

---

## 5. CODE FLOW
1. Mother clicks "Child Growth" in portal navigation.
2. Server loads growth measurements for the baby.
3. Template passes data coordinates to Chart.js.
4. Browser renders interactive graphical curve showing baby's weight gain over time.
5. Table below lists historical measurements and nurse's feeding advice.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **a digital Growth Chart poster hanging on the clinic wall**. Every time the nurse weighs and measures the baby, a new dot is added to the chart. As the baby gets older, the line connects the dots into a curve going up. If the line is climbing smoothly, the mother can be happy that her baby is growing well and healthy!

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Child Selector Tabs** | Toggles between siblings if the mother has multiple children. | Allows switching between children. |
| **Current Vitals Summary** | Cards showing latest Weight (kg), Height (cm), and Nutritional Rating. | Snapshot of child's most recent vitals. |
| **Interactive Chart Canvas** | Chart.js visual curve plotting Weight and Height over time. | Graphical visualization of growth velocity. |
| **Historical Measurement Table**| Table listing date, weight, height, status, and ASHA remarks. | Chronological audit log of physical checkups. |
| **WHO Guidelines Explainer** | Informational section explaining healthy child growth milestones. | Educates mothers on normal developmental stages. |
"""

# 34. user_vaccination_schedule.md
pages["user_vaccination_schedule.md"] = """# Page Documentation: Child Immunization Card (`user_vaccination_schedule.md`)

## 1. PAGE OVERVIEW
The **Child Immunization Card Page** is the mother's official digital vaccine passport for her child. It displays the complete immunization schedule from birth through age 5 according to the National Immunization Schedule (BCG, OPV, Hepatitis B, Pentavalent, Rotavirus, Measles-Rubella, DPT boosters), dose administration statuses, scheduled session dates, and clinic operational hours.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Immunization Passport Table: Vaccine name (`vaccine_name`), Target age milestone (`target_month_display`), Scheduled date (`vaccination_date`), Clinical indications (`description`), Session time window, and Status badge ('Administered', 'Scheduled', 'Upcoming', 'Overdue').
  - Immunization Compliance Counter: Doses Completed vs Total Doses Scheduled.
- **Data Source:** `myapp_vaccination` and `myapp_vaccine_schedule` linked to `CHILD` where `USER=mother`.
- **Data Format Example (JSON):**
```json
[
  {
    "vaccine_name": "BCG (Bacillus Calmette–Guérin)",
    "target_month": "Month 0 (At Birth)",
    "status": "Administered",
    "date": "2025-06-12"
  },
  {
    "vaccine_name": "Pentavalent Dose 1",
    "target_month": "Month 2 (2nd Month)",
    "status": "Administered",
    "date": "2025-08-15"
  },
  {
    "vaccine_name": "Measles-Rubella (MR) Dose 1",
    "target_month": "Month 9",
    "status": "Scheduled",
    "date": "2026-03-25"
  }
]
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/user_vaccination_schedule/` (also `/myapp/view_vaccination_schedule/`)
- **HTTP Method:** `GET`
- **Request Details:** Query parameter `?child_id=<id>`.
- **Response Details:** Returns compiled HTML (`user/view_vaccination_schedule.html`) with immunization records.
- **When API is Called:** On navigation to "Vaccination Schedule".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def user_vaccination_schedule(request):
    mother, err_redirect = get_logged_in_mother(request)
    if err_redirect:
        return err_redirect
    children = child.objects.filter(USER=mother)
    selected_child = children.filter(id=request.GET.get('child_id')).first() or children.first()
    
    vaccines = vaccination.objects.filter(CHILD=selected_child).order_by('target_month', 'id')
    completed_count = vaccines.filter(status='Administered').count()
    total_count = vaccines.count()
    return render(request, 'user/view_vaccination_schedule.html', {
        'children': children,
        'selected_child': selected_child,
        'vaccines': vaccines,
        'completed_count': completed_count,
        'total_count': total_count
    })
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def user_vaccination_schedule(request)`
- **Step-by-Step Processing:**
  1. Authenticates logged-in mother.
  2. Resolves selected child.
  3. Queries `myapp_vaccination` records linked to this child.
  4. Evaluates completed doses vs pending doses.
  5. Renders `user/view_vaccination_schedule.html`.
- **Database Interaction:** `SELECT * FROM myapp_vaccination WHERE CHILD_id = ... ORDER BY target_month ASC`.

---

## 5. CODE FLOW
1. Mother clicks "Vaccine Card" in portal navigation.
2. Server loads complete vaccine schedule for her child.
3. Page displays digital immunization card with green badges for completed doses and calendar dates for upcoming doses.
4. Mother can show this card during clinic visits or print it.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **a digital version of the yellow Baby Vaccination Card**. Instead of worrying about losing the paper card, the mother can open her phone to see all her baby's injections. It shows which vaccines have already been given (with green checkmarks) and which vaccine is due next so the baby never misses an immunization.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Immunization Card Header** | Displays child name, DOB, and completed doses ratio badge. | Header summarizing child vaccination progress. |
| **Child Selector Tabs** | Allows toggling between children if multiple exist. | Navigation selector for different children. |
| **Digital Vaccine Passport** | Table listing Vaccine Name, Target Age, Date, and Status Badge. | Main immunization schedule table. |
| **Status Badges** | Color-coded badges: Green for Administered, Blue for Scheduled, Red for Overdue. | Visual indicators of dose completion. |
| **Vaccine Indications Modal**| Explanatory pop-up detailing the diseases prevented by each vaccine dose. | Educates mothers about vaccine protections. |
"""

# 35. user_kit_history.md
pages["user_kit_history.md"] = """# Page Documentation: Nutrition Kit Allocation & History (`user_kit_history.md`)

## 1. PAGE OVERVIEW
The **Nutrition Kit Allocation & History Page** is the mother's supplementary food benefit passbook. It displays all maternal and infant nutrition kits allocated to her by her local Anganwadi center. Mothers can verify package contents, check scheduled distribution dates, track pickup statuses (Pending, Distributed, Rescheduled), and review historical receipts.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Nutrition Kit Passbook Table: Kit Product Name (`product_name`), Category (`kit_type`), Nutritional Contents (`product_details`), Allocated Quantity (`quantity`), Allocation Date (`date`), Scheduled Pickup Date (`distribution_date`), Fulfillment Status badge ('Distributed', 'Pending', 'Rescheduled'), and Distributing Teacher Name.
- **Data Source:** `myapp_nutrition_kit` where `USER=mother`.
- **Data Format Example (JSON):**
```json
[
  {
    "id": 14,
    "product_name": "Amrutham Nutri-Mix Phase 2",
    "kit_type": "Maternal Nutrition Kit",
    "product_details": "Fortified roasted cereal mix, Iron tablets, Folic acid packets",
    "quantity": 1,
    "distribution_date": "2026-03-12",
    "status": "Distributed",
    "teacher_name": "Radhika Suresh (Anganwadi Center 02)"
  }
]
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/user_kit_history/` (also `/myapp/view_kit_history/`)
- **HTTP Method:** `GET`
- **Request Details:** Authenticated GET request with mother session.
- **Response Details:** Returns compiled HTML (`user/view_kit_history.html`) with kit history table.
- **When API is Called:** On navigation to "Nutrition Kits".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def user_kit_history(request):
    mother, err_redirect = get_logged_in_mother(request)
    if err_redirect:
        return err_redirect
    kits = nutrition_kit.objects.filter(USER=mother).select_related('TEACHER').order_by('-distribution_date', '-id')
    return render(request, 'user/view_kit_history.html', {'kits': kits, 'mother': mother})
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def user_kit_history(request)`
- **Step-by-Step Processing:**
  1. Authenticates mother account.
  2. Queries `myapp_nutrition_kit` table where `USER=mother`.
  3. Uses `select_related('TEACHER')` to retrieve Anganwadi center details.
  4. Renders `user/view_kit_history.html`.
- **Database Interaction:** `SELECT * FROM myapp_nutrition_kit WHERE USER_id = ... ORDER BY distribution_date DESC`.

---

## 5. CODE FLOW
1. Mother clicks "Nutrition Kits" in portal navigation.
2. Server loads nutrition kit allocations for her account.
3. Page displays her kit passbook with pickup dates and status badges.
4. Mother can see if her next kit is ready to be collected from the Anganwadi center.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **a digital Ration & Nutrition Passbook for the mother**. Every time the Anganwadi center prepares a box of healthy food, cereal mix, and vitamins for the mother or baby, it is entered here. The mother can see what food items are in the box, when she should pick it up, and past food packets she already received.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Nutrition Passbook Header** | Shows page title and summary badge of kits received. | Header introducing nutrition kit benefits. |
| **Kit Allocation Cards / Table**| Lists Product Name, Contents, Quantity, Date, and Status Badge. | Main audit passbook of allocated nutrition kits. |
| **Package Composition Details**| Text section detailing ingredients and nutritional benefits. | Discloses ingredients and nutritional breakdown. |
| **Pickup Status Indicators** | Badges showing "Ready for Pickup", "Distributed", or "Rescheduled". | Informs mother of kit collection status. |
| **Anganwadi Center Details** | Displays the teacher's name and center address for pickup. | Informs mother where to collect her packet. |
"""

# 36. user_notifications.md
pages["user_notifications.md"] = """# Page Documentation: Notifications & Health Alerts Inbox (`user_notifications.md`)

## 1. PAGE OVERVIEW
The **Notifications & Health Alerts Inbox Page** is the personalized communications center for registered mothers. It aggregates automated alerts regarding upcoming antenatal clinical checkups, child immunization camp dates, nutrition kit pickup reminders from the Anganwadi teacher, and general public health advisories with exact date timestamps.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Notifications List: Alert message text (`message`), Broadcast date (`notification_date`), Alert type classification (Checkup, Vaccine, Kit, or General), and Unread indicator.
  - Category Filter Tabs: All Notifications, Clinical Checkups, Child Vaccines, Nutrition Kits.
- **Data Source:** `myapp_notification` and `myapp_kit_notification` linked to `USER=mother`.
- **Data Format Example (JSON):**
```json
[
  {
    "id": 42,
    "category": "Vaccination",
    "message": "Vaccination scheduled for child 'Aarav Nair': Measles-Rubella (MR) Dose 1 on March 25, 2026.",
    "date": "2026-03-15"
  },
  {
    "id": 41,
    "category": "Nutrition Kit",
    "message": "Nutrition Kit allocated: Amrutham Nutri-Mix Phase 2. Please collect it from your Anganwadi center on March 18, 2026.",
    "date": "2026-03-12"
  }
]
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/user_notifications/` (also `/myapp/notification/`)
- **HTTP Method:** `GET`
- **Request Details:** Authenticated GET request with mother session.
- **Response Details:** Returns compiled HTML (`user/notification.html`) with notifications list.
- **When API is Called:** On navigation to "Notifications" or clicking bell icon.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def user_notifications(request):
    mother, err_redirect = get_logged_in_mother(request)
    if err_redirect:
        return err_redirect
    general_notes = notification.objects.filter(USER=mother).order_by('-notification_date', '-id')
    kit_notes = kit_notification.objects.filter(USER=mother).order_by('-notification_date', '-id')
    
    # Merge and sort all alerts chronologically
    all_notes = list(general_notes)
    for kn in kit_notes:
        all_notes.append({
            'message': kn.notification_message,
            'notification_date': kn.notification_date,
            'is_kit': True
        })
    all_notes.sort(key=lambda x: x.notification_date if hasattr(x, 'notification_date') else x['notification_date'], reverse=True)
    return render(request, 'user/notification.html', {'notifications': all_notes, 'mother': mother})
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def user_notifications(request)`
- **Step-by-Step Processing:**
  1. Identifies logged-in mother.
  2. Queries `myapp_notification` (general clinical and vaccine alerts) and `myapp_kit_notification` (nutrition kit alerts).
  3. Merges both querysets into a single chronological message stream.
  4. Renders `user/notification.html`.
- **Database Interaction:** `SELECT * FROM myapp_notification WHERE USER_id = ...` and `SELECT * FROM myapp_kit_notification WHERE USER_id = ...`.

---

## 5. CODE FLOW
1. Mother clicks the bell icon or "Notifications" link in her portal.
2. Server queries all medical, vaccine, and food alerts linked to her profile.
3. Page displays alerts in chronological order with date stamps and icons.
4. Mother reads reminders for upcoming appointments and pickups.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **a digital Notification Inbox or SMS message tray on the mother's phone**. Whenever the nurse schedules a new checkup, the hospital schedules a baby vaccine, or the Anganwadi center packs a new food box, an alert message drops into this inbox so the mother never forgets an important health date.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Notification Inbox Header**| Displays page title, total notification count, and category tabs. | Header with message count and filter options. |
| **Notification Feed Stream** | Chronological list of alert cards with icon, message, and date stamp. | Main message feed of health alerts and reminders. |
| **Category Icons & Badges** | Visual icon indicators (Stethoscope for Checkup, Syringe for Vaccine, Apple for Kit). | Categorizes alerts with visual icons. |
| **Empty State Display** | Friendly illustration shown when no notifications are pending. | Informs mother when all notifications are up to date. |
"""

for fname, text in pages.items():
    with open(os.path.join(OUT_DIR, fname), "w", encoding="utf-8") as f:
        f.write(text.strip())
    print(f"Generated {fname}")

print("User / Mother pages generated successfully.")
