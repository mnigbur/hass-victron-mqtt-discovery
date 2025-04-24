#
# Makefile
# jorgen, 2025-04-24 23:18
#

ROOT_DIR?=$(shell dirname $(firstword $(MAKEFILE_LIST)))
IMAGE_NAME?="evens-solutions/victron-hass-mqtt-autodiscovery"

build:
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
