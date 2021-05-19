import requests
from bs4 import BeautifulSoup


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
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text()


if __name__ == "__main__":
    with open("src/websites.txt", "r") as file:
        urls = file.read().splitlines()

    for url in urls:
        content = fetch_content(url)
        if content:
            text = parse_html(content)
            print(f"Content from {url}:")
            print(text[:500])  # Print the first 500 characters
