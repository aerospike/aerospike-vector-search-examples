from typing import Any

import google.protobuf.empty_pb2

from . import conversions
from . import transact_pb2, types_pb2, transact_pb2_grpc
from . import types
from . import vectordb_channel_provider

empty = google.protobuf.empty_pb2.Empty()


class VectorDbClient(object):
    """Vector DB client"""

    def __init__(self, seeds: types.HostPort | tuple[types.HostPort, ...], listener_name: str = None):
        if not seeds:
            raise Exception("at least one seed host needed")
        
        if isinstance(seeds, types.HostPort):
            seeds = (seeds,)

        self._channelProvider = (
            vectordb_channel_provider.VectorDbChannelProvider(
                seeds, listener_name))
        
    def connect(self):
        self._channelProvider.connect()

    def put(self, namespace: str, set: str, key: Any, bins: dict[str, Any]):
        """Write a record to vector DB"""
        transact_stub = transact_pb2_grpc.TransactStub(
            self._channelProvider.getChannel())
        key = self.getKey(key, set, namespace)
        binList = [types_pb2.Bin(name=k, value=conversions.toVectorDbValue(v))
                   for (k, v) in bins.items()]
        transact_stub.Put(
            transact_pb2.PutRequest(key=key, bins=binList))

    def get(self, namespace: str, set: str, key: Any,
            *bin_names: str) -> types.RecordWithKey:
        """Read a record from vector DB"""
        transact_stub = transact_pb2_grpc.TransactStub(
            self._channelProvider.getChannel())
        key = self.getKey(key, set, namespace)
        bin_selector = self._getBinSelector(bin_names)
        # TODO: Convert to local types
        result = transact_stub.Get(
            transact_pb2.GetRequest(key=key, binSelector=bin_selector))
        return types.RecordWithKey(conversions.fromVectorDbKey(key),
                                   conversions.fromVectorDbRecord(
                                       result))

    def vectorSearch(self, namespace: str, index_name: str,
                     query: list[bool | float], limit: int,
                     *bin_names: str) -> list[types.RecordWithKey]:
        transact_stub = transact_pb2_grpc.TransactStub(
            self._channelProvider.getChannel())
        results = transact_stub.VectorSearch(
            transact_pb2.VectorSearchRequest(
                index=types_pb2.IndexId(namespace=namespace, name=index_name),
                queryVector=(conversions.toVectorDbValue(query).vectorValue),
                limit=limit,
                binSelector=self._getBinSelector(bin_names)
            )
        )
        return [conversions.fromVectorDbRecordWithKey(result) for result in
                results]

    def getKey(self, key, set, namespace):
        if isinstance(key, str):
            key = types_pb2.Key(namespace=namespace, set=set, stringValue=key)
        elif isinstance(key, int):
            key = types_pb2.Key(namespace=namespace, set=set, longValue=key)
        elif isinstance(key, (bytes, bytearray)):
            key = types_pb2.Key(namespace=namespace, set=set, bytesValue=key)
        else:
            raise Exception("Invalid key type" + type(key))
        return key

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._channelProvider.close()

    def _getBinSelector(self, bin_names):
        if not bin_names:
            bin_selector = transact_pb2.BinSelector(
                type=transact_pb2.BinSelectorType.ALL, binNames=bin_names)
        else:
            bin_selector = transact_pb2.BinSelector(
                type=transact_pb2.BinSelectorType.SPECIFIED, binNames=bin_names)
        return bin_selector
