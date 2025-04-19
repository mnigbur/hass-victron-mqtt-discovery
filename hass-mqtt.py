#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2025 jorgen <jorgen@jorgen-laptop>
#
# Distributed under terms of the MIT license.

from hass_victron_mqtt_discovery import HassVictronMqttDiscovery

hass_discovery = HassVictronMqttDiscovery(
    mqtt_host = '192.168.5.3',
    mqtt_prefix = 'victron/',
    registers_path = './assets/modbus-registers.xlsx',
    sensor_documentation_path = './assets/sensor-documentation.html',
)

hass_discovery.start()
