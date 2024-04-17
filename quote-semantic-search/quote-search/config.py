import os


def get_bool_env_var(var_name, default=False):
    value = os.environ.get(var_name)
    if value is not None:
        return value.lower() == "true"
    return default


class Config(object):
    BASIC_AUTH_USERNAME = os.environ.get("APP_USERNAME") or ""
    BASIC_AUTH_PASSWORD = os.environ.get("APP_PASSWORD") or ""
    NUM_QUOTES = int(os.environ.get("APP_NUM_QUOTES") or 5000)
    PROXIMUS_HOST = os.environ.get("PROXIMUS_HOST") or "localhost"
    PROXIMUS_PORT = int(os.environ.get("PROXIMUS_PORT") or 5000)
    PROXIMUS_ADVERTISED_LISTENER = (
        os.environ.get("PROXIMUS_ADVERTISED_LISTENER") or None
    )
    PROXIMUS_INDEX_NAME = (
        os.environ.get("PROXIMUS_INDEX_NAME") or "quote-semantic-search"
    )
    PROXIMUS_NAMESPACE = os.environ.get("PROXIMUS_NAMESPACE") or "test"
    PROXIMUS_SET = os.environ.get("PROXIMUS_SET") or "quote-data"
    PROXIMUS_VERIFY_TLS = get_bool_env_var("PROXIMUS_VERIFY_TLS", default=True)
    PROXIMUS_MAX_RESULTS = int(os.environ.get("PROXIMUS_MAX_RESULTS") or 5)
    INDEXER_PARALLELISM = int(os.environ.get("APP_INDEXER_PARALLELISM") or 1)
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH") or 10485760)
    PROXIMUS_IS_LOADBALANCER = get_bool_env_var("PROXIMUS_IS_LOADBALANCER")

    if NUM_QUOTES > 497715:
        NUM_QUOTES = 497715
