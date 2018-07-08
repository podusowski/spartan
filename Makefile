IMAGE_NAME=spartan
USER=`id -u`:`id -g`
DOCKER=docker run --rm -it -e DEBUG=1 -p 8000:8000 -u $(USER) -v `pwd`:/code $(IMAGE_NAME)

image:
	docker build -t $(IMAGE_NAME) .

test:
	$(DOCKER) python manage.py test

debugserver:
	$(DOCKER) python manage.py migrate
	$(DOCKER)

deploy:
	@test -n "$(IMAGE)" || ( echo "no IMAGE variable, try something like: make deploy IMAGE=johndoe/spartan"; exit 1 )
	docker stop spartan || true
	docker pull $(IMAGE)
	docker run -p 80:8000 --name spartan --restart always -d -u `id -u`:`id -g` -v /var/run/postgresql/:/var/run/postgresql $(IMAGE)
