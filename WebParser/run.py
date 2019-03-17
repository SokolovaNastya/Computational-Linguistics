import datetime
from csv import DictWriter
from crawler import Crawler
from connection import Link
import time

URL = 'https://www.bbc.com/news'
filename = str(datetime.datetime.now()).replace(" ", "_") + '.csv'

with open(filename, 'w') as f:
    start_time = time.time()
    fieldnames = ['story', 'meta', 'url', 'title', 'descr']
    writer = DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    story_set = set()
    for row in Crawler(Link(URL)).traverse():
        pair = (row.get('title'),row.get('descr'))
        if pair not in story_set:
            story_set.add(pair)
            writer.writerow(row)
    print(time.time() - start_time)