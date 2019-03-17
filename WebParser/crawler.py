from connection import Connection, Link
from collections import defaultdict
from typing import Generator, List, Tuple
from concurrent.futures import ThreadPoolExecutor
import re

MAX_STORY_NUMBER = 50#100000


class Crawler:
    def __init__(self, url:Link, n_workers: int = 4, **kwargs):
        self.conn = Connection(**kwargs)
        self.exec = ThreadPoolExecutor(max_workers = n_workers)
        self.main_url = url
        self.counter = 0

    def categories(self) -> Generator[Link, None, None]:
        cats = self.conn.children(self.main_url, '.nw-c-nav__wide .nw-o-link')
        for cat in cats:
            subcats = self.conn.children(cat, 'a.navigation-wide-list__link  ')
            if subcats:
                for subcat in subcats:
                    yield Link(subcat.url, cat.name + '/' + subcat.name)
            else:
                yield cat

    def get_stories(self) -> defaultdict:
        res = defaultdict(set)
        story_css = ['a.title-link', 'a.gs-c-promo-heading']
        for cat in self.categories():
            for css in story_css:
                stories = self.conn.children(cat, css, query=False)
                for story in stories:
                    if self.counter > MAX_STORY_NUMBER:
                        return res
                    res[story].add(cat.name)
                    self.counter += 1
        return res
    
    def get_tags(self, links: List[Link]) -> Generator[Tuple[Link, dict], None, None]:
        res = self.exec.map(lambda x: self.conn.meta_tags(x, ['og:title', 'og:description']), links)
        for link, tags in zip(links, res):
            if tags:
                yield link, tags

    def clean_text(self, text: str):
        return re.sub(r'[^a-zA-Z ]', '', text.strip())

    def traverse(self) -> Generator[dict, None, None]:
        for story, meta in self.get_stories().items():
            result = self.conn.children(story, 'a.title-link')
            for link, tags in self.get_tags(list(result)):
                yield {
                    'story': story.url,
                    'meta': list(meta),
                    'url': link.url,
                    'title': self.clean_text(tags['og:title']),
                    'descr': self.clean_text(tags['og:description'])
                }