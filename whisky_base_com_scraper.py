## Scraper for user data from whiskybase.com
## Author: HY Lau
## Last Updated: Dec 3, 2021

from bs4 import BeautifulSoup
import requests
import re
from selenium import webdriver
import pandas as pd

headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
          'accept-encoding': 'gzip, deflate, br',
          'accept-language': 'en-US,en;q=0.9',
          'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}


def getReviewLinks():

	# Search for all products and get the review section for each product
    
    link_list=[]
    pagenum = 0

    while True:
        pagenum += 1
    
        r = requests.get('https://www.whiskybase.com/market/browse?take=100&search=&price%5B%5D=-1&fillinglevel_id%5B%5D=&sort=added&direction=desc&page=' + str(pagenum), headers=headers)    
        html = r.content
        soup = BeautifulSoup(html, 'lxml')
    
        if soup.find_all('tr', {'class':'mp-whisky-item'}) == []:
            break
    
        all_links = soup.find_all('a', href=True)
    
        for link in all_links:
            if re.search('as=seller', link['href']):
                if link['href'] not in link_list:
                    link_list.append(link['href'])
        
        print(f'{pagenum} pages scraped...')
        
    return link_list


def getBuyerProfiles(url):

	# Get the buyer profile page
    
    link_list=[]
    
    r = requests.get(url, headers=headers)
    html = r.content
    soup = BeautifulSoup(html, 'lxml')
    all_links = soup.find_all('a', href=True)
    
    for link in all_links:
        if re.search('/profile/', link['href']):
            link_list.append(link['href'])
    
    link_list.pop(0)
    return link_list


def getAllBuyers(reviewLinks: list):

	# Get all buyer profile links from the list of review links
    
    link_list=[]
    processedCount = 0
    
    for reviewLink in reviewLinks:
        buyerLinks = getBuyerProfiles(reviewLink)
        for buyerLink in buyerLinks:
            if buyerLink not in link_list:
                link_list.append(buyerLink)
                
        processedCount += 1
        print(f'{processedCount} review links processed...')
    
    return link_list


def getUserNames(profiles: list):

	# Get the list of actual username from the list of profile page
    
    link_list = []
    processedCount = 0
    
    for profile in profiles:
        r = requests.get(profile, headers=headers)
        html = r.content
        soup = BeautifulSoup(html, 'lxml')
        all_links = soup.find_all('a', href=True)
        if len(all_links[41]['href']) > 20:
            link_list.append(all_links[41]['href'])
        
        processedCount += 1
        print(f'{processedCount} profiles processed...')
    
    return link_list


def getPageData(userPage: str):

	# Get ratings data from a user profile page

    driver.set_page_load_timeout(2400)
    driver.get(userPage + '/lists/ratings')
    columns=['Nil', 'Whislky', 'Age', 'Alc%', 'Volume', 'No. of Bottles', 'Cask Number', 'Votes', 'Avg. Rating', 'User Rating']
    rows = driver.find_elements_by_xpath('//tbody/tr')
    tabledata = pd.DataFrame(columns=columns)
    
    for row in rows:
        cols = row.find_elements_by_xpath('.//td')
        rowdata = []
        
        for col in cols:
            rowdata.append(col.text)
            
        rowdata = pd.DataFrame(rowdata).T.set_axis(columns, axis=1)
        rowdata['user'] = userPage.split('/')[-1]
        tabledata = pd.concat([tabledata, rowdata], axis=0)
    
    tabledata.pop('Nil')
    tabledata.reset_index(drop=True, inplace=True)
    
    return tabledata


def getAllData(pageList: list):

	# Get all ratings data from the list of user profile pages
    
    allData = pd.DataFrame()
    processCount = 0

    for page in pageList:
        userData = getPageData(page)
        allData = pd.concat([allData, userData])
        processCount += 1
        print(f'{processCount} pages processed...')
        
    return allData.reset_index(drop=True)


if __name__ == '__main__':
	all_usernames = getUserNames(getAllBuyers(getReviewLinks()))
	driver = webdriver.Chrome('chromedriver_win32\chromedriver')
	finalData = getAllData(all_usernames)
	finalData.to_csv('userratings_raw.csv')