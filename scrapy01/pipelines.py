# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.files import FilesPipeline


class Scrapy01Pipeline(FilesPipeline):
    FILES_URLS_FIELD = 'url'
    filename = None

    def file_path(self, request, response=None, info=None):
        return self.filename

    def process_item(self, item, spider):
        self.filename = item['number'][0] + 'ACL2018_' + item['author'][0] + '_' + item['title'][0] + '.pdf'
        return super(Scrapy01Pipeline, self).process_item(item, spider)

