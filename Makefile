IMAGE_NAME=spartan
COMPOSE_SERVICE=web
USER=`id -u`:`id -g`

image:
	docker build -t $(IMAGE_NAME) .

test:
	docker-compose run -u $(USER) $(COMPOSE_SERVICE) python manage.py test

debugserver:
	docker-compose run -u $(USER) $(COMPOSE_SERVICE)
