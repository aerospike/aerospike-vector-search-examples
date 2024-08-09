"""
pre-embed.py - This script reads the quotes.csv dataset file and embeds the quotes using the sentence-transformers/all-MiniLM-L6-v2 model. The quotes and embeddings are then saved to quote-embeddings.csv.
"""

from sentence_transformers import SentenceTransformer
import csv
import itertools
import os
import logging
import tarfile

logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)

# The image or text encoding model.
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
MODEL_DIM = 384


def encoder(data):
    logger.debug(f"Encoding data {data}")
    return model.encode(data)


def read_csv(filename):
    if not os.path.exists(filename) and os.path.exists(filename + ".tgz"):
        # Untar the file
        with tarfile.open(filename + ".tgz", "r:gz") as tar:
            tar.extractall(path=os.path.dirname(filename))

    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header
        for row in reader:
            yield row


DATASET_FILE = "./quotes.csv"
dataset = itertools.islice(read_csv(DATASET_FILE), 10000)


def embed_quote(quote):
    quote, author, catagory = quote
    doc = {}
    doc["quote"] = quote
    doc["author"] = author
    doc["tags"] = catagory.split(",")

    text = quote + " ".join(doc["tags"])
    embedding = encoder(text)
    return embedding


OUTPUT_FILE = "./quote-embeddings.csv"

if __name__ == "__main__":
    with open(OUTPUT_FILE, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["quote", "author", "tags", "quote_embedding_ndarray"])
        for quote in dataset:
            quote_embedding = embed_quote(quote)
            breakpoint()
            quote.append(quote_embedding.tobytes())
            writer.writerow(quote)
