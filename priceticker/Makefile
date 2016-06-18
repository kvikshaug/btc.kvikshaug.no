NAME = btc.kvikshaug.no-priceticker
IMAGE = kvikshaug/${NAME}
IMAGE_GCR = eu.gcr.io/monkey-island-1227/${NAME}

default: build

.PHONY: build
build:
	docker-compose build app
	docker tag ${IMAGE} ${IMAGE_GCR}

.PHONY: push
push:
	gcloud docker push ${IMAGE_GCR}
