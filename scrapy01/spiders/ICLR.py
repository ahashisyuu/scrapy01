# -*- coding:utf-8 -*-
import os
import re
import socket
import requests

from bs4 import BeautifulSoup
from urllib import request

import scrapy
from click import pause
from urllib.error import HTTPError
from scrapy import Request
from scrapy.http import HtmlResponse
from scrapy.selector import HtmlXPathSelector, Selector

from scrapy01.items import Scrapy01Item

FILES_STORE = './scrapy01/iclr2018'
socket.setdefaulttimeout(5)


def get_exist_files(filepath):
    listdir = os.listdir(filepath)
    exist_files = []
    for name in listdir:
        if os.path.isdir(os.path.join(filepath, name)):
            exist_files += get_exist_files(os.path.join(filepath, name))
        else:
            number = name.split('_ICLR2018_')[0][2:]
            exist_files.append(number)
    return exist_files


def paper_title_preprocessing(paper_title, filters='\\/:*?"<>|\n'):
    for x in filters:
        if x in paper_title:
            paper_title = paper_title.replace(x, ' ')

    space_list = ['       ', '      ', '     ', '    ', '   ', '  ']
    for x in space_list:
        if x in paper_title:
            paper_title = paper_title.replace(x, ' ')
    if len(paper_title) > 120:
        paper_title = paper_title[:121]
    return paper_title


class ICLRScrapy(scrapy.Spider):
    name = "ICLR"
    allowed_domains = ["iclr.cc"]
    start_urls = ["https://iclr.cc/Conferences/2018/Schedule"]
    paper_title = None
    paper_author = None
    exist_file = None
    path = None

    def parse(self, response):
        print('==================  get all sections  ========================')

        all_section = response.xpath('//*[@id="main"]/div/div/div[2]'
                                     '/div[re:test(@onclick,"showDetail\(\d+\)")]')
        print('==============================================================')
        exist_file = get_exist_files(FILES_STORE)
        for section in all_section:
            section_type = section.xpath('div/div[1]/text()').extract()[0]
            paper_title = paper_title_preprocessing(section.xpath('div/div[3]/text()').extract()[0])
            paper_author = section.xpath('div/div[5]/text()').extract()
            relative_url = section.xpath('div/div[6]/a/span/a/@href').extract()

            if len(relative_url) == 0:
                print('--------  no paper url, Type: %s, Title: %s  ---------' % (section_type, paper_title))
                continue

            if len(paper_author) == 0:
                print('--------  no paper author, Type: %s, Title: %s  ---------' % (section_type, paper_title))
                continue

            paper_id = relative_url[0].split('=')[-1]
            try:
                paper_url = self.get_url(relative_url[0])
            except HTTPError as hte:
                print('-------', hte.info(), relative_url, '--------')
                continue

            if paper_id in exist_file:
                print('\t' + paper_id)
                continue

            filename = 'I-' + paper_id + '_ICLR2018_' \
                       + paper_author[0].split(' · ')[0] + '_' + paper_title + '.pdf'
            path = os.path.join(FILES_STORE, section_type)
            if os.path.exists(path) is False:
                os.mkdir(path)
            filepath = os.path.join(path, filename)

            # print('==================  save paper as pdf file  ========================')
            try:
                request.urlretrieve(paper_url, filepath)
                print(section_type, paper_id, paper_url, paper_title)
            except socket.timeout:
                print('-----------  paper%s time out  -------------  skip  -----' % paper_number)
            # print('==================  save successfully  ========================')

    def get_url(self, relative_url, url_suffix='https://openreview.net'):
        html = request.urlopen(relative_url, timeout=10).read()
        response = HtmlResponse(url=relative_url, body=html, encoding='utf-8')
        content = Selector(response=response).xpath('//*[@id="content"]')
        opposite_url = content.xpath('div[1]/div[1]/h2/a/@href').extract()[0]
        paper_url = url_suffix + opposite_url
        return paper_url






