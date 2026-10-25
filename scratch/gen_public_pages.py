# -*- coding: utf-8 -*-
import os

OUT_DIR = r"c:\Users\HP\PycharmProjects\maatricaree\code-documentation"

pages = {}

# 1. home.md
pages["home.md"] = """# Page Documentation: Home / Landing Page (`home.md`)

## 1. PAGE OVERVIEW
The **Home / Landing Page** is the public-facing gateway for the MaatriCare healthcare management system. Its primary purpose is to introduce the platform's mission—digitalizing maternal and child health tracking in local communities—to visitors, mothers, community health workers, and administrators. It showcases core system capabilities (maternal health monitoring, child immunization schedules, pediatric growth tracking, supplementary nutrition kit distribution) and provides quick navigation links to the authentication portal and mother registration.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Informational banners regarding maternal care and infant wellness.
  - Core service descriptions: Antenatal Checkups, Child Vaccination Tracker, Nutrition Kit Allocation, Growth Analytics.
  - Navigation links to Login, Register, and About sections.
- **Data Source:** Static presentation content defined within the HTML template (`templates/index.html`).
- **Data Format Example (Mock JSON Representation):**
```json
{
  "platform_name": "MaatriCare",
  "tagline": "Empowering Mothers, Nurturing Children",
  "modules": [
    {"name": "Maternal Health Tracker", "description": "Antenatal checkup schedules and clinical logging."},
    {"name": "Child Immunization", "description": "Complete vaccination calendar from birth to age 5."},
    {"name": "Nutrition Kit Distribution", "description": "Supplementary nutrition kits allocated via Anganwadi centers."}
  ]
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/` or `/myapp/home/`
- **HTTP Method:** `GET`
- **Request Details:**
  - Headers: Standard HTTP GET headers (`Accept: text/html`).
  - Parameters: None.
  - Body: None.
- **Response Details:** Returns complete compiled HTML page (`index.html`) with HTTP status 200.
- **When API is Called:** Automatically on initial site visit or when a user clicks the "Home" or "Brand Logo" button.
- **Exact Code Snippet from Project:**
```python
# maatricaree/urls.py
path('', myapp_views.home, name='root_home'),

# myapp/urls.py
path('home/', views.home, name='home'),

# myapp/views.py
def home(request):
    return render(request, 'index.html')
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def home(request)`
- **Step-by-Step Processing:**
  1. The Django web server receives an incoming HTTP GET request at `/` or `/myapp/home/`.
  2. The URL router maps the request to `views.home`.
  3. The view function renders the template `templates/index.html` without requiring database queries.
  4. The rendered HTML stream is returned to the client browser.
- **Database Interaction:** No direct database read/write is required for this static promotional view.
- **Backend Output:** Server-rendered HTML string with status code 200 OK.

---

## 5. CODE FLOW
1. Visitor types the website URL in their web browser or clicks a bookmark.
2. The browser initiates an HTTP `GET` request to `/`.
3. Django routing evaluates `maatricaree/urls.py` and delegates execution to `myapp/views.py:home()`.
4. `home()` calls Django's `render()` method targeting `templates/index.html`.
5. The template engine loads CSS stylesheets, FontAwesome icons, and Google Fonts.
6. The fully rendered HTML page is sent back to the browser.
7. The browser displays the landing page hero section, feature cards, and portal login buttons.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of the Home Page like the **front entrance and reception lobby of a modern maternal hospital**. When you walk through the front door, you see posters explaining what services the hospital offers—like checkups for pregnant mothers, vaccinations for newborn babies, and nutrition packets from the local Anganwadi center. You also see clear signboards pointing you to the **Registration Desk** (if you are a new mother) or the **Login Doors** (if you are already a registered mother, doctor, or health worker).

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Document Head & Meta Tags** | Configures page title, responsive viewport, and links CSS/fonts. | Sets up responsive styling and typography resources. |
| **Navigation Header** | Displays MaatriCare logo and links to Home, Features, Login, and Register. | Provides top navigation bar across all device sizes. |
| **Hero Section** | Welcomes visitors with headline, call-to-action buttons, and health imagery. | Captures visitor interest with platform mission and sign-up buttons. |
| **Feature Highlights** | Grid cards explaining Maternal Care, Child Immunization, and Nutrition Kits. | Explains the 4 main healthcare services offered by the platform. |
| **Portal Access Cards** | Quick access cards directing users to their respective role login pages. | Directs health workers, teachers, and mothers to portal authentication. |
| **Footer & Contact Info** | Displays helpline numbers, government support details, and copyright. | Concludes page with administrative and emergency contact information. |
"""

# 2. login.md
pages["login.md"] = """# Page Documentation: Unified Login Portal (`login.md`)

## 1. PAGE OVERVIEW
The **Unified Login Portal** is the central authentication gateway for all MaatriCare users. It supports multi-role access for Administrators, ASHA Field Health Workers, Anganwadi Teachers, and Beneficiary Mothers through a single interface. It handles credential verification, role-based redirection, verification checks for new mothers (ensuring only ASHA-verified mothers can log in), and contains a password recovery tab.

---

## 2. DATA USED IN THIS PAGE
- **Data Collected (User Input via Form):**
  - `username`: User account username (alphanumeric string or phone number).
  - `password`: Secret authentication password string.
- **Data Displayed:**
  - Form input fields with error/warning alerts (e.g., "Invalid username or password", "Verification Pending").
  - Password recovery tab inputs (`reset_username`, `new_password`, `confirm_password`).
- **Data Format Example (Form POST Body):**
```json
{
  "username": "asha_ward01",
  "password": "securepassword123",
  "csrfmiddlewaretoken": "a1b2c3d4..."
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoints:**
  - Display Page: `/myapp/login/` or `/login/` (`GET`)
  - Authenticate User: `/myapp/login_post/` (`POST`)
  - Quick Password Reset: `/myapp/change_password_post/` (`POST`)
- **HTTP Methods:** `GET` (render page), `POST` (process authentication)
- **Request Details:** Form-encoded payload sent via HTTP POST with CSRF token.
- **Response Details:**
  - Successful Auth: HTTP 302 Redirect to the user's role-specific dashboard.
  - Failed Auth / Verification Pending: HTTP 200 Re-render with warning messages.
- **When API is Called:** When the user clicks the "Sign In" or "Reset Password" submit buttons.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py - login_post snippet
@csrf_exempt # or CSRF token protected
def login_post(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.groups.filter(name="admin").exists() or user.is_staff:
                login(request, user)
                return redirect("/myapp/adminhome/")
            elif user.groups.filter(name="angteacher").exists():
                login(request, user)
                return redirect('/myapp/teacher_home/')
            elif user.groups.filter(name="ashaworker").exists():
                login(request, user)
                w = asha_worker.objects.filter(LOGIN=user).first()
                if w:
                    request.session['asha_id'] = w.id
                return redirect('/myapp/ashaworker_home/')
            elif user_table.objects.filter(LOGIN=user).exists():
                mother = user_table.objects.filter(LOGIN=user).first()
                if mother and mother.ASHA is None:
                    messages.warning(request, "Verification Pending: Your account registration is awaiting verification by your local ASHA Healthcare Worker.")
                    return render(request, 'login.html', {'prefill_username': username})
                login(request, user)
                return redirect('/myapp/userhome/')
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def logins(request)`, `def login_post(request)`
- **Step-by-Step Backend Execution:**
  1. Reads `username` and `password` from `request.POST`.
  2. Runs Django's `authenticate(request, username=username, password=password)`.
  3. If invalid, injects warning message and renders `login.html`.
  4. If valid, checks `user.groups` or model links:
     - Group `admin` -> Redirects to `/myapp/adminhome/`.
     - Group `angteacher` -> Redirects to `/myapp/teacher_home/`.
     - Group `ashaworker` -> Finds `asha_worker` entity, sets `session['asha_id'] = w.id`, redirects to `/myapp/ashaworker_home/`.
     - Group `user` / `user_table` -> Checks if `mother.ASHA is None`. If unverified, halts login with warning; if verified, redirects to `/myapp/userhome/`.
- **Database Interaction:**
  - Queries `auth_user` table to match username and verify hashed password.
  - Queries `auth_user_groups` to resolve user roles.
  - Queries `myapp_user_table` to check ASHA verification status.
  - Queries `myapp_asha_worker` to fetch ASHA worker record.

---

## 5. CODE FLOW
1. User navigates to `/myapp/login/`.
2. Browser renders the login form tabs: "Sign In" and "Forgot Password".
3. User enters credentials and clicks "Log In".
4. Form sends an HTTP `POST` to `/myapp/login_post/`.
5. Backend verifies credentials against database.
6. Role-checking logic inspects user groups and verification status.
7. Session cookie is issued, and browser is redirected to the appropriate dashboard.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
The Login Page works just like a **secure digital security gate at a community health center**. One single gatekeeper stands at the door. When you present your username and password, the gatekeeper checks who you are:
- If you are the **Chief Medical Officer (Admin)**, you are escorted to the Administration Office.
- If you are an **ASHA Health Worker**, you are escorted to the Field Health Desk.
- If you are an **Anganwadi Teacher**, you are escorted to the Nutrition Store.
- If you are a **Mother**, the gatekeeper first checks your card to see if your local ASHA worker has verified your home address. If yes, you enter your Maternal Care Room; if not, you are kindly asked to wait until your ASHA worker verifies you!

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Authentication Form Header** | Displays system branding, subtitle, and tab toggles (Login vs Reset). | Welcomes user and toggles between login and reset tabs. |
| **Django Flash Messages** | Displays alerts for invalid credentials, success notices, or pending verification. | Shows feedback and warning messages from the backend. |
| **Login Credentials Form** | Inputs for username and password with submission button. | Captures user identity and credentials for authentication. |
| **Password Recovery Tab** | Form fields for entering username and new password with confirmation. | Allows registered users to self-reset forgotten passwords. |
| **Tab Switching Script** | JavaScript snippet switching active tabs between Login and Password Reset. | Provides interactive tab navigation without page reload. |
"""

# 3. forgot_password.md
pages["forgot_password.md"] = """# Page Documentation: Forgot Password (`forgot_password.md`)

## 1. PAGE OVERVIEW
The **Forgot Password Page** provides a dedicated, standalone recovery mechanism for users who cannot access their account. It allows mothers, health workers, and teachers to reset their account password by verifying their registered username or email address and setting a new secure password.

---

## 2. DATA USED IN THIS PAGE
- **Data Collected (User Input):**
  - `username`: The account username or registered email address.
  - `new_password`: The desired new password (minimum 6 characters).
  - `confirm_password`: Repetition of the new password to prevent typos.
- **Data Displayed:**
  - Informational instructions on password strength.
  - Success/Error alerts.
- **Data Format Example (POST Payload):**
```json
{
  "username": "priya_sharma",
  "new_password": "NewSecretPassword2026",
  "confirm_password": "NewSecretPassword2026"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/forgot_password/` (or `/myapp/change_password_post/`)
- **HTTP Method:** `GET` (render page), `POST` (execute password change)
- **Request Details:** Form-encoded POST request containing username and passwords.
- **Response Details:**
  - Success: Redirects or renders login with success message: "Password changed successfully!".
  - Failure: Renders form with warning (e.g. "Password must be at least 6 characters in length").
- **When API is Called:** When user clicks "Update Password" button.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def change_password_post(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")
        if len(new_password) < 6:
            messages.warning(request, "Password must be at least 6 characters in length.")
            return render(request, 'login.html', {'active_tab': 'forgot'})
        if new_password != confirm_password:
            messages.warning(request, "New password and Confirm password do not match.")
            return render(request, 'login.html', {'active_tab': 'forgot'})
        user = User.objects.filter(username=username).first() or User.objects.filter(email=username).first()
        if user:
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password changed successfully! You can now log in.")
            return render(request, 'login.html', {'active_tab': 'login', 'prefill_username': user.username})
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def forgot_password(request)`, `def change_password_post(request)`
- **Step-by-Step Execution:**
  1. Validates input existence and checks that `new_password` has at least 6 characters.
  2. Confirms that `new_password == confirm_password`.
  3. Queries Django's `User` model using `username` or `email`.
  4. Calls `user.set_password(new_password)` which securely hashes the new password with salt.
  5. Commits `user.save()` to the database and redirects to the login screen.
- **Database Interaction:** Executes SQL `SELECT` on `auth_user`, followed by `UPDATE auth_user SET password = ... WHERE id = ...`.

---

## 5. CODE FLOW
1. User clicks "Forgot Password" on the login screen or navigates to `/myapp/forgot_password/`.
2. Page displays username and password input fields.
3. User enters account details and submits the form.
4. Backend verifies that the passwords match and user exists.
5. Password hash is updated in the database.
6. User is redirected back to the login page with a green success message.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **replacing a lost house key**. If you forget your old key (password), you come to this counter, tell the officer your registered name or email, and present a brand new key twice so they know it wasn't a mistake. The officer updates the lock in the official registry, and you can now open your door with the new key.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Card Header & Icon** | Displays lock reset graphic and explanatory text. | Informs user about password reset instructions. |
| **System Alert Messages** | Renders backend validation errors or success alerts. | Displays validation warnings or success confirmations. |
| **Reset Form Fields** | Inputs for registered username, new password, and confirmation. | Captures user identity and the new password. |
| **Submit Action Buttons** | Submit button to trigger password change and back-to-login link. | Executes password reset or cancels operation. |
| **Client Validation Script** | JavaScript checking that password fields match before submit. | Validates password matching before network request. |
"""

# 4. user_registration.md
pages["user_registration.md"] = """# Page Documentation: Beneficiary Mother Registration (`user_registration.md`)

## 1. PAGE OVERVIEW
The **Beneficiary Mother Registration Page** is the digital onboarding portal for pregnant women and nursing mothers. It collects maternal demographic, clinical, and residential information (including blood group, expected delivery date, and designated ward), registers their user account, and places their profile into the local ASHA worker's verification queue.

---

## 2. DATA USED IN THIS PAGE
- **Data Collected (User Input via Form):**
  - Personal: `name`, `husband_name`, `age`, `dob`, `blood_group`.
  - Contact & Address: `phone`, `Email`, `Address`, `panchayath`, `area` (Ward 01 - 05), `district`, `state`, `pincode`.
  - Clinical Milestone: `expected_delivery_date` (EDD).
  - Credentials: `username`, `password`, `confirm_password`.
- **Data Displayed:**
  - Dropdown options for designated Panchayath Areas (`PANCHAYATH_AREAS`).
  - Validation errors for duplicate usernames, invalid phone formats, or mismatched passwords.
- **Data Format Example (JSON Representation):**
```json
{
  "name": "Ananya Nair",
  "husband_name": "Rajesh Nair",
  "age": 26,
  "dob": "1999-04-15",
  "blood_group": "O+",
  "phone": 9847123456,
  "Email": "ananya.nair@example.com",
  "Address": "House No 42, River View",
  "panchayath": "Nedumbassery",
  "area": "Ward 02 - East Sector",
  "district": "Ernakulam",
  "state": "Kerala",
  "pincode": "683572",
  "expected_delivery_date": "2026-11-20"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/user_registartion/`
- **HTTP Method:** `GET` (render registration form), `POST` (process registration)
- **Request Details:** Form-data payload containing all demographic and credential fields.
- **Response Details:**
  - Success: Renders registration page with `success=True` modal/banner prompting mother to await ASHA approval.
  - Validation Failure: Re-renders form with field error messages and preserved input values.
- **When API is Called:** When the mother clicks "Submit Registration".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def user_registartion(request):
    if request.method == "POST":
        # Extracts fields: username, password, name, phone, area, edd...
        # Validates regex for phone, email, pincode, password match
        user = User.objects.create_user(username=username, password=password, email=email)
        user_group, _ = Group.objects.get_or_create(name='user')
        user.groups.add(user_group)
        
        user_table.objects.create(
            LOGIN=user,
            ASHA=None,  # Crucial: Unverified state awaiting assigned ward ASHA worker
            name=name,
            husband_name=husband_name,
            age=age,
            dob=dob,
            blood_group=blood_group,
            phone=phone,
            Email=email,
            Address=address,
            panchayath=panchayath,
            area=area,
            district=district,
            state=state,
            pincode=pincode,
            expected_delivery_date=edd
        )
        return render(request, 'user/user_registartion.html', {'success': True, 'panchayath_areas': PANCHAYATH_AREAS})
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def user_registartion(request)`
- **Step-by-Step Processing:**
  1. Validates that username is unique in `auth_user`.
  2. Verifies phone format (10-digit Indian mobile `PHONE_REGEX`), email regex, and 6-digit pincode regex.
  3. Verifies that `password == confirm_password` and length >= 6.
  4. Parses `expected_delivery_date` and validates date order against `dob`.
  5. Creates a new `User` record in `auth_user` and assigns it to group `user`.
  6. Inserts a new record into `myapp_user_table` with `ASHA=None`.
  7. Passes `success=True` back to the template to alert the user that registration succeeded and verification is pending.
- **Database Interaction:**
  - `User.objects.create_user()` -> `INSERT INTO auth_user`.
  - `user_table.objects.create()` -> `INSERT INTO myapp_user_table`.

---

## 5. CODE FLOW
1. Expectant mother opens `/myapp/user_registartion/`.
2. Browser displays the comprehensive registration form with ward selections.
3. Mother fills in personal details, blood group, pregnancy due date, and desired password.
4. Mother clicks "Register".
5. Browser sends HTTP `POST` to `/myapp/user_registartion/`.
6. Server validates all fields, checks uniqueness, and saves user profile with `ASHA=None`.
7. Browser renders success screen informing the mother that her assigned ward ASHA worker will verify her profile.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **filling out an enrollment card at your local village maternal clinic**. When a mother becomes pregnant, she fills out her name, home address, ward number, blood group, and baby due date. When she submits it, the clinic creates a new health folder for her. However, before she can use all online services, her local neighborhood health sister (the ASHA worker) must visit or review her details to confirm her address.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Registration Header** | Displays title, step indicators, and link to login. | Welcomes mothers and explains registration steps. |
| **Account Credentials Block** | Inputs for username, email, password, and confirmation. | Sets up secure login credentials. |
| **Personal Demographics** | Inputs for mother's full name, husband's name, age, DOB, blood group. | Captures mother's identity and physiological data. |
| **Residential Address & Ward** | Inputs for address, panchayath, ward dropdown, district, pincode. | Assigns mother to her specific geographic health ward. |
| **Pregnancy Details Block** | Date picker for Expected Delivery Date (EDD). | Records pregnancy timeline to track gestation weeks. |
| **Form Action & Disclaimer** | Submission button and notice explaining ASHA verification policy. | Submits registration and explains approval process. |
| **Client Validation Scripts** | JavaScript checking phone digits, password match, and date limits. | Prevents malformed submissions before sending to server. |
"""

for fname, text in pages.items():
    with open(os.path.join(OUT_DIR, fname), "w", encoding="utf-8") as f:
        f.write(text.strip())
    print(f"Generated {fname}")

print("Public pages generated successfully.")
