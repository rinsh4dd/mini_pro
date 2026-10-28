# Page Documentation: Unified Login Portal (`login.md`)

## 1. PAGE OVERVIEW
The **Unified Login Portal** is the central authentication gateway for all MaatriCare users. It supports multi-role access for Administrators, ASHA Field Health Workers, Anganwadi Teachers, and Beneficiary Mothers through a single interface. It handles credential verification, role-based redirection, verification checks for new mothers (ensuring only ASHA-verified mothers can log in), and contains a password recovery tab.

### 1.1 Default System Credentials Reference

| Role | Ward / Center | Name | Username | Password |
| :--- | :--- | :--- | :--- | :--- |
| **Administrator** | Central Administration | Administrative Officer | `admin` | `admin123` |
| **ASHA Worker** | Ward 01 - Main Community Center | Fatima Beevi | `asha01` | `asha01` |
| **ASHA Worker** | Ward 02 - East Sector | Kavitha Nair | `asha02` | `asha02` |
| **ASHA Worker** | Ward 03 - West Gram | Priya Nair | `asha03` | `asha03` |
| **ASHA Worker** | Ward 04 - North Colony | Rekha Menon | `asha04` | `asha04` |
| **ASHA Worker** | Ward 05 - South Extension | Mary Joseph | `asha05` | `asha05` |
| **Anganwadi Teacher** | Model Center 01 (Ward 01) | Anita Sharma | `teacher01` | `teacher01` |
| **Anganwadi Teacher** | Community Center 02 (Ward 02) | Lakshmi Menon | `teacher02` | `teacher02` |
| **Anganwadi Teacher** | West Gram Center 03 (Ward 03) | Sunitha Varghese | `teacher03` | `teacher03` |
| **Anganwadi Teacher** | North Colony Center 04 (Ward 04) | Radhika Pillai | `teacher04` | `teacher04` |
| **Anganwadi Teacher** | South Extension Center 05 (Ward 05) | Deepa Mohan | `teacher05` | `teacher05` |

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