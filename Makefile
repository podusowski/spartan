COMPOSE_SERVICE=web

image:
	docker build -t spartan .

test:
	docker-compose run $(COMPOSE_SERVICE) python manage.py test

debugserver:
	docker-compose run $(COMPOSE_SERVICE)
