import os
import threading
import warnings
from threading import Thread

from config import Config
from indexer import NUM_QUOTES
from proximus_client import proximus_client

lock = threading.Lock()

dataset_counts = {}


def either(c):
    return '[%s%s]' % (c.lower(), c.upper()) if c.isalpha() else c


def collect_stats():
    lock.acquire()
    try:
        temp_counts = {}
        for i in range(NUM_QUOTES):
            # Check if record exists
            try:
                proximus_client.get(Config.PROXIMUS_NAMESPACE, "",
                                    i)
                # Record exists
                temp_counts["quotes"] = temp_counts["quotes"] + 1
            except:
                pass
        dataset_counts.update(temp_counts)
    except Exception as e:
        warnings.warn("Error collecting statistics:" + str(e))
    lock.release()

    # Repeat indexing.
    threading.Timer(30, collect_stats).start()


def start():
    # Start indexing in a separate thread
    thread = Thread(target=collect_stats)
    thread.start()
