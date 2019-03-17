"""
Module contains Spider for crawling news
"""

import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re

NEWS_FILE = re.sub(r'\W', '_', str(datetime.datetime.now())) + ".csv"


def clean_text(text: str) -> str:
    return re.sub(r'[^a-zA-Z ]', '', text.strip())


def is_valid_url(url: str) -> bool:
    if re.search(r'\d', url):
        return True
    return False


class BbcSpider(CrawlSpider):
    name = "bbc"
    allowed_domains = ["bbc.com"]
    start_urls = ['http://www.bbc.com/news/']

    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8',
    }

    rules = (Rule(LinkExtractor(allow="bbc.com/news"), callback="parse_item", follow=True),)

    def parse_item(self, response):
        visited_links = set()
        with open(NEWS_FILE, 'a') as f:
            for link in response.xpath('//a[contains(@class, "title-link")]'):
                url = response.url
                if url not in visited_links:
                    visited_links.add(url)
                    title = link.xpath("//meta[@property='og:title']/@content").extract()[0]
                    desc = link.xpath("//meta[@property='og:description']/@content").extract()[0]

                    if title and desc and is_valid_url(url):
                            f.write(f"{url},{clean_text(title)},{clean_text(desc)}\n")
