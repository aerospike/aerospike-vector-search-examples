from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)

# The image or text encoding model.
model = SentenceTransformer("clip-ViT-B-32")
MODEL_DIM = 512


def encoder(data):
    logger.debug(f"Encoding data {data}")
    return model.encode(data)
