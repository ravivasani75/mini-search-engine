import sqlite3
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import ssl
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


def apply_not_logic(results, not_terms, cursor):
    for term in not_terms:
        not_tokens = tokenize(term)
        for token in not_tokens:
            compressed_token = compress_term(token)
            cursor.execute(
                """
            SELECT documents.url FROM inverted_index
            JOIN documents ON inverted_index.doc_id = documents.id
            WHERE inverted_index.token = ?
            """,
                (compressed_token,),
            )
            for row in cursor.fetchall():
                url = row[0]
                if url in results:
                    del results[url]
    return results


def apply_and_logic(and_queries, cursor):
    results = None
    for subquery in and_queries:
        sub_results = search_subquery(subquery, cursor)
        if results is None:
            results = sub_results
        else:
            results = {
                url: results[url] + sub_results.get(url, 0)
                for url in results
                if url in sub_results
            }
    return results


def apply_or_logic(or_queries, cursor):
    results = {}
    for subquery in or_queries:
        sub_results = search_subquery(subquery, cursor)
        for url, score in sub_results.items():
            if url in results:
                results[url] += score
            else:
                results[url] = score
    return results


def search_subquery(query, cursor):
    if " not " in query:
        positive_part, negative_part = query.split(" not ", 1)
        positive_tokens = tokenize(positive_part)
        negative_tokens = tokenize(negative_part)

        results = {}
        for token in positive_tokens:
            compressed_token = compress_term(token)
            cursor.execute(
                """
            SELECT documents.url, inverted_index.tf, inverted_index.idf, inverted_index.tf * inverted_index.idf AS tfidf
            FROM inverted_index
            JOIN documents ON inverted_index.doc_id = documents.id
            WHERE inverted_index.token = ?
            ORDER BY tfidf DESC
            """,
                (compressed_token,),
            )
            for row in cursor.fetchall():
                url = row[0]
                tfidf_score = row[3] if row[3] is not None else 0
                if url in results:
                    results[url] += tfidf_score
                else:
                    results[url] = tfidf_score

        results = apply_not_logic(results, [negative_part], cursor)

    elif query.startswith("not "):
        # Handle standalone NOT queries
        not_terms = query.split("not ", 1)[1].strip()
        results = {row[0]: 0 for row in cursor.execute("SELECT url FROM documents")}
        results = apply_not_logic(results, [not_terms], cursor)

    else:
        results = {}
        tokens = tokenize(query)
        for token in tokens:
            compressed_token = compress_term(token)
            cursor.execute(
                """
            SELECT documents.url, inverted_index.tf, inverted_index.idf, inverted_index.tf * inverted_index.idf AS tfidf
            FROM inverted_index
            JOIN documents ON inverted_index.doc_id = documents.id
            WHERE inverted_index.token = ?
            ORDER BY tfidf DESC
            """,
                (compressed_token,),
            )
            for row in cursor.fetchall():
                url = row[0]
                tfidf_score = row[3] if row[3] is not None else 0
                if url in results:
                    results[url] += tfidf_score
                else:
                    results[url] = tfidf_score

    return results


def search_query(query, conn):
    cursor = conn.cursor()

    # Break the query into parts by AND, then further by OR
    and_parts = [part.strip() for part in query.lower().split(" and ")]
    or_parts = [part.split(" or ") for part in and_parts]

    # Process each OR group
    combined_results = None
    for or_group in or_parts:
        or_results = apply_or_logic(or_group, cursor)
        if combined_results is None:
            combined_results = or_results
        else:
            combined_results = {
                url: combined_results.get(url, 0) + or_results.get(url, 0)
                for url in combined_results
                if url in or_results
            }

    # Sort results by score in descending order
    sorted_results = (
        sorted(combined_results.items(), key=lambda item: item[1], reverse=True)
        if combined_results
        else []
    )
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
    if results:
        for url, score in results:
            print(f"URL: {url}, Score: {score}")
    else:
        print("No results found.")

    conn.close()
