import time
from flask import jsonify, request, send_file

from config import Config
from dataset_stats import dataset_counts
from data_encoder import encoder
from quote_search import app
from avs_client import avs_client
from aerospike_vector_search import types


@app.route("/")
def index_static():
    return send_file("static/index.html")


@app.route("/search")
def search_static():
    return send_file("static/index.html")


@app.route("/stats")
def stats_static():
    return send_file("static/index.html")


@app.route("/rest/v1/search", methods=["POST"])
def search():
    # FileStorage object wrapper
    text = request.form["text"]
    if text:
        embedding = encoder(text)
        start = time.time()
        results = vector_search(embedding)
        time_taken = time.time() - start
        return format_results(results, time_taken)
    else:
        return "No text uploaded", 400


@app.route("/rest/v1/stats", methods=["GET"])
def dataset_stats():
    return jsonify({"datasets": dataset_counts})


@app.route("/rest/v1/search_by_id", methods=["GET"])
def search_internal():
    quote_id = request.args.get("quote_id")

    if not quote_id:
        return "quote_id is required", 400

    record = avs_client.get(
        namespace=Config.AVS_NAMESPACE,
        set_name=Config.AVS_SET,
        key=int(quote_id),
        field_names=["quote_embedding"],
    )
    embedding = record.fields["quote_embedding"]
    # Search on more and filter the query id.
    start = time.time()
    results = vector_search(embedding, Config.AVS_MAX_RESULTS + 1)
    results = list(
        filter(lambda result: result.fields["quote_id"] != quote_id, results)
    )
    time_taken = time.time() - start
    return format_results(results[: Config.AVS_MAX_RESULTS], time_taken)


def vector_search(embedding, count=Config.AVS_MAX_RESULTS):
    # Execute kNN search over the dataset
    field_names = ["quote_id", "quote", "author"]
    r = avs_client.vector_search(
        namespace=Config.AVS_NAMESPACE,
        index_name=Config.AVS_INDEX_NAME,
        query=embedding,
        limit=count,
        field_names=field_names,
    )
    return r


def format_results(results: list[types.Neighbor], time_taken):
    return jsonify(
        {"timeTaken": time_taken, "results": [result.fields for result in results]}
    )
