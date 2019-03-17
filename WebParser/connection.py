from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import List, Generator
from collections import namedtuple
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, ErrorInResponseException, TimeoutException
from parser import parse_og_tags
import os

os.environ['MOZ_HEADLESS'] = '1'
FIREFOXDRIVER_PATH = os.path.dirname(os.path.abspath(__file__)) + '/geckodriver'


def drop_query(url: str) -> str:
    return urlparse(url)._replace(query=None).geturl()


Link = namedtuple('Link', ['url', 'name'], defaults = [None, ''])


class Connection:
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0'
    }

    def __init__(self, parser: str = 'html.parser') -> None:
        self.browser = webdriver.Firefox(executable_path=FIREFOXDRIVER_PATH)
        self.parser = parser
    
    def get(self, link: Link) -> BeautifulSoup:
        try:
            self.browser.get(link.url)
            return BeautifulSoup(self.browser.page_source, self.parser)
        except (WebDriverException, ErrorInResponseException, TimeoutException) as e:
            print(e.__class__.__name__, "at", link.url)
    
    def children(self, link: Link, css: str, query: bool = True) -> Generator[Link, None, None]:
        page = self.get(link)
        if page:
            for match in page.select(css):
                if '/news/' in match['href']:
                    url = urljoin(link.url, match['href'])
                    print(url)
                    if not query:
                        url = drop_query(url)
                    yield Link(url, match.text)

    def meta_tags(self, link: Link, tags: List[str]) -> dict:
        try:
            self.browser.get(link.url)
            return parse_og_tags(self.browser.page_source, tags)
        except (WebDriverException, ErrorInResponseException, TimeoutException) as e:
            print(e.__class__.__name__, "at", link.url)
