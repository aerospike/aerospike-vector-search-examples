import time

from flask import jsonify, request, send_file

from config import Config
from data_encoder import encoder
from dataset_stats import dataset_counts
from prism import app
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
    image_id = request.args.get("image_id")
    record = avs_client.get(
        namespace=Config.PROXIMUS_NAMESPACE, set=Config.PROXIMUS_SET, key=image_id,
        field_names="image_embedding"
    )
    embedding = record.fields["image_embedding"]

    # Search on more and filter the query image.
    start = time.time()
    results = vector_search(embedding, Config.PROXIMUS_MAX_RESULTS + 1)
    results = list(
        filter(lambda result: result.fields["image_id"] != image_id, results))
    time_taken = time.time() - start
    return format_results(results[: Config.PROXIMUS_MAX_RESULTS], time_taken)


def vector_search(embedding, count=Config.PROXIMUS_MAX_RESULTS):
    # Execute kNN search over the image dataset
    fields = ["image_id", "image_name", "relative_path"]
    return avs_client.vector_search(
        namespace=Config.PROXIMUS_NAMESPACE,
        index_name=Config.PROXIMUS_INDEX_NAME,
        query=embedding,
        limit=count,
        field_names=fields,
    )


def format_results(results, time_taken):
    return jsonify(
        {"timeTaken": time_taken,
         "results": [result.fields for result in results]}
    )
