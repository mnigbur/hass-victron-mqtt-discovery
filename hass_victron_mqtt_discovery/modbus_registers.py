#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2025 jorgen <jorgen@jorgen-pc>
#
# Distributed under terms of the MIT license.
import re
import json
import hashlib

from openpyxl import Workbook
from openpyxl.reader.excel import load_workbook

def generate_file_hash(path):
    with open(path, 'rb', buffering=0) as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def topic_from_row(row):
    if row[6] == '':
        return None

    value_range = [ float(v.strip()) for v in (row[5] or '').split('to') if re.match(r'^[-+]?\d+(.\d+)?$', v.strip()) ]

    if len(value_range) < 2:
        value_range = None

    return {
        'service': row[0].split('.')[-1],
        'name': row[1],
        'type': row[3],
        'range': value_range,
        'scalefactor': row[4],
        'topic': row[6],
        'writable': row[7] == 'yes',
        'unit': row[8]
    }


class ModbusRegisters:

    def __init__(self, source=None):
        self.services = {}

        if source is not None:
            self.from_xlsx(source)

    def has_cache(self, cache_id):
        return False

    def load_cache(self, cache_id):
        with open('.cache/' + cache_id, 'r') as f:
            self.services = json.load(f)

    def lookup_mqtt_topic(self, topic):
        m = re.search(r'N/([^/]+)/([^/]+)/(\d+)(/.*)$', topic)
        if m is None:
            return None

        service = m.group(2).lower()
        dbusTopic = m.group(4)

        if not service in self.services:
            return None

        topicMap = self.services[service]
        searchTopic = dbusTopic.lower()
        if not searchTopic in topicMap: searchTopic = re.sub(r'/power$', '/p', searchTopic)
        if not searchTopic in topicMap: searchTopic = re.sub(r'/current$', '/i', searchTopic)
        if not searchTopic in topicMap: searchTopic = re.sub(r'/voltage$', '/v', searchTopic)
        if not searchTopic in topicMap: searchTopic = re.sub(r'/frequency$', '/f', searchTopic)

        if not searchTopic in topicMap:
            return None

        return topicMap[searchTopic]

    def update_cache(self, cache_id):
        with open('.cache/' + cache_id, 'w') as f:
            json.dump(self.services, f)

    def from_xlsx(self, file):
        cache_id = generate_file_hash(file)

        if self.has_cache(cache_id):
            return self.load_cache(cache_id)

        wb = load_workbook(file)
        ws = wb['Field list']

        for row in ws.iter_rows(min_row=3):
            row = [ cell.value for cell in row ]
            row = topic_from_row(row)

            if row is None:
                continue

            service = row['service']
            topic = row['topic']

            if service is None or topic is None:
                 continue

            service = service.lower()
            topic = topic.lower()

            if service not in self.services:
                 self.services[service] = {}

            if not topic in self.services[service]:
                self.services[service][topic] = row
