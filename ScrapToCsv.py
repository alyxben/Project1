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
    :return:    category's url stored in category_urls dict
    """
    response = requests.get(base_url)
    if response.ok:
        category_urls = {}
        bookhtml = BeautifulSoup(response.text, features='html.parser')
        p = bookhtml.find_all('ul')[1]
        urls = p.find_all(href=True)
        urls = urls[1:]
        for url in urls:
            titre = url.text.strip()    #category title
            url = url['href']
            url = url.replace('index.html', '')
            category_urls[titre] = 'https://books.toscrape.com/' + url
    return category_urls


def get_book_urls(fullCategoryUrl):
    """
            Start request at the category url and parse through html to get each book urls
    :param fullCategoryUrl: base_url + category url
    :return: book's url stored in list
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
        while nextPage is not None:
            nextPageUrl = fullCategoryUrl + nextPage
            response = requests.get(nextPageUrl)
            bookHtml = BeautifulSoup(response.text, 'html.parser')
            p = bookHtml.findAll('h3')
            for url in p:
                url = url.find('a')
                url = url['href']
                book_urls.append('https://books.toscrape.com/catalogue/category/books' + url)
            try:
                nextPage = bookHtml.find(class_='next')
                nextPage = nextPage.find('a')['href']
            except:
                pass
    except:
        pass
    return book_urls


def get_book_items(book_url):
    """
            start request at book_url and parse through html page to get book info
    :param book_url:
    :return: Return book information stored in bookItems dict
    """
    response = requests.get(book_url)
    if response.ok:
        book_items = []
        bookhtml = BeautifulSoup(response.text, features='html.parser')  # Load HTML page in bookHTML
        product_page = bookhtml.find(class_='product_page')  # Load class 'product_page' in product_page
        image_url = bookhtml.find('img').attrs[
            'src']  # Load the src attribute that contains the short link of the image
        image_url = image_url[6:]
        image_url = base_url + image_url
        # print("image_url", image_url)
        tds = bookhtml.findAll('tr')
        for tr in tds:
            td = tr.find('td')  # Load all tr elements in td and add them
            book_items.append(td.text)  # to bookITEMS
        del book_items[1]  # Delete non needed elements of the list
        del book_items[5]
        del book_items[3]
        title = bookhtml.find('h1').text  # Load the h1 tag in title
        book_items.append(title)  # add it to bookItems
        book_items[1] = book_items[1][1:]  # Slice the first letter of the price excluding tax
        book_items[2] = book_items[2][1:]  # Slice the first letter of the price including tax
        category = bookhtml.findAll('li')[2].text.strip()
        book_items.append(category.strip())
        p = product_page.findAll('p')  # parse al p elements in product_page
        description = p[3]  # load product description in description
        rating = p[2]  # load rating
        rating = rating.attrs['class']
        rating = rating[1]
        book_items.append(description.text)
        book_items.append(rating)
        book_items.append(image_url)

        return {'link': book_url,
                'upc': book_items[0],
                'title': title,
                'price_including_tax': book_items[2],
                'price_excluding_tax': book_items[1],
                'Availability': book_items[3],
                'product_description': description,
                'category': category,
                'rating': rating,
                'image_url': image_url,
                }


def write_file_csv(book_items_list, category):
    """create a csv file named by the corresponding category and the book infos in it

    :param book_items_list: list of book_items
    :param category:
    :return:
    """
    with open(f'{category}.csv', 'w', newline='', encoding='iso-8859-1') as f:
        fieldnames = ['Universal_product_code', 'Price_no_tax', 'Price_with_tax', 'Stock', 'Title', 'Category',
                      'Description', 'Rating', 'Image_url', 'Book_url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for book_items in book_items_list:
            writer.writerow({
                fieldnames[0]: book_items['upc'],
                fieldnames[1]: book_items['price_excluding_tax'],
                fieldnames[2]: book_items['price_including_tax'],
                fieldnames[3]: book_items['Availability'],
                fieldnames[4]: book_items['title'],
                fieldnames[5]: book_items['category'],
                fieldnames[6]: book_items['product_description'],
                fieldnames[7]: book_items['rating'],
                fieldnames[8]: book_items['image_url'],
                fieldnames[9]: book_items['link']}
            )


def function_image(book_img_url, category):
    """ download and create a directory that will contain each book cover sorted by categories

    :param book_img_url:
    :param category:
    :return:
    """
    book_cover = 'Book_covers'
    path = f'{book_cover}/{category}'
    Path(path).mkdir(parents=True, exist_ok=True)
    wget.download(book_img_url, path, bar=None)


def info_from_category(links):
    """ get book info and download images all sorted by category

    :param links:   Book links
    :return: list of book info
    """
    infos = []
    for link in links:
        book_info = get_book_items(link)
        infos.append(book_info)
        function_image(book_info['image_url'], book_info['category'])
    return infos


if __name__ == '__main__':
    ## 
    categories = parse_categories_url(base_url)
    #print(categories)
    for categorie in categories.keys():
        links = get_book_urls(categories[categorie])    #Load book links by categories
        info = info_from_category(links)    #Load book info
        write_file_csv(info, categorie) #Generate csv file