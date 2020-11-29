import scrapy
from scrapy.utils.project import get_project_settings
from DarkwebCrawler.items import DarkwebCrawlerItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from multiprocessing import Process
from scrapy.crawler import CrawlerProcess
from newspaper import Article
from datetime import datetime
import requests
import pytz
import socket
import re


class DarkWebSpider(CrawlSpider):  


    links = []

    with open('master_onion.txt') as file:
        for line in file:
            links.append(line)


    name = 'tordata'
    allowed_domains = ['com']
    start_urls = links
    rules = [
        Rule(LinkExtractor(allow_domains ='onion', deny_extensions=[
                                  'mng', 'pct', 'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pst', 'psp', 'tif',
                                  'tiff', 'ai', 'drw', 'dxf', 'eps', 'ps', 'svg',
                                  'mp3', 'wma', 'ogg', 'wav', 'ra', 'aac', 'mid', 'au', 'aiff',
                                  '3gp', 'asf', 'asx', 'avi', 'mov', 'mp4', 'mpg', 'qt', 'rm', 'swf', 'wmv','m4a',
                                  'css', 'pdf', 'doc', 'exe', 'bin', 'rss', 'zip', 'rar','php'
                                  ]), callback="parse_item", follow=True)
    ]


    def parse_item(self, response):

        article = Article(url=response.url)
        article.fetch_images = lambda:True

        article.set_html(response.text)
        article.parse()

        yield DarkwebCrawlerItem(
            url=response.url,
            crawl_date=datetime.now(pytz.utc),
            network='tor',
            title=article.title,
            text=article.text,
            images=article.images,
            authors=article.authors,
            tags=list(article.tags),
            movies=article.movies,
            contact_number=re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', str(article.text)),
            email_addresses=re.findall(r'[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}', str(article.text)),
            addresses=re.findall(r'(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}|0x[a-zA-Z0-9]{40}|[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}|(?:bitcoincash\:)?[qp][a-z0-9]{41}|(?:BITCOINCASH\:)?[QP][A-Z0-9]{41}',article.text),
            btc_addresses=re.findall(r'(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}', str(article.text)),
            eth_addresses=re.findall(r'0x[a-zA-Z0-9]{40}', str(article.text)),
            ltc_addresses=re.findall(r'[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}', str(article.text)),
            bch_addresses=re.findall(r'((?:bitcoincash:)?(q|p)[a-z0-9]{41})|'
                                '((?:BITCOINCASH:)?(Q|P)[A-Z0-9]{41})', str(article.text)),
            xrp_addresses = re.findall(r'r[0-9a-zA-Z]{24,34}', str(article.text)),
            onion_urls = re.findall(r'(?:http?://)?(?:https?://)?(?:www)?\S*?\.onion', str(response.text)),
            meta_data=[{key: value} for key, value in article.meta_data.items()],
            meta_description=article.meta_description,
            meta_keywords=article.meta_keywords,
            meta_lang=article.meta_lang)
