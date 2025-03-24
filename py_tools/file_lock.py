import os
from pathlib import Path


class FileLock:
    def __init__(self, path: Path):
        self.path = path
        self.fd = None

    def __enter__(self):
        try:
            self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        except FileExistsError:
            raise LockUnavailable()

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.close(self.fd)
        os.remove(self.path)


class LockUnavailable(Exception):
    def __str__(self):
        return "The lock is unavailable. Perhaps another process is running?"
