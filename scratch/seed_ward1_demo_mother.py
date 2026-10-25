import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maatricaree.settings')
django.setup()

from django.contrib.auth.models import User, Group
from myapp.models import (
    user_table, asha_worker, anganwadi_teacher,
    pregnancy_record, child, child_growth_record, vaccination,
    nutrition_kit, kit_notification, notification, notification_seen
)

def seed_ward1_demo_mother():
    print("--- Seeding Demo Mother for Ward 01 ---")

    username = "ward1mother"
    raw_password = "Mother@123"
    email = "amina.ward1@example.com"
    phone_int = 9876543210

    # 1. Clean existing records if any
    existing_user = User.objects.filter(username=username).first()
    if existing_user:
        print(f"Removing pre-existing user '{username}' and related records...")
        user_table.objects.filter(LOGIN=existing_user).delete()
        existing_user.delete()

    # 2. Get Ward 01 ASHA Worker & Anganwadi Teacher
    ward1_asha = asha_worker.objects.filter(Area_assigned__icontains="Ward 01").first()
    if not ward1_asha:
        ward1_asha = asha_worker.objects.first()
    print(f"Assigning ASHA Worker: {ward1_asha.Full_name} ({ward1_asha.Area_assigned})")

    ward1_teacher = anganwadi_teacher.objects.filter(center_name__icontains="01").first()
    if not ward1_teacher:
        ward1_teacher = anganwadi_teacher.objects.first()
    print(f"Assigning Anganwadi Teacher: {ward1_teacher.Name} ({ward1_teacher.center_name})")

    # 3. Create User Account
    user_group, _ = Group.objects.get_or_create(name="user")
    user = User.objects.create_user(
        username=username,
        email=email,
        password=raw_password,
        first_name="Amina",
        last_name="Rahmath"
    )
    user.groups.add(user_group)

    # 4. Create Mother Profile (Currently in 7th Month of pregnancy, Week 29, EDD Dec 14, 2026)
    today = date(2026, 9, 28)
    edd_current = date(2026, 12, 14) # ~77 days left -> ~203 gest days -> Week 29 / Month 7

    mother = user_table.objects.create(
        LOGIN=user,
        ASHA=ward1_asha,
        name="Amina Rahmath",
        husband_name="Rahmathullah K",
        age=26,
        dob=date(2000, 4, 15),
        blood_group="O+",
        phone=phone_int,
        Email=email,
        Address="House #12/480, Near Community Hall, Ward 1, Kozhikode",
        panchayath="Kozhikode Grama Panchayath",
        area="Ward 01 - Main Community Center",
        district="Kozhikode",
        state="Kerala",
        pincode="673001",
        expected_delivery_date=edd_current,
    )
    print(f"Created Mother: {mother.name} (ID: {mother.id}) in {mother.area}")

    # 5. PREVIOUS PREGNANCY: 9 Months of Checkup Records (Baby born August 15, 2024)
    # First pregnancy EDD was 2024-08-18
    first_edd = date(2024, 8, 18)
    first_preg_data = [
        (date(2023, 12, 15), 52.0, 158.0, "118/76", 12.2, "Normal", "Conception confirmed. Routine antenatal screening normal.", date(2024, 1, 15)),
        (date(2024, 1, 15), 53.0, 158.0, "120/78", 12.0, "Normal", "Dating ultrasound confirms single viable intrauterine pregnancy.", date(2024, 2, 15)),
        (date(2024, 2, 15), 54.5, 158.0, "120/80", 11.8, "Normal", "Nuchal translucency and first trimester biochemistry normal.", date(2024, 3, 15)),
        (date(2024, 3, 15), 56.0, 158.0, "118/78", 11.9, "Normal", "Fetal quickening perceived. Iron-folic acid compliance good.", date(2024, 4, 15)),
        (date(2024, 4, 15), 58.0, 158.0, "122/80", 12.1, "Normal", "Anomaly scan (TIFFA) completed. Normal fetal anatomy.", date(2024, 5, 15)),
        (date(2024, 5, 15), 60.0, 158.0, "120/80", 11.7, "Normal", "Fetal movements regular. Oral glucose tolerance test normal.", date(2024, 6, 15)),
        (date(2024, 6, 15), 62.0, 158.0, "124/82", 11.5, "Normal", "Fundal height matches dates. Td-1 toxoid administered.", date(2024, 7, 15)),
        (date(2024, 7, 15), 64.0, 158.0, "122/80", 11.8, "Normal", "Cephalic presentation confirmed. Growth scan adequate.", date(2024, 8, 5)),
        (date(2024, 8, 5), 66.0, 158.0, "120/80", 12.0, "Normal", "Term maturity reached. Non-stress test reactive. Hospital admission plan prepared.", date(2024, 8, 18)),
    ]

    for chk_date, wt, ht, bp, hb, stat, notes, next_dt in first_preg_data:
        pregnancy_record.objects.create(
            USER=mother,
            ASHA=ward1_asha,
            previous_pregnency_count=0,
            expected_delivery_date=first_edd,
            checkup_date=chk_date,
            weight=wt,
            height=ht,
            blood_pressure=bp,
            hemoglobin=hb,
            health_status=stat,
            additional_report=notes,
            next_checkup_date=next_dt
        )
    print(f"Created {len(first_preg_data)} monthly checkup records for 1st pregnancy.")

    # 6. REGISTER DELIVERED CHILD (Born August 15, 2024 ~ 2 years old)
    ch = child.objects.create(
        USER=mother,
        ASHA=ward1_asha,
        child_name="Aarav Krishna",
        gender="Male",
        date_of_birth=date(2024, 8, 15),
        birth_weight=3.2,
        birth_height=49.5,
        blood_group="O+",
        place_of_birth="Govt Taluk Hospital, Kozhikode",
        delivery_type="Normal Delivery",
        hospital="Govt Taluk Hospital",
        health_status="Healthy & Thriving"
    )
    print(f"Created Child: {ch.child_name} (DOB: {ch.date_of_birth})")

    # 7. CHILD GROWTH RECORDS TILL 1 YEAR
    growth_data = [
        (date(2024, 8, 15), 3.2, 49.5, "Healthy", "Normal neonatal APGAR 9/10, active crying [At Birth]"),
        (date(2024, 9, 15), 4.1, 53.0, "Normal", "Exclusive breastfeeding established, weight gain 900g [Month 1]"),
        (date(2024, 10, 15), 5.0, 56.5, "Normal", "Social smile present, follows objects visually [Month 2]"),
        (date(2024, 11, 15), 5.8, 59.5, "Normal", "Holds head steady, cooing and vocalizing happily [Month 3]"),
        (date(2025, 2, 15), 7.3, 66.0, "Normal", "Sitting with support, reaching for colorful toys [Month 6]"),
        (date(2025, 5, 15), 8.6, 71.0, "Normal", "Crawling actively on floor, responsive to name [Month 9]"),
        (date(2025, 8, 15), 9.8, 75.5, "Normal", "1-Year milestone: Standing independently, first words spoken [Month 12]")
    ]

    for g_date, wt, ht, cond, rep in growth_data:
        child_growth_record.objects.create(
            CHILD=ch,
            height=ht,
            weight=wt,
            growth_date=g_date,
            health_condition=cond,
            report_details=rep
        )
    print(f"Created {len(growth_data)} child growth records up to 1 year.")

    # 8. ALL VACCINATIONS TAKEN DETAILS TILL 1 YEAR
    vaxes = [
        ("BCG", "VAC-003", "Bacterial Vaccine", 0, "Tuberculosis protection at birth", date(2024, 8, 15), "Taken"),
        ("Oral Polio Vaccine (OPV-0)", "VAC-OPV", "Viral Oral Vaccine", 0, "Polio birth dose given in labor room", date(2024, 8, 15), "Taken"),
        ("Hepatitis B Birth Dose", "VAC-HEPB", "Recombinant Vaccine", 0, "Hep B vaccine within 24 hours of birth", date(2024, 8, 15), "Taken"),
        ("Pentavalent-1", "VAC-002", "Inactivated Combined", 1, "DPT, Hep B, Hib 1st primary dose", date(2024, 9, 26), "Taken"),
        ("Oral Polio Vaccine (OPV-1)", "VAC-OPV1", "Viral Oral Vaccine", 1, "OPV primary 1st dose at 6 weeks", date(2024, 9, 26), "Taken"),
        ("Rotavirus Vaccine 1", "VAC-ROTA1", "Live Attenuated Oral", 1, "Severe diarrhea protection dose 1", date(2024, 9, 26), "Taken"),
        ("Pentavalent-2", "VAC-PENTA2", "Inactivated Combined", 2, "DPT, Hep B, Hib 2nd primary dose at 10 weeks", date(2024, 10, 24), "Taken"),
        ("Oral Polio Vaccine (OPV-2)", "VAC-OPV2", "Viral Oral Vaccine", 2, "OPV primary 2nd dose at 10 weeks", date(2024, 10, 24), "Taken"),
        ("Pentavalent-3", "VAC-PENTA3", "Inactivated Combined", 3, "DPT, Hep B, Hib 3rd primary dose at 14 weeks", date(2024, 11, 21), "Taken"),
        ("Fractional IPV", "VAC-FIPV", "Inactivated Injectable", 3, "Injectable polio vaccine 1st dose", date(2024, 11, 21), "Taken"),
        ("Typhoid Conjugate Vaccine (TCV)", "VAC-TCV", "Conjugate Vaccine", 6, "Typhoid fever prevention administered at 6 months", date(2025, 2, 15), "Taken"),
        ("Measles & Rubella 1 (MR-1)", "VAC-MR1", "Live Attenuated", 9, "MR vaccine 1st dose administered at 9 months", date(2025, 5, 15), "Taken"),
        ("Vitamin A (1st Dose)", "VAC-VITA1", "Oral Supplement", 9, "100,000 IU Vitamin A oral syrup", date(2025, 5, 15), "Taken"),
        ("Japanese Encephalitis 1 (JE-1)", "VAC-JE1", "Live Attenuated", 12, "Japanese Encephalitis completed at 12 months", date(2025, 8, 15), "Taken"),
    ]

    for name, code, vtype, t_month, desc, v_date, stat in vaxes:
        vaccination.objects.create(
            CHILD=ch,
            vaccine_name=name,
            vaccine_code=code,
            vaccine_type=vtype,
            target_month=t_month,
            description=desc,
            vaccination_date=v_date,
            status=stat
        )
    print(f"Created {len(vaxes)} completed (Taken) vaccination records.")

    # 9. SECOND PREGNANCY (CURRENT): Month 1 to Month 7 Checkup Records (In 7th Month)
    # Today: 2026-09-28. EDD: 2026-12-14.
    current_preg_data = [
        (date(2026, 4, 10), 54.0, 158.0, "116/74", 12.4, "Normal", "Second pregnancy confirmed. Folic acid 5mg daily prescribed.", date(2026, 5, 12)),
        (date(2026, 5, 12), 55.2, 158.0, "118/76", 12.2, "Normal", "Dating scan confirms intrauterine viable singleton at 9 weeks.", date(2026, 6, 10)),
        (date(2026, 6, 10), 56.5, 158.0, "120/78", 12.0, "Normal", "NT scan normal (1.4mm). Maternal blood parameters optimal.", date(2026, 7, 8)),
        (date(2026, 7, 8), 58.0, 158.0, "118/78", 11.9, "Normal", "Quickening felt actively. IFA and calcium carbonate initiated.", date(2026, 8, 6)),
        (date(2026, 8, 6), 59.8, 158.0, "120/80", 12.1, "Normal", "TIFFA scan at 20 weeks shows normal anatomical development.", date(2026, 9, 2)),
        (date(2026, 9, 2), 61.5, 158.0, "122/80", 11.8, "Normal", "Gestational diabetes screening (OGTT) 112 mg/dL (Normal).", date(2026, 9, 24)),
        (date(2026, 9, 24), 63.2, 158.0, "120/80", 12.0, "Normal", "7th Month Antenatal Evaluation: Fundal height 29 cm, Fetal Heart Rate 142 bpm. Nutrition kit collection advised.", date(2026, 10, 22)),
    ]

    for chk_date, wt, ht, bp, hb, stat, notes, next_dt in current_preg_data:
        pregnancy_record.objects.create(
            USER=mother,
            ASHA=ward1_asha,
            previous_pregnency_count=1,
            expected_delivery_date=edd_current,
            checkup_date=chk_date,
            weight=wt,
            height=ht,
            blood_pressure=bp,
            hemoglobin=hb,
            health_status=stat,
            additional_report=notes,
            next_checkup_date=next_dt
        )
    print(f"Created {len(current_preg_data)} antenatal records for current pregnancy up to Month 7.")

    # 10. NUTRITION KITS & NEW KIT COLLECTION NOTIFICATION
    # Historical kits from previous pregnancy and early current pregnancy:
    nutrition_kit.objects.create(
        TEACHER=ward1_teacher,
        USER=mother,
        kit_type="Postnatal Care & Lactation Kit",
        product_name="Amrutham Nutrimix Postnatal Mother Pack",
        product_details="3kg Amrutham Nutrimix powder, Postnatal galactagogue supplement, Calcium syrup",
        date=date(2024, 9, 10),
        distribution_date=date(2024, 9, 20),
        quantity=1,
        status="Distributed"
    )
    nutrition_kit.objects.create(
        TEACHER=ward1_teacher,
        USER=mother,
        kit_type="Pregnant Care Kit - Trimester 1",
        product_name="First Trimester Mother Nutrition & Care Kit",
        product_details="Folic acid, High-protein flour mix, Multivitamin supplement",
        date=date(2026, 5, 5),
        distribution_date=date(2026, 5, 15),
        quantity=1,
        status="Distributed"
    )
    nutrition_kit.objects.create(
        TEACHER=ward1_teacher,
        USER=mother,
        kit_type="Pregnant Care Kit - Trimester 2",
        product_name="Second Trimester Amrutham Care Pack",
        product_details="Amrutham Nutrimix flour, Iron-Folic Acid tablets, Calcium carbonate",
        date=date(2026, 7, 5),
        distribution_date=date(2026, 7, 15),
        quantity=1,
        status="Distributed"
    )

    # Active NEW Kit ready for collection in 7th Month:
    new_kit = nutrition_kit.objects.create(
        TEACHER=ward1_teacher,
        USER=mother,
        kit_type="Pregnant Care Kit - Trimester 3",
        product_name="Amrutham Nutrimix & Maternal Micronutrient Care Pack (Month 7)",
        product_details="3kg Amrutham Nutrimix multigrain roasted flour, Iron-Folic Acid 100 tablets, Calcium Carbonate 500mg, High-protein nutrition supplement for third trimester fetal development.",
        date=date(2026, 9, 28),
        distribution_date=date(2026, 9, 30),
        quantity=1,
        status="Pending"
    )
    print(f"Created Active Nutrition Kit: {new_kit.product_name} (Status: {new_kit.status})")

    # Kit Notification from Anganwadi Teacher:
    kit_notif = kit_notification.objects.create(
        NUTRITION=new_kit,
        USER=mother,
        notification_message="Dear Amina Rahmath, your 3rd Trimester Nutrition Kit (Amrutham Nutrimix & Maternal Micronutrient Pack) is ready for collection at Model Anganwadi Center 01, Ward 1. Scheduled pickup date: Sep 30, 2026 between 10:00 AM and 1:00 PM. Please bring your MCP card.",
        notification_date=date(2026, 9, 28)
    )
    print(f"Created Kit Notification (ID: {kit_notif.id}): {kit_notif.notification_message[:60]}...")

    # Clear any notification_seen for this mother so it shows up as an unread notification badge & triggers popup!
    notification_seen.objects.filter(USER=mother).delete()

    print("\n==========================================")
    print("DEMO MOTHER SUCCESSFULLY CREATED & SEEDED!")
    print("==========================================")
    print(f"Name:             {mother.name}")
    print(f"Username:         {username}")
    print(f"Password:         {raw_password}")
    print(f"Ward:             {mother.area}")
    print(f"Assigned ASHA:    {ward1_asha.Full_name} (Phone: {ward1_asha.Phone})")
    print(f"Assigned Teacher: {ward1_teacher.Name} ({ward1_teacher.center_name})")
    print(f"Current Status:   Pregnant — Month 7 (Week 29, Trimester 3)")
    print(f"Due Date (EDD):   {edd_current.strftime('%b %d, %Y')}")
    print(f"1st Child:        {ch.child_name} (Born: {ch.date_of_birth.strftime('%b %d, %Y')})")
    print(f"Child Growth:     7 checkups till 1 year (Weight: 9.8 kg, Height: 75.5 cm)")
    print(f"Vaccinations:     14 doses all 'Taken'")
    print(f"New Notification: Kit ready for collection on Sep 30, 2026 (Unread)")
    print("==========================================")

if __name__ == "__main__":
    seed_ward1_demo_mother()
