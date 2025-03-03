#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2025 jorgen <jorgen@jorgen-laptop>
#
# Distributed under terms of the MIT license.

import paho.mqtt.client as mqtt
import json
import time
import re

serials = []
created = False

def on_connect(client, userdata, flags, reason_code, properties):
    client.subscribe("victron/#")

def on_message(client, userdata, msg):
    global created

    if created:
        return

    if re.search(r'system\/\d+\/Serial$', msg.topic) is not None:
        payload = json.loads(msg.payload)
        serial = payload['value']

        print('Serial is %s' % serial)
        client.subscribe("victron/N/%s/+/+/ProductId" % serial)
        client.publish('victron/R/%s/keepalive' % serial, '')
        return

    m = re.search(r'N/([^/]+)/([^/]+)/(\d+)/(.*)$', msg.topic)
    if m is not None:
        serial = m.group(1)
        service = m.group(2)
        instance = m.group(3)
        dbusTopic = m.group(4)

        if service != 'battery':
            return

        device_id = "%s_%s_%s" % (serial, service, instance)
        topic = dbusTopic.replace('/', '_')

        print('homeassistant/sensor/%s/%s/config' % (device_id, topic))

        client.publish(
            'homeassistant/sensor/%s/%s/config' % (device_id, topic),
            json.dumps({
                'name': 'Topic Description',
                'state_topic': msg.topic,
                'platform': 'sensor',
                'device': {
                    'name': 'Victron %s %s' % (serial, service),
                    'manufacturer': 'Victron Energy',
                    'serial_number': serial,
                    'identifiers': [ serial ]
                }
            })
        )

        print(json.dumps({
            'serial': serial,
            'service': service,
            'instance': instance,
            'topic': dbusTopic
        }))

        created = True
    else:
        print(msg.topic + " " + str(msg.payload))

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect('192.168.5.3', 1883, 60)
mqttc.loop_forever()
