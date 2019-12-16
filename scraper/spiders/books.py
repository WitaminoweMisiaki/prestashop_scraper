# -*- coding: utf-8 -*-
import csv
import unicodedata
import random

import scrapy
from scrapy.spiders import CrawlSpider

from scraper.items import BookItem
from scraper.data_structures.tree import Tree


class BooksSpider(CrawlSpider):
    name = "books"
    allowed_domains = ["www.empik.com"]

    # each page has 30 products, 9 pages per each from 4 categories -> 30*9*4 = 1080 products
    start_urls = [
        # books
        'https://www.empik.com/nowosci/ksiazki?searchCategory=31&hideUnavailable=true&start=1&novelties=novelty',
        'https://www.empik.com/nowosci/ksiazki?searchCategory=31&hideUnavailable=true&start=31&novelties=novelty',
        'https://www.empik.com/nowosci/ksiazki?searchCategory=31&hideUnavailable=true&start=61&novelties=novelty',
        'https://www.empik.com/nowosci/ksiazki?searchCategory=31&hideUnavailable=true&start=91&novelties=novelty',
        'https://www.empik.com/nowosci/ksiazki?searchCategory=31&hideUnavailable=true&start=121&novelties=novelty',
        'https://www.empik.com/nowosci/ksiazki?searchCategory=31&hideUnavailable=true&start=151&novelties=novelty',
        'https://www.empik.com/nowosci/ksiazki?searchCategory=31&hideUnavailable=true&start=181&novelties=novelty',
        'https://www.empik.com/nowosci/ksiazki?searchCategory=31&hideUnavailable=true&start=211&novelties=novelty',
        'https://www.empik.com/nowosci/ksiazki?searchCategory=31&hideUnavailable=true&start=241&novelties=novelty',
        # ebooks
        'https://www.empik.com/nowosci/ebooki?searchCategory=3501&hideUnavailable=true&start=1&novelties=novelty',
        'https://www.empik.com/nowosci/ebooki?searchCategory=3501&hideUnavailable=true&start=31&novelties=novelty',
        'https://www.empik.com/nowosci/ebooki?searchCategory=3501&hideUnavailable=true&start=61&novelties=novelty',
        'https://www.empik.com/nowosci/ebooki?searchCategory=3501&hideUnavailable=true&start=91&novelties=novelty',
        'https://www.empik.com/nowosci/ebooki?searchCategory=3501&hideUnavailable=true&start=121&novelties=novelty',
        'https://www.empik.com/nowosci/ebooki?searchCategory=3501&hideUnavailable=true&start=151&novelties=novelty',
        'https://www.empik.com/nowosci/ebooki?searchCategory=3501&hideUnavailable=true&start=181&novelties=novelty',
        'https://www.empik.com/nowosci/ebooki?searchCategory=3501&hideUnavailable=true&start=211&novelties=novelty',
        'https://www.empik.com/nowosci/ebooki?searchCategory=3501&hideUnavailable=true&start=241&novelties=novelty',
        # press
        'https://www.empik.com/nowosci/prasa?searchCategory=44&hideUnavailable=true&start=1&novelties=novelty',
        'https://www.empik.com/nowosci/prasa?searchCategory=44&hideUnavailable=true&start=31&novelties=novelty',
        'https://www.empik.com/nowosci/prasa?searchCategory=44&hideUnavailable=true&start=61&novelties=novelty',
        'https://www.empik.com/nowosci/prasa?searchCategory=44&hideUnavailable=true&start=91&novelties=novelty',
        'https://www.empik.com/nowosci/prasa?searchCategory=44&hideUnavailable=true&start=121&novelties=novelty',
        'https://www.empik.com/nowosci/prasa?searchCategory=44&hideUnavailable=true&start=151&novelties=novelty',
        'https://www.empik.com/nowosci/prasa?searchCategory=44&hideUnavailable=true&start=181&novelties=novelty',
        'https://www.empik.com/nowosci/prasa?searchCategory=44&hideUnavailable=true&start=211&novelties=novelty',
        'https://www.empik.com/nowosci/prasa?searchCategory=44&hideUnavailable=true&start=241&novelties=novelty',

        # music
        'https://www.empik.com/nowosci/muzyka?searchCategory=32&hideUnavailable=true&start=1&novelties=novelty',
        'https://www.empik.com/nowosci/muzyka?searchCategory=32&hideUnavailable=true&start=31&novelties=novelty',
        'https://www.empik.com/nowosci/muzyka?searchCategory=32&hideUnavailable=true&start=61&novelties=novelty',
        'https://www.empik.com/nowosci/muzyka?searchCategory=32&hideUnavailable=true&start=91&novelties=novelty',
        'https://www.empik.com/nowosci/muzyka?searchCategory=32&hideUnavailable=true&start=121&novelties=novelty',
        'https://www.empik.com/nowosci/muzyka?searchCategory=32&hideUnavailable=true&start=151&novelties=novelty',
        'https://www.empik.com/nowosci/muzyka?searchCategory=32&hideUnavailable=true&start=181&novelties=novelty',
        'https://www.empik.com/nowosci/muzyka?searchCategory=32&hideUnavailable=true&start=211&novelties=novelty',
        'https://www.empik.com/nowosci/muzyka?searchCategory=32&hideUnavailable=true&start=241&novelties=novelty'
    ]
    categories_tree = Tree()

    def parse(self, response):
        item_links = response.xpath('//a[@class="seoTitle"]/@href').extract()

        for item_link in item_links:
            item_link = item_link.strip()
            item_link = 'https://www.empik.com' + item_link
            yield scrapy.Request(item_link, callback=self.parse_detail_page)

    def parse_detail_page(self, response):
        item = BookItem()

        title = response.xpath('//h1[@class="productBaseInfo__title ta-product-title"]/text()').extract()
        title = ''.join(title).strip()

        features = str()
        title_feature = 'Tytuł:%s:1:1' % title
        features = '%s%s;' % (features, title_feature)

        price = response.xpath('//span[@class="productPriceInfo__price ta-price  withoutLpPromo"]/text()').extract()[0]
        price = price.strip()[:-3].replace(',', '.')

        author_feature = ''
        author_content = response.xpath('//div[@class="productBaseInfo__subtitle"]/span/@content').extract()
        author_type = response.xpath('//td[@class="productDetailsLabel ta-label"]/text()').extract()

        # extract author info if it exists
        author_content = author_content[0] if author_content else ''
        author_type = author_type[0] if author_type else ''

        if author_type == 'Autor:':
            author_feature = 'Autor:%s:2:0' % author_content
        elif author_type == 'Wykonawca:':
            author_feature = 'Wykonawca:%s:2:0' % author_content

        features = '%s%s;' % (features, author_feature)

        # types as one column of table
        attributes_type = response.xpath(
            '//tr[@class="row--text row--text  attributeName ta-attribute-row"]/td/text()').extract()
        # remove empty values
        attributes_type = list(filter(None, list(map(lambda x: x.strip(), attributes_type))))

        publisher_feature = ''
        # get indexes of strings which contain phrases
        if_publisher = [i for i, attr_type in enumerate(attributes_type) if 'Wydawnictwo' in attr_type]
        if_distributor = [i for i, attr_type in enumerate(attributes_type) if 'Dystrybutor' in attr_type]
        if if_publisher:
            publisher_content = response.xpath('//tr[td="\nWydawnictwo:\n"]/td[2]//text()').extract()
            publisher_content = list(filter(None, list(map(lambda x: x.strip(), publisher_content))))
            # values on website are duplicated
            publisher_content = list(set(publisher_content))[0]
            publisher_content = ''.join(publisher_content)
            publisher_feature = 'Wydawnictwo:%s:3:0' % publisher_content
        elif if_distributor:
            publisher_content = response.xpath('//tr[td="\nDystrybutor:\n"]/td[2]//text()').extract()
            publisher_content = list(filter(None, list(map(lambda x: x.strip(), publisher_content))))
            # values on website are duplicated
            publisher_content = list(set(publisher_content))[0]
            publisher_content = ''.join(publisher_content)
            publisher_feature = 'Dystrybutor:%s:3:0' % publisher_content

        features = '%s%s;' % (features, publisher_feature)

        media_type_feature = ''
        # get indexes of strings which contain phrases
        if_pages_number = [i for i, attr_type in enumerate(attributes_type) if 'Liczba stron' in attr_type]
        if_media = [i for i, attr_type in enumerate(attributes_type) if 'Nośnik' in attr_type]
        if if_pages_number:
            media_type_content = response.xpath('//tr[td="\nLiczba stron:\n"]/td[2]//text()').extract()
            media_type_content = list(filter(None, list(map(lambda x: x.strip(), media_type_content))))
            # values on website are duplicated
            media_type_content = list(set(media_type_content))[0]
            media_type_feature = 'Liczba stron:%s:4:1' % media_type_content
        elif if_media:
            media_type_content = response.xpath('//tr[td="\nNośnik:\n"]/td[2]//text()').extract()
            media_type_content = list(filter(None, list(map(lambda x: x.strip(), media_type_content))))
            # values on website are duplicated
            media_type_content = list(set(media_type_content))[0]
            media_type_content = ''.join(media_type_content)
            media_type_feature = 'Nośnik:%s:4:0' % media_type_content

        features = '%s%s;' % (features, media_type_feature)

        description = response.xpath(
            '//div[@class="productComments productDescription ta-product-description "]//text()')
        description = list(
            map(lambda y: '<p>%s</p>' % y, list(filter(None, list(map(lambda x: x.extract().strip(), description))))))
        description = ''.join(description)

        category = response.xpath('//div[@class="empikBreadcrumb"]//ul/li/a/span/text()').extract()[1:]
        category = str(self.create_categories_tree(category))

        amount = str(random.randrange(0, 60))

        active = str(1)

        image_urls = response.xpath(
            '//div[contains(@class, "productGallery__mainImage")]/div/img/@src').extract()

        item['title'] = self.encode(title)
        item['price'] = self.encode(price)
        item['features'] = self.encode(features)
        item['description'] = self.encode(description)
        item['category'] = self.encode(category)
        item['amount'] = self.encode(amount)
        item["active"] = self.encode(active)
        item['image_urls'] = list(map(lambda x: self.encode(x), image_urls))

        yield item

    def create_categories_tree(self, categories_path):
        category_id = self.categories_tree.add_path(categories_path)
        return category_id

    def encode(self, string):
        # remove Latin1 \xa0 characters
        string = unicodedata.normalize('NFKC', string)
        return string.encode('utf-8').decode('utf-8')

    def closed(self, reason):
        self.write_categories_to_csv()

    def write_categories_to_csv(self):
        field_names = ['id', 'category', 'parent_category', 'active', 'root_category']
        with open('../data/categories/final_categories.csv', 'w', newline='', encoding='utf-8') as file:
            csv_writer = csv.DictWriter(file, field_names)
            csv_writer.writeheader()

            for root_category in self.categories_tree.root.children:
                csv_writer.writerow({'id': str(root_category.uid),
                                     'category': self.encode(root_category.name),
                                     'parent_category': str(root_category.parent_uid),
                                     'active': str(1),
                                     'root_category': str(0)})
                for category in self.categories_tree.get_children_nodes(root_category):
                    csv_writer.writerow({'id': str(category.uid),
                                         'category': self.encode(category.name),
                                         'parent_category': str(category.parent_uid),
                                         'active': str(1),
                                         'root_category': str(0)})
