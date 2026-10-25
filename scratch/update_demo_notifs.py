import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maatricaree.settings')
django.setup()

from datetime import date
from myapp.models import user_table, notification, kit_notification, nutrition_kit, notification_seen
from django.contrib.sessions.models import Session

def update_notifs():
    m = user_table.objects.get(name='Amina Rahmath')

    # 1. Remove child immune vaccine notifications
    del_count, _ = notification.objects.filter(USER=m).delete()
    print(f"Removed {del_count} vaccine/clinical notification(s) for mother {m.name}.")

    # 2. Update kit notification to Rescheduled
    kn = kit_notification.objects.filter(USER=m).first()
    if kn:
        kn.notification_message = (
            "Nutrition Kit Pickup Rescheduled: Dear Amina Rahmath, as you missed collecting your "
            "Month 7 Amrutham Nutrimix & Maternal Care Kit on the previously scheduled date, your pickup has "
            "been rescheduled to October 02, 2026 at Model Anganwadi Center 01, Ward 1. Please visit the "
            "center between 10:00 AM and 1:00 PM with your MCP card to collect your nutrition kit."
        )
        kn.notification_date = date(2026, 9, 28)
        kn.save()

        if kn.NUTRITION:
            kn.NUTRITION.distribution_date = date(2026, 10, 2)
            kn.NUTRITION.status = "Pending"
            kn.NUTRITION.save()
        print("Updated kit notification to Rescheduled (Pickup: Oct 02, 2026).")

    # 3. Clear seen records for Amina Rahmath
    notification_seen.objects.filter(USER=m).delete()
    print("Cleared notification_seen for Amina Rahmath.")

    # 4. Clear sessions to ensure clean state
    Session.objects.all().delete()
    print("Cleared stale sessions.")

if __name__ == '__main__':
    update_notifs()
