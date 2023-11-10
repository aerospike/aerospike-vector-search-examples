from typing import Any

import google.protobuf.empty_pb2

from . import conversions, index_pb2_grpc
from . import types
from . import types_pb2
from . import vectordb_channel_provider

empty = google.protobuf.empty_pb2.Empty()


class VectorDbAdminClient(object):
    """Vector DB Admin client"""

    def __init__(self, seeds: types.HostPort, listener_name: str = None):
        if not seeds:
            raise Exception("at least one seed host needed")
        
        if isinstance(seeds, types.HostPort):
            seeds = (seeds,)

        self.channelProvider = vectordb_channel_provider.VectorDbChannelProvider(
            seeds, listener_name)

    def indexCreate(self, namespace: str, name: str, set: str,
                    vector_bin_name: str, dimensions: int,
                    params: dict[str, Any] = None):
        """Create an index"""
        index_stub = index_pb2_grpc.IndexServiceStub(
            self.channelProvider.getChannel())
        if params is None:
            params = {}

        grpcParams = {}
        for k, v in params.items():
            grpcParams[k] = conversions.toVectorDbValue(v)

        index_stub.Create(
            types_pb2.IndexDefinition(
                id=types_pb2.IndexId(namespace=namespace, name=name),
                bin=vector_bin_name,
                dimensions=dimensions,
                params=grpcParams))

    def indexDrop(self, namespace: str, name: str, ):
        index_stub = index_pb2_grpc.IndexServiceStub(
            self.channelProvider.getChannel())
        index_stub.Drop(
            id=types_pb2.IndexId(namespace=namespace, name=name))

    def indexList(self) -> list[Any]:
        index_stub = index_pb2_grpc.IndexServiceStub(
            self.channelProvider.getChannel())
        return index_stub.List(empty).indices

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    def connect(self):
        self.channelProvider.connect()

    def close(self):
        self.channelProvider.close()
