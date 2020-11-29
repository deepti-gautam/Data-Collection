# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html


import scrapy
import json


class DarkwebCrawlerItem(scrapy.Item):
    url = scrapy.Field()
    crawl_date = scrapy.Field()
    network = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field()
    images = scrapy.Field()
    authors = scrapy.Field()
    tags = scrapy.Field()
    movies = scrapy.Field()
    email_addresses = scrapy.Field()
    ip_address = scrapy.Field()
    contact_number = scrapy.Field()
    addresses = scrapy.Field()
    btc_addresses = scrapy.Field()
    eth_addresses = scrapy.Field()
    bch_addresses = scrapy.Field()
    ltc_addresses = scrapy.Field()
    xrp_addresses = scrapy.Field()
    onionlinks = scrapy.Field()
    meta_data = scrapy.Field()
    meta_description = scrapy.Field()
    meta_keywords = scrapy.Field()
    meta_lang = scrapy.Field()


    def to_json(self):
        return dict(
                url=self['url'],
                crawl_date=self['crawl_date'],
                network=self['network'],
                title=self['title'],
                text=self['text'],
                images=self['images'],
                authors=self['authors'],
                tags=self['tags'],
                movies=self['movies'],
                email_addresses=self['email_addresses'],
                contact_number=self['contact_number'],
                ip_address=self['ip_address'],
                addresses=self['addresses'],
                btc_addresses=self['btc_addresses'],
                eth_addresses=self['eth_addresses'],
                bch_addresses=self['bch_addresses'],
                ltc_addresses=self['ltc_addresses'],
                xrp_addresses=self['xrp_addresses'],
                onionlinks=self['onionlinks'],
                meta_data=self['meta_data'],
                meta_description=self['meta_description'],
                meta_keywords=self['meta_keywords'],
                meta_lang=self['meta_lang'],
        )   
