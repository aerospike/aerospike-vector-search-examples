from aerospike_vector import vectordb_client, vectordb_admin, types

from config import Config

proximus_client = vectordb_client.VectorDbClient(
    types.HostPort(Config.PROXIMUS_HOST,
                   Config.PROXIMUS_PORT,
                   Config.PROXIMUS_VERIFY_TLS),
    Config.PROXIMUS_ADVERTISED_LISTENER)


proximus_admin_client = vectordb_admin.VectorDbAdminClient(
    types.HostPort(Config.PROXIMUS_HOST,
                   Config.PROXIMUS_PORT,
                   Config.PROXIMUS_VERIFY_TLS),
    Config.PROXIMUS_ADVERTISED_LISTENER)
