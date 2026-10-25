# Page Documentation: Newborn Infant Birth Registration (`register_newborn.md`)

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