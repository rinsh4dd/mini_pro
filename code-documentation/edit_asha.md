# Page Documentation: Edit ASHA Worker (`edit_asha.md`)

## 1. PAGE OVERVIEW
The **Edit ASHA Worker Page** allows administrators to update existing ASHA health worker profiles. It supports updating phone numbers, email addresses, educational qualifications, operational status (Active/Inactive), profile photographs, and reassigning workers to different Panchayat wards.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed (Prefilled Form):**
  - Current values from `myapp_asha_worker`: `Full_name`, `Age`, `dob`, `Qualification`, `Email`, `Phone`, `Address`, `Area_assigned`, `Current_status`, and current profile image preview.
- **Data Collected (Form POST):**
  - Updated contact details, status selection ('Active' / 'Inactive'), new assigned ward, and optional replacement profile photo.
- **Data Format Example (Form POST Body):**
```json
{
  "full_name": "Kavitha Menon",
  "phone": 9876543210,
  "area_assigned": "Ward 02 - East Sector",
  "current_status": "Active",
  "qualification": "GNM Nursing / Certified Midwife"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/edit_asha/<int:id>/`
- **HTTP Method:** `GET` (fetch and display current worker data), `POST` (save updates)
- **Request Details:** URL parameter `<int:id>` identifies the target worker.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/manage_asha/` with updated confirmation.
  - Validation Failure: Re-renders form displaying field validation errors.
- **When API is Called:** When administrator clicks "Edit" button in ASHA directory and submits changes.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def edit_asha(request, id):
    asha = get_object_or_404(asha_worker, id=id)
    if request.method == "POST":
        # Extracts updated phone, email, qualification, area, status
        asha.Full_name = request.POST.get('full_name')
        asha.Phone = request.POST.get('phone')
        asha.Area_assigned = request.POST.get('area_assigned')
        asha.Current_status = request.POST.get('current_status')
        if 'image' in request.FILES:
            asha.image = FileSystemStorage().save(request.FILES['image'].name, request.FILES['image'])
        asha.save()
        messages.success(request, f"ASHA Worker '{asha.Full_name}' profile updated successfully!")
        return redirect('/myapp/manage_asha/')
    return render(request, 'admin/edit_asha.html', {'asha': asha})
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def edit_asha(request, id)`
- **Step-by-Step Processing:**
  1. Retrieves target `asha_worker` instance using `id` or returns 404.
  2. On GET: Passes existing model record to template to prefill all form fields.
  3. On POST: Validates updated fields (phone length, email regex).
  4. If a new photo file is provided, stores it in `media/` and updates image path.
  5. Updates linked `auth_user` email if changed.
  6. Commits updates to database using `asha.save()`.
- **Database Interaction:** `UPDATE myapp_asha_worker SET ... WHERE id = ...`.

---

## 5. CODE FLOW
1. Admin clicks "Edit" icon next to a worker row on `/myapp/manage_asha/`.
2. Browser issues GET request to `/myapp/edit_asha/<id>/`.
3. Backend fetches worker details from MySQL and renders pre-filled form.
4. Admin modifies details (e.g. changes ward or updates phone number) and clicks "Save Changes".
5. Backend updates database and redirects to the ASHA directory.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **updating an employee's personnel file**. If an ASHA worker gets transferred to a neighboring village ward, gets a new mobile phone number, or takes medical leave, the administrator uses this page to modify her file so the system always has her most up-to-date details.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Profile Summary Banner** | Displays worker's photo thumbnail, name, ID, and current status badge. | Quick visual identity check of worker being edited. |
| **Personal Information Fields** | Pre-populated inputs for Full Name, Age, and Date of Birth. | Allows editing personal demographic details. |
| **Contact & Address Block** | Inputs for Phone Number, Email, and Postal Address. | Modifies contact and physical location records. |
| **Ward Assignment & Status** | Dropdowns to reallocate ward area and toggle Active/Inactive state. | Adjusts geographic responsibility and operational status. |
| **Photo Replacement Field** | File input allowing upload of a newer profile photograph. | Optional upload to refresh employee photograph. |
| **Save / Cancel Actions** | Submit button executing update transaction and cancel button. | Commits modifications to the database or aborts. |