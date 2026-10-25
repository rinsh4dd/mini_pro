import os
import shutil
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.contrib.sessions.models import Session
from django.conf import settings
from myapp.models import (
    asha_worker, anganwadi_teacher, user_table, pregnancy_record,
    child, child_growth_record, vaccination, nutrition_kit,
    kit_notification, notification, vaccine_schedule, report
)


class Command(BaseCommand):
    help = "Resets all database data while preserving the admin account and credentials."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting database reset..."))

        # 1. Delete dependent models in order to respect foreign key constraints
        report.objects.all().delete()
        kit_notification.objects.all().delete()
        nutrition_kit.objects.all().delete()
        vaccine_schedule.objects.all().delete()
        notification.objects.all().delete()
        vaccination.objects.all().delete()
        child_growth_record.objects.all().delete()
        child.objects.all().delete()
        pregnancy_record.objects.all().delete()
        user_table.objects.all().delete()
        anganwadi_teacher.objects.all().delete()
        asha_worker.objects.all().delete()

        self.stdout.write("Deleted all application model records.")

        # 2. Preserve admin / superuser accounts
        admin_users = User.objects.filter(is_superuser=True) | User.objects.filter(username='admin')
        admin_ids = list(admin_users.values_list('id', flat=True))

        deleted_users_count, _ = User.objects.exclude(id__in=admin_ids).delete()
        self.stdout.write(f"Deleted {deleted_users_count} non-admin user accounts.")

        # Ensure admin user has required admin group
        admin_group, _ = Group.objects.get_or_create(name='admin')
        for admin_u in User.objects.filter(id__in=admin_ids):
            admin_u.groups.add(admin_group)

        # 3. Ensure essential user groups exist
        for g_name in ['admin', 'ashaworker', 'angteacher', 'user']:
            Group.objects.get_or_create(name=g_name)

        # 4. Clear all user sessions
        Session.objects.all().delete()
        self.stdout.write("Cleared all active user sessions.")

        # 5. Clean media upload directory
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if media_root and os.path.exists(media_root):
            for filename in os.listdir(media_root):
                file_path = os.path.join(media_root, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Could not delete {file_path}: {e}"))
            self.stdout.write("Cleaned media files.")

        self.stdout.write(self.style.SUCCESS("[SUCCESS] Database reset complete! Admin account preserved."))
