# -*- coding:utf-8 -*-
import os
import re
import socket
from urllib.error import URLError

from bs4 import BeautifulSoup
from urllib import request

import scrapy
from click import pause
from scrapy import Request
from scrapy.http import HtmlResponse
from scrapy.selector import HtmlXPathSelector, Selector

from scrapy01.items import Scrapy01Item

YEAR = '2019'
FILES_STORE = './scrapy01/aaai' + YEAR
socket.setdefaulttimeout(30)


def get_exist_files(filepath):
    listdir = os.listdir(filepath)
    exist_files = []
    for name in listdir:
        if os.path.isdir(os.path.join(filepath, name)):
            exist_files += get_exist_files(os.path.join(filepath, name))
        else:
            number = name.split('AAAI')[0].split('-')[-1]
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
    return paper_title.strip()


class AAAIScrapy(scrapy.Spider):
    name = "AAAI"
    allowed_domains = ["aaai.org"]
    start_urls = ["https://www.aaai.org/ocs/index.php/AAAI/AAAI" + YEAR[-2:] + "/schedConf/presentations/"]
    paper_title = None
    paper_author = None
    exist_file = None
    path = None

    def parse(self, response):
        print('==================  get all sections  ========================')

        all_section = response.xpath('/html/body/div[@id="container"]/div[@id="body"]'
                                     '/div[@id="main"]/div[@id="content"]')
        print('===============================================================')
        # 网站排版问题需要识别html子标题
        all_h4 = all_section.extract()[0].split('<div class="separator"></div>')
        # 添加最外层标签
        header_label = '<div id="content">\n'
        tail_label = '\n</div><!-- content -->'
        length = len(all_h4)
        all_h4 = [h4 + tail_label for h4 in all_h4[:length]]+[all_h4[-1]]
        all_h4 = [all_h4[0]] + [header_label + h4 for h4 in all_h4[1:]]

        self.exist_file = get_exist_files(FILES_STORE)
        for i, h4 in enumerate(all_h4):
            h4_response = HtmlResponse(url=self.start_urls[0], body=h4.strip(), encoding='utf-8')
            h4_body = Selector(response=h4_response).xpath('/html/body/div[@id="content"]')
            print('------------------  new h4 title  ------------------------')
            # print(h4_body.extract()[0][:1000])
            h4_title = h4_body.xpath('h4/text()').extract()[0]
            print(h4_title)
            print('----------------------------------------------------------')
            h4_title = paper_title_preprocessing(h4_title)
            h4_path = os.path.join(FILES_STORE, h4_title)
            if os.path.exists(h4_path) is False:
                os.mkdir(h4_path)
            self.path = h4_path

            h4_papers = h4_body.xpath('table')
            for h4_paper in h4_papers:
                paper_title = h4_paper.xpath('tr[1]/td[1]/a/text()').extract()[0]
                self.paper_title = paper_title_preprocessing(paper_title)

                paper_url = h4_paper.xpath('tr[1]/td[2]/a/@href').extract()[0]

                self.paper_author = h4_paper.xpath('tr[2]/td[1]/text()').extract()[0].split(',')[0].strip()
                try:
                    html = request.urlopen(paper_url, timeout=30)
                except URLError:
                    print('---------  url error: %s  ---------' % paper_url)
                    continue
                except socket.timeout:
                    print('---------  url time out: %s  ---------  skip  -------' % paper_url)
                    continue
                h4_response = HtmlResponse(url=paper_url, body=html.read(), encoding='utf-8')
                paper_response = Selector(response=h4_response)
                self.parse_v2(paper_response)

    def parse_v2(self, response):
        paper_title = self.paper_title
        paper_author = self.paper_author
        paper_url = response.xpath('/html/frameset/frame[1]/@src').extract()[0]
        paper_number = paper_url.split('/')[-1]
        if paper_number not in self.exist_file:
            filename = 'A' + YEAR[-2:] + '-' + paper_number + 'AAAI' + YEAR + '_' + paper_author + '_' \
                       + paper_title + '.pdf'
            filepath = os.path.join(self.path, filename)

            # print('==================  save paper as pdf file  ========================')
            try:
                paper_response = request.urlopen(paper_url, timeout=30)
                paper_response = HtmlResponse(url=paper_url, body=paper_response.read(), encoding='utf-8')
                paper_url = Selector(response=paper_response)\
                    .xpath('/html/body/div/div/div/div[@id="content"]/p/a[3]/@href').extract()[0]
                request.urlretrieve(paper_url, filepath)
                print(paper_number, paper_title)
            except socket.timeout:
                print('-----------  paper%s time out  -------------  skip  -----' % paper_number)
            except URLError:
                print('-----------  url error: %s  -----------  skip  -----' % paper_url)
            except FileNotFoundError:
                print('-----------  notFoundError: URL: %s, '
                      'filepath: %s  -------------------' % (paper_url, filepath))
            # print('==================  save successfully  ========================')
        else:
            print('\t' + paper_number)





