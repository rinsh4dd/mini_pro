# Page Documentation: Beneficiary Mother Registration (`user_registration.md`)

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