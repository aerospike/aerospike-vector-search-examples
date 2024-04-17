import asyncio
import threading
from flask import Flask
from flask_basicauth import BasicAuth
from config import Config
import logging
from event_loop import run_async, loop

logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)


# The flask application.
app = Flask(__name__, static_url_path="")
app.config.from_object(Config)

if Config.BASIC_AUTH_USERNAME and Config.BASIC_AUTH_PASSWORD:
    logger.info("Running with basic auth")
    app.config["BASIC_AUTH_FORCE"] = True
    basic_auth = BasicAuth(app)

import indexer
import dataset_stats
import routes


def background():
    run_async(indexer.start(), blocking=False)
    run_async(dataset_stats.start(), blocking=False)
    loop.run_forever()


dir(routes)
background_thread = threading.Thread(target=background)
background_thread.start()

if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
