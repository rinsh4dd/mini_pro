# Page Documentation: Antenatal Pregnancy Health Timeline (`user_pregnancy_record.md`)

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