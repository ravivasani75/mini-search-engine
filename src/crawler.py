import logging
import requests
from bs4 import BeautifulSoup
import json
import os
import time
import hashlib

# Setup logging
logging.basicConfig(
    filename="crawler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def fetch_content(url):
    try:
        response = requests.get(url, timeout=10)  # Added timeout
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve {url}: {e}")
        return None


def parse_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text()


def save_to_file(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def is_duplicate_content(content, seen_hashes):
    content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()
    if content_hash in seen_hashes:
        return True
    seen_hashes.add(content_hash)
    return False


if __name__ == "__main__":
    # Create data directory if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")

    # Read URLs from websites.txt
    with open("src/websites.txt", "r") as file:
        urls = file.read().splitlines()

    # Keep track of seen URLs and hashes to avoid duplicates
    seen_urls = set()
    seen_hashes = set()

    for url in urls:
        if url in seen_urls:
            logging.info(f"Skipping duplicate URL: {url}")
            continue
        seen_urls.add(url)

        content = fetch_content(url)
        if content:
            text = " ".join(parse_html(content).split())  # Cleaned content
            if is_duplicate_content(text, seen_hashes):
                logging.info(f"Skipping duplicate content from {url}")
                continue
            filename = f"data/{url.replace('https://', '').replace('http://', '').replace('/', '_')}.json"
            save_to_file({"url": url, "content": text}, filename)
            logging.info(f"Saved content from {url} to {filename}")
        time.sleep(1)  # Delay to respect server resources
