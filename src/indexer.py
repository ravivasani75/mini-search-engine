import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import os
import json
import re
from collections import defaultdict
import sqlite3
import ssl
import math
import zlib

# Handle SSL certificate verification issues
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Initialize stop words and stemmer
stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()


def tokenize(text):
    # Tokenize and process text: lowercasing, removing stop words, and stemming
    tokens = re.findall(r"\b\w+\b", text.lower())
    filtered_tokens = [
        stemmer.stem(token) for token in tokens if token not in stop_words
    ]
    return filtered_tokens


def compress_term(term):
    # Compress the term using zlib for basic compression
    return zlib.compress(term.encode("utf-8"))


def decompress_term(compressed_term):
    # Decompress the term for lookup
    return zlib.decompress(compressed_term).decode("utf-8")


def build_index(data_directory, conn):
    doc_count = 0
    inverted_index = defaultdict(lambda: defaultdict(int))

    # Iterate over all JSON files in the data directory
    for filename in os.listdir(data_directory):
        if filename.endswith(".json"):
            filepath = os.path.join(data_directory, filename)
            with open(filepath, "r") as file:
                document = json.load(file)
                url = document["url"]
                content = document["content"]
                tokens = tokenize(content)
                doc_length = len(tokens)
                doc_count += 1

                # Count the frequency of each token
                for token in tokens:
                    compressed_token = compress_term(token)
                    inverted_index[compressed_token]["doc_freq"] += 1
                    inverted_index[compressed_token][url] += 1

                # Insert the document details into the database
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO documents (url, doc_length) VALUES (?, ?)",
                    (url, doc_length),
                )
                doc_id = cursor.lastrowid

    # Store or update the total document count for IDF calculation
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
        ("doc_count", doc_count),
    )
    conn.commit()

    # Calculate and store TF and IDF for each token in each document
    for compressed_token, data in inverted_index.items():
        doc_freq = data.pop("doc_freq")
        idf = max(math.log((doc_count + 1) / (1 + doc_freq)), 0)
        for url, tf_count in data.items():
            cursor.execute("SELECT id, doc_length FROM documents WHERE url=?", (url,))
            result = cursor.fetchone()
            if result:
                doc_id, doc_length = result
                tf = tf_count / doc_length if doc_length > 0 else 0
                cursor.execute(
                    "INSERT INTO inverted_index (token, doc_id, frequency, tf, idf) VALUES (?, ?, ?, ?, ?)",
                    (compressed_token, doc_id, tf_count, tf, idf),
                )

    conn.commit()


def save_index_sqlite(index, db_filepath):
    # Create or open the SQLite database
    conn = sqlite3.connect(db_filepath)

    # Create tables for storing the index and documents
    cursor = conn.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY,
        url TEXT NOT NULL,
        doc_length INTEGER NOT NULL
    )
    """
    )
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS inverted_index (
        id INTEGER PRIMARY KEY,
        token BLOB NOT NULL,  -- Store compressed tokens as BLOB
        doc_id INTEGER NOT NULL,
        frequency INTEGER NOT NULL,
        tf REAL NOT NULL,
        idf REAL NOT NULL,
        FOREIGN KEY (doc_id) REFERENCES documents (id)
    )
    """
    )
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS metadata (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """
    )

    conn.commit()

    return conn


if __name__ == "__main__":
    nltk.download("stopwords")  # Ensure stopwords are downloaded locally
    data_directory = "data"
    db_filepath = "inverted_index.db"
    conn = save_index_sqlite(None, db_filepath)
    build_index(data_directory, conn)
    conn.close()
    print(f"Inverted index with TF-IDF and compression saved to {db_filepath}")
