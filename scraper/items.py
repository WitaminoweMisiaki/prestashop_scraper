# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    price = scrapy.Field()
    features = scrapy.Field()
    description = scrapy.Field()
    category = scrapy.Field()
    amount = scrapy.Field()
    active = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()

    pass
