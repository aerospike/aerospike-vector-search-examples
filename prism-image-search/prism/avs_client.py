from aerospike_vector_search import Client, AdminClient, types

from config import Config

seeds = types.HostPort(
    host=Config.AVS_HOST,
    port=Config.AVS_PORT,
)

avs_client = Client(
    seeds=seeds,
    listener_name=Config.AVS_ADVERTISED_LISTENER,
    is_loadbalancer=Config.AVS_IS_LOADBALANCER,
)


avs_admin_client = AdminClient(
    seeds=seeds,
    listener_name=Config.AVS_ADVERTISED_LISTENER,
    is_loadbalancer=Config.AVS_IS_LOADBALANCER,
)
