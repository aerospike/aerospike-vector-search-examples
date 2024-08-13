import os


def get_bool_env(name, default):
    env = os.environ.get(name)
    if env is None:
        return default
    env = env.lower()

    if env in ["true", "1"]:
        return True
    else:
        return False


class Config(object):
    BASIC_AUTH_USERNAME = os.environ.get("APP_USERNAME") or ""
    BASIC_AUTH_PASSWORD = os.environ.get("APP_PASSWORD") or ""
    NUM_QUOTES = int(os.environ.get("APP_NUM_QUOTES") or 5000)
    AVS_HOST = os.environ.get("AVS_HOST") or "localhost"
    AVS_PORT = int(os.environ.get("AVS_PORT") or 5000)
    AVS_ADVERTISED_LISTENER = os.environ.get("AVS_ADVERTISED_LISTENER") or None
    AVS_TLS_CA_FILE = os.environ.get("AVS_TLS_CA_FILE") or None
    AVS_TLS_CA = None
    AVS_TLS_CERT_FILE = os.environ.get("AVS_TLS_CERT_FILE") or None
    AVS_TLS_CERT = None
    AVS_TLS_KEY_FILE = os.environ.get("AVS_TLS_KEY_FILE") or None
    AVS_TLS_KEY = None
    AVS_INDEX_NAME = os.environ.get("AVS_INDEX_NAME") or "quote-semantic-search"
    AVS_NAMESPACE = os.environ.get("AVS_NAMESPACE") or "test"
    AVS_SET = os.environ.get("AVS_SET") or "quote-data"
    AVS_INDEX_NAMESPACE = os.environ.get("AVS_INDEX_NAMESPACE") or "test"
    AVS_INDEX_SET = os.environ.get("AVS_INDEX_SET") or "quote-index"
    AVS_VERIFY_TLS = get_bool_env("VERIFY_TLS", True)
    AVS_MAX_RESULTS = int(os.environ.get("AVS_MAX_RESULTS") or 5)
    INDEXER_PARALLELISM = int(os.environ.get("APP_INDEXER_PARALLELISM") or 1)
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH") or 10485760)
    AVS_IS_LOADBALANCER = get_bool_env("AVS_IS_LOADBALANCER", False)
    DATASET_FILE_PATH = (
        os.environ.get("DATASET_FILE_PATH")
        or "../container-volumes/quote-search/data/quotes.csv"
    )

    if NUM_QUOTES > 100000:
        NUM_QUOTES = 100000

    if AVS_TLS_CA_FILE:
        with open(AVS_TLS_CA_FILE, "rb") as f:
            AVS_TLS_CA = f.read()

    if AVS_TLS_CERT_FILE:
        with open(AVS_TLS_CERT_FILE, "rb") as f:
            AVS_TLS_CERT = f.read()

    if AVS_TLS_KEY_FILE:
        with open(AVS_TLS_KEY_FILE, "rb") as f:
            AVS_TLS_KEY = f.read()
