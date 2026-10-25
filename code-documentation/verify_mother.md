# Page Documentation: Beneficiary Mother Verification (`verify_mother.md`)

## 1. PAGE OVERVIEW
The **Beneficiary Mother Verification Page** is the clinical onboarding queue for ASHA health workers. In MaatriCare, newly registered mothers cannot access internal health portal features until their identity, residential address, and pregnancy status are verified by their assigned ward ASHA worker. This page allows the worker to inspect registration details, approve/verify the mother (linking her account to the worker), or reject/delete fraudulent entries.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Pending Verification Roster: Mothers residing in the worker's ward with `ASHA_id IS NULL`. Displays full name, husband's name, age, phone number, address, blood group, EDD, and registration timestamp.
  - Verified Mothers Roster: Previously approved mothers in this ward with action to unverify or review.
  - Active ASHA Workers Dropdown: Enables delegating or assigning mother to a colleague in the same ward.
- **Data Collected (Action POST):**
  - `mother_id`: ID of target mother.
  - `action_type`: 'verify_mother', 'unverify_mother', or 'delete_mother'.
  - `asha_id`: ID of the assigned ASHA worker.
- **Data Format Example (JSON):**
```json
{
  "mother_id": 19,
  "name": "Deepa Thomas",
  "husband_name": "Thomas Mathew",
  "phone": 9847112244,
  "area": "Ward 01 - Main Community Center",
  "blood_group": "B+",
  "expected_delivery_date": "2026-10-05",
  "status": "Pending Verification"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoints:**
  - Verification Queue View: `/myapp/verify_mother/` (`GET`)
  - Verification Action: `/myapp/verify_mother/` (`POST`) or `/myapp/verify_mother_action/<int:id>/<str:action>/`
  - Remove Invalid Mother: `/myapp/delete_mother/<int:id>/` (`POST` or `GET`)
- **HTTP Methods:** `GET`, `POST`
- **Request Details:** Form-encoded POST body with `mother_id` and `action_type=verify_mother`.
- **Response Details:** Redirects to `/myapp/verify_mother/` with green success notification.
- **When API is Called:** When ASHA worker clicks "Verify & Assign" or "Reject".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def verify_mother(request):
    worker = get_current_asha_worker(request)
    area_q = get_area_filter_q(worker.Area_assigned) if worker else Q()
    base_area_mothers = user_table.objects.filter(area_q)
    
    if request.method == "POST":
        action_type = request.POST.get("action_type")
        if action_type == "verify_mother":
            mother = get_object_or_404(base_area_mothers, id=request.POST.get("mother_id"))
            mother.ASHA = worker  # Links mother to ASHA worker, unlocking her portal
            mother.save()
            messages.success(request, f"Mother '{mother.name}' has been verified and assigned to you!")
            return redirect('/myapp/verify_mother/')
    
    pending_mothers = base_area_mothers.filter(ASHA__isnull=True).order_by('-id')
    verified_mothers = base_area_mothers.filter(ASHA__isnull=False).order_by('-id')
    return render(request, 'ashawoker/verify_mother.html', {
        'pending_mothers': pending_mothers,
        'verified_mothers': verified_mothers,
        'worker': worker
    })
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def verify_mother()`, `def verify_mother_action()`, `def delete_mother()`
- **Step-by-Step Processing:**
  1. Resolves logged-in ASHA worker and identifies their assigned ward.
  2. Queries `myapp_user_table` splitting into `pending_mothers` (`ASHA__isnull=True`) and `verified_mothers` (`ASHA__isnull=False`).
  3. On POST `verify_mother`: Sets `mother.ASHA = worker` and saves to MySQL. This state change immediately unlocks the mother's account to log in and access maternal services.
  4. On POST `delete_mother`: Deletes `user_table` record and linked `auth_user` credentials.
- **Database Interaction:** `UPDATE myapp_user_table SET ASHA_id = ... WHERE id = ...`.

---

## 5. CODE FLOW
1. Mother registers online; her account is marked as unverified (`ASHA=None`).
2. ASHA worker opens `/myapp/verify_mother/` on her phone or tablet.
3. Pending list shows mother's name, phone, and home address.
4. ASHA worker visits mother or calls her to verify pregnancy details.
5. Worker clicks "Verify & Approve" button.
6. Server assigns `mother.ASHA = worker`.
7. Mother can now log in to the portal and view her health profile.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **a physical home inspection and identity check by a village nurse**. When a pregnant woman signs up on the app, her account is locked until the nurse in her neighborhood checks her details, confirms she lives in that village, and presses the "Verify" button. Once verified, the mother is officially under that nurse's care!

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Verification Queue Header** | Displays count of pending verifications and ward area. | Header displaying queue volume and location. |
| **Pending Mothers Cards** | Information cards showing new mothers awaiting approval. | Displays applicant identity, phone, and due date. |
| **Verification Action Buttons**| "Verify & Assign" button and "Reject / Delete" button. | Commits verification approval or rejects entry. |
| **Verified Beneficiaries Table**| List of currently verified mothers under this worker's supervision. | Roster of active verified mothers in this ward. |
| **Unverify / Reassign Action** | Allows transferring a mother to another worker or resetting status. | Administrative controls to reallocate patients. |