import os
import threading
import warnings
from threading import Thread
import logging

from config import Config
from indexer import image_data_files, relative_path
from proximus_client import proximus_client

lock = threading.Lock()

dataset_counts = {}

logger = logging.getLogger(__name__)


def either(c):
    return "[%s%s]" % (c.lower(), c.upper()) if c.isalpha() else c


def collect_stats():
    lock.acquire()
    try:
        filenames = image_data_files()
        temp_counts = {}
        for filename in filenames:
            # Check if record exists
            filename = filename.replace("/train", "")
            filename = filename.replace("/google-landmark/google-landmark", "/google-landmark")

            if proximus_client.isIndexed(
                Config.PROXIMUS_NAMESPACE,
                Config.PROXIMUS_SET,
                filename,
                Config.PROXIMUS_INDEX_NAME,
            ):
                # Record exists
                path = relative_path(filename)
                dataset_name = path.split(os.sep)[1]

                if dataset_name not in temp_counts:
                    temp_counts[dataset_name] = 0

                temp_counts[dataset_name] = temp_counts[dataset_name] + 1

        dataset_counts.update(temp_counts)
    except Exception as e:
        logger.warn("Error collecting statistics:" + str(e))
    lock.release()

    # Repeat indexing.
    threading.Timer(30, collect_stats).start()


def create_image_id(filename):
    return os.path.splitext(os.path.basename(filename))[0]


def start():
    # Start indexing in a separate thread
    thread = Thread(target=collect_stats)
    thread.start()
