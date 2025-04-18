import json

from topic_components import TopicComponents
from hass_gxdevice_entity import HomeAssistantGXDeviceEntity

class HomeAssistantGXDevice:

    def __init__(self, mqtt_client, serial, registers):
        self.mqtt = mqtt_client
        self.serial = serial
        self.registers = registers

    def subscribe(self):
        self.mqtt.subscribe("victron/N/%s/+/+/ProductId" % self.serial)
        self.mqtt.publish('victron/R/%s/keepalive' % self.serial, '')

    def on_mqtt_message(self, msg):
        topic_components = TopicComponents.from_topic(msg.topic)

        if not topic_components.valid:
            return

        if topic_components.serial != self.serial:
            return

        topic = self.registers.lookup_mqtt_topic(msg.topic)
        if topic is None:
            return

        print(topic_components.dbus_topic)

        entity = HomeAssistantGXDeviceEntity(msg, topic)

        self.mqtt.publish(
            'homeassistant/%s/%s/%s/config' % (entity.device_type, entity.device_id, entity.topic_id),
            json.dumps(entity.entity_description)
        )



