import requests
from bs4 import BeautifulSoup
import csv

base_url = 'https://books.toscrape.com/'
bookLink = 'catalogue/a-light-in-the-attic_1000/index.html'
book_url = base_url + bookLink


def parse_categories_url(base_url):
    """
    :param base_url: 
    :return: 
    """
    response = requests.get(base_url)
    if response.ok:
        category_url = []
        bookhtml = BeautifulSoup(response.text, features='html.parser')
        p = bookhtml.find_all('ul')[1]
        urls = p.find_all(href=True)
        urls = urls[1:]
        for url in urls:
            url = url.attrs
            category_url.append(list(url.values()))
    return category_url


urllist = parse_categories_url(base_url)
print(urllist)


def get_book_items(book_url):
    """

    :param book_url:
    :return:
    """
    response = requests.get(book_url)
    if response.ok:
        bookItems = []
        bookhtml = BeautifulSoup(response.text, features='html.parser')  # Load HTML page in bookHTML
        product_page = bookhtml.find(class_='product_page')  # Load class 'product_page' in product_page
        image_url = bookhtml.find('img').attrs[
            'src']  # Load the src attribute that contains the short link of the image
        image_url = image_url[6:]
        tds = bookhtml.findAll('tr')
        for tr in tds:
            td = tr.find('td')  # Load all tr elements in td and add them
            bookItems.append(td.text)  # to bookITEMS
        del bookItems[1]  # Delete non needed elements of the list
        del bookItems[5]
        del bookItems[3]
        title = bookhtml.find('h1').text  # Load the h1 tag in title
        bookItems.append(title)  # add it to bookItems
        bookItems[1] = bookItems[1][1:]  # Slice the first letter of the price excluding tax
        bookItems[2] = bookItems[2][1:]  # Slice the first letter of the price including tax
        category = bookhtml.findAll('li')[2].text
        bookItems.append(category.strip())
        p = product_page.findAll('p')  # parse al p elements in product_page
        description = p[3]  # load product description in description
        rating = p[2]  # load rating
        rating = rating.attrs['class']
        rating = rating[1]
        bookItems.append(description.text)
        bookItems.append(rating)
        bookItems.append(image_url)
        return bookItems

book_items = get_book_items(book_url)
print(book_items)

with open('test.csv','w') as f:
    writefile = csv.writer(f)
    writefile.writerow(book_items)