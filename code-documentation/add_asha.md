# Page Documentation: Add ASHA Worker (`add_asha.md`)

## 1. PAGE OVERVIEW
The **Add ASHA Worker Page** provides an administrative registration form to onboard new ASHA community health workers. It captures personal information, nursing qualifications, contact numbers, profile photo, assigned Grama Panchayat ward, and sets up secure system login credentials.

---

## 2. DATA USED IN THIS PAGE
- **Data Collected (Form Submission):**
  - Personal & Contact: `full_name`, `age`, `dob`, `qualification`, `email`, `phone`, `address`, `joining_date`.
  - Administrative: `area_assigned` (Ward 01 to Ward 05), `image` (Profile photo file).
  - Login Credentials: `username`, `password`, `confirm_password`.
- **Data Displayed:**
  - Ward dropdown options and real-time input validation feedback.
- **Data Format Example (Form POST):**
```json
{
  "full_name": "Sunitha Kumari",
  "age": 32,
  "dob": "1994-08-10",
  "qualification": "B.Sc Nursing",
  "email": "sunitha.asha@gmail.com",
  "phone": 9846011223,
  "area_assigned": "Ward 03 - West Gram",
  "joining_date": "2026-03-01",
  "username": "sunitha_ward03",
  "password": "Password@123"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/add_asha/`
- **HTTP Method:** `GET` (render blank form), `POST` (process creation)
- **Request Details:** `multipart/form-data` containing text parameters and image binary.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/manage_asha/` with green success notification.
  - Validation Error: HTTP 200 Re-renders form with error alerts and preserved inputs.
- **When API is Called:** When administrator clicks the "Register ASHA Worker" button.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def add_asha(request):
    if request.method == "POST":
        # Validates username uniqueness, phone regex, email format, password match
        user = User.objects.create_user(username=username, password=password, email=email)
        asha_group, _ = Group.objects.get_or_create(name='ashaworker')
        user.groups.add(asha_group)
        
        fs = FileSystemStorage()
        img_filename = fs.save(img_file.name, img_file)
        
        asha_worker.objects.create(
            LOGIN=user,
            Full_name=full_name,
            Age=age,
            dob=dob,
            Qualification=qualification,
            Email=email,
            Address=address,
            image=img_filename,
            Area_assigned=area_assigned,
            Phone=phone,
            Joining_date=joining_date,
            Current_status='Active'
        )
        messages.success(request, f"ASHA Worker '{full_name}' registered successfully!")
        return redirect('/myapp/manage_asha/')
    return render(request, 'admin/add_asha.html')
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def add_asha(request)`
- **Step-by-Step Processing:**
  1. Validates all required fields and checks regex for phone (10 digits starting 6-9) and email.
  2. Ensures username does not already exist in `auth_user`.
  3. Creates `User` account, encrypts password, and attaches to `ashaworker` permission group.
  4. Saves uploaded profile photo to `media/` folder using `FileSystemStorage`.
  5. Inserts new record into `myapp_asha_worker` table linking `LOGIN=user`.
  6. Redirects administrator to `manage_asha` with confirmation message.
- **Database Interaction:** Executes SQL `INSERT INTO auth_user` and `INSERT INTO myapp_asha_worker`.

---

## 5. CODE FLOW
1. Admin navigates to `/myapp/add_asha/`.
2. Form renders with personal, contact, and ward assignment sections.
3. Admin completes form and uploads worker photo.
4. Admin submits form via POST.
5. Server validates data, saves photo file, and writes user and worker records to database.
6. Admin is redirected to ASHA Directory with a success alert banner.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
This page is like **an employment and onboarding desk for a new village health nurse**. When the health department hires an ASHA worker, the admin enters her name, qualifications, phone number, and assigns her a specific neighborhood (Ward). The system also creates an official username and password so she can log in from her own smartphone or tablet.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Form Header & Back Link** | Displays page title, instructions, and link back to worker directory. | Header providing context and return navigation. |
| **Login Credentials Card** | Input fields for system username, password, and confirmation. | Establishes account credentials for the worker. |
| **Personal Demographics Card** | Inputs for full name, age, date of birth, and qualifications. | Collects identity and educational background. |
| **Contact & Ward Allocation** | Inputs for phone number, email, address, and assigned ward dropdown. | Links worker to contact details and specific ward. |
| **Photo Upload & Joining Date** | File input for profile picture and date picker for start of service. | Captures official photo and date of appointment. |
| **Submission Actions** | Submit button and cancel button triggering form reset. | Dispatches data payload to backend endpoint. |