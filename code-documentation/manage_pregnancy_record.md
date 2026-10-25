# Page Documentation: Maternal Antenatal Health Records (`manage_pregnancy_record.md`)

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