from bs4 import BeautifulSoup
import csv
import requests
import urllib
import pyodbc

connection = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'       
                            'Server=.;'
                            'DataBase=AmazonScrapper;'
                            'Trusted_Connection=Yes;')

cursor = connection.cursor()

if cursor.tables(table='products',tableType='TABLE').fetchone():
    print('Product table already present')
else:
    print('Table not present.......Creating a new one')
    cursor.execute('''create table products(product_name VARCHAR(255),
                                            product_id VARCHAR(255),
                                            price VARCHAR(255),
                                            sponsor  VARCHAR(255),
                                            average_rating VARCHAR(255),
                                            review_count VARCHAR(255),)''')
    connection.commit()

query = input('Enter the product to be search:')
query_params = {'page':1,'k':query}
params = urllib.parse.urlencode(query_params)

url = 'https://www.amazon.com/s?' + params

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
    'referer': 'https://www.amazon.com/',
    'Cookie': 'session-id=147-7595926-6084643; session-id-time=2082787201l; i18n-prefs=USD; ubid-main=135-7434178-2212849; session-token=S43Sg870C24tsxUR1cKDU+thNpCZD4dXDjHDVM4/6Pkwd8jWK5BveIUmE21RxbbdQ0br4QRB8e2UUJvXbGzOsF2QiYmXnn+wy+50g6gqmlaY1wehEc+CjK6Ing8wibD2KDezZkbt3giTkqXeKNVhE11J9+GukuzfnC1Fsnf1jXlnalKWRwfgJckTB8+tjf1GwXk3RLs3GWu9cc4Fo6gqtj6F4EKeuGUXtnKErjkDEdChQrKnKfGI8xaGX3SIejwS'

}
response = requests.get(url,headers= headers,verify=True)
soup = BeautifulSoup(response.text,'lxml')

products = soup.findAll('div',attrs={'data-component-type':"s-search-result"})
print('Total products:',len(products))

product_detail_class = "a-link-normal a-text-normal"

def get_product_details(url):
    response = requests.get(url,headers=headers,verify=True)
    product_soup = BeautifulSoup(response.text,'lxml')

    price = product_soup.find('span',id="priceblock_ourprice")
    price_value = price.get_text() if(price!=None) else ''

    average_rating = product_soup.find('span',class_="a-icon-alt")
    average_rating_value = average_rating.get_text() if(average_rating!=None) else ''

    review_count = product_soup.find('span',id="acrCustomerReviewText")
    review_count_value = review_count.get_text() if(review_count!=None) else ''

    product_detail_array = [price_value,average_rating_value,review_count_value]

    return product_detail_array

with open('new_file.csv','w',newline='', encoding="utf-8")as my_csv:
    csv_columns = ['Product Name','Product ID','Price','Sponsor','Average Rating','Review Count']
    
    csv_writer = csv.DictWriter(my_csv,fieldnames=csv_columns)
    csv_writer.writeheader()

    for product in products:
        detail = product.find('a',class_="a-link-normal a-text-normal")
        title = detail.get_text().strip('\n')
        asin = product['data-asin']
        href = detail['href']

        sponsor_details = product.find('span',class_="a-size-mini a-color-secondary")
        # print(type(sponsor_details.get_text()))
        sponsor_value = 'yes' if(sponsor_details!=None) else 'No'


        url = 'https://www.amazon.com'+href
    
        product_array = get_product_details(url)
        
        csv_writer.writerow({'Product Name':title,
                                'Product ID':asin,
                                'Price':product_array[0],
                                'Sponsor':sponsor_value,
                                'Average Rating':product_array[1],
                                'Review Count':product_array[2]})

        cursor.execute('''insert into products(product_name, product_id, price, sponsor, average_rating, review_count)
                            values(?,?,?,?,?,?)''',title, asin, product_array[0],sponsor_value, product_array[1], product_array[2])
        

connection.commit()
connection.close()