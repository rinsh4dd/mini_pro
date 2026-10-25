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

def test_flow():
    mother = user_table.objects.get(name='Amina Rahmath')
    notification_seen.objects.filter(USER=mother).delete()

    print("=== Testing Mother Login & Popup Flow ===")

    # Step 1: Mother logs in for the first time
    c1 = Client()
    r_login = c1.post('/myapp/login_post/', {'username': 'ward1mother', 'password': 'Mother@123'})
    assert r_login.status_code == 302, f"Expected redirect, got {r_login.status_code}"
    
    r_home = c1.get(r_login.url)
    assert r_home.status_code == 200
    html1 = r_home.content.decode('utf-8')
    assert 'id="loginNotifModal"' in html1, "loginNotifModal should be rendered on first login"
    assert 'Remind me again' in html1, "'Remind me again' button should be present"
    assert 'btnConfirmOkPopup' in html1, "'OK' button should be present"
    print("1. First Login: Notification popup is shown with 'Remind me again' & 'OK' buttons. [PASSED]")

    # Step 2: Mother clicks 'Remind me again'
    r_remind = c1.post('/myapp/mark_notifications_seen/', {'action': 'remind_again'})
    assert r_remind.status_code == 200
    resp_data = r_remind.json()
    assert resp_data['status'] == 'success'
    assert resp_data['action'] == 'remind_again'
    assert notification_seen.objects.filter(USER=mother).count() == 0, "No notifications should be marked seen"
    print("2. 'Remind me again': Keeps notification unread in DB. [PASSED]")

    # Step 3: Mother logs in again next time -> Popup MUST show again!
    c2 = Client()
    r_login2 = c2.post('/myapp/login_post/', {'username': 'ward1mother', 'password': 'Mother@123'})
    r_home2 = c2.get(r_login2.url)
    html2 = r_home2.content.decode('utf-8')
    assert 'id="loginNotifModal"' in html2, "loginNotifModal should show up again on next login"
    print("3. Next Login: Popup opens again because 'Remind me again' was chosen. [PASSED]")

    # Step 4: Mother clicks 'OK'
    r_ok = c2.post('/myapp/mark_notifications_seen/', {'action': 'ok', 'all': '1'})
    assert r_ok.status_code == 200
    assert r_ok.json()['status'] == 'success'
    assert notification_seen.objects.filter(USER=mother).count() > 0, "Notification should be marked seen"
    print("4. 'OK' Clicked: Notification marked as acknowledged/seen in DB. [PASSED]")

    # Step 5: Mother logs in in a fresh session -> Popup should NOT show
    c3 = Client()
    r_login3 = c3.post('/myapp/login_post/', {'username': 'ward1mother', 'password': 'Mother@123'})
    r_home3 = c3.get(r_login3.url)
    html3 = r_home3.content.decode('utf-8')
    assert 'id="loginNotifModal"' not in html3, "loginNotifModal should NOT be rendered after being marked seen"
    print("5. Subsequent Login after OK: No popup shown. [PASSED]")

    # Reset notification_seen so the demo account is fresh for the user/guide demonstration!
    notification_seen.objects.filter(USER=mother).delete()
    print("=== Demo Reset: Notification is unread and ready for live user demo! ===")

if __name__ == '__main__':
    test_flow()
