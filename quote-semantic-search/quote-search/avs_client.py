from aerospike_vector_search import Client, AdminClient, types

from config import Config

avs_client = Client(
    seeds=types.HostPort(
        host=Config.AVS_HOST,
        port=Config.AVS_PORT,
    ),
    root_certificate=Config.AVS_TLS_CA,
    certificate_chain=Config.AVS_TLS_CERT,
    private_key=Config.AVS_TLS_KEY,
    listener_name=Config.AVS_ADVERTISED_LISTENER,
    is_loadbalancer=Config.AVS_IS_LOADBALANCER,
)


avs_admin_client = AdminClient(
    seeds=types.HostPort(
        host=Config.AVS_HOST,
        port=Config.AVS_PORT,
    ),
    root_certificate=Config.AVS_TLS_CA,
    certificate_chain=Config.AVS_TLS_CERT,
    private_key=Config.AVS_TLS_KEY,
    listener_name=Config.AVS_ADVERTISED_LISTENER,
    is_loadbalancer=Config.AVS_IS_LOADBALANCER,
)
