import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import os
import json
import re
from collections import defaultdict
import sqlite3
import ssl

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


def build_index(data_directory, conn):
    inverted_index = defaultdict(list)
    doc_count = 0

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
                token_counts = defaultdict(int)

                # Count the frequency of each token
                for token in tokens:
                    token_counts[token] += 1

                # Insert the document details into the database
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO documents (url, doc_length) VALUES (?, ?)",
                    (url, doc_length),
                )
                doc_id = cursor.lastrowid

                # Update the inverted index
                for token, count in token_counts.items():
                    cursor.execute(
                        "INSERT INTO inverted_index (token, doc_id, frequency) VALUES (?, ?, ?)",
                        (token, doc_id, count),
                    )

    # Store or update the total document count for IDF calculation
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
        ("doc_count", doc_count),
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
        token TEXT NOT NULL,
        doc_id INTEGER NOT NULL,
        frequency INTEGER NOT NULL,
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
    print(f"Inverted index saved to {db_filepath}")
