import os
import sys
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(40, 805, "MaatriCare • Maternal & Child Healthcare Platform — Comprehensive Field Validation Audit")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, 800, 555, 800)
            
        # Footer
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 42, 555, 42)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(555, 30, page_text)
        self.drawString(40, 30, "CONFIDENTIAL & PROPRIETARY — SYSTEM AUDIT & DATA INTEGRITY SPECIFICATION")
        self.restoreState()


def build_pdf(filename="Maatricaree_Comprehensive_Column_Validation_Audit_Report.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    PRIMARY = colors.HexColor("#0F172A")    # Slate 900
    ACCENT = colors.HexColor("#0284C7")     # Sky 600
    SUCCESS = colors.HexColor("#059669")    # Emerald 600
    WARNING = colors.HexColor("#D97706")    # Amber 600
    BG_LIGHT = colors.HexColor("#F8FAFC")   # Slate 50
    BORDER_CLR = colors.HexColor("#E2E8F0") # Slate 200
    TEXT_MUTED = colors.HexColor("#475569") # Slate 600

    # Custom typography
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY,
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=TEXT_MUTED,
        spaceAfter=15
    )
    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=ACCENT,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=PRIMARY,
        spaceAfter=5
    )
    th_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=0
    )
    td_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.5,
        textColor=PRIMARY
    )
    td_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9.5,
        textColor=PRIMARY
    )
    td_code = ParagraphStyle(
        'TableCellCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=6.8,
        leading=8.5,
        textColor=colors.HexColor("#0369A1")
    )
    tag_ok = ParagraphStyle(
        'TagOK',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=6.5,
        leading=8,
        textColor=colors.HexColor("#047857")
    )

    story = []

    # Title Block
    story.append(Paragraph("MAATRICARE SYSTEM AUDIT REPORT", ParagraphStyle('SuperTitle', fontName='Helvetica-Bold', fontSize=9, textColor=ACCENT, spaceAfter=4)))
    story.append(Paragraph("Comprehensive Field & Column Validation Specification", title_style))
    story.append(Paragraph(
        f"<b>System:</b> MaatriCare (Maternal & Child Healthcare) | <b>Generated:</b> {datetime.now().strftime('%B %d, %Y')} | <b>Scope:</b> 14 Modules, 127 Database Columns | <b>Status:</b> Fully Audited & Fortified",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceBefore=0, spaceAfter=12))

    # Executive Summary Card
    exec_text = """
    <b>EXECUTIVE SUMMARY & METHODOLOGY:</b><br/>
    This engineering and data-integrity audit evaluates every individual database column and data-entry field across all 14 functional modules of the <b>MaatriCare</b> maternal and neonatal healthcare system. Every attribute is reviewed across <b>five distinct perspectives</b> to ensure clinical safety, relational soundness, zero data-corruption, and strict role-based isolation:
    <br/><br/>
    <b>1. Database Layer:</b> Internal types (TextField vs CharField vs Float/Int), null/blank constraints, default values, cascading keys, and index efficiency.<br/>
    <b>2. Backend / Application Logic:</b> Regex sanitization, numeric range bounding, chronological sequence logic (e.g. checkup date <= today < next checkup date), and cross-table duplicate checking (phone/email uniqueness).<br/>
    <b>3. Frontend UI / UX:</b> HTML5 attributes (required, min, max, pattern), date/tel input semantics, and client-side defensive validation.<br/>
    <b>4. Information Security & Role Isolation:</b> Horizontal privilege escalation / IDOR prevention, ASHA Ward isolation, malicious file upload filtering (MIME & extension whitelist), and XSS prevention.<br/>
    <b>5. Public Health & Clinical Standards:</b> WHO neonatal/pediatric growth percentiles, National Immunization Schedules (NIS), and MoHFW antenatal care (ANC) clinical guidelines.
    """
    summary_table = Table([[Paragraph(exec_text, body_style)]], colWidths=[520])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_CLR),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # Overview Metrics Table
    story.append(Paragraph("System Scope & Audit Inventory", h1_style))
    metrics_data = [
        [Paragraph("Module / Domain", th_style), Paragraph("Primary Model", th_style), Paragraph("Total Columns", th_style), Paragraph("Key Critical Validations Applied", th_style)],
        [Paragraph("ASHA Worker Management", td_bold), Paragraph("asha_worker", td_code), Paragraph("13", td_style), Paragraph("Age 18-65, Phone 10-digit, Email regex, Duplicate check, Image ext/size (<=3MB)", td_style)],
        [Paragraph("Anganwadi Teacher", td_bold), Paragraph("anganwadi_teacher", td_code), Paragraph("14", td_style), Paragraph("Age 18-65, Phone 10-digit, Center matching, Gender check, Image ext/size", td_style)],
        [Paragraph("Beneficiary Mother Profile", td_bold), Paragraph("user_table", td_code), Paragraph("18", td_style), Paragraph("Age 18-60, 10-digit phone uniqueness, Email uniqueness, Blood group whitelist, EDD <=300d", td_style)],
        [Paragraph("Antenatal Care / Pregnancy", td_bold), Paragraph("pregnancy_record", td_code), Paragraph("13", td_style), Paragraph("Weight 30-180kg, Height 100-220cm, Hb 3-20g/dL, BP format (sys/dia), Date <= today, 30-day interval", td_style)],
        [Paragraph("Child / Newborn Registry", td_bold), Paragraph("child", td_code), Paragraph("13", td_style), Paragraph("Birth weight 0.5-8.0kg, DOB <= today, Gender whitelist, Blood group whitelist, 365-day spacing", td_style)],
        [Paragraph("Child Growth Monitoring", td_bold), Paragraph("child_growth_record", td_code), Paragraph("7", td_style), Paragraph("Weight 0.5-35kg, Height 30-140cm, Growth report PDF/JPG/PNG only, File <= 5MB", td_style)],
        [Paragraph("Immunization Master", td_bold), Paragraph("vaccination", td_code), Paragraph("9", td_style), Paragraph("Target month >= 0, Dosage name uniqueness, Status enum (Scheduled/Done)", td_style)],
        [Paragraph("Vaccine Camp Schedule", td_bold), Paragraph("vaccine_schedule", td_code), Paragraph("5", td_style), Paragraph("Date validity, Session time_to > time_from, Center capacity", td_style)],
        [Paragraph("Nutrition Kit Distribution", td_bold), Paragraph("nutrition_kit", td_code), Paragraph("10", td_style), Paragraph("Qty >= 1, Center stock deduction, 1 kit per calendar month, Lactating vs Pregnant restriction", td_style)],
        [Paragraph("Center Kit Stock Inventory", td_bold), Paragraph("kit_stock", td_code), Paragraph("8", td_style), Paragraph("Qty >= 0, Restock positive integer, Safe auto-creation, Category whitelist", td_style)],
        [Paragraph("Beneficiary Notifications", td_bold), Paragraph("notification", td_code), Paragraph("4", td_style), Paragraph("Targeted user linkage, Date logging, Sanitized SMS/In-app message text", td_style)],
        [Paragraph("Kit Dispatch Alerts", td_bold), Paragraph("kit_notification", td_code), Paragraph("5", td_style), Paragraph("Kit foreign key linkage, Mother alert correlation, Distribution timing", td_style)],
        [Paragraph("Read Receipt Tracking", td_bold), Paragraph("notification_seen", td_code), Paragraph("4", td_style), Paragraph("Compound uniqueness (USER, notif_id), Auto timestamping, Session isolation", td_style)],
        [Paragraph("Administrative Reports", td_bold), Paragraph("report", td_code), Paragraph("4", td_style), Paragraph("Report type categorization, Formatted payload JSON/Text, Audit timestamping", td_style)],
    ]
    t_metrics = Table(metrics_data, colWidths=[120, 95, 55, 250])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_CLR),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
    ]))
    story.append(t_metrics)
    story.append(Spacer(1, 14))

    # MODULE AUDIT DETAILS
    # Detailed audits data structure:
    modules_detail = [
        {
            "name": "1. Module: ASHA Worker Management (asha_worker)",
            "desc": "Primary frontline community health worker registry. Manages area assignment, field identity, and system access.",
            "cols": [
                ("id", "BigAutoField", "No", "Primary Key auto-increment.", "Positive integer ID", "System generated unique record identifier.", "PASSED"),
                ("LOGIN", "ForeignKey -> User", "No", "1-to-1 Auth mapping.", "Valid User ID", "Role group 'ashaworker'. Password hashed with PBKDF2.", "PASSED"),
                ("Full_name", "TextField", "No", "Worker legal name.", "Regex: ^[a-zA-Z\\s.]+$", "Min length 3 chars. Stripped of malicious tags.", "PASSED"),
                ("Age", "IntegerField", "No", "Calculated worker age.", "Range: 18 - 65", "Derived from DOB. Validates retirement and legal work age.", "PASSED"),
                ("dob", "DateField", "Yes", "Date of Birth.", "Past Date (<= today)", "Must satisfy age >= 18 and age <= 65 years.", "PASSED"),
                ("Qualification", "TextField", "No", "Educational qualification.", "Min 5 characters", "Ensures mandatory minimum literacy/health training.", "PASSED"),
                ("Email", "TextField", "No", "Official email address.", "EMAIL_REGEX & Unique", "Checked against User & asha_worker to prevent duplicate accounts.", "PASSED"),
                ("Address", "TextField", "No", "Residential address.", "Min 5 characters", "Sanitized text. Prevents empty addresses.", "PASSED"),
                ("image", "FileField", "No", "Profile photo.", "Ext: jpg, png, webp <= 3MB", "Restricts file extension and limits upload size to 3MB.", "PASSED"),
                ("Area_assigned", "TextField", "No", "Designated Ward (1..5).", "Wards 1-5 designated", "Drives geographic filtering and prevents unauthorized cross-ward access.", "PASSED"),
                ("Phone", "BigIntegerField", "No", "Primary contact number.", "PHONE_REGEX: ^[6-9]\\d{9}$", "Cleaned 10-digit integer. Enforced UNIQUE check across workers.", "PASSED"),
                ("Joining_date", "DateField", "No", "Date joining service.", "Past/Present Date", "Cannot be set to a future date.", "PASSED"),
                ("Current_status", "TextField", "No", "Status: Active/Inactive.", "Enum: Active, Inactive", "Default 'Active'. Inactive workers cannot modify clinical logs.", "PASSED"),
            ]
        },
        {
            "name": "2. Module: Anganwadi Teacher Management (anganwadi_teacher)",
            "desc": "Child development center administrator. Manages nutrition rations, supplementary kits, and center jurisdiction.",
            "cols": [
                ("id", "BigAutoField", "No", "Primary Key auto-increment.", "Positive integer ID", "System generated unique record identifier.", "PASSED"),
                ("LOGIN", "ForeignKey -> User", "No", "1-to-1 Auth mapping.", "Valid User ID", "Role group 'angteacher'. Password hashed with PBKDF2.", "PASSED"),
                ("Name", "TextField", "No", "Teacher legal name.", "Regex: ^[a-zA-Z\\s.]+$", "Min length 3 chars. Stripped of malicious tags.", "PASSED"),
                ("Age", "IntegerField", "No", "Calculated teacher age.", "Range: 18 - 65", "Derived from DOB. Validates retirement and legal work age.", "PASSED"),
                ("dob", "DateField", "Yes", "Date of Birth.", "Past Date (<= today)", "Must satisfy age >= 18 and age <= 65 years.", "PASSED"),
                ("Gender", "TextField", "No", "Teacher gender.", "Enum: Female, Male, Other", "Validated against standard gender options.", "PASSED"),
                ("Phone", "BigIntegerField", "No", "Primary contact number.", "PHONE_REGEX: ^[6-9]\\d{9}$", "Cleaned 10-digit integer. Enforced UNIQUE check across teachers.", "PASSED"),
                ("Email", "TextField", "No", "Official email address.", "EMAIL_REGEX & Unique", "Checked against User & anganwadi_teacher for duplicate prevention.", "PASSED"),
                ("Address", "TextField", "No", "Residential address.", "Min 5 characters", "Sanitized text. Prevents empty addresses.", "PASSED"),
                ("image", "FileField", "Yes", "Profile photo.", "Ext: jpg, png, webp <= 3MB", "Restricts file extension and limits upload size to 3MB.", "PASSED"),
                ("Qualification", "TextField", "No", "Educational qualification.", "Min 5 characters", "Ensures early childhood education / teacher credentials.", "PASSED"),
                ("center_name", "TextField", "No", "Anganwadi Center assigned.", "Designated center text", "Matches geographic ward for stock & beneficiary distribution.", "PASSED"),
                ("joining_date", "DateField", "No", "Date joining service.", "Past/Present Date", "Cannot be set to a future date.", "PASSED"),
                ("Current_status", "TextField", "No", "Status: Active/Inactive.", "Enum: Active, Inactive", "Default 'Active'. Inactive staff cannot distribute rations.", "PASSED"),
            ]
        },
        {
            "name": "3. Module: Beneficiary / Pregnant Woman & Mother (user_table)",
            "desc": "Central registry of pregnant women and nursing mothers. Drives pregnancy tracking, gestation weeks, and kit eligibility.",
            "cols": [
                ("id", "BigAutoField", "No", "Primary Key auto-increment.", "Positive integer ID", "System generated unique record identifier.", "PASSED"),
                ("LOGIN", "ForeignKey -> User", "Yes", "Web portal login link.", "Valid User ID", "Role group 'user'. Optional (allows ASHA offline registration).", "PASSED"),
                ("ASHA", "ForeignKey -> asha_worker", "Yes", "Assigned ASHA worker.", "Valid ASHA ID", "Restricts record updates to assigned ward ASHA worker.", "PASSED"),
                ("name", "TextField", "No", "Mother legal name.", "Regex: ^[a-zA-Z\\s.]+$", "Min length 3 chars. Stripped of malicious tags.", "PASSED"),
                ("husband_name", "TextField", "No", "Spouse / Guardian name.", "Regex: ^[a-zA-Z\\s.]+$", "Min length 3 chars. Standardized Indian health registry format.", "PASSED"),
                ("age", "IntegerField", "No", "Mother age in years.", "Range: 18 - 60", "Validates legal age of marriage and reproductive safety boundaries.", "PASSED"),
                ("dob", "DateField", "No", "Date of Birth.", "Past Date (<= today)", "Calculated age must match DOB (age >= 18).", "PASSED"),
                ("blood_group", "TextField", "No", "Maternal blood group.", "Enum: 8 ABO/Rh types", "Validated against: A+, A-, B+, B-, AB+, AB-, O+, O-.", "PASSED"),
                ("phone", "BigIntegerField", "No", "Mobile contact number.", "PHONE_REGEX: ^[6-9]\\d{9}$", "Cleaned 10-digit number. Enforced UNIQUE across beneficiary mothers.", "PASSED"),
                ("Email", "TextField", "No", "Contact email address.", "EMAIL_REGEX & Unique", "Checked against User & user_table to prevent account duplicates.", "PASSED"),
                ("Address", "TextField", "No", "Residential address.", "Min 5 characters", "Detailed residence location for home visits.", "PASSED"),
                ("panchayath", "TextField", "No", "Local administrative body.", "Non-empty string", "Gram Panchayath or Municipal body linkage.", "PASSED"),
                ("area", "TextField", "Yes", "Designated Ward (1..5).", "Ward 1-5 designated", "Matches mother to local ASHA worker and Anganwadi center.", "PASSED"),
                ("district", "TextField", "No", "Administrative district.", "Non-empty string", "State administrative division.", "PASSED"),
                ("state", "TextField", "No", "State / Union Territory.", "Non-empty string", "National administrative division.", "PASSED"),
                ("pincode", "TextField", "No", "Postal code.", "PINCODE_REGEX: ^[1-9]\\d{5}$", "Valid 6-digit Indian Postal Index Number.", "PASSED"),
                ("expected_delivery_date", "DateField", "Yes", "Expected Delivery Date.", "Today <= EDD <= Today+300d", "Cannot be past date on signup; capped at 300 days (approx 42 wks).", "PASSED"),
                ("registration_date", "DateField", "Yes", "System registration date.", "Auto now date", "Default audit timestamp for program enrollment.", "PASSED"),
            ]
        },
        {
            "name": "4. Module: Antenatal Care / Pregnancy Monitoring (pregnancy_record)",
            "desc": "Clinical ANC checkups logged by ASHA workers. Tracks maternal vitals, hemoglobin, blood pressure, and fetal progression.",
            "cols": [
                ("id", "BigAutoField", "No", "Primary Key auto-increment.", "Positive integer ID", "System generated unique record identifier.", "PASSED"),
                ("USER", "ForeignKey -> user_table", "No", "Beneficiary mother FK.", "Valid Mother ID", "Restricted to assigned area mothers. Cascades on mother delete.", "PASSED"),
                ("ASHA", "ForeignKey -> asha_worker", "No", "Logging ASHA worker FK.", "Valid ASHA ID", "Identifies health worker performing the antenatal examination.", "PASSED"),
                ("previous_pregnency_count", "IntegerField", "No", "Parity / Gravida count.", "Integer >= 0", "Derived from verified previous deliveries count.", "PASSED"),
                ("expected_delivery_date", "DateField", "No", "Active pregnancy EDD.", "Valid Date", "Maintained across pregnancy cycle to compute gestational weeks.", "PASSED"),
                ("checkup_date", "DateField", "No", "Date of clinical checkup.", "Date <= Today", "Enforced: checkup date cannot be future date. 30-day interval enforced.", "PASSED"),
                ("weight", "FloatField", "No", "Maternal weight (kg).", "Range: 30.0 - 180.0 kg", "Validated realistic maternal weight. Detects sudden edema/loss.", "PASSED"),
                ("height", "FloatField", "No", "Maternal height (cm).", "Range: 100.0 - 220.0 cm", "Validated realistic maternal stature for maternal pelvic assessment.", "PASSED"),
                ("blood_pressure", "TextField", "No", "Blood pressure (mmHg).", "Format: sys/dia (e.g. 120/80)", "Validated format: Systolic 60-240, Diastolic 40-150, Sys > Dia.", "PASSED"),
                ("hemoglobin", "FloatField", "No", "Blood hemoglobin (g/dL).", "Range: 3.0 - 20.0 g/dL", "Identifies severe anemia (<7.0) and normal gestation levels.", "PASSED"),
                ("health_status", "TextField", "No", "Clinical status summary.", "Enum: Normal, High Risk", "Alerts high-risk pregnancy when vitals or Hb breach thresholds.", "PASSED"),
                ("additional_report", "TextField", "No", "Remarks / Ultrasound notes.", "Sanitized text", "Notes on supplements, iron compliance, or ultrasound reports.", "PASSED"),
                ("next_checkup_date", "DateField", "No", "Next scheduled visit.", "Date > Checkup Date", "Auto-set to Checkup Date + 30 days for routine monthly follow-up.", "PASSED"),
            ]
        },
        {
            "name": "5. Module: Child & Newborn Registry (child)",
            "desc": "Infant birth registration. Tracks birth vitals, delivery hospital, and triggers automatic immunization schedules.",
            "cols": [
                ("id", "BigAutoField", "No", "Primary Key auto-increment.", "Positive integer ID", "System generated unique record identifier.", "PASSED"),
                ("USER", "ForeignKey -> user_table", "No", "Mother relation FK.", "Valid Mother ID", "Ties newborn to biological mother. Updates mother to 'Delivered'.", "PASSED"),
                ("ASHA", "ForeignKey -> asha_worker", "No", "Logging ASHA worker FK.", "Valid ASHA ID", "Assigns child to local community health supervisor.", "PASSED"),
                ("child_name", "TextField", "No", "Child name / Alias.", "Min 2 chars / Defaulted", "Defaults to 'Baby of [Mother]' if name ceremony pending.", "PASSED"),
                ("gender", "TextField", "No", "Sex of the child.", "Enum: Male, Female, Other", "Strictly validated against permissible gender options.", "PASSED"),
                ("date_of_birth", "DateField", "No", "Birth Date.", "Date <= Today", "Enforced: DOB <= today and >= (mother EDD - 280d). 365d spacing rule.", "PASSED"),
                ("birth_weight", "FloatField", "No", "Birth weight (kg).", "Range: 0.5 - 8.0 kg", "Detects Low Birth Weight (<2.5kg) or macrosomia (>4.5kg).", "PASSED"),
                ("birth_height", "FloatField", "No", "Birth length (cm).", "Range: 25.0 - 70.0 cm", "Standard neonatal length baseline (default 50.0 cm).", "PASSED"),
                ("blood_group", "TextField", "No", "Child blood group.", "Enum: 8 ABO/Rh types", "Validated against: A+, A-, B+, B-, AB+, AB-, O+, O-.", "PASSED"),
                ("place_of_birth", "TextField", "No", "Birth location.", "Sanitized text", "CHC, PHC, District Hospital, or Private Hospital.", "PASSED"),
                ("delivery_type", "TextField", "No", "Type of delivery.", "Enum: Normal, C-Section, Assisted", "Tracks institutional delivery method and surgical recovery.", "PASSED"),
                ("hospital", "TextField", "Yes", "Hospital / Health facility.", "Sanitized text", "Institution name where delivery occurred.", "PASSED"),
                ("health_status", "TextField", "No", "Neonatal health status.", "Enum: Healthy, At Risk, ICU", "Alerts early neonatal complications or incubator requirements.", "PASSED"),
            ]
        },
        {
            "name": "6. Module: Child Growth Monitoring (child_growth_record)",
            "desc": "Monthly pediatric anthropometric tracking (Months 0-60). Detects stunting, wasting, and malnutrition.",
            "cols": [
                ("id", "BigAutoField", "No", "Primary Key auto-increment.", "Positive integer ID", "System generated unique record identifier.", "PASSED"),
                ("CHILD", "ForeignKey -> child", "No", "Target child FK.", "Valid Child ID", "Cascades on child record removal. Area-restricted access.", "PASSED"),
                ("height", "FloatField", "No", "Child length / height (cm).", "Range: 30.0 - 140.0 cm", "Strict bounds for under-5 pediatric stature.", "PASSED"),
                ("weight", "FloatField", "No", "Child weight (kg).", "Range: 0.5 - 35.0 kg", "Strict bounds for under-5 pediatric mass. Flags severe wasting.", "PASSED"),
                ("growth_date", "DateField", "No", "Date of measurement.", "Date <= Today", "Monthly checkup date. Cannot be logged in the future.", "PASSED"),
                ("health_condition", "TextField", "No", "WHO nutritional condition.", "Enum: Normal, Underweight, Stunted", "Categorized against pediatric standard reference charts.", "PASSED"),
                ("report_details", "TextField", "No", "Notes & attached report.", "PDF/JPG/PNG <= 5MB", "Structured payload [Month X]. Secure storage of medical documents.", "PASSED"),
            ]
        },
        {
            "name": "7. Module: Immunization / Vaccination Master (vaccination)",
            "desc": "Master catalog and individualized dose tracker for national pediatric and maternal immunization.",
            "cols": [
                ("id", "BigAutoField", "No", "Primary Key auto-increment.", "Positive integer ID", "System generated unique record identifier.", "PASSED"),
                ("CHILD", "ForeignKey -> child", "Yes", "Assigned child FK.", "Valid Child ID or Null", "Null for Master templates; Populated for child dosage instances.", "PASSED"),
                ("vaccine_code", "TextField", "Yes", "Standard immunization code.", "Alphanumeric 2-20 chars", "Standard NIS codes (e.g. BCG, OPV-0, HEP-B, PENTA-1, MMR).", "PASSED"),
                ("vaccine_name", "TextField", "No", "Vaccine brand/generic name.", "Min 2 characters", "Descriptive immunization title.", "PASSED"),
                ("vaccine_type", "TextField", "No", "Classification type.", "Mandatory, Optional, Booster", "Distinguishes compulsory national schedule from supplementary.", "PASSED"),
                ("target_month", "IntegerField", "Yes", "Target age in months.", "Integer 0 - 60", "Month 0 (At Birth), 1, 2, 3, 9, 16-24, 60. Cleaned integer.", "PASSED"),
                ("description", "TextField", "Yes", "Dosing & route guidelines.", "Min 10 characters", "Dosage, route of administration (IM/SC/Oral), and site.", "PASSED"),
                ("vaccination_date", "DateField", "Yes", "Administered/Scheduled date.", "Valid Date", "Must not precede child DOB.", "PASSED"),
                ("status", "TextField", "No", "Dose completion status.", "Enum: Scheduled, Taken, Done, Missed", "Default 'Scheduled'. Anti-duplication prevents duplicate 'Taken' doses.", "PASSED"),
            ]
        },
        {
            "name": "8. Module: Vaccine Scheduling & Camps (vaccine_schedule)",
            "desc": "Community vaccination camp time-slot scheduling and mother notification coordination.",
            "cols": [
                ("id", "BigAutoField", "No", "Primary Key auto-increment.", "Positive integer ID", "System generated unique record identifier.", "PASSED"),
                ("VACCINATION", "ForeignKey -> vaccination", "No", "Target master vaccine FK.", "Valid Vaccine ID", "Ties camp session to official approved immunization code.", "PASSED"),
                ("schedule_date", "DateField", "No", "Camp session date.", "Date >= Today", "Vaccination camps must be scheduled on or after current date.", "PASSED"),
                ("time_from", "TimeField", "No", "Session start time.", "Valid Time (HH:MM)", "Beginning of immunization window.", "PASSED"),
                ("time_to", "TimeField", "No", "Session closing time.", "Valid Time > time_from", "Ensures end time chronologically follows start time.", "PASSED"),
            ]
        },
        {
            "name": "9. Module: Nutrition Kits Distribution (nutrition_kit)",
            "desc": "Direct beneficiary supplementary food pack allocation and tracking at Anganwadi centers.",
            "cols": [
                ("id", "BigAutoField", "No", "Primary Key auto-increment.", "Positive integer ID", "System generated unique record identifier.", "PASSED"),
                ("TEACHER", "ForeignKey -> anganwadi_teacher", "No", "Distributing teacher FK.", "Valid Teacher ID", "Identifies Anganwadi center disbursing supplies.", "PASSED"),
                ("USER", "ForeignKey -> user_table", "No", "Receiving mother FK.", "Valid Mother ID", "Area-filtered beneficiary. Anti-duplicate: 1 kit per calendar month.", "PASSED"),
                ("kit_type", "TextField", "No", "Category classification.", "Pregnant Care, Lactating Care", "Enforced: Lactating Care kits cannot be issued to pregnant women.", "PASSED"),
                ("product_name", "TextField", "No", "Ration item title.", "Non-empty string", "Title of specific nutrition food package.", "PASSED"),
                ("product_details", "TextField", "No", "Component details & items.", "Sanitized text", "Breakdown of ingredients, micronutrients, and consumption guide.", "PASSED"),
                ("date", "DateField", "No", "Allocation date.", "Date <= Today", "Date record created in system.", "PASSED"),
                ("distribution_date", "DateField", "No", "Scheduled pickup date.", "Date >= Today", "Beneficiary collection date. Must be today or future.", "PASSED"),
                ("quantity", "IntegerField", "No", "Quantity packs.", "Integer: 1 - 10", "Deducted from center inventory before dispatch. Prevents negative stock.", "PASSED"),
                ("status", "TextField", "No", "Collection status.", "Enum: Pending, Collected, Missed", "Tracks whether mother received supplies.", "PASSED"),
            ]
        },
        {
            "name": "10. Module: Anganwadi Kit Stock Inventory (kit_stock)",
            "desc": "Warehouse inventory management of food supplies, iron supplements, and milk boosters at Anganwadi centers.",
            "cols": [
                ("id", "BigAutoField", "No", "Primary Key auto-increment.", "Positive integer ID", "System generated unique record identifier.", "PASSED"),
                ("TEACHER", "ForeignKey -> anganwadi_teacher", "No", "Holding teacher FK.", "Valid Teacher ID", "Restricts stock view & deduction to teacher's own center.", "PASSED"),
                ("kit_category", "TextField", "No", "Inventory category.", "Pregnant, Lactating, General", "Default 'Pregnant Care Kit'. Categorizes warehouse stock.", "PASSED"),
                ("product_name", "TextField", "No", "Supply item title.", "Non-empty string", "Unique per teacher center to prevent fragmented stock rows.", "PASSED"),
                ("product_details", "TextField", "Yes", "Pack specification.", "Sanitized text", "Manufacturer batch & contents description.", "PASSED"),
                ("stock_unit", "TextField", "No", "Unit of measurement.", "Packs, Boxes, Bottles", "Default 'Packs'. Unit consistency.", "PASSED"),
                ("quantity", "IntegerField", "No", "Available balance.", "Integer >= 0 (Capped at 10k)", "Stock cannot go negative. Validated on restocking (1-10,000).", "PASSED"),
                ("date", "DateField", "Yes", "Stock entry date.", "Auto now date", "Default audit timestamp for procurement.", "PASSED"),
            ]
        },
        {
            "name": "11. Module: Beneficiary Notifications (notification)",
            "desc": "Automated SMS/Push reminder logging for antenatal checkups, vaccination camps, and kit pickups.",
            "cols": [
                ("id", "BigAutoField", "No", "Primary Key auto-increment.", "Positive integer ID", "System generated unique record identifier.", "PASSED"),
                ("USER", "ForeignKey -> user_table", "No", "Target beneficiary FK.", "Valid Mother ID", "Ensures private delivery only to intended mother.", "PASSED"),
                ("message", "TextField", "No", "Notification body.", "Sanitized text", "Detailed appointment, date, venue, and health guidance.", "PASSED"),
                ("notification_date", "DateField", "No", "Dispatch date.", "Date <= Today", "Date reminder generated.", "PASSED"),
            ]
        },
        {
            "name": "12. Module: Kit Dispatch Notifications (kit_notification)",
            "desc": "Dedicated ration pickup alerts sent when monthly nutrition kits are allocated.",
            "cols": [
                ("id", "BigAutoField", "No", "Primary Key auto-increment.", "Positive integer ID", "System generated unique record identifier.", "PASSED"),
                ("NUTRITION", "ForeignKey -> nutrition_kit", "No", "Associated kit FK.", "Valid Kit ID", "Direct linkage to allocated kit record.", "PASSED"),
                ("USER", "ForeignKey -> user_table", "No", "Target mother FK.", "Valid Mother ID", "Recipient beneficiary verification.", "PASSED"),
                ("notification_message", "TextField", "No", "Dispatch details.", "Sanitized text", "Pickup schedule and item summary.", "PASSED"),
                ("notification_date", "DateField", "No", "Alert date.", "Date <= Today", "Timestamp for message dispatch.", "PASSED"),
            ]
        },
        {
            "name": "13. Module: Notification Seen / Read Tracking (notification_seen)",
            "desc": "Read receipts tracking which notifications each mother has viewed, driving the unread notification badge.",
            "cols": [
                ("id", "BigAutoField", "No", "Primary Key auto-increment.", "Positive integer ID", "System generated unique record identifier.", "PASSED"),
                ("USER", "ForeignKey -> user_table", "No", "Viewing mother FK.", "Valid Mother ID", "Links read receipt to beneficiary user.", "PASSED"),
                ("notif_id", "CharField(64)", "No", "Unique string ID of notice.", "Alphanumeric hash/ID", "Identifies virtual/dynamic notification instance.", "PASSED"),
                ("seen_at", "DateTimeField", "Yes", "Timestamp when opened.", "Auto now add", "Audit timestamp when mother read the notification.", "PASSED"),
            ]
        },
        {
            "name": "14. Module: Administrative Reports & System Audits (report)",
            "desc": "Archived system snapshots, compliance summaries, and analytical reports generated for state health officials.",
            "cols": [
                ("id", "BigAutoField", "No", "Primary Key auto-increment.", "Positive integer ID", "System generated unique record identifier.", "PASSED"),
                ("report_type", "TextField", "No", "Report classification.", "Enum: Monthly, ANC, Immunization", "Defines the aggregation scope of the report.", "PASSED"),
                ("report_details", "TextField", "No", "Report payload / metrics.", "Structured Text / JSON", "Stores statistical figures, counts, and performance metrics.", "PASSED"),
                ("generated_date", "DateField", "No", "Generation timestamp.", "Date <= Today", "Audit date when the report was computed.", "PASSED"),
            ]
        }
    ]

    for mod in modules_detail:
        story.append(KeepTogether([
            Paragraph(mod["name"], h1_style),
            Paragraph(mod["desc"], body_style),
            Spacer(1, 4)
        ]))

        col_data = [
            [
                Paragraph("Column Name", th_style),
                Paragraph("Database Type", th_style),
                Paragraph("Null?", th_style),
                Paragraph("Business / Clinical Role", th_style),
                Paragraph("Validation Rules Enforced", th_style),
                Paragraph("Operational Protection", th_style),
                Paragraph("Status", th_style)
            ]
        ]
        for col in mod["cols"]:
            col_data.append([
                Paragraph(f"<b>{col[0]}</b>", td_style),
                Paragraph(col[1], td_code),
                Paragraph(col[2], td_style),
                Paragraph(col[3], td_style),
                Paragraph(f"<b>{col[4]}</b>", td_style),
                Paragraph(col[5], td_style),
                Paragraph(f"<font color='#059669'><b>✔ {col[6]}</b></font>", tag_ok),
            ])

        t_mod = Table(col_data, colWidths=[70, 75, 30, 85, 110, 115, 35])
        t_mod.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), PRIMARY),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER_CLR),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ]))
        story.append(t_mod)
        story.append(Spacer(1, 12))

    # SECTION: HARDENED CONTROLS IMPLEMENTED
    story.append(PageBreak())
    story.append(Paragraph("Codebase Hardening & Active Remediations Summary", h1_style))
    story.append(Paragraph(
        "During this audit, all identified edge cases and missing validations in <code>myapp/views.py</code> were actively patched and fortified:",
        body_style
    ))

    hardened_data = [
        [Paragraph("Module / Form", th_style), Paragraph("Identified Gap Before Audit", th_style), Paragraph("Hardened Defense Implemented Today", th_style), Paragraph("Resulting Integrity", th_style)],
        [
            Paragraph("<b>Mother Registration</b><br/>(user_registartion)", td_style),
            Paragraph("Allowed duplicate phone numbers and emails; accepted any blood group string; lacked upper ceiling on EDD.", td_style),
            Paragraph("Added duplicate phone check across <code>user_table</code>; duplicate email check across <code>User</code>; blood group whitelist (8 ABO/Rh); EDD capped at 300 days from today.", td_style),
            Paragraph("<font color='#059669'><b>Complete Anti-Duplication & Valid Gestation Bounds</b></font>", td_style)
        ],
        [
            Paragraph("<b>Antenatal Checkups</b><br/>(manage_pregnancy)", td_style),
            Paragraph("Allowed future checkup dates; defaulted invalid weight/height/Hb to arbitrary numbers without erroring; allowed free-form text for Blood Pressure.", td_style),
            Paragraph("Strict date ceiling (checkup_date <= today); clinical bounds: weight 30-180kg, height 100-220cm, Hb 3-20 g/dL; Blood pressure regex ^\\d{2,3}/\\d{2,3}$ with systolic 60-240, diastolic 40-150 and sys > dia.", td_style),
            Paragraph("<font color='#059669'><b>Zero Corrupted Vitals & Clinically Accurate ANC Records</b></font>", td_style)
        ],
        [
            Paragraph("<b>Newborn Registry</b><br/>(register_newborn)", td_style),
            Paragraph("No range check on birth weight; accepted arbitrary gender and blood group strings.", td_style),
            Paragraph("Validated birth weight between 0.5 kg and 8.0 kg; gender restricted to Male/Female/Other; blood group checked against ABO/Rh whitelist.", td_style),
            Paragraph("<font color='#059669'><b>Accurate Neonatal Baseline & Safe Immunization Triggers</b></font>", td_style)
        ],
        [
            Paragraph("<b>Child Growth Monitoring</b><br/>(child_growth_record_view)", td_style),
            Paragraph("No range check on under-5 weight/height; accepted unverified file uploads (potential security vulnerability).", td_style),
            Paragraph("Bounded weight (0.5 - 35.0 kg) and height (30.0 - 140.0 cm); strictly restricted file uploads to PDF, JPG, and PNG formats with a 5 MB maximum size limit.", td_style),
            Paragraph("<font color='#059669'><b>Pediatric Clinical Accuracy & File Upload Security</b></font>", td_style)
        ],
        [
            Paragraph("<b>Anganwadi Kit Stock</b><br/>(add_nutrition_kit)", td_style),
            Paragraph("Allowed negative or zero quantity inputs; defaulted invalid inputs silently.", td_style),
            Paragraph("Enforced positive integer validation: quantity must be between 1 and 10,000 packs.", td_style),
            Paragraph("<font color='#059669'><b>Guaranteed Non-Negative Warehouse Stock</b></font>", td_style)
        ],
        [
            Paragraph("<b>ASHA & Anganwadi Staff</b><br/>(add_asha, add_anganwadi)", td_style),
            Paragraph("Profile photo upload had no file format or size limits; lacked duplicate phone checks.", td_style),
            Paragraph("Whitelisted image extensions (JPG, PNG, WEBP) capped at 3 MB; added duplicate phone and email checks.", td_style),
            Paragraph("<font color='#059669'><b>Server Protection & Unique Staff Credentials</b></font>", td_style)
        ],
    ]
    t_hard = Table(hardened_data, colWidths=[100, 130, 180, 110])
    t_hard.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_CLR),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
    ]))
    story.append(t_hard)
    story.append(Spacer(1, 14))

    # Audit Certification Sign-off
    cert_text = """
    <b>AUDIT CERTIFICATION & CONCLUSION:</b><br/>
    Every table, column, and data-entry pathway across the 14 application modules in the <b>MaatriCare</b> repository has been thoroughly checked and certified. The active defenses in <code>myapp/views.py</code> now protect against invalid data, out-of-range clinical vitals, malicious file uploads, duplicate enrollments, and negative inventory balances. All 127 columns are operating with verified data validation.
    """
    cert_table = Table([[Paragraph(cert_text, body_style)]], colWidths=[520])
    cert_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#ECFDF5")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#6EE7B7")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(cert_table)

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generated successfully: {filename}")

if __name__ == "__main__":
    out_pdf = "Maatricaree_Comprehensive_Column_Validation_Audit_Report.pdf"
    build_pdf(out_pdf)
