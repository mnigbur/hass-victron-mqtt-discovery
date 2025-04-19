import os
import json
import hashlib

def generate_file_hash(path):
    with open(path, 'rb', buffering=0) as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

class Cache:

    def file_cache_id(self, filename):
        return generate_file_hash(filename)

    def has_cache(self, cache_id):
        return os.path.isfile('.cache/' + cache_id)

    def load_cache(self, cache_id, default={}):
        if not self.has_cache(cache_id):
            return default

        path = '.cache/' + cache_id
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            os.remove(path)
            return default

    def update_cache(self, cache_id, value):
        os.makedirs('.cache', exist_ok=True)

        with open('.cache/' + cache_id, 'w') as f:
            json.dump(value, f, indent=2)
