#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2025 jorgen <jorgen@jorgen-laptop>
#
# Distributed under terms of the MIT license.

import paho.mqtt.client as mqtt
import json
import re

from modbus_registers import ModbusRegisters
from hass_gxdevice import HomeAssistantGXDevice
from topic_components import TopicComponents

class HassVictronMqttDiscovery:

    def __init__(self, mqtt_host=, mqtt_port=1883, mqtt_prefix="", registers=None, registers_path=None):
        self.mqtt = None
        self.registers = registers
        self.mqtt_host
        self.mqtt_port
        self.mqtt_prefix = mqtt_prefix

        self.devices = []

        if self.registers is None and registers_path is not None:
            self.registers = ModbusRegisters(registers_path)

        if self.registers is None:
            raise 'Must supply either registers or registers_path'

    def start():
        if self.mqtt is None:
            self.setup_mqtt()

        if self.mqtt.is_connected():
            raise 'MQTT client already connected'

        self.mqtt.connect(self.mqtt_host, self.mqtt_port, 60)
        self.mqtt.loop_start()


    def setup_mqtt(self):
        def on_connect(client, userdata, flags, reason_code, properties):
            self.on_connect()

        def on_message(client, userdata, msg):
            self.on_message(msg)

        self.mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt.on_connect = on_connect
        self.mqtt.on_message = on_message

    def on_connect():
        self.mqtt.subscribe(self.mqtt_prefix + '#')

    def on_device_discovery(msg):
        payload = json.loads(msg.payload)
        serial = payload['value']

        if serial not in self.devices:
            print('Found device with serial: %s' % serial)
            self.devices[serial] = HomeAssistantGXDevice(mqttc, serial, registers)
            self.devices[serial].subscribe()

    def on_message(msg):
        if re.search(r'system\/\d+\/Serial$', msg.topic) is not None:
            on_device_discovery(msg)

        c = TopicComponents.from_topic(msg.topic)

        if c.serial in self.devices:
            self.devices[c.serial].on_mqtt_message(msg)
