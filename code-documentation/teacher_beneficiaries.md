# Page Documentation: Center Beneficiaries Directory (`teacher_beneficiaries.md`)

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