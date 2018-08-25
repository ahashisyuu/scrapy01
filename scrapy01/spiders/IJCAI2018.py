# -*- coding:utf-8 -*-
import os
import re
import socket

from bs4 import BeautifulSoup
from urllib import request

import scrapy
from click import pause
from scrapy.http import HtmlResponse
from scrapy.selector import HtmlXPathSelector, Selector

from scrapy01.items import Scrapy01Item

FILES_STORE = './scrapy01/ijcai2018'
socket.setdefaulttimeout(5)


def get_exist_files(filepath):
    listdir = os.listdir(filepath)
    exist_files = []
    for name in listdir:
        if os.path.isdir(os.path.join(filepath, name)):
            exist_files += get_exist_files(os.path.join(filepath, name))
        else:
            number = name.split('IJCAI')[0].split('-')[-1]
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


def save_paper(subsection_papers, exist_file, path, start_url):
    for subsection_paper in subsection_papers:
        # print('==================  deal with property  ========================')
        # paper_id = subsection_paper.xpath('@id').extract()[0]  # 将paper0中的paper去掉
        paper_title = subsection_paper.xpath('div[@class="title"]/text()').extract()[0]
        paper_authors = subsection_paper.xpath('div[@class="authors"]/text()').extract()[0]
        # print(paper_authors)
        paper_opposite_url = subsection_paper.xpath('div[@class="details"]'
                                                    '/a[re:test(@href, "\d+\.pdf")]/@href').extract()[0]

        paper_number = paper_opposite_url.split('.')[0]
        if paper_number in exist_file:
            print('\t' + paper_number)
            continue
        paper_title = paper_title_preprocessing(paper_title)
        filename = 'P18-' + paper_number + 'IJCAI2018' + '_' + paper_authors.split(',')[0] + '_' \
                   + paper_title + '.pdf'
        filepath = os.path.join(path, filename)
        paper_url = start_url + paper_opposite_url
        # print('==================  save paper as pdf file  ========================')
        try:
            request.urlretrieve(paper_url, filepath)
            print(paper_number, paper_title)
        except socket.timeout:
            print('-----------  paper%s time out  -------------  skip  -----' % paper_number)
        # print('==================  save successfully  ========================')


class IJCAIScrapy(scrapy.Spider):
    name = "IJCAI"
    allowed_domains = ["ijcai.org"]
    start_urls = ["https://www.ijcai.org/proceedings/2018/"]

    def parse(self, response):
        print('==================  get all sections  ========================')

        all_section = response.xpath('/html/body/div[@id="container"]/div[@class="content-sidebar-wrap"]'
                                     '/div[@id="content"]/section[@id="post-content"]'
                                     '/div[@class="region region-content"]'
                                     '/div[@id="block-system-main"]/div[@class="content"]'
                                     '/div[@class="proceedings"]')
        print('===============================================================')
        # 网站排版问题需要重新识别html结构, 去除section0的内容
        pattern = re.compile(r'<div class="section" id="section0">.+(<div class="section" id="section0">.+)', flags=re.DOTALL)
        ob = pattern.search(all_section.xpath('div').extract()[0]).group(1)
        response = HtmlResponse(url=self.start_urls[0], body=ob, encoding='utf-8')
        all_section = Selector(response=response).xpath('/html/body/div')
        exist_file = get_exist_files(FILES_STORE)
        for i, section in enumerate(all_section):
            # 对每个section分别建立子文件夹
            # print(section.extract()[0:3000])
            print('==================  get section title  ========================')

            section_title = section.xpath('div[@class="section_title"]/h3/text()').extract()

            if section_title:
                print(section_title)
                section_title = paper_title_preprocessing(section_title[0])
                section_path = os.path.join(FILES_STORE, section_title)
                if os.path.exists(section_path) is False:
                    os.mkdir(section_path)

                print('==================  get all subsections  ========================')
                all_subsection = section.xpath('div[@class="subsection"]')

                for subsection in all_subsection:
                    # 对每个subsection分别建立子文件夹
                    # print('==================  get subsection titles and papers  ========================')
                    subsection_title = subsection.xpath('div[@class="subsection_title"]/text()').extract()
                    subsection_papers = subsection.xpath('div[@class="paper_wrapper"]')

                    if subsection_title:
                        subsection_title = paper_title_preprocessing(subsection_title[0])
                        subsection_path = os.path.join(section_path, subsection_title)
                        if os.path.exists(subsection_path) is False:
                            os.mkdir(subsection_path)
                        # print('==================  save section papers  ========================')
                        save_paper(subsection_papers, exist_file, subsection_path, self.start_urls[0])

                    else:
                        # print('==================  save section papers  ========================')
                        save_paper(subsection_papers, exist_file, section_path, self.start_urls[0])

