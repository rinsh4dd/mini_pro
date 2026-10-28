# MaatriCare — Default System Credentials Reference

This document provides a reference for all default and seed accounts across the four role-based portals in MaatriCare.

All of these accounts are populated into the database using:
```bash
python manage.py seed_demo_data
```

---

## 1. System Administrator
- **Portal URL:** [`/myapp/adminhome/`](http://127.0.0.1:8000/myapp/adminhome/) or Django Admin [`/admin/`](http://127.0.0.1:8000/admin/)
- **Username:** `admin`
- **Password:** `admin123`
- **Email:** `admin@gmail.com`
- **Permissions:** Superuser (`is_staff = True`, `is_superuser = True`, `Group: admin`)

---

## 2. ASHA Field Health Workers (All 5 Wards)
- **Portal URL:** [`/myapp/ashaworker_home/`](http://127.0.0.1:8000/myapp/ashaworker_home/)

| Ward Code | Assigned Area | Worker Name | Username | Password | Contact Phone | Qualification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Ward 01** | Main Community Center | Fatima Beevi | `asha01` | `asha01` | 9847123456 | B.Sc Nursing & Community Health |
| **Ward 02** | East Sector | Kavitha Nair | `asha02` | `asha02` | 9847123458 | Auxiliary Nurse Midwife (ANM) |
| **Ward 03** | West Gram | Priya Nair | `asha03` | `asha03` | 9847234567 | Diploma in Midwifery (GNM) |
| **Ward 04** | North Colony | Rekha Menon | `asha04` | `asha04` | 9847345677 | B.Sc Community Health Sciences |
| **Ward 05** | South Extension | Mary Joseph | `asha05` | `asha05` | 9847345678 | Auxiliary Nurse Midwife (ANM) |

---

## 3. Anganwadi Teachers (All 5 Centers)
- **Portal URL:** [`/myapp/teacher_home/`](http://127.0.0.1:8000/myapp/teacher_home/)

| Ward Code | Anganwadi Center | Teacher Name | Username | Password | Contact Phone | Qualification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Ward 01** | Model Anganwadi Center 01 | Anita Sharma | `teacher01` | `teacher01` | 9847456789 | Early Childhood Care (ECCE) |
| **Ward 02** | Community Anganwadi Center 02 | Lakshmi Menon | `teacher02` | `teacher02` | 9847567890 | Diploma in Pre-School Education |
| **Ward 03** | West Gram Anganwadi Center 03 | Sunitha Varghese | `teacher03` | `teacher03` | 9847678901 | B.Ed & ECCE Certified |
| **Ward 04** | North Colony Anganwadi Center 04 | Radhika Pillai | `teacher04` | `teacher04` | 9847789012 | Diploma in Child Psychology |
| **Ward 05** | South Extension Anganwadi Center 05 | Deepa Mohan | `teacher05` | `teacher05` | 9847890123 | Early Childhood Care (ECCE) |

---

## 4. Beneficiary Mothers
- **Self-Registration URL:** [`/myapp/user_registartion/`](http://127.0.0.1:8000/myapp/user_registartion/)
- **Dashboard URL:** [`/myapp/userhome/`](http://127.0.0.1:8000/myapp/userhome/)
- Mothers create their own custom credentials during self-registration.
- **Verification Requirement:** Newly registered mothers cannot log in until their local ward's ASHA worker approves them at `/myapp/verify_mother/`.
