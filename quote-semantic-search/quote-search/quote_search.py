from flask import Flask
from flask_basicauth import BasicAuth
from config import Config
import logging

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

dir(routes)
indexer.start()
dataset_stats.start()

if __name__ == "__main__":
    app.run(host="localhost", port=8080)
