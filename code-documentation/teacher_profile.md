# Page Documentation: Anganwadi Teacher Profile (`teacher_profile.md`)

## 1. PAGE OVERVIEW
The **Anganwadi Teacher Profile Page** allows the logged-in Anganwadi teacher to review her official center credentials, inspect assigned ward information, update her personal contact phone and address, upload a refreshed profile photograph, and update her account password.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Teacher Credentials: Name (`Name`), Center Name (`center_name`), Educational Qualifications (`Qualification`), Joining Date (`joining_date`), Contact Phone (`Phone`), Email (`Email`), Residential Address (`Address`), Profile Image (`image`), and Account Username.
- **Data Collected (Form POST):**
  - Updated phone, email, address, new profile photo file, and new password with confirmation.
- **Data Format Example (JSON):**
```json
{
  "name": "Radhika Suresh",
  "center_name": "Anganwadi Center 02 - East Sector",
  "phone": 9447123987,
  "email": "radhika.ang@gmail.com",
  "address": "45 Temple Road, Ward 02",
  "qualification": "Early Childhood Education"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/teacher_profile/`
- **HTTP Method:** `GET` (view profile), `POST` (update profile & password)
- **Request Details:** `multipart/form-data` containing contact fields and optional image file.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/teacher_profile/` with success message.
  - Failure: Re-renders profile with error alert.
- **When API is Called:** On loading profile page or clicking "Update Profile".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def teacher_profile_view(request):
    teacher = get_current_anganwadi_teacher(request)
    if request.method == "POST":
        teacher.Phone = request.POST.get('phone', teacher.Phone)
        teacher.Email = request.POST.get('email', teacher.Email)
        teacher.Address = request.POST.get('address', teacher.Address)
        if 'image' in request.FILES:
            teacher.image = FileSystemStorage().save(request.FILES['image'].name, request.FILES['image'])
        teacher.save()
        
        # Optional password update
        new_pw = request.POST.get('new_password')
        if new_pw and len(new_pw) >= 6:
            request.user.set_password(new_pw)
            request.user.save()
            messages.success(request, "Profile and password updated successfully! Please re-login.")
            return redirect('/myapp/login/')
        messages.success(request, "Profile updated successfully!")
        return redirect('/myapp/teacher_profile/')
    return render(request, 'anganwadi_teacher/teacher_profile.html', {'teacher': teacher})
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def teacher_profile_view(request)`
- **Step-by-Step Processing:**
  1. Resolves logged-in teacher using `request.user`.
  2. Renders profile cards on GET.
  3. Validates submitted contact details and image on POST.
  4. Commits changes to `myapp_anganwadi_teacher` and `auth_user`.
  5. Redirects with success notification.
- **Database Interaction:** Executes SQL `UPDATE myapp_anganwadi_teacher` and `UPDATE auth_user`.

---

## 5. CODE FLOW
1. Teacher clicks on profile avatar or "My Profile" in navigation.
2. Page displays current personal and center details.
3. Teacher modifies phone number or uploads a new photo.
4. Teacher clicks "Save Changes".
5. Backend updates database and reloads profile with success notice.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
This page is the **Teacher's Personal Identity & Settings Card**. Just like an employee ID card, it shows the teacher's photo, which Anganwadi center she works at, her phone number, and address. She can come here anytime to update her phone number or change her password.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Profile Card & Photo** | Displays teacher photo, center badge, and account status. | Visual profile banner and center assignment. |
| **Official Center Credentials**| Read-only display of Center Name, Joining Date, and Qualifications. | Shows official appointment details. |
| **Editable Contact Form** | Form inputs for Phone Number, Email, and Address. | Allows teacher to update contact details. |
| **Security & Password Update** | Inputs for new password and password confirmation. | Allows changing portal login password. |
| **Submit Action Button** | Button committing updates to database. | Triggers profile update transaction. |