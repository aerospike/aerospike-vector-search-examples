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
    INDEXER_PARALLELISM = int(os.environ.get("APP_INDEXER_PARALLELISM") or 1)
    AVS_HOST = os.environ.get("AVS_HOST") or "localhost"
    AVS_PORT = int(os.environ.get("AVS_PORT") or 5000)
    AVS_ADVERTISED_LISTENER = os.environ.get("AVS_ADVERTISED_LISTENER") or None
    AVS_INDEX_NAME = os.environ.get("AVS_INDEX_NAME") or "prism-image-search"
    AVS_NAMESPACE = os.environ.get("AVS_NAMESPACE") or "avs-data"
    AVS_SET = os.environ.get("AVS_SET") or "image-data"
    AVS_INDEX_NAMESPACE = os.environ.get("AVS_INDEX_NAMESPACE") or "avs-index"
    AVS_INDEX_SET = os.environ.get("AVS_INDEX_SET") or "image-index"
    AVS_VERIFY_TLS = get_bool_env("VERIFY_TLS", True)
    AVS_MAX_RESULTS = int(os.environ.get("AVS_MAX_RESULTS") or 20)
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH") or 10485760)
    # using a load balancer with AVS is best practice so this is the default
    # you should set this to False if you are not using a load balancer with an AVS cluster of more than 1 node
    AVS_IS_LOADBALANCER = get_bool_env("AVS_IS_LOADBALANCER", True)
