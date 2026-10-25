import os
import io
import re
import csv
import json
from datetime import datetime, date, timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User, Group
from django.core.files.storage import FileSystemStorage
from django.db.models import Q, Count, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from myapp.models import user_table, asha_worker, anganwadi_teacher, vaccination, pregnancy_record, child, child_growth_record, nutrition_kit, kit_stock, kit_notification, notification, vaccine_schedule, notification_seen

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'
PHONE_REGEX = r'^[6-9]\d{9}$'
PINCODE_REGEX = r'^[1-9]\d{5}$'

# Standard 5 designated areas per Panchayath
PANCHAYATH_AREAS = [
    "Ward 01 - Main Community Center",
    "Ward 02 - East Sector",
    "Ward 03 - West Gram",
    "Ward 04 - North Colony",
    "Ward 05 - South Extension"
]


def extract_ward_number(assigned_area):
    """
    Extracts the integer ward number (1..5) from an ASHA worker's assigned area or Anganwadi teacher's center name/address.
    """
    if not assigned_area:
        return None
    text = str(assigned_area).strip()
    # 1. Match 'Ward 01', 'Ward 1', 'Center 01', 'Center 1', 'Ward 02', etc.
    m = re.search(r'(?:ward|center)\s*0?(\d+)', text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    # 2. Sector keywords
    tl = text.lower()
    if 'main' in tl:
        return 1
    elif 'east' in tl:
        return 2
    elif 'west' in tl:
        return 3
    elif 'north' in tl:
        return 4
    elif 'south' in tl:
        return 5
    # 3. Match standalone digits 1 to 99
    m = re.search(r'\b0?([1-9]\d?)\b', text)
    if m:
        return int(m.group(1))
    return None


def get_area_filter_q(assigned_area):
    """
    Constructs a Q-filter to strictly match mothers belonging to an ASHA worker's or Anganwadi Teacher's assigned ward.
    Ensures strict ward-level data isolation so workers/teachers see beneficiaries ONLY from their exact ward.
    """
    if not assigned_area:
        return Q()

    ward_num = extract_ward_number(assigned_area)
    if ward_num is not None:
        q_object = (
            Q(area__icontains=f"Ward 0{ward_num}") |
            Q(area__icontains=f"Ward {ward_num}") |
            Q(panchayath__icontains=f"Ward 0{ward_num}") |
            Q(panchayath__icontains=f"Ward {ward_num}")
        )
        if 1 <= ward_num <= len(PANCHAYATH_AREAS):
            canonical = PANCHAYATH_AREAS[ward_num - 1]
            q_object |= Q(area__iexact=canonical)
        return q_object

    # Fallback to exact or clean containment if no ward number could be extracted
    assigned_clean = str(assigned_area).strip()
    return Q(area__iexact=assigned_clean) | Q(area__icontains=assigned_clean)



def home(request):
    return render(request, 'index.html')


def logins(request):
    return render(request, 'login.html')


def login_post(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username and not password:
            messages.warning(request, "Please enter your username/email and password.")
            return render(request, 'login.html')

        if not username:
            messages.warning(request, "Please enter your username or email.")
            return render(request, 'login.html', {'prefill_username': username})

        if not password:
            messages.warning(request, "Please enter your password.")
            return render(request, 'login.html', {'prefill_username': username})

        # Support login by both Username and Email address
        resolved_username = username
        candidate_user = User.objects.filter(username__iexact=username).first()
        if not candidate_user:
            candidate_user = User.objects.filter(email__iexact=username).first()
        if not candidate_user:
            m = user_table.objects.filter(Email__iexact=username).first()
            w = asha_worker.objects.filter(Email__iexact=username).first()
            t = anganwadi_teacher.objects.filter(Email__iexact=username).first()
            candidate_user = (m.LOGIN if m and m.LOGIN else None) or (w.LOGIN if w and w.LOGIN else None) or (t.LOGIN if t and t.LOGIN else None)

        if candidate_user:
            resolved_username = candidate_user.username

        user = authenticate(request, username=resolved_username, password=password)
        if user is not None:
            if user.groups.filter(name="admin").exists() or user.is_staff or user.is_superuser:
                login(request, user)
                return redirect("/myapp/adminhome/")
            elif user.groups.filter(name="angteacher").exists():
                login(request, user)
                t = anganwadi_teacher.objects.filter(LOGIN=user).first()
                if t:
                    request.session['teacher_id'] = t.id
                return redirect('/myapp/teacher_home/')
            elif user.groups.filter(name="ashaworker").exists():
                login(request, user)
                w = asha_worker.objects.filter(LOGIN=user).first()
                if w:
                    request.session['asha_id'] = w.id
                return redirect('/myapp/ashaworker_home/')
            elif user.groups.filter(name="user").exists() or user_table.objects.filter(LOGIN=user).exists():
                mother = user_table.objects.filter(LOGIN=user).first()
                if mother and mother.ASHA is None:
                    messages.warning(
                        request,
                        "Verification Pending: Your account registration is awaiting verification by your local ASHA Healthcare Worker. You will be able to log in once your account has been verified."
                    )
                    return render(request, 'login.html', {'prefill_username': username})
                login(request, user)
                request.session['login_notification_popup'] = True
                request.session['notif_popup_dismissed_session'] = False
                return redirect('/myapp/userhome/')
            else:
                login(request, user)
                return redirect("/myapp/adminhome/")
        else:
            messages.warning(request, "Invalid username/email or password. Please verify your credentials.")
            return render(request, 'login.html', {'prefill_username': username})
    return redirect('/myapp/logins/')


def change_password_post(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username:
            messages.warning(request, "Please enter your username or email.")
            return render(request, 'login.html', {'active_tab': 'forgot'})

        if not new_password or not confirm_password:
            messages.warning(request, "Please fill in both New Password and Confirm Password fields.")
            return render(request, 'login.html', {'active_tab': 'forgot', 'reset_username': username})

        if len(new_password) < 6:
            messages.warning(request, "Password must be at least 6 characters in length.")
            return render(request, 'login.html', {'active_tab': 'forgot', 'reset_username': username})

        if new_password != confirm_password:
            messages.warning(request, "New password and Confirm password do not match.")
            return render(request, 'login.html', {'active_tab': 'forgot', 'reset_username': username})

        user = User.objects.filter(username__iexact=username).first()
        if not user:
            user = User.objects.filter(email__iexact=username).first()
        if not user:
            m = user_table.objects.filter(Email__iexact=username).first()
            w = asha_worker.objects.filter(Email__iexact=username).first()
            t = anganwadi_teacher.objects.filter(Email__iexact=username).first()
            user = (m.LOGIN if m and m.LOGIN else None) or (w.LOGIN if w and w.LOGIN else None) or (t.LOGIN if t and t.LOGIN else None)

        if user:
            user.set_password(new_password)
            user.save()

            messages.success(request, "Password changed successfully! You can now log in with your new credentials.")
            return render(request, 'login.html', {'active_tab': 'login', 'prefill_username': user.username})
        else:
            messages.warning(request, "No registered account found with the provided username or email.")
            return render(request, 'login.html', {'active_tab': 'forgot', 'reset_username': username})

    return redirect('/myapp/logins/')


def forgot_password(request):
    if request.method == "POST":
        return change_password_post(request)
    return render(request, 'forgot_password.html')


def user_registartion(request):
    if request.method == "POST":
        form_data = {
            'name': request.POST.get('name', '').strip(),
            'husband_name': request.POST.get('husband_name', '').strip(),
            'dob': request.POST.get('dob', '').strip(),
            'age': request.POST.get('age', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'phone': request.POST.get('phone', '').strip(),
            'blood_group': request.POST.get('blood_group', '').strip(),
            'panchayath': request.POST.get('panchayath', 'Kozhikode Grama Panchayath').strip(),
            'area': request.POST.get('area', '').strip(),
            'address': request.POST.get('address', '').strip(),
            'district': request.POST.get('district', '').strip(),
            'state': request.POST.get('state', '').strip(),
            'pincode': request.POST.get('pincode', '').strip(),
            'expected_delivery_date': request.POST.get('expected_delivery_date', '').strip(),
            'username': request.POST.get('username', '').strip(),
            'password': request.POST.get('password', ''),
            'confirm_password': request.POST.get('confirm_password', ''),
        }

        # Required fields validation
        missing_fields = []
        for key in ['name', 'husband_name', 'dob', 'age', 'email', 'phone', 'blood_group', 'panchayath', 'area', 'address', 'district', 'state', 'pincode', 'username', 'password']:
            if not form_data[key]:
                missing_fields.append(key.replace('_', ' ').title())

        if missing_fields:
            messages.warning(request, f"Please fill in all required fields: {', '.join(missing_fields)}")
            return render(request, 'user/user_registartion.html', {'form': form_data, 'panchayath_areas': PANCHAYATH_AREAS})

        # Name validations
        if len(form_data['name']) < 3 or not re.match(r'^[a-zA-Z\s.]+$', form_data['name']):
            messages.warning(request, "Mother's name should contain only letters and be at least 3 characters.")
            return render(request, 'user/user_registartion.html', {'form': form_data, 'panchayath_areas': PANCHAYATH_AREAS})

        if len(form_data['husband_name']) < 3 or not re.match(r'^[a-zA-Z\s.]+$', form_data['husband_name']):
            messages.warning(request, "Husband's name should contain only letters and be at least 3 characters.")
            return render(request, 'user/user_registartion.html', {'form': form_data, 'panchayath_areas': PANCHAYATH_AREAS})

        # DOB & Age validation
        try:
            parsed_dob = datetime.strptime(form_data['dob'], '%Y-%m-%d').date()
            today = date.today()
            if parsed_dob >= today:
                messages.warning(request, "Date of birth cannot be today or in the future.")
                return render(request, 'user/user_registartion.html', {'form': form_data, 'panchayath_areas': PANCHAYATH_AREAS})

            calc_age = today.year - parsed_dob.year - ((today.month, today.day) < (parsed_dob.month, parsed_dob.day))
            if calc_age < 18:
                messages.warning(request, "Mother must be at least 18 years old to register.")
                return render(request, 'user/user_registartion.html', {'form': form_data, 'panchayath_areas': PANCHAYATH_AREAS})
        except ValueError:
            messages.warning(request, "Invalid Date of Birth format. Please select a valid date.")
            return render(request, 'user/user_registartion.html', {'form': form_data, 'panchayath_areas': PANCHAYATH_AREAS})

        # Optional EDD validation if supplied
        parsed_edd = None
        if form_data.get('expected_delivery_date'):
            try:
                parsed_edd = datetime.strptime(form_data['expected_delivery_date'], '%Y-%m-%d').date()
                if parsed_edd < date.today():
                    messages.warning(request, "Expecting Delivery Date must be today or in the future. Past dates cannot be selected.")
                    return render(request, 'user/user_registartion.html', {'form': form_data, 'panchayath_areas': PANCHAYATH_AREAS})
                if (parsed_edd - date.today()).days > 300:
                    messages.warning(request, "Expected delivery date cannot exceed 300 days (approx. 42 weeks) from today.")
                    return render(request, 'user/user_registartion.html', {'form': form_data, 'panchayath_areas': PANCHAYATH_AREAS})
            except ValueError:
                messages.warning(request, "Invalid Expecting Delivery Date format. Please select a valid date.")
                return render(request, 'user/user_registartion.html', {'form': form_data, 'panchayath_areas': PANCHAYATH_AREAS})

        # Blood group validation
        VALID_BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        if form_data['blood_group'].strip().upper() not in VALID_BLOOD_GROUPS:
            messages.warning(request, "Please select a valid blood group (A+, A-, B+, B-, AB+, AB-, O+, O-).")
            return render(request, 'user/user_registartion.html', {'form': form_data, 'panchayath_areas': PANCHAYATH_AREAS})

        try:
            age_int = int(form_data['age'])
            if age_int < 18 or age_int > 60:
                messages.warning(request, "Mother's age must be between 18 and 60 years.")
                return render(request, 'user/user_registartion.html', {'form': form_data, 'panchayath_areas': PANCHAYATH_AREAS})
        except (ValueError, TypeError):
            messages.warning(request, "Please enter a valid numeric age.")
            return render(request, 'user/user_registartion.html', {'form': form_data, 'panchayath_areas': PANCHAYATH_AREAS})

        # Email validation (strictly @gmail.com format)
        if not re.match(EMAIL_REGEX, form_data['email'], re.IGNORECASE):
            messages.warning(request, "Email address must be a valid @gmail.com address (e.g., example@gmail.com).")
            return render(request, 'user/user_registartion.html', {'form': form_data, 'panchayath_areas': PANCHAYATH_AREAS})

        # Phone validation (10 digits starting with 6-9)
        cleaned_phone = ''.join(filter(str.isdigit, form_data['phone']))
        if not re.match(PHONE_REGEX, cleaned_phone):
            messages.warning(request, "Please enter a valid 10-digit mobile number starting with 6, 7, 8, or 9.")
            return render(request, 'user/user_registartion.html', {'form': form_data, 'panchayath_areas': PANCHAYATH_AREAS})

        # Duplicate Phone check
        if user_table.objects.filter(phone=int(cleaned_phone)).exists():
            messages.warning(request, f"The phone number '{cleaned_phone}' is already registered with an existing account.")
            return render(request, 'user/user_registartion.html', {'form': form_data, 'panchayath_areas': PANCHAYATH_AREAS})

        # Duplicate Email check
        if User.objects.filter(email__iexact=form_data['email']).exists() or user_table.objects.filter(Email__iexact=form_data['email']).exists():
            messages.warning(request, f"The email address '{form_data['email']}' is already registered with another account.")
            return render(request, 'user/user_registartion.html', {'form': form_data, 'panchayath_areas': PANCHAYATH_AREAS})

        # Pincode validation
        if not re.match(PINCODE_REGEX, form_data['pincode']):
            messages.warning(request, "Please enter a valid 6-digit postal pincode.")
            return render(request, 'user/user_registartion.html', {'form': form_data, 'panchayath_areas': PANCHAYATH_AREAS})

        # Address minimum length
        if len(form_data['address']) < 5:
            messages.warning(request, "Address must be at least 5 characters long.")
            return render(request, 'user/user_registartion.html', {'form': form_data, 'panchayath_areas': PANCHAYATH_AREAS})

        # Password matching & length
        if form_data.get('confirm_password') and form_data['password'] != form_data['confirm_password']:
            messages.warning(request, "Password and Confirm Password do not match.")
            return render(request, 'user/user_registartion.html', {'form': form_data, 'panchayath_areas': PANCHAYATH_AREAS})

        if len(form_data['password']) < 6:
            messages.warning(request, "Password must be at least 6 characters long.")
            return render(request, 'user/user_registartion.html', {'form': form_data, 'panchayath_areas': PANCHAYATH_AREAS})

        # Username duplicate check
        if User.objects.filter(username=form_data['username']).exists():
            messages.warning(request, f"The username '{form_data['username']}' is already registered. Please choose another username.")
            return render(request, 'user/user_registartion.html', {'form': form_data, 'panchayath_areas': PANCHAYATH_AREAS})

        # Create user & profile
        user_group, _ = Group.objects.get_or_create(name="user")
        user = User.objects.create_user(
            username=form_data['username'],
            email=form_data['email'],
            password=form_data['password'],
            first_name=form_data['name']
        )
        user.groups.add(user_group)

        user_table.objects.create(
            LOGIN=user,
            name=form_data['name'],
            husband_name=form_data['husband_name'],
            age=age_int,
            dob=form_data['dob'],
            expected_delivery_date=parsed_edd,
            blood_group=form_data['blood_group'],
            phone=int(cleaned_phone),
            Email=form_data['email'],
            Address=form_data['address'],
            panchayath=form_data['panchayath'],
            area=form_data['area'],
            district=form_data['district'],
            state=form_data['state'],
            pincode=form_data['pincode'],
        )
        messages.success(
            request,
            f"Mother '{form_data['name']}' registered successfully! Your registration request has been forwarded directly to the designated ASHA Healthcare Worker for {form_data['area']} for verification."
        )
        return render(request, 'user/user_registartion.html', {'success': True, 'panchayath_areas': PANCHAYATH_AREAS})

    return render(request, 'user/user_registartion.html', {'panchayath_areas': PANCHAYATH_AREAS})


# ================= ASHA WORKER VIEWS =================
def manage_asha(request):
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', 'all').strip()
    workers = asha_worker.objects.all().order_by('-id')

    if status_filter and status_filter.lower() != 'all':
        workers = workers.filter(Current_status__iexact=status_filter)

    if search_query:
        workers = workers.filter(
            Q(Full_name__icontains=search_query) |
            Q(Email__icontains=search_query) |
            Q(Area_assigned__icontains=search_query) |
            Q(Phone__icontains=search_query) |
            Q(Qualification__icontains=search_query) |
            Q(Address__icontains=search_query)
        )

    all_workers = asha_worker.objects.all()
    total_workers = all_workers.count()
    active_workers = all_workers.filter(Current_status='Active').count()
    avg_households = (user_table.objects.filter(ASHA__isnull=False).count() // total_workers) if total_workers > 0 else 0

    context = {
        'workers': workers,
        'total_workers': total_workers,
        'active_workers': active_workers,
        'avg_households': avg_households,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'admin/manage_asha.html', context)


def add_asha(request):
    if request.method == "POST":
        form_data = {
            'full_name': request.POST.get("full_name", "").strip(),
            'dob': request.POST.get("dob", "").strip(),
            'age': request.POST.get("age", "").strip(),
            'phone': request.POST.get("phone", "").strip(),
            'email': request.POST.get("email", "").strip(),
            'area_assigned': request.POST.get("area_assigned", "").strip(),
            'address': request.POST.get("address", "").strip(),
            'joining_date': request.POST.get("joining_date", "").strip(),
            'status': request.POST.get("status", "Active"),
            'qualification': request.POST.get("qualification", "").strip(),
            'username': request.POST.get("username", "").strip(),
            'password': request.POST.get("password", ""),
        }
        image_file = request.FILES.get("image")

        # Check required fields
        for field, label in [
            ('full_name', 'Full Name'), ('dob', 'Date of Birth'), ('phone', 'Contact Number'),
            ('email', 'Email Address'), ('area_assigned', 'Assigned Area'),
            ('address', 'Address'), ('joining_date', 'Date of Joining'),
            ('qualification', 'Qualifications'), ('username', 'Username'), ('password', 'Password')
        ]:
            if not form_data[field]:
                messages.warning(request, f"Please enter {label}.")
                return render(request, 'admin/add_asha.html', {'form': form_data})

        if not image_file:
            messages.warning(request, "Please upload a profile image.")
            return render(request, 'admin/add_asha.html', {'form': form_data})

        # Image format & size validation
        img_ext = os.path.splitext(image_file.name)[1].lower()
        if img_ext not in ['.jpg', '.jpeg', '.png', '.webp']:
            messages.warning(request, "Profile picture must be a JPG, PNG, or WEBP image file.")
            return render(request, 'admin/add_asha.html', {'form': form_data})
        if image_file.size > 3 * 1024 * 1024:
            messages.warning(request, "Profile image cannot exceed 3 MB.")
            return render(request, 'admin/add_asha.html', {'form': form_data})

        # Name validation
        if len(form_data['full_name']) < 3 or not re.match(r'^[a-zA-Z\s.]+$', form_data['full_name']):
            messages.warning(request, "Full name must be at least 3 characters and contain only letters.")
            return render(request, 'admin/add_asha.html', {'form': form_data})

        # DOB & Age validation (Age >= 18)
        try:
            parsed_dob = datetime.strptime(form_data['dob'], '%Y-%m-%d').date()
            today = date.today()
            if parsed_dob > today:
                messages.warning(request, "Date of birth cannot be in the future.")
                return render(request, 'admin/add_asha.html', {'form': form_data})
            age_int = today.year - parsed_dob.year - ((today.month, today.day) < (parsed_dob.month, parsed_dob.day))
            if age_int < 18:
                messages.warning(request, "ASHA Worker age must be at least 18 years old.")
                return render(request, 'admin/add_asha.html', {'form': form_data})
            if age_int > 65:
                messages.warning(request, "ASHA Worker age cannot exceed 65 years.")
                return render(request, 'admin/add_asha.html', {'form': form_data})
        except ValueError:
            messages.warning(request, "Invalid Date of Birth format.")
            return render(request, 'admin/add_asha.html', {'form': form_data})

        # Joining date validation (Must be past or today)
        try:
            parsed_joining = datetime.strptime(form_data['joining_date'], '%Y-%m-%d').date()
            if parsed_joining > date.today():
                messages.warning(request, "Date of joining cannot be a future date (tomorrow or later).")
                return render(request, 'admin/add_asha.html', {'form': form_data})
        except ValueError:
            messages.warning(request, "Invalid Date of Joining format.")
            return render(request, 'admin/add_asha.html', {'form': form_data})

        # Phone validation
        cleaned_phone = ''.join(filter(str.isdigit, form_data['phone']))
        if not re.match(PHONE_REGEX, cleaned_phone):
            messages.warning(request, "Please enter a valid 10-digit phone number starting with 6, 7, 8, or 9.")
            return render(request, 'admin/add_asha.html', {'form': form_data})

        # Duplicate Phone check
        if asha_worker.objects.filter(Phone=int(cleaned_phone)).exists():
            messages.warning(request, f"The phone number '{cleaned_phone}' is already registered with an existing ASHA worker.")
            return render(request, 'admin/add_asha.html', {'form': form_data})

        # Email validation (strictly @gmail.com format)
        if not re.match(EMAIL_REGEX, form_data['email'], re.IGNORECASE):
            messages.warning(request, "Email address must be a valid @gmail.com address (e.g., example@gmail.com).")
            return render(request, 'admin/add_asha.html', {'form': form_data})

        # Duplicate Email check
        if User.objects.filter(email__iexact=form_data['email']).exists() or asha_worker.objects.filter(Email__iexact=form_data['email']).exists():
            messages.warning(request, f"The email address '{form_data['email']}' is already in use by another user.")
            return render(request, 'admin/add_asha.html', {'form': form_data})

        # Address length
        if len(form_data['address']) < 5:
            messages.warning(request, "Address must be at least 5 characters long.")
            return render(request, 'admin/add_asha.html', {'form': form_data})

        # Qualification length
        if len(form_data['qualification']) < 5:
            messages.warning(request, "Qualifications & Certifications must be at least 5 characters.")
            return render(request, 'admin/add_asha.html', {'form': form_data})

        # Password length
        if len(form_data['password']) < 6:
            messages.warning(request, "Password must be at least 6 characters long.")
            return render(request, 'admin/add_asha.html', {'form': form_data})

        # Username duplicate check
        if User.objects.filter(username=form_data['username']).exists():
            messages.warning(request, f"An account with username '{form_data['username']}' already exists.")
            return render(request, 'admin/add_asha.html', {'form': form_data})

        # Create User & ASHA Worker
        asha_group, _ = Group.objects.get_or_create(name="ashaworker")
        user = User.objects.create_user(
            username=form_data['username'],
            email=form_data['email'],
            password=form_data['password'],
            first_name=form_data['full_name']
        )
        user.groups.add(asha_group)

        worker_created = asha_worker.objects.create(
            LOGIN=user,
            Full_name=form_data['full_name'],
            Age=age_int,
            dob=parsed_dob,
            Qualification=form_data['qualification'],
            Email=form_data['email'],
            Address=form_data['address'],
            image=image_file,
            Area_assigned=form_data['area_assigned'],
            Phone=int(cleaned_phone),
            Joining_date=parsed_joining,
            Current_status=form_data['status'],
        )
        request.session['asha_id'] = worker_created.id
        messages.success(request, f"ASHA Worker '{form_data['full_name']}' registered successfully!")
        return redirect('/myapp/manage_asha/')

    return render(request, 'admin/add_asha.html')


def edit_asha(request, id):
    asha = get_object_or_404(asha_worker, id=id)
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        dob = request.POST.get("dob", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip()
        area_assigned = request.POST.get("area_assigned", "").strip()
        address = request.POST.get("address", "").strip()
        joining_date = request.POST.get("joining_date", "").strip()
        status = request.POST.get("status", "Active")
        qualification = request.POST.get("qualification", "").strip()
        image_file = request.FILES.get("image")

        # Validations
        if not full_name or len(full_name) < 3 or not re.match(r'^[a-zA-Z\s.]+$', full_name):
            messages.warning(request, "Full name must be at least 3 characters and contain only letters.")
            return render(request, 'admin/edit_asha.html', {'asha': asha})

        if not dob:
            messages.warning(request, "Please select Date of Birth.")
            return render(request, 'admin/edit_asha.html', {'asha': asha})

        try:
            parsed_dob = datetime.strptime(dob, '%Y-%m-%d').date()
            today = date.today()
            if parsed_dob > today:
                messages.warning(request, "Date of birth cannot be in the future.")
                return render(request, 'admin/edit_asha.html', {'asha': asha})
            age_int = today.year - parsed_dob.year - ((today.month, today.day) < (parsed_dob.month, parsed_dob.day))
            if age_int < 18:
                messages.warning(request, "Age must be at least 18 years old.")
                return render(request, 'admin/edit_asha.html', {'asha': asha})
            if age_int > 65:
                messages.warning(request, "Age cannot exceed 65 years.")
                return render(request, 'admin/edit_asha.html', {'asha': asha})
        except ValueError:
            messages.warning(request, "Invalid Date of Birth format.")
            return render(request, 'admin/edit_asha.html', {'asha': asha})

        if joining_date:
            try:
                parsed_joining = datetime.strptime(joining_date, '%Y-%m-%d').date()
                if parsed_joining > date.today():
                    messages.warning(request, "Date of joining cannot be a future date (tomorrow or later).")
                    return render(request, 'admin/edit_asha.html', {'asha': asha})
                asha.Joining_date = parsed_joining
            except ValueError:
                messages.warning(request, "Invalid Date of Joining format.")
                return render(request, 'admin/edit_asha.html', {'asha': asha})

        cleaned_phone = ''.join(filter(str.isdigit, phone))
        if not re.match(PHONE_REGEX, cleaned_phone):
            messages.warning(request, "Please enter a valid 10-digit mobile number starting with 6, 7, 8, or 9.")
            return render(request, 'admin/edit_asha.html', {'asha': asha})

        if not re.match(EMAIL_REGEX, email, re.IGNORECASE):
            messages.warning(request, "Email address must be a valid @gmail.com address (e.g., example@gmail.com).")
            return render(request, 'admin/edit_asha.html', {'asha': asha})

        if len(address) < 5:
            messages.warning(request, "Address must be at least 5 characters long.")
            return render(request, 'admin/edit_asha.html', {'asha': asha})

        if len(qualification) < 5:
            messages.warning(request, "Qualifications must be at least 5 characters long.")
            return render(request, 'admin/edit_asha.html', {'asha': asha})

        asha.Full_name = full_name
        asha.Age = age_int
        asha.dob = parsed_dob
        asha.Phone = int(cleaned_phone)
        asha.Email = email
        asha.Area_assigned = area_assigned
        asha.Address = address
        asha.Current_status = status
        asha.Qualification = qualification
        if image_file:
            asha.image = image_file
        asha.save()

        # Also update User model email / name if linked
        if asha.LOGIN:
            asha.LOGIN.first_name = full_name
            asha.LOGIN.email = email
            asha.LOGIN.save()

        request.session['asha_id'] = asha.id
        messages.success(request, f"ASHA Worker '{asha.Full_name}' profile updated successfully!")
        return redirect('/myapp/manage_asha/')

    return render(request, 'admin/edit_asha.html', {'asha': asha})


def delete_asha(request, id):
    asha = get_object_or_404(asha_worker, id=id)
    name = asha.Full_name
    if asha.LOGIN:
        asha.LOGIN.delete()
    else:
        asha.delete()
    messages.success(request, f"ASHA Worker '{name}' has been deleted successfully.")
    return redirect('/myapp/manage_asha/')


# ================= ANGANWADI TEACHER VIEWS =================
def manage_anganwadi(request):
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', 'all').strip()
    teachers = anganwadi_teacher.objects.all().order_by('-id')

    if status_filter and status_filter.lower() != 'all':
        teachers = teachers.filter(Current_status__iexact=status_filter)

    if search_query:
        teachers = teachers.filter(
            Q(Name__icontains=search_query) |
            Q(Email__icontains=search_query) |
            Q(center_name__icontains=search_query) |
            Q(Phone__icontains=search_query)
        )

    all_teachers = anganwadi_teacher.objects.all()
    total_teachers = all_teachers.count()
    active_centres = len(set(all_teachers.values_list('center_name', flat=True)))
    total_m = user_table.objects.count()
    total_k = nutrition_kit.objects.count()
    avg_kits = f"{round((total_k / total_m) * 100)}%" if total_m > 0 else "0%"

    context = {
        'teachers': teachers,
        'total_teachers': total_teachers,
        'active_centres': active_centres,
        'avg_kits': avg_kits,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'admin/manage_anganwadi.html', context)


def add_anganwadi(request):
    if request.method == "POST":
        form_data = {
            'name': request.POST.get("name", "").strip(),
            'dob': request.POST.get("dob", "").strip(),
            'age': request.POST.get("age", "").strip(),
            'gender': request.POST.get("gender", "Female").strip(),
            'phone': request.POST.get("phone", "").strip(),
            'email': request.POST.get("email", "").strip(),
            'center_name': request.POST.get("center_name", "").strip(),
            'address': request.POST.get("address", "").strip(),
            'joining_date': request.POST.get("joining_date", "").strip(),
            'status': request.POST.get("status", "Active"),
            'qualification': request.POST.get("qualification", "").strip(),
            'username': request.POST.get("username", "").strip(),
            'password': request.POST.get("password", ""),
        }
        image_file = request.FILES.get("image")

        # Check required fields
        for field, label in [
            ('name', 'Full Name'), ('dob', 'Date of Birth'), ('gender', 'Gender'),
            ('phone', 'Contact Number'), ('email', 'Email Address'),
            ('center_name', 'Assigned Center'), ('address', 'Address'),
            ('joining_date', 'Date of Joining'), ('qualification', 'Qualifications'),
            ('username', 'Username'), ('password', 'Password')
        ]:
            if not form_data[field]:
                messages.warning(request, f"Please enter {label}.")
                return render(request, 'admin/add_anganwadi.html', {'form': form_data})

        if image_file:
            img_ext = os.path.splitext(image_file.name)[1].lower()
            if img_ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                messages.warning(request, "Profile picture must be a JPG, PNG, or WEBP image file.")
                return render(request, 'admin/add_anganwadi.html', {'form': form_data})
            if image_file.size > 3 * 1024 * 1024:
                messages.warning(request, "Profile image cannot exceed 3 MB.")
                return render(request, 'admin/add_anganwadi.html', {'form': form_data})

        # Name validation
        if len(form_data['name']) < 3 or not re.match(r'^[a-zA-Z\s.]+$', form_data['name']):
            messages.warning(request, "Teacher's name must be at least 3 characters and contain only letters.")
            return render(request, 'admin/add_anganwadi.html', {'form': form_data})

        # Gender validation
        if form_data['gender'] not in ['Female', 'Male', 'Other']:
            form_data['gender'] = 'Female'

        # DOB & Age validation (Age >= 18)
        try:
            parsed_dob = datetime.strptime(form_data['dob'], '%Y-%m-%d').date()
            today = date.today()
            if parsed_dob > today:
                messages.warning(request, "Date of birth cannot be in the future.")
                return render(request, 'admin/add_anganwadi.html', {'form': form_data})
            age_int = today.year - parsed_dob.year - ((today.month, today.day) < (parsed_dob.month, parsed_dob.day))
            if age_int < 18:
                messages.warning(request, "Anganwadi Teacher age must be at least 18 years old.")
                return render(request, 'admin/add_anganwadi.html', {'form': form_data})
            if age_int > 65:
                messages.warning(request, "Anganwadi Teacher age cannot exceed 65 years.")
                return render(request, 'admin/add_anganwadi.html', {'form': form_data})
        except ValueError:
            messages.warning(request, "Invalid Date of Birth format.")
            return render(request, 'admin/add_anganwadi.html', {'form': form_data})

        # Joining date validation (Must be past or today)
        try:
            parsed_joining = datetime.strptime(form_data['joining_date'], '%Y-%m-%d').date()
            if parsed_joining > date.today():
                messages.warning(request, "Date of joining cannot be a future date (tomorrow or later).")
                return render(request, 'admin/add_anganwadi.html', {'form': form_data})
        except ValueError:
            messages.warning(request, "Invalid Date of Joining format.")
            return render(request, 'admin/add_anganwadi.html', {'form': form_data})

        # Phone validation
        cleaned_phone = ''.join(filter(str.isdigit, form_data['phone']))
        if not re.match(PHONE_REGEX, cleaned_phone):
            messages.warning(request, "Please enter a valid 10-digit phone number starting with 6, 7, 8, or 9.")
            return render(request, 'admin/add_anganwadi.html', {'form': form_data})

        # Duplicate Phone check
        if anganwadi_teacher.objects.filter(Phone=int(cleaned_phone)).exists():
            messages.warning(request, f"The phone number '{cleaned_phone}' is already registered with an existing Anganwadi teacher.")
            return render(request, 'admin/add_anganwadi.html', {'form': form_data})

        # Email validation (strictly @gmail.com format)
        if not re.match(EMAIL_REGEX, form_data['email'], re.IGNORECASE):
            messages.warning(request, "Email address must be a valid @gmail.com address (e.g., example@gmail.com).")
            return render(request, 'admin/add_anganwadi.html', {'form': form_data})

        # Duplicate Email check
        if User.objects.filter(email__iexact=form_data['email']).exists() or anganwadi_teacher.objects.filter(Email__iexact=form_data['email']).exists():
            messages.warning(request, f"The email address '{form_data['email']}' is already in use by another user.")
            return render(request, 'admin/add_anganwadi.html', {'form': form_data})

        # Address length
        if len(form_data['address']) < 5:
            messages.warning(request, "Address must be at least 5 characters long.")
            return render(request, 'admin/add_anganwadi.html', {'form': form_data})

        # Qualification length
        if len(form_data['qualification']) < 5:
            messages.warning(request, "Qualifications & Certifications must be at least 5 characters.")
            return render(request, 'admin/add_anganwadi.html', {'form': form_data})

        # Password length
        if len(form_data['password']) < 6:
            messages.warning(request, "Password must be at least 6 characters long.")
            return render(request, 'admin/add_anganwadi.html', {'form': form_data})

        # Username duplicate check
        if User.objects.filter(username=form_data['username']).exists():
            messages.warning(request, f"An account with username '{form_data['username']}' already exists.")
            return render(request, 'admin/add_anganwadi.html', {'form': form_data})

        # Create User & Anganwadi Teacher with correct role group 'angteacher'
        teacher_group, _ = Group.objects.get_or_create(name="angteacher")
        user = User.objects.create_user(
            username=form_data['username'],
            email=form_data['email'],
            password=form_data['password'],
            first_name=form_data['name']
        )
        user.groups.add(teacher_group)

        teacher_created = anganwadi_teacher.objects.create(
            LOGIN=user,
            Name=form_data['name'],
            Age=age_int,
            dob=parsed_dob,
            Gender=form_data['gender'],
            Phone=int(cleaned_phone),
            Email=form_data['email'],
            Address=form_data['address'],
            image=image_file,
            Qualification=form_data['qualification'],
            center_name=form_data['center_name'],
            joining_date=parsed_joining,
            Current_status=form_data['status'],
        )
        request.session['teacher_id'] = teacher_created.id
        messages.success(request, f"Anganwadi Teacher '{form_data['name']}' registered successfully!")
        return redirect('/myapp/manage_anganwadi/')

    return render(request, 'admin/add_anganwadi.html')


def edit_anganwadi(request, id):
    teacher = get_object_or_404(anganwadi_teacher, id=id)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        dob = request.POST.get("dob", "").strip()
        gender = request.POST.get("gender", "Female").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip()
        center_name = request.POST.get("center_name", "").strip()
        address = request.POST.get("address", "").strip()
        joining_date = request.POST.get("joining_date", "").strip()
        status = request.POST.get("status", "Active")
        qualification = request.POST.get("qualification", "").strip()
        image_file = request.FILES.get("image")

        # Validations
        if not name or len(name) < 3 or not re.match(r'^[a-zA-Z\s.]+$', name):
            messages.warning(request, "Name must be at least 3 characters and contain only letters.")
            return render(request, 'admin/edit_anganwadi.html', {'teacher': teacher})

        if not dob:
            messages.warning(request, "Please select Date of Birth.")
            return render(request, 'admin/edit_anganwadi.html', {'teacher': teacher})

        try:
            parsed_dob = datetime.strptime(dob, '%Y-%m-%d').date()
            today = date.today()
            if parsed_dob > today:
                messages.warning(request, "Date of birth cannot be in the future.")
                return render(request, 'admin/edit_anganwadi.html', {'teacher': teacher})
            age_int = today.year - parsed_dob.year - ((today.month, today.day) < (parsed_dob.month, parsed_dob.day))
            if age_int < 18:
                messages.warning(request, "Age must be at least 18 years old.")
                return render(request, 'admin/edit_anganwadi.html', {'teacher': teacher})
            if age_int > 65:
                messages.warning(request, "Age cannot exceed 65 years.")
                return render(request, 'admin/edit_anganwadi.html', {'teacher': teacher})
        except ValueError:
            messages.warning(request, "Invalid Date of Birth format.")
            return render(request, 'admin/edit_anganwadi.html', {'teacher': teacher})

        if joining_date:
            try:
                parsed_joining = datetime.strptime(joining_date, '%Y-%m-%d').date()
                if parsed_joining > date.today():
                    messages.warning(request, "Date of joining cannot be a future date (tomorrow or later).")
                    return render(request, 'admin/edit_anganwadi.html', {'teacher': teacher})
                teacher.joining_date = parsed_joining
            except ValueError:
                messages.warning(request, "Invalid Date of Joining format.")
                return render(request, 'admin/edit_anganwadi.html', {'teacher': teacher})

        cleaned_phone = ''.join(filter(str.isdigit, phone))
        if not re.match(PHONE_REGEX, cleaned_phone):
            messages.warning(request, "Please enter a valid 10-digit mobile number starting with 6, 7, 8, or 9.")
            return render(request, 'admin/edit_anganwadi.html', {'teacher': teacher})

        if not re.match(EMAIL_REGEX, email, re.IGNORECASE):
            messages.warning(request, "Email address must be a valid @gmail.com address (e.g., example@gmail.com).")
            return render(request, 'admin/edit_anganwadi.html', {'teacher': teacher})

        if len(address) < 5:
            messages.warning(request, "Address must be at least 5 characters long.")
            return render(request, 'admin/edit_anganwadi.html', {'teacher': teacher})

        if len(qualification) < 5:
            messages.warning(request, "Qualifications must be at least 5 characters long.")
            return render(request, 'admin/edit_anganwadi.html', {'teacher': teacher})

        teacher.Name = name
        teacher.Age = age_int
        teacher.dob = parsed_dob
        teacher.Gender = gender
        teacher.Phone = int(cleaned_phone)
        teacher.Email = email
        teacher.center_name = center_name
        teacher.Address = address
        teacher.Current_status = status
        teacher.Qualification = qualification
        if image_file:
            teacher.image = image_file
        teacher.save()

        if teacher.LOGIN:
            teacher.LOGIN.first_name = name
            teacher.LOGIN.email = email
            teacher.LOGIN.save()

        request.session['teacher_id'] = teacher.id
        messages.success(request, f"Anganwadi Teacher '{teacher.Name}' profile updated successfully!")
        return redirect('/myapp/manage_anganwadi/')

    return render(request, 'admin/edit_anganwadi.html', {'teacher': teacher})


def delete_anganwadi(request, id):
    teacher = get_object_or_404(anganwadi_teacher, id=id)
    name = teacher.Name
    if teacher.LOGIN:
        teacher.LOGIN.delete()
    else:
        teacher.delete()
    messages.success(request, f"Anganwadi Teacher '{name}' has been deleted successfully.")
    return redirect('/myapp/manage_anganwadi/')


# ================= VACCINATION VIEWS =================
def add_vaccination(request):
    master_vaccines = vaccination.objects.filter(CHILD__isnull=True).order_by('-id')

    if request.method == "POST":
        action_type = request.POST.get("action_type", "add")
        if action_type == "delete_master":
            rec_id = request.POST.get("vaccine_id")
            if rec_id:
                vaccination.objects.filter(id=rec_id, CHILD__isnull=True).delete()
                messages.success(request, "Master vaccine deleted successfully.")
            return redirect('/myapp/add_vaccination/')

        vaccine_name = request.POST.get("vaccine_name", "").strip()
        vaccine_code = request.POST.get("vaccine_code", "").strip().upper()
        vaccine_type = request.POST.get("vaccine_type", "").strip()
        target_month_raw = request.POST.get("target_month", "").strip()
        description = request.POST.get("description", "").strip()

        try:
            target_month = int(target_month_raw) if target_month_raw != "" else None
        except ValueError:
            target_month = None

        form_data = {
            'vaccine_name': vaccine_name,
            'vaccine_code': vaccine_code,
            'vaccine_type': vaccine_type,
            'target_month': target_month,
            'description': description
        }

        # Validations
        if not vaccine_name or len(vaccine_name) < 2:
            messages.warning(request, "Vaccine Name is required and must be at least 2 characters.")
            return render(request, 'admin/add_vaccination.html', {'form': form_data, 'master_vaccines': master_vaccines})

        if not vaccine_code or len(vaccine_code) < 2:
            messages.warning(request, "Vaccine Code is required (e.g., VAC-001).")
            return render(request, 'admin/add_vaccination.html', {'form': form_data, 'master_vaccines': master_vaccines})

        if vaccination.objects.filter(CHILD__isnull=True, vaccine_code=vaccine_code).exists():
            messages.warning(request, f"Warning: A vaccine with code '{vaccine_code}' is already registered in master list.")
            return render(request, 'admin/add_vaccination.html', {'form': form_data, 'master_vaccines': master_vaccines})

        if not vaccine_type or len(vaccine_type) < 2:
            messages.warning(request, "Please specify the Vaccine Type (e.g. mRNA, Inactivated, Live Attenuated).")
            return render(request, 'admin/add_vaccination.html', {'form': form_data, 'master_vaccines': master_vaccines})

        if target_month is None or target_month < 0:
            messages.warning(request, "Please select a specific month to administer this vaccine (e.g. Month 0, 1, 2, 3, etc.).")
            return render(request, 'admin/add_vaccination.html', {'form': form_data, 'master_vaccines': master_vaccines})

        if not description or len(description) < 10:
            messages.warning(request, "Description is required and should be at least 10 characters detailing usage & storage.")
            return render(request, 'admin/add_vaccination.html', {'form': form_data, 'master_vaccines': master_vaccines})

        vaccination.objects.create(
            vaccine_name=vaccine_name,
            vaccine_code=vaccine_code,
            vaccine_type=vaccine_type,
            target_month=target_month,
            description=description,
            CHILD=None
        )
        messages.success(request, f"Vaccine '{vaccine_name}' ({vaccine_code}) for Month {target_month} added successfully!")
        return redirect('/myapp/add_vaccination/')

    return render(request, 'admin/add_vaccination.html', {'master_vaccines': master_vaccines})


def schedule_vaccination(request):
    """
    Renders and handles Vaccination Scheduling form page.
    Restricted ONLY to master vaccines added by admin on Add Vaccination page (CHILD__isnull=True).
    Enforces:
    1. Child must match the specific month required by the vaccine.
    2. If a vaccine is completed/taken by a child, it cannot be re-assigned.
    """
    master_vaccine_qs = vaccination.objects.filter(CHILD__isnull=True).order_by('target_month', 'vaccine_name')

    if request.method == "POST":
        action_type = request.POST.get("action_type", "schedule_single")

        if action_type == "delete_vaccination":
            rec_id = request.POST.get("record_id")
            if rec_id:
                vaccination.objects.filter(id=rec_id).delete()
                messages.success(request, "Vaccination record deleted successfully.")
            return redirect('/myapp/vaccination_records/')

        # Bulk Scheduling & Notification based on Child's Month / Age
        if action_type == "schedule_bulk":
            target_month = request.POST.get("target_month", "all").strip()
            vaccine_id = request.POST.get("vaccine_id")
            vax_date_str = request.POST.get("vaccination_date", "").strip()
            reminder_msg = request.POST.get("reminder_message", "").strip()

            master_vax = master_vaccine_qs.filter(id=vaccine_id).first() if vaccine_id else None
            if not master_vax:
                messages.warning(request, "Please select a valid vaccine added by the admin.")
                return redirect('/myapp/schedule_vaccination/?tab=bulk')

            vax_date = date.today()
            if vax_date_str:
                try:
                    vax_date = datetime.strptime(vax_date_str, '%Y-%m-%d').date()
                except ValueError:
                    vax_date = date.today()

            all_children_list = child.objects.all().select_related('USER')
            today_dt = date.today()
            matching_children = []

            for ch in all_children_list:
                dob = ch.date_of_birth
                months = max((vax_date.year - dob.year) * 12 + vax_date.month - dob.month, 0) if dob else 0
                
                # Must match the vaccine's specific target_month
                if master_vax.target_month is not None:
                    if months == master_vax.target_month:
                        matching_children.append((ch, months))
                elif target_month != "all":
                    try:
                        t_m = int(target_month)
                        if months == t_m:
                            matching_children.append((ch, months))
                    except ValueError:
                        matching_children.append((ch, months))
                else:
                    matching_children.append((ch, months))

            if not matching_children:
                req_month_name = master_vax.target_month_display if master_vax.target_month is not None else f"Month {target_month}"
                messages.info(request, f"No registered children found matching the specific age criteria for '{master_vax.vaccine_name}' ({req_month_name}).")
                return redirect('/myapp/schedule_vaccination/?tab=bulk')

            count_scheduled = 0
            skipped_already_done = 0
            skipped_active = 0
            notified_mothers = set()

            for ch, ch_m in matching_children:
                # Anti-reassignment check: skip if child has ALREADY completed/taken this vaccine
                already_done = vaccination.objects.filter(
                    CHILD=ch,
                    vaccine_name__iexact=master_vax.vaccine_name,
                    status__in=["Taken", "Done"]
                ).exists()

                if already_done:
                    skipped_already_done += 1
                    continue

                # Skip if already actively scheduled
                already_active = vaccination.objects.filter(
                    CHILD=ch,
                    vaccine_name__iexact=master_vax.vaccine_name,
                    status__in=["Scheduled", "Rescheduled"]
                ).exists()

                if already_active:
                    skipped_active += 1
                    continue

                vaccination.objects.create(
                    CHILD=ch,
                    vaccine_code=master_vax.vaccine_code,
                    vaccine_name=master_vax.vaccine_name,
                    vaccine_type=master_vax.vaccine_type,
                    target_month=master_vax.target_month,
                    description=reminder_msg or f"Bulk scheduled for {master_vax.target_month_display} checkup.",
                    vaccination_date=vax_date,
                    status="Scheduled"
                )
                count_scheduled += 1

                if ch.USER and ch.USER.id not in notified_mothers:
                    vax_date_formatted = vax_date.strftime('%B %d, %Y')
                    mother_name = ch.USER.name if (ch.USER and ch.USER.name) else 'Mother'
                    msg_text = reminder_msg if reminder_msg else (
                        f"Dear {mother_name}, vaccination for your child {ch.child_name} is scheduled on "
                        f"{vax_date_formatted} for {master_vax.vaccine_name} ({master_vax.target_month_display}). "
                        f"Please visit your assigned Anganwadi / Health Center on this scheduled date."
                    )
                    notification.objects.create(
                        USER=ch.USER,
                        message=msg_text,
                        notification_date=today_dt
                    )
                    notified_mothers.add(ch.USER.id)

            success_msg = f"Bulk vaccination for '{master_vax.vaccine_name}' ({master_vax.target_month_display}) scheduled successfully for {count_scheduled} child(ren) and notifications sent to {len(notified_mothers)} mother(s)!"
            skip_notes = []
            if skipped_already_done > 0:
                skip_notes.append(f"{skipped_already_done} already completed/taken")
            if skipped_active > 0:
                skip_notes.append(f"{skipped_active} already scheduled")
            if skip_notes:
                success_msg += f" ({', '.join(skip_notes)} skipped)."
            messages.success(request, success_msg)
            return redirect('/myapp/vaccination_records/')

        # Single Child Vaccination Scheduling
        child_id = request.POST.get("child_id")
        vaccine_id = request.POST.get("vaccine_id")

        vax_date_str = request.POST.get("vaccination_date", "").strip()
        notification_msg = request.POST.get("notification_message", "").strip()
        clinical_notes = request.POST.get("clinical_notes", "").strip()

        if not child_id:
            messages.warning(request, "Please select a child to schedule vaccination.")
            return redirect('/myapp/schedule_vaccination/')

        child_obj = child.objects.filter(id=child_id).first()
        if not child_obj:
            messages.warning(request, "Selected child record not found.")
            return redirect('/myapp/schedule_vaccination/')

        master_vax = master_vaccine_qs.filter(id=vaccine_id).first() if vaccine_id else None
        if not master_vax:
            messages.warning(request, "Please select a vaccine added by the admin on Vaccination Adding page.")
            return redirect('/myapp/schedule_vaccination/')

        vax_date = date.today()
        if vax_date_str:
            try:
                vax_date = datetime.strptime(vax_date_str, '%Y-%m-%d').date()
            except ValueError:
                vax_date = date.today()

        # 1. SPECIFIC MONTH RESTRICTION:
        # Check child's age in months on the administration date
        dob = child_obj.date_of_birth
        child_age_months = 0
        if dob:
            child_age_months = max((vax_date.year - dob.year) * 12 + vax_date.month - dob.month, 0)

        if master_vax.target_month is not None:
            if child_age_months != master_vax.target_month:
                messages.warning(
                    request,
                    f"Age / Month Restriction: Vaccine '{master_vax.vaccine_name}' must be given specifically at Month {master_vax.target_month} ({master_vax.target_month_display}). '{child_obj.child_name}' is currently Month {child_age_months}, so this vaccine cannot be scheduled for this child."
                )
                return redirect('/myapp/schedule_vaccination/')

        # 2. ANTI-REASSIGNMENT RESTRICTION:
        # If the vaccine is already completed / done ("Taken") by this child, it cannot be re-assigned.
        completed_vax = vaccination.objects.filter(
            CHILD=child_obj,
            vaccine_name__iexact=master_vax.vaccine_name,
            status__in=["Taken", "Done"]
        ).first()

        if completed_vax:
            done_date_str = completed_vax.vaccination_date.strftime('%b %d, %Y') if completed_vax.vaccination_date else "a previous session"
            messages.warning(
                request,
                f"Vaccination Already Completed: '{child_obj.child_name}' has already completed / taken '{master_vax.vaccine_name}' on {done_date_str}. A completed vaccine cannot be re-assigned."
            )
            return redirect('/myapp/schedule_vaccination/')

        # 3. Prevent duplicate active scheduling (Scheduled or Rescheduled)
        active_vax = vaccination.objects.filter(
            CHILD=child_obj,
            vaccine_name__iexact=master_vax.vaccine_name,
            status__in=["Scheduled", "Rescheduled"]
        ).first()

        if active_vax:
            scheduled_date_str = active_vax.vaccination_date.strftime('%b %d, %Y') if active_vax.vaccination_date else "upcoming date"
            messages.warning(
                request,
                f"Already Scheduled: Vaccine '{master_vax.vaccine_name}' is already scheduled for '{child_obj.child_name}' on {scheduled_date_str} (Status: {active_vax.status}). Duplicate schedules are not allowed."
            )
            return redirect('/myapp/schedule_vaccination/')

        vax_obj = vaccination.objects.create(
            CHILD=child_obj,
            vaccine_code=master_vax.vaccine_code,
            vaccine_name=master_vax.vaccine_name,
            vaccine_type=master_vax.vaccine_type,
            target_month=master_vax.target_month,
            description=clinical_notes or master_vax.description or f"Scheduled for {master_vax.target_month_display} checkup.",
            vaccination_date=vax_date,
            status="Scheduled"
        )

        # Automatically Send Scheduling Date Notification to Mother
        if child_obj.USER:
            vax_date_formatted = vax_date.strftime('%B %d, %Y')
            mother_name = child_obj.USER.name if (child_obj.USER and child_obj.USER.name) else 'Mother'
            if not notification_msg:
                notification_msg = (
                    f"Dear {mother_name}, vaccination appointment for your child {child_obj.child_name} "
                    f"has been scheduled on {vax_date_formatted} for {master_vax.vaccine_name} "
                    f"({master_vax.vaccine_code}, {master_vax.target_month_display}). "
                    f"Please visit your assigned Anganwadi / Health Center on this scheduled date."
                )

            notification.objects.create(
                USER=child_obj.USER,
                message=notification_msg,
                notification_date=date.today()
            )

        messages.success(request, f"Vaccination '{master_vax.vaccine_name}' scheduled for '{child_obj.child_name}' on {vax_date.strftime('%b %d, %Y')} and automatic notification sent to mother!")
        return redirect('/myapp/vaccination_records/')

    all_children_qs = child.objects.all().select_related('USER').order_by('child_name')
    today_dt = date.today()
    all_children = []
    child_vaccine_status_map = {}

    for ch in all_children_qs:
        dob = ch.date_of_birth
        if dob:
            m_calc = max((today_dt.year - dob.year) * 12 + today_dt.month - dob.month, 0)
        else:
            m_calc = 0
        
        if m_calc == 0:
            age_label = "Month 0 (At Birth)"
        elif m_calc == 1:
            age_label = "Month 1 (1st Month)"
        elif m_calc == 2:
            age_label = "Month 2 (2nd Month)"
        elif m_calc == 3:
            age_label = "Month 3 (3rd Month)"
        elif m_calc >= 12:
            yrs = m_calc // 12
            rem_m = m_calc % 12
            age_label = f"Month {m_calc} ({yrs} Yr{'s' if yrs > 1 else ''} {rem_m} M)" if rem_m else f"Month {m_calc} ({yrs} Year{'s' if yrs > 1 else ''})"
        else:
            age_label = f"Month {m_calc} ({m_calc}th Month)"
        
        ch.child_age_months = m_calc
        ch.child_age_str = age_label

        done_vaxes = list(vaccination.objects.filter(CHILD=ch, status__in=["Taken", "Done"]).values_list('vaccine_name', flat=True))
        active_vaxes = list(vaccination.objects.filter(CHILD=ch, status__in=["Scheduled", "Rescheduled"]).values_list('vaccine_name', flat=True))

        ch.completed_vaccines_list = done_vaxes
        ch.active_vaccines_list = active_vaxes

        child_vaccine_status_map[str(ch.id)] = {
            'months': m_calc,
            'age_str': age_label,
            'completed': [v.strip().lower() for v in done_vaxes],
            'completed_display': done_vaxes,
            'active': [v.strip().lower() for v in active_vaxes],
            'active_display': active_vaxes
        }

        all_children.append(ch)

    today_str = today_dt.strftime('%Y-%m-%d')
    active_tab = request.GET.get('tab', 'single')

    context = {
        'all_children': all_children,
        'master_vaccines': master_vaccine_qs,
        'today_date': today_str,
        'active_tab': active_tab,
        'child_vax_json': json.dumps(child_vaccine_status_map)
    }
    return render(request, 'admin/schedule_vaccination.html', context)


def vaccination_records(request):
    """
    Renders and handles the dedicated Vaccination Records tracking page.
    Displays immunization records, supports Taken/Missed status updates,
    rescheduling missed doses with auto-notifications, and sending reminder notifications to mothers.
    """
    if request.method == "POST":
        action_type = request.POST.get("action_type", "")

        if action_type == "delete_vaccination":
            rec_id = request.POST.get("record_id")
            if rec_id:
                vaccination.objects.filter(id=rec_id).delete()
                messages.success(request, "Vaccination record deleted successfully.")
            return redirect('/myapp/vaccination_records/')

        # Update Vaccination Status (Taken / Missed / Scheduled / Rescheduled)
        if action_type == "update_vax_status":
            rec_id = request.POST.get("record_id")
            new_status = request.POST.get("status", "").strip()
            vax_rec = vaccination.objects.filter(id=rec_id, CHILD__isnull=False).first()
            if vax_rec and new_status in ["Taken", "Missed", "Scheduled", "Rescheduled"]:
                vax_rec.status = new_status
                vax_rec.save()
                messages.success(request, f"Vaccination status for '{vax_rec.CHILD.child_name}' updated to '{new_status}'!")
            else:
                messages.warning(request, "Invalid vaccination record or status.")
            return redirect('/myapp/vaccination_records/')

        # Reschedule Missed Vaccination & Send Auto-Notification
        if action_type == "reschedule_vax":
            rec_id = request.POST.get("record_id")
            new_date_str = request.POST.get("new_vaccination_date", "").strip()
            reminder_msg = request.POST.get("reminder_message", "").strip()
            reschedule_notes = request.POST.get("reschedule_notes", "").strip()

            vax_rec = vaccination.objects.filter(id=rec_id, CHILD__isnull=False).first()
            if not vax_rec:
                messages.warning(request, "Vaccination record not found.")
                return redirect('/myapp/vaccination_records/')

            new_date = date.today()
            if new_date_str:
                try:
                    new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
                except ValueError:
                    new_date = date.today()

            vax_rec.vaccination_date = new_date
            vax_rec.status = "Rescheduled"
            if reschedule_notes:
                vax_rec.description = f"Rescheduled: {reschedule_notes}"
            vax_rec.save()

            # Automatically Send Reschedule Reminder Notification to Mother
            if vax_rec.CHILD and vax_rec.CHILD.USER:
                final_msg = reminder_msg if reminder_msg else f"Vaccination ({vax_rec.vaccine_name}) for {vax_rec.CHILD.child_name} has been rescheduled to {new_date.strftime('%b %d, %Y')}."
                if reschedule_notes:
                    final_msg += f" Note: {reschedule_notes}"
                notification.objects.create(
                    USER=vax_rec.CHILD.USER,
                    message=final_msg,
                    notification_date=date.today()
                )

            messages.success(request, f"Vaccination for '{vax_rec.CHILD.child_name}' rescheduled to {new_date.strftime('%b %d, %Y')} and reminder notification sent to mother!")
            return redirect('/myapp/vaccination_records/')

        # Send Custom Reminder Notification to Mother
        if action_type == "send_vax_reminder":
            rec_id = request.POST.get("record_id")
            reminder_msg = request.POST.get("reminder_message", "").strip()

            vax_rec = vaccination.objects.filter(id=rec_id, CHILD__isnull=False).first()
            if not vax_rec:
                messages.warning(request, "Vaccination record not found.")
                return redirect('/myapp/vaccination_records/')

            if not reminder_msg:
                reminder_msg = f"Reminder: Vaccination appointment for {vax_rec.CHILD.child_name} for {vax_rec.vaccine_name} is scheduled on {vax_rec.vaccination_date.strftime('%b %d, %Y') if vax_rec.vaccination_date else 'upcoming date'}. Please visit your local health center."

            if vax_rec.CHILD and vax_rec.CHILD.USER:
                notification.objects.create(
                    USER=vax_rec.CHILD.USER,
                    message=reminder_msg,
                    notification_date=date.today()
                )
                messages.success(request, f"Reminder notification sent to mother '{vax_rec.CHILD.USER.name}' for child '{vax_rec.CHILD.child_name}'!")
            else:
                messages.warning(request, "Mother's user account not linked to child record.")
            return redirect('/myapp/vaccination_records/')

    scheduled_records = vaccination.objects.filter(CHILD__isnull=False).select_related('CHILD', 'CHILD__USER').order_by('-vaccination_date', '-id')

    # Status KPI Counters
    taken_count = scheduled_records.filter(status='Taken').count()
    missed_count = scheduled_records.filter(status='Missed').count()
    pending_count = scheduled_records.filter(Q(status='Scheduled') | Q(status='Pending') | Q(status='Rescheduled') | Q(status__isnull=True)).count()
    total_count = scheduled_records.count()

    filter_status = request.GET.get('filter_status', 'all')

    context = {
        'scheduled_records': scheduled_records,
        'records_count': total_count,
        'taken_count': taken_count,
        'missed_count': missed_count,
        'pending_count': pending_count,
        'filter_status': filter_status,
    }
    return render(request, 'admin/vaccination_records.html', context)




# ================= DASHBOARDS & OTHER HOMES =================
def adminhome(request):
    # Collect all ASHA workers and Anganwadi teachers
    all_ashas = asha_worker.objects.all().order_by('Full_name')
    all_teachers = anganwadi_teacher.objects.all().order_by('Name')

    total_ashas = all_ashas.count()
    active_ashas = all_ashas.filter(Current_status='Active').count()
    inactive_ashas = total_ashas - active_ashas

    total_teachers = all_teachers.count()
    active_teachers = all_teachers.filter(Current_status='Active').count()
    inactive_teachers = total_teachers - active_teachers

    total_workers = total_ashas + total_teachers
    total_active_workers = active_ashas + active_teachers

    # Group workers by each designated Panchayath Ward
    ward_data = []
    chart_ward_labels = []
    chart_asha_counts = []
    chart_teacher_counts = []

    for idx, ward_full_name in enumerate(PANCHAYATH_AREAS, start=1):
        parts = ward_full_name.split(' - ')
        code = parts[0].strip() if len(parts) > 1 else f"Ward {idx:02d}"
        title = parts[1].strip() if len(parts) > 1 else ward_full_name

        ward_ashas = []
        for w in all_ashas:
            wn = extract_ward_number(w.Area_assigned)
            if wn == idx or code.lower() in str(w.Area_assigned).lower() or title.lower() in str(w.Area_assigned).lower():
                ward_ashas.append(w)

        ward_teachers = []
        for t in all_teachers:
            wn = extract_ward_number(t.center_name) or extract_ward_number(t.Address)
            if wn == idx or code.lower() in str(t.center_name).lower() or title.lower() in str(t.center_name).lower():
                ward_teachers.append(t)

        active_w_ashas = sum(1 for a in ward_ashas if a.Current_status == 'Active')
        active_w_teachers = sum(1 for t in ward_teachers if t.Current_status == 'Active')

        ward_data.append({
            'ward_num': idx,
            'ward_code': code,
            'ward_title': title,
            'ward_full_name': ward_full_name,
            'ashas': ward_ashas,
            'teachers': ward_teachers,
            'asha_count': len(ward_ashas),
            'teacher_count': len(ward_teachers),
            'total_workers': len(ward_ashas) + len(ward_teachers),
            'active_workers': active_w_ashas + active_w_teachers,
            'inactive_workers': (len(ward_ashas) + len(ward_teachers)) - (active_w_ashas + active_w_teachers),
        })

        chart_ward_labels.append(code)
        chart_asha_counts.append(len(ward_ashas))
        chart_teacher_counts.append(len(ward_teachers))

    # Catch-all for any unassigned workers outside standard 1..5
    matched_asha_ids = {a.id for wd in ward_data for a in wd['ashas']}
    matched_teacher_ids = {t.id for wd in ward_data for t in wd['teachers']}
    unassigned_ashas = [a for a in all_ashas if a.id not in matched_asha_ids]
    unassigned_teachers = [t for t in all_teachers if t.id not in matched_teacher_ids]

    if unassigned_ashas or unassigned_teachers:
        ward_data.append({
            'ward_num': 99,
            'ward_code': 'Other',
            'ward_title': 'Other / Unassigned Area',
            'ward_full_name': 'Other / Unassigned Area',
            'ashas': unassigned_ashas,
            'teachers': unassigned_teachers,
            'asha_count': len(unassigned_ashas),
            'teacher_count': len(unassigned_teachers),
            'total_workers': len(unassigned_ashas) + len(unassigned_teachers),
            'active_workers': sum(1 for a in unassigned_ashas if a.Current_status == 'Active') + sum(1 for t in unassigned_teachers if t.Current_status == 'Active'),
            'inactive_workers': (len(unassigned_ashas) + len(unassigned_teachers)) - (sum(1 for a in unassigned_ashas if a.Current_status == 'Active') + sum(1 for t in unassigned_teachers if t.Current_status == 'Active')),
        })
        chart_ward_labels.append('Other')
        chart_asha_counts.append(len(unassigned_ashas))
        chart_teacher_counts.append(len(unassigned_teachers))

    worker_charts = {
        'labels': chart_ward_labels,
        'asha_counts': chart_asha_counts,
        'teacher_counts': chart_teacher_counts,
        'breakdown': {
            'labels': ['Active ASHA Workers', 'Inactive ASHA Workers', 'Active Anganwadi Teachers', 'Inactive Anganwadi Teachers'],
            'data': [active_ashas, inactive_ashas, active_teachers, inactive_teachers]
        }
    }
    worker_charts_json = json.dumps(worker_charts)
    # Beneficiary and clinical healthcare metrics across whole panchayath
    all_mothers_all = user_table.objects.all()
    total_mothers = all_mothers_all.count()
    total_pregnant = sum(1 for m in all_mothers_all if m.is_currently_pregnant)
    total_delivered = sum(1 for m in all_mothers_all if m.has_delivered and not m.is_currently_pregnant)
    total_children = child.objects.count()
    total_vaccinations = vaccination.objects.filter(CHILD__isnull=False).count()
    total_vaccinations_taken = vaccination.objects.filter(CHILD__isnull=False, status='Taken').count()
    total_vaccinations_pending = vaccination.objects.filter(CHILD__isnull=False).filter(Q(status='Scheduled') | Q(status='Pending') | Q(status='Rescheduled')).count()
    total_kits_distributed = nutrition_kit.objects.filter(status__in=['Collected', 'Distributed', 'Issued']).count()

    context = {
        'ward_data': ward_data,
        'total_wards': len(PANCHAYATH_AREAS),
        'total_ashas': total_ashas,
        'active_ashas': active_ashas,
        'inactive_ashas': inactive_ashas,
        'total_teachers': total_teachers,
        'active_teachers': active_teachers,
        'inactive_teachers': inactive_teachers,
        'total_workers': total_workers,
        'total_active_workers': total_active_workers,
        'worker_charts_json': worker_charts_json,
        'total_mothers': total_mothers,
        'total_pregnant': total_pregnant,
        'total_delivered': total_delivered,
        'total_children': total_children,
        'total_vaccinations': total_vaccinations,
        'total_vaccinations_taken': total_vaccinations_taken,
        'total_vaccinations_pending': total_vaccinations_pending,
        'total_kits_distributed': total_kits_distributed,
    }
    return render(request, 'admin/admin_home.html', context)


# ================= ANGANWADI TEACHER VIEWS =================
def get_current_anganwadi_teacher(request):
    """
    Retrieves the currently appropriate Anganwadi Teacher.
    1. If the user is logged in as an Anganwadi Teacher, returns that teacher's profile.
    2. If a specific teacher_id is provided in GET or POST parameter (e.g. Admin view/switch), returns that teacher.
    3. If session has a teacher_id, returns that teacher.
    4. Otherwise, returns the latest registered Anganwadi Teacher created by the admin.
    """
    teacher = None

    # 1. Logged-in Anganwadi Teacher profile takes highest precedence
    if request.user.is_authenticated:
        teacher = anganwadi_teacher.objects.filter(LOGIN=request.user).first()
        if teacher:
            request.session['teacher_id'] = teacher.id
            return teacher

    # 2. Specific teacher_id passed in GET or POST (e.g. Admin inspecting or switching teachers)
    teacher_id = request.GET.get('teacher_id') or request.POST.get('teacher_id')
    if teacher_id:
        teacher = anganwadi_teacher.objects.filter(id=teacher_id).first()
        if teacher:
            request.session['teacher_id'] = teacher.id
            return teacher

    # 3. Session cached teacher_id
    if request.session.get('teacher_id'):
        teacher = anganwadi_teacher.objects.filter(id=request.session.get('teacher_id')).first()
        if teacher:
            return teacher

    # 4. Default to the most recent teacher added by admin
    teacher = anganwadi_teacher.objects.filter(image__isnull=False).exclude(image='').order_by('-id').first()
    if not teacher:
        teacher = anganwadi_teacher.objects.order_by('-id').first()
    if teacher:
        request.session['teacher_id'] = teacher.id
    return teacher


def teacher_home(request):
    teacher = get_current_anganwadi_teacher(request)

    today_dt = date.today()

    area_q = get_area_filter_q(teacher.center_name) if teacher else Q()
    # Verified mothers strictly belonging to the current teacher's ward
    area_mothers = user_table.objects.filter(area_q, ASHA__isnull=False) if teacher else user_table.objects.filter(ASHA__isnull=False)
    verified_mothers = area_mothers.count()
    total_beneficiaries = verified_mothers

    # Distribution records = kits assigned strictly to mothers in this teacher's ward
    distribution_kits = nutrition_kit.objects.filter(USER__in=area_mothers).select_related('USER', 'TEACHER').order_by('-distribution_date', '-id') if teacher else nutrition_kit.objects.filter(USER__ASHA__isnull=False).select_related('USER', 'TEACHER').order_by('-distribution_date', '-id')
    recent_distributions = distribution_kits[:6]

    month_kits_count = distribution_kits.count()
    month_collected_count = distribution_kits.filter(status__in=['Collected', 'Distributed', 'Issued']).count()
    month_missed_count = distribution_kits.filter(status='Missed').count()
    month_pending_count = distribution_kits.filter(status='Pending').count()

    collection_rate_pct = round((month_collected_count / month_kits_count * 100), 1) if month_kits_count > 0 else 0.0

    today_distribution = distribution_kits.filter(distribution_date=today_dt, status__in=['Collected', 'Distributed', 'Issued']).count()
    pending_distribution = month_pending_count

    # Stock inventory configured by this teacher / center
    if teacher:
        ensure_teacher_stock(teacher)
        stock_kits = kit_stock.objects.filter(TEACHER=teacher)
    else:
        stock_kits = kit_stock.objects.all()
    stock_available = sum(k.quantity for k in stock_kits) if stock_kits.exists() else 0

    kit_chart_labels = ['Pregnant Care Kit', 'Lactating Care Kit']
    kit_chart_data = [
        distribution_kits.filter(Q(kit_type__icontains='Pregnant') | Q(product_name__icontains='Pregnant') | Q(kit_type__icontains='Prenatal') | Q(product_name__icontains='Prenatal')).count(),
        distribution_kits.filter(Q(kit_type__icontains='Lactat') | Q(product_name__icontains='Lactat') | Q(kit_type__icontains='Postnatal') | Q(product_name__icontains='Postnatal')).count(),
    ]

    context = {
        'teacher': teacher,
        'assigned_area': teacher.center_name if teacher else 'All Areas',
        'today_distribution': today_distribution,
        'pending_distribution': pending_distribution,
        'verified_mothers': verified_mothers,
        'total_beneficiaries': total_beneficiaries,
        'stock_available': stock_available,
        'total_distributed': month_collected_count,
        'recent_distributions': recent_distributions,
        'month_kits_count': month_kits_count,
        'month_collected_count': month_collected_count,
        'month_pending_count': month_pending_count,
        'month_missed_count': month_missed_count,
        'collection_rate_pct': collection_rate_pct,
        'current_month_name': today_dt.strftime('%B %Y'),
        'kit_chart_labels_json': json.dumps(kit_chart_labels),
        'kit_chart_data_json': json.dumps(kit_chart_data),
    }
    return render(request, 'anganwadi_teacher/anganwadi_home.html', context)


# ================= UPDATE KIT COLLECTION STATUS =================
def update_kit_status(request, kit_id):
    if request.method == "POST":
        kit = get_object_or_404(nutrition_kit, id=kit_id)
        new_status = request.POST.get("status", "").strip()
        next_url = request.POST.get("next", "/myapp/kit_history/").strip()
        if new_status in ["Collected", "Pending", "Missed", "Rescheduled"]:
            kit.status = new_status
            kit.save()
            messages.success(request, f"Collection status for kit issued to '{kit.USER.name}' updated to '{new_status}'!")
        else:
            messages.warning(request, "Invalid status selected.")
        return redirect(next_url if next_url else '/myapp/kit_history/')
    return redirect('/myapp/kit_history/')


DEFAULT_KIT_STOCKS = [
    {
        'kit_category': 'Pregnant Care Kit',
        'product_name': 'Amrutham Prenatal Nutrition Food Pack',
        'product_details': 'Category: Pregnant Care Kit | Items: Fortified Wheat Flour, Daliya, Ragi Mix, Iron & Folic Acid Tablets | Details: Prevents maternal malnutrition and promotes healthy fetal weight gain during pregnancy. | Unit: Packs',
        'stock_unit': 'Packs',
        'quantity': 50,
    },
    {
        'kit_category': 'Pregnant Care Kit',
        'product_name': 'Maternal Medicines & Iron Micronutrient Kit',
        'product_details': 'Category: Pregnant Care Kit | Items: Iron & Folic Acid Tablets, Calcium & Vitamin D3 Tablets, Protein Booster Drink, Medicated Dates | Details: Prevents maternal anemia, supports bone density, and enhances gestational hemoglobin levels. | Unit: Packs',
        'stock_unit': 'Packs',
        'quantity': 50,
    },
    {
        'kit_category': 'Lactating Care Kit',
        'product_name': 'Milk Production & Galactagogue Herbal Pack',
        'product_details': 'Category: Lactating Care Kit | Items: Shatavari Lactation Granules, Herbal Breastmilk Booster Powder, Fenugreek Mix, Energy Dates | Details: Stimulates natural breastmilk synthesis and restores maternal energy levels postpartum. | Unit: Packs',
        'stock_unit': 'Packs',
        'quantity': 50,
    },
    {
        'kit_category': 'Lactating Care Kit',
        'product_name': 'Postnatal Recovery & Protein Vitality Kit',
        'product_details': 'Category: Lactating Care Kit | Items: Multigrain Protein Mix, Dates, Calcium & Vitamin D Supplements, Whey Protein Powder | Details: Accelerates postpartum tissue recovery and provides balanced protein for lactation. | Unit: Packs',
        'stock_unit': 'Packs',
        'quantity': 50,
    },
    {
        'kit_category': 'General Nutrition Kit',
        'product_name': 'Child Growth Micronutrient & Syrup Kit',
        'product_details': 'Category: General Nutrition Kit | Items: Nutritious Cereal Mix, Zinc & Multivitamin Syrup, Fortified Micronutrient Powder | Details: Supports infant cognitive development, immune function, and age-appropriate physical growth. | Unit: Packs',
        'stock_unit': 'Packs',
        'quantity': 50,
    },
]


def ensure_teacher_stock(teacher):
    """Ensures a teacher center has standard kit stock inventory entries configured."""
    if not teacher:
        return
    if kit_stock.objects.filter(TEACHER=teacher).exists():
        return
    for d in DEFAULT_KIT_STOCKS:
        kit_stock.objects.create(
            TEACHER=teacher,
            kit_category=d['kit_category'],
            product_name=d['product_name'],
            product_details=d['product_details'],
            stock_unit=d['stock_unit'],
            quantity=d['quantity']
        )


def manage_kit(request):
    teacher = get_current_anganwadi_teacher(request)
    if teacher:
        ensure_teacher_stock(teacher)
        configured_kits = kit_stock.objects.filter(TEACHER=teacher).order_by('id')
    else:
        configured_kits = kit_stock.objects.all().order_by('id')

    for k in configured_kits:
        details = k.product_details or ""
        items_val = ""
        desc_val = details
        unit_val = k.stock_unit or "Packs"

        if "Items:" in details:
            parts = details.split("Items:", 1)
            after_items = parts[1]
            if "| Details:" in after_items:
                i_part, d_part = after_items.split("| Details:", 1)
                items_val = i_part.strip()
                if "| Unit:" in d_part:
                    d_sub, u_sub = d_part.split("| Unit:", 1)
                    desc_val = d_sub.strip()
                    unit_val = u_sub.strip()
                else:
                    desc_val = d_part.strip()
            elif "| Description:" in after_items:
                i_part, d_part = after_items.split("| Description:", 1)
                items_val = i_part.strip()
                desc_val = d_part.strip()
            else:
                items_val = after_items.strip()
                desc_val = ""
        elif "Category:" in details and "|" in details:
            pipe_parts = [p.strip() for p in details.split("|")]
            for p in pipe_parts:
                if p.startswith("Items:"):
                    items_val = p.replace("Items:", "").strip()
                elif p.startswith("Details:") or p.startswith("Instructions:"):
                    desc_val = p.split(":", 1)[1].strip()
                elif p.startswith("Unit:"):
                    unit_val = p.split(":", 1)[1].strip()

        k.parsed_items = items_val if items_val else (k.product_name if k.product_name else "Standard Kit Items")
        k.parsed_description = desc_val if desc_val else details
        k.parsed_unit = k.stock_unit or unit_val or "Packs"

    total_stock_count = sum(k.quantity for k in configured_kits)

    context = {
        'teacher': teacher,
        'kits': configured_kits,
        'configured_kits': configured_kits,
        'total_stock_count': total_stock_count,
    }
    return render(request, 'anganwadi_teacher/manage_kit.html', context)


def add_nutrition_kit(request):
    teacher = get_current_anganwadi_teacher(request)

    if request.method == "POST":
        kit_category = request.POST.get("kit_category", "Pregnant Care Kit").strip()
        selected_kit_name = request.POST.get("product_name", "").strip() or request.POST.get("kit_name", "").strip()
        custom_kit_name = request.POST.get("custom_product_name", "").strip()
        kit_name = custom_kit_name if (selected_kit_name == "custom" or not selected_kit_name) else selected_kit_name

        if not kit_name:
            kit_name = "Standard Nutrition Kit"

        quantity_str = request.POST.get("quantity", "50").strip()
        stock_unit = request.POST.get("stock_unit", "Packs").strip() or "Packs"
        contents = request.POST.get("contents", "").strip()
        descriptions = request.POST.get("descriptions", "").strip()

        try:
            qty = int(quantity_str) if quantity_str else 50
            if qty <= 0 or qty > 10000:
                messages.warning(request, "Kit stock quantity must be a positive number between 1 and 10,000.")
                return redirect('/myapp/add_nutrition_kit/')
        except ValueError:
            messages.warning(request, "Invalid quantity entered. Please specify a valid integer between 1 and 10,000.")
            return redirect('/myapp/add_nutrition_kit/')

        if not contents:
            contents = "Nutritional Mix & Medical Supplements"
        if not descriptions:
            descriptions = "Supplementary nutrition pack for maternal and child health."

        if teacher:
            product_details_text = f"Category: {kit_category} | Items: {contents} | Details: {descriptions} | Unit: {stock_unit}"
            
            existing_stock = kit_stock.objects.filter(TEACHER=teacher, product_name=kit_name).first()
            if existing_stock:
                existing_stock.quantity += qty
                existing_stock.kit_category = kit_category
                existing_stock.product_details = product_details_text
                existing_stock.stock_unit = stock_unit
                existing_stock.save()
                messages.success(request, f"Added {qty} {stock_unit} stock for '{kit_name}'. Total available stock: {existing_stock.quantity} {stock_unit}.")
            else:
                new_stock = kit_stock.objects.create(
                    TEACHER=teacher,
                    kit_category=kit_category,
                    product_name=kit_name,
                    product_details=product_details_text,
                    stock_unit=stock_unit,
                    quantity=qty
                )
                messages.success(request, f"Stock item '{kit_name}' added with {qty} {stock_unit} quantity!")

        return redirect('/myapp/manage_kit/')

    context = {
        'teacher': teacher,
    }
    return render(request, 'anganwadi_teacher/add_nutrition_kit.html', context)


def decrease_stock(teacher, kit_name, qty):
    """Decrease stock for a given teacher and kit name by qty.
    Returns True if stock was sufficient and deducted, False otherwise.
    """
    if not teacher:
        return True
    
    # 1. Exact match on product name
    stock_item = kit_stock.objects.filter(TEACHER=teacher, product_name__iexact=kit_name).first()
    # 2. Case-insensitive substring match
    if not stock_item:
        stock_item = kit_stock.objects.filter(TEACHER=teacher, product_name__icontains=kit_name).first()
    # 3. Match on category
    if not stock_item:
        stock_item = kit_stock.objects.filter(TEACHER=teacher, kit_category__iexact=kit_name).first()
    if not stock_item:
        stock_item = kit_stock.objects.filter(TEACHER=teacher, kit_category__icontains=kit_name).first()

    # 4. If not initialized, ensure default stocks
    if not stock_item:
        ensure_teacher_stock(teacher)
        stock_item = kit_stock.objects.filter(TEACHER=teacher, product_name__iexact=kit_name).first() or \
                     kit_stock.objects.filter(TEACHER=teacher, product_name__icontains=kit_name).first()

    if not stock_item:
        return False

    if stock_item.quantity < qty:
        return False

    stock_item.quantity -= qty
    stock_item.save()
    return True


def kit_distribution(request):
    teacher = get_current_anganwadi_teacher(request)

    area_q = get_area_filter_q(teacher.center_name) if (teacher and teacher.center_name) else Q()
    all_area_mothers = user_table.objects.filter(area_q, ASHA__isnull=False).order_by('name') if (teacher and teacher.center_name) else user_table.objects.filter(ASHA__isnull=False).order_by('name')

    # Filter mothers to Pregnant Women and Lactating Women (up to 6 months post-delivery) in teacher's area
    today_dt = date.today()
    mothers = []
    for m in all_area_mothers:
        children = child.objects.filter(USER=m).order_by('-date_of_birth')
        if children.exists():
            latest_child = children.first()
            c_dob = getattr(latest_child, 'date_of_birth', None)
            if c_dob:
                try:
                    c_dob_dt = datetime.strptime(str(c_dob), '%Y-%m-%d').date() if isinstance(c_dob, str) else c_dob
                    if 0 <= (today_dt - c_dob_dt).days <= 180:
                        mothers.append(m)
                except ValueError:
                    mothers.append(m)
            else:
                mothers.append(m)
        else:
            mothers.append(m)

    kits_by_category = {
        'Pregnant Care Kit': [
            "Amrutham Prenatal Nutrition Food Pack",
            "Maternal Medicines & Iron Micronutrient Kit"
        ],
        'Lactating Care Kit': [
            "Milk Production & Galactagogue Herbal Pack",
            "Postnatal Recovery & Protein Vitality Kit"
        ],
        'General Nutrition Kit': [
            "Child Growth Micronutrient & Syrup Kit"
        ]
    }

    if teacher:
        ensure_teacher_stock(teacher)
        teacher_stock_kits = kit_stock.objects.filter(TEACHER=teacher)
    else:
        teacher_stock_kits = kit_stock.objects.all()

    for k in teacher_stock_kits:
        cat = k.kit_category or ('Lactating Care Kit' if any(w in k.product_name for w in ['Lactat', 'Postnatal', 'Milk']) else 'Pregnant Care Kit')
        if cat not in kits_by_category:
            kits_by_category[cat] = []
        if k.product_name not in kits_by_category[cat]:
            kits_by_category[cat].append(k.product_name)

    stock_by_name = {
        k.product_name: {
            'quantity': k.quantity,
            'unit': k.stock_unit or 'Packs',
            'category': k.kit_category
        } for k in teacher_stock_kits
    }

    selected_mother_id = request.GET.get("selected_mother", "").strip()

    if request.method == "POST":
        dist_mode = request.POST.get("dist_mode", "single").strip()
        kit_category = request.POST.get("kit_category", "").strip()
        kit_type = request.POST.get("kit_type", "").strip()
        status = request.POST.get("status", "Pending").strip()
        quantity_str = request.POST.get("quantity", "1").strip()
        send_reminder = request.POST.get("send_reminder") == "yes"
        custom_reminder_msg = request.POST.get("reminder_message", "").strip()

        if not kit_type and not kit_category:
            messages.warning(request, "Please select a Kit Category and Kit Item.")
            return redirect('/myapp/kit_distribution/')

        try:
            qty = int(quantity_str) if quantity_str else 1
        except ValueError:
            qty = 1

        dist_date_str = request.POST.get("distribution_date", "").strip()
        dist_date = today_dt
        if dist_date_str:
            try:
                dist_date = datetime.strptime(dist_date_str, '%Y-%m-%d').date()
            except ValueError:
                dist_date = today_dt

        if dist_date < today_dt:
            messages.warning(request, "Invalid Date: Distribution scheduling / pickup date must be today or in the future.")
            return redirect('/myapp/kit_distribution/')

        STOCK_ITEMS_ITEMS = {
            "Amrutham Prenatal Nutrition Food Pack": "Fortified Wheat Flour, Daliya, Ragi Mix, Iron & Folic Acid Tablets",
            "Maternal Medicines & Iron Micronutrient Kit": "Iron & Folic Acid Tablets, Calcium & Vitamin D3 Tablets, Protein Booster Drink, Medicated Dates",
            "Milk Production & Galactagogue Herbal Pack": "Shatavari Lactation Granules, Herbal Breastmilk Booster Powder, Fenugreek Mix, Energy Dates",
            "Postnatal Recovery & Protein Vitality Kit": "Multigrain Protein Mix, Dates, Calcium & Vitamin D Supplements, Whey Protein Powder",
            "Child Growth Micronutrient & Syrup Kit": "Nutritious Cereal Mix, Zinc & Multivitamin Syrup, Fortified Micronutrient Powder"
        }
        item_contents = STOCK_ITEMS_ITEMS.get(kit_type, "Fortified Nutritional Mix & Supplements")
        dist_date_formatted = dist_date.strftime('%b %d, %Y')
        month_name = dist_date.strftime('%B %Y')
        combined_details = f"Category: {kit_category or 'Standard'} | Items: {item_contents}".strip()

        default_msg = f"Your monthly MaatriCare Nutrition Supplement Kit ({kit_type or kit_category} - Category: {kit_category or 'Standard'} | Items Included: {item_contents}) is scheduled for pickup at the Anganwadi Center on {dist_date_formatted}. Please collect it during operating hours."

        kit_name = kit_type or kit_category
        stock_item = kit_stock.objects.filter(TEACHER=teacher, product_name__iexact=kit_name).first() or \
                     kit_stock.objects.filter(TEACHER=teacher, product_name__icontains=kit_name).first()
        available_qty = stock_item.quantity if stock_item else 0
        stock_unit_name = stock_item.stock_unit if stock_item else 'Packs'

        if dist_mode == "bulk":
            target_group = request.POST.get("target_group", "all").strip()

            if target_group == "pregnant" and ("Lactat" in kit_category or "Lactat" in kit_type or "Postnatal" in kit_type or "Milk" in kit_type):
                messages.warning(request, "Eligibility Restriction: Lactating Care Kits cannot be issued to pregnant women. Please select 'Pregnant Care Kit'.")
                return redirect('/myapp/kit_distribution/')

            target_mothers = []
            for m in mothers:
                children = child.objects.filter(USER=m)
                is_lactating = False
                if children.exists():
                    latest_c = children.order_by('-date_of_birth').first()
                    if latest_c.date_of_birth:
                        c_dob_dt = datetime.strptime(str(latest_c.date_of_birth), '%Y-%m-%d').date() if isinstance(latest_c.date_of_birth, str) else latest_c.date_of_birth
                        if 0 <= (today_dt - c_dob_dt).days <= 180:
                            is_lactating = True

                if target_group == "pregnant" and not is_lactating:
                    target_mothers.append(m)
                elif target_group == "lactating" and is_lactating:
                    target_mothers.append(m)
                elif target_group == "all":
                    target_mothers.append(m)

            if not target_mothers:
                messages.warning(request, f"No active beneficiaries found matching the target group '{target_group}'.")
                return redirect('/myapp/kit_distribution/')

            # Filter out mothers who already have a kit this month
            eligible_mothers = []
            skipped_count = 0
            for m in target_mothers:
                already_issued = nutrition_kit.objects.filter(USER=m).filter(
                    Q(distribution_date__year=dist_date.year, distribution_date__month=dist_date.month) |
                    Q(date__year=dist_date.year, date__month=dist_date.month)
                ).exclude(status="Missed").exists()

                if already_issued:
                    skipped_count += 1
                else:
                    eligible_mothers.append(m)

            total_needed = len(eligible_mothers) * qty
            if total_needed > available_qty:
                messages.warning(
                    request,
                    f"Insufficient Stock for Bulk Issue: Distributing {qty} {stock_unit_name} to {len(eligible_mothers)} eligible mothers requires {total_needed} {stock_unit_name}, but center stock has only {available_qty} {stock_unit_name}. Please restock before distributing."
                )
                return redirect('/myapp/kit_distribution/')

            issued_count = 0
            notif_count = 0

            for m in eligible_mothers:
                # Decrease stock before creating distribution
                if not decrease_stock(teacher, kit_name, qty):
                    messages.warning(request, f"Insufficient stock for '{kit_name}'. Bulk distribution stopped after {issued_count} distributions.")
                    break

                nutrition_kit.objects.create(
                    TEACHER=teacher or anganwadi_teacher.objects.first(),
                    USER=m,
                    kit_type=kit_category or kit_type,
                    product_name=kit_type or kit_category,
                    product_details=combined_details,
                    date=today_dt,
                    distribution_date=dist_date,
                    quantity=qty,
                    status=status if status in ["Collected", "Pending", "Missed"] else "Pending"
                )
                issued_count += 1

                if send_reminder or status in ["Pending", "Missed"]:
                    notification.objects.create(
                        USER=m,
                        message=custom_reminder_msg or default_msg,
                        notification_date=today_dt
                    )
                    notif_count += 1

            # Refresh stock_item after deductions
            if stock_item:
                stock_item.refresh_from_db()
                remaining_qty = stock_item.quantity
            else:
                remaining_qty = 0

            msg = f"Bulk Distribution Complete! Scheduled '{kit_name}' for {issued_count} mother(s) for pickup on {dist_date_formatted}. Center stock updated ({remaining_qty} {stock_unit_name} remaining). {notif_count} pickup reminder notifications sent."
            if skipped_count > 0:
                msg += f" ({skipped_count} mother(s) skipped as they already have an active/collected kit for {month_name})."
            messages.success(request, msg)
            return redirect('/myapp/kit_history/')

        else:
            mother_id = request.POST.get("mother_id")
            if not mother_id:
                messages.warning(request, "Please select a beneficiary mother.")
                return redirect('/myapp/kit_distribution/')

            mother = get_object_or_404(all_area_mothers, id=mother_id)
            has_given_birth = child.objects.filter(USER=mother).exists()

            if not has_given_birth and ("Lactat" in kit_category or "Lactat" in kit_type or "Postnatal" in kit_type or "Milk" in kit_type):
                messages.warning(
                    request,
                    f"Eligibility Restriction: Lactating Care Kits can only be issued to mothers who have given birth. Beneficiary '{mother.name}' is currently pregnant and is eligible for Pregnant Care Kits."
                )
                return redirect('/myapp/kit_distribution/')

            existing_kit = nutrition_kit.objects.filter(
                USER=mother
            ).filter(
                Q(distribution_date__year=dist_date.year, distribution_date__month=dist_date.month) |
                Q(date__year=dist_date.year, date__month=dist_date.month)
            ).exclude(status="Missed").first()

            if existing_kit:
                messages.warning(
                    request,
                    f"Duplicate Distribution Restriction: Beneficiary '{mother.name}' has already been scheduled/issued a nutrition kit for {month_name} (Kit: '{existing_kit.product_name or existing_kit.kit_type}', Status: {existing_kit.status}). A beneficiary can only receive 1 kit per calendar month."
                )
                return redirect('/myapp/kit_distribution/')

            # Check stock before single distribution
            if available_qty < qty:
                messages.warning(
                    request,
                    f"Insufficient Stock: '{kit_name}' has only {available_qty} {stock_unit_name} available in inventory (requested: {qty} {stock_unit_name}). Please restock before distributing."
                )
                return redirect('/myapp/kit_distribution/')

            # Decrease stock for single distribution
            if not decrease_stock(teacher, kit_name, qty):
                messages.warning(request, f"Insufficient stock for '{kit_name}'. Distribution aborted.")
                return redirect('/myapp/kit_distribution/')

            new_kit = nutrition_kit.objects.create(
                TEACHER=teacher or anganwadi_teacher.objects.first(),
                USER=mother,
                kit_type=kit_category or kit_type,
                product_name=kit_type or kit_category,
                product_details=combined_details,
                date=today_dt,
                distribution_date=dist_date,
                quantity=qty,
                status=status if status in ["Collected", "Pending", "Missed"] else "Pending"
            )

            if send_reminder or status in ["Pending", "Missed"]:
                notification.objects.create(
                    USER=mother,
                    message=custom_reminder_msg or default_msg,
                    notification_date=today_dt
                )

            # Refresh stock_item after deduction
            if stock_item:
                stock_item.refresh_from_db()
                remaining_qty = stock_item.quantity
            else:
                remaining_qty = 0

            messages.success(request, f"Nutrition kit '{kit_name}' scheduled for '{mother.name}' for pickup on {dist_date_formatted} (Status: {status}). Stock updated: {remaining_qty} {stock_unit_name} remaining.")
            return redirect('/myapp/kit_history/')

    # Client-side map for instant auto-filling case no & village
    mothers_map = {}
    for idx, m in enumerate(mothers, start=1):
        has_given_birth = m.has_delivered_child
        is_pregnant = m.is_currently_pregnant
        existing_kit_month = nutrition_kit.objects.filter(
            USER=m
        ).filter(
            Q(distribution_date__year=today_dt.year, distribution_date__month=today_dt.month) |
            Q(date__year=today_dt.year, date__month=today_dt.month)
        ).exclude(status="Missed").first()

        mothers_map[str(m.id)] = {
            'id': m.id,
            'name': m.name,
            'case_no': f"MC-MOTH-{1000 + m.id}",
            'village': m.Address or "Panchayath Ward 04",
            'phone': str(m.phone),
            'husband': m.husband_name,
            'has_given_birth': has_given_birth,
            'is_pregnant': is_pregnant,
            'pregnancy_month': m.gestation_month if is_pregnant else None,
            'gestation_weeks': m.gestation_weeks if is_pregnant else None,
            'status_display': m.pregnancy_status_display if is_pregnant else ("Postpartum / Given Birth" if has_given_birth else "Registered Mother"),
            'already_issued_this_month': bool(existing_kit_month),
            'issued_kit_name': (existing_kit_month.product_name or existing_kit_month.kit_type) if existing_kit_month else None,
            'issued_kit_status': existing_kit_month.status if existing_kit_month else None,
        }

    context = {
        'teacher': teacher,
        'mothers': mothers,
        'kits_by_category_json': json.dumps(kits_by_category),
        'stock_by_name_json': json.dumps(stock_by_name),
        'selected_mother_id': selected_mother_id,
        'mothers_json': json.dumps(mothers_map),
        'today_date': date.today().strftime('%Y-%m-%d'),
    }
    return render(request, 'anganwadi_teacher/kit_distribution.html', context)


def kit_history(request):
    teacher = get_current_anganwadi_teacher(request)

    area_q = get_area_filter_q(teacher.center_name) if (teacher and teacher.center_name) else Q()
    area_mothers = user_table.objects.filter(area_q, ASHA__isnull=False) if (teacher and teacher.center_name) else user_table.objects.filter(ASHA__isnull=False)
    verified_mothers = area_mothers.count()

    total_mothers = user_table.objects.filter(area_q).count() if (teacher and teacher.center_name) else user_table.objects.count()
    other_beneficiaries = total_mothers - verified_mothers

    distributions = nutrition_kit.objects.filter(USER__in=area_mothers).select_related('USER', 'TEACHER') if (teacher and teacher.center_name) else nutrition_kit.objects.filter(USER__ASHA__isnull=False).select_related('USER', 'TEACHER')

    available_kit_types = ['Pregnant Care Kit', 'Lactating Care Kit']

    search_query = request.GET.get("q", "").strip()
    if search_query:
        distributions = distributions.filter(
            Q(USER__name__icontains=search_query) |
            Q(USER__husband_name__icontains=search_query) |
            Q(USER__phone__icontains=search_query) |
            Q(kit_type__icontains=search_query) |
            Q(product_name__icontains=search_query) |
            Q(product_details__icontains=search_query)
        )

    kit_type_filter = request.GET.get("kit_type", "").strip()
    if kit_type_filter and kit_type_filter not in ["All Kit Types", "All Categories"]:
        if "Pregnant" in kit_type_filter:
            distributions = distributions.filter(
                Q(kit_type__icontains='Pregnant') | Q(product_name__icontains='Pregnant') | Q(product_details__icontains='Pregnant') | Q(kit_type__icontains='Prenatal')
            )
        elif "Lactat" in kit_type_filter:
            distributions = distributions.filter(
                Q(kit_type__icontains='Lactat') | Q(product_name__icontains='Lactat') | Q(product_details__icontains='Lactat') | Q(kit_type__icontains='Postnatal')
            )
        else:
            distributions = distributions.filter(
                Q(kit_type__icontains=kit_type_filter) | Q(product_name__icontains=kit_type_filter)
            )

    status_filter = request.GET.get("status", "").strip()
    if status_filter and status_filter != "All Statuses":
        distributions = distributions.filter(status__iexact=status_filter)

    date_filter = request.GET.get("date", "").strip()
    if date_filter:
        try:
            parsed_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            distributions = distributions.filter(distribution_date=parsed_date)
        except ValueError:
            pass

    sort_order = request.GET.get("sort", "newest")
    if sort_order == "oldest":
        distributions = distributions.order_by('distribution_date', 'id')
    else:
        distributions = distributions.order_by('-distribution_date', '-id')

    # Metrics for bottom summary cards strictly isolated to this teacher's ward
    all_kits = distributions
    total_distributed = all_kits.count()
    collected_count = all_kits.filter(status__iexact='Collected').count()
    pending_count = all_kits.filter(Q(status__iexact='Pending') | Q(status__iexact='Rescheduled')).count()
    missed_count = all_kits.filter(status__iexact='Missed').count()

    context = {
        'teacher': teacher,
        'distributions': distributions,
        'kit_history': distributions,
        'available_kit_types': available_kit_types,
        'search_query': search_query,
        'kit_type_filter': kit_type_filter,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'sort_order': sort_order,
        'total_count': distributions.count(),
        'total_distributed': total_distributed,
        'collected_count': collected_count,
        'pending_count': pending_count,
        'missed_count': missed_count,
    }
    return render(request, 'anganwadi_teacher/kit_history.html', context)


# ================= RESCHEDULE MISSED NUTRITION KIT PICKUP =================
def reschedule_kit(request):
    """
    Reschedules missed nutrition kit distribution pickup date, resets status to 'Rescheduled',
    and sends automated reminder notification message to the mother.
    """
    if request.method == "POST":
        kit_id = request.POST.get("kit_id")
        new_date_str = request.POST.get("new_pickup_date", "").strip()
        reminder_msg = request.POST.get("reminder_message", "").strip()

        teacher = get_current_anganwadi_teacher(request)
        area_q = get_area_filter_q(teacher.center_name) if (teacher and teacher.center_name) else Q()
        area_mothers = user_table.objects.filter(area_q, ASHA__isnull=False) if (teacher and teacher.center_name) else user_table.objects.filter(ASHA__isnull=False)

        kit = get_object_or_404(
            nutrition_kit.objects.filter(USER__in=area_mothers) if (teacher and teacher.center_name) else nutrition_kit.objects.all(),
            id=kit_id
        )
        
        new_date = date.today()
        if new_date_str:
            try:
                new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
            except ValueError:
                new_date = date.today()

        kit.distribution_date = new_date
        kit.status = "Rescheduled"
        kit.save()

        # Automatically Send Reschedule Reminder Notification to Mother
        if kit.USER:
            final_msg = reminder_msg if reminder_msg else f"Nutrition Kit Pickup Rescheduled: Your pickup ({kit.kit_type}) for {kit.USER.name} has been rescheduled to {new_date.strftime('%b %d, %Y')}."
            
            kit_notification.objects.create(
                NUTRITION=kit,
                USER=kit.USER,
                notification_message=final_msg,
                notification_date=date.today()
            )
            notification.objects.create(
                USER=kit.USER,
                message=final_msg,
                notification_date=date.today()
            )

        messages.success(request, f"Nutrition kit pickup for '{kit.USER.name}' rescheduled to {new_date.strftime('%b %d, %Y')} and reminder notification sent to mother!")
    return redirect('/myapp/kit_history/')


# ================= ACTIVE BENEFICIARIES DIRECTORY (READ-ONLY FOR ANGANWADI) =================
def teacher_beneficiaries(request):
    teacher = get_current_anganwadi_teacher(request)

    area_q = get_area_filter_q(teacher.center_name) if (teacher and teacher.center_name) else Q()
    all_mothers = user_table.objects.filter(area_q, ASHA__isnull=False).order_by('name') if (teacher and teacher.center_name) else user_table.objects.filter(ASHA__isnull=False).order_by('name')

    search_query = request.GET.get("q", "").strip().lower()

    today_dt = date.today()
    mothers_list = []
    total_pregnant_count = 0
    total_lactating_count = 0

    for m in all_mothers:
        if m.is_currently_pregnant:
            status = 'Pregnant'
            total_pregnant_count += 1
        elif m.has_delivered_child:
            children = child.objects.filter(USER=m).order_by('-date_of_birth')
            latest_child = children.first()
            c_dob = getattr(latest_child, 'date_of_birth', None)
            if c_dob:
                try:
                    c_dob_dt = datetime.strptime(str(c_dob), '%Y-%m-%d').date() if isinstance(c_dob, str) else c_dob
                    age_in_days = (today_dt - c_dob_dt).days
                    if 0 <= age_in_days <= 180:
                        status = 'Lactating'
                        total_lactating_count += 1
                    else:
                        # Exceeded 6 months post-delivery and not currently pregnant
                        continue
                except ValueError:
                    status = 'Lactating'
                    total_lactating_count += 1
            else:
                status = 'Lactating'
                total_lactating_count += 1
        else:
            status = 'Pregnant'
            total_pregnant_count += 1

        if search_query:
            if not (
                search_query in m.name.lower() or
                search_query in m.husband_name.lower() or
                search_query in str(m.phone) or
                search_query in (m.Address or "").lower()
            ):
                continue

        # Check current month kit collection status
        current_month_kits = nutrition_kit.objects.filter(USER=m).filter(
            Q(distribution_date__year=today_dt.year, distribution_date__month=today_dt.month) |
            Q(date__year=today_dt.year, date__month=today_dt.month)
        ).order_by('-distribution_date', '-id')

        current_month_kit = current_month_kits.first()
        kit_collected_this_month = current_month_kits.filter(
            status__in=['Collected', 'Distributed', 'Issued']
        ).exists()

        last_kit = nutrition_kit.objects.filter(USER=m).order_by('-distribution_date').first()
        total_kits_received = nutrition_kit.objects.filter(USER=m).count()

        mothers_list.append({
            'obj': m,
            'status': status,
            'last_kit': last_kit,
            'total_kits': total_kits_received,
            'current_month_kit': current_month_kit,
            'kit_collected_this_month': kit_collected_this_month,
        })

    assigned_area = teacher.center_name if (teacher and teacher.center_name) else 'All Areas'

    context = {
        'teacher': teacher,
        'assigned_area': assigned_area,
        'mothers_list': mothers_list,
        'today_dt': today_dt,
        'search_query': request.GET.get("q", "").strip(),
        'total_pregnant_count': total_pregnant_count,
        'total_lactating_count': total_lactating_count,
        'total_eligible_mothers': total_pregnant_count + total_lactating_count,
    }
    return render(request, 'anganwadi_teacher/teacher_beneficiaries.html', context)


# ================= SEND KIT REMINDER NOTIFICATION (ANGANWADI) =================
def send_kit_reminder(request):
    if request.method == "POST":
        mother_id = request.POST.get("mother_id", "").strip()
        reminder_msg = request.POST.get("reminder_message", "").strip()

        if not reminder_msg:
            reminder_msg = "Your monthly MaatriCare Nutrition Supplement Kit is ready for pickup at the Anganwadi Center. Please collect it between 9:00 AM and 4:00 PM."

        teacher = get_current_anganwadi_teacher(request)

        area_q = get_area_filter_q(teacher.center_name) if (teacher and teacher.center_name) else Q()
        area_mothers = user_table.objects.filter(area_q, ASHA__isnull=False) if (teacher and teacher.center_name) else user_table.objects.filter(ASHA__isnull=False)

        today_dt = date.today()
        month_name = today_dt.strftime('%B %Y')

        if mother_id:
            mother = get_object_or_404(area_mothers, id=mother_id)

            # Check if this mother already collected her kit for the current month
            collected_this_month = nutrition_kit.objects.filter(USER=mother).filter(
                Q(distribution_date__year=today_dt.year, distribution_date__month=today_dt.month) |
                Q(date__year=today_dt.year, date__month=today_dt.month)
            ).filter(status__in=['Collected', 'Distributed', 'Issued']).exists()

            if collected_this_month:
                messages.warning(
                    request,
                    f"Reminder blocked: '{mother.name}' has already collected her monthly nutrition kit for {month_name}. Supplemental kits are issued once per month, so reminders cannot be sent again for this month."
                )
            else:
                notification.objects.create(
                    USER=mother,
                    message=reminder_msg,
                    notification_date=today_dt
                )
                messages.success(request, f"Pickup reminder sent to '{mother.name}' (Ph: {mother.phone}) successfully!")
        else:
            # Broadcast reminder: Send only to eligible mothers who have NOT collected their kit for the current month
            uncollected_mothers = []
            for m in area_mothers:
                collected = nutrition_kit.objects.filter(USER=m).filter(
                    Q(distribution_date__year=today_dt.year, distribution_date__month=today_dt.month) |
                    Q(date__year=today_dt.year, date__month=today_dt.month)
                ).filter(status__in=['Collected', 'Distributed', 'Issued']).exists()
                if not collected:
                    uncollected_mothers.append(m)

            if not uncollected_mothers:
                messages.info(request, f"All mothers in your area have already collected their nutrition kit for {month_name}! No pending reminders needed.")
            else:
                for m in uncollected_mothers:
                    notification.objects.create(
                        USER=m,
                        message=reminder_msg,
                        notification_date=today_dt
                    )
                messages.success(request, f"Kit pickup reminder sent to {len(uncollected_mothers)} mother(s) with pending/missed kit collection for {month_name}!")

    return redirect('/myapp/teacher_beneficiaries/')


# ================= ANGANWADI TEACHER PROFILE VIEWS =================
def teacher_profile_view(request):
    teacher = get_current_anganwadi_teacher(request)

    if request.method == "POST":
        action = request.POST.get("action", "").strip()

        # 1. Update Profile Information (name, center, image, phone, email, address, etc.)
        if action == "update_profile":
            name = request.POST.get("name", "").strip()
            center_name = request.POST.get("center_name", "").strip()
            phone = request.POST.get("phone", "").strip()
            email = request.POST.get("email", "").strip()
            address = request.POST.get("address", "").strip()
            gender = request.POST.get("gender", "").strip()
            qualification = request.POST.get("qualification", "").strip()
            dob_str = request.POST.get("dob", "").strip()
            joining_date_str = request.POST.get("joining_date", "").strip()
            status = request.POST.get("status", "").strip()
            image_file = request.FILES.get("image")

            if name:
                teacher.Name = name
            if center_name:
                teacher.center_name = center_name
            if phone:
                cleaned_phone = "".join(filter(str.isdigit, phone))
                if cleaned_phone:
                    teacher.Phone = int(cleaned_phone)
            if email:
                if not re.match(EMAIL_REGEX, email, re.IGNORECASE):
                    messages.warning(request, "Email address must be a valid @gmail.com address (e.g., example@gmail.com).")
                    return redirect('/myapp/teacher_profile/')
                if (User.objects.filter(email__iexact=email).exclude(id=teacher.LOGIN_id).exists() or 
                    anganwadi_teacher.objects.filter(Email__iexact=email).exclude(id=teacher.id).exists()):
                    messages.warning(request, f"The email address '{email}' is already in use by another user.")
                    return redirect('/myapp/teacher_profile/')
                teacher.Email = email
                if teacher.LOGIN:
                    teacher.LOGIN.email = email
                    teacher.LOGIN.save()
            if address:
                teacher.Address = address
            if gender:
                teacher.Gender = gender
            if qualification:
                teacher.Qualification = qualification
            if status:
                teacher.Current_status = status
            if joining_date_str:
                try:
                    teacher.joining_date = datetime.strptime(joining_date_str, "%Y-%m-%d").date()
                except Exception:
                    pass
            if dob_str:
                try:
                    parsed_dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
                    teacher.dob = parsed_dob
                    today = date.today()
                    teacher.Age = today.year - parsed_dob.year - ((today.month, today.day) < (parsed_dob.month, parsed_dob.day))
                except Exception:
                    pass
            if image_file:
                teacher.image = image_file

            teacher.save()
            if teacher.LOGIN:
                if name:
                    teacher.LOGIN.first_name = name
                teacher.LOGIN.save()

            messages.success(request, "Your profile details have been updated successfully!")
            return redirect(f'/myapp/teacher_profile/?teacher_id={teacher.id}')

        # 2. Change Password
        elif action == "change_password":
            current_password = request.POST.get("current_password", "").strip()
            new_password = request.POST.get("new_password", "").strip()
            confirm_password = request.POST.get("confirm_password", "").strip()

            user = teacher.LOGIN if (teacher and teacher.LOGIN) else (request.user if request.user.is_authenticated else None)

            if not user:
                messages.error(request, "No linked user account found for this profile.")
                return redirect(f'/myapp/teacher_profile/?tab=security&teacher_id={teacher.id if teacher else ""}')

            if user.has_usable_password() and current_password:
                if not user.check_password(current_password):
                    messages.warning(request, "Incorrect current password. Please re-enter your existing password.")
                    return redirect(f'/myapp/teacher_profile/?tab=security&teacher_id={teacher.id}')

            if len(new_password) < 6:
                messages.warning(request, "New password must be at least 6 characters in length.")
                return redirect(f'/myapp/teacher_profile/?tab=security&teacher_id={teacher.id}')

            if new_password != confirm_password:
                messages.warning(request, "New password and Confirm password do not match.")
                return redirect('/myapp/teacher_profile/?tab=security')

            user.set_password(new_password)
            user.save()

            if request.user.is_authenticated and request.user == user:
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)

            messages.success(request, "Password updated successfully!")
            return redirect('/myapp/teacher_profile/?tab=security')

    context = {
        'teacher': teacher,
        'panchayath_areas': PANCHAYATH_AREAS,
        'active_tab': request.GET.get('tab', 'details'),
    }
    return render(request, 'anganwadi_teacher/teacher_profile.html', context)



def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('/myapp/login/')


def get_current_asha_worker(request):
    """
    Retrieves the currently appropriate ASHA worker.
    1. If user is authenticated as an ASHA worker, returns her own profile record.
    2. If a specific worker_id is provided in GET or POST parameter, returns that worker.
    3. If session has an asha_id, returns that worker.
    4. Otherwise, returns the latest registered ASHA worker created by the admin.
    """
    # 1. Logged-in ASHA worker profile
    if request.user.is_authenticated:
        worker = asha_worker.objects.filter(LOGIN=request.user).first()
        if worker:
            request.session['asha_id'] = worker.id
            return worker

    # 2. Specific worker_id passed in GET or POST (e.g. Admin inspecting or switching workers)
    worker_id = request.GET.get('worker_id') or request.POST.get('worker_id')
    if worker_id:
        worker = asha_worker.objects.filter(id=worker_id).first()
        if worker:
            request.session['asha_id'] = worker.id
            return worker

    # 3. Session cached asha_id
    if request.session.get('asha_id'):
        worker = asha_worker.objects.filter(id=request.session.get('asha_id')).first()
        if worker:
            return worker

    # 4. Default to the most recent ASHA worker added by admin
    worker = asha_worker.objects.filter(image__isnull=False).exclude(image='').order_by('-id').first()
    if not worker:
        worker = asha_worker.objects.order_by('-id').first()
    if worker:
        request.session['asha_id'] = worker.id
    return worker


def ashaworker_home(request):
    worker = get_current_asha_worker(request)

    area_q = get_area_filter_q(worker.Area_assigned) if worker else Q()
    area_mothers = user_table.objects.filter(area_q) if worker else user_table.objects.all()

    # Handle quick mother creation from modal (automatically assigned to worker's area)
    if request.method == "POST" and request.POST.get("action_type") == "add_mother":
        name = request.POST.get("name", "").strip()
        husband_name = request.POST.get("husband_name", "").strip()
        dob = request.POST.get("dob", "").strip()
        age = request.POST.get("age", "").strip()
        phone = request.POST.get("phone", "").strip()
        blood_group = request.POST.get("blood_group", "").strip()
        panchayath = request.POST.get("panchayath", "Kozhikode Grama Panchayath").strip()
        area = (worker.Area_assigned if worker else request.POST.get("area", "").strip()) or "Ward 01 - Main Community Center"
        address = request.POST.get("address", "").strip()

        if name and husband_name and phone:
            user_table.objects.create(
                ASHA=worker,
                name=name,
                husband_name=husband_name,
                dob=dob if dob else "1998-01-01",
                age=int(age) if age.isdigit() else 25,
                phone=int(phone) if phone.isdigit() else 9876543210,
                blood_group=blood_group or "O+",
                panchayath=panchayath,
                area=area,
                Address=address or f"{area} Residence",
                district="Kozhikode",
                state="Kerala",
                pincode="673001",
                Email=f"{name.lower().replace(' ', '')}@gmail.com"
            )
            messages.success(request, f"Mother record for '{name}' added in {area} successfully!")
            return redirect('/myapp/ashaworker_home/')

    # Query counts accurately for this ASHA worker (strictly isolated to women in worker's ward only)
    w_mothers = area_mothers.filter(ASHA__isnull=False).distinct() if worker else user_table.objects.filter(ASHA__isnull=False)

    # All children strictly for mothers residing in this worker's ward only or assigned to worker
    all_children_qs = child.objects.filter(Q(USER__in=area_mothers) | Q(ASHA=worker)).select_related('USER', 'ASHA').distinct() if worker else child.objects.all().select_related('USER', 'ASHA').distinct()

    w_delivered_user_ids = set(all_children_qs.values_list('USER_id', flat=True))
    w_all_mother_ids = set(w_mothers.values_list('id', flat=True))

    pregnant_count = sum(1 for m in w_mothers if m.is_currently_pregnant)
    delivered_count = sum(1 for m in w_mothers if m.has_delivered and not m.is_currently_pregnant)
    total_mothers_count = w_mothers.count()
    newborns_count = all_children_qs.count()
    total_children_count = all_children_qs.count()
    # Distinct children in this area who have growth records recorded
    growth_records_count = child_growth_record.objects.filter(CHILD__in=all_children_qs).values('CHILD').distinct().count()
    total_growth_logs = child_growth_record.objects.filter(CHILD__in=all_children_qs).count()
    vaccinations_count = vaccination.objects.filter(CHILD__in=all_children_qs).count()
    vaccinations_taken = vaccination.objects.filter(CHILD__in=all_children_qs, status='Taken').count()

    # Calculate child growth status breakdown for dashboard overview
    normal_count = 0
    underweight_count = 0
    attention_count = 0

    for ch in all_children_qs:
        latest_rec = child_growth_record.objects.filter(CHILD=ch).order_by('-growth_date', '-id').first()
        ch_status = latest_rec.health_condition if latest_rec else "Healthy / Normal"
        if "underweight" in ch_status.lower():
            underweight_count += 1
        elif "malnutrition" in ch_status.lower() or "stunted" in ch_status.lower():
            attention_count += 1
        else:
            normal_count += 1

    nutritional_chart_data = {
        'labels': ['Normal Growth', 'Underweight', 'Needs Attention'],
        'counts': [normal_count, underweight_count, attention_count],
    }

    mothers_qs = w_mothers.order_by('-id')

    # Build list of upcoming/scheduled checkup visits based on pregnancy records
    pregnancy_visit_schedule = []
    today = date.today()

    for mother in w_mothers:
        # Include mothers who are currently pregnant
        if not mother.is_currently_pregnant:
            continue

        latest_rec = pregnancy_record.objects.filter(USER=mother).order_by('-checkup_date', '-id').first()
        if latest_rec:
            next_date = latest_rec.next_checkup_date or (latest_rec.checkup_date + timedelta(days=30))
            days_left = (next_date - today).days
            overdue_days = abs(days_left) if days_left < 0 else 0
            pregnancy_visit_schedule.append({
                'mother': mother,
                'name': mother.name,
                'husband_name': mother.husband_name,
                'phone': mother.phone,
                'latest_visit_date': latest_rec.checkup_date,
                'next_visit_date': next_date,
                'health_status': latest_rec.health_status,
                'days_left': days_left,
                'overdue_days': overdue_days,
                'has_record': True,
            })
        else:
            pregnancy_visit_schedule.append({
                'mother': mother,
                'name': mother.name,
                'husband_name': mother.husband_name,
                'phone': mother.phone,
                'latest_visit_date': None,
                'next_visit_date': None,
                'health_status': 'Pending',
                'days_left': None,
                'overdue_days': 0,
                'has_record': False,
            })

    # Sort: records with next visit dates first (nearest upcoming date first)
    pregnancy_visit_schedule.sort(
        key=lambda x: (0 if x['has_record'] else 1, x['next_visit_date'] if x['next_visit_date'] else date.max)
    )

    # Search filter within this area
    search_query = request.GET.get("search", "").strip()
    if search_query:
        mothers_qs = mothers_qs.filter(
            Q(name__icontains=search_query) |
            Q(husband_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(panchayath__icontains=search_query) |
            Q(area__icontains=search_query)
        )

    # Detect newly registered / unverified mothers pending verification in this worker's area
    unverified_mothers_qs = user_table.objects.filter(area_q, ASHA__isnull=True).order_by('-id') if worker else user_table.objects.filter(ASHA__isnull=True).order_by('-id')
    new_registered_mothers = list(unverified_mothers_qs)
    has_new_registration = len(new_registered_mothers) > 0

    context = {
        'worker': worker,
        'assigned_area': worker.Area_assigned if worker else 'All Areas',
        'pregnant_count': pregnant_count,
        'delivered_count': delivered_count,
        'total_mothers_count': total_mothers_count,
        'newborns_count': newborns_count,
        'growth_records_count': growth_records_count,
        'total_growth_logs': total_growth_logs,
        'vaccinations_count': vaccinations_count,
        'vaccinations_taken': vaccinations_taken,
        'normal_count': normal_count,
        'underweight_count': underweight_count,
        'attention_count': attention_count,
        'total_children_count': total_children_count,
        'nutritional_chart_json': json.dumps(nutritional_chart_data),
        'active_mothers': mothers_qs,
        'pregnancy_visit_schedule': pregnancy_visit_schedule,
        'search_query': search_query,
        'panchayath_areas': PANCHAYATH_AREAS,
        'new_registered_mothers': new_registered_mothers,
        'has_new_registration': has_new_registration,
    }
    return render(request, 'ashawoker/asha_home.html', context)


# ================= ASHA WORKER PROFILE VIEWS =================
def ashaworker_profile_view(request):
    worker = get_current_asha_worker(request)

    if request.method == "POST":
        action = request.POST.get("action", "").strip()

        # 1. Update Profile Information (name, image, phone, email, address, etc.)
        # Note: Assigned Panchayath/Ward is strictly assigned by Admin and cannot be changed by ASHA
        if action == "update_profile":
            full_name = request.POST.get("full_name", "").strip()
            phone = request.POST.get("phone", "").strip()
            email = request.POST.get("email", "").strip()
            address = request.POST.get("address", "").strip()
            qualification = request.POST.get("qualification", "").strip()
            # Admin-assigned fields (Area_assigned, Joining_date, Current_status) are protected and can only be modified by Admin
            dob_str = request.POST.get("dob", "").strip()
            image_file = request.FILES.get("image")

            if full_name:
                worker.Full_name = full_name
            if phone:
                cleaned_phone = "".join(filter(str.isdigit, phone))
                if cleaned_phone:
                    worker.Phone = int(cleaned_phone)
            if email:
                if not re.match(EMAIL_REGEX, email, re.IGNORECASE):
                    messages.warning(request, "Email address must be a valid @gmail.com address (e.g., example@gmail.com).")
                    return redirect('/myapp/ashaworker_profile/')
                if (User.objects.filter(email__iexact=email).exclude(id=worker.LOGIN_id).exists() or 
                    asha_worker.objects.filter(Email__iexact=email).exclude(id=worker.id).exists()):
                    messages.warning(request, f"The email address '{email}' is already in use by another user.")
                    return redirect('/myapp/ashaworker_profile/')
                worker.Email = email
                if worker.LOGIN:
                    worker.LOGIN.email = email
                    worker.LOGIN.save()
            if address:
                worker.Address = address
            if qualification:
                worker.Qualification = qualification
            if dob_str:
                try:
                    parsed_dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
                    worker.dob = parsed_dob
                    today = date.today()
                    worker.Age = today.year - parsed_dob.year - ((today.month, today.day) < (parsed_dob.month, parsed_dob.day))
                except Exception:
                    pass
            if image_file:
                worker.image = image_file

            worker.save()
            if worker.LOGIN:
                if full_name:
                    worker.LOGIN.first_name = full_name
                worker.LOGIN.save()

            messages.success(request, "Your profile details have been updated successfully!")
            return redirect('/myapp/ashaworker_profile/?tab=details')

        # 2. Change Password
        elif action == "change_password":
            current_password = request.POST.get("current_password", "").strip()
            new_password = request.POST.get("new_password", "").strip()
            confirm_password = request.POST.get("confirm_password", "").strip()

            user = worker.LOGIN if (worker and worker.LOGIN) else (request.user if request.user.is_authenticated else None)

            if not user:
                messages.error(request, "No linked user account found for this profile.")
                return redirect('/myapp/ashaworker_profile/?tab=security')

            # Verify current password if user has usable password
            if user.has_usable_password() and current_password:
                if not user.check_password(current_password):
                    messages.warning(request, "Incorrect current password. Please re-enter your existing password.")
                    return redirect('/myapp/ashaworker_profile/?tab=security')

            if len(new_password) < 6:
                messages.warning(request, "New password must be at least 6 characters in length.")
                return redirect('/myapp/ashaworker_profile/?tab=security')

            if new_password != confirm_password:
                messages.warning(request, "New password and Confirm password do not match.")
                return redirect('/myapp/ashaworker_profile/?tab=security')

            user.set_password(new_password)
            user.save()

            if request.user.is_authenticated and request.user == user:
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)

            messages.success(request, "Password updated successfully!")
            return redirect('/myapp/ashaworker_profile/?tab=security')

    context = {
        'worker': worker,
        'panchayath_areas': PANCHAYATH_AREAS,
        'active_tab': request.GET.get('tab', 'details'),
    }
    return render(request, 'ashawoker/asha_profile.html', context)



# ================= MOTHER VERIFICATION VIEWS (ASHA WORKER) =================
def verify_mother(request):
    worker = get_current_asha_worker(request)

    area_q = get_area_filter_q(worker.Area_assigned) if worker else Q()
    
    # Active ASHA workers in this specific ward for assignment dropdown
    if worker:
        w_num = extract_ward_number(worker.Area_assigned)
        if w_num:
            area_workers = asha_worker.objects.filter(
                Q(Area_assigned__icontains=f"Ward 0{w_num}") |
                Q(Area_assigned__icontains=f"Ward {w_num}")
            ).order_by('Full_name')
        else:
            area_workers = asha_worker.objects.filter(Area_assigned=worker.Area_assigned).order_by('Full_name')
        if not area_workers.exists():
            area_workers = [worker]
    else:
        area_workers = asha_worker.objects.all().order_by('Full_name')

    # Base QuerySet STRICTLY isolated to this worker's assigned area
    base_area_mothers = user_table.objects.filter(area_q) if worker else user_table.objects.all()

    # Handle POST Actions
    if request.method == "POST":
        action_type = request.POST.get("action_type", "").strip()

        # 1. Quick Verify / Assign Mother
        if action_type == "verify_mother":
            mother_id = request.POST.get("mother_id")
            selected_asha_id = request.POST.get("asha_id")
            mother = get_object_or_404(base_area_mothers, id=mother_id)

            if selected_asha_id:
                assignee = get_object_or_404(area_workers, id=selected_asha_id)
            elif worker:
                assignee = worker
            else:
                assignee = asha_worker.objects.first()

            mother.ASHA = assignee
            mother.save()
            messages.success(request, f"Mother '{mother.name}' ({mother.area or worker.Area_assigned if worker else 'Area'}) has been successfully verified and assigned to ASHA Worker {assignee.Full_name}!")
            return redirect('/myapp/verify_mother/')

        # 2. Unverify / Reset Status to Pending
        elif action_type == "unverify_mother":
            mother_id = request.POST.get("mother_id")
            mother = get_object_or_404(base_area_mothers, id=mother_id)
            mother.ASHA = None
            mother.save()
            messages.info(request, f"Mother '{mother.name}' status reset to Pending Verification.")
            return redirect('/myapp/verify_mother/')

        # 3. Edit Mother Details
        elif action_type == "edit_mother":
            mother_id = request.POST.get("mother_id")
            mother = get_object_or_404(base_area_mothers, id=mother_id)

            name = request.POST.get("name", "").strip()
            husband_name = request.POST.get("husband_name", "").strip()
            age = request.POST.get("age", "").strip()
            dob = request.POST.get("dob", "").strip()
            expected_delivery_date = request.POST.get("expected_delivery_date", "").strip()
            phone = request.POST.get("phone", "").strip()
            email = request.POST.get("email", "").strip()
            blood_group = request.POST.get("blood_group", "").strip()
            panchayath = request.POST.get("panchayath", "").strip() or mother.panchayath
            area = request.POST.get("area", "").strip() or (worker.Area_assigned if worker else mother.area)
            address = request.POST.get("address", "").strip()
            district = request.POST.get("district", "").strip() or (mother.district if mother.district else "Kozhikode")
            state = request.POST.get("state", "").strip() or (mother.state if mother.state else "Kerala")
            pincode = request.POST.get("pincode", "").strip() or (mother.pincode if mother.pincode else "673001")
            asha_id = request.POST.get("asha_id", "").strip()

            if not name or len(name) < 2:
                messages.warning(request, "Please enter a valid name for the mother.")
                return redirect('/myapp/verify_mother/')

            if not husband_name:
                messages.warning(request, "Please enter husband's name.")
                return redirect('/myapp/verify_mother/')

            cleaned_phone = ''.join(filter(str.isdigit, phone))
            if not cleaned_phone or len(cleaned_phone) < 10:
                messages.warning(request, "Please enter a valid 10-digit phone number.")
                return redirect('/myapp/verify_mother/')

            if dob:
                try:
                    p_dob = datetime.strptime(dob, '%Y-%m-%d').date()
                    t_today = date.today()
                    c_age = t_today.year - p_dob.year - ((t_today.month, t_today.day) < (p_dob.month, p_dob.day))
                    if c_age < 18:
                        messages.warning(request, "Mother must be at least 18 years old.")
                        return redirect('/myapp/verify_mother/')
                    mother.dob = dob
                    mother.age = c_age
                except ValueError:
                    pass
            elif age.isdigit():
                if int(age) < 18:
                    messages.warning(request, "Mother must be at least 18 years old.")
                    return redirect('/myapp/verify_mother/')
                mother.age = int(age)

            if expected_delivery_date:
                try:
                    edd_dt = datetime.strptime(expected_delivery_date, '%Y-%m-%d').date()
                    if edd_dt < date.today():
                        messages.warning(request, "Expecting Delivery Date must be today or in the future.")
                        return redirect('/myapp/verify_mother/')
                    mother.expected_delivery_date = edd_dt
                except ValueError:
                    mother.expected_delivery_date = None
            else:
                mother.expected_delivery_date = None

            mother.phone = int(cleaned_phone)
            if email:
                if not re.match(EMAIL_REGEX, email, re.IGNORECASE):
                    messages.warning(request, "Email address must be a valid @gmail.com address (e.g., example@gmail.com).")
                    return redirect('/myapp/verify_mother/')
                if user_table.objects.filter(Email__iexact=email).exclude(id=mother.id).exists():
                    messages.warning(request, f"The email address '{email}' is already in use by another mother.")
                    return redirect('/myapp/verify_mother/')
                mother.Email = email
                if mother.LOGIN:
                    mother.LOGIN.email = email
                    mother.LOGIN.save()
            if blood_group:
                mother.blood_group = blood_group
            mother.panchayath = panchayath
            mother.area = area
            mother.Address = address
            mother.district = district
            mother.state = state
            mother.pincode = pincode

            if asha_id:
                if asha_id == "unassigned":
                    mother.ASHA = None
                else:
                    assigned_w = asha_worker.objects.filter(id=asha_id).first()
                    if assigned_w:
                        mother.ASHA = assigned_w

            mother.save()
            messages.success(request, f"Details for mother '{mother.name}' updated successfully!")
            return redirect('/myapp/verify_mother/')

        # 4. Add and Verify New Mother (within worker's area)
        elif action_type == "add_mother":
            name = request.POST.get("name", "").strip()
            husband_name = request.POST.get("husband_name", "").strip()
            dob = request.POST.get("dob", "").strip()
            expected_delivery_date = request.POST.get("expected_delivery_date", "").strip()
            age = request.POST.get("age", "").strip()
            phone = request.POST.get("phone", "").strip()
            email = request.POST.get("email", "").strip()
            blood_group = request.POST.get("blood_group", "").strip()
            panchayath = request.POST.get("panchayath", "Kozhikode Grama Panchayath").strip()
            area = (worker.Area_assigned if worker else request.POST.get("area", "").strip()) or "Ward 01 - Main Community Center"
            address = request.POST.get("address", "").strip()
            district = request.POST.get("district", "Kozhikode").strip()
            state = request.POST.get("state", "Kerala").strip()
            pincode = request.POST.get("pincode", "673001").strip()
            auto_verify = request.POST.get("auto_verify") == "yes"

            if not name or not husband_name or not phone:
                messages.warning(request, "Name, Husband's Name, and Phone are required.")
                return redirect('/myapp/verify_mother/')

            cleaned_phone = ''.join(filter(str.isdigit, phone))
            if len(cleaned_phone) < 10:
                messages.warning(request, "Please enter a valid 10-digit phone number.")
                return redirect('/myapp/verify_mother/')

            if email:
                if not re.match(EMAIL_REGEX, email, re.IGNORECASE):
                    messages.warning(request, "Email address must be a valid @gmail.com address (e.g., example@gmail.com).")
                    return redirect('/myapp/verify_mother/')
                if user_table.objects.filter(Email__iexact=email).exists():
                    messages.warning(request, f"The email address '{email}' is already registered with another account.")
                    return redirect('/myapp/verify_mother/')

            mother_age_int = 25
            if dob:
                try:
                    p_dob = datetime.strptime(dob, '%Y-%m-%d').date()
                    t_today = date.today()
                    c_age = t_today.year - p_dob.year - ((t_today.month, t_today.day) < (p_dob.month, p_dob.day))
                    if c_age < 18:
                        messages.warning(request, "Mother must be at least 18 years old.")
                        return redirect('/myapp/verify_mother/')
                    mother_age_int = c_age
                except ValueError:
                    pass
            elif age.isdigit():
                mother_age_int = int(age)
                if mother_age_int < 18:
                    messages.warning(request, "Mother must be at least 18 years old.")
                    return redirect('/myapp/verify_mother/')

            target_asha = worker if (auto_verify and worker) else None

            parsed_edd = None
            if expected_delivery_date:
                try:
                    parsed_edd = datetime.strptime(expected_delivery_date, '%Y-%m-%d').date()
                    if parsed_edd < date.today():
                        messages.warning(request, "Expecting Delivery Date must be today or in the future.")
                        return redirect('/myapp/verify_mother/')
                except ValueError:
                    parsed_edd = None

            user_table.objects.create(
                ASHA=target_asha,
                name=name,
                husband_name=husband_name,
                dob=dob if dob else "1998-01-01",
                expected_delivery_date=parsed_edd,
                age=mother_age_int,
                phone=int(cleaned_phone),
                blood_group=blood_group or "O+",
                panchayath=panchayath,
                area=area,
                Address=address or f"{area} Residence",
                district=district,
                state=state,
                pincode=pincode,
                Email=email if email else f"{name.lower().replace(' ', '')}@gmail.com"
            )
            messages.success(request, f"New mother '{name}' successfully registered in {area} and {'verified' if target_asha else 'queued for verification'}!")
            return redirect('/myapp/verify_mother/')

        # 5. Delete Mother
        elif action_type == "delete_mother":
            mother_id = request.POST.get("mother_id")
            mother = get_object_or_404(base_area_mothers, id=mother_id)
            mother_name = mother.name
            if mother.LOGIN:
                mother.LOGIN.delete()
            else:
                mother.delete()
            messages.success(request, f"Mother record for '{mother_name}' deleted successfully.")
            return redirect('/myapp/verify_mother/')

    # Querying & Filters (Strictly Area Isolated)
    search_query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "all").strip()
    panchayath_filter = request.GET.get("panchayath", "").strip()
    blood_group_filter = request.GET.get("blood_group", "").strip()

    mothers_qs = base_area_mothers.order_by('-id')

    # Stats Calculation for this specific area
    total_count = base_area_mothers.count()
    pending_count = base_area_mothers.filter(ASHA__isnull=True).count()
    verified_count = base_area_mothers.filter(ASHA__isnull=False).count()
    my_assigned_count = base_area_mothers.filter(ASHA=worker).count() if worker else 0

    # High Risk count: Rh Negative (A-, B-, O-, AB-) or age < 19 or age > 35
    rh_negatives = ['A-', 'B-', 'O-', 'AB-']
    high_risk_count = base_area_mothers.filter(
        Q(blood_group__in=rh_negatives) | Q(age__lt=19) | Q(age__gt=35)
    ).count()

    # Apply search
    if search_query:
        mothers_qs = mothers_qs.filter(
            Q(name__icontains=search_query) |
            Q(husband_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(panchayath__icontains=search_query) |
            Q(area__icontains=search_query) |
            Q(district__icontains=search_query) |
            Q(blood_group__iexact=search_query) |
            Q(Address__icontains=search_query)
        )

    # Apply Status Filter
    if status_filter == "pending":
        mothers_qs = mothers_qs.filter(ASHA__isnull=True)
    elif status_filter == "verified":
        mothers_qs = mothers_qs.filter(ASHA__isnull=False)
    elif status_filter == "my_assigned" and worker:
        mothers_qs = mothers_qs.filter(ASHA=worker)
    elif status_filter == "high_risk":
        mothers_qs = mothers_qs.filter(
            Q(blood_group__in=rh_negatives) | Q(age__lt=19) | Q(age__gt=35)
        )

    # Apply Panchayath Filter
    if panchayath_filter:
        mothers_qs = mothers_qs.filter(
            Q(panchayath__iexact=panchayath_filter) | Q(area__iexact=panchayath_filter)
        )

    # Apply Blood Group Filter
    if blood_group_filter:
        mothers_qs = mothers_qs.filter(blood_group__iexact=blood_group_filter)

    # Distinct Panchayaths / Areas for filter dropdown
    panchayath_list = base_area_mothers.values_list('panchayath', flat=True).distinct()
    panchayaths = [p for p in panchayath_list if p]

    context = {
        'worker': worker,
        'assigned_area': worker.Area_assigned if worker else 'All Areas',
        'all_workers': area_workers,
        'mothers': mothers_qs,
        'total_count': total_count,
        'pending_count': pending_count,
        'verified_count': verified_count,
        'my_assigned_count': my_assigned_count,
        'high_risk_count': high_risk_count,
        'search_query': search_query,
        'status_filter': status_filter,
        'panchayath_filter': panchayath_filter,
        'blood_group_filter': blood_group_filter,
        'panchayaths': panchayaths,
        'panchayath_areas': PANCHAYATH_AREAS,
        'rh_negatives': rh_negatives,
    }
    return render(request, 'ashawoker/verify_mother.html', context)


def verify_mother_action(request, id, action):
    worker = get_current_asha_worker(request)

    area_q = get_area_filter_q(worker.Area_assigned) if worker else Q()
    mother = get_object_or_404(user_table.objects.filter(area_q) if worker else user_table.objects.all(), id=id)

    if action == "verify":
        mother.ASHA = worker
        mother.save()
        messages.success(request, f"Mother '{mother.name}' has been verified and assigned to you.")
    elif action == "unverify":
        mother.ASHA = None
        mother.save()
        messages.info(request, f"Mother '{mother.name}' status set to Pending Verification.")
    return redirect('/myapp/verify_mother/')


def delete_mother(request, id):
    worker = get_current_asha_worker(request)

    area_q = get_area_filter_q(worker.Area_assigned) if worker else Q()
    mother = get_object_or_404(user_table.objects.filter(area_q) if worker else user_table.objects.all(), id=id)
    mother_name = mother.name
    if mother.LOGIN:
        mother.LOGIN.delete()
    else:
        mother.delete()
    messages.success(request, f"Mother record for '{mother_name}' deleted successfully.")
    return redirect('/myapp/verify_mother/')


def get_logged_in_mother(request):
    """
    Helper function to safely retrieve the authenticated mother's profile.
    Supports staff/admin preview fallback for testing.
    """
    if not request.user.is_authenticated:
        return None, redirect('/myapp/login/')

    mother = user_table.objects.filter(LOGIN=request.user).first()
    if mother and mother.ASHA is None and not request.user.is_staff:
        logout(request)
        messages.warning(
            request,
            "Verification Pending: Your account registration is awaiting verification by your local ASHA Healthcare Worker. You will be able to log in once your account has been verified."
        )
        return None, redirect('/myapp/login/')

    if not mother and request.user.is_staff:
        mother = user_table.objects.filter(ASHA__isnull=False).first() or user_table.objects.first()
    elif not mother:
        mother = user_table.objects.first()

    return mother, None


def get_user_seen_notification_ids(mother):
    """
    Returns set of notification IDs that the mother has already seen/acknowledged.
    """
    if not mother:
        return set()
    return set(notification_seen.objects.filter(USER=mother).values_list('notif_id', flat=True))


def mark_notifications_as_seen(mother, notif_ids=None):
    """
    Marks specific or all notifications as seen by the mother.
    """
    if not mother:
        return 0
    if notif_ids is None:
        all_notifs = get_user_filtered_notifications(mother)
        notif_ids = [n['id'] for n in all_notifs]
    created_count = 0
    for nid in notif_ids:
        if nid:
            _, created = notification_seen.objects.get_or_create(USER=mother, notif_id=str(nid).strip())
            if created:
                created_count += 1
    return created_count


def extract_scheduled_event_date(text, default_date):
    if not text:
        return default_date
    m = re.search(r'(?:on|to|for)\s+([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})', text, re.IGNORECASE)
    if m:
        raw_str = m.group(1).replace(',', '').strip()
        for fmt in ('%b %d %Y', '%B %d %Y'):
            try:
                return datetime.strptime(raw_str, fmt).date()
            except ValueError:
                pass
    return default_date


def parse_growth_record_details(raw_details):
    """
    Parses raw report_details to extract clean observation notes and any uploaded media path/URL.
    Returns (clean_notes, media_url, media_filename, media_type).
    """
    if not raw_details:
        return "Routine clinical checkup", None, None, None

    clean_text = str(raw_details).strip()
    media_url = None
    media_filename = None
    media_type = None

    # Match Report: <path_or_filename>
    m = re.search(r'Report:\s*([^\s|]+)', clean_text, re.IGNORECASE)
    if m:
        file_part = m.group(1).strip()
        media_filename = os.path.basename(file_part)
        clean_rel = file_part.lstrip('/')
        if not clean_rel.startswith('media/'):
            media_url = f"/media/{clean_rel}"
        else:
            media_url = f"/{clean_rel}"
        lower_fn = media_filename.lower()
        if any(lower_fn.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
            media_type = 'image'
        elif lower_fn.endswith('.pdf'):
            media_type = 'pdf'
        else:
            media_type = 'file'

        clean_text = re.sub(r'\|\s*Report:\s*[^\s|]+', '', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'Report:\s*[^\s|]+', '', clean_text, flags=re.IGNORECASE)

    # Remove internal system tags like [Month X], [At Birth]
    clean_text = re.sub(r'\[Month\s*\d+\]', '', clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'\[At Birth\]', '', clean_text, flags=re.IGNORECASE)
    clean_text = clean_text.strip(' |').strip()

    return clean_text or "Routine clinical checkup", media_url, media_filename, media_type


def get_user_filtered_notifications(mother):
    """
    Returns only TWO types of notifications for the logged-in mother:
    1. Kit Notifications (sent by Anganwadi Teacher)
    2. Vaccine Notifications (sent by Administrative Officer / Admin)
    Excludes all checkup or unrelated general alerts.
    Deduplicates identical notifications.
    Includes is_new flag indicating whether the mother has seen it before.
    Includes is_past flag indicating if the scheduled date has passed and user has seen it.
    """
    if not mother:
        return []

    today_dt = date.today()
    seen_messages = set()
    formatted_notifs = []
    seen_ids = get_user_seen_notification_ids(mother)

    # 1. Process Kit notifications from kit_notification table (Anganwadi)
    kit_notifs_qs = kit_notification.objects.filter(USER=mother).order_by('-notification_date', '-id')
    for kn in kit_notifs_qs:
        msg_clean = (kn.notification_message or '').strip()
        norm_key = ('kit', msg_clean.lower())
        if norm_key in seen_messages:
            continue
        seen_messages.add(norm_key)

        is_rescheduled = 'reschedul' in msg_clean.lower()
        notif_id_str = f"k-{kn.id}"
        is_new = notif_id_str not in seen_ids
        scheduled_date = kn.NUTRITION.distribution_date if (kn.NUTRITION and kn.NUTRITION.distribution_date) else extract_scheduled_event_date(msg_clean, kn.notification_date or today_dt)
        is_past = bool((scheduled_date and scheduled_date < today_dt) and not is_new)

        # Past notifications that have been seen are removed after 1 day from the scheduled date to prevent bulk accumulation
        if not is_new and scheduled_date and (today_dt - scheduled_date).days > 1:
            continue

        formatted_notifs.append({
            'id': notif_id_str,
            'type': 'kit',
            'is_new': is_new,
            'is_past': is_past,
            'scheduled_date': scheduled_date,
            'scheduled_date_str': scheduled_date.strftime('%b %d, %Y') if scheduled_date else None,
            'is_rescheduled': is_rescheduled,
            'category_title': 'Rescheduled Kit Pickup Alert' if is_rescheduled else 'Nutrition Kit Alert',
            'sender_title': 'Anganwadi Teacher',
            'sender_badge': 'Rescheduled • Anganwadi' if is_rescheduled else 'Sent by Anganwadi',
            'sender_class': 'sender-rescheduled' if is_rescheduled else 'sender-angteacher',
            'card_class': 'notif-rescheduled' if is_rescheduled else '',
            'icon': 'fa-solid fa-clock-rotate-left' if is_rescheduled else 'fa-solid fa-box-archive',
            'icon_bg': '#f3e8ff' if is_rescheduled else '#e0f2fe',
            'icon_color': '#7e22ce' if is_rescheduled else '#0369a1',
            'title': f"Rescheduled: {kn.NUTRITION.product_name if kn.NUTRITION else 'Nutrition Kit'}" if is_rescheduled else f"Kit Distribution: {kn.NUTRITION.product_name if kn.NUTRITION else 'Nutrition Kit'}",
            'message': msg_clean,
            'date': kn.notification_date.strftime('%b %d, %Y') if kn.notification_date else 'Recent',
            'raw_date': kn.notification_date or today_dt,
            'badge': 'Rescheduled Kit' if is_rescheduled else 'Kit • Anganwadi',
            'badge_class': 'chip-rescheduled' if is_rescheduled else 'chip-kit',
            'link': '/myapp/user_kit_history/',
            'action_label': 'View Kit Details'
        })

    # 2. Process General & Vaccine notifications from notification table
    user_notifs_qs = notification.objects.filter(USER=mother).order_by('-notification_date', '-id')
    for un in user_notifs_qs:
        msg_clean = (un.message or '').strip()
        msg_lower = msg_clean.lower()

        # Check if it's a Kit Notification sent by Anganwadi
        is_kit = any(kw in msg_lower for kw in ['nutrition', 'amrutham', 'supplement', 'kit pickup', 'ration', 'diet pack', 'matrutva']) or ('kit' in msg_lower and any(w in msg_lower for w in ['rescheduled', 'pickup', 'distribution', 'collected', 'center', 'anganwadi']))
        # Check if it's a Vaccine Notification sent by Admin
        is_vaccine = any(kw in msg_lower for kw in ['vaccin', 'dose', 'immuniz', 'immunis', 'bcg', 'opv', 'polio', 'hepatitis', 'pentavalent', 'rotavirus', 'pcv', 'ipv', 'measles', 'rubella', 'vitamin a', 'dpt', 'tcv'])

        is_rescheduled = 'reschedul' in msg_lower
        notif_id_str = f"u-{un.id}"
        is_new = notif_id_str not in seen_ids
        scheduled_date = extract_scheduled_event_date(msg_clean, un.notification_date or today_dt)
        is_past = bool((scheduled_date and scheduled_date < today_dt) and not is_new)

        # Past notifications that have been seen are removed after 1 day from the scheduled date to prevent bulk accumulation
        if not is_new and scheduled_date and (today_dt - scheduled_date).days > 1:
            continue

        if is_kit:
            norm_key = ('kit', msg_clean.lower())
            if norm_key in seen_messages:
                continue
            seen_messages.add(norm_key)
            formatted_notifs.append({
                'id': notif_id_str,
                'type': 'kit',
                'is_new': is_new,
                'is_past': is_past,
                'scheduled_date': scheduled_date,
                'scheduled_date_str': scheduled_date.strftime('%b %d, %Y') if scheduled_date else None,
                'is_rescheduled': is_rescheduled,
                'category_title': 'Rescheduled Kit Pickup Alert' if is_rescheduled else 'Nutrition Kit Alert',
                'sender_title': 'Anganwadi Teacher',
                'sender_badge': 'Rescheduled • Anganwadi' if is_rescheduled else 'Sent by Anganwadi',
                'sender_class': 'sender-rescheduled' if is_rescheduled else 'sender-angteacher',
                'card_class': 'notif-rescheduled' if is_rescheduled else '',
                'icon': 'fa-solid fa-clock-rotate-left' if is_rescheduled else 'fa-solid fa-box-archive',
                'icon_bg': '#f3e8ff' if is_rescheduled else '#e0f2fe',
                'icon_color': '#7e22ce' if is_rescheduled else '#0369a1',
                'title': 'Nutrition Kit Pickup Rescheduled' if is_rescheduled else 'Nutrition Kit Pickup Alert',
                'message': msg_clean,
                'date': un.notification_date.strftime('%b %d, %Y') if un.notification_date else 'Recent',
                'raw_date': un.notification_date or today_dt,
                'badge': 'Rescheduled Kit' if is_rescheduled else 'Kit • Anganwadi',
                'badge_class': 'chip-rescheduled' if is_rescheduled else 'chip-kit',
                'link': '/myapp/user_kit_history/',
                'action_label': 'View Kit Details'
            })
        elif is_vaccine:
            norm_key = ('vaccine', msg_clean.lower())
            if norm_key in seen_messages:
                continue
            seen_messages.add(norm_key)
            formatted_notifs.append({
                'id': notif_id_str,
                'type': 'vaccine',
                'is_new': is_new,
                'is_past': is_past,
                'scheduled_date': scheduled_date,
                'scheduled_date_str': scheduled_date.strftime('%b %d, %Y') if scheduled_date else None,
                'is_rescheduled': is_rescheduled,
                'category_title': 'Rescheduled Vaccination Alert' if is_rescheduled else 'Vaccination Schedule',
                'sender_title': 'Administrative Officer (Admin)',
                'sender_badge': 'Rescheduled • Admin' if is_rescheduled else 'Sent by Admin',
                'sender_class': 'sender-rescheduled' if is_rescheduled else 'sender-admin',
                'card_class': 'notif-rescheduled' if is_rescheduled else '',
                'icon': 'fa-solid fa-clock-rotate-left' if is_rescheduled else 'fa-solid fa-syringe',
                'icon_bg': '#f3e8ff' if is_rescheduled else '#fef3c7',
                'icon_color': '#7e22ce' if is_rescheduled else '#b45309',
                'title': 'Vaccination Rescheduled by Admin' if is_rescheduled else 'Child Immunization Schedule',
                'message': msg_clean,
                'date': un.notification_date.strftime('%b %d, %Y') if un.notification_date else 'Recent',
                'raw_date': un.notification_date or today_dt,
                'badge': 'Rescheduled Vaccine' if is_rescheduled else 'Vaccine • Admin',
                'badge_class': 'chip-rescheduled' if is_rescheduled else 'chip-vax',
                'link': '/myapp/user_vaccination_schedule/',
                'action_label': 'View Schedule'
            })
        # If it is neither Kit nor Vaccine, it is strictly excluded.

    formatted_notifs.sort(key=lambda x: x['raw_date'], reverse=True)
    return formatted_notifs


def get_child_filtered_vaccinations(selected_child, mother=None):
    """
    Returns vaccination records for a child:
    1. Taken / Completed vaccines: Always shown as Taken (including when taken after reschedule).
    2. Not taken in given date: If vaccination_date < today and not taken, or status == 'Missed',
       shown as Missed.
    3. Rescheduled: If rescheduled to a future date, shown as Rescheduled.
    4. Scheduled: Upcoming date scheduled dose, shown as Scheduled.
    Excludes unnotified/unscheduled master vaccine placeholders.
    """
    if not selected_child:
        return []

    today_dt = date.today()
    mother = mother or selected_child.USER
    mother_notifs = notification.objects.filter(USER=mother) if mother else notification.objects.none()
    notif_texts = [n.message.lower() for n in mother_notifs]

    all_vax = vaccination.objects.filter(CHILD=selected_child).order_by('target_month', 'vaccination_date', 'id')
    valid_vax = []

    for v in all_vax:
        v_name = (v.vaccine_name or '').lower()
        v_code = (v.vaccine_code or '').lower()
        was_notified = any(
            (v_name in msg) or (v_code and len(v_code) > 2 and v_code in msg)
            for msg in notif_texts
        )

        # Include if child has this vaccine actively notified or recorded
        if not (was_notified or v.status in ['Taken', 'Completed', 'Scheduled', 'Rescheduled', 'Missed']):
            continue

        # Check if this vaccine has been rescheduled (via status or reschedule notification)
        is_notif_rescheduled = any(
            ('reschedul' in msg) and (v_name in msg or (v_code and len(v_code) > 2 and v_code in msg))
            for msg in notif_texts
        )
        is_rescheduled = (v.status == 'Rescheduled') or is_notif_rescheduled

        # 1. Taken vaccine (always Taken, including when taken after reschedule)
        if v.status in ['Taken', 'Completed']:
            v.effective_status = 'Taken'
            v.effective_status_display = 'Taken / Administered'
            v.status_badge_class = 'status-completed'
            valid_vax.append(v)
        # 2. Rescheduled: If it is rescheduled, remove missed status and show as Rescheduled
        elif is_rescheduled:
            v.effective_status = 'Rescheduled'
            v.effective_status_display = 'Rescheduled (Notified)'
            v.status_badge_class = 'status-rescheduled'
            valid_vax.append(v)
        # 3. Not taken in given date -> Missed (only if NOT rescheduled)
        elif v.status == 'Missed' or (v.vaccination_date and v.vaccination_date < today_dt):
            v.effective_status = 'Missed'
            v.effective_status_display = 'Missed Dose'
            v.status_badge_class = 'status-missed'
            valid_vax.append(v)
        # 4. Scheduled upcoming
        else:
            v.effective_status = 'Scheduled'
            v.effective_status_display = 'Scheduled (Notified)'
            v.status_badge_class = 'status-scheduled'
            valid_vax.append(v)

    return valid_vax


def userhome(request):
    """
    Renders personalized Maternal Health & Child Care Portal Dashboard for registered mothers.
    Displays gestation progress, pregnancy countdown, child metrics, upcoming vaccinations,
    kit distribution status, and notification alerts.
    """
    mother, err_redirect = get_logged_in_mother(request)
    if err_redirect:
        return err_redirect

    today_dt = date.today()
    preg_rec = pregnancy_record.objects.filter(USER=mother).order_by('-checkup_date').first() if mother else None
    
    gest_weeks = 0
    trimester = 0
    gest_percent = 0
    days_to_delivery = 0
    edd_str = "---"
    days_to_go_str = "---"
    current_weight_str = "---"
    pregnancy_stage_str = "---"
    
    is_currently_pregnant = mother.is_currently_pregnant if mother else False
    has_delivered = mother.has_delivered if mother else False
    current_preg_number = mother.current_pregnancy_number if mother else 1
    gest_month = mother.gestation_month if is_currently_pregnant else 1
    edd = None
    if mother and mother.expected_delivery_date:
        edd = mother.expected_delivery_date
    elif preg_rec and preg_rec.expected_delivery_date:
        edd = preg_rec.expected_delivery_date

    if is_currently_pregnant and edd:
        edd_str = edd.strftime('%b %d, %Y')
        days_left = (edd - today_dt).days
        days_to_delivery = max(days_left, 0)
        days_to_go_str = f"{days_to_delivery} Days" if days_to_delivery > 0 else "Due / Post-term"
        gest_days = max(280 - days_left, 0)
        gest_weeks = max(min(gest_days // 7, 40), 1)
        gest_percent = min(max(round((gest_weeks / 40) * 100), 2), 100)

        if gest_weeks <= 13:
            trimester = 1
        elif gest_weeks <= 27:
            trimester = 2
        else:
            trimester = 3
        pregnancy_stage_str = f"Trimester {trimester} (Week {gest_weeks})"
    elif has_delivered:
        pregnancy_stage_str = "Delivered"
        gest_weeks = 40
        gest_percent = 100
        days_to_go_str = "Delivered"
        edd_str = None
    elif edd:
        edd_str = edd.strftime('%b %d, %Y')
        days_left = (edd - today_dt).days
        days_to_delivery = max(days_left, 0)
        days_to_go_str = f"{days_to_delivery} Days" if days_to_delivery > 0 else "Due / Post-term"
        gest_days = max(280 - days_left, 0)
        gest_weeks = max(min(gest_days // 7, 40), 1)
        gest_percent = min(max(round((gest_weeks / 40) * 100), 2), 100)
        trimester = 1 if gest_weeks <= 13 else (2 if gest_weeks <= 27 else 3)
        pregnancy_stage_str = f"Trimester {trimester} (Week {gest_weeks})"

    if preg_rec and preg_rec.weight:
        current_weight_str = f"{preg_rec.weight} kg"

    # Child & Vaccination Info (strictly Taken & Notified-Scheduled doses only)
    next_vax_str = "None scheduled"
    next_vax_date = None
    children_qs = child.objects.filter(USER=mother) if mother else child.objects.none()
    first_child = children_qs.first()
    
    if first_child:
        valid_child_vaxes = get_child_filtered_vaccinations(first_child, mother)
        upcoming_vax = next((v for v in valid_child_vaxes if v.effective_status in ['Scheduled', 'Rescheduled']), None)
        missed_vax = next((v for v in valid_child_vaxes if v.effective_status == 'Missed'), None)
        if upcoming_vax:
            next_vax_str = upcoming_vax.vaccine_name
            next_vax_date = upcoming_vax.vaccination_date.strftime('%b %d, %Y') if upcoming_vax.vaccination_date else None
        elif missed_vax:
            next_vax_str = f"{missed_vax.vaccine_name} (Missed)"
            next_vax_date = f"Missed ({missed_vax.vaccination_date.strftime('%b %d') if missed_vax.vaccination_date else 'Date passed'})"

    # Nutrition Kit Info for Mother
    next_kit_str = "No active kits"
    latest_kit_status = "None"
    kits_qs = nutrition_kit.objects.filter(USER=mother).order_by('-distribution_date', '-date') if mother else nutrition_kit.objects.none()
    latest_kit = kits_qs.first()
    if latest_kit:
        next_kit_str = latest_kit.kit_type or latest_kit.product_name
        latest_kit_status = latest_kit.status

    # Notifications (Strictly 2 Types: Kit from Anganwadi, Vaccine from Admin)
    all_notifs = get_user_filtered_notifications(mother)
    new_notifs = [n for n in all_notifs if n.get('is_new', False)]
    active_notifs = [n for n in all_notifs if not n.get('is_past', False)]
    past_notifs = [n for n in all_notifs if n.get('is_past', False)]
    notif_count = len(new_notifs)  # Strictly only NEW unread notifications count!

    # Login Notification Pop-up Trigger: Pop up on login whenever there are unread notifications
    force_popup = bool(request.GET.get('show_popup') or request.GET.get('popup'))
    popup_dismissed = request.session.get('notif_popup_dismissed_session', False)
    
    if force_popup:
        show_login_popup = True
        popup_notifications = new_notifs if new_notifs else all_notifs
    else:
        show_login_popup = bool(new_notifs and not popup_dismissed)
        popup_notifications = new_notifs if show_login_popup else []

    # Child Growth Info
    child_weight_str = "---"
    child_height_str = "---"
    child_growth_logs = child_growth_record.objects.filter(CHILD=first_child).order_by('-growth_date') if first_child else []
    latest_growth = child_growth_logs.first() if child_growth_logs else None
    
    if latest_growth:
        if latest_growth.weight:
            child_weight_str = f"{latest_growth.weight} kg"
        if latest_growth.height:
            child_height_str = f"{latest_growth.height} cm"
    elif first_child:
        if first_child.birth_weight:
            child_weight_str = f"{first_child.birth_weight} kg"
        if first_child.birth_height:
            child_height_str = f"{first_child.birth_height} cm"

    first_child_age_str = "0 Days"
    first_child_growth_count = 0
    if first_child:
        first_child_growth_count = child_growth_record.objects.filter(CHILD=first_child).count()
        if first_child.date_of_birth:
            days_old = (today_dt - first_child.date_of_birth).days
            if days_old < 30:
                first_child_age_str = f"{days_old} Days"
            elif days_old < 365:
                m_old = days_old // 30
                first_child_age_str = f"{m_old} Month{'s' if m_old > 1 else ''}"
            else:
                y_old = days_old // 365
                first_child_age_str = f"{y_old} Year{'s' if y_old > 1 else ''}"

    all_pregnancy_records = pregnancy_record.objects.filter(USER=mother).order_by('-checkup_date') if mother else []
    if is_currently_pregnant:
        current_preg_records = [r for r in all_pregnancy_records if (r.expected_delivery_date and r.expected_delivery_date >= today_dt) or r.previous_pregnency_count > 0]
        previous_preg_records = [r for r in all_pregnancy_records if r not in current_preg_records]
    else:
        current_preg_records = []
        previous_preg_records = list(all_pregnancy_records)
    all_growth_records = []
    if mother:
        for ch_obj in children_qs:
            g_logs = child_growth_record.objects.filter(CHILD=ch_obj).order_by('-growth_date')
            for g in g_logs:
                details_str = g.report_details or ""
                if "[at birth]" in details_str.lower() or "registered birth metrics" in details_str.lower():
                    continue

                clean_notes, media_url, media_filename, media_type = parse_growth_record_details(details_str)

                m_calc = max((g.growth_date.year - ch_obj.date_of_birth.year) * 12 + g.growth_date.month - ch_obj.date_of_birth.month, 0) if ch_obj.date_of_birth else 0
                if "[Month " in details_str:
                    try:
                        m_calc = int(details_str.split("[Month ")[1].split("]")[0])
                    except Exception:
                        pass
                st_label = f"Month {m_calc}"
                all_growth_records.append({
                    'id': g.id,
                    'child_name': ch_obj.child_name,
                    'stage_label': st_label,
                    'month': m_calc,
                    'growth_date': g.growth_date,
                    'date': g.growth_date.strftime('%b %d, %Y') if g.growth_date else "-",
                    'weight': g.weight,
                    'height': g.height,
                    'health_condition': g.health_condition or "Healthy",
                    'report_details': clean_notes,
                    'media_url': media_url,
                    'media_filename': media_filename,
                    'media_type': media_type,
                })
        all_growth_records.sort(key=lambda r: (r['growth_date'] or date.min), reverse=True)
    
    # Only include taken and notified scheduled vaccines across mother's children
    all_vax_records = []
    if mother:
        for ch_obj in children_qs:
            all_vax_records.extend(get_child_filtered_vaccinations(ch_obj, mother))
        all_vax_records.sort(key=lambda v: (v.vaccination_date or date.min), reverse=True)

    # Recent health activities stream
    recent_activities = []
    if preg_rec:
        recent_activities.append({
            'icon': 'fa-solid fa-stethoscope',
            'title': f'Antenatal Checkup: BP {preg_rec.blood_pressure}, Wt {preg_rec.weight} kg',
            'date': preg_rec.checkup_date.strftime('%b %d, %Y') if preg_rec.checkup_date else 'Recent',
            'status': preg_rec.health_status or 'Normal',
            'badge_class': 'badge-success'
        })
    if latest_growth:
        recent_activities.append({
            'icon': 'fa-solid fa-child',
            'title': f'Child Growth Log: {latest_growth.weight} kg, {latest_growth.height} cm',
            'date': latest_growth.growth_date.strftime('%b %d, %Y') if latest_growth.growth_date else 'Recent',
            'status': latest_growth.health_condition or 'Normal',
            'badge_class': 'badge-info'
        })
    if latest_kit:
        recent_activities.append({
            'icon': 'fa-solid fa-box-archive',
            'title': f'Nutrition Kit: {latest_kit.product_name}',
            'date': latest_kit.distribution_date.strftime('%b %d, %Y') if latest_kit.distribution_date else 'Recent',
            'status': latest_kit.status,
            'badge_class': 'badge-warning' if latest_kit.status == 'Pending' else 'badge-success'
        })

    context = {
        'mother': mother,
        'preg_rec': preg_rec,
        'gest_weeks': gest_weeks,
        'gest_percent': gest_percent,
        'trimester': trimester,
        'days_to_delivery': days_to_delivery,
        'days_to_go_str': days_to_go_str,
        'current_weight_str': current_weight_str,
        'pregnancy_stage_str': pregnancy_stage_str,
        'has_delivered': has_delivered,
        'is_currently_pregnant': is_currently_pregnant,
        'current_preg_number': current_preg_number,
        'gest_month': gest_month,
        'edd_str': edd_str,
        'next_vax_str': next_vax_str,
        'next_vax_date': next_vax_date,
        'next_kit_str': next_kit_str,
        'latest_kit_status': latest_kit_status,
        'notif_count': notif_count,
        'notifications': all_notifs,
        'active_notifs': active_notifs,
        'past_notifs': past_notifs,
        'show_login_popup': bool(popup_notifications),
        'popup_notifications': popup_notifications,
        'children': children_qs,
        'first_child': first_child,
        'first_child_age_str': first_child_age_str,
        'first_child_growth_count': first_child_growth_count,
        'child_weight_str': child_weight_str,
        'child_height_str': child_height_str,
        'child_growth_logs': child_growth_logs,
        'all_pregnancy_records': all_pregnancy_records,
        'current_preg_records': current_preg_records,
        'previous_preg_records': previous_preg_records,
        'has_multiple_pregnancies': bool(current_preg_records and previous_preg_records),
        'all_growth_records': all_growth_records,
        'all_vax_records': all_vax_records,
        'kits': kits_qs,
        'recent_activities': recent_activities,
        'today': today_dt.strftime('%b %d, %Y'),
    }
    return render(request, 'user/user_home.html', context)


def user_profile_view(request):
    """
    Renders comprehensive Profile page for the logged-in mother.
    Displays personal particulars, husband/guardian info, residential & ward info,
    assigned ASHA healthcare worker contact, and local Anganwadi center.
    """
    mother, err_redirect = get_logged_in_mother(request)
    if err_redirect:
        return err_redirect

    today_dt = date.today()
    asha = mother.ASHA if mother else None
    
    # Locate matching Anganwadi teacher based on mother's area or panchayath
    teacher = None
    if mother and mother.area:
        match = re.search(r'0?(\d+)', mother.area)
        if match:
            num = match.group(1)
            teacher = anganwadi_teacher.objects.filter(center_name__icontains=num).first()
    if not teacher:
        teacher = anganwadi_teacher.objects.first()

    # Counts
    preg_count = pregnancy_record.objects.filter(USER=mother).count() if mother else 0
    child_count = child.objects.filter(USER=mother).count() if mother else 0
    kit_count = nutrition_kit.objects.filter(USER=mother).count() if mother else 0

    patient_id = f"MC-M{mother.id:04d}" if mother else "--"
    children = child.objects.filter(USER=mother).order_by('date_of_birth') if mother else child.objects.none()
    is_currently_pregnant = mother.is_currently_pregnant if mother else False
    current_preg_number = mother.current_pregnancy_number if mother else 1

    context = {
        'mother': mother,
        'asha': asha,
        'teacher': teacher,
        'preg_count': preg_count,
        'child_count': child_count,
        'kit_count': kit_count,
        'children': children,
        'is_currently_pregnant': is_currently_pregnant,
        'current_preg_number': current_preg_number,
        'patient_id': patient_id,
        'today': today_dt.strftime('%b %d, %Y'),
    }
    return render(request, 'user/view_profile.html', context)


def edit_user_profile(request):
    """
    Allows the logged-in mother to update her contact phone, husband name, address, and password.
    """
    mother, err_redirect = get_logged_in_mother(request)
    if err_redirect:
        return err_redirect

    if request.method == "POST":
        action = request.POST.get('action', 'update_info')

        if action == 'update_password':
            current_pw = request.POST.get('current_password', '')
            new_pw = request.POST.get('new_password', '')
            confirm_pw = request.POST.get('confirm_password', '')

            if not request.user.check_password(current_pw):
                messages.error(request, "Incorrect current password. Please verify and try again.")
                return redirect('/myapp/user_profile/')

            if len(new_pw) < 6:
                messages.error(request, "New password must be at least 6 characters in length.")
                return redirect('/myapp/user_profile/')

            if new_pw != confirm_pw:
                messages.error(request, "New password and confirmation password do not match.")
                return redirect('/myapp/user_profile/')

            request.user.set_password(new_pw)
            request.user.save()
            messages.success(request, "Your password has been changed successfully!")
            return redirect('/myapp/user_profile/')

        else:
            # Update personal info
            phone = request.POST.get('phone', '').strip()
            husband_name = request.POST.get('husband_name', '').strip()
            address = request.POST.get('address', '').strip()
            pincode = request.POST.get('pincode', '').strip()

            if phone and not re.match(PHONE_REGEX, phone):
                messages.warning(request, "Phone number must be a valid 10-digit Indian mobile number.")
                return redirect('/myapp/user_profile/')

            if pincode and not re.match(PINCODE_REGEX, pincode):
                messages.warning(request, "Pincode must be a valid 6-digit postal code.")
                return redirect('/myapp/user_profile/')

            if phone:
                mother.phone = int(phone)
            if husband_name:
                mother.husband_name = husband_name
            if address:
                mother.Address = address
            if pincode:
                mother.pincode = pincode

            mother.save()
            messages.success(request, "Your profile information has been updated successfully.")
            return redirect('/myapp/user_profile/')

    return redirect('/myapp/user_profile/')


def user_pregnancy_record(request):
    """
    Renders dedicated Pregnancy Record View Page for the logged-in mother.
    Displays full antenatal checkup history added by ASHA, trimester progress,
    EDD countdown, vitals tracking (Weight, BP, Hb, Height), and next checkup dates.
    """
    mother, err_redirect = get_logged_in_mother(request)
    # Allow inspecting a specific mother if requested (e.g., ASHA worker, admin, or direct link)
    req_mother_id = request.GET.get('mother_id') or request.GET.get('selected_mother') or request.GET.get('id')
    if req_mother_id:
        target_m = user_table.objects.filter(id=req_mother_id).first()
        if target_m:
            mother = target_m
            err_redirect = None
    elif not mother:
        mother = user_table.objects.filter(ASHA__isnull=False).first() or user_table.objects.first()
        if mother:
            err_redirect = None

    if err_redirect and not mother:
        return err_redirect

    today_dt = date.today()
    all_preg_records = pregnancy_record.objects.filter(USER=mother).order_by('-checkup_date') if mother else pregnancy_record.objects.none()
    latest_preg = all_preg_records.first()

    patient_name = mother.name if mother else "--"
    patient_id = f"MC-M{mother.id:04d}" if mother else "--"
    managing_physician = mother.ASHA.Full_name if (mother and mother.ASHA) else "--"
    last_checkup_date = latest_preg.checkup_date.strftime('%b %d, %Y') if latest_preg else "--"
    
    is_active = False
    status_str = "--"
    edd_str = "--"
    weight_str = "--"
    bp_str = "--"
    height_str = "--"
    health_status_str = "--"
    gest_weeks = 0
    trimester = 1

    is_currently_pregnant = mother.is_currently_pregnant if mother else False
    has_delivered = mother.has_delivered if mother else False
    current_preg_number = mother.current_pregnancy_number if mother else 1

    edd = None
    if mother and mother.expected_delivery_date:
        edd = mother.expected_delivery_date
    elif latest_preg and latest_preg.expected_delivery_date:
        edd = latest_preg.expected_delivery_date

    if is_currently_pregnant and edd:
        edd_str = edd.strftime('%b %d, %Y')
        days_left = (edd - today_dt).days
        gest_days = max(280 - days_left, 0)
        gest_weeks = max(min(gest_days // 7, 40), 1)
        trimester = 1 if gest_weeks <= 13 else (2 if gest_weeks <= 27 else 3)
        status_str = f"Trimester {trimester} (Week {gest_weeks})"
        is_active = True
    elif has_delivered:
        status_str = "Delivered"
        is_active = False
        edd_str = None
    elif edd:
        edd_str = edd.strftime('%b %d, %Y')
        days_left = (edd - today_dt).days
        gest_days = max(280 - days_left, 0)
        gest_weeks = max(min(gest_days // 7, 40), 1)
        trimester = 1 if gest_weeks <= 13 else (2 if gest_weeks <= 27 else 3)
        status_str = f"Trimester {trimester} (Week {gest_weeks})"
        is_active = (edd >= today_dt)
    elif latest_preg:
        status_str = "Active"
        is_active = True
    else:
        status_str = "Registered Mother"
        is_active = False

    if latest_preg:
        if latest_preg.weight:
            weight_str = f"{latest_preg.weight}"
        if latest_preg.blood_pressure:
            bp_str = f"{latest_preg.blood_pressure}"
        if latest_preg.height:
            height_str = f"{latest_preg.height}"
        if latest_preg.health_status:
            health_status_str = f"{latest_preg.health_status}"

    delivered_child = child.objects.filter(USER=mother).order_by('date_of_birth').first()
    latest_delivered_child = child.objects.filter(USER=mother).order_by('-date_of_birth').first()

    if is_currently_pregnant:
        min_date = latest_delivered_child.date_of_birth if latest_delivered_child else date.min
        current_preg_records = all_preg_records.filter(
            Q(checkup_date__gt=min_date) | Q(previous_pregnency_count=mother.delivered_children_count) | Q(expected_delivery_date__gte=today_dt)
        ).order_by('checkup_date')
        previous_preg_records = all_preg_records.exclude(
            id__in=current_preg_records.values_list('id', flat=True)
        ).order_by('checkup_date')
    else:
        current_preg_records = pregnancy_record.objects.none()
        previous_preg_records = all_preg_records.order_by('checkup_date')

    context = {
        'mother': mother,
        'patient_name': patient_name,
        'patient_id': patient_id,
        'managing_physician': managing_physician,
        'last_checkup_date': last_checkup_date,
        'status_str': status_str,
        'edd_str': edd_str,
        'has_delivered': has_delivered,
        'is_currently_pregnant': is_currently_pregnant,
        'current_preg_number': current_preg_number,
        'is_active': is_active,
        'weight_str': weight_str,
        'bp_str': bp_str,
        'height_str': height_str,
        'health_status_str': health_status_str,
        'gest_weeks': gest_weeks,
        'trimester': trimester,
        'monthly_records': all_preg_records,
        'current_preg_records': current_preg_records,
        'previous_preg_records': previous_preg_records,
        'has_multiple_pregnancies': bool(mother and mother.has_delivered_child and (is_currently_pregnant or previous_preg_records.exists())),
        'delivered_child': delivered_child,
        'records_count': all_preg_records.count(),
        'today': today_dt.strftime('%b %d, %Y'),
    }
    return render(request, 'user/view_pregnency_record.html', context)


def user_child_profile(request):
    """
    Renders dedicated Child Profile Page for the logged-in mother.
    Displays complete child identity, birth particulars (birth weight, birth height,
    delivery type, hospital, birth health status), guardian info, and summary cards.
    """
    mother, err_redirect = get_logged_in_mother(request)
    if err_redirect:
        return err_redirect

    today_dt = date.today()
    children_qs = child.objects.filter(USER=mother) if mother else child.objects.none()
    
    child_id_param = request.GET.get('child_id')
    selected_child = None
    if child_id_param and children_qs.filter(id=child_id_param).exists():
        selected_child = children_qs.get(id=child_id_param)
    else:
        selected_child = children_qs.first()

    child_id_str = f"CH-{selected_child.id:04d}" if selected_child else "-"
    child_name = selected_child.child_name if selected_child else "-"
    child_dob = selected_child.date_of_birth.strftime('%b %d, %Y') if (selected_child and selected_child.date_of_birth) else "-"
    child_gender = selected_child.gender if selected_child else "-"
    child_birth_weight = f"{selected_child.birth_weight} kg" if (selected_child and selected_child.birth_weight) else "-"
    child_birth_height = f"{selected_child.birth_height} cm" if (selected_child and selected_child.birth_height) else "-"

    # Age calculation in months and days
    age_display = "-"
    if selected_child and selected_child.date_of_birth:
        days_old = (today_dt - selected_child.date_of_birth).days
        months_old = days_old // 30
        if months_old == 0:
            age_display = f"{days_old} Days Old"
        elif months_old < 24:
            age_display = f"{months_old} Month{'s' if months_old > 1 else ''} Old"
        else:
            yrs = months_old // 12
            rem_m = months_old % 12
            age_display = f"{yrs} Year{'s' if yrs > 1 else ''} {rem_m} Month{'s' if rem_m > 1 else ''}"

    growth_logs = child_growth_record.objects.filter(CHILD=selected_child).order_by('growth_date', 'id') if selected_child else []
    latest_growth = growth_logs.last() if growth_logs else None
    
    current_weight_val = f"{selected_child.birth_weight} kg" if (selected_child and selected_child.birth_weight) else "0 kg"
    if latest_growth and latest_growth.weight:
        current_weight_val = f"{latest_growth.weight} kg"

    current_height_val = f"{selected_child.birth_height} cm" if (selected_child and selected_child.birth_height) else "0 cm"
    if latest_growth and latest_growth.height:
        current_height_val = f"{latest_growth.height} cm"

    # Vaccinations summary (Taken, Scheduled, Missed)
    valid_child_vaxes = get_child_filtered_vaccinations(selected_child, mother)
    completed_vax_count = len([v for v in valid_child_vaxes if v.effective_status == 'Taken'])
    scheduled_vax_count = len([v for v in valid_child_vaxes if v.effective_status in ['Scheduled', 'Rescheduled']])
    missed_vax_count = len([v for v in valid_child_vaxes if v.effective_status == 'Missed'])
    total_vax_count = len(valid_child_vaxes)
    upcoming_vax = next((v for v in valid_child_vaxes if v.effective_status in ['Scheduled', 'Rescheduled']), None)

    # Build comprehensive growth records with official At Birth entry
    growth_logs_data = []
    if selected_child:
        raw_list = []
        for g in growth_logs:
            details_str = g.report_details or ""
            if "[at birth]" in details_str.lower() or "registered birth metrics" in details_str.lower():
                continue

            clean_notes, media_url, media_filename, media_type = parse_growth_record_details(details_str)

            log_m = max((g.growth_date.year - selected_child.date_of_birth.year) * 12 + g.growth_date.month - selected_child.date_of_birth.month, 0) if selected_child.date_of_birth else 0
            if "[Month " in details_str:
                try:
                    m_tag = int(details_str.split("[Month ")[1].split("]")[0])
                    log_m = m_tag
                except Exception:
                    pass
            stage_label = f"Month {log_m}"

            raw_list.append({
                'id': g.id,
                'month': log_m,
                'stage_label': stage_label,
                'growth_date': g.growth_date,
                'date': g.growth_date.strftime('%b %d, %Y') if g.growth_date else "-",
                'weight': f"{g.weight} kg",
                'height': f"{g.height} cm",
                'condition': g.health_condition or "Normal / Healthy Growth",
                'details': clean_notes,
                'media_url': media_url,
                'media_filename': media_filename,
                'media_type': media_type,
            })

        raw_list.sort(key=lambda x: (x.get('growth_date') or date(2000, 1, 1)))
        growth_logs_data = raw_list

    context = {
        'mother': mother,
        'children': children_qs,
        'selected_child': selected_child,
        'child_id_str': child_id_str,
        'child_name': child_name,
        'child_dob': child_dob,
        'child_gender': child_gender,
        'age_display': age_display,
        'child_birth_weight': child_birth_weight,
        'child_birth_height': child_birth_height,
        'current_weight_val': current_weight_val,
        'current_height_val': current_height_val,
        'completed_vax_count': completed_vax_count,
        'total_vax_count': total_vax_count,
        'upcoming_vax': upcoming_vax,
        'growth_logs_data': growth_logs_data,
        'growth_logs_count': len(growth_logs_data),
        'today': today_dt.strftime('%b %d, %Y'),
    }
    return render(request, 'user/user_child_profile.html', context)


def user_child_growth(request):
    """
    Renders dedicated Child Record / Growth Tracking View Page for the logged-in mother.
    Displays month-by-month physical growth logs (weight, height, health condition,
    observation details) added by ASHA, with visual trend comparisons.
    """
    mother, err_redirect = get_logged_in_mother(request)
    if err_redirect:
        return err_redirect

    today_dt = date.today()
    children_qs = child.objects.filter(USER=mother) if mother else child.objects.none()
    
    child_id_param = request.GET.get('child_id')
    selected_child = None
    if child_id_param and children_qs.filter(id=child_id_param).exists():
        selected_child = children_qs.get(id=child_id_param)
    else:
        selected_child = children_qs.first()

    child_id_str = f"CH-{selected_child.id:04d}" if selected_child else "-"
    child_name = selected_child.child_name if selected_child else "-"
    child_dob = selected_child.date_of_birth.strftime('%b %d, %Y') if (selected_child and selected_child.date_of_birth) else "-"
    child_gender = selected_child.gender if selected_child else "-"
    child_birth_weight = f"{selected_child.birth_weight} kg" if (selected_child and selected_child.birth_weight) else "-"

    growth_logs = child_growth_record.objects.filter(CHILD=selected_child).order_by('-growth_date') if selected_child else []
    latest_growth = growth_logs.first() if growth_logs else None
    
    current_weight_val = "0"
    current_weight_sub = "No data recorded"
    if latest_growth and latest_growth.weight:
        current_weight_val = f"{latest_growth.weight}"
        current_weight_sub = f"Recorded on {latest_growth.growth_date.strftime('%b %d, %Y')}"
    elif selected_child and selected_child.birth_weight:
        current_weight_val = f"{selected_child.birth_weight}"
        current_weight_sub = "Birth Weight"

    current_height_val = "0"
    current_height_sub = "No data recorded"
    if latest_growth and latest_growth.height:
        current_height_val = f"{latest_growth.height}"
        current_height_sub = f"Recorded on {latest_growth.growth_date.strftime('%b %d, %Y')}"
    elif selected_child and selected_child.birth_height:
        current_height_val = f"{selected_child.birth_height}"
        current_height_sub = "Birth Height"

    growth_logs_data = []
    if selected_child:
        has_birth_record = False
        raw_list = []
        for g in growth_logs:
            details_str = g.report_details or ""
            if "[at birth]" in details_str.lower() or "registered birth metrics" in details_str.lower():
                continue

            clean_notes, media_url, media_filename, media_type = parse_growth_record_details(details_str)

            log_m = max((g.growth_date.year - selected_child.date_of_birth.year) * 12 + g.growth_date.month - selected_child.date_of_birth.month, 0)
            if "[Month " in details_str:
                try:
                    m_tag = int(details_str.split("[Month ")[1].split("]")[0])
                    log_m = m_tag
                except Exception:
                    pass
            stage_label = f"Month {log_m}"

            raw_list.append({
                'id': g.id,
                'month': log_m,
                'stage_label': stage_label,
                'growth_date': g.growth_date,
                'date': g.growth_date.strftime('%b %d, %Y'),
                'weight': f"{g.weight} kg",
                'height': f"{g.height} cm",
                'condition': g.health_condition or "Normal / Healthy Growth",
                'details': clean_notes,
                'media_url': media_url,
                'media_filename': media_filename,
                'media_type': media_type,
            })

        raw_list.sort(key=lambda x: x['growth_date'])
        growth_logs_data = raw_list

    context = {
        'mother': mother,
        'children': children_qs,
        'selected_child': selected_child,
        'child_id_str': child_id_str,
        'child_name': child_name,
        'child_dob': child_dob,
        'child_gender': child_gender,
        'child_birth_weight': child_birth_weight,
        'current_weight_val': current_weight_val,
        'current_weight_sub': current_weight_sub,
        'current_height_val': current_height_val,
        'current_height_sub': current_height_sub,
        'growth_logs_data': growth_logs_data,
        'records_count': len(growth_logs_data),
        'today': today_dt.strftime('%b %d, %Y'),
    }
    return render(request, 'user/view_child_growth.html', context)


def user_vaccination_schedule(request):
    """
    Renders dedicated Month-by-Month Vaccination Schedule & Tracker for the child.
    Organizes vaccines by Month 0 (At Birth), Month 1 (6 Weeks), Month 2 (10 Weeks),
    Month 3 (14 Weeks), Month 9 (9 Months), and Boosters (12-24 Months).
    Displays doses taken, scheduled dates, time slots, and status badges.
    """
    mother, err_redirect = get_logged_in_mother(request)
    if err_redirect:
        return err_redirect

    today_dt = date.today()
    children_qs = child.objects.filter(USER=mother) if mother else child.objects.none()
    
    child_id_param = request.GET.get('child_id')
    selected_child = None
    if child_id_param and children_qs.filter(id=child_id_param).exists():
        selected_child = children_qs.get(id=child_id_param)
    else:
        selected_child = children_qs.first()

    # Strictly only Taken/Completed vaccines and Scheduled/Rescheduled vaccines that were notified to the mother
    all_vax = get_child_filtered_vaccinations(selected_child, mother)

    # Organize vaccines into standard developmental month brackets
    month_brackets = [
        {'id': 0, 'label': 'Month 0 (At Birth)', 'desc': 'Primary birth immunity doses (BCG, OPV 0, Hep B)', 'vax_list': []},
        {'id': 1, 'label': 'Month 1 - 2 (6 Weeks)', 'desc': 'Primary infant protection series (OPV 1, Pentavalent 1, Rotavirus 1, PCV 1, IPV 1)', 'vax_list': []},
        {'id': 2, 'label': 'Month 2 - 3 (10 Weeks)', 'desc': 'Second primary series (Pentavalent 2, OPV 2, Rotavirus 2)', 'vax_list': []},
        {'id': 3, 'label': 'Month 3 - 4 (14 Weeks)', 'desc': 'Third primary series (Pentavalent 3, OPV 3, Rotavirus 3, PCV 2, IPV 2)', 'vax_list': []},
        {'id': 6, 'label': 'Month 6 (6 Months)', 'desc': 'Typhoid & Pediatric Influenza Protection (TCV / Flu 1)', 'vax_list': []},
        {'id': 9, 'label': 'Month 9 (9 Months)', 'desc': 'Measles, Rubella & Vitamin A Dose 1', 'vax_list': []},
        {'id': 12, 'label': 'Month 12 (1 Year / 12th Month)', 'desc': 'Japanese Encephalitis & Hepatitis Protection (JE-1 / Hep A-1)', 'vax_list': []},
        {'id': 16, 'label': 'Month 16 - 24 (Booster Phase)', 'desc': 'Booster immunization series (DPT Booster 1, OPV Booster, MR 2)', 'vax_list': []},
    ]

    completed_count = 0
    scheduled_count = 0
    missed_count = 0

    for v in all_vax:
        target = v.target_month or 0
        eff_stat = getattr(v, 'effective_status', v.status)
        if eff_stat in ['Completed', 'Taken']:
            completed_count += 1
            status_label = 'Taken'
            chip_class = 'status-completed'
        elif eff_stat == 'Missed':
            missed_count += 1
            status_label = 'Missed'
            chip_class = 'status-missed'
        elif eff_stat == 'Rescheduled':
            scheduled_count += 1
            status_label = 'Rescheduled'
            chip_class = 'status-rescheduled'
        else:
            scheduled_count += 1
            status_label = 'Scheduled'
            chip_class = 'status-scheduled'

        # Find schedule session time if linked
        schedule_info = vaccine_schedule.objects.filter(VACCINATION=v).first()
        v_data = {
            'id': v.id,
            'name': v.vaccine_name,
            'type': v.vaccine_type or 'Immunization',
            'month': v.target_month,
            'description': v.description or 'Scheduled immunization dose notified by Health Admin.',
            'date': v.vaccination_date.strftime('%b %d, %Y') if v.vaccination_date else 'Scheduled',
            'status': status_label,
            'status_display': getattr(v, 'effective_status_display', status_label),
            'chip_class': chip_class,
            'raw_status': v.status,
            'time_slot': f"{schedule_info.time_from.strftime('%I:%M %p')} - {schedule_info.time_to.strftime('%I:%M %p')}" if schedule_info else None
        }

        # Bracket assignment
        placed = False
        for b in month_brackets:
            if b['id'] == 16 and target >= 16:
                b['vax_list'].append(v_data)
                placed = True
                break
            elif b['id'] == 12 and 12 <= target < 16:
                b['vax_list'].append(v_data)
                placed = True
                break
            elif b['id'] == target:
                b['vax_list'].append(v_data)
                placed = True
                break
        if not placed:
            month_brackets[0]['vax_list'].append(v_data)

    total_count = len(all_vax)
    progress_percent = round((completed_count / total_count * 100)) if total_count > 0 else 0

    context = {
        'mother': mother,
        'children': children_qs,
        'selected_child': selected_child,
        'month_brackets': month_brackets,
        'total_count': total_count,
        'completed_count': completed_count,
        'scheduled_count': scheduled_count,
        'missed_count': missed_count,
        'progress_percent': progress_percent,
        'today': today_dt.strftime('%b %d, %Y'),
    }
    return render(request, 'user/view_vaccination_schedule.html', context)


def user_kit_history(request):
    """
    Renders dedicated Nutrition Kit History Page for the logged-in mother.
    Displays complete record of nutritional supplementary food packs, Matrutva Kits,
    and iron supplements received from the Anganwadi teacher with status badges and distribution dates.
    """
    mother, err_redirect = get_logged_in_mother(request)
    if err_redirect:
        return err_redirect

    today_dt = date.today()
    all_kits = nutrition_kit.objects.filter(USER=mother).order_by('-distribution_date', '-date') if mother else nutrition_kit.objects.none()

    total_kits = all_kits.count()
    collected_kits = all_kits.filter(status__in=['Collected', 'Distributed']).count()
    pending_kits = all_kits.filter(status='Pending').count()
    total_qty = sum([k.quantity or 1 for k in all_kits])

    last_kit = all_kits.first()
    last_distribution_date = last_kit.distribution_date.strftime('%b %d, %Y') if (last_kit and last_kit.distribution_date) else "None"

    context = {
        'mother': mother,
        'all_kits': all_kits,
        'total_kits': total_kits,
        'collected_kits': collected_kits,
        'pending_kits': pending_kits,
        'total_qty': total_qty,
        'last_distribution_date': last_distribution_date,
        'today': today_dt.strftime('%b %d, %Y'),
    }
    return render(request, 'user/view_kit_history.html', context)


def user_notifications(request):
    """
    Renders dedicated Notifications Center for the logged-in mother.
    Strictly displays ONLY TWO types of notifications:
    1. Nutrition Kit Alerts (sent by Anganwadi Teacher)
    2. Child Vaccination Reminders (sent by Health Admin)
    """
    mother, err_redirect = get_logged_in_mother(request)
    if err_redirect:
        return err_redirect

    today_dt = date.today()
    category_filter = request.GET.get('category', 'all')

    # Get strictly filtered Kit and Vaccine notifications with deduplication
    formatted_notifs = get_user_filtered_notifications(mother)

    # Filter if requested
    if category_filter == 'kit':
        display_notifs = [n for n in formatted_notifs if n['type'] == 'kit']
    elif category_filter == 'vaccine':
        display_notifs = [n for n in formatted_notifs if n['type'] == 'vaccine']
    else:
        display_notifs = formatted_notifs

    new_count = len([n for n in formatted_notifs if n.get('is_new', False)])
    total_count = len(formatted_notifs)
    kit_count = len([n for n in formatted_notifs if n['type'] == 'kit'])
    vax_count = len([n for n in formatted_notifs if n['type'] == 'vaccine'])

    active_notifs = [n for n in display_notifs if not n.get('is_past', False)]
    past_notifs = [n for n in display_notifs if n.get('is_past', False)]
    active_count = len([n for n in formatted_notifs if not n.get('is_past', False)])
    past_count = len([n for n in formatted_notifs if n.get('is_past', False)])

    context = {
        'mother': mother,
        'notifications': display_notifs,
        'active_notifs': active_notifs,
        'past_notifs': past_notifs,
        'total_count': total_count,
        'active_count': active_count,
        'past_count': past_count,
        'new_count': new_count,
        'notif_count': new_count,
        'kit_count': kit_count,
        'vax_count': vax_count,
        'active_category': category_filter,
        'today': today_dt.strftime('%b %d, %Y'),
    }
    return render(request, 'user/notification.html', context)


def mark_notifications_seen(request):
    """
    AJAX endpoint to acknowledge notifications:
    - action='ok': marks notifications as seen in database.
    - action='remind_again': dismisses popup for current session, keeps unread so it pops up again on next login!
    """
    mother, err_redirect = get_logged_in_mother(request)
    if not mother:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=403)

    action = request.POST.get('action', 'ok').strip().lower()

    if action == 'remind_again':
        request.session['notif_popup_dismissed_session'] = True
        all_notifs = get_user_filtered_notifications(mother)
        unread_count = len([n for n in all_notifs if n.get('is_new', False)])
        return JsonResponse({
            'status': 'success',
            'action': 'remind_again',
            'message': 'Notification will pop up again next time you log in.',
            'unread_count': unread_count
        })

    notif_ids = request.POST.getlist('notif_ids[]')
    if not notif_ids and request.POST.get('notif_ids'):
        notif_ids = [x.strip() for x in request.POST.get('notif_ids').split(',') if x.strip()]

    marked = mark_notifications_as_seen(mother, notif_ids if notif_ids else None)
    request.session['notif_popup_dismissed_session'] = True

    all_notifs = get_user_filtered_notifications(mother)
    unread_count = len([n for n in all_notifs if n.get('is_new', False)])
    return JsonResponse({'status': 'success', 'action': 'ok', 'marked': marked, 'unread_count': unread_count})




# ================= PREGNANCY RECORD VIEWS (ASHA WORKER) =================
def manage_pregnancy(request):
    worker = get_current_asha_worker(request)

    area_q = get_area_filter_q(worker.Area_assigned) if worker else Q()
    area_mothers = user_table.objects.filter(area_q) if worker else user_table.objects.all()
    all_mothers_qs = area_mothers.filter(ASHA__isnull=False).distinct().order_by('name') if worker else user_table.objects.filter(ASHA__isnull=False).order_by('name')

    # Handle Record Deletion
    action_type = request.POST.get("action_type", "")
    if request.method == "POST" and action_type == "delete_pregnancy_record":
        record_id = request.POST.get("record_id")
        if record_id:
            pregnancy_record.objects.filter(id=record_id, USER__in=all_mothers_qs).delete()
            messages.success(request, "Checkup record deleted successfully.")
            return redirect('/myapp/manage_pregnancy/?tab=list')

    # Handle New Pregnancy Checkup POST
    if request.method == "POST" and action_type != "delete_pregnancy_record":
        mother_id = request.POST.get("mother_id")
        checkup_date_str = request.POST.get("checkup_date") or date.today().strftime('%Y-%m-%d')
        weight = request.POST.get("weight", "").strip()
        height = request.POST.get("height", "").strip()
        blood_pressure = request.POST.get("blood_pressure", "").strip()
        hemoglobin = request.POST.get("hemoglobin", "").strip()
        health_status = request.POST.get("health_status", "Normal").strip()
        remarks = request.POST.get("remarks", "").strip()

        if not mother_id:
            messages.warning(request, "Please select a mother from your assigned area registry.")
            return redirect('/myapp/manage_pregnancy/?tab=add')

        mother = get_object_or_404(all_mothers_qs, id=mother_id)

        form_edd_str = request.POST.get("expected_delivery_date", "").strip()
        if form_edd_str:
            try:
                parsed_form_edd = datetime.strptime(form_edd_str, '%Y-%m-%d').date()
                mother.expected_delivery_date = parsed_form_edd
                mother.save()
            except ValueError:
                pass

        # Validate Checkup Date
        try:
            today_dt = datetime.strptime(checkup_date_str, '%Y-%m-%d').date() if checkup_date_str else date.today()
            if today_dt > date.today():
                messages.warning(request, "Checkup date cannot be in the future.")
                return redirect(f'/myapp/manage_pregnancy/?tab=add&selected_mother={mother.id}')
        except ValueError:
            today_dt = date.today()

        # Validate Weight
        try:
            w_val = float(weight) if weight else 62.5
            if w_val < 30.0 or w_val > 180.0:
                messages.warning(request, "Please enter a realistic maternal weight between 30.0 kg and 180.0 kg.")
                return redirect(f'/myapp/manage_pregnancy/?tab=add&selected_mother={mother.id}')
        except ValueError:
            messages.warning(request, "Invalid weight value. Please enter a valid decimal number (e.g., 62.5).")
            return redirect(f'/myapp/manage_pregnancy/?tab=add&selected_mother={mother.id}')

        # Validate Height
        try:
            h_val = float(height) if height else 160.0
            if h_val < 100.0 or h_val > 220.0:
                messages.warning(request, "Please enter a realistic maternal height between 100.0 cm and 220.0 cm.")
                return redirect(f'/myapp/manage_pregnancy/?tab=add&selected_mother={mother.id}')
        except ValueError:
            messages.warning(request, "Invalid height value. Please enter a valid decimal number (e.g., 160.0).")
            return redirect(f'/myapp/manage_pregnancy/?tab=add&selected_mother={mother.id}')

        # Validate Hemoglobin
        try:
            hb_val = float(hemoglobin) if hemoglobin else 11.2
            if hb_val < 3.0 or hb_val > 20.0:
                messages.warning(request, "Please enter a realistic hemoglobin level between 3.0 g/dL and 20.0 g/dL.")
                return redirect(f'/myapp/manage_pregnancy/?tab=add&selected_mother={mother.id}')
        except ValueError:
            messages.warning(request, "Invalid hemoglobin value. Please enter a valid decimal number (e.g., 11.2).")
            return redirect(f'/myapp/manage_pregnancy/?tab=add&selected_mother={mother.id}')

        # Validate Blood Pressure format (Systolic / Diastolic)
        bp_cleaned = blood_pressure.strip() if blood_pressure else "120/80"
        bp_match = re.match(r'^(\d{2,3})\s*/\s*(\d{2,3})$', bp_cleaned)
        if bp_match:
            sys_val, dia_val = int(bp_match.group(1)), int(bp_match.group(2))
            if not (60 <= sys_val <= 240 and 40 <= dia_val <= 150 and sys_val > dia_val):
                messages.warning(request, "Blood Pressure out of physiological range. Systolic must exceed diastolic (e.g., 120/80).")
                return redirect(f'/myapp/manage_pregnancy/?tab=add&selected_mother={mother.id}')
            blood_pressure = f"{sys_val}/{dia_val}"
        else:
            messages.warning(request, "Please enter Blood Pressure in valid 'Systolic/Diastolic' format (e.g., 120/80).")
            return redirect(f'/myapp/manage_pregnancy/?tab=add&selected_mother={mother.id}')

        # Enforce 30-day interval requirement before creating a new monthly record
        latest_c = mother.latest_child
        if latest_c:
            latest_rec = pregnancy_record.objects.filter(USER=mother, checkup_date__gt=latest_c.date_of_birth).order_by('-checkup_date', '-id').first()
        else:
            latest_rec = pregnancy_record.objects.filter(USER=mother).order_by('-checkup_date', '-id').first()

        if latest_rec:
            delta_days = (today_dt - latest_rec.checkup_date).days
            if delta_days < 30:
                days_remaining = 30 - (delta_days if delta_days > 0 else 0)
                days_str = f"{days_remaining} day" if days_remaining == 1 else f"{days_remaining} days"
                messages.warning(
                    request,
                    f"Record for this month is recorded so it will take {days_str} to enter the next record."
                )
                return redirect(f'/myapp/manage_pregnancy/?tab=add&selected_mother={mother.id}')

        prev_preg_count = mother.delivered_children_count
        edd_dt = mother.active_edd or mother.expected_delivery_date or (today_dt + timedelta(days=240))
        if mother.has_delivered or not mother.is_currently_pregnant or not mother.expected_delivery_date:
            mother.expected_delivery_date = edd_dt
            mother.save(update_fields=['expected_delivery_date'])

        next_dt = today_dt + timedelta(days=30)

        pregnancy_record.objects.create(
            USER=mother,
            ASHA=worker or mother.ASHA or asha_worker.objects.first(),
            previous_pregnency_count=prev_preg_count,
            expected_delivery_date=edd_dt,
            checkup_date=today_dt,
            weight=w_val,
            height=h_val,
            blood_pressure=blood_pressure or "120/80",
            hemoglobin=hb_val,
            health_status=health_status,
            additional_report=remarks,
            next_checkup_date=next_dt
        )
        preg_label = f"Pregnancy #{prev_preg_count + 1}" if prev_preg_count > 0 else "Active Pregnancy"
        messages.success(request, f"Maternal health metrics for '{mother.name}' ({preg_label}) logged successfully!")
        return redirect('/myapp/manage_pregnancy/?tab=list')

    # Build structured mother list with status (Pregnant / Delivered) & checkup history
    search_query = request.GET.get("q", "").strip().lower()
    status_filter = request.GET.get("status", "all").strip().lower()

    mothers_list = []
    mothers_modal_data = {}
    pregnant_count = 0
    delivered_count = 0

    for m in all_mothers_qs:
        if m.is_currently_pregnant:
            m_status = "Pregnant"
            pregnant_count += 1
        elif m.has_delivered:
            m_status = "Delivered"
            delivered_count += 1
        else:
            m_status = "Pregnant" if m.expected_delivery_date else "Registered"
            if m.expected_delivery_date:
                pregnant_count += 1

        # Check filter
        if status_filter in ["pregnant", "delivered"] and m_status.lower() != status_filter:
            continue

        # Search filter
        if search_query:
            if not (
                search_query in m.name.lower() or
                search_query in m.husband_name.lower() or
                search_query in str(m.phone) or
                search_query in (m.Address or "").lower() or
                search_query in (m.blood_group or "").lower()
            ):
                continue

        m_records = pregnancy_record.objects.filter(USER=m).order_by('-checkup_date', '-id')
        records_count = m_records.count()
        latest_rec = m_records.first()

        # Check delivered children to separate previous pregnancy records
        children_objs = child.objects.filter(USER=m).order_by('date_of_birth', 'id')
        latest_c = children_objs.last()
        delivered_children_list = []
        for ch in children_objs:
            delivered_children_list.append({
                'id': ch.id,
                'name': ch.child_name,
                'dob': ch.date_of_birth.strftime('%b %d, %Y'),
                'gender': ch.gender,
                'weight': f"{ch.birth_weight} kg",
                'height': f"{ch.birth_height} cm",
                'blood_group': ch.blood_group,
                'place_of_birth': ch.place_of_birth,
                'hospital': ch.hospital or "Community Health Center",
                'delivery_type': ch.delivery_type or "Normal",
                'health_status': ch.health_status or "Healthy",
            })

        logs_data = []
        current_logs = []
        previous_logs = []
        for r in m_records:
            log_item = {
                'id': r.id,
                'date': r.checkup_date.strftime('%b %d, %Y'),
                'weight': f"{r.weight} kg",
                'height': f"{r.height} cm",
                'bp': r.blood_pressure,
                'hb': f"{r.hemoglobin} g/dL",
                'status': r.health_status,
                'notes': r.additional_report or "Routine Monthly Checkup",
                'edd': r.expected_delivery_date.strftime('%b %d, %Y') if r.expected_delivery_date else "N/A",
                'gestation_week': r.gestation_week_display,
                'gestation_month': f"Month {r.gestation_month}" if r.gestation_month else "N/A",
                'gestational_stage': r.gestational_stage,
            }
            logs_data.append(log_item)
            if latest_c and r.checkup_date <= latest_c.date_of_birth:
                previous_logs.append(log_item)
            else:
                current_logs.append(log_item)

        mothers_modal_data[str(m.id)] = {
            'id': m.id,
            'name': m.name,
            'spouse': m.husband_name,
            'phone': str(m.phone),
            'age': m.age,
            'blood_group': m.blood_group or 'O+',
            'address': m.Address or 'N/A',
            'status': m_status,
            'has_delivered': m.has_delivered,
            'has_delivered_child': m.has_delivered_child,
            'is_pregnant': m.is_currently_pregnant,
            'current_pregnancy_number': m.current_pregnancy_number,
            'pregnancy_month': m.gestation_month if m.is_currently_pregnant else None,
            'gestation_weeks': m.gestation_weeks if m.is_currently_pregnant else None,
            'status_display': m.pregnancy_status_display if m.is_currently_pregnant else m_status,
            'active_edd': m.active_edd.strftime('%b %d, %Y') if (m.is_currently_pregnant and m.active_edd) else (m.expected_delivery_date.strftime('%b %d, %Y') if (m.is_currently_pregnant and m.expected_delivery_date) else None),
            'logs_count': records_count,
            'last_checkup': latest_rec.checkup_date.strftime('%b %d, %Y') if latest_rec else 'Initial Visit',
            'last_checkup_iso': latest_rec.checkup_date.strftime('%Y-%m-%d') if latest_rec else '',
            'gestational_age': m.gestation_week_display if m.is_currently_pregnant else ('Delivered' if m.has_delivered else 'N/A'),
            'logs': logs_data,
            'current_logs': current_logs,
            'previous_logs': previous_logs,
            'delivered_children': delivered_children_list,
            'has_previous_pregnancy': bool(len(delivered_children_list) > 0 or len(previous_logs) > 0),
        }

        mothers_list.append({
            'obj': m,
            'status': m_status,
            'records_count': records_count,
            'latest_rec': latest_rec,
        })

    active_tab = request.GET.get("tab", "list")
    selected_mother_id = request.GET.get("selected_mother", "")
    if selected_mother_id:
        active_tab = "add"

    selected_mother = None
    if selected_mother_id:
        selected_mother = all_mothers_qs.filter(id=selected_mother_id).first()

    recent_logs = []
    if selected_mother:
        recent_logs = pregnancy_record.objects.filter(USER=selected_mother).order_by('-checkup_date')[:5]

    context = {
        'worker': worker,
        'mothers_list': mothers_list,
        'all_mothers': all_mothers_qs,
        'selected_mother': selected_mother,
        'recent_logs': recent_logs,
        'mothers_modal_data_json': json.dumps(mothers_modal_data),
        'today_date': date.today().strftime('%Y-%m-%d'),
        'active_tab': active_tab,
        'search_query': request.GET.get("q", "").strip(),
        'status_filter': status_filter,
        'total_count': all_mothers_qs.count(),
        'pregnant_count': pregnant_count,
        'delivered_count': delivered_count,
    }
    return render(request, 'ashawoker/manage_pregenecy_record.html', context)


# ================= NEWBORN REGISTRATION VIEWS (ASHA WORKER) =================
def register_newborn(request):
    worker = get_current_asha_worker(request)

    area_q = get_area_filter_q(worker.Area_assigned) if worker else Q()
    area_mothers = user_table.objects.filter(area_q) if worker else user_table.objects.all()
    all_area_mothers = area_mothers.filter(ASHA__isnull=False).distinct().order_by('name') if worker else user_table.objects.filter(ASHA__isnull=False).order_by('name')

    today = date.today()
    eligible_mothers = []
    for m in all_area_mothers:
        # Exclude mothers who are not currently pregnant
        if not m.is_currently_pregnant:
            continue

        if m.expected_delivery_date:
            preg_start = m.expected_delivery_date - timedelta(days=280)
        else:
            p_rec = pregnancy_record.objects.filter(USER=m).order_by('checkup_date').first()
            preg_start = p_rec.checkup_date if p_rec else (m.registration_date or today)

        days_completed = (today - preg_start).days
        records_count = pregnancy_record.objects.filter(USER=m).count()

        # Include mother in dropdown only if she has completed at least 6 months (180 days) of pregnancy or has 6+ records
        if days_completed >= 180 or records_count >= 6:
            eligible_mothers.append(m)

    if request.method == "POST":
        mother_id = request.POST.get("mother_id")
        child_name = request.POST.get("child_name", "").strip()
        gender = request.POST.get("gender", "Male").strip()
        dob_str = request.POST.get("dob") or today.strftime('%Y-%m-%d')
        birth_weight = request.POST.get("birth_weight", "").strip()
        blood_group = request.POST.get("blood_group", "").strip()
        observations = request.POST.get("observations", "").strip()

        if not mother_id:
            messages.warning(request, "Please choose a mother from your assigned area registry.")
            return redirect('/myapp/register_newborn/')

        mother = get_object_or_404(all_area_mothers, id=mother_id)

        try:
            bw_val = float(birth_weight) if birth_weight else 3.1
            if bw_val < 0.5 or bw_val > 8.0:
                messages.warning(request, "Validation Error: Birth weight must be between 0.5 kg and 8.0 kg.")
                return redirect('/myapp/register_newborn/')
        except ValueError:
            messages.warning(request, "Validation Error: Invalid birth weight. Please enter a valid decimal number (e.g., 3.1).")
            return redirect('/myapp/register_newborn/')

        if gender not in ['Male', 'Female', 'Other']:
            gender = 'Male'

        VALID_BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        if blood_group and blood_group.strip().upper() not in VALID_BLOOD_GROUPS:
            messages.warning(request, "Validation Error: Please select a valid blood group (A+, A-, B+, B-, AB+, AB-, O+, O-).")
            return redirect('/myapp/register_newborn/')

        try:
            dob_dt = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else today
        except ValueError:
            dob_dt = today

        if dob_dt > today:
            messages.warning(request, "Validation Error: Child date of birth cannot be in the future.")
            return redirect('/myapp/register_newborn/')

        # Minimum DOB based on mother's expected delivery date (approx 280 days before expected delivery)
        if mother.expected_delivery_date:
            min_allowed = mother.expected_delivery_date - timedelta(days=280)
            if dob_dt < min_allowed:
                messages.warning(request, "Validation Error: Child date of birth is earlier than allowed based on mother's expected delivery date.")
                return redirect('/myapp/register_newborn/')

        # Prevent duplicate child registration for the same mother within 12 months (365 days)
        existing_child = child.objects.filter(USER=mother).order_by('-date_of_birth', '-id').first()
        if existing_child and existing_child.date_of_birth:
            days_gap = abs((dob_dt - existing_child.date_of_birth).days)
            if days_gap < 365:
                messages.warning(
                    request,
                    f"Duplicate Registration Restriction: A child ('{existing_child.child_name}') was already registered for mother '{mother.name}' on {existing_child.date_of_birth.strftime('%b %d, %Y')}. You cannot register another child for the same mother within 12 months."
                )
                return redirect('/myapp/register_newborn/')

        new_child = child.objects.create(
            USER=mother,
            ASHA=worker or mother.ASHA or asha_worker.objects.first(),
            child_name=child_name or f"Baby of {mother.name}",
            gender=gender,
            date_of_birth=dob_dt,
            birth_weight=bw_val,
            birth_height=50.0,
            blood_group=blood_group or mother.blood_group or "O+",
            place_of_birth=observations or "Community Health Center",
            hospital=request.POST.get("hospital", "").strip(),
            delivery_type="Normal",
            health_status="Healthy"
        )

        # Transition mother to Delivered status upon successful childbirth
        mother.expected_delivery_date = None
        mother.save(update_fields=['expected_delivery_date'])

        messages.success(request, f"Newborn '{new_child.child_name}' registered successfully in {worker.Area_assigned if worker else 'Area'}!")
        return redirect('/myapp/register_newborn/')

    context = {
        'worker': worker,
        'assigned_area': worker.Area_assigned if worker else 'All Areas',
        'mothers': eligible_mothers,
        'today_date': today.strftime('%Y-%m-%d'),
    }
    return render(request, 'ashawoker/register_newborn.html', context)


# ================= CHILD GROWTH RECORD VIEWS (ASHA WORKER) =================
def child_growth_record_view(request):
    worker = get_current_asha_worker(request)

    area_q = get_area_filter_q(worker.Area_assigned) if worker else Q()
    if worker:
        area_mothers = user_table.objects.filter(area_q)
        all_children_qs = child.objects.filter(Q(USER__in=area_mothers) | Q(ASHA=worker)).select_related('USER', 'ASHA').distinct().order_by('child_name')
    else:
        all_children_qs = child.objects.all().select_related('USER', 'ASHA').order_by('child_name')

    # Handle Record Deletion
    action_type = request.POST.get("action_type", "")
    if request.method == "POST" and action_type == "delete_growth_record":
        record_id = request.POST.get("record_id")
        if record_id:
            child_growth_record.objects.filter(id=record_id, CHILD__in=all_children_qs).delete()
            messages.success(request, "Child growth entry deleted successfully.")
            return redirect('/myapp/child_growth_record/?tab=list')

    if request.method == "POST" and action_type == "delete_child":
        child_id = request.POST.get("child_id")
        if child_id:
            c_target = all_children_qs.filter(id=child_id).first()
            if c_target:
                c_name = c_target.child_name
                c_target.delete()
                messages.success(request, f"Child record for '{c_name}' and all associated growth logs deleted successfully.")
                return redirect('/myapp/child_growth_record/?tab=list')

    # Handle New Growth Checkup POST
    if request.method == "POST" and action_type not in ["delete_growth_record", "delete_child"]:
        child_id = request.POST.get("child_id")
        checkup_month = request.POST.get("checkup_month", "0").strip()
        existing_record_id = request.POST.get("existing_record_id", "").strip()
        weight = request.POST.get("weight", "").strip()
        height = request.POST.get("height", "").strip()
        health_condition = request.POST.get("health_condition", "Normal / Healthy Growth").strip()
        extra_details = request.POST.get("extra_details", "").strip()

        if not child_id:
            messages.warning(request, "Please select a child from your assigned area register.")
            return redirect('/myapp/child_growth_record/?tab=add')

        child_obj = get_object_or_404(all_children_qs, id=child_id)

        try:
            month_num = int(checkup_month)
        except ValueError:
            month_num = 0

        try:
            w_val = float(weight) if weight else (child_obj.birth_weight or 3.5)
            if w_val < 0.5 or w_val > 35.0:
                messages.warning(request, "Validation Error: Child weight must be between 0.5 kg and 35.0 kg.")
                return redirect(f'/myapp/child_growth_record/?tab=add&selected_child={child_obj.id}')
        except ValueError:
            messages.warning(request, "Validation Error: Invalid weight value. Please enter a valid decimal number.")
            return redirect(f'/myapp/child_growth_record/?tab=add&selected_child={child_obj.id}')

        try:
            h_val = float(height) if height else (child_obj.birth_height or 50.0)
            if h_val < 30.0 or h_val > 140.0:
                messages.warning(request, "Validation Error: Child height must be between 30.0 cm and 140.0 cm.")
                return redirect(f'/myapp/child_growth_record/?tab=add&selected_child={child_obj.id}')
        except ValueError:
            messages.warning(request, "Validation Error: Invalid height value. Please enter a valid decimal number.")
            return redirect(f'/myapp/child_growth_record/?tab=add&selected_child={child_obj.id}')

        report_file_name = ""
        if 'extra_report' in request.FILES:
            uploaded_file = request.FILES['extra_report']
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            if file_ext not in ['.pdf', '.jpg', '.jpeg', '.png']:
                messages.warning(request, "Validation Error: Only PDF, JPG, and PNG files are accepted for growth reports.")
                return redirect(f'/myapp/child_growth_record/?tab=add&selected_child={child_obj.id}')
            if uploaded_file.size > 5 * 1024 * 1024:
                messages.warning(request, "Validation Error: Growth report file cannot exceed 5 MB.")
                return redirect(f'/myapp/child_growth_record/?tab=add&selected_child={child_obj.id}')
            try:
                fs = FileSystemStorage()
                saved_name = fs.save(f"growth_reports/{uploaded_file.name}", uploaded_file)
                report_file_name = saved_name
            except Exception:
                pass

        # Check if updating an existing record
        target_rec = None
        if existing_record_id and existing_record_id.isdigit():
            target_rec = child_growth_record.objects.filter(id=int(existing_record_id), CHILD=child_obj).first()

        if not target_rec:
            all_recs = child_growth_record.objects.filter(CHILD=child_obj)
            for r in all_recs:
                m_calc = max((r.growth_date.year - child_obj.date_of_birth.year) * 12 + r.growth_date.month - child_obj.date_of_birth.month, 0)
                if m_calc == month_num:
                    target_rec = r
                    break

        if not report_file_name and target_rec and target_rec.report_details:
            m_prev = re.search(r'Report:\s*([^\s|]+)', target_rec.report_details, re.IGNORECASE)
            if m_prev:
                report_file_name = m_prev.group(1).strip()

        details_parts = []
        details_parts.append(f"[Month {month_num}]")
        if extra_details:
            details_parts.append(extra_details)
        if report_file_name:
            details_parts.append(f"Report: {report_file_name}")

        combined_details = " | ".join(details_parts)

        if target_rec:
            target_rec.weight = w_val
            target_rec.height = h_val
            target_rec.health_condition = health_condition
            target_rec.report_details = combined_details
            target_rec.save()

            if month_num == 0:
                child_obj.birth_weight = w_val
                child_obj.birth_height = h_val
                child_obj.save()

            messages.success(request, f"Month {month_num} growth record for '{child_obj.child_name}' updated successfully.")
        else:
            # Enforce 30-day minimum spacing between new growth checkup records for the same child
            latest_growth = child_growth_record.objects.filter(CHILD=child_obj).order_by('-growth_date', '-id').first()
            if latest_growth and latest_growth.growth_date:
                days_elapsed = (date.today() - latest_growth.growth_date).days
                if days_elapsed < 30:
                    days_left = 30 - days_elapsed
                    messages.warning(
                        request,
                        f"Growth Checkup Restriction: A growth record for '{child_obj.child_name}' was recorded on {latest_growth.growth_date.strftime('%b %d, %Y')} ({days_elapsed} days ago). The next monthly growth record can only be added after 30 days ({days_left} days remaining)."
                    )
                    return redirect('/myapp/child_growth_record/?tab=add')

            calc_date = child_obj.date_of_birth + timedelta(days=int(month_num * 30.4375))
            if calc_date > date.today():
                calc_date = date.today()

            child_growth_record.objects.create(
                CHILD=child_obj,
                height=h_val,
                weight=w_val,
                growth_date=calc_date,
                health_condition=health_condition,
                report_details=combined_details
            )
            messages.success(request, f"Month {month_num} growth record for '{child_obj.child_name}' saved successfully!")
        return redirect('/myapp/child_growth_record/?tab=list')

    # Build structured children list with growth status & history
    search_query = request.GET.get("q", "").strip().lower()
    condition_filter = request.GET.get("condition", "all").strip().lower()

    children_list = []
    children_modal_data = {}
    normal_count = 0
    underweight_count = 0
    attention_count = 0

    today = date.today()

    for ch in all_children_qs:
        dob = ch.date_of_birth
        months = (today.year - dob.year) * 12 + today.month - dob.month
        if months < 12:
            age_str = f"{max(months, 0)} Months"
        else:
            years = months // 12
            rem_months = months % 12
            age_str = f"{years} Yrs {rem_months} M" if rem_months else f"{years} Years"

        ch_records = child_growth_record.objects.filter(CHILD=ch).order_by('-growth_date', '-id')
        records_count = ch_records.count()
        latest_rec = ch_records.first()

        ch_status = latest_rec.health_condition if latest_rec else "Healthy / Normal"

        if "underweight" in ch_status.lower():
            underweight_count += 1
            cond_key = "underweight"
        elif "malnutrition" in ch_status.lower() or "stunted" in ch_status.lower():
            attention_count += 1
            cond_key = "attention"
        else:
            normal_count += 1
            cond_key = "normal"

        logs_data = []
        existing_months = {}
        raw_logs = []

        for r in ch_records:
            details_str = r.report_details or ""
            if "[at birth]" in details_str.lower() or "registered birth metrics" in details_str.lower():
                continue

            clean_notes, media_url, media_filename, media_type = parse_growth_record_details(details_str)

            log_m = max((r.growth_date.year - ch.date_of_birth.year) * 12 + r.growth_date.month - ch.date_of_birth.month, 0) if ch.date_of_birth else 0
            if "[Month " in details_str:
                try:
                    m_tag = int(details_str.split("[Month ")[1].split("]")[0])
                    log_m = m_tag
                except Exception:
                    pass
            stage_label = f"Month {log_m}"

            existing_months[str(log_m)] = {
                'record_id': r.id,
                'month': log_m,
                'stage_label': stage_label,
                'weight': float(r.weight),
                'height': float(r.height),
                'health_condition': r.health_condition,
                'details': clean_notes,
                'media_url': media_url,
                'media_filename': media_filename,
                'media_type': media_type,
                'date': r.growth_date.strftime('%b %d, %Y') if r.growth_date else ""
            }
            raw_logs.append({
                'id': r.id,
                'month': log_m,
                'stage_label': stage_label,
                'growth_date': r.growth_date,
                'date': r.growth_date.strftime('%b %d, %Y') if r.growth_date else "",
                'weight': f"{r.weight} kg",
                'height': f"{r.height} cm",
                'condition': r.health_condition,
                'details': clean_notes,
                'media_url': media_url,
                'media_filename': media_filename,
                'media_type': media_type,
            })

        raw_logs.sort(key=lambda x: (x.get('growth_date') or date(2000, 1, 1)))
        for item in raw_logs:
            item.pop('growth_date', None)
        logs_data = raw_logs

        # Calculate child-specific next unrecorded month number sequentially (0 -> 1 -> 2 -> 3 -> 4...)
        db_month_keys = [int(k) for k in existing_months.keys() if existing_months[k].get('record_id') is not None]
        next_month_num = 0
        while next_month_num in db_month_keys:
            next_month_num += 1

        # Chronological measurements (oldest to newest) for WHO Standard Growth Chart
        chrono_records = child_growth_record.objects.filter(CHILD=ch).order_by('growth_date')
        child_measurements = []
        if ch.birth_weight and ch.date_of_birth:
            child_measurements.append({
                'month': 0,
                'age_label': 'Birth',
                'weight': float(ch.birth_weight),
                'height': float(ch.birth_height) if ch.birth_height else 50.0,
                'condition': 'Birth Baseline',
                'date': ch.date_of_birth.strftime('%b %d, %Y')
            })

        for r in chrono_records:
            log_months = max((r.growth_date.year - ch.date_of_birth.year) * 12 + r.growth_date.month - ch.date_of_birth.month, 0)
            child_measurements.append({
                'month': log_months,
                'age_label': f"M{log_months}",
                'weight': float(r.weight),
                'height': float(r.height),
                'condition': r.health_condition,
                'date': r.growth_date.strftime('%b %d, %Y')
            })

        # WHO Standard Reference Percentiles (0 to 24 months)
        who_ref = {
            'months': [0, 1, 2, 3, 4, 6, 9, 12, 18, 24],
            'sd_minus3': [2.1, 2.9, 3.8, 4.4, 4.9, 5.7, 6.5, 7.1, 8.1, 9.0],
            'sd_minus2': [2.5, 3.4, 4.4, 5.1, 5.6, 6.4, 7.2, 7.8, 8.9, 9.9],
            'median': [3.3, 4.5, 5.6, 6.4, 7.0, 7.9, 8.9, 9.6, 10.9, 12.2],
            'sd_plus2': [4.4, 5.8, 7.1, 8.0, 8.7, 9.8, 11.0, 12.0, 13.7, 15.3]
        }

        total_logs_count = max(records_count, len(logs_data))

        children_modal_data[str(ch.id)] = {
            'id': ch.id,
            'name': ch.child_name,
            'mother': ch.USER.name if ch.USER else 'N/A',
            'phone': str(ch.USER.phone) if ch.USER else '',
            'gender': ch.gender,
            'age': age_str,
            'dob': ch.date_of_birth.strftime('%b %d, %Y'),
            'blood_group': ch.blood_group or (ch.USER.blood_group if ch.USER else 'O+'),
            'address': ch.USER.Address if ch.USER else '',
            'status': ch_status,
            'logs_count': total_logs_count,
            'weight': latest_rec.weight if latest_rec else ch.birth_weight,
            'height': latest_rec.height if latest_rec else ch.birth_height,
            'existing_months': existing_months,
            'next_month_num': next_month_num,
            'logs': logs_data,
            'measurements': child_measurements,
            'who_ref': who_ref,
        }

        # Check condition filter
        if condition_filter == "normal" and cond_key != "normal":
            continue
        elif condition_filter == "underweight" and cond_key != "underweight":
            continue
        elif condition_filter == "attention" and cond_key != "attention":
            continue

        # Search filter
        if search_query:
            mother_name = ch.USER.name if ch.USER else ""
            if not (
                search_query in ch.child_name.lower() or
                search_query in mother_name.lower() or
                search_query in ch_status.lower() or
                search_query in (ch.place_of_birth or "").lower()
            ):
                continue

        children_list.append({
            'obj': ch,
            'age_str': age_str,
            'status': ch_status,
            'records_count': total_logs_count,
            'latest_rec': latest_rec,
        })

    active_tab = request.GET.get("tab", "list")
    selected_child_id = request.GET.get("selected_child", "")
    if selected_child_id:
        active_tab = "add"

    nutritional_chart_data = {
        'labels': ['Normal / Healthy', 'Mild Underweight', 'Attention Required (Stunted/Malnutrition)'],
        'counts': [normal_count, underweight_count, attention_count],
    }

    context = {
        'worker': worker,
        'assigned_area': worker.Area_assigned if worker else 'All Areas',
        'children_list': children_list,
        'all_children': all_children_qs,
        'children_modal_data_json': json.dumps(children_modal_data),
        'nutritional_chart_json': json.dumps(nutritional_chart_data),
        'active_tab': active_tab,
        'search_query': request.GET.get("q", "").strip(),
        'condition_filter': condition_filter,
        'total_count': all_children_qs.count(),
        'normal_count': normal_count,
        'underweight_count': underweight_count,
        'attention_count': attention_count,
        'selected_child_id': selected_child_id,
    }
    return render(request, 'ashawoker/child_growth_record.html', context)


# ==============================================================================
# ================= ADMIN COMPREHENSIVE ANALYTICS & REPORTS ====================
# ==============================================================================

def get_report_analytics_data(request):
    """
    Centralized analytics engine calculating Panchayath-level maternal trends,
    nutrition kit stock inventory, child vaccination coverage & missed doses,
    and clinical high-risk metrics.
    """
    today = date.today()
    # Default to True so Complete Comprehensive Report for all wards is loaded when opening the page
    has_filter_applied = (request.GET.get("applied") != "0")
    selected_panchayath = request.GET.get("panchayath", "all").strip()
    date_range = request.GET.get("date_range", "all").strip().lower()
    search_query = request.GET.get("q", "").strip().lower()
    report_type = request.GET.get("report_type") or request.GET.get("tab") or "all"
    report_type = report_type.strip().lower()
    if report_type not in ['all', 'charts', 'wards', 'vax', 'kits', 'highrisk']:
        report_type = 'all'
    active_tab = report_type

    # 1. Base QuerySets
    all_mothers_qs = user_table.objects.all().select_related('ASHA').order_by('name')
    all_children_qs = child.objects.all().select_related('USER', 'ASHA').order_by('child_name')
    all_kits_qs = nutrition_kit.objects.all().select_related('USER', 'TEACHER').order_by('-distribution_date', '-id')
    all_preg_records_qs = pregnancy_record.objects.all().select_related('USER', 'ASHA')
    all_vax_qs = vaccination.objects.all().select_related('CHILD', 'CHILD__USER')

    # 2. Standard 5 Administrative Wards (Only all 5 wards separately and whole panchayath)
    standard_panchayaths = [
        "Ward 01 - Main Community Center",
        "Ward 02 - East Sector",
        "Ward 03 - West Gram",
        "Ward 04 - North Colony",
        "Ward 05 - South Extension"
    ]
    all_panchayaths = standard_panchayaths

    # Extract ward code if a specific ward is selected
    selected_ward_code = ""
    alt_ward_code = ""
    if selected_panchayath and selected_panchayath.lower() != "all":
        # Supports "Ward 5", "Ward 05", "ward 5", "5", "Ward 05 - South Extension"
        match = re.search(r'\b(?:ward\s*)?0?([1-5])\b', selected_panchayath, re.IGNORECASE)
        if match:
            ward_num = int(match.group(1))
            selected_ward_code = f"Ward {ward_num:02d}"
            alt_ward_code = f"Ward {ward_num}"
        else:
            selected_ward_code = selected_panchayath.split(' - ')[0].strip()
            alt_ward_code = selected_ward_code

    # Scope display label
    scope_display_name = "Whole Panchayath (All 5 Wards)"
    if selected_ward_code:
        for p in standard_panchayaths:
            if selected_ward_code.lower() in p.lower() or (alt_ward_code and alt_ward_code.lower() in p.lower()):
                scope_display_name = p
                break
        else:
            scope_display_name = selected_ward_code

    # 3. Apply Date Filtering Cutoff
    date_filter_cutoff = None
    if date_range == "30days":
        date_filter_cutoff = today - timedelta(days=30)
    elif date_range == "90days":
        date_filter_cutoff = today - timedelta(days=90)
    elif date_range == "year":
        date_filter_cutoff = date(today.year, 1, 1)

    # 4. Filter Scope (Ward vs Whole Panchayath)
    if selected_ward_code:
        filtered_mothers = all_mothers_qs.filter(
            Q(panchayath__icontains=selected_ward_code) | Q(panchayath__icontains=alt_ward_code) |
            Q(area__icontains=selected_ward_code) | Q(area__icontains=alt_ward_code) |
            Q(Address__icontains=selected_ward_code) | Q(Address__icontains=alt_ward_code) |
            Q(ASHA__Area_assigned__icontains=selected_ward_code) | Q(ASHA__Area_assigned__icontains=alt_ward_code)
        ).distinct()
        filtered_children = all_children_qs.filter(USER__in=filtered_mothers)
        filtered_kits = all_kits_qs.filter(USER__in=filtered_mothers)
        filtered_vax = all_vax_qs.filter(CHILD__in=filtered_children)
        filtered_preg_records = all_preg_records_qs.filter(USER__in=filtered_mothers)
    else:
        filtered_mothers = all_mothers_qs
        filtered_children = all_children_qs
        filtered_kits = all_kits_qs
        filtered_vax = all_vax_qs.filter(CHILD__isnull=False)
        filtered_preg_records = all_preg_records_qs

    if date_filter_cutoff:
        filtered_mothers = filtered_mothers.filter(
            Q(registration_date__gte=date_filter_cutoff) | Q(registration_date__isnull=True)
        )

    # 5. Temporal Trend Reference Windows (Last 30 Days vs Prior 30 Days)
    window_current_start = today - timedelta(days=30)
    window_prev_start = today - timedelta(days=60)
    window_prev_end = today - timedelta(days=31)

    # 6. Build Statistics for Each of the 5 Wards
    all_panchayath_stats = []
    
    for p_name in all_panchayaths:
        w_code = p_name.split(' - ')[0].strip()
        # Match mothers belonging to this ward
        p_mothers = all_mothers_qs.filter(
            Q(panchayath__icontains=w_code) |
            Q(area__icontains=w_code) |
            Q(Address__icontains=w_code) |
            Q(ASHA__Area_assigned__icontains=w_code)
        ).distinct()
        p_total_women = p_mothers.count()

        # Children in this ward
        p_children = all_children_qs.filter(USER__in=p_mothers)
        p_children_count = p_children.count()
        p_pregnant_count = sum(1 for m in p_mothers if m.is_currently_pregnant)
        p_delivered_count = sum(1 for m in p_mothers if m.has_delivered and not m.is_currently_pregnant)

        # Growth / Increase-Decrease Calculation
        curr_period_count = p_mothers.filter(
            Q(registration_date__gte=window_current_start) | Q(registration_date__isnull=True)
        ).count()
        prev_period_count = p_mothers.filter(
            registration_date__gte=window_prev_start,
            registration_date__lte=window_prev_end
        ).count()

        if prev_period_count > 0:
            growth_pct = round(((curr_period_count - prev_period_count) / prev_period_count) * 100, 1)
        elif curr_period_count > 0:
            growth_pct = 100.0
        else:
            growth_pct = 0.0

        net_change = curr_period_count - prev_period_count
        trend_direction = "up" if growth_pct > 0 else ("down" if growth_pct < 0 else "neutral")

        # Nutrition Kits in this Ward
        p_kits = all_kits_qs.filter(USER__in=p_mothers)
        p_kits_supplied = p_kits.count()
        p_kits_qty = sum(k.quantity for k in p_kits) if p_kits.exists() else 0
        p_stock_left = max((p_total_women * 2) - p_kits_supplied, 0) if p_total_women > 0 else 0

        # Child Immunization in this Ward
        p_vax_records = all_vax_qs.filter(CHILD__in=p_children)
        p_vax_supplied = p_vax_records.count()
        p_vaccinated_count = p_vax_records.filter(vaccination_date__isnull=False).values('CHILD').distinct().count()
        p_missed_vax_count = max(p_children_count - p_vaccinated_count, 0)
        p_vax_rate = round((p_vaccinated_count / p_children_count) * 100, 1) if p_children_count > 0 else 0.0

        # High-Risk Cases in this Ward
        p_high_risk = all_preg_records_qs.filter(
            USER__in=p_mothers
        ).filter(
            Q(hemoglobin__lt=10.0) |
            Q(health_status__icontains='high') |
            Q(health_status__icontains='risk') |
            Q(health_status__icontains='critical') |
            Q(blood_pressure__icontains='140') |
            Q(blood_pressure__icontains='150')
        ).values('USER').distinct().count()

        # Assigned ASHA Worker(s) for this Ward
        assigned_ashas = asha_worker.objects.filter(Area_assigned__icontains=w_code)
        asha_list = [f"{a.Full_name} ({a.Phone})" for a in assigned_ashas]
        asha_display = ", ".join(asha_list) if asha_list else "General Staff Assigned"
        asha_first = assigned_ashas.first()
        asha_name = asha_first.Full_name if asha_first else "Staff Assigned"
        asha_phone = str(asha_first.Phone) if asha_first else "N/A"

        # Assigned Anganwadi Center & Teacher for this Ward
        num_code = w_code.split()[1] if len(w_code.split()) > 1 else "01"
        matched_teachers = anganwadi_teacher.objects.filter(
            Q(center_name__icontains=num_code) | Q(Address__icontains=num_code)
        )
        t_first = matched_teachers.first()
        teacher_name = t_first.Name if t_first else f"Anganwadi Staff (Center {num_code})"
        center_name = t_first.center_name if t_first else f"Anganwadi Center {num_code}"
        teacher_phone = str(t_first.Phone) if t_first else "N/A"

        # Nutrition Kits in this Ward (Supplied vs Missed/Pending)
        p_kits = all_kits_qs.filter(USER__in=p_mothers)
        p_kits_supplied = p_kits.count()
        p_kits_qty = sum(k.quantity for k in p_kits) if p_kits.exists() else 0
        p_stock_left = max((p_total_women * 2) - p_kits_supplied, 0) if p_total_women > 0 else 0
        mothers_with_kits = set(p_kits.values_list('USER_id', flat=True))
        p_kits_missed = max(p_total_women - len(mothers_with_kits), 0) + p_kits.filter(status__in=['Pending', 'Missed', 'Rescheduled']).count()

        # Child Immunization in this Ward (Supplied vs Missed)
        p_vax_records = all_vax_qs.filter(CHILD__in=p_children)
        p_vax_supplied = p_vax_records.count()
        p_vaccinated_count = p_vax_records.filter(vaccination_date__isnull=False).values('CHILD').distinct().count()
        p_missed_vax_count = max(p_children_count - p_vaccinated_count, 0) + p_vax_records.filter(status='Missed').count()
        p_vax_rate = round((p_vaccinated_count / p_children_count) * 100, 1) if p_children_count > 0 else 0.0

        all_panchayath_stats.append({
            'name': p_name,
            'ward_code': w_code,
            'sector': p_name.split(' - ')[1] if ' - ' in p_name else '',
            'total_women': p_total_women,
            'pregnant_count': p_pregnant_count,
            'delivered_count': p_delivered_count,
            'growth_pct': growth_pct,
            'growth_str': f"+{growth_pct}%" if growth_pct > 0 else f"{growth_pct}%",
            'trend_direction': trend_direction,
            'net_change': net_change,
            'kits_supplied': p_kits_supplied,
            'kits_missed': p_kits_missed,
            'kits_qty': p_kits_qty,
            'kits_stock_left': p_stock_left,
            'children_count': p_children_count,
            'vax_supplied': p_vax_supplied,
            'vax_missed': p_missed_vax_count,
            'vaccinated_count': p_vaccinated_count,
            'missed_vax_count': p_missed_vax_count,
            'vax_rate': p_vax_rate,
            'high_risk_count': p_high_risk,
            'asha_name': asha_name,
            'asha_phone': asha_phone,
            'asha_display': asha_display,
            'teacher_name': teacher_name,
            'center_name': center_name,
            'teacher_phone': teacher_phone,
        })

    # Sort Wards by ward number order (Ward 01, Ward 02, etc.)
    all_panchayath_stats.sort(key=lambda x: x['ward_code'])

    # Determine displayed wards: If a specific ward is selected, show only that ward!
    # If "All Wards" is selected, show all 5 wards!
    if selected_ward_code:
        panchayath_stats = [
            p for p in all_panchayath_stats 
            if (
                selected_ward_code.lower() in p['ward_code'].lower() or 
                (alt_ward_code and alt_ward_code.lower() in p['ward_code'].lower()) or
                selected_ward_code.lower() in p['name'].lower() or
                (alt_ward_code and alt_ward_code.lower() in p['name'].lower())
            )
        ]
    else:
        panchayath_stats = all_panchayath_stats

    # 7. Summary KPIs for the Active Filter Scope (Whole Panchayath or Selected Ward)
    total_registered_mothers = filtered_mothers.count()
    total_pregnant_overall = sum(1 for m in filtered_mothers if m.is_currently_pregnant)
    total_delivered_overall = sum(1 for m in filtered_mothers if m.has_delivered and not m.is_currently_pregnant)
    total_children_count = filtered_children.count()
    total_vax_supplied = filtered_vax.count()
    total_kits_supplied = filtered_kits.count()
    total_kits_units_distributed = sum(k.quantity for k in filtered_kits) if filtered_kits.exists() else total_kits_supplied

    # Global growth rate calculation
    global_curr_count = filtered_mothers.filter(
        Q(registration_date__gte=window_current_start) | Q(registration_date__isnull=True)
    ).count()
    global_prev_count = filtered_mothers.filter(
        registration_date__gte=window_prev_start,
        registration_date__lte=window_prev_end
    ).count()
    
    if global_prev_count > 0:
        overall_growth_pct = round(((global_curr_count - global_prev_count) / global_prev_count) * 100, 1)
    elif global_curr_count > 0:
        overall_growth_pct = 100.0
    else:
        overall_growth_pct = 0.0
    overall_growth_trend = "up" if overall_growth_pct > 0 else ("down" if overall_growth_pct < 0 else "neutral")

    # Kit Stock Metrics & Missed Kits
    if total_registered_mothers > 0:
        total_stock_capacity = max(total_registered_mothers * 2, total_kits_units_distributed)
        total_stock_left = max(total_stock_capacity - total_kits_units_distributed, 0)
    else:
        total_stock_capacity = 0
        total_stock_left = 0
    stock_percent_remaining = round((total_stock_left / total_stock_capacity) * 100, 1) if total_stock_capacity > 0 else 0.0
    stock_percent_distributed = round((total_kits_units_distributed / total_stock_capacity) * 100, 1) if total_stock_capacity > 0 else 0.0
    total_kits_missed = sum(p['kits_missed'] for p in panchayath_stats)

    # Child Immunization Metrics in active scope
    total_vaccinated_children = filtered_vax.filter(vaccination_date__isnull=False).values('CHILD').distinct().count()
    total_missed_vax_children = max(total_children_count - total_vaccinated_children, 0) + filtered_vax.filter(status='Missed').count()
    overall_vax_coverage = round((total_vaccinated_children / total_children_count) * 100, 1) if total_children_count > 0 else 0.0

    # High-Risk Pregnancies in active scope
    high_risk_records_qs = filtered_preg_records.filter(
        Q(hemoglobin__lt=10.0) |
        Q(health_status__icontains='high') |
        Q(health_status__icontains='risk') |
        Q(health_status__icontains='critical') |
        Q(blood_pressure__icontains='140') |
        Q(blood_pressure__icontains='150')
    )
    total_high_risk_count = high_risk_records_qs.values('USER').distinct().count()

    # 8. Detailed Missed / Overdue Child Vaccination Audit List in active scope
    missed_vax_list = []
    for ch in filtered_children:
        ch_vax_records = all_vax_qs.filter(CHILD=ch, vaccination_date__isnull=False)
        received_types = [v.vaccine_type.lower() for v in ch_vax_records if v.vaccine_type]
        
        # Calculate Age
        dob = ch.date_of_birth
        months_old = (today.year - dob.year) * 12 + today.month - dob.month
        if months_old < 12:
            age_str = f"{max(months_old, 0)} Months"
        else:
            age_str = f"{months_old // 12} Yrs {months_old % 12} M" if (months_old % 12) else f"{months_old // 12} Years"

        # Standard Recommended Schedule
        due_vaccines = []
        if months_old >= 0 and not any('bcg' in vt or 'polio' in vt or 'hep' in vt for vt in received_types):
            due_vaccines.append("BCG / OPV-0 / Hep-B")
        if months_old >= 2 and not any('penta' in vt or 'opv 1' in vt or 'rotavirus' in vt for vt in received_types):
            due_vaccines.append("Pentavalent-1 / OPV-1 / Rota-1")
        if months_old >= 4 and not any('penta 2' in vt or 'penta-2' in vt or 'opv 2' in vt for vt in received_types):
            due_vaccines.append("Pentavalent-2 / OPV-2")
        if months_old >= 9 and not any('measles' in vt or 'mr' in vt or 'rubella' in vt for vt in received_types):
            due_vaccines.append("Measles & Rubella (MR-1)")

        if not ch_vax_records.exists():
            if not due_vaccines:
                due_vaccines.append("Primary Immunization Doses")
            status_tag = "Overdue (No records)"
            is_missed = True
        elif due_vaccines:
            status_tag = "Overdue Doses"
            is_missed = True
        else:
            is_missed = False

        if is_missed:
            missed_vax_list.append({
                'child_id': ch.id,
                'child_name': ch.child_name,
                'gender': ch.gender,
                'age_str': age_str,
                'dob': ch.date_of_birth.strftime('%b %d, %Y'),
                'mother_name': ch.USER.name if ch.USER else 'N/A',
                'mother_phone': str(ch.USER.phone) if ch.USER else 'N/A',
                'panchayath': ch.USER.panchayath if (ch.USER and ch.USER.panchayath) else (ch.USER.Address if ch.USER else 'Ward 01'),
                'missing_vaccines': ", ".join(due_vaccines) if due_vaccines else "Primary Childhood Vaccines",
                'status': status_tag,
                'asha_name': ch.ASHA.Full_name if ch.ASHA else 'General Staff'
            })

    # 9. Nutrition Kit Inventory Breakdown (Grouped by Real Warehouse Stock & Distributions)
    kit_breakdown = []
    
    kit_clean_names = {
        'Amrutham Prenatal Nutrition Food Pack': 'Amrutham Prenatal',
        'Maternal Medicines & Iron Micronutrient Kit': 'Iron & Medicines',
        'Milk Production & Galactagogue Herbal Pack': 'Galactagogue Herbal',
        'Postnatal Recovery & Protein Vitality Kit': 'Postnatal Vitality',
        'Child Growth Micronutrient & Syrup Kit': 'Child Growth Syrup',
        'First Trimester Mother Nutrition & Care Kit': 'Trimester 1 Nutrimix',
        'Second Trimester Amrutham Care Pack': 'Trimester 2 Nutrimix',
        'Amrutham Nutrimix & Maternal Micronutrient Care Pack (Month 7)': 'Trimester 3 Nutrimix',
        'Amrutham Nutrimix Postnatal Mother Pack': 'Postnatal Nutrimix',
    }

    # Query real warehouse stock from kit_stock
    if selected_ward_code:
        num_code = selected_ward_code.split()[1] if len(selected_ward_code.split()) > 1 else "01"
        matched_teachers = anganwadi_teacher.objects.filter(
            Q(center_name__icontains=num_code) | Q(Address__icontains=num_code)
        )
        stocks_qs = kit_stock.objects.filter(TEACHER__in=matched_teachers) if matched_teachers.exists() else kit_stock.objects.all()
    else:
        stocks_qs = kit_stock.objects.all()

    stock_totals = {}
    for st in stocks_qs:
        p_name = st.product_name or st.kit_category
        stock_totals[p_name] = stock_totals.get(p_name, 0) + st.quantity

    distinct_kit_names = []
    seen_k = set()
    for p_name in stock_totals.keys():
        if p_name not in seen_k:
            seen_k.add(p_name)
            distinct_kit_names.append(p_name)

    for k in filtered_kits:
        k_name = k.product_name or k.kit_type
        if k_name and k_name not in seen_k:
            seen_k.add(k_name)
            distinct_kit_names.append(k_name)

    for k_name in distinct_kit_names:
        matched_kits = filtered_kits.filter(Q(product_name__icontains=k_name) | Q(kit_type__icontains=k_name))
        disbursed_qty = sum(k.quantity for k in matched_kits) if matched_kits.exists() else 0
        
        # Real warehouse stock buffer
        stock_remaining = stock_totals.get(k_name, 0)
        if stock_remaining == 0:
            for s_name, s_qty in stock_totals.items():
                if k_name.lower() in s_name.lower() or s_name.lower() in k_name.lower():
                    stock_remaining = s_qty
                    break

        allocated = stock_remaining + disbursed_qty
        if allocated == 0:
            allocated = max(disbursed_qty, 10)
            stock_remaining = max(allocated - disbursed_qty, 0)

        last_dist = matched_kits.first().distribution_date.strftime('%b %d, %Y') if matched_kits.exists() else "Ready in Stock"
        
        status_label = "In Stock" if stock_remaining > 5 else ("Low Stock" if stock_remaining > 0 else "Depleted")
        status_color = "#065f46" if stock_remaining > 5 else ("#b45309" if stock_remaining > 0 else "#991b1b")
        status_bg = "#d1fae5" if stock_remaining > 5 else ("#fef3c7" if stock_remaining > 0 else "#fee2e2")

        short_label = kit_clean_names.get(k_name)
        if not short_label:
            short_label = (k_name[:20] + '..') if len(k_name) > 22 else k_name

        kit_breakdown.append({
            'kit_name': k_name,
            'short_name': short_label,
            'disbursed_qty': disbursed_qty,
            'allocated_stock': allocated,
            'stock_remaining': stock_remaining,
            'status_label': status_label,
            'status_color': status_color,
            'status_bg': status_bg,
            'last_issued': last_dist,
        })

    # 10. High-Risk Pregnancy Watchlist in active scope
    high_risk_watchlist = []
    for rec in high_risk_records_qs.order_by('-checkup_date')[:15]:
        m = rec.USER
        reasons = []
        if rec.hemoglobin and rec.hemoglobin < 10.0:
            reasons.append(f"Low Hb: {rec.hemoglobin} g/dL (Anemia)")
        if rec.blood_pressure and any(term in str(rec.blood_pressure) for term in ['140', '150', '160', 'high', 'Stage']):
            reasons.append(f"Elevated BP: {rec.blood_pressure}")
        if rec.health_status and any(term in str(rec.health_status).lower() for term in ['high', 'risk', 'complication', 'critical']):
            reasons.append(f"Status: {rec.health_status}")
        if not reasons:
            reasons.append(rec.health_status or "Clinical Observation Required")

        m_name = m.name if (m and m.name) else 'N/A'
        m_phone = str(m.phone) if (m and m.phone) else 'N/A'
        m_age = m.age if (m and m.age) else 'N/A'
        m_panchayath = (m.panchayath or m.Address or 'Ward 01') if m else 'Ward 01'

        asha_name = 'General Staff'
        if rec.ASHA and rec.ASHA.Full_name:
            asha_name = rec.ASHA.Full_name
        elif m and m.ASHA and m.ASHA.Full_name:
            asha_name = m.ASHA.Full_name

        edd_str = 'N/A'
        if rec.expected_delivery_date:
            edd_str = rec.expected_delivery_date.strftime('%b %d, %Y')
        elif m and m.expected_delivery_date:
            edd_str = m.expected_delivery_date.strftime('%b %d, %Y')

        hb_str = f"{rec.hemoglobin} g/dL" if rec.hemoglobin else "N/A"
        risk_str = " • ".join(reasons)

        high_risk_watchlist.append({
            'mother_id': m.id if m else '',
            'mother_name': m_name,
            'name': m_name,
            'age': m_age,
            'phone': m_phone,
            'panchayath': m_panchayath,
            'edd': edd_str,
            'hemoglobin': hb_str,
            'hemoglobin_val': rec.hemoglobin if rec.hemoglobin else '',
            'hemoglobin_display': hb_str,
            'blood_pressure': rec.blood_pressure or '120/80',
            'asha_name': asha_name,
            'asha': asha_name,
            'risk_summary': risk_str,
            'complication': risk_str,
        })

    # 11. Graphical Visualizations Datasets for the Dedicated Charts
    # 11.1 Monthly Time-Series Trend (Increase & Decrease in Pregnant Women Registrations)
    trend_labels = []
    trend_reg = []
    trend_preg = []
    trend_deliv = []
    trend_new_adm = []

    for i in range(5, -1, -1):
        m_offset = today.month - i
        y_offset = today.year
        while m_offset <= 0:
            m_offset += 12
            y_offset -= 1
        
        m_start = date(y_offset, m_offset, 1)
        if m_offset == 12:
            m_end = date(y_offset + 1, 1, 1) - timedelta(days=1)
        else:
            m_end = date(y_offset, m_offset + 1, 1) - timedelta(days=1)
        
        m_label = m_start.strftime('%b %y')
        trend_labels.append(m_label)

        cum_reg = filtered_mothers.filter(Q(registration_date__lte=m_end) | Q(registration_date__isnull=True)).count()
        new_in_m = filtered_mothers.filter(registration_date__gte=m_start, registration_date__lte=m_end).count()
        cum_deliv = filtered_children.filter(date_of_birth__lte=m_end).values('USER').distinct().count()
        cum_preg = max(cum_reg - cum_deliv, 0)

        trend_reg.append(cum_reg)
        trend_preg.append(cum_preg)
        trend_deliv.append(cum_deliv)
        trend_new_adm.append(new_in_m)

    # 11.2 Ward Information arrays for Charts
    p_labels = [p['name'].split(' - ')[0] if ' - ' in p['name'] else p['name'] for p in panchayath_stats]
    p_full_labels = [p['name'] for p in panchayath_stats]
    p_pregnant = [p['pregnant_count'] for p in panchayath_stats]
    p_delivered = [p['delivered_count'] for p in panchayath_stats]
    p_children_chart = [p['children_count'] for p in panchayath_stats]
    p_vax_supplied_chart = [p['vax_supplied'] for p in panchayath_stats]
    p_vax_missed_chart = [p['missed_vax_count'] for p in panchayath_stats]
    p_kits_supplied_chart = [p['kits_supplied'] for p in panchayath_stats]
    p_kits_missed_chart = [p['kits_missed'] for p in panchayath_stats]
    p_vaccinated_chart = [p['vaccinated_count'] for p in panchayath_stats]
    p_high_risk = [p['high_risk_count'] for p in panchayath_stats]

    # Nutrition Kit names & counts (Clean short names for compact canvas, full names for tooltips)
    kit_labels = [k['short_name'] for k in kit_breakdown]
    kit_full_labels = [k['kit_name'] for k in kit_breakdown]
    kit_disbursed = [k['disbursed_qty'] for k in kit_breakdown]
    kit_remaining = [k['stock_remaining'] for k in kit_breakdown]

    charts_dict = {
        'trend': {
            'labels': trend_labels,
            'registered': trend_reg,
            'pregnant': trend_preg,
            'delivered': trend_deliv,
            'new_admissions': trend_new_adm,
        },
        'vax_audit': {
            'labels': p_labels,
            'full_labels': p_full_labels,
            'supplied': p_vax_supplied_chart,
            'missed': p_vax_missed_chart,
        },
        'kit_audit': {
            'labels': p_labels,
            'full_labels': p_full_labels,
            'supplied': p_kits_supplied_chart,
            'missed': p_kits_missed_chart,
        },
        'child_stat': {
            'labels': p_labels,
            'full_labels': p_full_labels,
            'children': p_children_chart,
            'vaccinated': p_vaccinated_chart,
            'unvaccinated': p_vax_missed_chart,
        },
        'panchayath': {
            'labels': p_labels,
            'full_labels': p_full_labels,
            'pregnant': p_pregnant,
            'delivered': p_delivered,
            'children': p_children_chart,
            'vax': p_vax_supplied_chart,
            'kits': p_kits_supplied_chart,
            'high_risk': p_high_risk,
        },
        'kits': {
            'labels': kit_labels,
            'full_labels': kit_full_labels,
            'disbursed': kit_disbursed,
            'remaining': kit_remaining,
        },
    }

    summary_kpis = {
        'total_registered': total_registered_mothers,
        'total_pregnant': total_pregnant_overall,
        'total_delivered': total_delivered_overall,
        'total_children': total_children_count,
        'total_vax_supplied': total_vax_supplied,
        'vax_supplied': total_vax_supplied,
        'vax_missed': total_missed_vax_children,
        'kits_supplied': total_kits_supplied,
        'kits_missed': total_kits_missed,
        'kits_units_distributed': total_kits_units_distributed,
        'kits_stock_capacity': total_stock_capacity,
        'kits_stock_reserve': total_stock_left,
        'kits_stock_pct': stock_percent_remaining,
        'kits_disbursed_pct': stock_percent_distributed,
        'vax_completed': total_vaccinated_children,
        'vax_coverage_pct': overall_vax_coverage,
        'high_risk_count': total_high_risk_count,
        'pregnant_growth_pct': overall_growth_pct,
        'pregnant_growth_str': f"+{overall_growth_pct}%" if overall_growth_pct > 0 else f"{overall_growth_pct}%",
        'pregnant_growth_trend': overall_growth_trend,
    }

    report_type_titles = {
        'all': 'Complete Comprehensive Report',
        'charts': 'Graphics & Analytical Charts',
        'wards': 'Ward Details Information',
        'vax': 'Total Vaccination Information',
        'kits': 'Total Nutrition Kits Logistics',
        'highrisk': 'High Risk Maternal Watchlist',
    }
    report_type_display = report_type_titles.get(report_type, 'Complete Comprehensive Report')

    return {
        'has_filter_applied': has_filter_applied,
        'all_panchayaths': all_panchayaths,
        'all_panchayath_stats': all_panchayath_stats,
        'selected_panchayath': selected_panchayath,
        'selected_ward_code': selected_ward_code,
        'scope_display_name': scope_display_name,
        'date_range': date_range,
        'report_type': report_type,
        'report_type_display': report_type_display,
        'search_query': search_query,
        'active_tab': active_tab,
        'summary_kpis': summary_kpis,
        'panchayath_stats': panchayath_stats,
        'missed_vax_list': missed_vax_list,
        'kit_breakdown': kit_breakdown,
        'high_risk_watchlist': high_risk_watchlist,
        'charts': charts_dict,
        'charts_json': json.dumps(charts_dict),
        'generated_date': today.strftime('%B %d, %Y'),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }


def admin_report(request):
    """
    Renders the interactive analytical Report Dashboard for the Admin.
    """
    analytics = get_report_analytics_data(request)
    context = {
        'has_filter_applied': analytics['has_filter_applied'],
        'analytics': analytics,
        'kpis': analytics['summary_kpis'],
        'panchayaths': analytics['panchayath_stats'],
        'all_panchayaths_list': analytics['all_panchayaths'],
        'missed_vax': analytics['missed_vax_list'],
        'kits': analytics['kit_breakdown'],
        'high_risk': analytics['high_risk_watchlist'],
        'selected_panchayath': analytics['selected_panchayath'],
        'selected_ward_code': analytics['selected_ward_code'],
        'scope_display_name': analytics['scope_display_name'],
        'date_range': analytics['date_range'],
        'report_type': analytics['report_type'],
        'report_type_display': analytics['report_type_display'],
        'search_query': analytics['search_query'],
        'active_tab': analytics['active_tab'],
        'charts': analytics['charts'],
        'charts_json': analytics['charts_json'],
        'generated_date': analytics['generated_date'],
    }
    return render(request, 'admin/report.html', context)


def export_report_pdf(request):
    """
    Generates and downloads a formal, publication-ready PDF Health Analytics Report
    containing full executive KPIs, 5 Wards administrative assignments, maternal demographics,
    vaccinations supplied/missed, nutrition kits supplied/missed, and clinical watchlists.
    """
    analytics = get_report_analytics_data(request)
    kpis = analytics['summary_kpis']
    panchayaths = analytics['panchayath_stats']
    missed_vax = analytics['missed_vax_list']
    kits = analytics['kit_breakdown']
    high_risk = analytics['high_risk_watchlist']
    generated_date = analytics['generated_date']
    today = date.today()

    buffer = io.BytesIO()

    if REPORTLAB_AVAILABLE:
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        brand_green = colors.HexColor('#073423')
        sub_green = colors.HexColor('#0f4a33')
        accent_bg = colors.HexColor('#f9f6f0')
        border_col = colors.HexColor('#e2ddd3')

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            textColor=brand_green,
            alignment=0,
            spaceAfter=2
        )

        subtitle_style = ParagraphStyle(
            'DocSubTitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor('#4b5563'),
            spaceAfter=12
        )

        section_heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=10.5,
            leading=14,
            textColor=sub_green,
            spaceBefore=12,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'CellBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#1f2937')
        )

        body_bold = ParagraphStyle(
            'CellBodyBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#111827')
        )

        body_alert = ParagraphStyle(
            'CellBodyAlert',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#dc2626')
        )

        elements = []

        # Document Header
        header_text = "<b>MAATRICARE HEALTH SYSTEM</b> — ADMINISTRATIVE & ANALYTICAL HEALTH REPORT"
        elements.append(Paragraph(header_text, title_style))
        elements.append(Paragraph(f"Official Health Administration Report • Scope: {analytics['scope_display_name']} • Report: {analytics['report_type_display']} • Period: {analytics['date_range'].upper()} • Generated on {generated_date}", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=brand_green, spaceBefore=0, spaceAfter=8))

        # 1. Executive Summary & Core Health Metrics
        elements.append(Paragraph("1. Executive Summary & Core Health KPIs", section_heading_style))
        kpi_data = [
            [
                Paragraph("<b>Total Registered Beneficiaries</b>", body_style),
                Paragraph(f"<b>{kpis['total_registered']}</b>", body_bold),
                Paragraph("<b>Active Pregnant Women</b>", body_style),
                Paragraph(f"<b>{kpis['total_pregnant']} ({kpis['pregnant_growth_str']})</b>", body_bold),
            ],
            [
                Paragraph("<b>Delivered Mothers</b>", body_style),
                Paragraph(f"<b>{kpis['total_delivered']}</b>", body_bold),
                Paragraph("<b>Total Registered Children</b>", body_style),
                Paragraph(f"<b>{kpis['total_children']}</b>", body_bold),
            ],
            [
                Paragraph("<b>Vaccinations Supplied</b>", body_style),
                Paragraph(f"<b>{kpis['total_vax_supplied']} Doses ({kpis['vax_completed']} Done)</b>", body_bold),
                Paragraph("<b>Vaccinations Missed / Overdue</b>", body_style),
                Paragraph(f"<b>{kpis['vax_missed']} Overdue Doses</b>", body_alert),
            ],
            [
                Paragraph("<b>Nutrition Kits Supplied</b>", body_style),
                Paragraph(f"<b>{kpis['kits_supplied']} Packs ({kpis['kits_disbursed_pct']}%)</b>", body_bold),
                Paragraph("<b>Nutrition Kits Missed / Pending</b>", body_style),
                Paragraph(f"<b>{kpis['kits_missed']} Pending Allocation</b>", body_alert),
            ],
            [
                Paragraph("<b>Vaccination Coverage Rate</b>", body_style),
                Paragraph(f"<b>{kpis['vax_coverage_pct']}% Coverage</b>", body_bold),
                Paragraph("<b>Nutrition Kits In Stock Reserve</b>", body_style),
                Paragraph(f"<b>{kpis['kits_stock_reserve']} Units Reserve</b>", body_bold),
            ],
            [
                Paragraph("<b>High-Risk Pregnancies</b>", body_style),
                Paragraph(f"<b>{kpis['high_risk_count']} Flagged Cases</b>", body_alert),
                Paragraph("<b>Active Jurisdiction Scope</b>", body_style),
                Paragraph(f"<b>{analytics['scope_display_name']}</b>", body_bold),
            ]
        ]
        kpi_table = Table(kpi_data, colWidths=[140, 120, 140, 120])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), accent_bg),
            ('BOX', (0, 0), (-1, -1), 1, border_col),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, border_col),
            ('TOPPADDING', (0, 0), (-1, -1), 3.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 8))

        # 2. Ward Administrative Directory & Staff Assignments
        ward_heading = f"2. Ward Administrative Directory & Staff Assignments ({analytics['scope_display_name']})"
        elements.append(Paragraph(ward_heading, section_heading_style))
        ward_staff_data = [
            [
                Paragraph("<b>Ward & Sector</b>", body_bold),
                Paragraph("<b>Assigned ASHA Worker(s) & Contact</b>", body_bold),
                Paragraph("<b>Assigned Anganwadi Worker & Center</b>", body_bold),
            ]
        ]
        for p in panchayaths:
            asha_info = p.get('asha_display', p.get('asha_name', 'Not Assigned'))
            if p.get('asha_phone') and p['asha_phone'] != 'N/A':
                asha_info += f"<br/><font color='#4b5563'>Ph: {p['asha_phone']}</font>"
            
            aw_info = f"<b>{p.get('teacher_name', 'General Staff')}</b><br/><font color='#4b5563'>{p.get('center_name', 'Anganwadi Center')}</font>"
            
            ward_staff_data.append([
                Paragraph(f"<b>{p['name']}</b><br/><font color='#4b5563'>{p.get('sector', 'Community Sector')}</font>", body_style),
                Paragraph(asha_info, body_style),
                Paragraph(aw_info, body_style),
            ])

        ward_staff_table = Table(ward_staff_data, colWidths=[140, 180, 200])
        ward_staff_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), brand_green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, border_col),
            ('TOPPADDING', (0, 0), (-1, -1), 3.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ]))
        elements.append(ward_staff_table)
        elements.append(Spacer(1, 8))

        # 3. Ward Demographics, Child Health, Vaccines & Kits Breakdown
        elements.append(Paragraph("3. Ward Health Demographics & Supply Logistics Audit", section_heading_style))
        ward_metrics_data = [
            [
                Paragraph("<b>Ward Name</b>", body_bold),
                Paragraph("<b>Total Women</b>", body_bold),
                Paragraph("<b>Pregnant</b>", body_bold),
                Paragraph("<b>Delivered</b>", body_bold),
                Paragraph("<b>Children</b>", body_bold),
                Paragraph("<b>Vaccines (Supp / Missed)</b>", body_bold),
                Paragraph("<b>Kits (Supp / Missed)</b>", body_bold),
                Paragraph("<b>Coverage %</b>", body_bold),
            ]
        ]
        for p in panchayaths:
            vax_cell = f"<b>{p['vax_supplied']}</b> / <font color='#dc2626'>{p.get('vax_missed', 0)}</font>"
            kit_cell = f"<b>{p['kits_supplied']}</b> / <font color='#b45309'>{p.get('kits_missed', 0)}</font>"
            ward_metrics_data.append([
                Paragraph(p['name'], body_style),
                Paragraph(str(p['total_women']), body_style),
                Paragraph(str(p['pregnant_count']), body_style),
                Paragraph(str(p['delivered_count']), body_style),
                Paragraph(str(p['children_count']), body_style),
                Paragraph(vax_cell, body_style),
                Paragraph(kit_cell, body_style),
                Paragraph(f"<b>{p['vax_rate']}%</b>", body_style),
            ])

        ward_metrics_table = Table(ward_metrics_data, colWidths=[120, 50, 45, 50, 45, 80, 80, 50])
        ward_metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), sub_green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, border_col),
            ('TOPPADDING', (0, 0), (-1, -1), 3.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ]))
        elements.append(ward_metrics_table)
        elements.append(Spacer(1, 8))

        # 4. Nutrition Kit Logistics & Inventory Breakdown
        elements.append(Paragraph("4. Nutrition Kit Inventory & Stock Analysis", section_heading_style))
        kit_table_data = [
            [
                Paragraph("<b>Kit Name / Type</b>", body_bold),
                Paragraph("<b>Disbursed Units</b>", body_bold),
                Paragraph("<b>Allocated Stock</b>", body_bold),
                Paragraph("<b>Stock Remaining</b>", body_bold),
                Paragraph("<b>Status</b>", body_bold),
                Paragraph("<b>Last Issued</b>", body_bold),
            ]
        ]
        for k in kits:
            kit_table_data.append([
                Paragraph(k['kit_name'], body_style),
                Paragraph(f"{k['disbursed_qty']} Units", body_style),
                Paragraph(f"{k['allocated_stock']} Units", body_style),
                Paragraph(f"{k['stock_remaining']} Units", body_bold),
                Paragraph(k['status_label'], body_style),
                Paragraph(k['last_issued'], body_style),
            ])
        kit_table = Table(kit_table_data, colWidths=[150, 70, 70, 70, 80, 80])
        kit_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#047857')),
            ('GRID', (0, 0), (-1, -1), 0.5, border_col),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(kit_table)
        elements.append(Spacer(1, 8))

        # 5. Missed & Overdue Child Immunization Directory
        if missed_vax:
            elements.append(Paragraph("5. Child Immunization Audit — Overdue & Missed Schedules", section_heading_style))
            vax_table_data = [
                [
                    Paragraph("<b>Child Name</b>", body_bold),
                    Paragraph("<b>Age</b>", body_bold),
                    Paragraph("<b>Mother Name & Contact</b>", body_bold),
                    Paragraph("<b>Ward / Panchayath</b>", body_bold),
                    Paragraph("<b>Overdue Vaccines</b>", body_bold),
                    Paragraph("<b>Status</b>", body_bold),
                ]
            ]
            for v in missed_vax[:15]:
                vax_table_data.append([
                    Paragraph(v['child_name'], body_style),
                    Paragraph(v['age_str'], body_style),
                    Paragraph(f"{v['mother_name']}<br/><font color='#6b7280'>{v['mother_phone']}</font>", body_style),
                    Paragraph(v['panchayath'], body_style),
                    Paragraph(v['missing_vaccines'], body_style),
                    Paragraph(f"<b>{v['status']}</b>", body_bold),
                ])
            vax_table = Table(vax_table_data, colWidths=[90, 50, 115, 100, 105, 60])
            vax_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#991b1b')),
                ('GRID', (0, 0), (-1, -1), 0.5, border_col),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            elements.append(vax_table)
            elements.append(Spacer(1, 8))

        # 6. High-Risk Pregnancy Clinical Watchlist
        if high_risk:
            elements.append(Paragraph("6. High-Risk Maternal Health Watchlist", section_heading_style))
            hr_table_data = [
                [
                    Paragraph("<b>Mother Name & Age</b>", body_bold),
                    Paragraph("<b>Contact</b>", body_bold),
                    Paragraph("<b>Ward</b>", body_bold),
                    Paragraph("<b>EDD</b>", body_bold),
                    Paragraph("<b>Hemoglobin</b>", body_bold),
                    Paragraph("<b>Blood Pressure</b>", body_bold),
                    Paragraph("<b>Risk Factors</b>", body_bold),
                ]
            ]
            for hr in high_risk[:10]:
                hr_table_data.append([
                    Paragraph(f"{hr['mother_name']} ({hr['age']} Yrs)", body_style),
                    Paragraph(hr['phone'], body_style),
                    Paragraph(hr['panchayath'], body_style),
                    Paragraph(hr['edd'], body_style),
                    Paragraph(hr['hemoglobin'], body_bold),
                    Paragraph(hr['blood_pressure'], body_style),
                    Paragraph(hr['risk_summary'], body_style),
                ])
            hr_table = Table(hr_table_data, colWidths=[95, 65, 80, 55, 60, 60, 105])
            hr_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#b45309')),
                ('GRID', (0, 0), (-1, -1), 0.5, border_col),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            elements.append(hr_table)

        # Footer Signature Block
        elements.append(Spacer(1, 12))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=border_col, spaceBefore=4, spaceAfter=6))
        elements.append(Paragraph(f"Certified Official Health Record • Generated by MaatriCare Government Administrative Portal on {analytics['timestamp']} • Authorized Signature: _______________________", subtitle_style))

        doc.build(elements)
        pdf_content = buffer.getvalue()
        buffer.close()

        response = HttpResponse(pdf_content, content_type='application/pdf')
        if analytics.get('selected_ward_code'):
            clean_ward = analytics['selected_ward_code'].replace(' ', '_')
            pdf_filename = f"MaatriCare_Report_{clean_ward}_{today}.pdf"
        else:
            pdf_filename = f"MaatriCare_Analytics_Report_{today}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
        return response
    else:
        # Fallback if ReportLab not installed
        lines = [
            f"MAATRICARE ADMINISTRATIVE HEALTH SYSTEM -- REPORT ({analytics['scope_display_name']})",
            f"Generated: {generated_date}",
            f"Pregnant Women: {kpis['total_pregnant']}",
            f"Delivered Women: {kpis['total_delivered']}",
            f"Children Registered: {kpis['total_children']}",
            f"Vaccinations Supplied: {kpis['total_vax_supplied']} (Missed: {kpis['vax_missed']})",
            f"Nutrition Kits Supplied: {kpis['kits_supplied']} (Missed/Pending: {kpis['kits_missed']})"
        ]
        resp = HttpResponse("\n".join(lines), content_type='text/plain; charset=utf-8')
        if analytics.get('selected_ward_code'):
            clean_ward = analytics['selected_ward_code'].replace(' ', '_')
            pdf_filename = f"MaatriCare_Report_{clean_ward}_{today}.txt"
        else:
            pdf_filename = f"MaatriCare_Analytics_Report_{today}.txt"
        resp['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
        return resp


def export_report_csv(request):
    """
    Exports comprehensive analytical records, graph-based metrics, and all 5 wards demographics
    as a clean, highly reliable CSV spreadsheet (Excel compatible).
    """
    analytics = get_report_analytics_data(request)
    kpis = analytics['summary_kpis']
    panchayaths = analytics['panchayath_stats']
    missed_vax = analytics['missed_vax_list']
    kits = analytics['kit_breakdown']
    high_risk = analytics['high_risk_watchlist']
    charts = analytics['charts']
    today = date.today()

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    if analytics.get('selected_ward_code'):
        clean_ward = analytics['selected_ward_code'].replace(' ', '_')
        csv_filename = f"MaatriCare_Report_{clean_ward}_{today}.csv"
    else:
        csv_filename = f"MaatriCare_Health_Analytics_{today}.csv"
    response['Content-Disposition'] = f'attachment; filename="{csv_filename}"'

    writer = csv.writer(response)
    writer.writerow(["MAATRICARE ADMINISTRATIVE HEALTH SYSTEM - COMPREHENSIVE ANALYTICS REPORT"])
    writer.writerow([f"Jurisdiction Scope: {analytics['scope_display_name']}", f"Report Type: {analytics['report_type_display']}", f"Reporting Period: {analytics['date_range'].upper()}", f"Generated Date: {analytics['generated_date']} {analytics['timestamp']}"])
    writer.writerow([])

    # 1. Executive KPIs
    writer.writerow(["=== 1. EXECUTIVE SUMMARY & CORE HEALTH KPIS ==="])
    writer.writerow(["Key Performance Indicator", "Recorded Value", "Operational Notes & Status"])
    writer.writerow(["Total Registered Beneficiaries", kpis['total_registered'], "Mothers and infants in primary healthcare registry"])
    writer.writerow(["Current Pregnant Women", kpis['total_pregnant'], f"Active expectant mothers (Growth Trend: {kpis['pregnant_growth_str']})"])
    writer.writerow(["Delivered Mothers", kpis['total_delivered'], "Postnatal mothers with registered childbirth"])
    writer.writerow(["Registered Children", kpis['total_children'], "Infants and newborns under pediatric tracking"])
    writer.writerow(["Vaccinations Supplied", kpis['total_vax_supplied'], f"{kpis['vax_completed']} Completed Doses ({kpis['vax_coverage_pct']}% Coverage)"])
    writer.writerow(["Vaccinations Missed / Overdue", kpis['vax_missed'], "Children with overdue doses requiring ASHA follow-up"])
    writer.writerow(["Nutrition Kits Supplied", kpis['kits_supplied'], f"{kpis['kits_disbursed_pct']}% of allocated nutrition kits distributed"])
    writer.writerow(["Nutrition Kits Missed / Pending", kpis['kits_missed'], "Pending kit allocations for eligible mothers"])
    writer.writerow(["Nutrition Kits in Stock Reserve", kpis['kits_stock_reserve'], f"Safety buffer stock units ({kpis['kits_stock_pct']}% reserve)"])
    writer.writerow(["High-Risk Pregnancies Flagged", kpis['high_risk_count'], "Low Hemoglobin (<10 g/dL) or Blood Pressure flags"])
    writer.writerow([])

    # 2. Graph-Based Analytical Insights & Data
    writer.writerow(["=== 2. GRAPH-BASED ANALYTICS & STATISTICAL FINDINGS (ALL 4 CHARTS) ==="])
    
    # 2A. Graph 1: Maternal Registration Dynamics
    writer.writerow(["--- GRAPH 1: MATERNAL REGISTRATION DYNAMICS (INCREASE / DECREASE TREND) ---"])
    writer.writerow(["Analysis: 6-Month longitudinal trajectory tracking active pregnancies, cumulative registered mothers, and delivery transitions."])
    writer.writerow(["Month", "Total Registered Beneficiaries", "Active Pregnant Women", "Delivered Mothers", "Monthly Growth Trajectory"])
    if charts.get('trend'):
        trend = charts['trend']
        for i, m_label in enumerate(trend.get('labels', [])):
            reg_val = trend['registered'][i] if i < len(trend.get('registered', [])) else kpis['total_registered']
            preg_val = trend['pregnant'][i] if i < len(trend.get('pregnant', [])) else kpis['total_pregnant']
            deliv_val = trend['delivered'][i] if i < len(trend.get('delivered', [])) else kpis['total_delivered']
            writer.writerow([m_label, reg_val, preg_val, deliv_val, kpis['pregnant_growth_str']])
    writer.writerow([])

    # 2B. Graph 2: Vaccinations Supplied vs Missed
    writer.writerow(["--- GRAPH 2: CHILD IMMUNIZATION AUDIT (VACCINATIONS SUPPLIED VS MISSED) ---"])
    writer.writerow(["Analysis: Comparative audit of vaccination doses supplied/administered vs overdue missed doses across all 5 Wards."])
    writer.writerow(["Ward / Jurisdiction", "Vaccinations Supplied", "Vaccinations Missed / Overdue", "Immunization Coverage %", "Compliance Status"])
    for p in panchayaths:
        status_txt = "Optimal Coverage" if p.get('vax_missed', 0) == 0 else "Outreach Required"
        writer.writerow([p['name'], f"{p['vax_supplied']} Doses", f"{p.get('vax_missed', 0)} Missed", f"{p['vax_rate']}%", status_txt])
    vax_bench_label = f"{analytics['scope_display_name']} Benchmark" if analytics.get('selected_ward_code') else "Whole Panchayath Benchmark"
    writer.writerow([vax_bench_label, f"{kpis['total_vax_supplied']} Doses", f"{kpis['vax_missed']} Missed", f"{kpis['vax_coverage_pct']}%", "Overall Target"])
    writer.writerow([])

    # 2C. Graph 3: Nutrition Kits Supplied vs Missed
    writer.writerow(["--- GRAPH 3: NUTRITION KITS LOGISTICS (SUPPLIED VS MISSED / PENDING) ---"])
    writer.writerow(["Analysis: Distribution efficiency of nutrition kits supplied to mothers vs pending quotas and emergency reserve inventory."])
    writer.writerow(["Ward / Jurisdiction", "Kits Supplied", "Kits Missed / Pending", "Safety Stock Left", "Allocation Status"])
    for p in panchayaths:
        kit_status = "Fully Disbursed" if p.get('kits_missed', 0) == 0 else "Pending Allocation"
        writer.writerow([p['name'], f"{p['kits_supplied']} Packs", f"{p.get('kits_missed', 0)} Pending", f"{p['kits_stock_left']} Units", kit_status])
    kit_bench_label = f"{analytics['scope_display_name']} Benchmark" if analytics.get('selected_ward_code') else "Whole Panchayath Benchmark"
    writer.writerow([kit_bench_label, f"{kpis['kits_supplied']} Packs", f"{kpis['kits_missed']} Pending", f"{kpis['kits_stock_reserve']} Units Reserve", f"{kpis['kits_disbursed_pct']}% Efficiency"])
    writer.writerow([])

    # 2D. Graph 4: Registered Children Distribution
    writer.writerow(["--- GRAPH 4: REGISTERED CHILDREN DEMOGRAPHICS & PROTECTION PROFILE ---"])
    writer.writerow(["Analysis: Pediatric population distribution across Wards and protective immunization status."])
    writer.writerow(["Ward / Jurisdiction", "Total Registered Children", "Immunized Children", "Overdue / Pending", "Protection Rate %"])
    for p in panchayaths:
        writer.writerow([p['name'], p['children_count'], p['vax_supplied'], p.get('vax_missed', 0), f"{p['vax_rate']}%"])
    child_bench_label = f"{analytics['scope_display_name']} Total" if analytics.get('selected_ward_code') else "Whole Panchayath Total"
    writer.writerow([child_bench_label, kpis['total_children'], kpis['vax_completed'], kpis['vax_missed'], f"{kpis['vax_coverage_pct']}%"])
    writer.writerow([])

    # 3. Ward Directory & Staff Assignments
    sec3_header = f"=== 3. {analytics['scope_display_name'].upper()} ADMINISTRATIVE DIRECTORY & STAFF ASSIGNMENTS ==="
    writer.writerow([sec3_header])
    writer.writerow([
        "Ward Name",
        "Administrative Sector",
        "Assigned ASHA Worker(s)",
        "ASHA Contact Phone",
        "Assigned Anganwadi Worker",
        "Anganwadi Center",
        "Total Women Registered",
        "Active Pregnant Women",
        "Delivered Mothers",
        "Registered Children",
        "Vaccinations Supplied",
        "Vaccinations Missed",
        "Nutrition Kits Supplied",
        "Nutrition Kits Missed",
        "Kits Stock Remaining",
        "Immunization Coverage %",
        "High-Risk Cases Flagged"
    ])
    for p in panchayaths:
        writer.writerow([
            p['name'],
            p.get('sector', 'Primary Sector'),
            p.get('asha_display', p.get('asha_name', 'General ASHA')),
            p.get('asha_phone', 'N/A'),
            p.get('teacher_name', 'General Staff'),
            p.get('center_name', 'Anganwadi Center'),
            p['total_women'],
            p['pregnant_count'],
            p['delivered_count'],
            p['children_count'],
            p['vax_supplied'],
            p.get('vax_missed', 0),
            p['kits_supplied'],
            p.get('kits_missed', 0),
            p['kits_stock_left'],
            f"{p['vax_rate']}%",
            p['high_risk_count']
        ])
    totals_label = f"{analytics['scope_display_name'].upper()} TOTALS" if analytics.get('selected_ward_code') else "WHOLE PANCHAYATH TOTALS"
    scope_sub = f"Focus: {analytics['scope_display_name']}" if analytics.get('selected_ward_code') else "All 5 Wards Combined"
    writer.writerow([
        totals_label,
        scope_sub,
        "Assigned ASHA Worker(s)" if analytics.get('selected_ward_code') else "All Assigned ASHA Workers",
        "-",
        "Assigned Anganwadi Staff" if analytics.get('selected_ward_code') else "All Assigned Anganwadi Workers",
        f"{len(panchayaths)} Anganwadi Center(s)",
        kpis['total_registered'],
        kpis['total_pregnant'],
        kpis['total_delivered'],
        kpis['total_children'],
        kpis['total_vax_supplied'],
        kpis['vax_missed'],
        kpis['kits_supplied'],
        kpis['kits_missed'],
        kpis['kits_stock_reserve'],
        f"{kpis['vax_coverage_pct']}%",
        kpis['high_risk_count']
    ])
    writer.writerow([])

    # 4. Nutrition Kit Stock Logistics
    writer.writerow(["=== 4. NUTRITION KIT INVENTORY & STOCK LOGISTICS ==="])
    writer.writerow(["Kit Name / Type", "Disbursed Units", "Allocated Stock", "Stock Remaining", "Inventory Status", "Last Issued Date"])
    for k in kits:
        writer.writerow([k['kit_name'], k['disbursed_qty'], k['allocated_stock'], k['stock_remaining'], k['status_label'], k['last_issued']])
    writer.writerow([])

    # 5. Overdue Vaccine List
    if missed_vax:
        writer.writerow(["=== 5. CHILD IMMUNIZATION AUDIT (MISSED & OVERDUE SCHEDULES) ==="])
        writer.writerow(["Child Name", "Gender", "Age", "Date of Birth", "Mother Name", "Mother Phone", "Ward / Panchayath", "Overdue Vaccine(s)", "Status", "Assigned ASHA Worker"])
        for v in missed_vax:
            writer.writerow([v['child_name'], v['gender'], v['age_str'], v['dob'], v['mother_name'], v['mother_phone'], v['panchayath'], v['missing_vaccines'], v['status'], v['asha_name']])
        writer.writerow([])

    # 6. High-Risk Watchlist
    if high_risk:
        writer.writerow(["=== 6. HIGH-RISK MATERNAL HEALTH WATCHLIST ==="])
        writer.writerow(["Mother Name", "Age", "Contact Phone", "Ward / Panchayath", "Expected Delivery (EDD)", "Hemoglobin (g/dL)", "Blood Pressure", "Assigned ASHA", "Clinical Risk Summary"])
        for h in high_risk:
            writer.writerow([h['mother_name'], h['age'], h['phone'], h['panchayath'], h['edd'], h['hemoglobin'], h['blood_pressure'], h['asha_name'], h['risk_summary']])
        writer.writerow([])

    writer.writerow(["=== 7. OFFICIAL CERTIFICATION FOR MANUAL USAGE ==="])
    writer.writerow(["I hereby certify that this report has been compiled from live field records across all 5 administrative wards for governmental audit and manual field inspection."])
    writer.writerow(["Authorized Medical Officer Signature: _________________________________", "Date: __________________"])

    return response


def export_report_text(request):
    """
    Generates and downloads a clean, highly reliable Plain Text (.txt) Health Report
    featuring full graph-based analytical interpretations, statistics, and 5-ward demographics.
    """
    analytics = get_report_analytics_data(request)
    kpis = analytics['summary_kpis']
    panchayaths = analytics['panchayath_stats']
    missed_vax = analytics['missed_vax_list']
    kits = analytics['kit_breakdown']
    high_risk = analytics['high_risk_watchlist']
    charts = analytics['charts']
    today = date.today()

    lines = []
    lines.append("=" * 88)
    lines.append("MAATRICARE ADMINISTRATIVE HEALTH SYSTEM -- COMPREHENSIVE ANALYTICS REPORT")
    lines.append(f"Jurisdiction Scope: {analytics['scope_display_name']} | Report Type: {analytics['report_type_display']} | Period: {analytics['date_range'].upper()}")
    lines.append(f"Generated Date: {analytics['generated_date']} | Generated Timestamp: {analytics['timestamp']}")
    lines.append("=" * 88)
    lines.append("")
    lines.append("1. EXECUTIVE SUMMARY & CORE HEALTH KEY PERFORMANCE INDICATORS")
    lines.append("-" * 88)
    lines.append(f"  * Total Registered Beneficiaries : {kpis['total_registered']}")
    lines.append(f"  * Current Pregnant Women         : {kpis['total_pregnant']} (Growth Trend: {kpis['pregnant_growth_str']})")
    lines.append(f"  * Delivered Mothers with Child   : {kpis['total_delivered']}")
    lines.append(f"  * Total Registered Children      : {kpis['total_children']}")
    lines.append(f"  * Vaccinations Supplied          : {kpis['total_vax_supplied']} Doses ({kpis['vax_completed']} Completed, {kpis['vax_coverage_pct']}% Coverage)")
    lines.append(f"  * Vaccinations Missed / Overdue  : {kpis['vax_missed']} Overdue Doses Flagged")
    lines.append(f"  * Nutrition Kits Supplied        : {kpis['kits_supplied']} Packs ({kpis['kits_disbursed_pct']}% Disbursed)")
    lines.append(f"  * Nutrition Kits Missed / Pending: {kpis['kits_missed']} Pending Allocation")
    lines.append(f"  * Nutrition Kits in Stock Reserve: {kpis['kits_stock_reserve']} Units Safety Buffer")
    lines.append(f"  * High-Risk Maternal Cases       : {kpis['high_risk_count']} Priority Flagged")
    lines.append("")
    lines.append("2. GRAPH-BASED ANALYTICS & STATISTICAL FINDINGS (ALL 4 CHARTS)")
    lines.append("-" * 88)
    
    # Graph 1 Findings
    lines.append("  [GRAPH 1] MATERNAL REGISTRATION DYNAMICS (INCREASE / DECREASE TREND)")
    lines.append("  Analysis: Longitudinal tracking of active pregnancies, cumulative mothers, and deliveries.")
    lines.append(f"  {'Month':<18} | {'Total Reg':<12} | {'Pregnant':<12} | {'Delivered':<12} | {'Growth Rate'}")
    lines.append("  " + "-" * 70)
    if charts.get('trend'):
        trend = charts['trend']
        for i, m_label in enumerate(trend.get('labels', [])):
            reg_val = trend['registered'][i] if i < len(trend.get('registered', [])) else kpis['total_registered']
            preg_val = trend['pregnant'][i] if i < len(trend.get('pregnant', [])) else kpis['total_pregnant']
            deliv_val = trend['delivered'][i] if i < len(trend.get('delivered', [])) else kpis['total_delivered']
            lines.append(f"  {m_label:<18} | {reg_val:<12} | {preg_val:<12} | {deliv_val:<12} | {kpis['pregnant_growth_str']}")
    lines.append("")

    # Graph 2 Findings
    lines.append("  [GRAPH 2] CHILD IMMUNIZATION AUDIT (VACCINATIONS SUPPLIED VS MISSED)")
    lines.append("  Analysis: Immunization doses administered vs overdue missed doses across all 5 wards.")
    lines.append(f"  {'Ward / Jurisdiction':<32} | {'Supplied':<12} | {'Missed':<10} | {'Coverage':<10} | {'Status'}")
    lines.append("  " + "-" * 78)
    for p in panchayaths:
        lines.append(f"  {p['name'][:30]:<32} | {str(p['vax_supplied']) + ' Doses':<12} | {str(p.get('vax_missed', 0)) + ' Missed':<10} | {str(p['vax_rate']) + '%':<10} | {'Optimal' if p.get('vax_missed', 0) == 0 else 'Outreach Needed'}")
    vax_bench_txt = f"{analytics['scope_display_name']} Benchmark" if analytics.get('selected_ward_code') else "Whole Panchayath Benchmark"
    lines.append(f"  {vax_bench_txt:<32} | {str(kpis['total_vax_supplied']) + ' Doses':<12} | {str(kpis['vax_missed']) + ' Missed':<10} | {str(kpis['vax_coverage_pct']) + '%':<10} | {'Overall Standard'}")
    lines.append("")

    # Graph 3 Findings
    lines.append("  [GRAPH 3] NUTRITION KITS LOGISTICS (SUPPLIED VS MISSED / PENDING)")
    lines.append("  Analysis: Supply disbursement efficiency vs pending allocations and emergency reserves.")
    lines.append(f"  {'Ward / Jurisdiction':<32} | {'Supplied':<12} | {'Missed':<10} | {'Stock Left':<12} | {'Allocation Status'}")
    lines.append("  " + "-" * 80)
    for p in panchayaths:
        lines.append(f"  {p['name'][:30]:<32} | {str(p['kits_supplied']) + ' Packs':<12} | {str(p.get('kits_missed', 0)) + ' Pending':<10} | {str(p['kits_stock_left']) + ' Units':<12} | {'Fully Disbursed' if p.get('kits_missed', 0) == 0 else 'Pending Allocation'}")
    kit_bench_txt = f"{analytics['scope_display_name']} Benchmark" if analytics.get('selected_ward_code') else "Whole Panchayath Benchmark"
    lines.append(f"  {kit_bench_txt:<32} | {str(kpis['kits_supplied']) + ' Packs':<12} | {str(kpis['kits_missed']) + ' Pending':<10} | {str(kpis['kits_stock_reserve']) + ' Buffer':<12} | {kpis['kits_disbursed_pct']}% Efficiency")
    lines.append("")

    # Graph 4 Findings
    lines.append("  [GRAPH 4] REGISTERED CHILDREN DEMOGRAPHICS & PROTECTION PROFILE")
    lines.append("  Analysis: Infant cohort size and protected immunization coverage rates.")
    lines.append(f"  {'Ward / Jurisdiction':<32} | {'Children':<10} | {'Immunized':<12} | {'Overdue':<10} | {'Protection %'}")
    lines.append("  " + "-" * 78)
    for p in panchayaths:
        lines.append(f"  {p['name'][:30]:<32} | {p['children_count']:<10} | {p['vax_supplied']:<12} | {p.get('vax_missed', 0):<10} | {p['vax_rate']}%")
    child_bench_txt = f"{analytics['scope_display_name']} Total" if analytics.get('selected_ward_code') else "Whole Panchayath Total"
    lines.append(f"  {child_bench_txt:<32} | {kpis['total_children']:<10} | {kpis['vax_completed']:<12} | {kpis['vax_missed']:<10} | {kpis['vax_coverage_pct']}%")
    lines.append("")

    # 3. Ward Directory & Health Audit
    lines.append(f"3. {analytics['scope_display_name'].upper()} ADMINISTRATIVE DIRECTORY & HEALTH AUDIT")
    lines.append("-" * 88)
    lines.append(f"{'Ward Name':<28} | {'ASHA Worker':<20} | {'Anganwadi Staff':<22} | {'Women':<8} | {'Child':<6} | {'Vax':<8} | {'Kits'}")
    lines.append("-" * 88)
    for p in panchayaths:
        w_counts = f"{p['total_women']}/{p['pregnant_count']}"
        v_counts = f"{p['vax_supplied']}/{p.get('vax_missed', 0)}"
        k_counts = f"{p['kits_supplied']}/{p.get('kits_missed', 0)}"
        lines.append(f"{p['name'][:26]:<28} | {p.get('asha_display', p.get('asha_name', 'ASHA'))[:18]:<20} | {p.get('teacher_name', 'Staff')[:20]:<22} | {w_counts:<8} | {p['children_count']:<6} | {v_counts:<8} | {k_counts}")
    lines.append("-" * 88)
    lines.append("")

    # 4. Nutrition Kits
    lines.append("4. NUTRITION KIT STOCK LOGISTICS")
    lines.append("-" * 88)
    for k in kits:
        lines.append(f"  * {k['kit_name']:<30}: Disbursed: {k['disbursed_qty']} | Remaining: {k['stock_remaining']} | Status: {k['status_label']}")
    lines.append("")

    # 5. High-Risk Cases
    if high_risk:
        lines.append("5. HIGH-RISK MATERNAL WATCHLIST")
        lines.append("-" * 88)
        for h in high_risk:
            lines.append(f"  * {h['mother_name']} ({h['age']} Yrs, Ph: {h['phone']}) - Ward: {h['panchayath']} | EDD: {h['edd']} | Hb: {h['hemoglobin']} | BP: {h['blood_pressure']} | Risk: {h['risk_summary']}")
        lines.append("")

    lines.append("=" * 88)
    lines.append("OFFICIAL ADMINISTRATIVE CERTIFICATION & SIGN-OFF (FOR MANUAL USAGE)")
    lines.append("I certify that these records have been verified against active primary health registers.")
    lines.append("Inspecting Medical Officer Signature: __________________________________   Date: _________")
    lines.append("=" * 88)

    report_text = "\n".join(lines)
    response = HttpResponse(report_text, content_type='text/plain; charset=utf-8')
    if analytics.get('selected_ward_code'):
        clean_ward = analytics['selected_ward_code'].replace(' ', '_')
        txt_filename = f"MaatriCare_Report_{clean_ward}_{today}.txt"
    else:
        txt_filename = f"MaatriCare_Health_Analytics_{today}.txt"
    response['Content-Disposition'] = f'attachment; filename="{txt_filename}"'
    return response


def seed_demo_data_view(request):
    """
    1-Click Demo Data Refresh Endpoint for live demonstrations and testing.
    """
    try:
        from myapp.management.commands.seed_demo_data import seed_all_demo_data
        seed_all_demo_data()
        messages.success(request, "Demonstration data structure has been successfully refreshed with complete realistic records!")
    except Exception as e:
        messages.error(request, f"Error initializing demo structure: {str(e)}")

    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or '/myapp/report/'
    return redirect(next_url)