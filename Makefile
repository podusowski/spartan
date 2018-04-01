IMAGE_NAME=spartan
COMPOSE_SERVICE=web
USER=`id -u`:`id -g`
DOCKER=docker run -e DEBUG=1 -p 8000:8000 -u $(USER) -v `pwd`:/code $(IMAGE_NAME)

image:
	docker build -t $(IMAGE_NAME) .

test:
	$(DOCKER) python manage.py test

debugserver:
	$(DOCKER) python manage.py migrate
	$(DOCKER)
