# Page Documentation: Schedule Child Vaccination (`schedule_vaccination.md`)

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