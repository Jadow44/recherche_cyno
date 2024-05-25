import requests
from bs4 import BeautifulSoup
import random
import os
from datetime import datetime, timedelta

def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    proxies = []
    for row in soup.find('table', {'id': 'proxylisttable'}).tbody.find_all('tr'):
        if row.find_all('td')[4].text == 'elite proxy' and row.find_all('td')[6].text == 'yes':
            proxies.append(f"{row.find_all('td')[0].text}:{row.find_all('td')[1].text}")
    return proxies

def read_proxies_from_file(proxy_file):
    with open(proxy_file, 'r') as f:
        proxies = f.read().splitlines()
    return proxies

def select_proxy(proxies):
    if not proxies:
        raise ValueError("No proxies available.")
    return {'http': f'http://{random.choice(proxies)}'}

def update_proxies_if_needed():
    proxy_file = 'proxies.txt'
    if not os.path.exists(proxy_file):
        print("Proxy file not found, creating new one.")
        proxies = get_proxies()
        if proxies:
            with open(proxy_file, 'w') as f:
                for proxy in proxies:
                    f.write(f"{proxy}\n")
            print(f"Saved {len(proxies)} proxies to file.")
        else:
            print("No proxies available to save.")
        return

    last_modified_time = datetime.fromtimestamp(os.path.getmtime(proxy_file))
    if datetime.now() - last_modified_time > timedelta(weeks=1):
        print("Proxy file is outdated, updating.")
        proxies = get_proxies()
        if proxies:
            with open(proxy_file, 'w') as f:
                for proxy in proxies, f.write(f"{proxy}\n")
            print(f"Updated and saved {len(proxies)} proxies to file.")
        else:
            print("No proxies available to save.")
    else:
        print("Proxy file is up to date.")
