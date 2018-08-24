# -*- coding:utf-8 -*-
import os
from urllib import request

import scrapy
from scrapy01.settings import FILES_STORE
from scrapy01.items import Scrapy01Item


def get_exist_files(filepath):
    listdir = os.listdir(filepath)
    exist_files = []
    for name in listdir:
        number = name.split('ACL')[0].split('-')[-1]
        exist_files.append(number)
    return exist_files


class ACLScrapy(scrapy.Spider):
    name = "ACL"
    allowed_domains = ["aclweb.org"]
    start_urls = ["https://aclanthology.coli.uni-saarland.de/events/acl-2018"]

    def parse(self, response):

        all_p = response.xpath('/html/body/div[@id="main-container"]'
                               '/div[@id="content"]/div[@class="span12"]'
                               '/div[@class="row"]/div[@class="span12"]'
                               '/p'
                               )
        # print(all_p)
        filters = '\\/:*?"<>|\n'
        exist_file = get_exist_files(FILES_STORE)
        item = Scrapy01Item()
        for p in all_p:

            paper_url = p.xpath('a[re:test(@href, "http://aclweb.org/anthology/P[0-9]+-[0-9]+")]/@href').extract()[0]
            paper_number = paper_url.split('/')[-1]
            paper_title = p.xpath('strong/a/text()').extract()[0]
            paper_first_author = p.xpath('a[re:test(@href, "/people/[a-z\-]+")]/text()').extract()[0]

            if paper_number.split('-')[-1] in exist_file:
                print('    ' + paper_number)
                continue

            for x in filters:
                if x in paper_title:
                    paper_title = paper_title.replace(x, ' ')

            item['url'] = [paper_url]
            item['number'] = [paper_number]
            item['author'] = [paper_first_author]
            item['title'] = [paper_title]

            filename = item['number'][0] + 'ACL2018_' + item['author'][0] + '_' + item['title'][0] + '.pdf'
            filepath = os.path.join(FILES_STORE, filename)
            request.urlretrieve(paper_url, filepath)
            # yield item
            print(paper_number, paper_url)












