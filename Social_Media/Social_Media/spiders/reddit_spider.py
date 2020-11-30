import scrapy
import re
from dateutil import parser
from Social_Media.items import SocialMediaItem
from newspaper import Article
from urllib.parse import urlencode
import json
import requests
from Social_Media.spiders.social_media.smedia_resources.subreddit import subreddits


class RedditSpider(scrapy.Spider):
    name = 'reddit'
    allowed_domains = ['reddit.com']

    def start_requests(self):
        params = {
               "rtj": "only",
               "redditWebClient": "web2x",
               "app": "web2x-client-production",
               "allow_over18": "",
               "include": "prefsSubreddit",
               "after": '',
               "dist": '',
               "layout": "card",
               "sort": "hot",
               "geo_filter": "IN"    
              }

        for subreddit in subreddits:
            base_url = 'https://gateway.reddit.com/desktopapi/v1/subreddits/{}?'.format(subreddit['subreddit_name'])
            params['after'] = subreddit['after']
            params['dist'] = subreddit['dist']
            url = base_url + urlencode(params)
            yield scrapy.Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        content = json.loads(response.text)
        for post in content['posts']:
            post_url = content['posts'][post]['permalink']
            yield response.follow(url=post_url,callback=self.parse_post)
        current_url = response.request.url
        split_url = current_url.split('?')
        new_base_url = split_url[0]+'?'
        new_param = split_url[1]

        param_new = {}
        parameter = [param_new.update({param.split('=')[0]: param.split('=')[-1]}) for param in new_param.split('&')] 
        json.dumps(param_new, indent=2)   
        param_new['after'] = content['token']
        param_new['dist'] = content['dist']
        next_page_url = new_base_url + urlencode(param_new)
        yield scrapy.Request(url=next_page_url,callback=self.parse_page)

    def parse_post(self, response):
        title = response.xpath(
            '//*[contains(concat( " ", @class, " " ), concat( " ", "_eYtD2XCVieq6emjKBH3m", " " ))]/text()'
            ).get(default='')
        upvoted = response.xpath(
            '//*[contains(concat( " ", @class, " " ), concat( " ", "t4Hq30BDzTeJ85vREX7_M", " " ))]//span/text()'
            ).get(default='') 
        post_timestamp = response.xpath(
            '//*[@data-click-id="timestamp"]/text()'
            ).get(default='')
        post_images = response.xpath(
            '//img[@alt="Post image"]/@src'
            ).getall()
        post_videos = response.xpath(
            '//a[contains(concat(" ",normalize-space(@class)," ")," _13svhQIUZqD9PVzFcLwOKT ")]/@href'
            ).getall()
        post_screenshot = response.xpath(
            '//*[contains(concat(" ",normalize-space(@class)," ")," D3IL3FD0RFy_mkKLPwL4 ")]'
            '//div[contains(concat(" ",normalize-space(@class)," ")," _292iotee39Lmt0MkQZ2hPV ")]'
            '//pre[contains(concat(" ",normalize-space(@class)," ")," _3GnarIQX9tD_qsgXkfSDz1 ")]'
            '//code[contains(concat(" ",normalize-space(@class)," ")," _34q3PgLsx9zIU5BiSOjFoM ")]/text()'
            ).getall()  
        post_text = response.xpath(
            '//*[contains(concat(" ",normalize-space(@class)," ")," D3IL3FD0RFy_mkKLPwL4 ")]'
            '//div[contains(concat(" ",normalize-space(@class)," ")," _292iotee39Lmt0MkQZ2hPV ")]'
            '//p[contains(concat(" ",normalize-space(@class)," ")," _1qeIAgB0cPwnLhDF9XSiJM ")]/text()').getall()
        post_tags = response.xpath(
            '//*[contains(concat(" ",normalize-space(@class)," ")," D3IL3FD0RFy_mkKLPwL4 ")]'
            '//div[contains(concat(" ",normalize-space(@class)," ")," _292iotee39Lmt0MkQZ2hPV ")]'
            '//p[contains(concat(" ",normalize-space(@class)," ")," _1qeIAgB0cPwnLhDF9XSiJM ")]'
            '//a[contains(concat(" ",normalize-space(@class)," ")," _3t5uN8xUmg0TOwRCOGQEcU ")]/text()').getall()  
        comment_text = response.xpath(
            '//div[contains(concat(" ",normalize-space(@class)," ")," _3cjCphgls6DH-irkVaA0GM ")]'
            '//p[contains(concat(" ",normalize-space(@class)," ")," _1qeIAgB0cPwnLhDF9XSiJM ")]/text()').getall()
        comment_count = response.xpath(
            '//*[contains(concat( " ", @class, " " ), concat( " ", "FHCV02u6Cp2zYL0fhQPsO", " " ))]/text()').getall()
        comment_timestamp = response.xpath(
            '//*[@id="CommentTopMeta--Created--t1_fxcpc90"]//span/text()').getall()
        read_more_comments = response.xpath(
            '//*[contains(concat(" ",normalize-space(@class)," ")," _23013peWUhznY89KuYPZKv ")]').getall()
        for comment in read_more_comments:
            comment_text = response.xpath(
                '//div[contains(concat(" ",normalize-space(@class)," ")," _3cjCphgls6DH-irkVaA0GM ")]'
                '//p[contains(concat(" ",normalize-space(@class)," ")," _1qeIAgB0cPwnLhDF9XSiJM ")]/text()').getall()
        article = Article(url=response.url)
        article.fetch_images = lambda: True
        article.set_html(response.text)
        article.parse()
    
        yield SocialMediaItem(
                url=response.url,
                keyword=requests.utils.urlparse(response.url).path.rsplit('/', 5)[1],
                post_id=requests.utils.urlparse(response.url).path.rsplit('/', 5)[3],
                title=title,
                title_addresses=re.findall(r'(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}|'
                    '0x[a-zA-Z0-9]{40}|'
                    '[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}|'
                    '(?:bitcoincash\:)?[qp][a-z0-9]{41}|'
                    '(?:BITCOINCASH\:)?[QP][A-Z0-9]{41}|r[0-9a-zA-Z]{24,34}', str(title)),
                post=post_text,
                mentions=' ',
                call_to_action=' ',
                bitcoin_addresses=re.findall(r'(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}', str(post_text)),
                ethereum_addresses=re.findall(r'0x[a-zA-Z0-9]{40}', str(post_text)),
                litecoin_addresses=re.findall(r'[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}', str(post_text)),
                bitcoincash_addresses=re.findall(r'((bitcoincash:)?(q|p)[a-z0-9]{41})|'
                    '((BITCOINCASH:)?(Q|P)[A-Z0-9]{41})', str(post_text)),
                ripple_addresses = re.findall(r'r[0-9a-zA-Z]{24,34}', str(post_text)),
                author_username='',
                author_fullname='',
                post_sentiment={
                                    'likes':upvoted,
                                    'code_snippet':post_screenshot,
                                    'comment_count': comment_count,
                                },
                post_timestamp=post_timestamp,
                post_images=post_images,
                post_videos=post_videos,
                comments=[dict(
                            comment_id='',
                            comment_text=comment_text,
                            mentions=' ',
                            call_to_action=' ',
                            btc_addresses=re.findall(r'(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}', str(comment_text)),
                            eth_addresses=re.findall(r'0x[a-zA-Z0-9]{40}', str(comment_text)),
                            ltc_addresses=re.findall(r'[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}', str(comment_text)),
                            bch_addresses=re.findall(r'((?:bitcoincash:)?(q|p)[a-z0-9]{41})|'
                                '((?:BITCOINCASH:)?(Q|P)[A-Z0-9]{41})', str(comment_text)),
                            xrp_addresses = re.findall(r'r[0-9a-zA-Z]{24,34}', str(comment_text)),
                            sentiment={'retweets': '', 'likes': ''},
                            timestamp=comment_timestamp,
                            images='',
                            videos='',
                            author={'username': '', 'fullname': ''}
                            )],   
                network='clearweb',
                source='reddit',
                html='' if IS_LOCAL_SERVER_ENV else article.html,
                images=article.images,
                tags=list(article.tags),
                movies=article.movies,
                meta_description=article.meta_description,
                meta_keywords=article.meta_keywords,
                meta_lang=article.meta_lang,
            )



