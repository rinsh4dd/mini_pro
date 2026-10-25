# Page Documentation: Mother Profile & Demographics (`user_profile.md`)

## 1. PAGE OVERVIEW
The **Mother Profile Page** provides beneficiary mothers with complete visibility over their registered personal, residential, and medical profile details. It displays their registered blood group, spouse's name, assigned Grama Panchayat ward, assigned ASHA worker, and allows mothers to update their contact telephone number, postal address, and login password.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Personal Demographics: Full Name (`name`), Husband's Name (`husband_name`), Age (`age`), Date of Birth (`dob`), Blood Group (`blood_group`).
  - Residential & Geographic: Address (`Address`), Panchayath (`panchayath`), Ward (`area`), District (`district`), State (`state`), Pincode (`pincode`).
  - Maternal Details: Expected Delivery Date (`expected_delivery_date`), Registration Date (`registration_date`).
  - Healthcare Association: Assigned ASHA Worker Name (`ASHA.Full_name`), Worker Contact Phone (`ASHA.Phone`).
- **Data Collected (Edit Form POST):**
  - Updated phone, address, and new password with confirmation.
- **Data Format Example (JSON):**
```json
{
  "name": "Ananya Nair",
  "husband_name": "Rajesh Nair",
  "age": 26,
  "blood_group": "O+",
  "phone": 9847123456,
  "panchayath": "Nedumbassery",
  "area": "Ward 02 - East Sector",
  "pincode": "683572",
  "asha_worker": "Kavitha Menon (Ph: 9876543210)"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoints:**
  - View Profile: `/myapp/user_profile/` or `/myapp/view_profile/` (`GET`)
  - Edit Profile: `/myapp/edit_user_profile/` (`POST`)
- **HTTP Methods:** `GET`, `POST`
- **Request Details:** Form-encoded POST payload containing updated phone, address, and passwords.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/view_profile/` with green confirmation notice.
  - Failure: Re-renders profile with error alert.
- **When API is Called:** On loading profile page or clicking "Save Changes".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def user_profile_view(request):
    mother, err_redirect = get_logged_in_mother(request)
    if err_redirect:
        return err_redirect
    return render(request, 'user/view_profile.html', {'mother': mother})

def edit_user_profile(request):
    mother, err_redirect = get_logged_in_mother(request)
    if err_redirect:
        return err_redirect
    if request.method == "POST":
        mother.phone = request.POST.get('phone', mother.phone)
        mother.Address = request.POST.get('address', mother.Address)
        mother.save()
        
        new_pw = request.POST.get('new_password')
        if new_pw and len(new_pw) >= 6:
            request.user.set_password(new_pw)
            request.user.save()
            messages.success(request, "Profile and password updated successfully! Please re-login.")
            return redirect('/myapp/login/')
        messages.success(request, "Profile information updated successfully!")
        return redirect('/myapp/view_profile/')
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def user_profile_view()`, `def edit_user_profile()`
- **Step-by-Step Processing:**
  1. Identifies logged-in mother via `get_logged_in_mother()`.
  2. Queries `myapp_user_table` linked to current `request.user`.
  3. Renders pre-filled profile view on GET.
  4. On POST, updates phone and address fields in `myapp_user_table`.
  5. If password was provided, re-encrypts password in `auth_user`.
  6. Commits changes to database.
- **Database Interaction:** `SELECT * FROM myapp_user_table WHERE LOGIN_id = ...` and `UPDATE myapp_user_table SET ...`.

---

## 5. CODE FLOW
1. Mother clicks "Profile" on the top navigation.
2. Server loads her personal and health records from MySQL.
3. Page displays her information cards and assigned ASHA contact.
4. Mother updates her contact phone or password and clicks Save.
5. Server writes changes to the database and reloads with success notice.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
This page is the **Mother's Official Health Identity Card**. It shows her name, blood group, home address, and the name and phone number of her assigned village health sister. If she changes her phone number or wants to create a new password, she can do it here.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Profile Identity Card** | Displays mother name, blood group badge, and due date. | Visual header highlighting patient identity. |
| **Personal Demographics Block**| Shows Husband's Name, Age, DOB, and Registration Date. | Core personal and demographic records. |
| **Address & Ward Block** | Displays postal address, panchayath, ward, and district. | Geographic and residential records. |
| **Assigned ASHA Worker Card** | Displays the dedicated ASHA worker's name and contact number. | Dedicated field healthcare worker connection. |
| **Edit Profile Modal / Form** | Form fields to update phone, address, and account password. | Allows mother to update contact details. |