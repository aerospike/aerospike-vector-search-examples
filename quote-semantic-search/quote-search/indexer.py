import glob
import os
import threading
from multiprocessing import get_context
from threading import Thread
import logging
import warnings

from tqdm import tqdm

from config import Config
from data_encoder import encoder
from proximus_client import proximus_admin_client, proximus_client

from datasets import load_dataset

dataset = load_dataset("Abirate/english_quotes", split="train")
NUM_QUOTES = len(dataset)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

warnings.filterwarnings('ignore') 

def create_index():
    for index in proximus_admin_client.indexList():
        if (index.id.namespace == Config.PROXIMUS_NAMESPACE and
                index.id.name ==
                Config.PROXIMUS_INDEX_NAME):
            return
    proximus_admin_client.indexCreate(Config.PROXIMUS_NAMESPACE,
                                      Config.PROXIMUS_INDEX_NAME,
                                      "",
                                      "quote_embedding", 768)


def either(c):
    return '[%s%s]' % (c.lower(), c.upper()) if c.isalpha() else c


def index_data():
    try:
        logger.info("Creating index")
        create_index()

        logger.info("Found new files to index")
        for data in tqdm(enumerate(dataset), "Indexing quotes",
                      total=len(dataset)):
            
            index_quote(data)

    except Exception as e:
        logger.warning("Error indexing:" + str(e))
        import traceback
        traceback.print_exc()

def index_quote(id_quote):
    id, quote = id_quote
    doc = {'quote_id': id}
    doc['quote'] = quote["quote"]
    doc['author'] = quote["author"]
    doc["tags"] = quote["tags"]
    logger.debug(f"Creating text vector embedding {id}")
    text = quote["quote"] + " ".join(quote["tags"])
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
    index_data()


if __name__ == '__main__':
    start()
    print("Indexing done")