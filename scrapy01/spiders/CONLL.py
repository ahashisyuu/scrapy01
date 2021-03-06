# -*- coding:utf-8 -*-
import os
import socket
from urllib import request
from urllib.error import URLError

import scrapy

socket.setdefaulttimeout(30)

YEAR = '2017'
FILES_STORE = './scrapy01/conll' + YEAR


def get_exist_files(filepath):
    listdir = os.listdir(filepath)
    exist_files = []
    for name in listdir:
        number = name.split('CONLL' + YEAR)[0].split('-')[-1]
        exist_files.append(number)
    return exist_files


class ACLScrapy(scrapy.Spider):
    name = "CONLL"
    allowed_domains = ["aclweb.org"]
    start_urls = ["https://aclanthology.coli.uni-saarland.de/events/conll-" + YEAR]

    def parse(self, response):

        all_p = response.xpath('/html/body/div[@id="main-container"]'
                               '/div[@id="content"]/div[@class="span12"]'
                               '/div[@class="row"]/div[@class="span12"]'
                               '/p'
                               )
        # print(all_p)
        filters = '\\/:*?"<>|\n'
        exist_file = get_exist_files(FILES_STORE)
        for p in all_p:

            paper_url = p.xpath('a[re:test(@href, "http://www.aclweb.org/anthology/K[0-9]+-[0-9]+")]/@href').extract()[0]
            paper_number = paper_url.split('/')[-1]
            paper_title = p.xpath('strong/a/text()').extract()[0]
            paper_first_author = p.xpath('a[re:test(@href, "/people/[a-z\-]+")]/text()').extract()[0]

            if paper_number.split('-')[-1] in exist_file:
                print('    ' + paper_number)
                continue

            for x in filters:
                if x in paper_title:
                    paper_title = paper_title.replace(x, ' ')

            filename = paper_number + 'CONLL' + YEAR + '_' + \
                paper_first_author + '_' + paper_title.strip() + '.pdf'
            filepath = os.path.join(FILES_STORE, filename)
            try:
                request.urlretrieve(paper_url, filepath)
                print(paper_number, paper_url, paper_title)
            except socket.timeout:
                print('---------  url time out: %s  ---------  skip  -------' % paper_url)
            except URLError:
                print('-----------  url error: %s  -----------  skip  -----' % paper_url)














