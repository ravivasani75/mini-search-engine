
# Mini Search Engine

## Project Overview

The Mini Search Engine is a Python-based project designed to crawl a set of predefined websites, parse the content, and store it in a structured format. The ultimate goal is to build a search engine that can index and search through the collected data.

### Features
- **Web Crawling:** Fetch HTML content from specified URLs.
- **Content Parsing:** Extract raw text from HTML using BeautifulSoup.
- **Data Storage:** Save parsed content as JSON files for easy indexing and retrieval.

## Project Structure

```
mini-search-engine/
│
├── data/                     # Directory where JSON files will be stored
│   └── example-blog_com.json  # Example of a saved JSON file
│
├── docs/                     # Directory for documentation
│
├── src/
│   ├── crawler.py            # The web crawler script
│   └── websites.txt          # List of URLs to crawl
│
├── tests/                    # Directory for unit/integration tests
│
├── .gitignore                # Python .gitignore file
├── README.md                 # Project overview
└── requirements.txt          # List of dependencies
```

## Setup Instructions

1. **Clone the Repository:**
   ```bash
   git clone git@github.com:yourusername/mini-search-engine.git
   cd mini-search-engine
   ```

2. **Set Up the Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## How to Use

1. **Specify Websites to Crawl:**
   - Add or modify URLs in the `src/websites.txt` file.

2. **Run the Web Crawler:**
   ```bash
   python src/crawler.py
   ```

3. **Output:**
   - The crawled and parsed content will be saved as JSON files in the `data/` directory.

## Next Steps

- Implement an indexing system to enable searching through the stored content.
- Add more robust error handling and edge case management for the web crawler.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
