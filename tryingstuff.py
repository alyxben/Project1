##TEST FOR CATEGORIES

import requests
from bs4 import BeautifulSoup

base_url = 'https://books.toscrape.com/catalogue/category/books/travel_2/index.html'
response = requests.get(base_url)
if response.ok:
    book_urls = []
    bookHtml = BeautifulSoup(response.text, features='html.parser')
    p = bookHtml.find_all('h3')
    for url in p:
        url = url.find_all('a')
        book_urls.append(url)
        print(book_urls)
