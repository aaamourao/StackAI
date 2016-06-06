#!/usr/bin/python
# coding: utf-8

# To use this project execute it with:
# scrapy runspider stack_spider.py

import scrapy
import json
import codecs
import time
import re

#from crawler.items import VidInfo
from functools import partial
from os.path import isfile, isdir, splitext, dirname, exists, basename
from os import makedirs, listdir, rmdir

MAX_QUESTIONS=10

innerHtml = re.compile('\A<[^>]*>(.*)</[^>]*>\Z', re.DOTALL)
def getInner(html):
    return innerHtml.match(html).group(1)

class VidSpider(scrapy.Spider):
    # Required attributes:
    name = "videos"
    start_urls = [
        # Looking for the newest questions:
        "http://stackoverflow.com/questions?sort=newest"
      ]

    pages = []

    # Pre-load some files/data:
    def __init__(self):
        pass

    count = 0
    
    # Parse the starting page
    # Save data on self attributes
    # and yield a parse request when you need a link to be
    # parsed by other function.
    def parse(self, resp):

        for link in resp.css('#mainbar a.question-hyperlink::attr(href)').extract():
            if self.count == 10:
                break
            else:
                self.count += 1

            # Schedule it to be parsed:
            yield scrapy.Request(
                resp.urljoin(link),
                callback=partial(self.parseQuestion)
              )

    def parseQuestion(self, resp):
        page = {}
        page['url'] = resp.url
        page['title'] = resp.css('#question-header a::text').extract_first()
        page['up_votes'] = resp.css('#question span.vote-count-post::text').extract_first()
        page['tags'] = resp.css('.post-taglist .post-tag::text').extract()

        aux = list( resp.css('td[style] p.label-key') )
        page['post_date'] = aux[0].css('::attr(title)').extract_first()
        page['views'] = int((aux[1].css('b').re('b>([0-9]+) ')[:1] or [None])[0])

        page['author_name'] = resp.css('.user-details a::text').extract_first()
        page['author_rep'] = int(resp.css('.reputation-score::text').extract_first().replace(',',''))

        # Save that page:
        self.pages.append(page)

    # To download data be it a image, video or an
    # html page, just Request it and set download
    # as a callback with patial(self.download, "path/to/file")
    def download(self, path, resp): 
        print  
        print "  Downloading %s!" % path 
        print 
        # Make sure path exists: 
        if not isdir(dirname(path)): 
            makedirs(dirname(path))        
        with open(path, 'wb') as file: 
            file.write(resp.body) 

    # Save the data before quit:
    def closed(self, reason):

        # To write utf-8 files do as described bellow:
        with codecs.open('crawled_questions.json', 'w', 'utf-8') as file:
            text = json.dumps(
                self.pages,
                indent = 2,
                sort_keys=True).decode('raw_unicode_escape')
            
            file.write(text)
















