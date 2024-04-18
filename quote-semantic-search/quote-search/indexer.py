import asyncio
import collections
from concurrent.futures import ProcessPoolExecutor
import csv
import itertools
from multiprocessing import get_context
import os
import logging
from tqdm import tqdm
import tarfile

from config import Config
from data_encoder import MODEL_DIM, encoder
from proximus_client import proximus_admin_client, proximus_client
from aerospike_vector import types_pb2

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def read_csv(filename):
    if not os.path.exists(filename) and os.path.exists(filename + ".tgz"):
        # Untar the file
        with tarfile.open(filename + ".tgz", "r:gz") as tar:
            tar.extractall(path=os.path.dirname(filename))

    with open(filename, "r") as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header
        for row in reader:
            yield row


DATASET_FILE = "../container-volumes/quote-search/data/quotes.csv"
dataset = itertools.islice(read_csv(DATASET_FILE), Config.NUM_QUOTES)


def create_index():
    for index in proximus_admin_client.indexList():
        if (
            index.id.namespace == Config.PROXIMUS_NAMESPACE
            and index.id.name == Config.PROXIMUS_INDEX_NAME
        ):
            return

    proximus_admin_client.indexCreate(
        namespace=Config.PROXIMUS_NAMESPACE,
        name=Config.PROXIMUS_INDEX_NAME,
        setFilter=Config.PROXIMUS_SET,
        vector_bin_name="quote_embedding",
        dimensions=MODEL_DIM,
        vector_distance_metric=types_pb2.VectorDistanceMetric.COSINE,
    )


def either(c):
    return "[%s%s]" % (c.lower(), c.upper()) if c.isalpha() else c


def index_data():
    try:
        logger.info("Creating index")
        create_index()

        if Config.INDEXER_PARALLELISM <= 1:
            for quote in tqdm(
                enumerate(dataset), "Indexing quotes", total=Config.NUM_QUOTES
            ):
                embedding, _ = embed_text(quote)
                index_quote(quote, embedding)

        else:

            with get_context("spawn").Pool(
                processes=Config.INDEXER_PARALLELISM
            ) as pool:
                for r in tqdm(
                    pool.imap(embed_text, enumerate(dataset)),
                    "Indexing quotes",
                    total=Config.NUM_QUOTES,
                ):
                    index_quote(r[1], r[0])

    except Exception as e:
        logger.warning("Error indexing:" + str(e))
        import traceback

        traceback.print_exc()


def embed_text(id_quote):
    id, quote = id_quote
    quote, author, catagory = quote
    text = quote + " ".join(catagory.split(","))
    return encoder(text), id_quote


def index_quote(id_quote, embedding):
    id, quote = id_quote
    quote, author, category = quote
    doc = {"quote_id": id}
    doc["quote"] = quote
    doc["author"] = author
    doc["tags"] = category.split(",")
    logger.debug(f"Creating text vector embedding {id}")
    doc["quote_embedding"] = embedding.tolist()

    # Insert record
    try:
        proximus_client.put(
            namespace=Config.PROXIMUS_NAMESPACE,
            set=Config.PROXIMUS_SET,
            key=doc["quote_id"],
            bins=doc,
        )
    except Exception as e:
        logger.warning(
            f"Error inserting vector embedding into proximus {id}: {str(e)} quote: {quote}"
        )
        # Retry again
        pass


def start():
    # Index data once
    index_data()
    logger.info("Indexing complete")
