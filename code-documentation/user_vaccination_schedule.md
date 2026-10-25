# Page Documentation: Child Immunization Card (`user_vaccination_schedule.md`)

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