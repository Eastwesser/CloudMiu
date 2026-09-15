# MiuMiu 2.0 — Docker helpers
# Windows: Git Bash / WSL / Chocolatey `make`, or use make.bat (CMD/PowerShell)

COMPOSE ?= docker compose
SERVICE ?= miumiu
HUB_IMAGE ?= eastwesser/home_arm_miumiu2:latest
ARM_PLATFORM ?= linux/arm/v7

.PHONY: help build up down restart logs ps shell test pull clean arm-builder arm-push

help:
	@echo MiuMiu 2.0 make targets:
	@echo   make build       - local (host arch) image
	@echo   make up          - start bot (detached)
	@echo   make down        - stop and remove
	@echo   make restart     - restart container
	@echo   make logs        - follow logs
	@echo   make ps          - status
	@echo   make shell       - shell inside container
	@echo   make test        - pytest in a one-off container
	@echo   make clean       - down + remove image
	@echo   make arm-builder - create/use buildx builder for Pi 3B+
	@echo   make arm-push    - build linux/arm/v7 and push $(HUB_IMAGE)

build:
	$(COMPOSE) build

up: build
	$(COMPOSE) up -d
	@echo Bot started. Use: make logs

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) restart $(SERVICE)

logs:
	$(COMPOSE) logs -f $(SERVICE)

ps:
	$(COMPOSE) ps

shell:
	$(COMPOSE) exec $(SERVICE) /bin/bash

test:
	$(COMPOSE) run --rm --no-deps $(SERVICE) pip install -q pytest pytest-asyncio && \
	$(COMPOSE) run --rm --no-deps $(SERVICE) pytest -q

pull:
	$(COMPOSE) pull || true

clean: down
	-docker rmi miumiu-2.0:latest

arm-builder:
	docker buildx create --name miumiuarm --use --bootstrap 2>/dev/null || docker buildx use miumiuarm
	docker buildx inspect --bootstrap

# Cross-build for Raspberry Pi 3B+ and upload to Docker Hub (requires docker login)
arm-push: arm-builder
	docker buildx build --platform $(ARM_PLATFORM) -t $(HUB_IMAGE) --push .
