IMAGE_NAME=spartan
COMPOSE_SERVICE=web
USER=`id -u`:`id -g`

image:
	docker build -t $(IMAGE_NAME) .

test:
	docker run -e DEBUG=1 -u $(USER) -v `pwd`:/code $(IMAGE_NAME) python manage.py test

debugserver:
	docker run -e DEBUG=1 -p 8000:8000 -u $(USER) -v `pwd`:/code $(IMAGE_NAME)
