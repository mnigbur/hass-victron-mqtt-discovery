#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2025 jorgen <jorgen@jorgen-laptop>
#
# Distributed under terms of the MIT license.

from pyquery import PyQuery as pq
import paho.mqtt.client as mqtt
import json
import time
import re

from modbus_registers import ModbusRegisters
from hass_gxdevice import HomeAssistantGXDevice
from topic_components import TopicComponents

registers = ModbusRegisters(source="./assets/modbus-registers.xlsx")

gx_devices = {}

def on_connect(client, userdata, flags, reason_code, properties):
    client.subscribe("victron/#")

def on_device_discovery(msg):
        payload = json.loads(msg.payload)
        serial = payload['value']

        if serial not in gx_devices:
            print('Serial is %s' % serial)
            gx_devices[serial] = HomeAssistantGXDevice(mqttc, serial, registers)
            gx_devices[serial].subscribe()

        return gx_devices[serial]

def on_message(client, userdata, msg):
    if re.search(r'system\/\d+\/Serial$', msg.topic) is not None:
        on_device_discovery(msg)

    c = TopicComponents.from_topic(msg.topic)

    if c.serial in gx_devices:
        gx_devices[c.serial].on_mqtt_message(msg)

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect('192.168.5.3', 1883, 60)
mqttc.loop_forever()
