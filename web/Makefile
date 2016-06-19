NAME = btc.kvikshaug.no-web
IMAGE = kvikshaug/${NAME}
IMAGE_GCR = eu.gcr.io/monkey-island-1227/${NAME}

default: build
qa: test

.PHONY: build
build:
	# Compile css before creating the image
	docker-compose run --rm builder sass --scss --update scss:css
	docker-compose build web
	docker tag ${IMAGE} ${IMAGE_GCR}

.PHONY: push
push:
	gcloud docker push ${IMAGE_GCR}

.PHONY: test
test:
	docker-compose run --rm web python app/tests.py
