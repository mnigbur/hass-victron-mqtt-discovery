#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2025 jorgen <jorgen@jorgen-laptop>
#
# Distributed under terms of the MIT license.

import paho.mqtt.client as mqtt
import json
import re

from .modbus_registers import ModbusRegisters
from .hass_gxdevice import HomeAssistantGXDevice
from .topic_components import TopicComponents
from .sensor_documentation import SensorDocumentation

class HassVictronMqttDiscovery:

    def __init__(self,
        mqtt_host='127.0.0.1',
        mqtt_port=1883,
        mqtt_prefix="",
        registers=None,
        registers_path=None,
        sensor_documentation=None,
        sensor_documentation_path=None):

        self.mqtt = None
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_prefix = mqtt_prefix

        self.devices = {}

        self.registers = self.init_registers(registers, registers_path)
        self.sensor_documentation = self.init_sensor_documentation(sensor_documentation, sensor_documentation_path)

    def start(self):
        self.setup_mqtt()

        self.mqtt.connect(self.mqtt_host, self.mqtt_port, 60)
        self.mqtt.loop_forever()

    def setup_mqtt(self):
        def on_connect(client, userdata, flags, reason_code, properties):
            self.on_connect()

        def on_message(client, userdata, msg):
            self.on_message(msg)

        self.mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt.on_connect = on_connect
        self.mqtt.on_message = on_message

    def init_registers(self, registers, registers_path):
        if registers is not None:
            return registers

        if registers_path is not None:
            return ModbusRegisters(registers_path)

        raise 'Must supply either registers or registers_path'

    def init_sensor_documentation(self, sensor_documentation, sensor_documentation_path):
        if sensor_documentation is not None:
            return sensor_documentation

        if sensor_documentation_path is not None:
            return SensorDocumentation(sensor_documentation_path)

        raise 'Must supply either sensor_documentation or sensor_documentation_path'

    def on_connect(self):
        self.mqtt.subscribe(self.mqtt_prefix + '#')

    def on_device_discovery(self, msg):
        payload = json.loads(msg.payload)
        serial = payload['value']

        if serial not in self.devices:
            print('Found device with serial: %s' % serial)
            self.devices[serial] = HomeAssistantGXDevice(self.mqtt, serial, self.registers, self.sensor_documentation)
            self.devices[serial].subscribe()

    def on_message(self, msg):
        if re.search(r'system\/\d+\/Serial$', msg.topic) is not None:
            self.on_device_discovery(msg)

        c = TopicComponents.from_topic(msg.topic)

        if c.serial in self.devices:
            self.devices[c.serial].on_mqtt_message(msg)
