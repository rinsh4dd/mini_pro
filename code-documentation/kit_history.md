# Page Documentation: Kit Distribution History (`kit_history.md`)

## 1. PAGE OVERVIEW
The **Kit Distribution History Page** is the audit log of all supplementary nutrition kit handovers. It provides Anganwadi teachers with a filterable history of kits issued, collected, pending, or rescheduled. It allows teachers to mark pending kits as "Distributed", reschedule delivery dates if a mother was unable to visit, or cancel allocations.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Distribution Audit Table: Recipient mother name (`USER.name`), Mother contact phone (`USER.phone`), Kit product name (`product_name`), Kit category (`kit_type`), Quantity, Allocation Date (`date`), Scheduled Distribution Date (`distribution_date`), and Status badge ('Distributed', 'Pending', 'Rescheduled', 'Missed').
  - Filter Controls: Status filter dropdown ('All', 'Distributed', 'Pending', 'Rescheduled').
- **Data Format Example (JSON):**
```json
{
  "id": 24,
  "mother_name": "Ananya Nair",
  "phone": 9847123456,
  "product_name": "Maternal Care Kit Phase 2",
  "distribution_date": "2026-03-12",
  "status": "Distributed"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoints:**
  - View History: `/myapp/kit_history/` (`GET`)
  - Update Delivery Status: `/myapp/update_kit_status/<int:kit_id>/` (`POST` or `GET`)
  - Reschedule Pickup Date: `/myapp/reschedule_kit/` (`POST`)
- **HTTP Methods:** `GET`, `POST`
- **Request Details:** Form parameters or URL kit ID for status changes.
- **Response Details:** Returns updated HTML history table or redirects to `/myapp/kit_history/`.
- **When API is Called:** On page load or when clicking "Mark Collected" or submitting reschedule form.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def update_kit_status(request, kit_id):
    kit = get_object_or_404(nutrition_kit, id=kit_id)
    new_status = request.POST.get('status') or request.GET.get('status', 'Distributed')
    kit.status = new_status
    kit.save()
    messages.success(request, f"Kit #{kit.id} marked as '{new_status}'!")
    return redirect('/myapp/kit_history/')

def reschedule_kit(request):
    if request.method == "POST":
        kit = get_object_or_404(nutrition_kit, id=request.POST.get('kit_id'))
        kit.distribution_date = request.POST.get('new_date')
        kit.status = 'Rescheduled'
        kit.save()
        messages.success(request, f"Kit distribution rescheduled to {kit.distribution_date}!")
        return redirect('/myapp/kit_history/')
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def kit_history(request)`, `def update_kit_status()`, `def reschedule_kit()`
- **Step-by-Step Processing:**
  1. Queries all `myapp_nutrition_kit` entries linked to verified mothers (`USER__ASHA__isnull=False`) under current center.
  2. Applies search and status filters from `request.GET`.
  3. Handles status transitions ('Pending' -> 'Distributed' or 'Rescheduled').
  4. Renders `anganwadi_teacher/kit_history.html`.
- **Database Interaction:** `SELECT * FROM myapp_nutrition_kit JOIN myapp_user_table ...` and `UPDATE myapp_nutrition_kit SET status = ...`.

---

## 5. CODE FLOW
1. Teacher opens `/myapp/kit_history/`.
2. Page displays complete history of past kit allocations.
3. When a mother collects her kit, teacher clicks "Mark Distributed".
4. If a mother misses her date, teacher clicks "Reschedule" and enters a new date.
5. Server updates database record and refreshes the audit table.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like the **Official Delivery Receipt Book of the Anganwadi center**. When mothers come to collect their food packets, the teacher flips to this page and marks them as "Delivered". If a mother was sick and couldn't come on her scheduled day, the teacher can give her a new date next week so she doesn't miss her nutrition kit.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **History Log Header** | Shows page title, total count, and filter dropdowns. | Header controls for filtering delivery history. |
| **Audit Data Table** | Displays Mother, Kit Name, Quantity, Scheduled Date, and Status Badge. | Main historical record table of kit distributions. |
| **Status Update Controls** | Quick buttons to mark kit as "Distributed" or "Missed". | Changes delivery fulfillment status in database. |
| **Reschedule Modal Dialog** | Pop-up modal allowing teacher to set a new pickup date. | Reschedules missed collection appointments. |