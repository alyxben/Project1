##TEST FOR CATEGORIES

import requests
from bs4 import BeautifulSoup

base_url = 'https://books.toscrape.com/catalogue/category/books/travel_2/index.html'
response = requests.get(base_url)
if response.ok:
    book_urls = []
    bookHtml = BeautifulSoup(response.text, 'html.parser')
    p = bookHtml.findAll('h3')
    for url in p:
        url = url.find('a')
        url = url['href']
        # print("=========",url)
        book_urls.append(url)
    print(book_urls)

# J'ai toucher le code tout est ok, franchement je ne sais pas ou se trouvait l'erreur. 
# Surement tu as oubilé de pusher la bonne version sur git.