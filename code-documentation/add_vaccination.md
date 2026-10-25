# Page Documentation: Add Vaccination to Catalog (`add_vaccination.md`)

## 1. PAGE OVERVIEW
The **Add Vaccination Page** is the administrative master catalog manager for childhood immunizations. It allows healthcare administrators to configure standardized vaccines according to national immunization guidelines (such as BCG, OPV, Pentavalent, Rotavirus, Measles-Rubella), set target age milestones in months (from birth to 5 years), and define mandatory clinical descriptions.

---

## 2. DATA USED IN THIS PAGE
- **Data Collected (Form Submission):**
  - `vaccine_code`: Short standardized medical code (e.g., "BCG", "OPV-0", "ROTA-1", "MR-1").
  - `vaccine_name`: Official vaccine name (e.g., "Bacillus Calmette–Guérin", "Oral Polio Vaccine").
  - `vaccine_type`: Category ('Mandatory', 'Recommended', 'Optional').
  - `target_month`: Target child age in months (0 = At Birth, 1.5, 2.5, 3.5, 9, 16-24, 60).
  - `description`: Clinical indications, diseases prevented, and dosage instructions.
- **Data Displayed:**
  - Catalog list of existing master vaccines already configured in the system.
- **Data Format Example (JSON):**
```json
{
  "vaccine_code": "PENTA-1",
  "vaccine_name": "Pentavalent Vaccine Dose 1",
  "vaccine_type": "Mandatory",
  "target_month": 2,
  "description": "Protects against Diphtheria, Pertussis, Tetanus, Hepatitis B, and Hib."
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/add_vaccination/`
- **HTTP Method:** `GET` (view catalog & form), `POST` (add new vaccine)
- **Request Details:** Form-encoded POST body containing vaccine catalog parameters.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/add_vaccination/` with success toast.
  - Failure: Re-renders form with error notice.
- **When API is Called:** When administrator clicks "Add to Master Catalog".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def add_vaccination(request):
    master_vaccines = vaccination.objects.filter(CHILD__isnull=True).order_by('target_month')
    if request.method == "POST":
        vaccine_code = request.POST.get("vaccine_code", "").strip()
        vaccine_name = request.POST.get("vaccine_name", "").strip()
        vaccine_type = request.POST.get("vaccine_type", "Mandatory").strip()
        target_month = int(request.POST.get("target_month", 0))
        description = request.POST.get("description", "").strip()
        
        vaccination.objects.create(
            CHILD=None,  # Master catalog template definition
            vaccine_code=vaccine_code,
            vaccine_name=vaccine_name,
            vaccine_type=vaccine_type,
            target_month=target_month,
            description=description,
            status='Master Template'
        )
        messages.success(request, f"Vaccine '{vaccine_name}' added to Master Schedule!")
        return redirect('/myapp/add_vaccination/')
    return render(request, 'admin/add_vaccination.html', {'master_vaccines': master_vaccines})
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def add_vaccination(request)`
- **Step-by-Step Processing:**
  1. Retrieves all master vaccine templates where `CHILD__isnull=True`.
  2. Validates incoming form fields (non-empty name, non-negative target month).
  3. Creates `vaccination` record with `CHILD=None`, which serves as a master template for child scheduling.
  4. Redirects back to page with success alert.
- **Database Interaction:** `INSERT INTO myapp_vaccination (CHILD_id, vaccine_code, vaccine_name, target_month, ...)` values `(NULL, ...)`.

---

## 5. CODE FLOW
1. Admin navigates to `/myapp/add_vaccination/`.
2. Page displays the vaccine creation form alongside a table of existing master vaccines.
3. Admin fills in vaccine code, name, target month, and description.
4. Admin submits form.
5. Server writes vaccine template into MySQL.
6. Page refreshes and displays the newly added vaccine in the master schedule table.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
This page is like **setting up the official Childhood Vaccination Calendar for the whole hospital**. It tells the system: "At birth, every baby must get BCG. At 6 weeks, every baby must get Pentavalent." Once the admin defines these standard rules here, health workers can schedule these vaccines for individual newborn babies.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Catalog Form Header** | Displays page title and explanation of immunization master schedule. | Header explaining master vaccine setup. |
| **Vaccine Code & Name Fields**| Inputs for medical code (e.g. BCG) and complete vaccine dose name. | Captures standardized medical names. |
| **Target Month & Type** | Input for target milestone in months and type dropdown (Mandatory/Optional). | Sets child age milestone and category. |
| **Clinical Description** | Textarea for indications, diseases prevented, and storage instructions. | Stores clinical background and guidelines. |
| **Master Vaccines Table** | Displays list of all configured master vaccines sorted by target month. | Shows current official immunization catalog. |