# Page Documentation: Beneficiary Mother Dashboard (`user_home.md`)

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