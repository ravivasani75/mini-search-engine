import logging
import requests
from bs4 import BeautifulSoup
import json
import os
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse
import time
import random

# Setup logging
logging.basicConfig(
    filename="crawler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Configurable delay range between requests (in seconds)
REQUEST_DELAY_MIN = 1  # Minimum delay
REQUEST_DELAY_MAX = 3  # Maximum delay


def fetch_content(url):
    try:
        # Introduce a random delay between requests
        time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve {url}: {e}")
        return None


def parse_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup


def extract_links(soup, base_url):
    links = set()
    for link in soup.find_all("a", href=True):
        href = link.get("href")
        full_url = urljoin(base_url, href)
        if urlparse(full_url).scheme in ["http", "https"]:
            links.add(full_url)
    return links


def save_to_file(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def crawl(url, depth, max_depth, seen_urls):
    if depth > max_depth:
        logging.info(f"Maximum depth reached at {url}. Stopping crawl.")
        return set()

    if url in seen_urls:
        logging.info(f"Skipping duplicate URL: {url}")
        return set()
    seen_urls.add(url)

    content = fetch_content(url)
    if content:
        soup = parse_html(content)
        text = " ".join(soup.get_text().split())
        filename = f"data/{url.replace('https://', '').replace('http://', '').replace('/', '_')}.json"
        save_to_file({"url": url, "content": text}, filename)
        logging.info(f"Successfully crawled and saved content from {url}")

        if depth < max_depth:
            links = extract_links(soup, url)
            return links  # Return links to be crawled at the next depth level
    return set()


if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")

    with open("src/websites.txt", "r") as file:
        urls = file.read().splitlines()

    max_depth = 2  # Set the maximum crawl depth
    seen_urls = set()

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {
            executor.submit(crawl, url, 0, max_depth, seen_urls): url for url in urls
        }
        for depth in range(1, max_depth + 1):
            next_level_urls = set()
            for future in future_to_url:
                result = future.result()
                if result:
                    next_level_urls.update(result)
            if not next_level_urls:
                break
            future_to_url = {
                executor.submit(crawl, url, depth, max_depth, seen_urls): url
                for url in next_level_urls
            }
