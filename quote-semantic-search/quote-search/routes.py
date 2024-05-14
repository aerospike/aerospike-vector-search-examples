import time
from flask import jsonify, request, send_file

from config import Config
from dataset_stats import dataset_counts
from data_encoder import encoder
from quote_search import app
from avs_client import avs_client


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
        results = vector_search(embedding.tolist())
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
        namespace=Config.PROXIMUS_NAMESPACE, set_name=Config.PROXIMUS_SET, key=int(quote_id), field_names=["quote_embedding"]
    )
    embedding = record.fields["quote_embedding"]
    # Search on more and filter the query id.
    start = time.time()
    results = vector_search(embedding, Config.PROXIMUS_MAX_RESULTS + 1)
    results = list(filter(lambda result: result.fields["quote_id"] != quote_id, results))
    time_taken = time.time() - start
    return format_results(results[: Config.PROXIMUS_MAX_RESULTS], time_taken)


def vector_search(embedding, count=Config.PROXIMUS_MAX_RESULTS):
    # Execute kNN search over the dataset
    fields = ("quote_id", "quote", "author")
    return avs_client.vectorSearch(
        namespace=Config.PROXIMUS_NAMESPACE,
        index_name=Config.PROXIMUS_INDEX_NAME,
        query=embedding,
        limit=count,
        field_names=fields,
    )


def format_results(results, time_taken):
    return jsonify(
        {"timeTaken": time_taken, "results": [result.fields for result in results]}
    )
