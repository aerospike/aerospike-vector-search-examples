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
from proximus_client import proximus_admin_client, proximus_client

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def read_csv(filename):
    if not os.path.exists(filename) and os.path.exists(filename + ".tgz"):
        # Untar the file
        with tarfile.open(filename + ".tgz", "r:gz") as tar:
            tar.extractall(path=os.path.dirname(filename))
        
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header
        for row in reader:
            yield row


DATASET_FILE = "../container-volumes/quote-search/data/quotes.csv"
dataset = itertools.islice(read_csv(DATASET_FILE), Config.NUM_QUOTES)


def create_index():
    for index in proximus_admin_client.indexList():
        if (index.id.namespace == Config.PROXIMUS_NAMESPACE and
                index.id.name ==
                Config.PROXIMUS_INDEX_NAME):
            return
    proximus_admin_client.indexCreate(Config.PROXIMUS_NAMESPACE,
                                      Config.PROXIMUS_INDEX_NAME,
                                      "",
                                      "quote_embedding", MODEL_DIM)


def either(c):
    return '[%s%s]' % (c.lower(), c.upper()) if c.isalpha() else c


def index_data():
    try:
        logger.info("Creating index")
        create_index()

        logger.info("Found new files to index")
        
        if Config.INDEXER_PARALLELISM <= 1:
            for quote in tqdm(enumerate(dataset), "Indexing quotes", total=Config.NUM_QUOTES):
                index_quote(quote)
        else:
            with get_context("spawn").Pool(
                    processes=Config.INDEXER_PARALLELISM) as pool:
                for _ in tqdm(pool.imap(index_quote, enumerate(dataset)), "Indexing quotes",
                                total=Config.NUM_QUOTES):
                    pass

    except Exception as e:
        logger.warning("Error indexing:" + str(e))
        import traceback
        traceback.print_exc()
    

def index_quote(id_quote):
    id, quote  = id_quote
    quote, author, catagory = quote
    doc = {'quote_id': id}
    doc['quote'] = quote
    doc['author'] = author
    doc["tags"] = catagory.split(",")
    logger.debug(f"Creating text vector embedding {id}")
    text = quote + " ".join(doc["tags"])
    embedding = encoder(text)
    doc['quote_embedding'] = embedding.tolist()

    # Insert record
    try:
        proximus_client.put(Config.PROXIMUS_NAMESPACE, "",
                            doc['quote_id'], doc)
    except Exception as e:
        logger.warning(f"Error inserting vector embedding into proximus {id}: {str(e)} quote: {quote}")
        # Retry again
        pass


def start():
    # Index data once
    thread = Thread(target=index_data)
    thread.start()


if __name__ == '__main__':
    start()
    print("Indexing done")