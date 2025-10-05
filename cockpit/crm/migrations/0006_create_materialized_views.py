from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [('crm', '0005_entity_entity_display_name_gin')]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE MATERIALIZED VIEW IF NOT EXISTS entity_current_snapshot AS
            SELECT e.entity_uid,
                   e.display_name,
                   e.entity_type_id,
                   e.valid_from,
                   e.valid_to,
                   e.updated_at
            FROM crm_entity e
            WHERE e.is_current = TRUE;
            """,
            reverse_sql='DROP MATERIALIZED VIEW IF EXISTS entity_current_snapshot;'
        )
    ]