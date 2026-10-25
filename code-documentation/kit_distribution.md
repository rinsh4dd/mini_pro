# Page Documentation: Nutrition Kit Distribution (`kit_distribution.md`)

## 1. PAGE OVERVIEW
The **Nutrition Kit Distribution Page** is the fulfillment interface where Anganwadi teachers allocate supplementary nutrition kits to verified mothers in their ward. It displays eligible beneficiaries, allows selecting available kits from inventory, automatically deducts stock upon issuance, and dispatches collection notification reminders to the recipient mother.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Eligible Beneficiaries List: Verified mothers residing in the teacher's ward (`user_table` filtered by `area_q`).
  - Available Stock Kits: Current inventory units available for distribution.
  - Active Allocations Table: List of distributions scheduled or completed this month.
- **Data Collected (Form Submission):**
  - `user_id`: ID of the recipient beneficiary mother.
  - `kit_name` / `kit_type`: Selected nutrition kit product.
  - `distribution_date`: Scheduled pickup/distribution date.
  - `quantity`: Number of units allocated (usually 1 or 2).
- **Data Format Example (Form POST):**
```json
{
  "user_id": 15,
  "product_name": "Maternal Nutrition Kit",
  "distribution_date": "2026-03-18",
  "quantity": 1
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/kit_distribution/`
- **HTTP Method:** `GET` (render distribution dashboard), `POST` (execute kit allocation)
- **Request Details:** Form-encoded POST body containing mother ID, kit choice, and date.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/kit_distribution/` with confirmation notice.
  - Validation Failure: Re-renders form with error alert (e.g. "Insufficient Stock").
- **When API is Called:** When teacher clicks "Allocate & Distribute Kit".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def kit_distribution(request):
    teacher = get_current_anganwadi_teacher(request)
    if request.method == "POST":
        mother = get_object_or_404(user_table, id=request.POST.get('user_id'))
        qty = int(request.POST.get('quantity', 1))
        # Deducts center inventory stock
        decrease_stock(request.POST.get('product_name'), qty)
        
        kit = nutrition_kit.objects.create(
            TEACHER=teacher,
            USER=mother,
            kit_type=request.POST.get('kit_type'),
            product_name=request.POST.get('product_name'),
            product_details=request.POST.get('product_details'),
            date=date.today(),
            distribution_date=request.POST.get('distribution_date'),
            quantity=qty,
            status='Pending'
        )
        # Dispatches notification to mother
        kit_notification.objects.create(
            NUTRITION=kit,
            USER=mother,
            notification_message=f"Nutrition Kit allocated: {kit.product_name}. Please collect it from your Anganwadi center on {kit.distribution_date}.",
            notification_date=date.today()
        )
        messages.success(request, f"Kit successfully allocated to '{mother.name}'!")
        return redirect('/myapp/kit_distribution/')
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def kit_distribution(request)`, `def decrease_stock(kit_name, qty)`
- **Step-by-Step Processing:**
  1. Filters eligible mothers using `get_area_filter_q(teacher.center_name)` to maintain strict ward isolation.
  2. On POST, calls `decrease_stock()` to atomically deduct quantity from center reserve records.
  3. Inserts a new `myapp_nutrition_kit` entry linking `USER=mother` and `TEACHER=teacher`.
  4. Creates a `myapp_kit_notification` record notifying the mother of the pickup date.
  5. Redirects to distribution view with confirmation toast.
- **Database Interaction:** Updates `myapp_nutrition_kit` (stock decrease), inserts allocation record, and inserts `myapp_kit_notification`.

---

## 5. CODE FLOW
1. Teacher navigates to `/myapp/kit_distribution/`.
2. Page lists verified mothers in the teacher's ward alongside available food kits.
3. Teacher selects mother's name, chooses kit, sets collection date, and clicks Submit.
4. Backend checks stock availability, deducts inventory, and records allocation.
5. Automated pickup notification is logged for the mother.
6. Page refreshes displaying the newly scheduled kit distribution.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **giving a food parcel to a registered mother at the Anganwadi center**. The teacher picks the mother's name from her village list, chooses which food packet to give her, and marks the collection date. The system automatically reduces the count on the center's shelf by 1 and sends a message to the mother saying: "Your nutrition packet is ready for pickup!"

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Distribution Form** | Selectors for Beneficiary Mother, Kit Product, Quantity, and Pickup Date. | Form to allocate a kit to a specific mother. |
| **Ward Beneficiaries Dropdown**| Displays verified mothers filtered strictly by the teacher's center ward. | Ensures kits are given to eligible local mothers. |
| **Inventory Stock Auto-Deduct**| Backend routine reducing central inventory when a kit is issued. | Prevents over-distribution of physical stock. |
| **Alert Notification Trigger** | Creates in-app pickup alert in `kit_notification` for the mother. | Automatically informs mother of collection date. |
| **Recent Distributions Grid** | Table showing kits allocated this month with delivery status badges. | Audit table tracking current distribution rounds. |