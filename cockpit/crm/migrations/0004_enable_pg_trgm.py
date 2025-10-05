from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0003_auditlog')
    ]

    operations = [
        migrations.RunSQL('CREATE EXTENSION IF NOT EXISTS pg_trgm;'),
    ]
