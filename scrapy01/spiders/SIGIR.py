# -*- coding:utf-8 -*-
import os
import random
import re
import socket
import scrapy

from urllib.error import HTTPError, URLError
from scrapy import Selector
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from ..middlewares import RotateUserAgentMiddleware
from urllib import request

YEAR = '2017'
FILES_STORE = './scrapy01/sigir' + YEAR
socket.setdefaulttimeout(90)


def get_exist_files(filepath):
    listdir = os.listdir(filepath)
    exist_files = []
    for name in listdir:
        if os.path.isdir(os.path.join(filepath, name)):
            exist_files += get_exist_files(os.path.join(filepath, name))
        else:
            number = name.split('SIGIR' + YEAR)[0]
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


def paper_section_path(section_title):
    section_title = paper_title_preprocessing(section_title)
    section_path = os.path.join(FILES_STORE, section_title)
    if os.path.exists(section_path) is False:
        os.mkdir(section_path)
    return section_path


class SIGIRScrapy(scrapy.Spider):
    name = "SIGIR"
    allowed_domains = ["sigir.org"]
    start_urls = ["https://sigir.org/sigir" + YEAR + "/toc.html"]
    START_LOCATION = 'C:/Users/ahashi_syuu/AppData/Local/Google/Chrome/Application/'
    driver = None

    def open_chrome(self):
        driver = webdriver.Chrome(self.START_LOCATION + 'chromedriver.exe')
        driver.set_page_load_timeout(90)
        self.driver = driver
        self.driver.get('https://www.baidu.com')

    def close_chrome(self):
        self.driver.quit()

    def parse(self, response):
        print('==================  get all sections  ========================')
        all_section = response.xpath('//*[@id="DLcontent"]')
        print('==============================================================')

        print('==================  get section titles  ======================')
        all_section_title = all_section.xpath('h2/text()').extract()
        all_section_path = [paper_section_path(section_title) for section_title in all_section_title]
        print('==============================================================')

        exist_file = get_exist_files(FILES_STORE)
        pattern = re.compile(r'<h2>.+?</h2>', flags=re.DOTALL)
        all_section = pattern.split(all_section.extract()[0])[1:]
        all_section = [re.search(r'<h3>.+?</h3>.*', string, flags=re.DOTALL).group(0)
                       for string in all_section]

        sec_pattern = re.compile(r'<h3>.+?</h3>.*?<ul class="DLauthors">'
                                 r'.+?</ul>.*?<div class="DLabstract">.*?</div>', flags=re.DOTALL)
        paper_pattern = re.compile(r'<h3>.*?<a class="DLtitleLink" href="(.+)" '
                                   r'title="Get the Full Text from the ACM Digital Library">(.+)</a>.*?</h3>',
                                   flags=re.DOTALL)
        user_agent_list = RotateUserAgentMiddleware.user_agent_list
        self.open_chrome()

        for section, section_path in zip(all_section, all_section_path):
            print('------------------------------------------')
            print(section_path)
            print('------------------------------------------')
            for paper in sec_pattern.findall(section):
                paper_info = paper_pattern.search(paper)
                paper_title = paper_info.group(2)
                paper_title = paper_title_preprocessing(paper_title)
                fake_paper_url = paper_info.group(1)
                paper_number = fake_paper_url.split('?')[-1]

                if paper_number in exist_file:
                    print('    ' + paper_number)
                    continue

                # Getting real paper url from fake paper url
                try:
                    self.driver.get(fake_paper_url)
                except TimeoutException:
                    print('--------  driver time out: %s' % fake_paper_url)
                    continue
                html = self.driver.page_source
                # print('----------------------------------------')
                paper_response = HtmlResponse(url=fake_paper_url, body=html, encoding='utf-8')
                # print('------------   paper response  ---------')
                selector = Selector(response=paper_response)
                opposite_url = selector.xpath('//*[@id="divmain"]/table/tbody/tr/td[1]'
                                              '/table[1]/tbody/tr/td[2]/a/@href').extract()[0]
                # print('----------------------------------------')
                paper_author = selector.xpath('//*[@id="divmain"]/table/tbody/tr/td[1]/'
                                              'table[2]/tbody/tr/td[2]/a/text()').extract()[0]

                print('------------------------------------------')
                try:
                    headers = {'User-Agent': random.choice(user_agent_list)}
                    paper_url = 'https://dl.acm.org/' + opposite_url
                    req = request.Request(paper_url, headers=headers)
                    pdf_data = request.urlopen(req, timeout=30).read()

                    filename = paper_number + 'SIGIR' + YEAR + '_' + paper_author + '_' + paper_title + '.pdf'
                    with open(os.path.join(section_path, filename), 'wb') as fw:
                        fw.write(pdf_data)
                    print(paper_number, paper_author, paper_title)
                except socket.timeout:
                    print('-----------  paper%s time out  -------------  skip  -----' % paper_number)
                except URLError:
                    print('-----------  url error, paper number: %s  -----------  skip  -----' % paper_number)
                # print('==================  save successfully  ========================')

        self.close_chrome()






