.PHONY: test dev docker-build docker-compose-up docker-compose-down

VERSION := 0.1.0
IMAGE_NAME := kimo.ai-docker:$(VERSION)

test:
	@docker run -itd --rm \
		--name mongodb \
		-p 27017:27017 \
		-v $(shell pwd)/data:/data/db \
		mongo:6.0
	@env $(shell cat .env) poetry run pytest -s -vv
	@docker stop mongodb

dev:
	@docker run -itd --rm \
		--name mongodb \
        -e MONGO_INITDB_ROOT_USERNAME=user \
        -e MONGO_INITDB_ROOT_PASSWORD=password \
        -e MONGO_INITDB_DATABASE=db_name \
		-p 27017:27017 \
		-v $(shell pwd)/data:/data/db \
		mongo:6.0
	@env $(shell cat .env) poetry run gunicorn -k uvicorn.workers.UvicornWorker --reload --bind 0.0.0.0:8888 -w 4 app.main:app

docker-build:
	@docker build -t $(IMAGE_NAME) .

docker-compose-up:
	@docker-compose up -d --build --remove-orphans --force-recreate

docker-compose-down:
	@docker-compose down -v --remove-orphans --rmi all
	@docker-compose rm -f -v 

docker-compose-update:
	@docker-compose down -v --remove-orphans --rmi all
	@docker-compose rm -f -v 
	@docker-compose up -d --build --remove-orphans --force-recreate
