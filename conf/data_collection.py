import requests
from bs4 import BeautifulSoup
import random
import time
from .utils import select_proxy, read_proxies_from_file, update_proxies_if_needed

def google_scholar_search(query, num_results, proxies):
    results = []
    num_pages = num_results // 10 + (num_results % 10 > 0)
    total_attempts = 0
    max_attempts = 3  # Maximum attempts across all pages

    for page in range(num_pages):
        if total_attempts >= max_attempts:
            print("Too many failed attempts, stopping Google Scholar search.")
            break

        start = page * 10
        url = f"https://scholar.google.com/scholar?q={query}&start={start}"
        for attempt in range(3):  # Try up to 3 times per page
            print(f"Fetching URL: {url} with proxy {proxies}")  # Debugging line
            response = requests.get(url, proxies=proxies)
            if response.status_code == 429:  # Too many requests
                print("Too many requests, changing proxy...")
                proxies = select_proxy(read_proxies_from_file('proxies.txt'))
                time.sleep(5)
                continue
            elif response.status_code != 200:
                print(f"Failed to fetch URL: {url} with status code: {response.status_code}")
                break
            else:
                break
        else:
            print("Failed to fetch URL after 3 attempts")
            total_attempts += 1
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('div', class_='gs_ri')
        
        for article in articles:
            title = article.find('h3').text if article.find('h3') else 'No title'
            link = article.find('a')['href'] if article.find('a') else 'No link'
            summary = article.find('div', class_='gs_rs').text if article.find('div', class_='gs_rs') else 'No summary'
            results.append({'title': title, 'link': link, 'summary': summary})
        
        print(f"Found {len(articles)} articles on page {page + 1}")  # Debugging line

        if len(articles) == 0:
            break

    return results

def semantic_scholar_search(query, num_results, api_key):
    headers = {
        "x-api-key": api_key
    }
    results = []
    offset = 0
    while len(results) < num_results:
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&offset={offset}&limit=10&fields=title,url,abstract"
        print(f"Fetching URL: {url}")  # Debugging line
        response = requests.get(url, headers=headers)
        if response.status_code == 403:  # Forbidden
            print(f"Failed to fetch URL: {url} with status code: {response.status_code}")
            break
        data = response.json()
        for article in data.get('data', []):
            title = article.get('title', 'No title')
            summary = article.get('abstract', 'No summary')
            results.append({
                'title': title,
                'link': article.get('url', 'No link'),
                'summary': summary
            })
        print(f"Found {len(data.get('data', []))} articles")  # Debugging line
        if not data.get('data', []):
            break
        offset += 10
    return results[:num_results]

def collect_data(queries, num_results, api_key):
    all_articles = []
    proxies = read_proxies_from_file('proxies.txt')
    selected_proxy = select_proxy(proxies)
    for lang, query in queries.items():
        print(f"Collecting articles for query: {query} in {lang}")
        gs_articles = google_scholar_search(query, num_results, selected_proxy)
        print(f"Collected {len(gs_articles)} articles from Google Scholar for query: {query} in {lang}")
        ss_articles = semantic_scholar_search(query, num_results, api_key)
        print(f"Collected {len(ss_articles)} articles from Semantic Scholar for query: {query} in {lang}")
        articles = gs_articles + ss_articles
        for article in articles:
            article['language'] = lang
        all_articles.extend(articles)
        print(f"Collected {len(articles)} articles for query: {query} in {lang}")
    return all_articles
