.EXPORT_ALL_VARIABLES:
COMPOSE_FILE ?= ./docker-compose.yml
SERVICE_NAME ?= fastapi

-include .$(PWD)/.env

.PHONY: help
help: # Display available commands
	@echo "\n\033[0;33mAvailable make commands:\033[0m\n"
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: start
start: build up # Build and spin up the application in one command

.PHONY: restart
restart: down up # Restart the application

.PHONY: up
up:  # Spin up the application
	docker compose -f $(COMPOSE_FILE) up -d
	docker compose ps

.PHONY: down
down: # Shut down the application
	docker compose down

.PHONY: migrate
migrate: # Use migrations
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) alembic upgrade head

.PHONY: load-data
load-data: # Load data in database
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) python -m src.db.data.push_test_data

.PHONY: logs
logs: # Follow logs of all running containers
	docker compose logs --follow

.PHONY: connect
connect: # Connect to the running container
	docker compose exec -it $(SERVICE_NAME) /bin/bash

.PHONY: run-linters
run-linters: run-flake8 run-isort run-mypy # Run black & ruff linters

.PHONY: run-flake8
run-flake8: # Run black linter
	docker compose exec $(SERVICE_NAME) flake8 .

.PHONY: isort
run-isort: # Run ruff linter
	docker compose exec $(SERVICE_NAME) isort .

.PHONY: mypy
run-mypy: # Run ruff linter
	docker compose exec $(SERVICE_NAME) mypy .

.PHONY: tests
tests: # Run tests
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) pytest tests/.

.PHONY: show-cov-report
show-cov-report: # Displays coverage report from the last pytest run
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) coverage run -m pytest
	docker compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) coverage report --show-missing

.PHONY: build
build: # Build docker image of the application
	docker build --tag=$(SERVICE_NAME) --file=Dockerfile .