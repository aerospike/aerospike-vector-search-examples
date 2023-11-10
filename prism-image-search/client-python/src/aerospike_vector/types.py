from typing import Any


class HostPort(object):
    def __init__(self, address: str, port: int, isTls=False):
        self.address = address
        self.port = port
        self.isTls = isTls


class Key(object):
    def __init__(self, namespace: str, set: str, digest: bytearray, key: Any):
        self.namespace = namespace
        self.set = set
        self.digest = digest
        self.key = key


class RecordWithKey(object):
    def __init__(self, key: Key, bins: dict[str, Any]):
        self.key = key
        self.bins = bins
