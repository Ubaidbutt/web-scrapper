# This program is written for Arbisoft as part of the technical assessment for a job

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time


# MongoDB setup, database and collection
client = MongoClient('mongodb://localhost:27017')
database = client['my-db']
collection = database['job-data']


# Function to store the values in MongoDB database
def store_mongodb(values):
    if len(values) == 0:
        print ('No values to Insert!')
        return
    for val in values:
        # Val is a tuple
        data = {
            'JobText': val[0],
            'Company': val[1],
            'Time': val[2]
        }
        collection.insert_one(data)
    print('Inserted Successfully into the MongoDB database')


web_url = 'https://news.ycombinator.com/jobs'



# The function that scraps the website and returns a tuple as a response with only new data from the previous run
def scrap_website(url, index):
    # A list to store tuples (The text, Company's Url, Hours)
    data_to_send = []

    page_response = requests.get(url, timeout=10)
    page_content = BeautifulSoup(page_response.content, "html.parser")

    # Find all the the <tr> that inculdes the the company's site URL and text
    tr_list = page_content.find_all('tr', attrs={'class': 'athing'})

    # Loop through each <tr> to extract relevant Information
    for tr in tr_list:
        maintext = tr.find('a', attrs={'class': 'storylink'})
        siteurl = tr.find('span', attrs={'class': 'sitestr'})

        itemid = 'item?id=' + tr['id']
        time_posted = page_content.find_all('a', attrs={'href': itemid})

        # For the first run, it will store all what came in
        if index == 1:
            if siteurl is None:
                pass
            else:
                data_to_send.append((maintext.text, siteurl.text, time_posted[0].text))
        else:
            '''
            For the subsequent runs, it will first check that time should be in minutes as the function runs after 
            every 59 minutes
            '''
            time_check = time_posted[0].text
            if time_check.__contains__('minutes'):
                data_to_send.append((maintext.text, siteurl.text, time_posted[0].text))

    return data_to_send


# Main function
if __name__ == '__main__':
    print('----------- Main function starting -----------')
    next_time = time.time()
    count = 1
    while True:
        results = scrap_website(web_url, count)
        count = count + 1
        print('The scrap results are as follows:')
        for res in results:
            print(res)

        store_mongodb(results)
        next_time += 2
        time.sleep(max(0, next_time - time.time()))

        print('Pass {} started'.format(count))