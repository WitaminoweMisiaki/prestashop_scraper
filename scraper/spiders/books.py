# -*- coding: utf-8 -*-
import csv
import unicodedata
import random
import time

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from scraper.items import BookItem


class BooksSpider(CrawlSpider):
    name = "books"

    allowed_domains = ["www.empik.com"]

    # each page has 30 products, 9 pages per each from 4 categories -> 30*9*4 = 1080 products
    start_urls = [
        # books
        'https://www.empik.com/nowosci/ksiazki?searchCategory=31&hideUnavailable=true&start=1&novelties=novelty',
        # 'https://www.empik.com/nowosci/ksiazki?searchCategory=31&hideUnavailable=true&start=31&novelties=novelty',
        # 'https://www.empik.com/nowosci/ksiazki?searchCategory=31&hideUnavailable=true&start=61&novelties=novelty',
        # 'https://www.empik.com/nowosci/ksiazki?searchCategory=31&hideUnavailable=true&start=91&novelties=novelty',
        # 'https://www.empik.com/nowosci/ksiazki?searchCategory=31&hideUnavailable=true&start=121&novelties=novelty',
        # 'https://www.empik.com/nowosci/ksiazki?searchCategory=31&hideUnavailable=true&start=151&novelties=novelty',
        # 'https://www.empik.com/nowosci/ksiazki?searchCategory=31&hideUnavailable=true&start=181&novelties=novelty',
        # 'https://www.empik.com/nowosci/ksiazki?searchCategory=31&hideUnavailable=true&start=211&novelties=novelty',
        # 'https://www.empik.com/nowosci/ksiazki?searchCategory=31&hideUnavailable=true&start=241&novelties=novelty',
        # # ebooks
        # 'https://www.empik.com/nowosci/ebooki?searchCategory=3501&hideUnavailable=true&start=1&novelties=novelty',
        # 'https://www.empik.com/nowosci/ebooki?searchCategory=3501&hideUnavailable=true&start=31&novelties=novelty',
        # 'https://www.empik.com/nowosci/ebooki?searchCategory=3501&hideUnavailable=true&start=61&novelties=novelty',
        # 'https://www.empik.com/nowosci/ebooki?searchCategory=3501&hideUnavailable=true&start=91&novelties=novelty',
        # 'https://www.empik.com/nowosci/ebooki?searchCategory=3501&hideUnavailable=true&start=121&novelties=novelty',
        # 'https://www.empik.com/nowosci/ebooki?searchCategory=3501&hideUnavailable=true&start=151&novelties=novelty',
        # 'https://www.empik.com/nowosci/ebooki?searchCategory=3501&hideUnavailable=true&start=181&novelties=novelty',
        # 'https://www.empik.com/nowosci/ebooki?searchCategory=3501&hideUnavailable=true&start=211&novelties=novelty',
        # 'https://www.empik.com/nowosci/ebooki?searchCategory=3501&hideUnavailable=true&start=241&novelties=novelty',
        # # press
        # 'https://www.empik.com/nowosci/prasa?searchCategory=44&hideUnavailable=true&start=1&novelties=novelty',
        # 'https://www.empik.com/nowosci/prasa?searchCategory=44&hideUnavailable=true&start=31&novelties=novelty',
        # 'https://www.empik.com/nowosci/prasa?searchCategory=44&hideUnavailable=true&start=61&novelties=novelty',
        # 'https://www.empik.com/nowosci/prasa?searchCategory=44&hideUnavailable=true&start=91&novelties=novelty',
        # 'https://www.empik.com/nowosci/prasa?searchCategory=44&hideUnavailable=true&start=121&novelties=novelty',
        # 'https://www.empik.com/nowosci/prasa?searchCategory=44&hideUnavailable=true&start=151&novelties=novelty',
        # 'https://www.empik.com/nowosci/prasa?searchCategory=44&hideUnavailable=true&start=181&novelties=novelty',
        # 'https://www.empik.com/nowosci/prasa?searchCategory=44&hideUnavailable=true&start=211&novelties=novelty',
        # 'https://www.empik.com/nowosci/prasa?searchCategory=44&hideUnavailable=true&start=241&novelties=novelty',
        #
        # # music
        # 'https://www.empik.com/nowosci/muzyka?searchCategory=32&hideUnavailable=true&start=1&novelties=novelty',
        # 'https://www.empik.com/nowosci/muzyka?searchCategory=32&hideUnavailable=true&start=31&novelties=novelty',
        # 'https://www.empik.com/nowosci/muzyka?searchCategory=32&hideUnavailable=true&start=61&novelties=novelty',
        # 'https://www.empik.com/nowosci/muzyka?searchCategory=32&hideUnavailable=true&start=91&novelties=novelty',
        # 'https://www.empik.com/nowosci/muzyka?searchCategory=32&hideUnavailable=true&start=121&novelties=novelty',
        # 'https://www.empik.com/nowosci/muzyka?searchCategory=32&hideUnavailable=true&start=151&novelties=novelty',
        # 'https://www.empik.com/nowosci/muzyka?searchCategory=32&hideUnavailable=true&start=181&novelties=novelty',
        # 'https://www.empik.com/nowosci/muzyka?searchCategory=32&hideUnavailable=true&start=211&novelties=novelty',
        # 'https://www.empik.com/nowosci/muzyka?searchCategory=32&hideUnavailable=true&start=241&novelties=novelty'
    ]

    # rules = (
    #     Rule(LinkExtractor(allow=(), restrict_css=('.arrow',)), callback='parse_item', follow=True),
    # )

    # list of tuples: (child category, parent category)
    # order is important!
    categories = []

    # def parse_item(self, response):
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

        # content as one column of table
        # attributes_content = response.xpath(
        #     '//tr[@class="row--text row--text  attributeName ta-attribute-row"]/td/span//text()').extract()
        # remove empty values
        # attributes_content = list(filter(None, list(map(lambda x: x.strip(), attributes_content))))

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
            # publisher_feature = 'Wydawnictwo:%s:3:0' % attributes_content[if_publisher[0]]
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
            # media_type_feature = 'Liczba stron:%s:4:1' % attributes_content[if_pages_number[0]]
            media_type_feature = 'Liczba stron:%s:4:1' % media_type_content
        elif if_media:
            media_type_content = response.xpath('//tr[td="\nNośnik:\n"]/td[2]//text()').extract()
            media_type_content = list(filter(None, list(map(lambda x: x.strip(), media_type_content))))
            # values on website are duplicated
            media_type_content = list(set(media_type_content))[0]
            media_type_content = ''.join(media_type_content)
            # media_type_feature = 'Nośnik:%s:4:0' % attributes_content[if_media[0]]
            media_type_feature = 'Nośnik:%s:4:0' % media_type_content

        features = '%s%s;' % (features, media_type_feature)

        description = response.xpath(
            '//div[@class="productComments productDescription ta-product-description "]//text()').extract()
        description = ' '.join(description).strip()
        description = '<p>%s</p>' % description
        description = description.replace('\n', '</p><p>')

        category = response.xpath('//div[@class="empikBreadcrumb"]//ul/li/a/span/text()').extract()[1:]
        self.scrape_categories_tree(category)
        category = '~~'.join(category)
        # category = category[-1]

        amount = str(random.randrange(0, 60))

        active = str(1)

        image_urls = response.xpath(
            '//div[contains(@class, "productGallery__mainImage")]/div/img/@src').extract()

        item['title'] = self.encode(title)
        item['price'] = self.encode(price)
        item['features'] = self.encode(features)
        item['description'] = self.encode(description)
        item['category'] = self.encode(category)
        # item['category'] = list(map(lambda x: self.encode(x), category))
        item['amount'] = self.encode(amount)
        item["active"] = self.encode(active)
        item['image_urls'] = list(map(lambda x: self.encode(x), image_urls))

        yield item

    def scrape_categories_tree(self, category):
        for i in range(1, len(category)):
            self.categories.append(('%s' % category[i], '%s' % category[i - 1]))

    def encode(self, string):
        # remove Latin1 \xa0 characters
        string = unicodedata.normalize('NFKC', string)
        return string.encode('utf-8').decode('utf-8')

    def closed(self, reason):
        self.remove_categories_duplicates()
        root_categories = self.separate_root_categories()

        field_names = ['id', 'category', 'parent_category', 'active', 'root_category']
        # with open('../data/categories/%s.csv' % str(time.strftime("%Y-%m-%dT%H-%M-%S")), 'w', newline='',
        #           encoding='utf-8') as file:
        with open('../data/categories/final_categoriess.csv', 'w', newline='', encoding='utf-8') as file:
            csv_writer = csv.DictWriter(file, field_names)
            csv_writer.writeheader()

            # write root categories
            for i in range(len(root_categories)):
                csv_writer.writerow({'id': str(i + 3),
                                     'category': self.encode(root_categories[i][0]),
                                     'parent_category': str(2),
                                     'active': str(1),
                                     'root_category': str(0)})

            # write other categories
            for cat in self.categories:
                cat_id = [i for i, cat_tuple in enumerate(root_categories) if
                          cat_tuple[0] == cat[0] and cat_tuple[1] == cat[1]]
                if not cat_id:
                    root_categories.append([cat[0], cat[1]])
                    cat_id = len(root_categories) + 2
                else:
                    cat_id = cat_id[0] + 3

                parent_id = [i for i, cat_tuple in enumerate(root_categories) if
                             cat_tuple[1] != cat[1] and cat_tuple[0] == cat[1]]
                if not parent_id:
                    parent_id = 2  # should not enter here TODO
                else:
                    parent_id = parent_id[0] + 3

                csv_writer.writerow({'id': str(cat_id),
                                     'category': self.encode(cat[0]),
                                     'parent_category': str(parent_id),
                                     'active': str(1),
                                     'root_category': str(0)})
        self.correct_csv_file()

    def remove_categories_duplicates(self):
        for i in range(len(self.categories)):
            for j in range(i, len(self.categories)):
                if i != j and self.categories[i] and self.categories[j] and self.categories[i][0] == self.categories[j][
                    0] and self.categories[i][1] == self.categories[j][1]:
                    self.categories[j] = []

        self.categories = [list for list in self.categories if list != []]

    def separate_root_categories(self):
        # do not change set
        root_categories = set()

        for parent_cat in self.categories:
            root_flag = True
            for child_cat in self.categories:
                # check if there is parent category for category
                if child_cat[0] == parent_cat[1]:
                    root_flag = False
                    break
            if root_flag is True:
                root_categories.add(parent_cat[1])

        root_categories.add("Muzyka")
        root_categories = [[elem, ""] for elem in root_categories]
        return root_categories

    def correct_csv_file(self):
        with open('../data/books/final_products.csv', newline='', encoding='utf-8') as in_file:
            csv_reader = csv.reader(in_file.readlines())

        with open('../data/books/final_products.csv', 'w', newline='', encoding='utf-8') as out_file:
            csv_writer = csv.writer(out_file)
            header = next(csv_reader)
          #  csv_writer.writerow(header)
            for line in csv_reader:
                category_id = self.find_category_id(line[4])
                line[4] = category_id
                csv_writer.writerow(line)

    def find_category_id(self, input_categories):
        categories = input_categories.split('~~')
        categories.reverse()

        cat_id = []
        with open('../data/categories/final_categoriess.csv', newline='', encoding='utf-8') as in_file:
            csv_reader = csv.reader(in_file.readlines())
            for line in csv_reader:
                if line[1] == categories[0]:
                    cat_id.append(self.find(categories[1:], line[2], line[0]))

        cat_id = list(filter(None, cat_id))[0]
        return cat_id

    def find(self, categories, parent_category, cat_id):
        if parent_category == '2':
            return cat_id
        else:
            with open('../data/categories/final_categoriess.csv', newline='', encoding='utf-8') as in_file:
                csv_reader = csv.reader(in_file.readlines())
                for line in csv_reader:
                    if line[0] == parent_category and line[1] == categories[0]:
                        return self.find(categories[1:], line[2], cat_id)

            return None
