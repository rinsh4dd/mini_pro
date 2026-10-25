# Page Documentation: Edit Anganwadi Teacher (`edit_anganwadi.md`)

## 1. PAGE OVERVIEW
The **Edit Anganwadi Teacher Page** enables administrators to modify existing Anganwadi teacher profiles. It allows updating contact numbers, qualifications, center assignments, operational status (Active/Inactive), and profile photos.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed (Prefilled Form):**
  - Pre-populated fields from `myapp_anganwadi_teacher`: `Name`, `Age`, `dob`, `Gender`, `Phone`, `Email`, `Address`, `Qualification`, `center_name`, `Current_status`, and current photo preview.
- **Data Collected (Form Submission):**
  - Updated contact information, reassigned center name, status dropdown, and optional new profile image.
- **Data Format Example (Form POST):**
```json
{
  "name": "Radhika Suresh",
  "phone": 9447123987,
  "center_name": "Anganwadi Center 02 - East Sector",
  "current_status": "Active",
  "qualification": "Diploma in Nutrition & Early Child Care"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/edit_anganwadi/<int:id>/`
- **HTTP Method:** `GET` (fetch and render existing details), `POST` (save updates)
- **Request Details:** URL integer parameter `<int:id>` identifies the teacher record.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/manage_anganwadi/` with green success notification.
  - Validation Failure: Re-renders form with error alert banner.
- **When API is Called:** When admin clicks "Edit" in the Anganwadi directory and submits modifications.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def edit_anganwadi(request, id):
    teacher = get_object_or_404(anganwadi_teacher, id=id)
    if request.method == "POST":
        teacher.Name = request.POST.get('name')
        teacher.Phone = request.POST.get('phone')
        teacher.center_name = request.POST.get('center_name')
        teacher.Current_status = request.POST.get('current_status')
        if 'image' in request.FILES:
            teacher.image = FileSystemStorage().save(request.FILES['image'].name, request.FILES['image'])
        teacher.save()
        messages.success(request, f"Anganwadi Teacher '{teacher.Name}' updated successfully!")
        return redirect('/myapp/manage_anganwadi/')
    return render(request, 'admin/edit_anganwadi.html', {'teacher': teacher})
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def edit_anganwadi(request, id)`
- **Step-by-Step Processing:**
  1. Finds `anganwadi_teacher` instance by primary key `id`.
  2. Renders prefilled HTML form on GET.
  3. Validates submitted form fields on POST.
  4. Saves replacement image file if uploaded.
  5. Commits changes to MySQL database via `teacher.save()`.
  6. Redirects administrator to `/myapp/manage_anganwadi/`.
- **Database Interaction:** Executes SQL `UPDATE myapp_anganwadi_teacher SET ... WHERE id = ...`.

---

## 5. CODE FLOW
1. Admin clicks "Edit" button next to a teacher in the directory.
2. Server loads existing record and displays prefilled edit form.
3. Admin edits center name or phone number and clicks "Save Changes".
4. Server validates modifications and updates database record.
5. Browser redirects back to Anganwadi directory with success message.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
This page is like **updating the center assignment or contact details of an Anganwadi teacher**. If a teacher transfers to another village center or changes her phone number, the administrator opens this page to make sure her contact info and center name stay accurate.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Profile Card Header** | Displays current teacher name, thumbnail photo, and center name. | Visual confirmation of teacher account being modified. |
| **Personal Demographics** | Inputs for Name, Age, and Date of Birth. | Updates personal identifying details. |
| **Contact & Center Info** | Inputs for Mobile Phone, Email, Center Name dropdown, and Address. | Updates contact information and center allocation. |
| **Status & Qualifications** | Dropdown for Active/Inactive status and text input for qualifications. | Modifies operational status and qualifications. |
| **Photo Upload Widget** | Allows uploading a new image to replace current profile photo. | Updates teacher profile photo. |
| **Form Action Buttons** | "Save Changes" submit button and "Cancel" link. | Submits modifications or cancels operation. |