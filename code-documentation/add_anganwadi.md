# Page Documentation: Add Anganwadi Teacher (`add_anganwadi.md`)

## 1. PAGE OVERVIEW
The **Add Anganwadi Teacher Page** allows administrators to register a new Anganwadi teacher and link them to a specific child development center. It collects their personal information, educational qualifications, contact numbers, center name, and automatically creates their system user account.

---

## 2. DATA USED IN THIS PAGE
- **Data Collected (Form Submission):**
  - Personal: `name`, `age`, `dob`, `gender` ('Female', 'Male'), `qualification`, `image`.
  - Center & Contact: `center_name` (e.g., Anganwadi Center 01), `phone`, `email`, `address`, `joining_date`.
  - Credentials: `username`, `password`, `confirm_password`.
- **Data Displayed:**
  - Center selection dropdown and form validation instructions.
- **Data Format Example (Form POST):**
```json
{
  "name": "Lakshmi Narayanan",
  "age": 29,
  "gender": "Female",
  "qualification": "Pre-Primary Teaching Diploma",
  "center_name": "Anganwadi Center 04 - North Colony",
  "phone": 9847556677,
  "email": "lakshmi.ang@gmail.com",
  "username": "lakshmi_ang04",
  "password": "Password@2026"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/add_anganwadi/`
- **HTTP Method:** `GET` (render blank registration form), `POST` (process creation)
- **Request Details:** `multipart/form-data` with form fields and optional profile picture.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/manage_anganwadi/` with success toast alert.
  - Validation Failure: Re-renders form with error alerts.
- **When API is Called:** When admin clicks "Register Anganwadi Teacher".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def add_anganwadi(request):
    if request.method == "POST":
        # Validates fields, checks username uniqueness, phone & email formats
        user = User.objects.create_user(username=username, password=password, email=email)
        ang_group, _ = Group.objects.get_or_create(name='angteacher')
        user.groups.add(ang_group)
        
        anganwadi_teacher.objects.create(
            LOGIN=user,
            Name=name,
            Age=age,
            dob=dob,
            Gender=gender,
            Phone=phone,
            Email=email,
            Address=address,
            image=img_filename,
            Qualification=qualification,
            center_name=center_name,
            joining_date=joining_date,
            Current_status='Active'
        )
        messages.success(request, f"Anganwadi Teacher '{name}' registered successfully!")
        return redirect('/myapp/manage_anganwadi/')
    return render(request, 'admin/add_anganwadi.html')
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def add_anganwadi(request)`
- **Step-by-Step Processing:**
  1. Validates inputs, ensuring phone is 10 digits and username is unique.
  2. Creates new `User` record in `auth_user` and assigns group `angteacher`.
  3. Uploads profile image file to `media/` folder.
  4. Inserts `anganwadi_teacher` record into MySQL linking to created `User`.
  5. Redirects to `/myapp/manage_anganwadi/` with success notification.
- **Database Interaction:** Executes SQL `INSERT` into `auth_user` and `myapp_anganwadi_teacher`.

---

## 5. CODE FLOW
1. Admin opens `/myapp/add_anganwadi/`.
2. Form loads with fields for teacher demographics, center name, and login credentials.
3. Admin inputs teacher details and clicks "Submit".
4. Server validates data and creates user account with `angteacher` role.
5. Server saves Anganwadi teacher profile in database.
6. Browser redirects back to Anganwadi Teacher Directory.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
This page is the **Official Appointment Desk for a new Anganwadi Center Teacher**. When the government assigns a teacher to manage a local village day-care and nutrition center, the admin uses this form to register her name, assign her center, and give her a login account so she can order and distribute baby food packets.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Form Banner** | Displays title and navigation link back to directory. | Top navigation and header. |
| **Login Setup Section** | Username, password, and confirmation inputs for teacher portal access. | Establishes portal login credentials. |
| **Personal Demographics** | Name, age, DOB, gender, and educational qualifications. | Records personal and professional details. |
| **Center Assignment Section**| Center name / ward dropdown, contact phone, email, and address. | Assigns teacher to specific Anganwadi center. |
| **Photo Upload & Dates** | File picker for profile picture and joining date selector. | Attaches profile photo and official start date. |
| **Submit Action Buttons** | Submit registration button and cancel link. | Initiates backend account creation. |