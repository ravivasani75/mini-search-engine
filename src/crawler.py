import requests
from bs4 import BeautifulSoup
import json
import os

def fetch_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to retrieve {url} with status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    return None

def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()

def save_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')

    # Read URLs from websites.txt
    with open('src/websites.txt', 'r') as file:
        urls = file.read().splitlines()

    # Crawl each URL, parse content, and save to file
    for url in urls:
        content = fetch_content(url)
        if content:
            text = parse_html(content)
            filename = f"data/{url.replace('https://', '').replace('http://', '').replace('/', '_')}.json"
            save_to_file({"url": url, "content": text}, filename)
            print(f"Saved content from {url} to {filename}")
