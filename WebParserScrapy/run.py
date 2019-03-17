from Spider import BbcSpider
from scrapy.crawler import CrawlerProcess


process = CrawlerProcess()
process.crawl(BbcSpider)
process.start() # the script will block here until the crawling is finished
