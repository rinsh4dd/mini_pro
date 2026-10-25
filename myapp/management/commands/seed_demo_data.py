from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from myapp.models import asha_worker, anganwadi_teacher


class Command(BaseCommand):
    help = "Initializes essential user groups, 5 ASHA Workers, and 5 Anganwadi Teachers across all 5 Panchayath Wards."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Setting up system groups, 5 ASHA Workers, and 5 Anganwadi Teachers..."))
        setup_essential_groups()
        self.stdout.write(self.style.SUCCESS("[SUCCESS] 5 ASHA & 5 Teacher accounts setup complete."))


def setup_essential_groups():
    today = date.today()
    groups = {}
    for g_name in ['admin', 'ashaworker', 'angteacher', 'user']:
        g, _ = Group.objects.get_or_create(name=g_name)
        groups[g_name] = g

    # Admin User
    admin_user, _ = User.objects.get_or_create(username='admin')
    admin_user.set_password('admin123')
    admin_user.email = 'admin@gmail.com'
    admin_user.first_name = 'Administrative'
    admin_user.last_name = 'Officer'
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()
    admin_user.groups.add(groups['admin'])

    # 5 ASHA Worker Accounts across 5 Wards
    ashaworkers = [
        {'username': 'asha01', 'name': 'Fatima Beevi', 'phone': 9847123456, 'qual': 'B.Sc Nursing & Community Health', 'area': 'Ward 01 - Main Community Center'},
        {'username': 'asha02', 'name': 'Kavitha Nair', 'phone': 9847123458, 'qual': 'Auxiliary Nurse Midwife (ANM)', 'area': 'Ward 02 - East Sector'},
        {'username': 'asha03', 'name': 'Priya Nair', 'phone': 9847234567, 'qual': 'Diploma in Midwifery (GNM)', 'area': 'Ward 03 - West Gram'},
        {'username': 'asha04', 'name': 'Rekha Menon', 'phone': 9847345677, 'qual': 'B.Sc Community Health Sciences', 'area': 'Ward 04 - North Colony'},
        {'username': 'asha05', 'name': 'Mary Joseph', 'phone': 9847345678, 'qual': 'Auxiliary Nurse Midwife (ANM)', 'area': 'Ward 05 - South Extension'}
    ]

    for a in ashaworkers:
        u = User.objects.filter(username=a['username']).first()
        if not u:
            u = User.objects.create_user(username=a['username'], password=a['username'], email=f"{a['username']}@gmail.com")
        else:
            u.set_password(a['username'])
            u.email = f"{a['username']}@gmail.com"
        u.first_name = a['name'].split()[0]
        u.last_name = a['name'].split()[-1]
        u.save()
        u.groups.add(groups['ashaworker'])

        w, _ = asha_worker.objects.get_or_create(LOGIN=u, defaults={
            'Full_name': a['name'],
            'Age': 32,
            'Qualification': a['qual'],
            'Email': u.email,
            'Phone': a['phone'],
            'Address': f"{a['area']} Clinic",
            'Area_assigned': a['area'],
            'Joining_date': today - timedelta(days=500),
            'Current_status': 'Active'
        })
        w.Full_name = a['name']
        w.Area_assigned = a['area']
        w.Current_status = 'Active'
        w.save()

    # 5 Anganwadi Teacher Accounts across 5 Centers
    teachers = [
        {'username': 'teacher01', 'name': 'Anita Sharma', 'phone': 9847456789, 'center': 'Model Anganwadi Center 01', 'qual': 'Early Childhood Care (ECCE)'},
        {'username': 'teacher02', 'name': 'Lakshmi Menon', 'phone': 9847567890, 'center': 'Community Anganwadi Center 02', 'qual': 'Diploma in Pre-School Education'},
        {'username': 'teacher03', 'name': 'Sunitha Varghese', 'phone': 9847678901, 'center': 'West Gram Anganwadi Center 03', 'qual': 'B.Ed & ECCE Certified'},
        {'username': 'teacher04', 'name': 'Radhika Pillai', 'phone': 9847789012, 'center': 'North Colony Anganwadi Center 04', 'qual': 'Diploma in Child Psychology'},
        {'username': 'teacher05', 'name': 'Deepa Mohan', 'phone': 9847890123, 'center': 'South Extension Anganwadi Center 05', 'qual': 'Early Childhood Care (ECCE)'}
    ]

    for t in teachers:
        u = User.objects.filter(username=t['username']).first()
        if not u:
            u = User.objects.create_user(username=t['username'], password=t['username'], email=f"{t['username']}@gmail.com")
        else:
            u.set_password(t['username'])
            u.email = f"{t['username']}@gmail.com"
        u.first_name = t['name'].split()[0]
        u.last_name = t['name'].split()[-1]
        u.save()
        u.groups.add(groups['angteacher'])

        t_obj, _ = anganwadi_teacher.objects.get_or_create(LOGIN=u, defaults={
            'Name': t['name'],
            'Age': 35,
            'Gender': 'Female',
            'Phone': t['phone'],
            'Email': u.email,
            'Address': f"{t['center']} Center",
            'Qualification': t['qual'],
            'center_name': t['center'],
            'joining_date': today - timedelta(days=500),
            'Current_status': 'Active'
        })
        t_obj.Name = t['name']
        t_obj.center_name = t['center']
        t_obj.Current_status = 'Active'
        t_obj.save()
