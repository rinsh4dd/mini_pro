import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maatricaree.settings')
django.setup()

from django.test import Client
from myapp.models import user_table, notification_seen
from myapp.views import get_user_filtered_notifications

def test():
    m = user_table.objects.get(name='Amina Rahmath')
    notifs = get_user_filtered_notifications(m)
    print("Total notifs for Amina:", len(notifs))
    for n in notifs:
        print(f"ID: {n['id']} | Type: {n['type']} | is_rescheduled: {n['is_rescheduled']} | title: {n['title']} | is_new: {n['is_new']}")
        print(f"Message: {n['message']}")
        print(f"Badge: {n['badge']} | Sender: {n['sender_badge']}")
    
    assert len(notifs) == 1, f"Expected 1 notif, got {len(notifs)}"
    assert notifs[0]['type'] == 'kit'
    assert notifs[0]['is_rescheduled'] is True
    assert notifs[0]['is_new'] is True

    # Test login client and verify popup on dashboard
    c = Client()
    r_login = c.post('/myapp/login_post/', {'username': 'ward1mother', 'password': 'Mother@123'})
    assert r_login.status_code == 302
    r_home = c.get(r_login.url)
    print("r_home status:", r_home.status_code)
    if r_home.status_code == 302:
        print("Redirected to:", r_home.url)
        r_home = c.get(r_home.url)
        print("Final status:", r_home.status_code)
    html = r_home.content.decode('utf-8')
    assert 'id="loginNotifModal"' in html
    assert 'Rescheduled' in html
    assert 'Remind me again' in html
    assert 'btnConfirmOkPopup' in html
    assert 'fa-clock-rotate-left' in html
    print("\n[SUCCESS] Dashboard popup successfully renders Rescheduled Kit Notification with 'Remind me again' and 'OK' buttons!")

if __name__ == '__main__':
    test()
