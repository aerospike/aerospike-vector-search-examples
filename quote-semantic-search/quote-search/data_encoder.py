from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)

# The image or text encoding model.
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
MODEL_DIM = 384


def encoder(data):
    logger.debug(f"Encoding data {data}")
    return model.encode(data)
