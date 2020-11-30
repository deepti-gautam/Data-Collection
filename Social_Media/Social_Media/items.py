# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SocialMediaItem(scrapy.Item):
    url = scrapy.Field()
    keyword = scrapy.Field()
    post_id = scrapy.Field()
    title = scrapy.Field()
    title_addresses = scrapy.Field()
    post = scrapy.Field()
    bitcoin_addresses = scrapy.Field()
    ethereum_addresses = scrapy.Field()
    litecoin_addresses = scrapy.Field()
    bitcoincash_addresses = scrapy.Field()
    ripple_addresses = scrapy.Field()
    author_username = scrapy.Field()
    author_fullname = scrapy.Field()
    post_sentiment = scrapy.Field()
    post_timestamp = scrapy.Field()
    post_images = scrapy.Field()
    post_videos = scrapy.Field()
    comments = scrapy.Field()
    network = scrapy.Field()
    source = scrapy.Field()
    html = scrapy.Field()
    images = scrapy.Field()
    tags = scrapy.Field()
    movies = scrapy.Field()
    meta_data = scrapy.Field()
    meta_description = scrapy.Field()
    meta_keywords = scrapy.Field()
    meta_lang = scrapy.Field()
    crawl_date = scrapy.Field()

    def to_json(self):
        return dict(
                url=self['url'],
                keyword=self['keyword'],
                post_id=self['post_id'],
                title=self['title'],
                title_addresses=self['title_addresses'],
                post=self['post'],
                bitcoin_addresses=self['bitcoin_addresses'],
                ethereum_addresses=self['ethereum_addresses'],
                litecoin_addresses=self['litecoin_addresses'],
                bitcoincash_addresses=self['bitcoincash_addresses'],
                ripple_addresses=self['ripple_addresses'],
                author_username=self['author_username'],
                author_fullname=self['author_fullname'],
                post_sentiment=self['post_sentiment'],
                post_timestamp=self['post_timestamp'],
                post_images=self['post_images'],
                post_videos=self['post_videos'],
                comments=self['comments'],
                network=self['network'],
                source=self['source'],
                html=self['html'],
                images=self['images'],
                tags=self['tags'],
                movies=self['movies'],
                meta_description=self['meta_description'],
                meta_keywords=self['meta_keywords'],
