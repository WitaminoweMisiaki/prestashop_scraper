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
    # start_urls = [
    #     'https://www.empik.com/bestsellery/ksiazki',
    #     'https://www.empik.com/bestsellery/ebooki',
    #     'https://www.empik.com/bestsellery/ksiazki?searchCategory=3167&hideUnavailable=true&qtype=facetForm',
    #     'https://www.empik.com/bestsellery/prasa',
    #     'https://www.empik.com/bestsellery/muzyka',
    #     'https://www.empik.com/bestsellery/filmy',
    #     'https://www.empik.com/bestsellery/gry-i-konsole',
    #     'https://www.empik.com/bestsellery/szkolne-i-papiernicze',
    #     'https://www.empik.com/bestsellery/elektronika',
    #     'https://www.empik.com/bestsellery/zabawki',
    # ]

    books = [
        'https://www.empik.com/nowosci/ksiazki?searchCategory=31&hideUnavailable=true&start=%d&novelties=novelty' %
        i for i in range(1, 270, 30)]
    ebooks = [
        'https://www.empik.com/nowosci/ebooki?searchCategory=3501&hideUnavailable=true&start=%d&novelties=novelty' %
        i for i in range(1, 270, 30)]
    press = [
        'https://www.empik.com/nowosci/prasa?searchCategory=44&hideUnavailable=true&start=%d&novelties=novelty' %
        i for i in range(1, 270, 30)]
    music = [
        'https://www.empik.com/nowosci/muzyka?searchCategory=32&hideUnavailable=true&start=%d&novelties=novelty' %
        i for i in range(1, 270, 30)]

    start_urls = [
        'https://www.empik.com/nowosci/ksiazki?searchCategory=31&hideUnavailable=true&start=1&novelties=novelty']

    # rules = (
    #     Rule(LinkExtractor(allow=(), restrict_css=('.arrow',)), callback='parse_item', follow=True),
    # )
    # rules = (
    #     Rule(LinkExtractor(allow=(), restrict_css=()), callback='parse_item', follow=True),
    # )

    # list of tuples: (child category, parent category)
    # order is important!
    # categories = []
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

        title_feature = 'Tytuł:%s:0:1' % title

        price = response.xpath('//span[@class="productPriceInfo__price ta-price  withoutLpPromo"]/text()').extract()[0]
        price = price.strip()[:-3].replace(',', '.')

        author_feature = ''
        author_content = response.xpath('//div[@class="productBaseInfo__subtitle"]/span/@content').extract()[0]
        author_type = response.xpath('//td[@class="productDetailsLabel ta-label"]/text()').extract()[0]
        if author_type == 'Autor:':
            author_feature = 'Autor:%s:1:0' % author_content
        elif author_type == 'Wykonawca:':
            author_feature = 'Wykonawca:%s:1:0' % author_content

        publisher_feature = ''
        publisher_content = response.xpath('//div[@class="productBaseInfo__subtitle"]/span/@content').extract()[0]
        publisher_type = response.xpath('//td[@class="productDetailsLabel ta-label"]/text()').extract()[0]
        if publisher_type == 'Autor:':
            publisher_feature = 'Autor:%s:1:0' % publisher_content
        elif publisher_type == 'Wykonawca:':
            publisher_feature = 'Wykonawca:%s:1:0' % publisher_content

        # features = []
        # list(map(lambda x: self.encode(x), image_urls))

        description = response.xpath(
            '//div[@class="productComments productDescription ta-product-description "]//text()').extract()
        description = ' '.join(description).strip()
        description = '<p>%s</p>' % description
        description = description.replace('\n', '</p><p>')

        category = response.xpath('//div[@class="empikBreadcrumb"]//ul/li/a/span/text()').extract()[1:]
        self.scrape_categories_tree(category)
        category = category[-1]

        amount = str(random.randrange(0, 60))

        active = str(1)

        image_urls = response.xpath(
            '//div[contains(@class, "productGallery__mainImage")]/div/img/@src').extract()

        item['title'] = self.encode(title)
        item['title_feature'] = self.encode(title_feature)
        item['price'] = self.encode(price)
        item['author_feature'] = self.encode(author_feature)
        item['publisher_feature'] = self.encode(publisher_feature)
        item['description'] = self.encode(description)
        item['category'] = self.encode(category)
        item['amount'] = self.encode(amount)
        item["active"] = self.encode(active)
        item['image_urls'] = list(map(lambda x: self.encode(x), image_urls))

        yield item

    def scrape_categories_tree(self, category):
        for i in range(1, len(category)):
            # self.categories.append(['%s' % category[i], '%s' % category[i - 1]])
            self.categories.append(('%s' % self.encode(category[i]), '%s' % self.encode(category[i - 1])))

    def encode(self, string):
        # remove Latin1 \xa0 characters
        string = unicodedata.normalize('NFKC', string)
        return string.encode('utf-8').decode('utf-8')

    def closed(self, reason):
        self.remove_categories_duplicates()
        root_categories = self.separate_root_categories()

        field_names = ['id', 'category', 'parent_category', 'active', 'root_category']
        with open('../data/categories/%s.csv' % str(time.strftime("%Y-%m-%dT%H-%M-%S")), 'w', newline='') as file:
            # file.writelines('id,category,parent_category,active,root_category\n')
            csv_writer = csv.DictWriter(file, field_names)
            csv_writer.writeheader()

            # write root categories
            for i in range(len(root_categories)):
                # row = '{0},{1},2,1,0\n'.format(i + 3, root_categories[i][0])  # prestashop -> id=1 root, id=2 home
                # file.writelines(self.encode(row))
                csv_writer.writerow({'id': str(i + 3),
                                     'category': root_categories[i][0],
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
                    parent_id = 2  # TODO
                else:
                    parent_id = parent_id[0] + 3

                # row = '{0},{1},{2},1,0\n'.format(cat_id, cat[0], parent_id)
                # file.writelines(self.encode(row))
                csv_writer.writerow({'id': str(cat_id),
                                     'category': cat[0],
                                     'parent_category': str(parent_id),
                                     'active': str(1),
                                     'root_category': str(0)})

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

        root_categories = [[elem, ""] for elem in root_categories]
        return root_categories