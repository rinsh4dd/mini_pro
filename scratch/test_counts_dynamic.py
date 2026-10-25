import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maatricaree.settings')
django.setup()

from django.db import transaction
from django.contrib.auth.models import User
from myapp.models import (
    user_table, asha_worker, anganwadi_teacher,
    pregnancy_record, child, child_growth_record,
    vaccination, nutrition_kit, kit_stock
)

print("=" * 60)
print("TESTING DYNAMIC COUNT INCREMENTS AND DECREMENTS")
print("=" * 60)

with transaction.atomic():
    # 1. Mother Count Test
    initial_mothers = user_table.objects.count()
    test_user = User.objects.create_user(username='test_count_mother', password='Password123')
    test_mother = user_table.objects.create(
        LOGIN=test_user,
        name='Test Mother Count',
        husband_name='Test Husband',
        age=24,
        dob='2000-01-01',
        blood_group='O+',
        phone=9998887771,
        Email='testmothercount@example.com',
        Address='Ward 01 Test House',
        panchayath='Kozhikode',
        area='Ward 01 - Main Community Center',
        district='Kozhikode',
        state='Kerala',
        pincode='673001',
        expected_delivery_date='2027-01-01'
    )
    after_add_mothers = user_table.objects.count()
    print(f"Mother Count: Initial = {initial_mothers} -> After Add = {after_add_mothers} (Diff = {after_add_mothers - initial_mothers})")
    assert after_add_mothers == initial_mothers + 1, "Mother count did not increase by 1!"

    # 2. Child Count Test
    initial_children = child.objects.count()
    test_child = child.objects.create(
        USER=test_mother,
        ASHA=asha_worker.objects.first() or asha_worker.objects.create(
            LOGIN=User.objects.create_user(username='test_asha_w', password='pw'),
            Full_name='Test Asha', Age=30, Qualification='BSc', Email='testasha@ex.com',
            Address='Test', Area_assigned='Ward 01 - Main Community Center', Phone=9876543210, Joining_date='2020-01-01'
        ),
        child_name='Baby Test Count',
        gender='Female',
        date_of_birth='2026-05-01',
        birth_weight=3.2,
        birth_height=50.0,
        blood_group='O+',
        place_of_birth='CHC Hospital',
        delivery_type='Normal',
        health_status='Healthy'
    )
    after_add_children = child.objects.count()
    print(f"Child Count: Initial = {initial_children} -> After Add = {after_add_children} (Diff = {after_add_children - initial_children})")
    assert after_add_children == initial_children + 1, "Child count did not increase by 1!"

    # 3. Growth Record Count Test
    initial_growth = child_growth_record.objects.count()
    test_growth = child_growth_record.objects.create(
        CHILD=test_child,
        height=55.0,
        weight=4.1,
        growth_date='2026-06-01',
        health_condition='Normal',
        report_details='Month 1 checkup'
    )
    after_add_growth = child_growth_record.objects.count()
    print(f"Growth Record Count: Initial = {initial_growth} -> After Add = {after_add_growth} (Diff = {after_add_growth - initial_growth})")
    assert after_add_growth == initial_growth + 1, "Growth count did not increase by 1!"

    # 4. Vaccination Count Test
    initial_vax = vaccination.objects.count()
    test_vax = vaccination.objects.create(
        CHILD=test_child,
        vaccine_name='BCG Test',
        vaccine_type='Mandatory',
        target_month=0,
        status='Scheduled'
    )
    after_add_vax = vaccination.objects.count()
    print(f"Vaccination Count: Initial = {initial_vax} -> After Add = {after_add_vax} (Diff = {after_add_vax - initial_vax})")
    assert after_add_vax == initial_vax + 1, "Vaccination count did not increase by 1!"

    # 5. Pregnancy Record Count Test
    initial_preg = pregnancy_record.objects.count()
    test_preg = pregnancy_record.objects.create(
        USER=test_mother,
        ASHA=test_child.ASHA,
        previous_pregnency_count=0,
        expected_delivery_date='2027-01-01',
        checkup_date='2026-06-01',
        weight=60.0,
        height=160.0,
        blood_pressure='120/80',
        hemoglobin=12.0,
        health_status='Normal',
        additional_report='All vitals normal',
        next_checkup_date='2026-07-01'
    )
    after_add_preg = pregnancy_record.objects.count()
    print(f"Pregnancy Record Count: Initial = {initial_preg} -> After Add = {after_add_preg} (Diff = {after_add_preg - initial_preg})")
    assert after_add_preg == initial_preg + 1, "Pregnancy record count did not increase by 1!"

    # NOW TEST DELETIONS AND DECREMENTS:
    test_growth.delete()
    after_del_growth = child_growth_record.objects.count()
    print(f"Growth Record Count After Delete: {after_del_growth} (Matches initial = {after_del_growth == initial_growth})")
    assert after_del_growth == initial_growth, "Growth count did not decrease by 1!"

    test_vax.delete()
    after_del_vax = vaccination.objects.count()
    print(f"Vaccination Count After Delete: {after_del_vax} (Matches initial = {after_del_vax == initial_vax})")
    assert after_del_vax == initial_vax, "Vaccination count did not decrease by 1!"

    test_preg.delete()
    after_del_preg = pregnancy_record.objects.count()
    print(f"Pregnancy Record Count After Delete: {after_del_preg} (Matches initial = {after_del_preg == initial_preg})")
    assert after_del_preg == initial_preg, "Pregnancy count did not decrease by 1!"

    test_child.delete()
    after_del_child = child.objects.count()
    print(f"Child Count After Delete: {after_del_child} (Matches initial = {after_del_child == initial_children})")
    assert after_del_child == initial_children, "Child count did not decrease by 1!"

    test_mother.delete()
    test_user.delete()
    after_del_mother = user_table.objects.count()
    print(f"Mother Count After Delete: {after_del_mother} (Matches initial = {after_del_mother == initial_mothers})")
    assert after_del_mother == initial_mothers, "Mother count did not decrease by 1!"

    print("\nALL COUNTS PROVED: Increments on Addition, Decrements on Deletion perfectly!")
    # Rollback transaction so DB remains untouched
    transaction.set_rollback(True)

print("Test finished and database rolled back clean.")
