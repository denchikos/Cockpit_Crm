from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Refresh materialized views (snapshots of current entities)'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.exucate('REFRESH MATERIALIZED VIEW CONCURRENTLY entity_current_snapshot;')
        self.stdout.write(self.style.SUCCESS('Materialized views refreshed.'))