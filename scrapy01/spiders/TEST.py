import re
from bs4 import BeautifulSoup
from scrapy import Request
from scrapy.selector import HtmlXPathSelector
from urllib import request


# with open('aaai2018html.txt', 'rb') as fw:
#     html = fw.read()
#
# parser = BeautifulSoup(html, "html.parser")
# content = parser.body.find('div', id="container").find('div', id="body")\
#           .find('div', id="main").find('div', id="content")
# patial = str(content).split('<div class="separator"></div>')
# print(patial[0])


