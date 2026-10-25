# Page Documentation: Registered Children Profiles (`user_child_profile.md`)

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