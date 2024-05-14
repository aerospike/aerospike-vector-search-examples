from aerospike_vector_search import Client, AdminClient, types

from config import Config

avs_client = Client(
    seeds=types.HostPort(host=Config.PROXIMUS_HOST,
                   port=Config.PROXIMUS_PORT,
                   is_tls=Config.PROXIMUS_VERIFY_TLS),
    listener_name=Config.PROXIMUS_ADVERTISED_LISTENER,
    is_loadbalancer=Config.PROXIMUS_IS_LOADBALANCER
)


avs_admin_client = AdminClient(
    seeds=types.HostPort(host=Config.PROXIMUS_HOST,
                   port=Config.PROXIMUS_PORT,
                   is_tls=Config.PROXIMUS_VERIFY_TLS),
    listener_name=Config.PROXIMUS_ADVERTISED_LISTENER,
    is_loadbalancer=Config.PROXIMUS_IS_LOADBALANCER
)
