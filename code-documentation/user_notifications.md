# Page Documentation: Notifications & Health Alerts Inbox (`user_notifications.md`)

## 1. PAGE OVERVIEW
The **Notifications & Health Alerts Inbox Page** is the personalized communications center for registered mothers. It aggregates automated alerts regarding upcoming antenatal clinical checkups, child immunization camp dates, nutrition kit pickup reminders from the Anganwadi teacher, and general public health advisories with exact date timestamps.

---

## 2. DATA USED IN THIS PAGE
- **Data Displayed:**
  - Notifications List: Alert message text (`message`), Broadcast date (`notification_date`), Alert type classification (Checkup, Vaccine, Kit, or General), and Unread indicator.
  - Category Filter Tabs: All Notifications, Clinical Checkups, Child Vaccines, Nutrition Kits.
- **Data Source:** `myapp_notification` and `myapp_kit_notification` linked to `USER=mother`.
- **Data Format Example (JSON):**
```json
[
  {
    "id": 42,
    "category": "Vaccination",
    "message": "Vaccination scheduled for child 'Aarav Nair': Measles-Rubella (MR) Dose 1 on March 25, 2026.",
    "date": "2026-03-15"
  },
  {
    "id": 41,
    "category": "Nutrition Kit",
    "message": "Nutrition Kit allocated: Amrutham Nutri-Mix Phase 2. Please collect it from your Anganwadi center on March 18, 2026.",
    "date": "2026-03-12"
  }
]
```

---

## 3. API CONNECTION FOR THIS PAGE
- **API Endpoint:** `/myapp/user_notifications/` (also `/myapp/notification/`)
- **HTTP Method:** `GET`
- **Request Details:** Authenticated GET request with mother session.
- **Response Details:** Returns compiled HTML (`user/notification.html`) with notifications list.
- **When API is Called:** On navigation to "Notifications" or clicking bell icon.
- **Exact Code Snippet from Project:**
```python
# myapp/views.py
def user_notifications(request):
    mother, err_redirect = get_logged_in_mother(request)
    if err_redirect:
        return err_redirect
    general_notes = notification.objects.filter(USER=mother).order_by('-notification_date', '-id')
    kit_notes = kit_notification.objects.filter(USER=mother).order_by('-notification_date', '-id')
    
    # Merge and sort all alerts chronologically
    all_notes = list(general_notes)
    for kn in kit_notes:
        all_notes.append({
            'message': kn.notification_message,
            'notification_date': kn.notification_date,
            'is_kit': True
        })
    all_notes.sort(key=lambda x: x.notification_date if hasattr(x, 'notification_date') else x['notification_date'], reverse=True)
    return render(request, 'user/notification.html', {'notifications': all_notes, 'mother': mother})
```

---

## 4. BACKEND CONNECTION FOR THIS PAGE
- **Backend Controller:** `myapp/views.py` -> `def user_notifications(request)`
- **Step-by-Step Processing:**
  1. Identifies logged-in mother.
  2. Queries `myapp_notification` (general clinical and vaccine alerts) and `myapp_kit_notification` (nutrition kit alerts).
  3. Merges both querysets into a single chronological message stream.
  4. Renders `user/notification.html`.
- **Database Interaction:** `SELECT * FROM myapp_notification WHERE USER_id = ...` and `SELECT * FROM myapp_kit_notification WHERE USER_id = ...`.

---

## 5. CODE FLOW
1. Mother clicks the bell icon or "Notifications" link in her portal.
2. Server queries all medical, vaccine, and food alerts linked to her profile.
3. Page displays alerts in chronological order with date stamps and icons.
4. Mother reads reminders for upcoming appointments and pickups.

---

## 6. SIMPLE EXPLANATION (IN EASY WORDS)
Think of this page like **a digital Notification Inbox or SMS message tray on the mother's phone**. Whenever the nurse schedules a new checkup, the hospital schedules a baby vaccine, or the Anganwadi center packs a new food box, an alert message drops into this inbox so the mother never forgets an important health date.

---

## 7. BLOCK-BY-BLOCK SUMMARY

| Block / Section Name | What the Code Inside Does | One-Line Summary |
| :--- | :--- | :--- |
| **Notification Inbox Header**| Displays page title, total notification count, and category tabs. | Header with message count and filter options. |
| **Notification Feed Stream** | Chronological list of alert cards with icon, message, and date stamp. | Main message feed of health alerts and reminders. |
| **Category Icons & Badges** | Visual icon indicators (Stethoscope for Checkup, Syringe for Vaccine, Apple for Kit). | Categorizes alerts with visual icons. |
| **Empty State Display** | Friendly illustration shown when no notifications are pending. | Informs mother when all notifications are up to date. |