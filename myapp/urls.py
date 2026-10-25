from django.urls import path
from myapp import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('login/', views.logins, name='login'),
    path('logins/', views.logins, name='logins'),
    path('login_post/', views.login_post, name='login_post'),
    path('change_password_post/', views.change_password_post, name='change_password_post'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('user_registartion/', views.user_registartion, name='user_registartion'),
    path('logout/', views.user_logout, name='logout'),
    path('adminhome/', views.adminhome, name='adminhome'),
    
    # ASHA Worker URLs
    path('manage_asha/', views.manage_asha, name='manage_asha'),
    path('add_asha/', views.add_asha, name='add_asha'),
    path('edit_asha/<int:id>/', views.edit_asha, name='edit_asha'),
    path('delete_asha/<int:id>/', views.delete_asha, name='delete_asha'),
    
    # Anganwadi Teacher URLs
    path('manage_anganwadi/', views.manage_anganwadi, name='manage_anganwadi'),
    path('add_anganwadi/', views.add_anganwadi, name='add_anganwadi'),
    path('edit_anganwadi/<int:id>/', views.edit_anganwadi, name='edit_anganwadi'),
    path('delete_anganwadi/<int:id>/', views.delete_anganwadi, name='delete_anganwadi'),
    
    # Vaccination URLs
    path('add_vaccination/', views.add_vaccination, name='add_vaccination'),
    path('schedule_vaccination/', views.schedule_vaccination, name='schedule_vaccination'),
    path('vaccination_records/', views.vaccination_records, name='vaccination_records'),
    
    # Mother Verification & Clinical Records (ASHA Worker)
    path('verify_mother/', views.verify_mother, name='verify_mother'),
    path('verify_mother_action/<int:id>/<str:action>/', views.verify_mother_action, name='verify_mother_action'),
    path('delete_mother/<int:id>/', views.delete_mother, name='delete_mother'),
    path('manage_pregnancy/', views.manage_pregnancy, name='manage_pregnancy'),
    path('manage_pregenecy_record/', views.manage_pregnancy, name='manage_pregenecy_record'),
    path('view_pregnancy_records/', views.manage_pregnancy, name='view_pregnancy_records'),
    path('register_newborn/', views.register_newborn, name='register_newborn'),
    path('child_growth_record/', views.child_growth_record_view, name='child_growth_record'),
    path('child_growth/', views.child_growth_record_view, name='child_growth'),
    path('view_child_growth/', views.child_growth_record_view, name='view_child_growth'),
    
    # Anganwadi Teacher Portal
    path('teacher_home/', views.teacher_home, name='teacher_home'),
    path('manage_kit/', views.manage_kit, name='manage_kit'),
    path('add_nutrition_kit/', views.add_nutrition_kit, name='add_nutrition_kit'),
    path('kit_distribution/', views.kit_distribution, name='kit_distribution'),
    path('kit_history/', views.kit_history, name='kit_history'),
    path('update_kit_status/<int:kit_id>/', views.update_kit_status, name='update_kit_status'),
    path('reschedule_kit/', views.reschedule_kit, name='reschedule_kit'),
    path('teacher_beneficiaries/', views.teacher_beneficiaries, name='teacher_beneficiaries'),
    path('send_kit_reminder/', views.send_kit_reminder, name='send_kit_reminder'),
    path('teacher_profile/', views.teacher_profile_view, name='teacher_profile'),
    
    # User / Role Homes & Mother Portal
    path('ashaworker_home/', views.ashaworker_home, name='ashaworker_home'),
    path('ashaworker_profile/', views.ashaworker_profile_view, name='ashaworker_profile'),
    path('userhome/', views.userhome, name='userhome'),
    path('user_profile/', views.user_profile_view, name='user_profile'),
    path('view_profile/', views.user_profile_view, name='view_profile'),
    path('edit_user_profile/', views.edit_user_profile, name='edit_user_profile'),
    path('user_pregnancy_record/', views.user_pregnancy_record, name='user_pregnancy_record'),
    path('view_pregnency_record/', views.user_pregnancy_record, name='view_pregnency_record'),
    path('view_pregnancy_record/', views.user_pregnancy_record, name='view_pregnancy_record'),
    path('view_record/', views.user_pregnancy_record, name='view_record'),
    path('view_records/', views.user_pregnancy_record, name='view_records'),
    path('user_child_profile/', views.user_child_profile, name='user_child_profile'),
    path('user_child_growth/', views.user_child_growth, name='user_child_growth'),
    path('view_child_growth_user/', views.user_child_growth, name='view_child_growth_user'),
    path('user_vaccination_schedule/', views.user_vaccination_schedule, name='user_vaccination_schedule'),
    path('view_vaccination_schedule/', views.user_vaccination_schedule, name='view_vaccination_schedule'),
    path('user_kit_history/', views.user_kit_history, name='user_kit_history'),
    path('view_kit_history/', views.user_kit_history, name='view_kit_history'),
    path('user_notifications/', views.user_notifications, name='user_notifications'),
    path('notification/', views.user_notifications, name='notification'),
    path('mark_notifications_seen/', views.mark_notifications_seen, name='mark_notifications_seen'),
    
    # Admin Reports & Analytics
    path('report/', views.admin_report, name='admin_report'),
    path('export_report_pdf/', views.export_report_pdf, name='export_report_pdf'),
    path('export_report_csv/', views.export_report_csv, name='export_report_csv'),
    path('export_report_text/', views.export_report_text, name='export_report_text'),
    path('seed_demo_data/', views.seed_demo_data_view, name='seed_demo_data'),
]

