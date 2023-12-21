from aerospike_vector import types
from aerospike_vector import vectordb_admin, vectordb_client

host = "localhost"
port = 5000
listener_name = None

setName = "simple_search"
indexName = "simple_index"

with vectordb_admin.VectorDbAdminClient(
        types.HostPort(host, port), listener_name=listener_name) as adminClient:
    try:
        print("creating index")
        adminClient.indexCreate("test", indexName, "vector", 2,
                                setFilter=setName)
    except Exception as e:
        print("failed creating index " + str(e))
        pass

with vectordb_client.VectorDbClient(
        types.HostPort(host, port), listener_name=listener_name) as client:
    print("inserting vectors")
    for i in range(10):
        client.put("test", setName, "r" + str(i),
                   {"url": f"http://host.com/data{i}", "vector": [i * 1.0,
                                                                  i * 1.0],
                    "map": {"a": "A", "inlist": [1, 2, 3]},
                    "list": ["a", 1, "c", {"a": "A"}]})

    print("waiting for indexing to complete")
    with vectordb_admin.VectorDbAdminClient(
            types.HostPort(host, port),
            listener_name=listener_name) as adminClient:
        adminClient.waitForIndexCompletion("test", indexName)

    print("querying")
    for i in range(10):
        print("   query " + str(i))
        results = client.vectorSearch("test", indexName, [i * 1.0, i * 1.0],
                                      10)
        for result in results:
            print(str(result.key.digest) + " -> " + str(result.bins))