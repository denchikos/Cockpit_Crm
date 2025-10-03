.PHONY: up down build migrate shell test logs createsuperuser

up:
docker-compose up -d

down:
docker-compose down

build:
docker-compose build

migrate:
docker-compose run --rm web python manage.py migrate

shell:
docker-compose run --rm web python manage.py shell

createsuperuser:
docker-compose run --rm web python manage.py createsuperuser

test:
docker-compose run --rm web pytest -v

logs:
docker-compose logs -f web