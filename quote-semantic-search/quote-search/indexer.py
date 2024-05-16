import csv
import itertools
from multiprocessing import get_context
import os
from threading import Thread
import logging
from tqdm import tqdm
import tarfile

from config import Config
from data_encoder import MODEL_DIM, encoder
from avs_client import avs_admin_client, avs_client
from aerospike_vector_search import types

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def read_csv(filename):
    if not os.path.exists(filename) and os.path.exists(filename + ".tgz"):
        # Untar the file
        with tarfile.open(filename + ".tgz", "r:gz") as tar:
            tar.extractall(path=os.path.dirname(filename))

    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header
        for row in reader:
            yield row


DATASET_FILE = Config.DATASET_FILE_PATH
dataset = itertools.islice(read_csv(DATASET_FILE), Config.NUM_QUOTES)


def create_index():
    for index in avs_admin_client.index_list():
        if (
            index["id"]["namespace"] == Config.AVS_NAMESPACE
            and index["id"]["name"] == Config.AVS_INDEX_NAME
        ):
            return

    avs_admin_client.index_create(
        namespace=Config.AVS_NAMESPACE,
        name=Config.AVS_INDEX_NAME,
        sets=Config.AVS_SET,
        vector_field="quote_embedding",
        dimensions=MODEL_DIM,
        vector_distance_metric=types.VectorDistanceMetric.COSINE,
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
                index_quote(quote)
        else:
            with get_context("spawn").Pool(
                processes=Config.INDEXER_PARALLELISM
            ) as pool:
                for _ in tqdm(
                    pool.imap(index_quote, enumerate(dataset)),
                    "Indexing quotes",
                    total=Config.NUM_QUOTES,
                ):
                    pass

    except Exception as e:
        logger.warning("Error indexing:" + str(e))
        import traceback

        traceback.print_exc()


def index_quote(id_quote):
    id, quote = id_quote
    quote, author, catagory = quote
    doc = {"quote_id": id}
    doc["quote"] = quote
    doc["author"] = author
    doc["tags"] = catagory.split(",")
    logger.debug(f"Creating text vector embedding {id}")
    text = quote + " ".join(doc["tags"])
    embedding = encoder(text)
    doc["quote_embedding"] = embedding  # Numpy array is supported by aerospike

    # Insert record
    try:
        avs_client.upsert(
            namespace=Config.AVS_NAMESPACE,
            set_name=Config.AVS_SET,
            key=doc["quote_id"],
            record_data=doc,
        )
    except Exception as e:
        logger.warning(
            f"Error inserting vector embedding into avs {id}: {str(e)} quote: {quote}"
        )
        # Retry again
        pass


def start():
    # Index data once
    thread = Thread(target=index_data)
    thread.start()


if __name__ == "__main__":
    start()
