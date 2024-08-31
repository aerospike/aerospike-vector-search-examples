import argparse
from aerospike_vector_search import types
from aerospike_vector_search import AdminClient, Client
listener_name = None


with AdminClient(
     seeds=types.HostPort(host="34.71.101.78", port=5000),
     is_loadbalancer=True,
     listener_name=listener_name,
 ) as adminClient:
    try:
        print("creating index")
        namespace = "test"
        name = "basic_search_idx_binary_index_whatever"
        vector_field = "vector"
        dimensions = 2
        sets = "sillypy_index_binary_index_whatever"

        adminClient.index_create(
            namespace=namespace,
            name=name,
            vector_field="vector",
            dimensions=dimensions,
            sets=sets,
            index_storage=types.IndexStorage(namespace=namespace, set_name="sillypy_index_binary_index_storage"),
        )
    except Exception as e:
        print("failed creating index " + str(e))
        pass

with Client(
     seeds=types.HostPort(host="34.71.101.78", port=5000),
     is_loadbalancer=True,
     listener_name=listener_name,
 ) as client:
    print("inserting vector")
    namespace = "test"
    set_name = "basic_search_binary_data_2"
    key="nah_bro_binary_data_2"
    client.upsert(
        namespace=namespace,
        set_name=set_name,
        key=key,
        record_data={
            "vector": [True, False, False],
        }
    )

