
# Mini Search Engine

## Project Overview
This project implements a mini search engine that crawls specified websites, indexes the content, and allows users to search through the content using a command-line interface. The search results are ranked based on TF-IDF (Term Frequency-Inverse Document Frequency) scores, which measure the relevance of documents to the search query.

## Features
- **Web Crawler**: A robust crawler that fetches and parses content from specified websites.
- **Text Processing**: Tokenization, stemming, and stop word removal to prepare the text for indexing.
- **Inverted Index**: Creation of an inverted index that maps terms to the documents in which they appear, along with their TF-IDF scores.
- **TF-IDF Ranking**: Documents are ranked based on their TF-IDF scores, which prioritize terms that are distinctive to fewer documents.
- **Boolean Search**: Support for Boolean operators (`AND`, `OR`, `NOT`) in search queries, with correct operator precedence.
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

### Instructions
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd mini-search-engine
   ```

2. **Set up a virtual environment** (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the web crawler** to fetch and parse content:
   ```bash
   python src/crawler.py
   ```

5. **Run the indexer** to build the inverted index and calculate TF-IDF scores:
   ```bash
   python src/indexer.py
   ```

6. **Search through the indexed data** using the command-line interface:
   ```bash
   python src/search.py
   ```

### Example Queries
- **Basic Search**: `python`
- **Boolean Search**: `python AND machine OR java AND NOT javascript`

## Future Enhancements
- **Phrase and Proximity Search**: Implement support for exact phrases and proximity-based searches.
- **Web Interface**: Develop a Flask-based web interface for more user-friendly search interactions.
- **Performance Optimization**: Implement index compression and parallel crawling to enhance performance.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Inspired by basic search engine concepts and TF-IDF implementations.
- NLTK library for natural language processing.
