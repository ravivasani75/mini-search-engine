
# Mini Search Engine


## Project Overview
This project implements a mini search engine that crawls specified websites, indexes the content, and allows users to search through the content using both a command-line interface and a web-based interface. The search results are ranked based on TF-IDF (Term Frequency-Inverse Document Frequency) scores, which measure the relevance of documents to the search query. Additionally, search terms are now highlighted in the results to enhance readability.
## Features
- **Web Crawler**: A robust crawler that fetches and parses content from specified websites.
- **Text Processing**: Tokenization, stemming, and stop word removal to prepare the text for indexing.
- **Inverted Index**: Creation of an inverted index that maps terms to the documents in which they appear, along with their TF-IDF scores.
- **TF-IDF Ranking**: Documents are ranked based on their TF-IDF scores, which prioritize terms that are distinctive to fewer documents.
- **Boolean Search**: Support for Boolean operators (`AND`, `OR`, `NOT`) in search queries, with correct operator precedence.
- **Web-Based User Interface**: A Flask-based web interface for querying and displaying search results.
- **Result Highlighting**: Search terms are highlighted in the web interface results for easier readability.

- **Search Interface**: A command-line interface that allows users to input search queries and retrieve ranked results based on TF-IDF ranking.

## Project Structure
- `crawler.py`: The script responsible for crawling specified websites and extracting text content.
- `indexer.py`: The script that processes the crawled data, builds the inverted index, and calculates TF-IDF scores.
- `search.py`: The script that allows users to search through the indexed data and retrieve results based on Boolean logic and TF-IDF ranking.

## How It Works

### 1. Web Crawler (`crawler.py`)
- Fetches content from the URLs listed in `websites.txt`.
- Parses the HTML content to extract the text.
- Stores the extracted content in JSON format.

### 2. Indexing and TF-IDF Calculation (`indexer.py`)
- Processes the crawled text, tokenizing it into individual words.
- Applies stemming and stop word removal.
- Builds an inverted index, mapping each term to the documents where it appears.
- Calculates TF-IDF scores for each term in each document to determine its relevance.

### 3. Boolean Search and Interface (`search.py`)
- Accepts a user’s search query through the command line.
- Supports Boolean operators (`AND`, `OR`, `NOT`) with correct precedence handling (`NOT > AND > OR`).
- Tokenizes and processes the query using the same methods as in `indexer.py`.
- Retrieves relevant documents from the SQLite database and ranks them using TF-IDF scores.
- Displays the top-ranked results to the user.

## Installation and Setup

### Requirements
- Python 3.x
- Required Python packages (listed in `requirements.txt`):
  - `nltk`
  - `requests`
  - `beautifulsoup4`
  - `Flask`

#

## Instructions

This project provides a mini search engine with both command-line and web-based interfaces. Follow the steps below to set up and use the project:

### 1. Install Dependencies

Ensure you have Python installed on your system. Install the required dependencies by running:

```bash
pip install -r requirements.txt
```

### 2. Run the Web Crawler

Use the `crawler.py` script to crawl websites listed in the `websites.txt` file:

```bash
python crawler.py
```

This script will fetch the content from the URLs and store the crawled data in the `data` directory as JSON files.

### 3. Run the Indexer

After crawling, index the data using the `indexer.py` script:

```bash
python indexer.py
```

This script processes the crawled data, builds an inverted index, and calculates TF-IDF scores. The results are stored in an SQLite database (`inverted_index.db`).

### 4. Search the Data

#### Command-Line Interface:

You can perform searches directly from the command line using the `search.py` script. This script supports Boolean queries (e.g., `python AND not java`) and returns ranked results based on TF-IDF scores.

```bash
python search.py
```

Follow the on-screen instructions to input your search query.

#### Web-Based Interface:

Alternatively, you can use the web-based interface provided by the Flask application. To start the web interface, run:

```bash
python app.py
```

Open your web browser and navigate to `http://127.0.0.1:5000/` to access the search page. Enter your query in the search box and press "Search." The search results will be displayed with the matching terms highlighted for easy identification.

