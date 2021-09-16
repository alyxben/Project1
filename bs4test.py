import requests
from bs4 import BeautifulSoup
import csv
import path
import wget


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
            category_urls.append(url)
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
            book_urls.append('https://books.toscrape.com/catalogue/' + url)
    try:
        nextPage = bookHtml.find(class_='next')
        nextPage = nextPage.find('a')['href']
        if nextPage is not None:
            nextPageUrl = base_url + nextPage
            response = requests.get(nextPageUrl)
            bookHtml = BeautifulSoup(response.text, 'html.parser')
            p = bookHtml.findAll('h3')
            for url in p:
                url = url.find('a')
                url = url['href']
                book_urls.append('https://books.toscrape.com/catalogue/' + url)
    except:
        pass
    # print(book_urls)
    return book_urls


def get_book_items(book_url):
    """
            start request at book_url and parse through html page to get book info
    :param book_url:
    :return: Return book information stored in bookItems
    """
    response = requests.get(book_url)
    if response.ok:
        bookItems = []
        bookhtml = BeautifulSoup(response.text, features='html.parser')  # Load HTML page in bookHTML
        product_page = bookhtml.find(class_='product_page')  # Load class 'product_page' in product_page
        image_url = bookhtml.find('img').attrs['src']  # Load the src attribute that contains the short link of the image
        image_url = image_url[6:]
        image_url = base_url + image_url
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
        img_data = wget.download(image_url)
        with open('image.jpg', 'wb') as handler:
            handler.write(img_data)

        return bookItems


bookUrls = []
fullCategoryUrl = []
categoryLinks = parse_categories_url(base_url)
for url in categoryLinks:
    fullCategoryUrl.append(base_url + url)



for link in fullCategoryUrl:
    bookLinks = get_book_urls(link)
    bookUrls.append(base_url + link)
print("Les livres===",bookLinks)

# book_items = get_book_items(book_url)
# print(book_items)

# with open('test.csv', 'w') as f:
# writefile = csv.writer(f)
# writefile.writerow(book_items)
