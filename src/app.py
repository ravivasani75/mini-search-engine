
from flask import Flask, render_template, request
import sqlite3
from search import search_query

app = Flask(__name__)

def highlight_terms(text, terms):
    for term in terms:
        text = text.replace(term, f"<mark>{term}</mark>")
    return text

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    query = ""
    if request.method == "POST":
        query = request.form["query"]
        conn = sqlite3.connect("inverted_index.db")
        results = search_query(query, conn)
        conn.close()

        # Highlight the search terms in the results
        terms = query.lower().split()
        results = [(highlight_terms(url, terms), score) for url, score in results]

    return render_template("index.html", results=results, query=query)

if __name__ == "__main__":
    app.run(debug=True)
