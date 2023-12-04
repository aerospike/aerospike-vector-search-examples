import glob
import os
import threading
from multiprocessing import get_context
from threading import Thread
import logging

from PIL import Image
from tqdm import tqdm

from config import Config
from data_encoder import encoder
from proximus_client import proximus_admin_client, proximus_client

lock = threading.Lock()
extensions = [".jp*g", ".png"]
image_datasets_glob = "static/images/data/**/*"
image_datasets_folder = "static/images/data"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def create_index():
    for index in proximus_admin_client.indexList():
        if (index.id.namespace == Config.PROXIMUS_NAMESPACE and
                index.id.name ==
                Config.PROXIMUS_INDEX_NAME):
            return
    proximus_admin_client.indexCreate(Config.PROXIMUS_NAMESPACE,
                                      Config.PROXIMUS_INDEX_NAME,
                                      "",
                                      "image_embedding", 512)


def either(c):
    return '[%s%s]' % (c.lower(), c.upper()) if c.isalpha() else c


def index_data():
    lock.acquire()
    try:
        logger.info("Creating index")
        create_index()
        filenames = image_data_files()

        to_index = []
        for filename in tqdm(filenames, "Checking for new files", total=len(
                filenames)):
            # Check if record exists
            try:
                proximus_client.get(Config.PROXIMUS_NAMESPACE, "",
                                    filename)
                # Record exists
                continue
            except:
                pass
            to_index.append(filename)
        if len(to_index) > 0:
            logger.info("Found new files to index")
            if Config.INDEXER_PARALLELISM <= 1:
                for filename in tqdm(to_index, "Indexing new files", total=len(to_index)):
                    index_image(filename)
            else:
                with get_context("spawn").Pool(
                        processes=Config.INDEXER_PARALLELISM) as pool:
                    for _ in tqdm(pool.imap(index_image, to_index), "Indexing new files",
                                  total=len(to_index)):
                        pass

    except Exception as e:
        logger.warning("Error indexing:" + str(e))
        import traceback
        traceback.print_exc()

    lock.release()

    # Repeat indexing.
    threading.Timer(30, index_data).start()


def image_data_files():
    filenames = sum(
        [glob.glob(
            ''.join(either(char) for char in (image_datasets_glob + x)),
            recursive=True) for x in
            extensions], [])
    return filenames


def index_image(filename):
    doc = {'image_id': filename}
    logger.debug(f"Opening file {filename}")
    image = Image.open(filename)
    doc['image_name'] = os.path.basename(filename)
    logger.debug(f"Creating image vector embedding {filename}")
    embedding = encoder(image)
    doc['image_embedding'] = embedding.tolist()
    doc['relative_path'] = relative_path(filename)
    # Insert record
    try:
        logger.info(f"Inserting vector embedding into proximus {filename}")
        proximus_client.put(Config.PROXIMUS_NAMESPACE, "",
                            doc['image_id'], doc)
    except:
        # Retry again
        pass


def relative_path(filename):
    return os.path.relpath(filename).split(image_datasets_folder)[1]


def create_image_id(filename):
    return os.path.splitext(os.path.basename(filename))[0]


def start():
    # Start indexing in a separate thread
    thread = Thread(target=index_data)
    thread.start()
