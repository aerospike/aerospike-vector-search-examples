import time
from flask import jsonify, request, send_file

from config import Config
from dataset_stats import dataset_counts
from data_encoder import encoder
from quote_search import app
from proximus_client import proximus_client


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
    try:
        text = request.form["text"]
        if text:
            embedding = encoder(text)
            start = time.time()
            # results = run_async(vector_search(embedding.tolist()))
            results = vector_search(embedding.tolist())
            time_taken = time.time() - start
            return format_results(results, time_taken)
        else:
            return "No text uploaded", 400
    except Exception as e:
        return str(e), 405


@app.route("/rest/v1/stats", methods=["GET"])
def dataset_stats():
    return jsonify({"datasets": dataset_counts})


@app.route("/rest/v1/search_by_id", methods=["GET"])
def search_internal():
    quote_id = request.args.get("quote_id")

    if not quote_id:
        return "quote_id is required", 400

    bin_names = ("quote_embedding",)

    record = proximus_client.get(
        Config.PROXIMUS_NAMESPACE,
        Config.PROXIMUS_SET,
        int(quote_id),
        *bin_names,
    )

    embedding = record.bins["quote_embedding"]
    # Search on more and filter the query id.
    start = time.time()
    results = vector_search(embedding, Config.PROXIMUS_MAX_RESULTS + 1)
    results = list(filter(lambda result: result.bins["quote_id"] != quote_id, results))
    time_taken = time.time() - start
    return format_results(results[: Config.PROXIMUS_MAX_RESULTS], time_taken)


def vector_search(embedding, count=Config.PROXIMUS_MAX_RESULTS):
    # Execute kNN search over the dataset
    bins = ("quote_id", "quote", "author")
    return proximus_client.vectorSearch(
        Config.PROXIMUS_NAMESPACE,
        Config.PROXIMUS_INDEX_NAME,
        embedding,
        count,
        None,
        *bins,
    )


def format_results(results, time_taken):
    return jsonify(
        {"timeTaken": time_taken, "results": [result.bins for result in results]}
    )
