import requests
from bs4 import BeautifulSoup
import csv
import wget
from pathlib import Path
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

base_url = 'https://books.toscrape.com/'


def parse_categories_url(base_url):
    """
        Start request at base url and parse through html code to get categories url
    :param base_url: link of the website
    :return:    category's shortlink url stored in category_urls list
    """
    response = requests.get(base_url)
    if response.ok:
        category_urls = []
        bookhtml = BeautifulSoup(response.text, features='html.parser')
        p = bookhtml.find_all('ul')[1]
        urls = p.find_all(href=True)
        urls = urls[1:]
        for url in urls:
            url = url['href']
            url = url.replace('index.html', '')
            category_urls.append('https://books.toscrape.com/' + url)
    return category_urls


def get_book_urls(fullCategoryUrl):
    """
            Start request at the category url and parse through html to get each book urls
    :param fullCategoryUrl: base_url + category url
    :return: book's shortlink url
    """

    response = requests.get(fullCategoryUrl)
    if response.ok:
        book_urls = []
        bookHtml = BeautifulSoup(response.text, 'html.parser')
        p = bookHtml.findAll('h3')
        for url in p:
            url = url.find('a')
            url = url['href']
            book_urls.append('https://books.toscrape.com/catalogue/category/books' + url)
    try:
        nextPage = bookHtml.find(class_='next')
        nextPage = nextPage.find('a')['href']
        if nextPage is not None:
            nextPageUrl = fullCategoryUrl + nextPage
            response = requests.get(nextPageUrl)
            bookHtml = BeautifulSoup(response.text, 'html.parser')
            p = bookHtml.findAll('h3')
            for url in p:
                url = url.find('a')
                url = url['href']
                book_urls.append('https://books.toscrape.com/catalogue/category/books' + url)
    except:
        pass
    return book_urls


def get_book_items(book_url):
    """
            start request at book_url and parse through html page to get book info
    :param book_url:
    :return: Return book information stored in bookItems
    """
    response = requests.get(book_url)
    if response.ok:
        book_Items = []
        bookhtml = BeautifulSoup(response.text, features='html.parser')  # Load HTML page in bookHTML
        product_page = bookhtml.find(class_='product_page')  # Load class 'product_page' in product_page
        image_url = bookhtml.find('img').attrs['src']  # Load the src attribute that contains the short link of the image
        image_url = image_url[6:]
        image_url = base_url + image_url
        tds = bookhtml.findAll('tr')
        for tr in tds:
            td = tr.find('td')  # Load all tr elements in td and add them
            book_Items.append(td.text)  # to bookITEMS
        del book_Items[1]  # Delete non needed elements of the list
        del book_Items[5]
        del book_Items[3]
        title = bookhtml.find('h1').text  # Load the h1 tag in title
        book_Items.append(title)  # add it to bookItems
        book_Items[1] = book_Items[1][1:]  # Slice the first letter of the price excluding tax
        book_Items[2] = book_Items[2][1:]  # Slice the first letter of the price including tax
        category = bookhtml.findAll('li')[2].text
        book_Items.append(category.strip())
        p = product_page.findAll('p')  # parse al p elements in product_page
        description = p[3]  # load product description in description
        rating = p[2]  # load rating
        rating = rating.attrs['class']
        rating = rating[1]
        book_Items.append(description.text)
        book_Items.append(rating)
        book_Items.append(image_url)
        #image_data = wget.download(image_url)

        return book_Items

def write_file_csv(category, book_items_list):
    with open(category + '.csv','w+') as f:
        fieldnames = ['Universal_product_code','Price_no_tax','Price_with_tax','Stock','Title','Category','Description','Rating','Image_url','Book_url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for book_items in book_items_list:
            writer.writerow({fieldnames[0]:book_items[0],
                              fieldnames[1]:book_items[1],
                              fieldnames[2]:book_items[2],
                              fieldnames[3]:book_items[3],
                              fieldnames[4]:book_items[4],
                              fieldnames[5]:book_items[5],
                              fieldnames[6]:book_items[6],
                              fieldnames[7]:book_items[7],
                              fieldnames[8]:book_items[8],
                              fieldnames[9]:book_items[9]})

def function_image(book_img_url, category):
    book_cover = 'Book_covers'
    path = f'{book_cover}/{category}'
    Path(path).mkdir(parents=True, exist_ok=True)
    wget.download(book_img_url, path, bar=None)



categoryLinks = parse_categories_url(base_url)
book_urls = []
n = 0
for link in categoryLinks:
    booklinks = get_book_urls(link)
    book_urls.append(booklinks)
for l in book_urls:
    print('NEW CATEGORY !!!')
    print(l)
    book_items_list = []
    category = str()
    for url in l:
        book_items = get_book_items(url)
        book_items.append(url)
        category = book_items[5]
        image_url = book_items[8]
        #function_image(image_url, category)
        book_items_list.append(book_items)
    write_file_csv(category, book_items_list)
