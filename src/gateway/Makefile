build-image:
	docker build -t capaths/games-gateway:$(TAG) .;

docker-tag:
	docker tag capaths/games-gateway:$(FROM_TAG) \
	capaths/games-gateway:$(TAG)

push-image:
	docker push capaths/games-gateway:$(TAG)
