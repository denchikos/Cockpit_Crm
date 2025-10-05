# Test Task – Artemenko

## Quick Start
```bash
1. Clone the repository:

git clone https://github.com/denchikos/Cockpit_Crm.git

2. Build and run the project using Docker:

docker-compose build
docker-compose up

3. Access the API in your browser:

http://127.0.0.1:8000/api/v1/entities

---

Advanced Cockpit CRM (SCD2 Assignment)

Architecture Overview

Modular CRM core for Advanced Management Cockpit, implementing SCD Type 2 (Slowly Changing Dimensions) for entity versioning.

Key features:

Unified data model: Entity → EntityType → EntityDetail

Table-level versioning (valid_from, valid_to, is_current)

Idempotent data loading and updating via service layer

DRF API for interactive access

Audit log (AuditLog) to track changes


Database is the single source of truth, enforced via PostgreSQL constraints (GiST exclusion, unique indexes, pg_trgm).

---

Tech Stack

Component Version / Purpose

Python 3.11
Django 5.x
Django REST Framework 3.x
PostgreSQL 15 (btree_gist, pg_trgm)
Docker / docker-compose Deployment
pytest / pytest-django Testing & idempotency verification

---

Core Data Model

EntityType — entity type (PERSON, INSTITUTION)

Entity — fields: display_name, entity_type, valid_from, valid_to, is_current

EntityDetail — typed attributes, versioned like Entity

AuditLog — tracks who changed what and when


SCD2 versioning is inline (no separate history tables). Updates “close” the previous version (valid_to) and create a new one (is_current=True).

---

API Examples

Create entity

POST /api/v1/entities/
{
  "entity_uid": "b1f1a6b6-56b5-11ee-b962-0242ac120002",
  "entity_type": "PERSON",
  "display_name": "Alice",
  "details": [
    {"detail_code": "EMAIL", "value": {"value": "alice@example.com"}}
  ]
}

Get all current entities

GET /api/v1/entities/

Update entity (creates new version)

PATCH /api/v1/entities/<entity_uid>/
{
  "display_name": "Alice Brown"
}

Entity state as of a date

GET /api/v1/entities-asof?as_of=2025-10-01

Entity history

GET /api/v1/entities/<entity_uid>/history/

Diff between two dates

GET /api/v1/diff?from=2025-09-01&to=2025-09-30

---

Idempotency & SCD2 Logic

Implemented in services.py:

scd2_upsert_entity() — updates entities with hashdiff control

scd2_upsert_detail() — idempotent detail updates

automatic closure of previous versions

AuditLog records creation


Idempotency ensures that identical data does not create new versions.

---

Audit & Security

All changes recorded in AuditLog:

actor — who made the change

action — INSERT / UPDATE

entity_uid, detail_code

before / after values

timestamp

---

Tests

Run in Docker:

pytest -v

Tests cover:

SCD2 transitions

Idempotent loading

History, state-as-of, and diff

Negative scenarios (overlaps, uniqueness)

---

Batch Loading & View Refresh

refresh_materialized_views() — refresh materialized views

load_entities_from_file() — batch import (CSV/JSON, optional)

---

Design Overview

Modular CRM core extendable with other modules (Risks, Compliance, Sales Analytics)

Unified model (entity_uid, SCD2) ensures consistent interactions


Architecture:

Models → Services → API → AuditLog
(PostgreSQL as the single source of truth)
