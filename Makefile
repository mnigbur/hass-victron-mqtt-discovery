#
# Makefile
# jorgen, 2025-04-24 23:18
#

ROOT_DIR?=$(shell dirname $(firstword $(MAKEFILE_LIST)))
IMAGE_NAME?="evens-solutions/victron-hass-mqtt-autodiscovery"
VERSION?=$(shell git tag | sort -r -V | head -n1 | sed 's/^v//')

build: build-docker build-hassio-addon
	echo "Build complete"

build-hassio-addon:
	docker build \
		--pull \
		--build-arg BUILD_FROM=alpine \
		--build-arg BUILD_VERSION=$(VERSION) \
		-t $(IMAGE_NAME):latest-hass-addon \
		$(ROOT_DIR)/addon

build-docker:
	docker build \
		--pull \
		--file $(ROOT_DIR)/docker/Dockerfile \
		-t $(IMAGE_NAME) \
		$(ROOT_DIR)

debug: build
	docker run \
		-ti --rm \
		--entrypoint /bin/sh \
		$(IMAGE_NAME)

start: build
	docker run \
		-ti --rm \
		-e MQTT_HOST="127.0.0.1" \
		$(IMAGE_NAME)

# vim:ft=make
#
