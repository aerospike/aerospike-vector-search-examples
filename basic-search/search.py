from aerospike_vector_search import types
from aerospike_vector_search import AdminClient, Client

host = "localhost"
port = 5000
listener_name = None

namespace = "test"
set_name = "simple_search"
index_name = "simple_index"

with AdminClient(
    seeds=types.HostPort(host=host, port=port), listener_name=listener_name
) as adminClient:
    try:
        print("creating index")
        adminClient.index_create(
            namespace=namespace,
            name=index_name,
            vector_field="vector",
            dimensions=2,
            sets=set_name,
        )
    except Exception as e:
        print("failed creating index " + str(e))
        pass

with Client(
    seeds=types.HostPort(host=host, port=port), listener_name=listener_name
) as client:
    print("inserting vectors")
    for i in range(10):
        key = "r" + str(i)
        if not client.is_indexed(
            namespace="test", set_name=set_name, key=key, index_name=index_name
        ):
            client.upsert(
                namespace=namespace,
                set_name=set_name,
                key=key,
                record_data={
                    "url": f"http://host.com/data{i}",
                    "vector": [i * 1.0, i * 1.0],
                    "map": {"a": "A", "inlist": [1, 2, 3]},
                    "list": ["a", 1, "c", {"a": "A"}],
                },
            )

    print("waiting for indexing to complete")
    client.wait_for_index_completion(namespace="test", name=index_name)

    print("querying")
    for i in range(10):
        print("   query " + str(i))
        results = client.vector_search(
            namespace=namespace,
            index_name=index_name,
            query=[i * 1.0, i * 1.0],
            limit=10,
        )
        for result in results:
            print(str(result.key.key) + " -> " + str(result.fields))
