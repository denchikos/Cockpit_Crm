import csv
import json
from django.core.management.base import BaseCommand, CommandError
from crm.services import scd2_upsert_entity
from crm.models import EntityType


class Command(BaseCommand):
    help = "Batch load entities from CSV or JSON file."

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to CSV or JSON file")

    def handle(self, *args, **options):
        file_path = options["file_path"]
        try:
            if file_path.endswith(".csv"):
                with open(file_path, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.process_row(row)
            elif file_path.endswith(".json"):
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                    for row in data:
                        self.process_row(row)
            else:
                raise CommandError("Supported formats: .csv or .json")

            self.stdout.write(self.style.SUCCESS("File loaded successfully."))
        except Exception as e:
            raise CommandError(f"Error loading file: {e}")

    def process_row(self, row):
        entity_type_code = row.get("entity_type", "PERSON")
        entity_type, _ = EntityType.objects.get_or_create(code=entity_type_code)

        details = []
        for key, value in row.items():
            if key not in ("entity_uid", "entity_type", "display_name"):
                details.append({"detail_code": key.upper(), "value": {"value": value}})

        scd2_upsert_entity(
            entity_uid=row["entity_uid"],
            entity_type=entity_type,
            display_name=row["display_name"],
            details=details,
            actor="batch_loader",
        )