# -*- coding: utf-8 -*-
import logging
import re

import requests
import scrapy
from newspaper import Article
from scrapy.utils.project import get_project_settings

from scrapers.items import SocialMediaItem
from scrapers.spiders.social_media.smedia_resources.username import usernames

settings = get_project_settings()
IS_LOCAL_SERVER_ENV = settings.get("SERVER_ENV", "local") not in (
    "production",
    "staging",
)


class HashtagSpider(scrapy.Spider):
    name = "twitter_username"
    allowed_domains = ["twitter.com"]

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; "
        "compatible; Googlebot/2.1; "
        "+http://www.google.com/bot.html) Safari/537.36",
        "CONCURRENT_REQUESTS": 5,
        "DOWNLOAD_DELAY": 1,
        "LOG_LEVEL": "INFO",
    }

    ELASTICSEARCH_INDEX = "SOCIALMEDIA_ELASTICSEARCH_INDEX"
    ELASTICSEARCH_BUFFER_LENGTH = 100

    def start_requests(self):
        for user in usernames:
            if user:
                start_url = "https://mobile.twitter.com/{}".format(user["user_name"])
                yield scrapy.Request(
                    start_url, callback=self.find_tweets, dont_filter=True
                )

    def find_tweets(self, response):
        current_url = response.request.url
        tweets = response.xpath('//table[@class="tweet  "]/@href').getall()
        logging.info(f"{len(tweets)} tweets found")
        for tweet_id in tweets:
            tweet_id = re.findall("\d+", tweet_id)[-1]
            tweet_url = "https://twitter.com/anyuser/status/" + str(tweet_id)
            yield scrapy.Request(
                tweet_url, callback=self.parse_tweet, meta={"current_url": current_url}
            )

        next_page = response.xpath('//*[@class="w-button-more"]/a/@href').get(
            default=""
        )
        logging.info("Next page found:")
        if next_page != "":
            next_page = "https://mobile.twitter.com" + next_page
            yield scrapy.Request(next_page, callback=self.find_tweets)

    def parse_tweet(self, response):
        logging.info("Processing --> " + response.url)
        username = response.xpath(
            '//*[@class="permalink-inner permalink-tweet-container"]'
            '//*[@class="username u-dir u-textTruncate"]/b/text()'
        ).get(default="")
        full_name = response.xpath(
            '//*[@class="permalink-inner permalink-tweet-container"]//*[@class="FullNameGroup"]/strong/text()'
        ).get(default="")
        try:
            tweet_text = (
                response.xpath("//title/text()").get(default="").split(":")[1].strip()
            )
        except:
            tweet_text = " ".join(
                response.xpath(
                    '//*[contains(@class,"permalink-inner permalink-tweet-container")]'
                    '//*[@class="js-tweet-text-container"]/p//text()'
                ).getall()
            ).strip()
        image_list = response.xpath(
            '//*[contains(@class,"permalink-inner permalink-tweet-container")]'
            '//*[@class="AdaptiveMediaOuterContainer"]//img/@src'
        ).getall()
        post_video = response.xpath(
            '//*[contains(concat(" ",normalize-space(@class)," ")," js-tweet-text-container ")]'
            '//p[contains(concat(" ",normalize-space(@class)," ")," TweetTextSize--jumbo ")]'
            '//a[contains(concat(" ",normalize-space(@class)," ")," twitter-timeline-link ")]/@href'
        ).get(default="")
        date_time = response.xpath(
            '//*[contains(@class,"permalink-inner permalink-tweet-container")]'
            '//*[@class="js-tweet-details-fixer tweet-details-fixer"]'
            '/div[@class="client-and-actions"]/span[@class="metadata"]/span/text()'
        ).get(default="")
        retweets = response.xpath(
            '//*[contains(@class,"permalink-inner permalink-tweet-container")]'
            '//*[@class="js-tweet-details-fixer tweet-details-fixer"]'
            '/div[@class="js-tweet-stats-container tweet-stats-container"]'
            '//*[@class="js-stat-count js-stat-retweets stat-count"]/a/strong/text()'
        ).get(default="")
        likes = response.xpath(
            '//*[contains(@class,"permalink-inner permalink-tweet-container")]'
            '//*[@class="js-tweet-details-fixer tweet-details-fixer"]'
            '/div[@class="js-tweet-stats-container tweet-stats-container"]'
            '//*[@class="js-stat-count js-stat-favorites stat-count"]/a/strong/text()'
        ).get(default="")
        replies = response.xpath(
            '//*[contains(@class,"permalink-inner permalink-tweet-container")]'
            '//*[contains(@id,"profile-tweet-action-reply-count")]'
            "/parent::span/@data-tweet-stat-count"
        ).get(default="")
        call_to_action = re.findall(r"(?P<url>https?://[^\s]+)", tweet_text)
        mentions = re.findall("(^|[^@/w])@(/w{1,15})", tweet_text)
        if len(mentions) != 0:
            mentions = [i[1] for i in mentions]
        comments = response.xpath(
            '//a[contains(concat(" ",normalize-space(@class)," ")," tweet-timestamp ")]/@href'
        ).getall()
        current_url = response.meta["current_url"]
        logging.info(f"{len(comments)} comments found")
        for comment in comments:
            comment = re.findall("\d+", comment)[-1]
            comment_url = "https://twitter.com/anyuser/status/" + str(comment)
            yield scrapy.Request(
                comment_url,
                callback=self.parse_comment,
                meta={
                    "username": username,
                    "full_name": full_name,
                    "tweet_text": tweet_text,
                    "tweet_time": date_time,
                    "number_of_likes": likes,
                    "no_of_retweets": retweets,
                    "no_of_replies": replies,
                    "image_url": image_list,
                    "post_video": post_video,
                    "current_url": current_url,
                    "call_to_action": call_to_action,
                    "mentions": mentions,
                },
            )

    def parse_comment(self, response):
        comment_url = response.request.url
        logging.info("Processing --> " + response.url)
        comment_url = response.request.url
        comment_username = response.xpath(
            '//*[@class="permalink-inner permalink-tweet-container"]'
            '//*[@class="username u-dir u-textTruncate"]/b/text()'
        ).get(default="")
        comment_full_name = response.xpath(
            '//*[@class="permalink-inner permalink-tweet-container"]'
            '//*[@class="FullNameGroup"]/strong/text()'
        ).get(default="")
        try:
            comment_text = (
                response.xpath("//title/text()").get(default="").split(":")[1].strip()
            )
        except:
            comment_text = " ".join(
                response.xpath(
                    '//*[contains(@class,"permalink-inner permalink-tweet-container")]'
                    '//*[@class="js-tweet-text-container"]/p//text()'
                ).getall()
            ).strip()
        comment_image_list = response.xpath(
            '//*[contains(@class,"permalink-inner permalink-tweet-container")]'
            '//*[@class="AdaptiveMediaOuterContainer"]//img/@src'
        ).getall()
        comment_video = response.xpath(
            '//*[contains(concat(" ",normalize-space(@class)," ")," js-tweet-text-container ")]'
            '//p[contains(concat(" ",normalize-space(@class)," ")," TweetTextSize--jumbo ")]'
            '//a[contains(concat(" ",normalize-space(@class)," ")," twitter-timeline-link ")]/@href'
        ).get(default="")
        comment_date_time = response.xpath(
            '//*[contains(@class,"permalink-inner permalink-tweet-container")]'
            '//*[@class="js-tweet-details-fixer tweet-details-fixer"]'
            '/div[@class="client-and-actions"]/span[@class="metadata"]/span/text()'
        ).get(default="")
        comment_retweets = response.xpath(
            '//*[contains(@class,"permalink-inner permalink-tweet-container")]'
            '//*[@class="js-tweet-details-fixer tweet-details-fixer"]'
            '/div[@class="js-tweet-stats-container tweet-stats-container"]'
            '//*[@class="js-stat-count js-stat-retweets stat-count"]/a/strong/text()'
        ).get(default="")
        comment_likes = response.xpath(
            '//*[contains(@class,"permalink-inner permalink-tweet-container")]'
            '//*[@class="js-tweet-details-fixer tweet-details-fixer"]'
            '/div[@class="js-tweet-stats-container tweet-stats-container"]'
            '//*[@class="js-stat-count js-stat-favorites stat-count"]/a/strong/text()'
        ).get(default="")
        comment_call_to_action = re.findall(r"(?P<url>https?://[^\s]+)", comment_text)
        comment_mentions = re.findall("(^|[^@\w])@(\w{1,15})", comment_text)
        if len(comment_mentions) != 0:
            comment_mentions = [i[1] for i in comment_mentions]

        username = response.meta["username"]
        full_name = response.meta["full_name"]
        tweet_text = response.meta["tweet_text"]
        tweet_time = response.meta["tweet_time"]
        likes = response.meta["number_of_likes"]
        retweets = response.meta["no_of_retweets"]
        replies = response.meta["no_of_replies"]
        image_url = response.meta["image_url"]
        post_video = response.meta["post_video"]
        current_url = response.meta["current_url"]
        call_to_action = response.meta["call_to_action"]
        mentions = response.meta["mentions"]

        article = Article(url=response.url)
        article.fetch_images = lambda: True
        article.set_html(response.text)
        article.parse()

        yield SocialMediaItem(
            url=response.url,
            keyword=requests.utils.urlparse(current_url).path.rsplit("/", 2)[1],
            post_id=requests.utils.urlparse(response.url).path.rsplit("/", 2)[2],
            title="",
            title_addresses=re.findall(
                r"(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}|"
                "0x[a-zA-Z0-9]{40}|"
                "[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}|"
                "(?:bitcoincash\:)?[qp][a-z0-9]{41}|"
                "(?:BITCOINCASH\:)?[QP][A-Z0-9]{41}|"
                "r[0-9a-zA-Z]{24,34}",
                str(call_to_action),
            ),
            post=tweet_text,
            mentions=" ".join(mentions),
            call_to_action=" ".join(call_to_action),
            bitcoin_addresses=re.findall(
                r"(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}", str(tweet_text)
            ),
            ethereum_addresses=re.findall(r"0x[a-zA-Z0-9]{40}", str(tweet_text)),
            litecoin_addresses=re.findall(
                r"[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}", str(tweet_text)
            ),
            bitcoincash_addresses=re.findall(
                r"((bitcoincash:)?(q|p)[a-z0-9]{41})|((BITCOINCASH:)?(Q|P)[A-Z0-9]{41})",
                str(tweet_text),
            ),
            ripple_addresses=re.findall(r"r[0-9a-zA-Z]{24,34}", str(tweet_text)),
            total_addresses=re.findall(
                r"(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}|"
                "0x[a-zA-Z0-9]{40}|[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}|"
                "(?:bitcoincash\:)?[qp][a-z0-9]{41}|"
                "(?:BITCOINCASH\:)?[QP][A-Z0-9]{41}|"
                "r[0-9a-zA-Z]{24,34}",
                str(tweet_text),
            ),
            author_username=username,
            author_fullname=full_name,
            post_sentiment={
                "likes": str(likes),
                "retweets": str(retweets),
                "code_snippet": "",
                "comment_count": str(replies),
            },
            post_timestamp=str(tweet_time),
            post_images=image_url,
            post_videos=post_video,
            comments=[
                dict(
                    comment_id=requests.utils.urlparse(comment_url).path.rsplit("/", 2)[
                        2
                    ],
                    comment_text=comment_text,
                    mentions=" ".join(comment_mentions),
                    call_to_action=" ".join(comment_call_to_action),
                    cta_addresses=re.findall(
                        r"(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}|"
                        "0x[a-zA-Z0-9]{40}|"
                        "[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}|"
                        "(?:bitcoincash\:)?[qp][a-z0-9]{41}|"
                        "(?:BITCOINCASH\:)?[QP][A-Z0-9]{41}|"
                        "r[0-9a-zA-Z]{24,34}",
                        str(comment_call_to_action),
                    ),
                    mentions_addresses=re.findall(
                        r"(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}|"
                        "0x[a-zA-Z0-9]{40}|"
                        "[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}|"
                        "(?:bitcoincash\:)?[qp][a-z0-9]{41}|"
                        "(?:BITCOINCASH\:)?[QP][A-Z0-9]{41}|"
                        "r[0-9a-zA-Z]{24,34}",
                        str(mentions),
                    ),
                    btc_addresses=re.findall(
                        r"(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}", str(comment_text)
                    ),
                    eth_addresses=re.findall(r"0x[a-zA-Z0-9]{40}", str(comment_text)),
                    ltc_addresses=re.findall(
                        r"[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}", str(comment_text)
                    ),
                    bch_addresses=re.findall(
                        r"((?:bitcoincash:)?(q|p)[a-z0-9]{41})|"
                        "((?:BITCOINCASH:)?(Q|P)[A-Z0-9]{41})",
                        str(comment_text),
                    ),
                    xrp_addresses=re.findall(r"r[0-9a-zA-Z]{24,34}", str(comment_text)),
                    total_addresses=re.findall(
                        r"(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}|"
                        "0x[a-zA-Z0-9]{40}|"
                        "[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}|"
                        "(?:bitcoincash\:)?[qp][a-z0-9]{41}|"
                        "(?:BITCOINCASH\:)?[QP][A-Z0-9]{41}|"
                        "r[0-9a-zA-Z]{24,34}",
                        str(comment_text),
                    ),
                    sentiment={
                        "retweets": str(comment_retweets),
                        "likes": str(comment_likes),
                    },
                    timestamp=str(comment_date_time),
                    images=comment_image_list,
                    videos=comment_video,
                    author={
                        "username": comment_username,
                        "fullname": comment_full_name,
                    },
                )
            ],
            network="clearweb",
            source="twitter",
            html="" if IS_LOCAL_SERVER_ENV else article.html,
            images=article.images,
            tags=list(article.tags),
            movies=article.movies,
            meta_description=article.meta_description,
            meta_keywords=article.meta_keywords,
            meta_lang=article.meta_lang,
        )
