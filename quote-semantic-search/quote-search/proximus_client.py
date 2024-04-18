from aerospike_vector import vectordb_client, vectordb_admin, types

from config import Config

proximus_client = vectordb_client.VectorDbClient(
    seeds=types.HostPort(
        address=Config.PROXIMUS_HOST,
        port=Config.PROXIMUS_PORT,
        isTls=Config.PROXIMUS_VERIFY_TLS,
    ),
    listener_name=Config.PROXIMUS_ADVERTISED_LISTENER,
    # is_loadbalancer=Config.PROXIMUS_IS_LOADBALANCER,
)


proximus_admin_client = vectordb_admin.VectorDbAdminClient(
    seeds=types.HostPort(
        address=Config.PROXIMUS_HOST,
        port=Config.PROXIMUS_PORT,
        isTls=Config.PROXIMUS_VERIFY_TLS,
    ),
    listener_name=Config.PROXIMUS_ADVERTISED_LISTENER,
    # is_loadbalancer=Config.PROXIMUS_IS_LOADBALANCER,
)
