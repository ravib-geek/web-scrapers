#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Scrape job details from newcareers24.com website.

Program will parse data dynamically using all job links and populates data into
a CSV file.
"""


import sys
import csv
import time
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from collections import defaultdict

#update chromedriver path here
PATH = '/path/to/chromedriver'

WEBSITE = 'http://www.careers24.com/jobs/lc-south-africa/se-it/'
driver = webdriver.Chrome(executable_path=PATH)

driver.get(WEBSITE)

def get_page_numbers():
    pages = driver.find_elements_by_class_name('page-navigation')
    print('Getting total page count...')

    for page in pages:
        html_text = page.get_attribute('innerHTML')
        soup = BeautifulSoup(html_text, 'html.parser')
        pagination = soup.find().attrs
        total_pages = int(pagination['data-total-pages'])
        current_page = int(pagination['data-current-page-number'])
        return {'total_pages':total_pages, 'current_page':current_page}

def get_urls():
    url_list = []
    pagination = get_page_numbers()
    total_pages =  pagination['total_pages'] - 1
    current_page = pagination['current_page']
    print('Getting web links...')

    while current_page <= total_pages:
        driver.find_element_by_xpath('//*[@id="pagination"]/li[6]/a').click()
        time.sleep(3)
        for elem in driver.find_elements_by_class_name('job-card'):
            date = elem.text.split(':')
            date = date[-1].split('\n')[0]
            url = elem.find_element_by_css_selector('a').get_attribute('href')
            url_list.append((url, date))
            current_page += 1
    return url_list

def get_items(url_list):
    final = {}
    count = 0
    for url in url_list:
        print(f'Fetching data from {url[0]}')

        driver.get(url[0])
        time.sleep(3)
        elements = driver.find_elements_by_class_name(
                                            'c24-vacancy-deatils-container')
        for elem in elements:
            html_text = elem.get_attribute('innerHTML')
            soup = BeautifulSoup(html_text, 'html.parser')
            details_list = soup.find('div', {'class': 'detailsList'})
            final[count] = {}
            final[count]['url'] = url
            final[count]['date'] = url[-1]
            final[count]['title'] = soup.h1.text.strip()
            for a in soup.find_all('p', attrs={'class' : 'mb-15'}):
                if len(a.find_all('strong')) != 0:
                    final[count]['employer'] = a.text.strip(
                                                            ).split(':')[-1]
            final[count]['location'] = details_list.find_all(
                                                       'li')[0].text.strip()
            final[count]['salary'] = details_list.find_all(
                                        'li')[1].text.strip().split(':')[-1]
            final[count]['job_type'] = details_list.find_all(
                                        'li')[2].text.strip().split(':')[-1]
            final[count]['reference'] = details_list.find_all(
                                        'li')[4].text.strip().split(':')[-1]
            final[count]['description'] = soup.find(
                                 'div', {'class': 'v-descrip'}).text.strip()
            count += 1
    return final

def create_csv(data):
    filename = 'careers24-' + datetime.today().strftime('%Y-%m-%d') + '.csv'
    with open(filename, mode='w', encoding='utf-8') as csv_file:
        cols = ['url', 'date', 'title', 'employer', 'location',
                        'salary', 'job_type', 'reference', 'description']
        writer = csv.DictWriter(csv_file, fieldnames=cols, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for k in data:
            writer.writerow(data[k])

if __name__ == '__main__':
    print()
    print(f'Please wait while the program process data from {WEBSITE}')
    final_data = get_items(get_urls())
    create_csv(final_data)
    driver.quit()
    print('Records have been successfully saved!')
