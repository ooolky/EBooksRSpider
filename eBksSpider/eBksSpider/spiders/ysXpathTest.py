# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import scrapy
import logging

from scrapy.utils.response import open_in_browser
from scrapy_splash import SplashRequest
from eBksSpider.items import eBookItem, eBookListItem


class YsxpathtestSpider(scrapy.Spider):
    name = "ysXpathTest"
    allowed_domains = ["www.yousuu.com"]
    start_urls = ['https://www.yousuu.com/booklists/?type=man&screen=comprehensive&page=1']
    MAX = 5
    begin = 1
    MAX_item = 2
    begin_item = 1

    def parse(self, response):
        for tr in response.xpath(
                '//*[@id="app"]/div[2]/section/div/div[2]/section[2]/div[2]/bookmainleftlayout/div/div'):
            new_book_list = eBookListItem()
            # URL
            urls = tr.xpath('./div/div[1]/div/a').extract()[0].split("\"")[1]
            url = "https://www.yousuu.com" + urls
            new_book_list['url'] = url
            # Publisher
            publishers = tr.xpath('./div/div[1]/div/div[2]/a/text()').extract()[0].strip()
            new_book_list['publisher'] = publishers
            new_book_list['bookList'] = []
            yield SplashRequest(url, meta={'item': new_book_list}, callback=self.parse_booklist,
                                args={'wait': '0.5'})

        # Get next page
        # if we get the same page
        if self.begin < self.MAX:
            self.begin += 1
            next_page_url = "https://www.yousuu.com/booklists/?type=man&screen=comprehensive&page=" + str(self.begin)
            logging.info("******************* list Count:" + str(self.begin))
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_booklist(self, response):
        new_book_list = response.meta['item']
        book_list_to_add = new_book_list['bookList']
        for booklistItem in response.xpath(
                '//*[@id="app"]/div[2]/section/div/section/div[2]/div/div[2]/div/div[1]/div'):
            # 是否存在id
            temp = booklistItem.xpath('./div[1]/div[2]/a/@href').extract()
            if len(temp) == 0:
                continue
            new_book = {}
            # id
            short_url = booklistItem.xpath('./div[1]/div[2]/a/@href').extract()[0]
            new_book['id'] = short_url.split("/")[2]
            # Name
            names = booklistItem.xpath('./div[1]/div[2]/a/text()').extract()[0]
            new_book['name'] = names
            # score
            scores = booklistItem.xpath('.//@aria-valuenow').extract()[0]
            new_book['score'] = int(scores)
            # comment
            comments = booklistItem.xpath('./div[2]/div[1]/div/span/text()').extract()
            if len(comments) > 0:
                new_book['comment'] = comments[0]

            book_list_to_add.append(new_book)
        new_book_list['bookList'] = book_list_to_add

        if self.begin_item < self.MAX_item:
            self.begin_item += 1
            next_page_url = response.url.split('?')[0] + "?page=" + str(self.begin_item)
            logging.info("******************* item Count:" + str(self.begin_item))
            yield SplashRequest(next_page_url, meta={'item': new_book_list}, callback=self.parse_booklist,
                                args={'wait': '0.5'})
        else:
            self.begin_item = 1
            yield new_book_list
