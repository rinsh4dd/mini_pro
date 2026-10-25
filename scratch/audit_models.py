import os
import sys
import django

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maatricaree.settings')
django.setup()

from django.apps import apps
from myapp import models as myapp_models

app_models = apps.get_app_config('myapp').get_models()

print(f"{'MODEL':<25} | {'FIELD NAME':<25} | {'FIELD TYPE':<25} | {'NULL':<6} | {'BLANK':<6} | {'DEFAULT'}")
print("-" * 105)

for model in app_models:
    for field in model._meta.get_fields():
        if field.is_relation and field.auto_created:
            continue
        rel = f" -> {field.related_model.__name__}" if field.is_relation else ""
        default = str(field.default) if field.default != django.db.models.fields.NOT_PROVIDED else ""
        print(f"{model.__name__:<25} | {field.name:<25} | {field.get_internal_type() + rel:<25} | {str(field.null):<6} | {str(field.blank):<6} | {default}")
