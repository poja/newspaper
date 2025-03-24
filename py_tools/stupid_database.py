import threading

import yaml


class StupidDatabase:

    def __init__(self, path):
        self.path = path
        self.lock = threading.Lock()

    def read(self):
        with self.lock:
            with open(self.path, 'r') as f:
                return yaml.safe_load(f)

    def write(self, new_data):
        assert len(str(new_data)) < 1_000_000, 'Database should be less than 1MB'
        with self.lock:
            with open(self.path, 'w') as f:
                yaml.dump(new_data, f)
