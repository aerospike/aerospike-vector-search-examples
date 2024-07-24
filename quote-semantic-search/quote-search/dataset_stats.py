import threading
import logging
from threading import Thread

from avs_client import avs_client
from config import Config
from indexer import index_created

logger = logging.getLogger(__name__)

lock = threading.Lock()

dataset_counts = {}


def either(c):
    return "[%s%s]" % (c.lower(), c.upper()) if c.isalpha() else c


def collect_stats():
    lock.acquire()
    if index_created:
        try:
            logger.info("Collecting statistics")
            temp_counts = {}
            not_indexed = 0

            for quote_id in range(Config.NUM_QUOTES):
                # Check if record exists
                if avs_client.is_indexed(
                    namespace=Config.AVS_NAMESPACE,
                    set_name=Config.AVS_SET,
                    key=quote_id,
                    index_name=Config.AVS_INDEX_NAME,
                ):
                    # Record exists
                    quote_id = str(quote_id)

                    if quote_id not in temp_counts:
                        temp_counts[quote_id] = 0

                    temp_counts[quote_id] = temp_counts[quote_id] + 1
                else:
                    not_indexed += 1

            dataset_counts.update(temp_counts)

            logger.info(
                f"{len(dataset_counts)} quotes indexed and {not_indexed} not indexed."
            )
        except Exception as e:
            logger.warn("Error collecting statistics:" + str(e))

    lock.release()
    threading.Timer(30, collect_stats).start()


def start():
    # Start indexing in a separate thread
    thread = Thread(target=collect_stats)
    thread.start()
