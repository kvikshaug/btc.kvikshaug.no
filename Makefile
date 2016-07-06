NAME_PRICETICKER = btc.kvikshaug.no-priceticker
IMAGE_PRICETICKER = kvikshaug/${NAME_PRICETICKER}
IMAGE_GCR_PRICETICKER = eu.gcr.io/monkey-island-1227/${NAME_PRICETICKER}

NAME_WEB = btc.kvikshaug.no-web
IMAGE_WEB = kvikshaug/${NAME_WEB}
IMAGE_GCR_WEB = eu.gcr.io/monkey-island-1227/${NAME_WEB}

default: qa build push
qa: test

.PHONY: build
build:
	docker-compose build priceticker
	docker tag ${IMAGE_PRICETICKER} ${IMAGE_GCR_PRICETICKER}

	docker-compose run --rm builder sass --scss --update scss:css
	docker-compose build web
	docker tag ${IMAGE_WEB} ${IMAGE_GCR_WEB}

.PHONY: push
push:
	gcloud docker push ${IMAGE_GCR_PRICETICKER}
	gcloud docker push ${IMAGE_GCR_WEB}

.PHONY: deploy
deploy:
	kubectl delete -f rc.yml
	kubectl create -f rc.yml

.PHONY: test
test:
	docker-compose run --rm web python app/tests.py
