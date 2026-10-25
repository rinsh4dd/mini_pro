# Page Documentation: Child Growth & Development Charts (`user_child_growth.md`)

## 1. PAGE OVERVIEW
The **Child Growth & Development Charts Page** provides mothers with an interactive visual tracking tool for their child's physical development. It plots the child's weight-for-age and height-for-age progression against healthy developmental reference curves using Chart.js, displays nutritional status assessments from ASHA visits, and lists chronological measurement logs.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Selected Child Details: Child name, date of birth, current age in months, current weight, and latest height.
  - Interactive Growth Curves: Chart.js visualization plotting measured weight (kg) and height (cm) over chronological time.
  - Growth Measurements Table: Date of measurement (`growth_date`), Recorded Weight (`weight`), Recorded Height (`height`), Nutritional Condition (`health_condition`), and ASHA Dietary Guidance (`report_details`).
- **Data Source:** `myapp_child_growth_record` linked to `myapp_child` where `USER=mother`.
- **Data Format Example (JSON):**
```json
{
  "child_name": "Aarav Nair",
  "current_weight": 8.4,
  "current_height": 71.5,
  "records": [
    {"date": "2025-06-10", "weight": 3.2, "height": 50.0, "status": "Birth Baseline"},
    {"date": "2025-09-15", "weight": 5.8, "height": 60.5, "status": "Normal Growth"},
    {"date": "2026-03-10", "weight": 8.4, "height": 71.5, "status": "Normal Growth"}
  ]
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/user_child_growth/` (also `/myapp/view_child_growth_user/`)
- **HTTP Method:** `GET`
- **Request Details:** Query parameter `?child_id=<id>` (defaults to mother's first child).
- **Response Details:** Returns compiled HTML (`user/view_child_growth.html`) with growth dataset and Chart.js payload.
- **When API is Called:** On navigation to "Growth Charts" or when selecting a child.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def user_child_growth(request):
    mother, err_redirect = get_logged_in_mother(request)
    if err_redirect:
        return err_redirect
    children = child.objects.filter(USER=mother)
    selected_child = children.filter(id=request.GET.get('child_id')).first() or children.first()
    
    growth_records = child_growth_record.objects.filter(CHILD=selected_child).order_by('growth_date')
    dates = [r.growth_date.strftime('%b %d, %Y') for r in growth_records]
    weights = [r.weight for r in growth_records]
    heights = [r.height for r in growth_records]
    return render(request, 'user/view_child_growth.html', {
        'children': children,
        'selected_child': selected_child,
        'records': growth_records,
        'dates_json': json.dumps(dates),
        'weights_json': json.dumps(weights),
        'heights_json': json.dumps(heights)
    })
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def user_child_growth(request)`
- **Step-by-Step Processing:**
  1. Identifies logged-in mother and retrieves her children.
  2. Resolves selected child from `request.GET.get('child_id')`.
  3. Queries chronological growth measurements from `myapp_child_growth_record`.
  4. Formats dates, weights, and heights into JSON arrays for Chart.js.
  5. Renders `user/view_child_growth.html`.
- **Database Interaction:** `SELECT * FROM myapp_child_growth_record WHERE CHILD_id = ... ORDER BY growth_date ASC`.

---

## 5. CODE FLOW
1. Mother clicks "Child Growth" in portal navigation.
2. Server loads growth measurements for the baby.
3. Template passes data coordinates to Chart.js.
4. Browser renders interactive graphical curve showing baby's weight gain over time.
5. Table below lists historical measurements and nurse's feeding advice.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **a digital Growth Chart poster hanging on the clinic wall**. Every time the nurse weighs and measures the baby, a new dot is added to the chart. As the baby gets older, the line connects the dots into a curve going up. If the line is climbing smoothly, the mother can be happy that her baby is growing well and healthy!

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Child Selector Tabs** | Toggles between siblings if the mother has multiple children. | Allows switching between children. |
| **Current Vitals Summary** | Cards showing latest Weight (kg), Height (cm), and Nutritional Rating. | Snapshot of child's most recent vitals. |
| **Interactive Chart Canvas** | Chart.js visual curve plotting Weight and Height over time. | Graphical visualization of growth velocity. |
| **Historical Measurement Table**| Table listing date, weight, height, status, and ASHA remarks. | Chronological audit log of physical checkups. |
| **WHO Guidelines Explainer** | Informational section explaining healthy child growth milestones. | Educates mothers on normal developmental stages. |