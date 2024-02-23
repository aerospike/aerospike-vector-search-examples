import os


class Config(object):
    BASIC_AUTH_USERNAME = os.environ.get('PRISM_APP_USERNAME') or ''
    BASIC_AUTH_PASSWORD = os.environ.get('PRISM_APP_PASSWORD') or ''
    PROXIMUS_HOST = os.environ.get('PROXIMUS_HOST') or 'localhost'
    PROXIMUS_PORT = int(os.environ.get('PROXIMUS_PORT') or 5000)
    PROXIMUS_ADVERTISED_LISTENER = os.environ.get(
        'PROXIMUS_ADVERTISED_LISTENER') or None
    PROXIMUS_INDEX_NAME = os.environ.get(
        'PROXIMUS_INDEX_NAME') or "quote-semantic-search"
    PROXIMUS_NAMESPACE = os.environ.get('PROXIMUS_NAMESPACE') or "test"
    PROXIMUS_VERIFY_TLS = os.environ.get('VERIFY_TLS') or True
    PROXIMUS_MAX_RESULTS = int(os.environ.get('PROXIMUS_MAX_RESULTS') or 5)
    INDEXER_PARALLELISM = int(os.environ.get('INDEXER_PARALLELISM') or 1)
    MAX_CONTENT_LENGTH = int(
        os.environ.get('MAX_CONTENT_LENGTH')) if os.environ.get(
        'MAX_CONTENT_LENGTH') is not None else 10485760
