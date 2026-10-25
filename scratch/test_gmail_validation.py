import os
import sys

sys.path.insert(0, os.path.abspath('.'))

import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maatricaree.settings')
django.setup()

from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from myapp.models import user_table, asha_worker, anganwadi_teacher, GMAIL_REGEX
from myapp.views import EMAIL_REGEX

def run_tests():
    print("=" * 60)
    print("STARTING GMAIL FORMAT VALIDATION TEST SUITE")
    print("=" * 60)

    # 1. Regex test
    valid_emails = [
        "john.doe@gmail.com",
        "mother123@gmail.com",
        "priya.k+tag@gmail.com",
        "asha_worker.kerala@gmail.com",
        "USER@GMAIL.COM",
    ]

    invalid_emails = [
        "user@yahoo.com",
        "test@hotmail.com",
        "admin@maatricare.org",
        "person@domain.co.in",
        "notanemail",
        "missingatsign.gmail.com",
        "user@gmail.co",
        "user@gmail.com.fake",
        "user@fakegmail.com",
        "user@gmail.net",
    ]

    print("\n--- 1. Testing Backend View EMAIL_REGEX ---")
    for email in valid_emails:
        match = re.match(EMAIL_REGEX, email, re.IGNORECASE)
        assert match is not None, f"Expected {email} to match EMAIL_REGEX"
        print(f" [PASS] Valid email accepted: {email}")

    for email in invalid_emails:
        match = re.match(EMAIL_REGEX, email, re.IGNORECASE)
        assert match is None, f"Expected {email} to REJECT by EMAIL_REGEX"
        print(f" [PASS] Invalid email rejected: {email}")

    print("\n--- 2. Testing Model Clean Method Validation ---")
    # Test user_table
    mother = user_table(
        name="Test Mother",
        husband_name="Husband",
        age=24,
        dob="2000-01-01",
        blood_group="O+",
        phone=9876543210,
        Email="invalid@yahoo.com",
        Address="Test Address",
        panchayath="Test Panchayath",
        district="Kozhikode",
        state="Kerala",
        pincode="673001"
    )

    try:
        mother.clean()
        raise AssertionError("user_table.clean() should have raised ValidationError for non-gmail address!")
    except ValidationError as e:
        print(f" [PASS] user_table rejected 'invalid@yahoo.com' with: {e.message_dict['Email']}")

    mother.Email = "valid.mother@gmail.com"
    mother.clean()
    print(f" [PASS] user_table accepted 'valid.mother@gmail.com' successfully")

    # Test asha_worker
    worker = asha_worker(
        Full_name="Test Worker",
        Age=30,
        Qualification="ANM",
        Email="worker@outlook.com",
        Address="Test Address",
        Phone=9876543211,
        Joining_date="2020-01-01"
    )
    try:
        worker.clean()
        raise AssertionError("asha_worker.clean() should have raised ValidationError for non-gmail address!")
    except ValidationError as e:
        print(f" [PASS] asha_worker rejected 'worker@outlook.com' with: {e.message_dict['Email']}")

    worker.Email = "valid.asha@gmail.com"
    worker.clean()
    print(f" [PASS] asha_worker accepted 'valid.asha@gmail.com' successfully")

    # Test anganwadi_teacher
    teacher = anganwadi_teacher(
        Name="Test Teacher",
        Age=32,
        Gender="Female",
        Phone=9876543212,
        Email="teacher@school.org",
        Address="Test Address",
        Qualification="ECCE",
        center_name="Center 1",
        joining_date="2020-01-01"
    )
    try:
        teacher.clean()
        raise AssertionError("anganwadi_teacher.clean() should have raised ValidationError for non-gmail address!")
    except ValidationError as e:
        print(f" [PASS] anganwadi_teacher rejected 'teacher@school.org' with: {e.message_dict['Email']}")

    teacher.Email = "valid.teacher@gmail.com"
    teacher.clean()
    print(f" [PASS] anganwadi_teacher accepted 'valid.teacher@gmail.com' successfully")

    print("\n--- 3. Verifying All Existing Database Emails ---")
    all_users = User.objects.all()
    non_gmail_users = [u.email for u in all_users if u.email and not u.email.lower().endswith("@gmail.com")]
    assert len(non_gmail_users) == 0, f"Found non-gmail users: {non_gmail_users}"
    print(f" [PASS] All {all_users.count()} Auth User emails are strictly @gmail.com")

    all_ashas = asha_worker.objects.all()
    non_gmail_ashas = [a.Email for a in all_ashas if a.Email and not a.Email.lower().endswith("@gmail.com")]
    assert len(non_gmail_ashas) == 0, f"Found non-gmail ashas: {non_gmail_ashas}"
    print(f" [PASS] All {all_ashas.count()} ASHA worker emails are strictly @gmail.com")

    all_teachers = anganwadi_teacher.objects.all()
    non_gmail_teachers = [t.Email for t in all_teachers if t.Email and not t.Email.lower().endswith("@gmail.com")]
    assert len(non_gmail_teachers) == 0, f"Found non-gmail teachers: {non_gmail_teachers}"
    print(f" [PASS] All {all_teachers.count()} Anganwadi teacher emails are strictly @gmail.com")

    all_mothers = user_table.objects.all()
    non_gmail_mothers = [m.Email for m in all_mothers if m.Email and not m.Email.lower().endswith("@gmail.com")]
    assert len(non_gmail_mothers) == 0, f"Found non-gmail mothers: {non_gmail_mothers}"
    print(f" [PASS] All {all_mothers.count()} Mother emails are strictly @gmail.com")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY! EMAIL IS 100% STRICT @gmail.com FORMAT.")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()
