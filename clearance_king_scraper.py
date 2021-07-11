import requests
import re
import random
import pandas as pd
import time
from bs4 import BeautifulSoup
from math import ceil
from tqdm import tqdm
from user_agents import user_agent_list


class ClearanceKingScraper():

    def __init__(self, url):
        self.url = url        


    def scraper(self):
        # Pick a random uer agent
        user_agent = random.choice(user_agent_list.user_agent_list)

        # Set the headers
        headers = {
            'User-Agent': user_agent
        }

        # This is the session
        s = requests.Session()       

        # Make a request in a session      
        r = s.get(self.url, headers=headers)

        # Scrape the content to end page
        soup = BeautifulSoup(r.content, 'lxml')

        # Define the end page number
        try:
            end_page_number = int(soup.find('p', class_='amount amount--has-pages').text.strip()[8:])
        except:
            end_page_number = 'no end page'

        # Define the sum end page number
        try:
            sum_page_number = int(soup.find('p', class_='amount amount--has-pages').text.strip()[2:4])
        except:
            sum_page_number = 'no sum page number'
       
        end_page = ceil((end_page_number / sum_page_number) + 1)

        # print(end_page_number)
        # print(sum_page_number)    
        # print(end_page)

        # A list to productlinks
        productlinks = []

        # Iterate all productlinks between a range
        for x in range(1, end_page):            
            # Make a request in a session 
            r = s.get(self.url + f'?p={x}')
            
            # Scrape the content
            soup = BeautifulSoup(r.content, 'lxml')
            
            # Identify all products
            productlist = soup.find_all('h2', class_='product-name')

            # Save all links in productlinks list
            for item in productlist:
                for link in item.find_all('a', href=True):
                    productlinks.append(link['href'])
                    #print(link['href'])

        # A list to the scraping data
        list = []

        # Iterate all links in productlinks
        for link in tqdm(productlinks):            
            # Make requests with headers in one sessions (s)
            r = s.get(link, headers=headers)

            # Scrape the content in the soup variable with 'lxml' parser
            soup = BeautifulSoup(r.content, 'lxml')
            
            # Scrape name       
            try:                
                name = str(soup.find('div', class_='product-name').text.strip())
            except:
                name = ''

            # Scrape Barcode
            try:
                barcode = str(soup.find_all('div', class_='sku')[1].text[9:].strip())
            except:
                barcode = ''

            # Scrape Pack Size
            try:             
                pack_size = int(soup.find('table', {'id': 'product-attribute-specs-table'}).text.strip()[11:])
            except:
                pack_size = ''

            # scrape netto unit price and origi price
            try:                
                netto_unit_price_origi_price = float(soup.find('div', class_='price-info').find('span', class_='price').string.strip()[1:])
            except:                
                netto_unit_price_origi_price = ''

            try:
                # scraper gross unit price and origi price
                gross_unit_price_origi_price = float(round(netto_unit_price_origi_price * 1.2, 2))
                        
                # VAT calculation
                vat = round(((gross_unit_price_origi_price - netto_unit_price_origi_price) / netto_unit_price_origi_price) * 100)
            except:
                pass

            # Discount Price
            try:
                netto_discount_price = float(soup.find('div', class_='price-info').find('p', class_='special-price').find('span', class_='price').text.strip()[1:])
                discount_price = netto_discount_price * ((vat / 100) + 1)
            except:
                discount_price = ''

            # Quantity Discount Tier 1
            try:                
                quantity_discount_tier_1 = int(soup.find('ul', class_='tier-prices product-pricing').find('li', class_='tier-price tier-0').find(text=re.compile("Buy")).strip()[4:-4])
            except:
                quantity_discount_tier_1 = ''

            # Quantity Discount Tier 1 Price
            try:
                netto_quantity_discount_tier_1_price = float(soup.find('ul', class_='tier-prices product-pricing').find('li', class_='tier-price tier-0').find('span', class_='price').text.strip()[1:])
                quantity_discount_tier_1_price = netto_quantity_discount_tier_1_price * ((vat / 100) + 1)
            except:
                quantity_discount_tier_1_price = ''

            # Quantity Discount Tier 2
            try:                
                quantity_discount_tier_2 = int(soup.find('ul', class_='tier-prices product-pricing').find('li', class_='tier-price tier-1').find(text=re.compile("Buy")).strip()[4:-4])
            except:
                quantity_discount_tier_2 = ''

            # Quantity Discount Tier 2 Price
            try:
                netto_quantity_discount_tier_2_price = float(soup.find('ul', class_='tier-prices product-pricing').find('li', class_='tier-price tier-1').find('span', class_='price').text.strip()[1:])
                quantity_discount_tier_2_price = netto_quantity_discount_tier_2_price * ((vat / 100) + 1)
            except:
                quantity_discount_tier_2_price = ''
            
            # Quantity Discount Tier 3
            try:                
                quantity_discount_tier_3 = int(soup.find('ul', class_='tier-prices product-pricing').find('li', class_='tier-price tier-2').find(text=re.compile("Buy")).strip()[4:-4])
            except:
                quantity_discount_tier_3 = ''

            # Quantity Discount Tier 3 Price
            try:
                netto_quantity_discount_tier_3_price = float(soup.find('ul', class_='tier-prices product-pricing').find('li', class_='tier-price tier-2').find('span', class_='price').text.strip()[1:])
                quantity_discount_tier_3_price = netto_quantity_discount_tier_3_price * ((vat / 100) + 1)
            except:
                quantity_discount_tier_3_price = ''

            # Scrape Product Code
            try:
                product_code = str(soup.find_all('div', class_='sku')[0].text[14:].strip())
            except:
                product_code = ''

            # Scrape Availability
            try:
                availability = bool(soup.find(text=re.compile("Add to Cart")).strip())                
            except:
                availability = False

            # Define a dictionary for csv
            clearance_king = {                
                'link': link,
                'name': name,
                'barcode': barcode,
                'pack_size': pack_size,            
                'netto_unit_price_origi_price': netto_unit_price_origi_price,
                'gross_unit_price_origi_price': gross_unit_price_origi_price,
                'vat': vat,
                'discount_price': discount_price,
                'quantity_discount_tier_1': quantity_discount_tier_1,
                'quantity_discount_tier_1_price': quantity_discount_tier_1_price,
                'quantity_discount_tier_2': quantity_discount_tier_2,
                'quantity_discount_tier_2_price': quantity_discount_tier_2_price,
                'quantity_discount_tier_3': quantity_discount_tier_3,
                'quantity_discount_tier_3_price': quantity_discount_tier_3_price,
                'product_code': product_code,            
                'availability': availability
            }

            # Add the dictionary to the list every iteration
            list.append(clearance_king)

            # print every iteration        
            # print(
            #     '\n--------- Saving: ---------\n'             
            #     'link: ' + str(clearance_king['link']) + '\n'
            #     'name: ' + str(clearance_king['name']) + '\n'
            #     'barcode: ' + str(clearance_king['barcode']) + '\n'
            #     'pack size: ' + str(clearance_king['pack_size']) + '\n'            
            #     'netto unit price origi price: ' + str(clearance_king['netto_unit_price_origi_price']) + '\n'
            #     'gross unit price origi price: ' + str(clearance_king['gross_unit_price_origi_price']) + '\n'
            #     'vat: ' + str(clearance_king['vat']) + '\n'
            #     'discount price: ' + str(clearance_king['discount_price']) + '\n'
            #     'quantity discount tier 1: ' + str(clearance_king['quantity_discount_tier_1']) + '\n'
            #     'quantity discount tier 1 price: ' + str(clearance_king['quantity_discount_tier_1_price']) + '\n'       
            #     'quantity discount tier 2: ' + str(clearance_king['quantity_discount_tier_2']) + '\n' 
            #     'quantity discount tier 2 price: ' + str(clearance_king['quantity_discount_tier_2_price']) + '\n'
            #     'quantity discount tier 3: ' + str(clearance_king['quantity_discount_tier_3']) + '\n'
            #     'quantity discount tier 3 price: ' + str(clearance_king['quantity_discount_tier_3_price']) + '\n'
            #     'product code: ' + str(clearance_king['product_code']) + '\n'
            #     'availability: ' + str(clearance_king['availability']) + '\n'
            # )

        # Make table to list
        df = pd.DataFrame(list)

        # Save to csv       
        df.to_csv(r'C:\WEBDEV\clearance_king_scraper\exports\clearance_king.csv', mode='a', index=False, header=True)
        
get_clearance_king_baby_and_kids = ClearanceKingScraper('https://www.clearance-king.co.uk/baby-kids.html')
get_clearance_king_car_bike = ClearanceKingScraper('https://www.clearance-king.co.uk/car-bike.html')
get_clearance_king_clearance_lines = ClearanceKingScraper('https://www.clearance-king.co.uk/clearance-lines.html')
get_clearance_king_diy = ClearanceKingScraper('https://www.clearance-king.co.uk/diy.html')
get_clearance_king_electrical = ClearanceKingScraper('https://www.clearance-king.co.uk/electrical.html')
get_clearance_king_electronic_cigarettes = ClearanceKingScraper('https://www.clearance-king.co.uk/electronic-cigarettes.html')
get_clearance_king_food_anddrinks = ClearanceKingScraper('https://www.clearance-king.co.uk/food-drink.html')
get_clearance_king_garden_outdoor_living = ClearanceKingScraper('https://www.clearance-king.co.uk/garden-outdoor-living.html')
get_clearance_king_gifts_toys = ClearanceKingScraper('https://www.clearance-king.co.uk/gifts-toys.html')
get_clearance_king_health_and_beauty = ClearanceKingScraper('https://www.clearance-king.co.uk/health-beauty.html')
get_clearance_king_household = ClearanceKingScraper('https://www.clearance-king.co.uk/household.html')
get_clearance_king_medical_first_aid = ClearanceKingScraper('https://www.clearance-king.co.uk/medical-first-aid.html')
get_clearance_king_party_celebrations = ClearanceKingScraper('https://www.clearance-king.co.uk/party-celebrations.html')
get_clearance_king_pets = ClearanceKingScraper('https://www.clearance-king.co.uk/pets.html')
get_clearance_king_pound_lines = ClearanceKingScraper('https://www.clearance-king.co.uk/pound-lines.html')
get_clearance_king_smoking = ClearanceKingScraper('https://www.clearance-king.co.uk/smoking.html')
get_clearance_king_stationery_crafts = ClearanceKingScraper('https://www.clearance-king.co.uk/stationery-crafts.html')
get_clearance_king_summer_essentials = ClearanceKingScraper('https://www.clearance-king.co.uk/summer-essentials.html')
get_clearance_king_travel = ClearanceKingScraper('https://www.clearance-king.co.uk/travel.html')

get_clearance_king_baby_and_kids.scraper()
time.sleep(10)
get_clearance_king_car_bike.scraper()
time.sleep(10)
get_clearance_king_clearance_lines.scraper()
time.sleep(10)
get_clearance_king_diy.scraper()
time.sleep(10)
get_clearance_king_electrical.scraper()
time.sleep(10)
get_clearance_king_electronic_cigarettes.scraper()
time.sleep(10)
get_clearance_king_food_anddrinks.scraper()
time.sleep(10)
get_clearance_king_garden_outdoor_living.scraper()
time.sleep(10)
get_clearance_king_gifts_toys.scraper()
time.sleep(10)
get_clearance_king_health_and_beauty.scraper()
time.sleep(10)
get_clearance_king_household.scraper()
time.sleep(10)
get_clearance_king_medical_first_aid.scraper()
time.sleep(10)
get_clearance_king_party_celebrations.scraper()
time.sleep(10)
get_clearance_king_pets.scraper()
time.sleep(10)
get_clearance_king_pound_lines.scraper()
time.sleep(10)
get_clearance_king_smoking.scraper()
time.sleep(60)
get_clearance_king_stationery_crafts.scraper()
time.sleep(10)
get_clearance_king_summer_essentials.scraper()
time.sleep(10)
get_clearance_king_travel.scraper()