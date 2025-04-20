#! /usr/bin/env python3

import asyncio

from hass_victron_mqtt_discovery import HassVictronMqttDiscovery

async def main():
    hass_discovery = HassVictronMqttDiscovery(
        mqtt_host = '192.168.5.3',
        mqtt_prefix = 'victron/',
        registers_path = './assets/modbus-registers.xlsx',
        sensor_documentation_path = './assets/sensor-documentation.html',
    )

    await hass_discovery.start()

asyncio.run(main())
