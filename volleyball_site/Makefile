SHELL := /bin/bash

.PHONY: build up down logs migrate collectstatic createsuperuser shell debug

build:
	docker-compose -f docker-compose.yml build

up:
	docker-compose -f docker-compose.yml up -d --remove-orphans

down:
	docker-compose -f docker-compose.yml down

logs:
	docker-compose -f docker-compose.yml logs -f web

migrate:
	docker-compose -f docker-compose.yml run --rm web python manage.py migrate

collectstatic:
	docker-compose -f docker-compose.yml run --rm web python manage.py collectstatic --noinput

createsuperuser:
	docker-compose -f docker-compose.yml run --rm web python manage.py createsuperuser

shell:
	docker-compose -f docker-compose.yml run --rm web python manage.py shell

debug:
	../scripts/debug.sh
