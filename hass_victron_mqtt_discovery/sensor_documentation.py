from pyquery import PyQuery as pq

from .cache import Cache

class SensorDocumentation(Cache):

    def __init__(self, sensor_documentation_path):
        self.unit_device_class_map = {}
        self.read_file(sensor_documentation_path)

    def add_unit_device_class_mapping(self, unit, clazz):
        if unit in self.unit_device_class_map:
            return

        self.unit_device_class_map[unit] = clazz

    def read_file(self, path):
        cache_id = self.file_cache_id(path)
        page = pq(filename=path)

        self.read_device_classes(page, cache_id=cache_id)

    def read_device_classes(self, page, cache_id=None):
        if cache_id is not None and self.has_cache(cache_id):
            self.unit_device_class_map = self.load_cache(cache_id)
            return

        state_table = pq(page('#available-device-classes').next_all('table')[0])

        for row in state_table('tbody tr').items():
            clazz, units, description = [ pq(c).text() for c in row('td') ]
            clazz = clazz.split('.')[-1].lower()
            units = [ u.strip() for u in units.split(',') ]

            for u in units:
                self.add_unit_device_class_mapping(u, clazz)

        if cache_id is not None:
            self.update_cache(cache_id, self.unit_device_class_map)

    def device_class_from_unit(self, unit):
        if unit in self.unit_device_class_map:
            return self.unit_device_class_map[unit]

        return None
