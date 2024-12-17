import sys, os, argparse, timeit, random

from faker import Faker
from aerospike_vector_search import types
from aerospike_vector_search import AdminClient, Client
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.traversal import T, P, Operator
from time import perf_counter_ns

arg_parser = argparse.ArgumentParser(description="Aerospike Vector adn Graph Search Example")
arg_parser.add_argument(
    "--host",
    dest="host",
    required=False,
    default="localhost",
    help="Aerospike Vector Search host.",
)
arg_parser.add_argument(
    "--port",
    dest="port",
    required=False,
    default=5555,
    help="Aerospike Vector Search port.",
)
arg_parser.add_argument(
    "--namespace",
    dest="namespace",
    required=False,
    default="avs-data",
    help="Aerospike namespace for vector data.",
)
arg_parser.add_argument(
    "--set",
    dest="set",
    required=False,
    default="basic-data",
    help="Aerospike set for vector data.",
)
arg_parser.add_argument(
    "--index-name",
    dest="index_name",
    required=False,
    default="basic_index",
    help="Name of the index.",
)
arg_parser.add_argument(
    "--index-namespace",
    dest="index_namespace",
    required=False,
    default="avs-index",
    help="Aerospike namespace the for vector index.",
)
arg_parser.add_argument(
    "--index-set",
    dest="index_set",
    required=False,
    default="basic-index",
    help="Aerospike set for the vector index.",
)
arg_parser.add_argument(
    "--dimensions",
    dest="dimensions",
    required=False,
    default=3,
    help="number of dimensions",
)
arg_parser.add_argument(
    "--number-of-items-in-each-dimesnsion",
    dest="number_of_items_in_each_dimesnsion",
    required=False,
    default=10,
    help="number of items in a dimension",
)
arg_parser.add_argument(
    "--load-balancer",
    dest="load_balancer",
    action="store_true",
    required=False,
    default=True,
    help="Use this if the host is a load balancer.",
)
args = arg_parser.parse_args()

def vector_space_builder(current_list, current_iteration):
    list = []
    if current_iteration == args.dimensions: 
        for i in range(args.number_of_items_in_each_dimesnsion):
            item = [i * 1.0]
            list.append(item)
        return list
    
    current_list = vector_space_builder(current_list, current_iteration+1)
    for item in current_list:
        for i in range(args.number_of_items_in_each_dimesnsion):
            newItem = item.copy()
            newItem.append(i  * 1.0)
            list.append(newItem)
    return list

def vertex_builder(fake):
    result = []
    for i in range(args.dimensions):
        list = []
        list.append(i)
        list.append(fake.job())
        result.append(list)
    return result

def insert_jobs(gClient, jobs):
    print("Inserting jobs!")
    for j in jobs:
        gClient.add_v('Jobs').property(T.id, j[0]).property('Job', j[1]).next()
    print("Inserting jobs completed!")

def insert_data(gClient, vClient, vectors):
    print("Inserting "+ str(len(vectors)) + " vertices and edges!")
    start = perf_counter_ns()
    for v in vectors:
        key = ','.join( str(x) for x in v )
        vClient.upsert(namespace=args.namespace, set_name=args.set, key=key, record_data={ "vector": v } )
        person = gClient.add_v('Person').property(T.id, key).property('Name', fake.name()).property('IP', fake.ipv4_private()).next()
        gClient.V(person).addE("HAS_JOB").to(gClient.V(random.randint(0, args.dimensions-1)).next()).next()

    m_secs = round((perf_counter_ns() - start) / 10 ** 6, 3)
    print(f"Inserting took: {m_secs} milliseconds.")

def wait_for_index(vClient):
    print("Waiting for indexing to complete")
    start = perf_counter_ns()
    vClient.wait_for_index_completion(namespace=args.namespace, name=args.index_name)
    m_secs = round((perf_counter_ns() - start) / 10 ** 6, 3)
    print(f"Indexing took: {m_secs} milliseconds")

def query_vector_and_then_graph(vClient, gClient):
    print("Querying Vector and then Graph:")
    for i in range(args.dimensions):
        v = []
        for j in range(args.dimensions):
            v.append(random.uniform(0, args.number_of_items_in_each_dimesnsion))
        key = ','.join(map(str, v))
        start = perf_counter_ns()
        results = vClient.vector_search(namespace=args.namespace, index_name=args.index_name, query=v, limit=args.dimensions + 1)
        m_secs = round((perf_counter_ns() - start) / 10 ** 6, 3)
        print(f"Querying [{key}] took: {m_secs} milliseconds")

        for result in results:
            print(str(gClient.V(result.key.key).element_map().to_list()) + " -> " + str(gClient.V(result.key.key).out("HAS_JOB").value_map().to_list()))  

def query_graph_and_then_vector(vClient, gClient, jobs):
    print("Querying Graph and then Vector:")
    jobId = jobs[random.randint(0,args.dimensions-1)]
    print("Finding people who are " + gClient.V(jobId).values("Job").next())
    vertices = gClient.V(gClient.V(jobId).next()).inE().outV().to_list()
    people = list(map(lambda v: v.id, vertices))

    for j in range(args.dimensions):
        personId = people[random.randint(0,len(people)-1)]
        personVertex = gClient.V(personId).element_map().to_list()[0]
        personVector = [float(i) for i in personId.split(",")]
        print("A vertex representing of a random person with that job is: " + str(personVertex) )
        print("Here are few people close to them in vector space:")
        results = vClient.vector_search(namespace=args.namespace, index_name=args.index_name, query=personVector, limit=args.dimensions + 1)
        for result in results:
            print(str(gClient.V(result.key.key).element_map().to_list()))  

print("Clearing the environment and setting up!")
with AdminClient(seeds=types.HostPort(host=args.host, port=args.port), is_loadbalancer=args.load_balancer) as adminClient:
    try:
        old_stderr = sys.stderr # backup current stderr
        sys.stderr = open(os.devnull, "w")
        adminClient.index_drop(namespace=args.namespace, name=args.index_name, timeout=60)
    except Exception as e:
        pass
    sys.stderr = old_stderr # reset old stderr
    try:
        adminClient.index_create(namespace=args.namespace, name=args.index_name, vector_field="vector", dimensions=args.dimensions, sets=args.set, index_storage=types.IndexStorage(namespace=args.index_namespace, set_name=args.index_set))
    except Exception as e:
        print("failed creating index " + str(e))
        pass

fake = Faker()
vectors = vector_space_builder([], 1)
jobs = vertex_builder(fake)
vClient = Client(seeds=types.HostPort(host=args.host, port=args.port), is_loadbalancer=args.load_balancer)
gClient = traversal().with_remote(DriverRemoteConnection('ws://localhost:8182/gremlin', 'g')) 
gClient.V().drop().iterate()
print("Setup completed!")

insert_jobs(gClient, jobs)
insert_data(gClient, vClient, vectors)
wait_for_index(vClient)
query_vector_and_then_graph(vClient, gClient)
query_graph_and_then_vector(vClient, gClient, jobs)