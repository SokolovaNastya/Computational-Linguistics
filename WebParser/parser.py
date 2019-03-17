from html.parser import HTMLParser
from typing import List, Tuple
from bs4 import BeautifulSoup, SoupStrainer
from ftfy import fix_text
import re


def preprocess(string: str) -> str:
    string = fix_text(string)
    if re.search('[a-zA-Z]', string):
        string = BeautifulSoup(string, "html.parser").text
        return " ".join(string.split())


class OGParser(HTMLParser):
    def __init__(self, tags: List[str]):
        HTMLParser.__init__(self)
        self.tags = dict.fromkeys(tags, None)

    def handle_starttag(self, html_tag: str, attrs: List[Tuple[str]]) -> bool:
        attrs = dict(attrs)
        if html_tag == 'meta':
            for og_tag in self.tags.keys():
                if attrs.get('property') == og_tag and attrs.get('content'):
                    self.tags[og_tag] = preprocess(attrs.get('content'))
                    if all(self.tags.values()):
                        return True
    
    def handle_endtag(self, html_tag: str) -> bool:
        if html_tag == 'head':
            return True


def parse_og_tags(page_source: str, tags: List[str], chunk_size: int = 128) -> dict:
    parser = OGParser(tags)

    page = BeautifulSoup(page_source, "html.parser", parse_only=SoupStrainer('meta'))
    if page:
        for tag in tags:
            match = page.find('meta', property=tag, content=True)
            if match:
                parser.tags[tag] = match['content']

        if all(parser.tags.values()):
            return parser.tags