# Page Documentation: Forgot Password (`forgot_password.md`)

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