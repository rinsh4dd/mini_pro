# Page Documentation: Nutrition Kit Inventory Management (`manage_kit.md`)

## 1. PAGE OVERVIEW
The **Nutrition Kit Inventory Management Page** gives Anganwadi teachers complete oversight over food supply inventory. It displays stock levels across standard kit categories (Maternal Nutrition Kits, Lactation Kits, Infant Weaning Kits), indicates safety thresholds, lists item composition details, and provides quick shortcuts to restock supplies.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Inventory Overview: Available stock units, safety buffer alert levels, total distributed packages.
  - Kit Catalog Cards: Kit type (`kit_type`), Product name (`product_name`), Contents and nutrition specs (`product_details`), Current quantity in stock (`quantity`), Batch date (`date`).
- **Data Source:** `myapp_nutrition_kit` where records represent center inventory reserves.
- **Data Format Example (JSON):**
```json
{
  "kit_type": "Maternal Nutrition Support Kit",
  "product_name": "Amrutham Nutri-Mix (Pregnancy)",
  "product_details": "Fortified wheat flour, roasted gram, soya flour, jaggery, iron & folic acid packets.",
  "quantity": 85,
  "status": "In Stock"
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/manage_kit/`
- **HTTP Method:** `GET`
- **Request Details:** Authenticated GET request with session credentials.
- **Response Details:** Returns compiled HTML (`anganwadi_teacher/manage_kit.html`) with inventory tables.
- **When API is Called:** When teacher clicks "Manage Kit Inventory" in navigation.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def manage_kit(request):
    teacher = get_current_anganwadi_teacher(request)
    kits = nutrition_kit.objects.filter(TEACHER=teacher).order_by('-date')
    total_stock = sum(k.quantity for k in kits)
    return render(request, 'anganwadi_teacher/manage_kit.html', {
        'kits': kits,
        'teacher': teacher,
        'total_stock': total_stock
    })
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def manage_kit(request)`
- **Step-by-Step Processing:**
  1. Authenticates current teacher.
  2. Queries `myapp_nutrition_kit` records managed by this teacher.
  3. Evaluates stock counts and highlights low-stock items (< 10 units).
  4. Passes inventory list to `anganwadi_teacher/manage_kit.html`.
- **Database Interaction:** `SELECT * FROM myapp_nutrition_kit WHERE TEACHER_id = ...`.

---

## 5. CODE FLOW
1. Teacher clicks "Manage Stock" on teacher portal.
2. Server loads all inventory batches linked to teacher's center.
3. Page displays cards for each nutrition kit product with current stock count.
4. If stock is low, a red warning badge indicates restocking is needed.
5. Teacher can click "Add / Restock Kit" to add more units.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **checking the pantry and inventory shelves of the Anganwadi store**. It lists all the different food boxes in stock—like nutritious cereal mix, iron capsules, and baby food—and counts how many packets are left. If any box is nearly empty, the screen displays a warning to order more supplies.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Inventory Header & Restock**| Displays title and button to add/restock new nutrition kits. | Header with action to add new inventory. |
| **Stock Summary Metric Cards** | Cards displaying Total Inventory Units, Active Kit Types, and Low Stock Alerts. | High-level inventory capacity counters. |
| **Kit Catalog Cards / Table** | Detailed listing showing product name, nutrition ingredients, and available count. | Product breakdown with ingredients and quantities. |
| **Stock Level Indicator** | Color-coded badges: Green for healthy stock, Red for low stock warning. | Visual threshold indicator for supplies. |