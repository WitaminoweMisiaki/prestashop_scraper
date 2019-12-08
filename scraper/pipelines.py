# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem


class ScraperPipeline(object):
    def process_item(self, item, spider):
        return item


class ImagePathPipeline(object):
    def process_item(self, item, spider):
        images = item["images"]
        item["images"] = []

        for image in images:
            url = 'http://witaminowemisiaki.ml/imgimports/' + image["path"].split('/')[-1]
            url = url.encode('utf-8').decode('utf-8')
            item["images"].append(url)
        return item


class InvalidTextPipeline(object):
    def process_item(self, item, spider):
        description = item["description"]
        title = item["title"]
        if description.find('Dane szczegółowe'.encode('utf-8').decode('utf-8')) is not -1:
            raise DropItem("Description invalid format in %s" % item)
        elif title.find("#".encode('utf-8').decode('utf-8')) is not -1:
            raise DropItem("Title invalid format in %s" % item)

        return item
