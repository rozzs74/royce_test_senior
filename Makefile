blue=\033[0;34m
normal=\033[m

.PHONY: help build run start stop test clean deploy

help:
	@echo "Available commands:"
	@echo "  build    - Build Docker image"
	@echo "  run      - Run with Docker Compose"
	@echo "  start    - Activate venv, export environment variables and run FastAPI locally in background"
	@echo "  stop     - Stop the FastAPI application"
	@echo "  test     - Run tests"
	@echo "  clean    - Clean Docker containers and images"
	@echo "  deploy   - Deploy to Google Cloud Run"

build:
	docker-compose build

run:
	docker-compose up --build

start:
	@echo "🎳 Starting Bowling Shoes Rental Service..."
	@echo "🛑 Stopping any existing uvicorn processes..."
	@pkill -f uvicorn || true
	rm -rf venv
	@echo "🚀 Activating virtual environment and starting application locally..."
	@if [ ! -d "venv" ]; then python3 -m venv venv; fi
	@echo "📦 Installing dependencies..."
	@venv/bin/pip install -r requirements.txt > /dev/null 2>&1
	@echo "🌍 Exporting environment variables and starting uvicorn..."
	@export $$(cat environments/.env.dev | xargs) && PYTHONPATH=. venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
	@sleep 2
	@echo "✅ Application started in background!"
	@echo "🌐 Application URLs:"
	@echo "   - API: http://localhost:8000"
	@echo "   - API Docs: http://localhost:8000/docs"
	@echo "   - Health Check: http://localhost:8000/health"

stop:
	@echo "🛑 Stopping FastAPI application..."
	@pkill -f uvicorn || true
	@echo "✅ Application stopped!"

test:
	docker-compose run --rm app python -m pytest

clean:
	docker-compose down --volumes --rmi all
	@pkill -f uvicorn || true

deploy:
	gcloud run deploy llm-discount-service --source . --platform managed --region us-central1 

prune:
	docker builder prune -f