# MaatriCare — Comprehensive Project Architecture & System Overview

## 1. Project Purpose in Simple Words
**MaatriCare** is a community-driven maternal and child healthcare management ecosystem. It bridges the critical healthcare gap between rural/local healthcare authorities, field workers, and mothers. In many rural and suburban localities, tracking antenatal checkups, child growth parameters, routine immunization schedules, and the distribution of supplementary nutrition kits is done through fragmented manual paper registers. This leads to missed immunizations, undetected maternal anemia or gestational complications, and delayed nutritional support.

MaatriCare solves this by providing a unified digital platform with four specialized role-based portals:
- **Administrative Portal (Medical Officers / Program Directors):** Manages personnel (ASHA workers and Anganwadi teachers), configures the national vaccine schedule catalog, oversees geographic ward allocations, monitors high-risk pregnancy watchlists, and generates analytical compliance reports.
- **ASHA Healthcare Worker Portal (Field Health Workers):** Verifies newly registered pregnant mothers in their assigned wards, logs clinical antenatal care checkups (blood pressure, weight, hemoglobin, trimester milestones), registers newborn babies, monitors pediatric growth velocity, and identifies at-risk mothers.
- **Anganwadi Teacher Portal (Child Care & Nutrition Centers):** Manages inventory for maternal and child supplementary nutrition kits, distributes kits to enrolled beneficiaries, schedules delivery dates, logs fulfillment history, and issues pickup reminders.
- **Beneficiary Mother / User Portal (Expectant & Nursing Mothers):** Provides mothers with transparent, direct access to their personal antenatal records, pregnancy progression timeline, digital child growth charts, complete child immunization card, nutrition kit delivery records, and instant appointment/reminder alerts.

---

## 2. Tech Stack Used

| Component Layer | Technologies Used | Details & Configuration |
| :--- | :--- | :--- |
| **Backend Framework** | **Django 5.2 / Python 3** | Robust Python web framework leveraging MVT (Model-View-Template) architectural pattern, secure session management, built-in CSRF protection, and Django ORM for relational querying. |
| **Database** | **MySQL (Relational Database)** | Database Name: `healthcare`<br>Host: `localhost:3306`<br>Managed through Django ORM with foreign key cascades, date computations, and relational integrity. |
| **Frontend Templates** | **HTML5 & Django Template Language (DTL)** | Modular templates with dynamic conditional rendering, filter expressions, template inheritance, and context variable bindings. |
| **Styling & Design** | **Vanilla CSS3 & Responsive Design** | Custom CSS design systems featuring responsive Flexbox/Grid layouts, glassmorphism UI elements, curated health palettes (teals, emeralds, roses, and indigos), and responsive mobile breakpoints. |
| **Client-side Scripting** | **Vanilla JavaScript (ES6+)** | Dynamic modal dialogs, tab switching, client-side date & phone regex validation, inline alert dismissals, dynamic search/filter filtering, and Chart.js bindings. |
| **Data Visualization** | **Chart.js (HTML5 Canvas)** | Renders interactive pediatric growth curves (Weight-for-Age and Height-for-Age) and administrative healthcare analytics bar, line, and doughnut charts. |
| **Icons & Typography** | **FontAwesome 6 & Google Fonts** | Visual iconography via FontAwesome; modern typography powered by Google Fonts (*Outfit*, *Inter*, and *Poppins*). |
| **Document Export Engine** | **ReportLab 4.x & Plaintext Engine** | Server-side programmatic generation of publication-quality administrative PDF reports (`SimpleDocTemplate`, `Table`, `ParagraphStyle`) and structured plain-text audit logs. |
| **Authentication & Auth** | **Django Auth & Role Groups** | Built-in `django.contrib.auth.models.User` extended with role groups (`admin`, `ashaworker`, `angteacher`, `user`) and database-backed profile entities. |

---

## 3. Overall Data Flow Diagram (Text Form)

The application follows an end-to-end client-server architecture powered by HTTP request-response cycles, server-side template rendering, and database transactions:

```text
+----------------------------------------------------------------------------------------------------+
|                                      MAATRICARE SYSTEM DATA FLOW                                   |
+----------------------------------------------------------------------------------------------------+

1. User Interaction:
   [Beneficiary / Healthcare Worker / Administrator]
                           │
                           ▼
2. Page Request:
   Opens Browser ───► Navigates to URL (e.g., http://localhost:8000/myapp/...) 
                           │
                           ▼
3. Request Dispatch:
   Web Browser sends HTTP GET / POST Request (Headers, Cookies, Form Data, URL Parameters)
                           │
                           ▼
4. Routing Layer:
   maatricaree/urls.py ───► myapp/urls.py (Matches URL pattern & resolves to corresponding view function)
                           │
                           ▼
5. Middleware Processing:
   Security Middleware ──► Session Middleware ──► Authentication Middleware ──► Message Middleware
                           │
                           ▼
6. Controller / View Logic (myapp/views.py):
   • Authenticates user role and checks session permission / ASHA assignment
   • Validates incoming HTTP POST payload (phone, dates, medical records, kit status)
   • Calls Django ORM models
                           │
                           ▼
7. Database Operations (MySQL - 'healthcare'):
   • Executes SQL queries (SELECT, INSERT, UPDATE, DELETE)
   • Enforces Foreign Key relationships (User <-> Mother <-> Child <-> Vaccination <-> Nutrition Kit)
   • Returns queryset / model instances back to Django ORM
                           │
                           ▼
8. Response Preparation & Template Engine:
   • View prepares Python dictionary context (records, KPIs, charts, alerts)
   • Django Template Engine compiles HTML template + merges dynamic context variables
   • (Or generates binary file streams like PDF/Text for download endpoints)
                           │
                           ▼
9. HTTP Response:
   Server sends HTTP 200 OK HTML payload or HTTP 302 Redirect with flash messages to browser
                           │
                           ▼
10. Client Rendering & Visual Display:
    Browser renders styled DOM, executes client-side scripts, initializes Chart.js graphs, displays alerts.
+----------------------------------------------------------------------------------------------------+
```

---

## 4. Complete List of ALL APIs and Endpoints in the Project

MaatriCare uses standard RESTful web endpoints implemented as Django view endpoints that handle both GET requests (page delivery, filtering, data display) and POST requests (state modifications, data submission, transactions):

| # | API Endpoint / Route | Method | What It Does | Calling Pages / Templates |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `/` or `/myapp/home/` | GET | Renders public landing page showcasing mission, key modules, and portal access | `index.html` |
| 2 | `/myapp/login/` or `/login/` | GET | Displays unified role-based login portal | `login.html` |
| 3 | `/myapp/login_post/` | POST | Authenticates credentials, checks verification status, routes to role dashboard | Form submission from `login.html` |
| 4 | `/myapp/change_password_post/` | POST | Validates and updates user password with confirmation check | `login.html` (Password Reset Tab) |
| 5 | `/myapp/forgot_password/` | GET, POST | Renders standalone password reset page and executes password update | `forgot_password.html` |
| 6 | `/myapp/user_registartion/` | GET, POST | Enrolls new beneficiary mother, creates User record and unverified mother profile | `user/user_registartion.html` |
| 7 | `/myapp/logout/` | GET | Clears session data, flushes authentication tokens, redirects to login | All authenticated page navbars |
| 8 | `/myapp/adminhome/` | GET | Computes and displays administrative overview KPIs and system statistics | `admin/admin_home.html` |
| 9 | `/myapp/manage_asha/` | GET | Lists all ASHA workers with ward assignments and caseload counts | `admin/manage_asha.html` |
| 10 | `/myapp/add_asha/` | GET, POST | Validates and registers new ASHA worker with user login credentials | `admin/add_asha.html` |
| 11 | `/myapp/edit_asha/<int:id>/` | GET, POST | Updates an existing ASHA worker's demographics and assigned ward | `admin/edit_asha.html` |
| 12 | `/myapp/delete_asha/<int:id>/` | GET, POST | Deactivates or removes an ASHA worker from the system | `admin/manage_asha.html` |
| 13 | `/myapp/manage_anganwadi/` | GET | Lists all Anganwadi teachers and their assigned community centers | `admin/manage_anganwadi.html` |
| 14 | `/myapp/add_anganwadi/` | GET, POST | Validates and registers new Anganwadi teacher with user login credentials | `admin/add_anganwadi.html` |
| 15 | `/myapp/edit_anganwadi/<int:id>/` | GET, POST | Modifies Anganwadi teacher profile, contact details, and center name | `admin/edit_anganwadi.html` |
| 16 | `/myapp/delete_anganwadi/<int:id>/` | GET, POST | Deactivates or removes an Anganwadi teacher from the registry | `admin/manage_anganwadi.html` |
| 17 | `/myapp/add_vaccination/` | GET, POST | Adds a standardized vaccine to the national immunization catalog | `admin/add_vaccination.html` |
| 18 | `/myapp/schedule_vaccination/` | GET, POST | Schedules an immunization camp/session for a child and sends notification | `admin/schedule_vaccination.html` |
| 19 | `/myapp/vaccination_records/` | GET, POST | Displays child vaccination statuses; updates dose status to Administered | `admin/vaccination_records.html` |
| 20 | `/myapp/report/` | GET | Generates analytics on high-risk mothers, kit supplies, and vaccination rates | `admin/report.html` |
| 21 | `/myapp/export_report_pdf/` | GET | Generates and streams publication-ready administrative PDF report | `admin/report.html` (Download PDF) |
| 22 | `/myapp/export_report_text/` | GET | Generates and streams structured plaintext summary health audit report | `admin/report.html` (Download Text) |
| 23 | `/myapp/seed_demo_data/` | GET | One-click seeder initializing realistic clinical demo records for demonstration | `admin/report.html` (Demo Button) |
| 24 | `/myapp/teacher_home/` | GET | Anganwadi teacher home dashboard with center kit inventory and alerts | `anganwadi_teacher/anganwadi_home.html` |
| 25 | `/myapp/manage_kit/` | GET | Displays kit categories, stock quantities, and inventory thresholds | `anganwadi_teacher/manage_kit.html` |
| 26 | `/myapp/add_nutrition_kit/` | GET, POST | Restocks or adds new nutrition kit products with quantity and contents | `anganwadi_teacher/add_nutrition_kit.html` |
| 27 | `/myapp/kit_distribution/` | GET, POST | Allocates nutrition kits to verified mothers in the teacher's ward | `anganwadi_teacher/kit_distribution.html` |
| 28 | `/myapp/kit_history/` | GET | Audit trail of distributed, pending, and rescheduled nutrition kits | `anganwadi_teacher/kit_history.html` |
| 29 | `/myapp/update_kit_status/<int:kit_id>/` | GET, POST | Updates delivery status of a nutrition kit to Distributed or Cancelled | `anganwadi_teacher/kit_history.html` |
| 30 | `/myapp/reschedule_kit/` | POST | Updates kit distribution date to a future scheduled date | `anganwadi_teacher/kit_history.html` |
| 31 | `/myapp/teacher_beneficiaries/` | GET | Roster of pregnant and lactating mothers within the teacher's center ward | `anganwadi_teacher/teacher_beneficiaries.html` |
| 32 | `/myapp/send_kit_reminder/` | POST | Sends automated kit collection notification reminder to a mother | `anganwadi_teacher/teacher_beneficiaries.html` |
| 33 | `/myapp/teacher_profile/` | GET, POST | Displays and updates Anganwadi teacher profile and password | `anganwadi_teacher/teacher_profile.html` |
| 34 | `/myapp/ashaworker_home/` | GET | Field dashboard for ASHA worker showing pending verifications and checkups | `ashawoker/asha_home.html` |
| 35 | `/myapp/verify_mother/` | GET | Displays pending mother registrations requiring local ward ASHA verification | `ashawoker/verify_mother.html` |
| 36 | `/myapp/verify_mother_action/<int:id>/<str:action>/` | GET, POST | Approves or rejects mother registration; links mother to ASHA worker | `ashawoker/verify_mother.html` |
| 37 | `/myapp/delete_mother/<int:id>/` | GET, POST | Deletes an unverified or invalid mother registration entry | `ashawoker/verify_mother.html` |
| 38 | `/myapp/manage_pregnancy/` | GET, POST | Records antenatal checkup clinical metrics (BP, weight, Hb, notes) | `ashawoker/manage_pregenecy_record.html` |
| 39 | `/myapp/register_newborn/` | GET, POST | Registers newborn infant with birth metrics and creates child profile | `ashawoker/register_newborn.html` |
| 40 | `/myapp/child_growth_record/` | GET, POST | Logs pediatric growth measurements (weight, height, nutritional status) | `ashawoker/child_growth_record.html` |
| 41 | `/myapp/ashaworker_profile/` | GET, POST | Displays and updates ASHA worker profile and credentials | `ashawoker/asha_profile.html` |
| 42 | `/myapp/userhome/` | GET | Maternal dashboard displaying gestational countdown, guides, and reminders | `user/user_home.html` |
| 43 | `/myapp/user_profile/` or `/myapp/view_profile/` | GET | Displays mother's personal, medical, and contact details | `user/view_profile.html` |
| 44 | `/myapp/edit_user_profile/` | POST | Updates mother's contact phone, address, and login password | `user/view_profile.html` |
| 45 | `/myapp/user_pregnancy_record/` | GET | Displays complete clinical antenatal checkup history and observations | `user/view_pregnency_record.html` |
| 46 | `/myapp/user_child_profile/` | GET | Lists registered children with birth statistics and clinical profile | `user/user_child_profile.html` |
| 47 | `/myapp/user_child_growth/` | GET | Shows child growth records, developmental milestones, and Chart.js graphs | `user/view_child_growth.html` |
| 48 | `/myapp/user_vaccination_schedule/` | GET | Digital child immunization card showing dose timings and status | `user/view_vaccination_schedule.html` |
| 49 | `/myapp/user_kit_history/` | GET | Lists supplementary nutrition kits assigned to mother with status | `user/view_kit_history.html` |
| 50 | `/myapp/user_notifications/` | GET | Notification center showing reminders for checkups, kits, and vaccines | `user/notification.html` |

---

## 5. Complete Database Schema & Data Dictionary

The project uses a MySQL relational database named **`healthcare`**, managed via Django's Object-Relational Mapper (ORM). Below is the comprehensive schema definition of all database tables, foreign keys, fields, data types, and constraints.

### 5.1 Tables Summary
1. `auth_user` (Django User System)
2. `auth_group` (Role Management)
3. `myapp_asha_worker` (Field Health Workers)
4. `myapp_anganwadi_teacher` (Nutrition Center Teachers)
5. `myapp_user_table` (Registered Mothers / Beneficiaries)
6. `myapp_pregnancy_record` (Antenatal Clinical Checkups)
7. `myapp_child` (Newborn & Child Profiles)
8. `myapp_child_growth_record` (Pediatric Growth Metrics)
9. `myapp_vaccination` (Immunization Doses & Master Catalog)
10. `myapp_vaccine_schedule` (Immunization Camp Schedules)
11. `myapp_nutrition_kit` (Supplementary Food Kits & Orders)
12. `myapp_kit_notification` (Nutrition Kit Alerts)
13. `myapp_notification` (General Patient Healthcare Alerts)
14. `myapp_report` (Generated Healthcare Reports)

---

### 5.2 Detailed Table Specifications

#### Table: `auth_user` (Django System Users)
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Auto Increment | Unique user identifier |
| `username` | Varchar(150) | Unique, Not Null | Login username (phone or identifier) |
| `password` | Varchar(128) | Not Null | PBKDF2/Argon2 hashed password |
| `email` | Varchar(254) | Nullable | User email address |
| `is_staff` | Boolean | Default False | Administrator privilege flag |
| `is_active` | Boolean | Default True | Account active status flag |
| `date_joined` | DateTime | Auto | Timestamp when user registered |

#### Table: `myapp_asha_worker`
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigInt | Primary Key, Auto Increment | Unique record identifier |
| `LOGIN_id` | Integer | Foreign Key (`auth_user.id`), ON DELETE CASCADE | Associated user login credentials |
| `Full_name` | LongText | Not Null | Full legal name of the ASHA worker |
| `Age` | Integer | Not Null | Worker age in years |
| `dob` | Date | Nullable | Date of birth |
| `Qualification` | LongText | Not Null | Educational and nursing qualification |
| `Email` | LongText | Not Null | Contact email address |
| `Address` | LongText | Not Null | Residential physical address |
| `image` | Varchar(100) | File Path (media/) | Uploaded profile photo filename |
| `Area_assigned` | LongText | Not Null | Assigned Panchayat Ward (e.g. Ward 01) |
| `Phone` | BigInt | Not Null | 10-digit primary mobile number |
| `Joining_date` | Date | Not Null | Date of service commencement |
| `Current_status` | LongText | Default 'Active' | Employment status ('Active', 'Inactive') |

#### Table: `myapp_anganwadi_teacher`
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigInt | Primary Key, Auto Increment | Unique record identifier |
| `LOGIN_id` | Integer | Foreign Key (`auth_user.id`), ON DELETE CASCADE | Associated user login credentials |
| `Name` | LongText | Not Null | Full legal name of the teacher |
| `Age` | Integer | Not Null | Age in years |
| `dob` | Date | Nullable | Date of birth |
| `Gender` | LongText | Not Null | Gender ('Female', 'Male') |
| `Phone` | BigInt | Not Null | 10-digit primary contact phone |
| `Email` | LongText | Not Null | Contact email address |
| `Address` | LongText | Not Null | Residential address |
| `image` | Varchar(100) | Nullable, File Path (media/) | Uploaded profile picture |
| `Qualification` | LongText | Not Null | Teacher educational qualifications |
| `center_name` | LongText | Not Null | Name of Anganwadi Center / Ward |
| `joining_date` | Date | Not Null | Date of official appointment |
| `Current_status` | LongText | Default 'Active' | Operational status ('Active', 'Inactive') |

#### Table: `myapp_user_table` (Beneficiary Mothers)
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigInt | Primary Key, Auto Increment | Unique beneficiary identifier |
| `LOGIN_id` | Integer | Foreign Key (`auth_user.id`), Nullable | Linked login account (enables self-service) |
| `ASHA_id` | BigInt | Foreign Key (`myapp_asha_worker.id`), Nullable | Verifying ASHA worker; **NULL if pending** |
| `name` | LongText | Not Null | Full legal name of expectant/nursing mother |
| `husband_name` | LongText | Not Null | Spouse / guardian name |
| `age` | Integer | Not Null | Mother's age in years |
| `dob` | Date | Not Null | Date of birth |
| `blood_group` | LongText | Not Null | Blood type (e.g. A+, O-, B+) |
| `phone` | BigInt | Not Null | 10-digit mobile contact number |
| `Email` | LongText | Not Null | Email address |
| `Address` | LongText | Not Null | Full postal address |
| `panchayath` | LongText | Not Null | Administrative Grama Panchayath |
| `area` | LongText | Nullable | Designated Ward / Area name |
| `district` | LongText | Not Null | District name |
| `state` | LongText | Not Null | State name |
| `pincode` | LongText | Not Null | 6-digit postal PIN code |
| `expected_delivery_date` | Date | Nullable | Estimated Delivery Date (EDD) |
| `registration_date` | Date | Auto Now Add, Nullable | Timestamp of initial system registration |

*Calculated Model Properties:*
- `gestation_weeks`: Calculated as `(280 - (expected_delivery_date - today).days) // 7`
- `gestation_month`: Calculated month of pregnancy (1 to 9)
- `gestation_week_display`: Formatted display string (e.g., "24 Weeks")
- `pregnancy_status_display`: Comprehensive pregnancy stage label

#### Table: `myapp_pregnancy_record` (Antenatal Checkups)
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigInt | Primary Key, Auto Increment | Unique clinical checkup log ID |
| `USER_id` | BigInt | Foreign Key (`myapp_user_table.id`), ON DELETE CASCADE | Mother being examined |
| `ASHA_id` | BigInt | Foreign Key (`myapp_asha_worker.id`), ON DELETE CASCADE | ASHA worker conducting visit |
| `previous_pregnency_count`| Integer | Not Null | Gravida / parity count |
| `expected_delivery_date` | Date | Not Null | Confirmed Expected Delivery Date |
| `checkup_date` | Date | Not Null | Date on which clinical checkup occurred |
| `weight` | Double | Not Null | Maternal body weight in kilograms (kg) |
| `height` | Double | Not Null | Maternal height in centimeters (cm) |
| `blood_pressure` | LongText | Not Null | Blood pressure string (e.g. "120/80 mmHg") |
| `hemoglobin` | Double | Not Null | Hemoglobin count in g/dL |
| `health_status` | LongText | Not Null | Clinical status ('Normal', 'High Risk', 'Anemic') |
| `additional_report` | LongText | Not Null | Clinical notes, dietary advisories |
| `next_checkup_date` | Date | Not Null | Next scheduled antenatal checkup date |

#### Table: `myapp_child`
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigInt | Primary Key, Auto Increment | Unique child identity record |
| `USER_id` | BigInt | Foreign Key (`myapp_user_table.id`), ON DELETE CASCADE | Mother of the child |
| `ASHA_id` | BigInt | Foreign Key (`myapp_asha_worker.id`), ON DELETE CASCADE | Attending field health worker |
| `child_name` | LongText | Not Null | Full name of infant |
| `gender` | LongText | Not Null | Gender ('Male', 'Female') |
| `date_of_birth` | Date | Not Null | Actual date of birth |
| `birth_weight` | Double | Not Null | Weight at birth in kilograms (kg) |
| `birth_height` | Double | Not Null | Length/height at birth in centimeters (cm) |
| `blood_group` | LongText | Not Null | Infant blood group |
| `place_of_birth` | LongText | Not Null | Facility type ('Hospital', 'Home', 'PHC') |
| `delivery_type` | LongText | Not Null | Method ('Normal Delivery', 'Cesarean Section')|
| `hospital` | LongText | Nullable | Name of medical institution |
| `health_status` | LongText | Not Null | Neonatal health rating ('Healthy', 'NICU Observed')|

#### Table: `myapp_child_growth_record`
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigInt | Primary Key, Auto Increment | Growth measurement log ID |
| `CHILD_id` | BigInt | Foreign Key (`myapp_child.id`), ON DELETE CASCADE | Child being monitored |
| `height` | Double | Not Null | Measured length / height (cm) |
| `weight` | Double | Not Null | Measured body weight (kg) |
| `growth_date` | Date | Not Null | Date of clinical measurement |
| `health_condition` | LongText | Not Null | Assessment ('Normal', 'Underweight', 'Stunted')|
| `report_details` | LongText | Not Null | Nutritional recommendations and notes |

#### Table: `myapp_vaccination`
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigInt | Primary Key, Auto Increment | Unique vaccination record ID |
| `CHILD_id` | BigInt | Foreign Key (`myapp_child.id`), Nullable | Assigned child (null for master catalog items)|
| `vaccine_code` | LongText | Nullable | Code identifier (e.g. "BCG", "ROTA-1") |
| `vaccine_name` | LongText | Not Null | Formal vaccine dose name |
| `vaccine_type` | LongText | Not Null | Category ('Mandatory', 'Recommended') |
| `target_month` | Integer | Default 0, Nullable | Target age milestone in months |
| `description` | LongText | Nullable | Clinical indications and protective scope |
| `vaccination_date`| Date | Nullable | Date scheduled or administered |
| `status` | LongText | Default 'Scheduled' | Status ('Scheduled', 'Administered', 'Pending')|

#### Table: `myapp_vaccine_schedule`
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigInt | Primary Key, Auto Increment | Schedule appointment ID |
| `VACCINATION_id` | BigInt | Foreign Key (`myapp_vaccination.id`), ON DELETE CASCADE | Linked vaccine record |
| `schedule_date` | Date | Not Null | Immunization session date |
| `time_from` | Time | Not Null | Session start time |
| `time_to` | Time | Not Null | Session conclusion time |

#### Table: `myapp_nutrition_kit`
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigInt | Primary Key, Auto Increment | Kit distribution record ID |
| `TEACHER_id` | BigInt | Foreign Key (`myapp_anganwadi_teacher.id`), ON DELETE CASCADE | Distributing Anganwadi teacher |
| `USER_id` | BigInt | Foreign Key (`myapp_user_table.id`), ON DELETE CASCADE | Recipient mother |
| `kit_type` | LongText | Not Null | Kit Category ('Maternal Nutrition', 'Infant Care')|
| `product_name` | LongText | Not Null | Item / Kit product name |
| `product_details` | LongText | Not Null | Ingredient & composition breakdown |
| `date` | Date | Not Null | Allocation date |
| `distribution_date`| Date | Not Null | Scheduled collection / delivery date |
| `quantity` | Integer | Not Null | Number of units distributed |
| `status` | LongText | Default 'Pending' | Fulfillment ('Pending', 'Distributed', 'Rescheduled')|

#### Table: `myapp_kit_notification`
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigInt | Primary Key, Auto Increment | Kit notification log ID |
| `NUTRITION_id` | BigInt | Foreign Key (`myapp_nutrition_kit.id`), ON DELETE CASCADE | Linked nutrition kit |
| `USER_id` | BigInt | Foreign Key (`myapp_user_table.id`), ON DELETE CASCADE | Recipient mother |
| `notification_message` | LongText | Not Null | Notification text alerting collection time |
| `notification_date` | Date | Not Null | Date sent |

#### Table: `myapp_notification`
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigInt | Primary Key, Auto Increment | Notification alert ID |
| `USER_id` | BigInt | Foreign Key (`myapp_user_table.id`), ON DELETE CASCADE | Recipient mother |
| `message` | LongText | Not Null | General alert / reminder message text |
| `notification_date` | Date | Not Null | Broadcast date |

#### Table: `myapp_report`
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigInt | Primary Key, Auto Increment | Report log entry ID |
| `report_type` | LongText | Not Null | Type ('Maternal Analytics', 'Vaccine Coverage') |
| `report_details` | LongText | Not Null | Serialized summary data or notes |
| `generated_date` | Date | Not Null | Date of generation |

### 5.3 External Data Sources
- The core platform is fully self-contained and does not rely on third-party cloud SaaS dependencies for patient health records, adhering to privacy-by-design healthcare standards.
- External static CDNs are used exclusively for user-interface styling and layout libraries:
  - FontAwesome 6 (icons)
  - Google Fonts (Outfit, Inter, Poppins webfonts)
  - Chart.js (client-side graphing engine via standard CDN bundle)

---

## 6. How the Frontend is Connected to the Backend

1. **Architecture Model:**
   MaatriCare utilizes Django's classical server-side rendered **Model-View-Template (MVT)** architecture. Unlike decoupled Single Page Applications (SPAs) that require external HTTP client libraries like Axios or Fetch for every page render, MaatriCare renders fully hydrated, SEO-optimized HTML pages directly on the server before transmitting them to the client.

2. **Base URL and Route Resolution:**
   - The primary application base URL root is mounted at `/myapp/` via `maatricaree/urls.py`:
     ```python
     path('myapp/', include('myapp.urls'))
     ```
   - Shortcuts are configured at `/` and `/login/` directing to the landing page and authentication portal.
   - Internal links inside HTML templates dynamically resolve target views using Django's reverse URL tag:
     ```html
     <a href="{% url 'adminhome' %}">Dashboard</a>
     <form method="POST" action="{% url 'login_post' %}">
     ```

3. **Form Submissions & Data Exchange:**
   - Client-to-server data transmission is conducted via standard HTTP `POST` requests with `multipart/form-data` (for file/image uploads like profile photos) or `application/x-www-form-urlencoded` (for text and demographic inputs).
   - Dynamic client-side operations (like filtering distribution history, sorting tables, or triggering alert dismissals) use vanilla JavaScript DOM event listeners that interact directly with the rendered DOM elements.

4. **Security & Session Authentication:**
   - User identity and permissions are tracked across HTTP requests via HTTP-only session cookies (`sessionid`) and Django session backends.
   - Every state-altering form (`POST`) contains Django's `{% csrf_token %}` to prevent Cross-Site Request Forgery attacks.
   - Role boundaries are strictly enforced inside Python view functions using Django's `request.user.groups` verification and session-stored identifier bindings (`request.session['asha_id']`, `mother = user_table.objects.filter(LOGIN=request.user).first()`).

---

## 7. System Credentials Reference & Demo Accounts

All credentials can be initialized or refreshed into the database using:
```bash
python manage.py seed_demo_data
```

### 7.1 Administrator Account
| Role | Username | Password | Email | Access Scope |
| :--- | :--- | :--- | :--- | :--- |
| **System Administrator** | `admin` | `admin123` | `admin@gmail.com` | Full Administrative Portal (`/myapp/adminhome/`) & Django Admin (`/admin/`) |

### 7.2 ASHA Healthcare Workers (Panchayath Wards 01 to 05)
| Ward Code | Assigned Area | Staff Name | Username | Password | Contact Phone |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Ward 01** | Main Community Center | Fatima Beevi | `asha01` | `asha01` | 9847123456 |
| **Ward 02** | East Sector | Kavitha Nair | `asha02` | `asha02` | 9847123458 |
| **Ward 03** | West Gram | Priya Nair | `asha03` | `asha03` | 9847234567 |
| **Ward 04** | North Colony | Rekha Menon | `asha04` | `asha04` | 9847345677 |
| **Ward 05** | South Extension | Mary Joseph | `asha05` | `asha05` | 9847345678 |

### 7.3 Anganwadi Teachers (Centers 01 to 05)
| Ward Code | Anganwadi Center | Teacher Name | Username | Password | Contact Phone |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Ward 01** | Model Anganwadi Center 01 | Anita Sharma | `teacher01` | `teacher01` | 9847456789 |
| **Ward 02** | Community Anganwadi Center 02 | Lakshmi Menon | `teacher02` | `teacher02` | 9847567890 |
| **Ward 03** | West Gram Anganwadi Center 03 | Sunitha Varghese | `teacher03` | `teacher03` | 9847678901 |
| **Ward 04** | North Colony Anganwadi Center 04 | Radhika Pillai | `teacher04` | `teacher04` | 9847789012 |
| **Ward 05** | South Extension Anganwadi Center 05 | Deepa Mohan | `teacher05` | `teacher05` | 9847890123 |

### 7.4 Beneficiary Mother Accounts
- Beneficiary mothers register directly via the portal at `/myapp/user_registartion/`.
- Mothers choose their own `username` and `password` during registration.
- Once registered, the mother must be verified by the ASHA worker assigned to her designated ward before her login becomes active.
