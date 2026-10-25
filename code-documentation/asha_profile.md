# Page Documentation: ASHA Worker Profile (`asha_profile.md`)

## 1. PAGE OVERVIEW
The **ASHA Worker Profile Page** allows the logged-in field worker to inspect her official registration details, review her assigned Grama Panchayat ward, update personal contact numbers and residential address, refresh her profile photograph, and change her account password.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Official Profile: Full Name (`Full_name`), Ward Assignment (`Area_assigned`), Official Contact Phone (`Phone`), Email (`Email`), Qualification (`Qualification`), Service Joining Date (`Joining_date`), Profile Picture (`image`), and Username.
- **Data Collected (Form POST):**
  - Updated phone, email, address, new profile image file, and new password with confirmation.
- **Data Format Example (JSON):**
```json
{
  "full_name": "Kavitha Menon",
  "area_assigned": "Ward 01 - Main Community Center",
  "phone": 9876543210,
  "email": "kavitha.asha@gmail.com",
  "qualification": "GNM Nursing",
  "address": "House 12, Ward 01 Grama Colony"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/ashaworker_profile/`
- **HTTP Method:** `GET` (view profile), `POST` (save updates & password)
- **Request Details:** `multipart/form-data` containing contact fields and optional image binary.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/ashaworker_profile/` with success toast.
  - Failure: Re-renders form with error message.
- **When API is Called:** On loading profile page or submitting updates.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def ashaworker_profile_view(request):
    worker = get_current_asha_worker(request)
    if request.method == "POST":
        worker.Phone = request.POST.get('phone', worker.Phone)
        worker.Email = request.POST.get('email', worker.Email)
        worker.Address = request.POST.get('address', worker.Address)
        if 'image' in request.FILES:
            worker.image = FileSystemStorage().save(request.FILES['image'].name, request.FILES['image'])
        worker.save()
        
        # Handle password reset
        new_pw = request.POST.get('new_password')
        if new_pw and len(new_pw) >= 6:
            request.user.set_password(new_pw)
            request.user.save()
            messages.success(request, "Profile & password updated successfully! Please re-login.")
            return redirect('/myapp/login/')
        messages.success(request, "Profile details updated successfully!")
        return redirect('/myapp/ashaworker_profile/')
    return render(request, 'ashawoker/asha_profile.html', {'worker': worker})
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def ashaworker_profile_view(request)`
- **Step-by-Step Processing:**
  1. Resolves logged-in ASHA worker from `request.user`.
  2. Renders profile details on GET.
  3. On POST, updates contact phone, email, and address.
  4. Saves uploaded profile photo to `media/`.
  5. If password was changed, re-hashes password via `request.user.set_password()`.
  6. Commits updates to database.
- **Database Interaction:** Executes SQL `UPDATE myapp_asha_worker` and `UPDATE auth_user`.

---

## 5. CODE FLOW
1. ASHA worker clicks on profile photo or "My Profile" in sidebar.
2. Page displays official details, photo, and assigned ward.
3. Worker modifies contact number or password and clicks "Update Profile".
4. Server validates data and updates MySQL tables.
5. Confirmation alert appears on screen.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
This page is the **ASHA Health Worker's Official Identity and Account Settings**. It shows her photo, her assigned village area, and her phone number. If she buys a new SIM card or gets a new mobile number, she can update it here so that mothers and the hospital can always reach her.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Worker Identity Card** | Displays photo, full name, assigned ward, and active status badge. | Visual summary of worker credentials. |
| **Official Qualifications** | Read-only display of Qualifications, Joining Date, and Username. | Official service and employment records. |
| **Contact Edit Fields** | Form inputs for Mobile Phone, Email, and Residential Address. | Allows modifying personal contact info. |
| **Password Security Form** | Inputs for new password and password confirmation. | Updates portal login password. |
| **Update Commit Action** | Submit button executing profile changes. | Saves updates to database. |