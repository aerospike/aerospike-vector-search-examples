import random
import re
import threading
import warnings

import google.protobuf.empty_pb2
import grpc

from . import types, vector_db_pb2
from . import vector_db_pb2_grpc

empty = google.protobuf.empty_pb2.Empty()


class ChannelAndEndpoints(object):
    def __init__(self, channel: grpc.Channel,
                 endpoints: vector_db_pb2.ServerEndpointList):
        self.channel = channel
        self.endpoints = endpoints


class VectorDbChannelProvider(object):
    """Vector DB client"""

    def __init__(self, seeds: tuple[types.HostPort], listener_name: str = None):
        if not seeds:
            raise Exception("at least one seed host needed")
        self._nodeChannels: dict[int, ChannelAndEndpoints] = {}
        self._seedChannels: list[grpc.Channel] = {}
        self._closed = True
        self._clusterId = 0
        self.seeds = seeds
        self.listener_name = listener_name

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    def connect(self):
        if not self._closed:
            return
        
        self._seedChannels = [self._createChannelFromHostPort(seed) for seed in
                              self.seeds]
        self._tend()
        self._closed = False

    def close(self):
        self._closed = True
        for channel in self._seedChannels:
            channel.close()

        for k, channelEndpoints in self._nodeChannels.items():
            channelEndpoints.channel.close()

    def getChannel(self) -> grpc.Channel:
        discoveredChannels: list[ChannelAndEndpoints] = list(
            self._nodeChannels.values())

        if len(discoveredChannels) <= 0:
            return self._seedChannels[0]

        # Return a random channel.
        return random.choice(discoveredChannels).channel

    def _tend(self):
        # TODO: Worry about thread safety
        temp_endpoints: dict[int, vector_db_pb2.ServerEndpointList] = {}
        
        if self._closed:
            return

        try:
            update_endpoints = False
            channels = self._seedChannels + [x.channel for x in
                                             self._nodeChannels.values()]
            for seedChannel in channels:
                try:
                    stub = vector_db_pb2_grpc.ClusterInfoStub(seedChannel)
                    newClusterId = stub.GetClusterId(empty).id
                    if newClusterId == self._clusterId:
                        continue

                    update_endpoints = True
                    self._clusterId = newClusterId
                    endpoints = stub.GetClusterEndpoints(
                        vector_db_pb2.ClusterNodeEndpointsRequest(listenerName=self.listener_name)).endpoints

                    if len(endpoints) > len(temp_endpoints):
                        temp_endpoints = endpoints
                except:
                    continue

            if update_endpoints:
                for node, newEndpoints in temp_endpoints.items():
                    channel_endpoints = self._nodeChannels.get(node)
                    add_new_channel = True
                    if channel_endpoints:
                        # We have this node. Check if the endpoints changed.
                        if channel_endpoints.endpoints == newEndpoints:
                            # Nothing to be done for this node
                            add_new_channel = False
                        else:
                            # TODO: Wait for all calls to drain
                            channel_endpoints.channel.close()
                            add_new_channel = True

                    if add_new_channel:
                        # We have discovered a new node
                        new_channel = self._createChannelFromServerEndpointList(
                            newEndpoints)
                        self._nodeChannels[node] = ChannelAndEndpoints(
                            new_channel, newEndpoints)

                for node, channel_endpoints in self._nodeChannels.items():
                    if not temp_endpoints.get(node):
                        # TODO: Wait for all calls to drain
                        channel_endpoints.channel.close()
                        del self._nodeChannels[node]

        except Exception as e:
            # TODO: log this exception
            warnings.warn("error tending: " + str(e))

        if not self._closed:
            # TODO: check tend interval.
            threading.Timer(1, self._tend).start()

    def _createChannelFromHostPort(self, host: types.HostPort) -> grpc.Channel:
        return self._createChannel(host.address, host.port, host.isTls)

    def _createChannelFromServerEndpointList(self,
                                             endpoints: vector_db_pb2.ServerEndpointList) -> grpc.Channel:
        # TODO: Create channel with all endpoints
        for endpoint in endpoints.endpoints:
            if ":" in endpoint.address:
                # Ignore IPv6 for now
                continue

            try:
                return self._createChannel(endpoint.address, endpoint.port,
                                           endpoint.isTls)
            except:
                continue

    def _createChannel(self, host: str, port: int, isTls: bool) -> grpc.Channel:
        # TODO: Take care of TLS
        host = re.sub(r'%.*', '', host)
        return grpc.insecure_channel(f'{host}:{port}')
