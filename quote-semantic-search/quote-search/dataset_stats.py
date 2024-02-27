import threading
from threading import Thread

lock = threading.Lock()

dataset_counts = {}


def either(c):
    return '[%s%s]' % (c.lower(), c.upper()) if c.isalpha() else c


def collect_stats():
    # lock.acquire()
    # TODO
    # lock.release()

    # Repeat indexing.
    # threading.Timer(30, collect_stats).start()


def start():
    # Start indexing in a separate thread
    thread = Thread(target=collect_stats)
    thread.start()
