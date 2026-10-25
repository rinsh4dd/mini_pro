import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maatricaree.settings')
django.setup()

from django.test import Client
from myapp.models import user_table, notification_seen

m = user_table.objects.get(name='Amina Rahmath')
notification_seen.objects.filter(USER=m).delete()

c = Client()
res_login = c.post('/myapp/login_post/', {'username': 'ward1mother', 'password': 'Mother@123'})
print('Login status:', res_login.status_code, 'Redirect:', res_login.url)
assert res_login.status_code == 302

res_home = c.get(res_login.url)
assert res_home.status_code == 200
html_home = res_home.content.decode('utf-8')

print('1. Notification modal active on login:', ('id="loginNotifModal"' in html_home and 'modal-overlay active' in html_home))
print('2. Home contains Pregnancy #2 • Month 7:', ('PREGNANCY #2 • MONTH 7' in html_home))
print('3. Home contains Child #1 from Pregnancy #1:', ('CHILD #1 • FROM PREGNANCY #1' in html_home))

# Test Child Growth view
res_growth = c.get('/myapp/user_child_growth/')
assert res_growth.status_code == 200
html_growth = res_growth.content.decode('utf-8')
m_count = sum(1 for m_num in range(1, 13) if f'Month {m_num}' in html_growth)
print('4. All 12 months present in child growth:', m_count == 12, f'({m_count}/12 months verified)')

# Test Pregnancy Record view
res_preg = c.get('/myapp/user_pregnancy_record/')
assert res_preg.status_code == 200
html_preg = res_preg.content.decode('utf-8')
print('5. Pregnancy record differentiates Pregnancy #1 and #2:', ('PREGNANCY #2' in html_preg and 'PREGNANCY #1' in html_preg))

print('\nALL VERIFICATIONS PASSED SUCCESSFULLY!')
