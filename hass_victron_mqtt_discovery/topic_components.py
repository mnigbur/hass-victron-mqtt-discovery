import re

from functools import cache

RE_MQTT_TOPIC = r'N/([^/]+)/([^/]+)/(\d+)(/.*)$'

class TopicComponents(dict):
    __getattr__ = dict.get

    @cache
    def from_topic(topic):
        return TopicComponents(topic)

    def __init__(self, topic):
        m = re.search(RE_MQTT_TOPIC, topic)

        if m is None:
            self.update({ 'valid': False })
            return

        self.update({
            'valid': True,
            'serial': m.group(1),
            'service': m.group(2),
            'instance': m.group(3),
            'dbus_topic': m.group(4),
        })
