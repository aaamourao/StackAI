#!/usr/bin/python
# coding: utf-8

# To use this project execute it with:
# scrapy runspider stack_spider.py

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from lxml import etree

import scrapy
import json
import codecs
import time
import re

#from crawler.items import VidInfo
from functools import partial
from os.path import isfile, isdir, splitext, dirname, exists, basename
from os import makedirs, listdir, rmdir

innerHtml = re.compile('\A<[^>]*>(.*)</[^>]*>\Z', re.DOTALL)
def getInner(html):
  return innerHtml.match(html).group(1)

def xmlSet(xml, attr, value):
  if type(value).__name__ in [ 'unicode', 'str' ]:
    xml.set(attr, value)

uid_re = re.compile("users/([0-9]+)/[^/]+\Z")

subI = re.compile('[^0-9.]')

class VidSpider(scrapy.Spider):
  # Required attributes:
  name = "videos"
  start_urls = [
      "http://stackoverflow.com/users/5228806/ffxsam",
      "http://stackoverflow.com/users/3918736/sebnorth",
      "http://superuser.com/users/502453/justin-brown"
    ]

  users = etree.Element('users')

  # Pre-load some files/data:
  def __init__(self, uid=None):
    print('Scheduling user to be crawled!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    if uid:
      self.start_urls = [ "http://superuser.com/users/%s/" % uid ]

  def parse(self, resp):
    user = etree.Element('row')

    xmlSet(user, 'Id', uid_re.findall(resp.url)[0])
    xmlSet(user, 'DisplayName', resp.css("h2.user-card-name::text").extract_first().strip())
    xmlSet(user, 'Reputation', subI.sub('', resp.css('div.reputation::text').extract_first()))
    xmlSet(user, 'CreationDate', resp.css('.user-links li span[title]:not([class])::attr(title)').extract_first())
    xmlSet(user, 'UpVoted', "0")
    xmlSet(user, 'DownVoted', "0")

    n_answers = int(subI.sub('', resp.css('.user-stats .answers .number::text').extract_first()))
    n_questions = int(subI.sub('', resp.css('.user-stats .questions .number::text').extract_first()))
    xmlSet(user, 'NumPosts', str(n_answers+n_questions))

    # Crawl for all user tags info:
    xmlSet(user, 'Tags', '')
    yield scrapy.Request(
        resp.url+"?tab=tags", callback=partial(self.parseTags, user)
      )

    # Crawl for user up/down votes info:
    yield scrapy.Request(
        resp.url+"?tab=topactivity", callback=partial(self.parseVotes, user)
      )

    # Crawl for user total number of comments:
    yield scrapy.Request(
        resp.url+"?tab=activity&sort=comments", callback=partial(self.parseNumComments, user)
      )

    # Save that post:
    self.users.append(user)

  def parseVotes(self, user, resp):

    votes_sel = list(resp.css('.votes-cast-stats tr'))

    if len(votes_sel) == 0:
      xmlSet(user, 'UpVotes', '0')
      xmlSet(user, 'DownVotes', '0')
    else:
      xmlSet(user, 'UpVotes', votes_sel[1].css('td::text').extract_first())
      xmlSet(user, 'DownVotes', votes_sel[2].css('td::text').extract_first())

  def parseNumComments(self, user, resp):
    total = resp.css('h1 span.count').extract_first()
    xmlSet(user, 'NumComments', subI.sub('', total))

  def parseBadges(self, user, resp):
    tags = user.get('Tags')
    for sel in resp.css(".user-tags td"):
      tag_name = sel.css("a.post-tag::text").extract_first()
      tag_count = sel.css(".item-multiplier-count::text").extract_first() or 1
      tags += (("<%s>" % tag_name) * int(subI.sub('', tag_count)))
    xmlSet(user, 'Tags', tags)

    # TODO: If the internet stops hanging we could uncomment this
    # so that we would get all the user tags, instead of just the most
    # common ones.
    #next_page = resp.css('a[href][rel="next"]::attr(href)').extract_first()
    #if next_page:
    #  yield scrapy.Request(
    #      resp.urljoin(next_page), callback=partial(self.parseTags, user)
    #    )

  def parseTags(self, user, resp):
    tags = user.get('Tags')
    for sel in resp.css(".user-tags td"):
      tag_name = sel.css("a.post-tag::text").extract_first()
      tag_count = sel.css(".item-multiplier-count::text").extract_first() or 1
      if type(tag_count) == str:
        tag_count = subI.sub('', tag_count)
      tags += (("<%s>" % tag_name) * int(tag_count))
    xmlSet(user, 'Tags', tags)

    next_page = resp.css('a[href][rel="next"]::attr(href)').extract_first()
    if next_page:
      yield scrapy.Request(
          resp.urljoin(next_page), callback=partial(self.parseTags, user)
        )

  # To download data be it a image, video or an
  # html page, just Request it and set download
  # as a callback with patial(self.download, "path/to/file")
  def download(self, path, resp): 
    print()
    print("  Downloading %s!" % path)
    print()
    # Make sure path exists: 
    if not isdir(dirname(path)): 
      makedirs(dirname(path))        
    with open(path, 'wb') as file: 
      file.write(resp.body) 

  # Save the data before quit:
  def closed(self, reason):

    with open('data/Users.xml', 'wb') as file:
      xml_text = etree.tostring(
        self.users, encoding='utf-8', pretty_print=True, xml_declaration=True)
      file.write(xml_text)















