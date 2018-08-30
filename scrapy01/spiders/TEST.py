import random
import re
from bs4 import BeautifulSoup
from scrapy import Request
from scrapy.selector import HtmlXPathSelector
from urllib import request
from selenium import webdriver
import ssl
import time

# context = ssl._create_unverified_context()
# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
# req = request.Request('https://dl.acm.org/authorize?N652299', headers=headers)
# html = request.urlopen(req)
# print(html.read())
# chrome_option = webdriver.ChromeOptions()
# chrome_option.headless = True
# print(chrome_option.headless)
# driver = webdriver.Chrome('C:/Users/ahashi_syuu/AppData/Local/Google/Chrome/Application/chrome.exe',
#                           options=chrome_option)
# START_LOCATION = 'C:/Users/ahashi_syuu/AppData/Local/Google/Chrome/Application/'
# driver = webdriver.Chrome(START_LOCATION + 'chromedriver.exe')
# driver.set_page_load_timeout(60)
# time.sleep(3)
# driver.get('https://dl.acm.org/authorize?N652299')
# driver.close()
# print('-----------------------------------------------------------------------------------------------')
#
# html = driver.page_source
# print(html)
# soup = BeautifulSoup(html, 'lxml')
# href = soup.body.find('div', style="width:940px; margin-left: auto; margin-right: auto; text-align:left")\
#        .find('div', class_="text14").find('p', style="margin-top:5px; margin-left:50px;")\
#        .find('a').get('href')
# print(href)
# from scrapy01.middlewares import RotateUserAgentMiddleware
#
# paper_url = 'https://dl.acm.org/ft_gateway.cfm?id=3210230&amp;ftid=1982759&amp;' \
#             'dwn=1&amp;CFID=67244081&amp;' \
#             'CFTOKEN=cde9f71b225dc4bc-38188910-A65B-9E66-073AB3D7920D2A0D'
# filepath = 'test.pdf'
# user_agent_list = RotateUserAgentMiddleware.user_agent_list
# headers = {'User-Agent': random.choice(user_agent_list)}
# req = request.Request(paper_url, headers=headers)
# data = request.urlopen(req, timeout=30).read()
# with open(filepath, 'wb') as fw:
#     fw.write(data)


