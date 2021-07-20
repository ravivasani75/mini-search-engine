import logging
import aiohttp
import asyncio
import aiofiles
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin, urlparse
import random

# Setup logging
logging.basicConfig(
    filename="crawler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Configurable delay range between requests (in seconds)
REQUEST_DELAY_MIN = 1
REQUEST_DELAY_MAX = 3

# Semaphore to limit the number of concurrent tasks
semaphore = asyncio.Semaphore(100)


async def fetch_content(session, url):
    try:
        await asyncio.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))
        async with session.get(url, timeout=10) as response:
            response.raise_for_status()
            return await response.text()
    except aiohttp.ClientError as e:
        logging.error(f"Failed to retrieve {url}: {e}")
        return None


def parse_html(html_content):
    return BeautifulSoup(html_content, "html.parser")


def extract_links(soup, base_url):
    links = set()
    for link in soup.find_all("a", href=True):
        href = link.get("href")
        full_url = urljoin(base_url, href)
        if urlparse(full_url).scheme in ["http", "https"]:
            links.add(full_url)
    return links


async def save_to_file(data, filename):
    async with aiofiles.open(filename, "w") as f:
        await f.write(json.dumps(data, indent=4))


async def crawl(session, url, depth, max_depth, seen_urls):
    async with semaphore:
        if depth > max_depth:
            logging.info(f"Maximum depth reached at {url}. Stopping crawl.")
            return set()

        if url in seen_urls:
            logging.info(f"Skipping duplicate URL: {url}")
            return set()
        seen_urls.add(url)

        content = await fetch_content(session, url)
        if content:
            soup = parse_html(content)
            text = " ".join(soup.get_text().split())
            filename = f"data/{url.replace('https://', '').replace('http://', '').replace('/', '_')}.json"
            await save_to_file({"url": url, "content": text}, filename)
            logging.info(f"Successfully crawled and saved content from {url}")

            if depth < max_depth:
                links = extract_links(soup, url)
                return links
        return set()


async def process_links(session, depth, max_depth, urls, seen_urls):
    tasks = [crawl(session, url, depth, max_depth, seen_urls) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    next_level_urls = set()
    for result in results:
        if isinstance(result, set):
            next_level_urls.update(result)

    return next_level_urls


async def main(urls, max_depth):
    seen_urls = set()
    async with aiohttp.ClientSession() as session:
        next_level_urls = await process_links(session, 0, max_depth, urls, seen_urls)

        for depth in range(1, max_depth + 1):
            if not next_level_urls:
                break
            next_level_urls = await process_links(
                session, depth, max_depth, next_level_urls, seen_urls
            )


if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")

    with open("src/websites.txt", "r") as file:
        urls = file.read().splitlines()

    max_depth = 2  # Set the maximum crawl depth

    # Explicitly creating the event loop and using it to run the main coroutine
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main(urls, max_depth))
    finally:
        loop.close()
