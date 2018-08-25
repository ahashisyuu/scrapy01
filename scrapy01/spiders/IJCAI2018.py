# -*- coding:utf-8 -*-
import os
from urllib import request

import scrapy
from scrapy01.items import Scrapy01Item

FILES_STORE = './scrapy01/ijcai2018'


def get_exist_files(filepath):
    listdir = os.listdir(filepath)
    exist_files = []
    for name in listdir:
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
    if len(paper_title) > 100:
        paper_title = paper_title[:101]
    return paper_title


class COLINGScrapy(scrapy.Spider):
    name = "IJCAI"
    allowed_domains = ["ijcai.org"]
    start_urls = ["https://www.ijcai.org/proceedings/2018/"]

    def parse(self, response):

        all_section = response.xpath('/html/body/div[@id="container"]'
                                     '/div[@id="content"]/section[@id="post-content"]'
                                     '/div[@class="region region-content"]'
                                     '/div[@id="block-system-main"]/div[@class="content"]'
                                     '/div[@class="proceedings"]/div[@class="section"]')

        exist_file = get_exist_files(FILES_STORE)
        for section in all_section:
            # 对每个section分别建立子文件夹
            section_title = section.xpath('div[@class="section_title"]/h3/text()').extract()[0]

            if section_title:
                section_path = os.path.join(FILES_STORE, section_title)
                if os.path.exists(section_path) is False:
                    os.mkdir(section_path)

                all_subsection = section.xpath('div[@class="subsection"]/')

                for subsection in all_subsection:
                    # 对每个subsection分别建立子文件夹
                    subsection_title = subsection.xpath('div[@class="subsection_title"]/text()').extract()[0]
                    subsection_papers = subsection.xpath('div[@class="paper_wrapper"]')

                    if subsection_title:
                        subsection_path = os.path.join(FILES_STORE, subsection_title)
                        if os.path.exists(subsection_path) is False:
                            os.mkdir(subsection_path)

                        for subsection_paper in subsection_papers:
                            # paper_id = subsection_paper.xpath('@id').extract()[0][5:]  # 将paper0中的paper去掉
                            paper_title = subsection_paper.xpath('div[@class="title"]/text()').extract()[0]
                            paper_authors = subsection_paper.xpath('div[@class="title"]/text()').extract()[0]
                            paper_opposite_url = subsection_paper.xpath('div[@class="details"]'
                                                                        '/a[@href="\d+\.pdf"]/@href').extract()[0]

                            paper_number = paper_opposite_url.split('.')[0]
                            if paper_number in exist_file:
                                print('\t' + paper_number)
                                continue
                            paper_title = paper_title_preprocessing(paper_title)
                            filename = 'P18-' + paper_number + 'IJCAI2018' + '_' + paper_authors.split(',')[0] + '_' \
                                       + paper_title
                            filepath = os.path.join(FILES_STORE, filename)
                            paper_url = self.start_urls[0] + paper_opposite_url
                            request.urlretrieve(paper_url, filepath)
                            print(paper_number, paper_title)
