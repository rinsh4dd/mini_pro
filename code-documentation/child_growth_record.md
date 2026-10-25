# Page Documentation: Child Growth & Development Monitoring (`child_growth_record.md`)

## 1. PAGE OVERVIEW
The **Child Growth & Development Monitoring Page** enables ASHA health workers to record pediatric developmental measurements over time. Health workers record periodic weight and height measurements during routine community visits, evaluate nutritional classifications (Normal, Moderately Underweight, Severely Underweight, Stunted), log dietary advice, and inspect developmental trends against WHO child growth standards.

---

## 2. DATA USED IN THIS PAGE
- **Data Collected (Form Submission):**
  - `child_id`: ID of target registered child.
  - `growth_date`: Date on which measurement was taken.
  - `weight`: Current measured body weight in kilograms (kg).
  - `height`: Current measured height / recumbent length in centimeters (cm).
  - `health_condition`: Assessment ('Normal Growth', 'Underweight', 'Severely Underweight', 'Stunted', 'Overweight').
  - `report_details`: Nutritional recommendations, feeding practices, and clinical remarks.
- **Data Displayed:**
  - Chronological growth logs table for selected child.
  - Interactive Chart.js Weight-for-Age and Height-for-Age trend curve.
- **Data Format Example (JSON):**
```json
{
  "child_id": 8,
  "growth_date": "2026-03-10",
  "weight": 8.4,
  "height": 71.5,
  "health_condition": "Normal Growth",
  "report_details": "Weight velocity is normal. Exclusive breastfeeding continued. Alert and active."
}
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/child_growth_record/` (also `/myapp/child_growth/`, `/myapp/view_child_growth/`)
- **HTTP Method:** `GET` (view growth logs & chart), `POST` (save measurement)
- **Request Details:** Form-encoded POST body with child ID, weight, height, and date.
- **Response Details:**
  - Success: HTTP 302 Redirect to `/myapp/child_growth_record/?child_id=<id>` with success toast.
  - Failure: Re-renders form with validation alert.
- **When API is Called:** When ASHA worker clicks "Save Growth Record".
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def child_growth_record_view(request):
    worker = get_current_asha_worker(request)
    area_q = get_area_filter_q(worker.Area_assigned) if worker else Q()
    children = child.objects.filter(area_q).select_related('USER')
    
    if request.method == "POST":
        target_child = get_object_or_404(children, id=request.POST.get("child_id"))
        rec = child_growth_record.objects.create(
            CHILD=target_child,
            height=float(request.POST.get("height", 65.0)),
            weight=float(request.POST.get("weight", 7.0)),
            growth_date=request.POST.get("growth_date"),
            health_condition=request.POST.get("health_condition", "Normal"),
            report_details=request.POST.get("report_details", "")
        )
        # Notify mother
        notification.objects.create(
            USER=target_child.USER,
            message=f"Growth record logged for '{target_child.child_name}': Weight {rec.weight} kg, Height {rec.height} cm ({rec.health_condition}).",
            notification_date=date.today()
        )
        messages.success(request, f"Growth record for '{target_child.child_name}' recorded successfully!")
        return redirect(f'/myapp/child_growth_record/?child_id={target_child.id}')
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def child_growth_record_view(request)`
- **Step-by-Step Processing:**
  1. Filters registered children in worker's assigned ward.
  2. On POST, parses height and weight measurements.
  3. Inserts growth datapoint into `myapp_child_growth_record`.
  4. Logs an in-app notification for the mother.
  5. Assembles historical chronological coordinates (dates, weights, heights) for Chart.js rendering.
  6. Renders template `ashawoker/child_growth_record.html`.
- **Database Interaction:** Executes SQL `INSERT INTO myapp_child_growth_record` and `INSERT INTO myapp_notification`.

---

## 5. CODE FLOW
1. ASHA worker visits child's home with portable infant hanging scale and measuring tape.
2. Worker opens `/myapp/child_growth_record/` on smartphone.
3. She selects child's name and enters current weight and height.
4. She clicks "Save Growth Record".
5. Backend writes measurement to database and computes growth velocity.
6. The interactive growth curve updates automatically showing if the child is gaining weight properly.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **marking a child's height and weight on the doorframe every few months**. When the health sister visits the baby, she weighs the baby on a scale and measures how tall the baby has grown. If the baby is growing healthy and chubby, the graph goes up green! If the baby lost weight, the graph warns the nurse that the baby might need extra nutrition food.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Child Selector Card** | Dropdown listing children in worker's ward with age and mother details. | Selects child for growth measurement. |
| **Measurement Logging Form** | Inputs for Growth Date, Weight (kg), Height (cm), and Nutritional Status. | Captures physical growth measurements. |
| **Clinical Notes & Diet** | Textarea for feeding recommendations and nutritional remarks. | Records feeding practices and advice. |
| **Interactive Growth Chart** | Chart.js visual canvas displaying Weight and Height progression curves. | Visual graph comparing child growth over time. |
| **Chronological Records Table**| Historical measurement log showing dates, numbers, and delete action. | Complete tabular history of all growth checkups. |