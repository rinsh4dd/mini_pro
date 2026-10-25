import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maatricaree.settings')
django.setup()

from django.apps import apps

app_models = apps.get_app_config('myapp').get_models()

schema_data = []

for model in app_models:
    model_name = model.__name__
    fields = []
    for f in model._meta.get_fields():
        if f.is_relation and f.auto_created:
            continue
        field_info = {
            'name': f.name,
            'type': f.get_internal_type(),
            'is_relation': f.is_relation,
            'related_model': f.related_model.__name__ if f.is_relation and f.related_model else None,
            'null': f.null,
            'blank': f.blank,
            'default': str(f.default) if f.default != django.db.models.fields.NOT_PROVIDED else None,
            'max_length': getattr(f, 'max_length', None),
        }
        fields.append(field_info)
    schema_data.append({
        'model': model_name,
        'doc': model.__doc__,
        'fields': fields
    })

import json
with open('scratch/schema_dump.json', 'w', encoding='utf-8') as out:
    json.dump(schema_data, out, indent=2)

print(f"Dumped {len(schema_data)} models with total fields: {sum(len(m['fields']) for m in schema_data)}")
for m in schema_data:
    print(f"- {m['model']}: {len(m['fields'])} fields")
