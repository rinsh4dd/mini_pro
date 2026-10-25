# Page Documentation: Nutrition Kit Allocation & History (`user_kit_history.md`)

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