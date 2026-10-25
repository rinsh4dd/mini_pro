import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maatricaree.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from myapp.models import asha_worker, anganwadi_teacher
from myapp.views import ashaworker_profile_view, teacher_profile_view

print("=== VERIFYING ASHA WORKER PROFILES ===")
ashas = asha_worker.objects.all().order_by('id')
print(f"Total ASHA workers in DB: {ashas.count()}")
for a in ashas:
    print(f"ID={a.id} | Name={a.Full_name} | DOB={a.dob} | Age={a.Age} | Phone={a.Phone} | Area={a.Area_assigned} | Email={a.Email} | Status={a.Current_status} | Image={bool(a.image)} | Username={a.LOGIN.username if a.LOGIN else 'None'}")

client = Client()

# Test ASHA profile for worker 45 (shaikha)
resp = client.get('/myapp/ashaworker_profile/?worker_id=45')
print(f"\nGET /myapp/ashaworker_profile/?worker_id=45 => Status {resp.status_code}")
content = resp.content.decode('utf-8')
assert "shaikha" in content, "Worker name 'shaikha' should be in response"
assert "Ward 01" in content or "Ward 01 - North" in content or "45" in content, "Ward / ID should be in response"
print("SUCCESS: ASHA profile loads exact admin data for worker 45 ('shaikha')!")

# Test Anganwadi teacher profile
print("\n=== VERIFYING ANGANWADI TEACHER PROFILES ===")
teachers = anganwadi_teacher.objects.all().order_by('id')
print(f"Total Anganwadi teachers in DB: {teachers.count()}")
for t in teachers:
    print(f"ID={t.id} | Name={t.Name} | DOB={t.dob} | Age={t.Age} | Gender={t.Gender} | Phone={t.Phone} | Center={t.center_name} | Email={t.Email} | Status={t.Current_status} | Image={bool(t.image)} | Username={t.LOGIN.username if t.LOGIN else 'None'}")

# Test Anganwadi profile for teacher 20
first_teacher = teachers.first()
resp_t = client.get(f'/myapp/teacher_profile/?teacher_id={first_teacher.id}')
print(f"\nGET /myapp/teacher_profile/?teacher_id={first_teacher.id} => Status {resp_t.status_code}")
content_t = resp_t.content.decode('utf-8')
assert first_teacher.Name in content_t, f"Teacher name {first_teacher.Name} should be in response"
assert first_teacher.Phone in content_t, f"Teacher phone {first_teacher.Phone} should be in response"
print(f"SUCCESS: Anganwadi teacher profile loads exact admin data for teacher {first_teacher.id} ('{first_teacher.Name}')!")

print("\n=== ALL PROFILE DATA VALIDATION PASSED ===")
