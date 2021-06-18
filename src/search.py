import sqlite3
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
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


def search_query(query, conn):
    tokens = tokenize(query)
    results = {}

    cursor = conn.cursor()

    for token in tokens:
        cursor.execute(
            """
        SELECT documents.url, inverted_index.tf, inverted_index.idf, inverted_index.tf * inverted_index.idf AS tfidf
        FROM inverted_index
        JOIN documents ON inverted_index.doc_id = documents.id
        WHERE inverted_index.token = ?
        ORDER BY tfidf DESC
        """,
            (token,),
        )

        for row in cursor.fetchall():
            url = row[0]
            tfidf_score = (
                row[3] if row[3] is not None else 0
            )  # Handle NoneType by assigning a score of 0
            if url in results:
                results[url] += tfidf_score
            else:
                results[url] = tfidf_score

    # Sort results by score in descending order
    sorted_results = sorted(results.items(), key=lambda item: item[1], reverse=True)
    return sorted_results


if __name__ == "__main__":
    nltk.download("stopwords")  # Ensure stopwords are downloaded locally

    # Connect to the SQLite database
    db_filepath = "inverted_index.db"
    conn = sqlite3.connect(db_filepath)

    # Input search query from user
    query = input("Enter your search query: ")
    results = search_query(query, conn)

    # Display the results
    print("Search Results:")
    for url, score in results:
        print(f"URL: {url}, Score: {score}")

    conn.close()
