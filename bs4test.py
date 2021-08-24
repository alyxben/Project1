import requests
from bs4 import BeautifulSoup

url = 'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'
response = requests.get(url)
if response.ok:
    bookItems = []
    bookHtml = BeautifulSoup(response.text, features='html.parser')             # Load HTML page in bookHTML
    tds = bookHtml.findAll('tr')
    for tr in tds:
        td = tr.find('td')                                                      # Load all tr elements in td and add them
        bookItems.append(td.text)                                               # to bookITEMS
    del bookItems[1]                                                            # Delete non needed elements of the list
    del bookItems[5]
    del bookItems[3]
    title = bookHtml.find('h1')                                                 # Load the h1 tag in title
    bookItems.append(title.text)                                                # add it to bookItems
    product_page = bookHtml.find(class_='product_page')                         # Load class 'product_page' in product_page
    p = product_page.findAll('p')                                               # parse al p elements in product_page
    description = p[3]                                                          # load product description in description
    rating = p[2]                                                               # load rating
    rating = rating.attrs['class']
    rating = rating[1]
    bookItems.append(description.text)                                           
    bookItems.append(rating)






    print(bookItems)




