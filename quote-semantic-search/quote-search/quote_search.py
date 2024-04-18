import time
from config import Config
import logging

logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)


import indexer
import routes
from proximus_client import proximus_client
from data_encoder import encoder

# time.sleep(10)

dir(routes)
indexer.index_data()

bins = ("quote_id", "quote", "author")
embedding = encoder("dogs").tolist()
i = 0

while True:
    results = proximus_client.vectorSearch(
        Config.PROXIMUS_NAMESPACE,
        Config.PROXIMUS_INDEX_NAME,
        embedding,
        5,
        None,
        *bins,
    )

    print(f"Query {i} results")

    for i, r in enumerate(results):
        print("Result", i, r.bins)

    time.sleep(5)
