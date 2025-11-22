.PHONY: help build up down restart logs migrate test clean

help:
	@echo "TrendMaster AI - Development Commands"
	@echo "======================================"
	@echo "make build       - Build Docker containers"
	@echo "make up          - Start all services"
	@echo "make down        - Stop all services"
	@echo "make restart     - Restart all services"
	@echo "make logs        - View logs"
	@echo "make migrate     - Run Django migrations"
	@echo "make createsuperuser - Create Django superuser"
	@echo "make test        - Run tests"
	@echo "make clean       - Clean up containers and volumes"
	@echo "make scrape      - Run trend scrapers manually"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started. Django: http://localhost:8000 | Frontend: http://localhost:3000"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

migrate:
	docker-compose exec django python manage.py migrate

createsuperuser:
	docker-compose exec django python manage.py createsuperuser

test:
	docker-compose exec django python manage.py test
	docker-compose exec nextjs npm test

clean:
	docker-compose down -v
	docker system prune -f

scrape:
	docker-compose exec django python manage.py shell -c "from apps.trends.tasks import scrape_all_sources; scrape_all_sources.delay()"

rebuild-index:
	docker-compose exec django python manage.py shell -c "from apps.trends.vectorstore import get_vector_store; get_vector_store().rebuild_index()"
