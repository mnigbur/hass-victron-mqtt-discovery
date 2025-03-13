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

serials = []

registerMap = {}

with open('./assets/registers.json', 'r') as fp:
    registers = json.load(fp)

for register in registers:
    service = register['service']
    topic = register['topic']

    if service is None or topic is None:
        continue

    service = service.lower()
    topic = topic.lower()

    if not service in registerMap:
        registerMap[service] = {}

    topicMap = registerMap[service]
    if not topic in topicMap:
        topicMap[topic] = register

state_classes = {}

page = pq(filename='./assets/sensor-documentation.html')
state_table = pq(page('#available-device-classes').next_all('table')[0])
for row in state_table('tbody tr').items():
    clazz, units, description = [ pq(c).text() for c in row('td') ]
    clazz = clazz.split('.')[-1].lower()
    units = [ u.strip() for u in units.split(',') ]

    for u in units:
        if not u in state_classes:
            state_classes[u] = clazz

def on_connect(client, userdata, flags, reason_code, properties):
    client.subscribe("victron/#")

def on_message(client, userdata, msg):
    if re.search(r'system\/\d+\/Serial$', msg.topic) is not None:
        payload = json.loads(msg.payload)
        serial = payload['value']

        print('Serial is %s' % serial)
        client.subscribe("victron/N/%s/+/+/ProductId" % serial)
        client.publish('victron/R/%s/keepalive' % serial, '')
        return


    m = re.search(r'N/([^/]+)/([^/]+)/(\d+)(/.*)$', msg.topic)
    if m is not None:
        serial = m.group(1)
        service = m.group(2)
        instance = m.group(3)
        dbusTopic = m.group(4)

        payload = json.loads(msg.payload)
        value = payload['value']

        device_id = "%s_%s_%s" % (serial, service, instance)
        topic = dbusTopic[1:].replace('/', '_')

        if not service in registerMap:
            #  print('Could not find service %s in registerset for %s' % (service, dbusTopic))
            return

        serviceRegisters = registerMap[service]
        searchTopic = dbusTopic.lower()
        if not searchTopic in serviceRegisters: searchTopic = re.sub(r'/power$', '/p', searchTopic)
        if not searchTopic in serviceRegisters: searchTopic = re.sub(r'/current$', '/i', searchTopic)
        if not searchTopic in serviceRegisters: searchTopic = re.sub(r'/voltage$', '/v', searchTopic)
        if not searchTopic in serviceRegisters: searchTopic = re.sub(r'/frequency$', '/f', searchTopic)

        if not searchTopic in serviceRegisters:
            #  print('Could not find topic %s in registerset for %s' % (dbusTopic, service))
            return
        register = serviceRegisters[searchTopic]

        options = None
        device_class = None

        unit = register['unit']
        if unit == 'count': unit = None

        if unit is not None and re.match(r'((\d+)=[^;]+;\s*)*((\d+)=[^;]+)', unit):
            device_class = 'enum'
            matches = re.findall(r'(\d+)=([^;]+)', unit)
            maxIndex = max([ int(v[0]) for v in matches ]) + 1
            options = [None] * maxIndex
            unit = None
            for match in matches:
                options[int(match[0])] = match[1]

        if unit is not None:
            unit = re.sub(r'^(A|V) (AC|DC)$', '\\1', unit)
            unit = unit.replace('Degrees celsius', '°C')
            unit = unit.replace('Degrees fahrenheit', '°F')
            unit = unit.replace('seconds', 's')
            unit = unit.split(' or ')[-1].strip()
            unit = re.sub(r'^watts?$', 'W', unit, flags=re.I)

        if unit in state_classes and state_classes[unit] is not None:
            device_class = state_classes[unit]

        state_class = None
        if unit in ['A', 'V']: state_class = 'measurement'
        if unit in ['kWh', 'Wh']: state_class = 'total'

        value_template = 'value_json.value'
        if device_class == 'enum':
            value_template = json.dumps(options) + '[value_json.value]'

        classInfo = {}
        if device_class is not None: classInfo['device_class'] = device_class
        if state_class is not None: classInfo['state_class'] = state_class
        if options is not None: classInfo['options'] = list(filter(None, options))

        device_type = 'sensor'
        if register['writable']:
            if re.match(r'int(32|16)', register['type']): device_type = 'number'
            if re.match(r'string', register['type']): device_type = 'text'
            if device_type == 'number' and options is not None: device_type = 'select'

            if device_type == 'number':
                classInfo['mode'] = 'box'
                classInfo['max'] = 999999
                classInfo['min'] = -999999

                if register.get('range', None) is not None:
                    classInfo['max'] = max(register['range'])
                    classInfo['min'] = min(register['range'])

                if 'max' in payload: classInfo['max'] = payload['max']
                if 'min' in payload: classInfo['min'] = payload['min']

            if device_type != 'sensor':
                classInfo['command_topic'] = re.sub(r'victron/N/', 'victron/W/', msg.topic)
                classInfo['command_template'] = '{{ { "value": value } | tojson }}'

        if isinstance(value, float):
            classInfo['suggested_display_precision'] = max([ len(str(register['scalefactor'])) - 1, 0 ]);

        name = re.sub(r'System;\s*', '', register['name'])
        name = name[0].upper() + name[1:]

        client.publish(
            'homeassistant/%s/%s/%s/config' % (device_type, device_id, topic),
            json.dumps({
                **classInfo,
                'name': name,
                'unique_id': '%s:%s' % (device_id, topic),
                'state_topic': msg.topic,
                'value_template': '{{ ' + value_template + ' }}',
                'unit_of_measurement': unit,
                'device': {
                    'name': 'Victron %s %s #%s' % (serial, service, instance),
                    'manufacturer': 'Victron Energy',
                    'serial_number': serial,
                    'identifiers': [ device_id ]
                },
                'enabled_by_default': value is not None,
            })
        )
    else:
        print(msg.topic + " " + str(msg.payload))

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect('192.168.5.3', 1883, 60)
mqttc.loop_forever()
