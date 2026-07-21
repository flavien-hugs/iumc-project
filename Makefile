.DEFAULT_GOAL := help

COMPOSE := docker compose -f infra/docker-compose.yml
COMPOSE_PROD := $(COMPOSE) -f infra/docker-compose.prod.yml

.PHONY: help up down restart build logs ps clean \
	migrate migration seed backend-shell backend-lint \
	frontend-install frontend-dev-website frontend-dev-admin frontend-check frontend-build \
	prod-up prod-down prod-logs

help: ## Affiche cette aide
	@echo "IUMC — cibles disponibles :"
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_-]+:.*## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

## Stack Docker (dev)

up: ## Démarre toute la stack (build si nécessaire)
	$(COMPOSE) up -d --build

down: ## Arrête la stack (conserve les volumes de données)
	$(COMPOSE) down

restart: down up ## Redémarre toute la stack

build: ## Reconstruit les images sans démarrer les conteneurs
	$(COMPOSE) build

logs: ## Suit les logs de tous les services
	$(COMPOSE) logs -f

ps: ## Liste l'état des conteneurs
	$(COMPOSE) ps

clean: ## Arrête la stack et supprime les volumes (irréversible: données perdues)
	$(COMPOSE) down -v

## Base de données

migrate: ## Applique les migrations Alembic en attente
	$(COMPOSE) exec backend alembic upgrade head

migration: ## Génère une migration à partir des modèles (make migration name="...")
	$(COMPOSE) exec backend alembic revision --autogenerate -m "$(name)"

seed: ## Peuple la base (super admin, pôles, services, implantations) — idempotent
	$(COMPOSE) exec backend python -m app.seed

## Backend

backend-shell: ## Ouvre un shell dans le conteneur backend
	$(COMPOSE) exec backend bash

backend-lint: ## Lint du backend (installe les dépendances de dev si absentes)
	cd backend && .venv/bin/pip install -q -e ".[dev]" && .venv/bin/ruff check app

## Frontend

frontend-install: ## Installe les dépendances du monorepo frontend
	cd frontend && npm install

frontend-dev-website: ## Lance le site public en dev (hors Docker, rechargement à chaud)
	cd frontend && npm run dev:website

frontend-dev-admin: ## Lance le panel admin en dev (hors Docker, rechargement à chaud)
	cd frontend && npm run dev:admin

frontend-check: ## Vérifie les types Svelte/TypeScript des deux apps
	cd frontend && npm run check --workspace=@iumc/website && npm run check --workspace=@iumc/admin

frontend-build: ## Build de production des deux apps (hors Docker)
	cd frontend && npm run build

## Production

prod-up: ## Démarre la stack en configuration production (+ Nginx/TLS)
	$(COMPOSE_PROD) up -d --build

prod-down: ## Arrête la stack production
	$(COMPOSE_PROD) down

prod-logs: ## Suit les logs de la stack production
	$(COMPOSE_PROD) logs -f
