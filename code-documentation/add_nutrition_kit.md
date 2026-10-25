# Page Documentation: Add / Restock Nutrition Kit (`add_nutrition_kit.md`)

## 1. PAGE OVERVIEW
The **Add Nutrition Kit Page** is the supply replenishment form used by Anganwadi teachers. It allows teachers to log incoming shipments of supplementary nutrition food supplies, select standardized kit categories, enter product ingredients, and update stock counts for their center.

---

## 2. DATA USED IN THIS PAGE
- **Data Collected (Form Submission):**
  - `kit_type`: Category ('Maternal Nutrition Kit', 'Lactating Mother Kit', 'Infant Weaning Food').
  - `product_name`: Name of supplementary product (e.g., 'Amrutham Nutri-Mix Phase 1').
  - `product_details`: Nutritional breakdown (iron, folic acid, calcium, proteins, calories).
  - `quantity`: Number of units received in shipment.
  - `date`: Date of stock arrival.
- **Data Displayed:**
  - Standard kit type presets and stock input guidelines.
- **Data Format Example (Form POST):**
```json
{
  "kit_type": "Maternal Nutrition Kit",
  "product_name": "Nutri-Care Pregnancy Pack",
  "product_details": "500g Roasted cereal mix, Iron tablets, Folic acid, Calcium supplements, Iodine salt",
  "quantity": 50,
  "date": "2026-03-10"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/add_nutrition_kit/`
- **HTTP Method:** `GET` (display form), `POST` (save stock entry)
- **Request Details:** Form-encoded POST body with kit details and quantity.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/manage_kit/` with success toast.
  - Validation Failure: Re-renders form with field error alert.
- **When API is Called:** When teacher clicks "Add to Center Stock".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def add_nutrition_kit(request):
    teacher = get_current_anganwadi_teacher(request)
    if request.method == "POST":
        kit_type = request.POST.get('kit_type')
        product_name = request.POST.get('product_name')
        product_details = request.POST.get('product_details')
        quantity = int(request.POST.get('quantity', 0))
        arrival_date = request.POST.get('date') or date.today()
        
        # Save inventory record
        nutrition_kit.objects.create(
            TEACHER=teacher,
            USER=None,  # Center inventory reserve
            kit_type=kit_type,
            product_name=product_name,
            product_details=product_details,
            date=arrival_date,
            distribution_date=arrival_date,
            quantity=quantity,
            status='In Stock'
        )
        messages.success(request, f"Successfully stocked {quantity} units of '{product_name}'!")
        return redirect('/myapp/manage_kit/')
    return render(request, 'anganwadi_teacher/add_nutrition_kit.html', {'teacher': teacher})
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def add_nutrition_kit(request)`
- **Step-by-Step Processing:**
  1. Identifies logged-in Anganwadi teacher.
  2. Parses and validates input fields on POST.
  3. Inserts a new `myapp_nutrition_kit` record linked to `TEACHER=teacher` with `USER=None` (representing central center stock).
  4. Dispatches confirmation message and redirects to inventory manager.
- **Database Interaction:** Executes SQL `INSERT INTO myapp_nutrition_kit`.

---

## 5. CODE FLOW
1. Teacher clicks "Add New Kit" on the inventory page.
2. Form loads with category selectors, product name inputs, and quantity field.
3. Teacher enters arrival shipment details and submits form.
4. Server validates data and creates new inventory batch record in MySQL.
5. Teacher is redirected to stock manager showing updated totals.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **logging a new shipment of food boxes received at the Anganwadi center**. When the delivery van arrives with 50 packets of nutrition flour and vitamins, the teacher opens this form, types in "50 packets arrived today," and clicks save so the system knows the pantry is restocked.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Form Header** | Shows page title and breadcrumb link to inventory. | Navigation header and form introduction. |
| **Category & Product Name** | Dropdown for kit category and text input for brand/product name. | Classifies product type and records official title. |
| **Nutritional Contents Field** | Textarea describing ingredients, vitamins, and minerals. | Logs dietary details and ingredients. |
| **Quantity & Date Inputs** | Numeric input for packet count and date picker for arrival date. | Captures batch volume and arrival timestamp. |
| **Submit Action Buttons** | Submit button to commit stock and cancel link. | Dispatches data to backend database. |