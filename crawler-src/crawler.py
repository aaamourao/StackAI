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

MAX_QUESTIONS=10

innerHtml = re.compile('\A<[^>]*>(.*)</[^>]*>\Z', re.DOTALL)
def getInner(html):
  return innerHtml.match(html).group(1)

def xmlSet(xml, attr, value):
  if type(value).__name__ in [ 'unicode', 'str' ]:
    xml.set(attr, value)

uid_re = re.compile("users/([0-9]+)/[^/]+\Z")
qid_re = re.compile("questions/([0-9]+)/[^/]+\Z")

class VidSpider(scrapy.Spider):
  # Required attributes:
  name = "videos"
  start_urls = [
      # Looking for the newest questions:
      #"http://stackoverflow.com/questions?sort=featured",#newest"
      "http://superuser.com/questions?sort=featured"
    ]

  users_url = [
    "http://stackoverflow.com/users/5228806/ffxsam",
    "http://stackoverflow.com/users/3918736/sebnorth",
    "http://superuser.com/users/502453/justin-brown"
  ]

  posts = etree.Element('posts')
  users = etree.Element('users')

  # Pre-load some files/data:
  def __init__(self, uid=None, refreshQuestions=True):
    # Toggle when to crawl for questions as well:
    self.refreshQuestions = refreshQuestions == True

    if uid:
      self.users_url = [ "http://superuser.com/users/%s/" % uid ]

  count = 0
  
  # Parse the starting page
  # Save data on self attributes
  # and yield a parse request when you need a link to be
  # parsed by other function.
  def parse(self, resp):

    for link in self.users_url:
      # Schedule it to be parsed:
      yield scrapy.Request(
          link, callback=partial(self.parseUser)
        )

    if self.refreshQuestions:
      for link in resp.css('#mainbar a.question-hyperlink::attr(href)').extract():
        if self.count == MAX_QUESTIONS:
            break
        else:
            self.count += 1

        # Schedule it to be parsed:
        yield scrapy.Request(
            resp.urljoin(link),
            callback=partial(self.parseQuestion)
          )

  def parseUser(self, resp):
    user = etree.Element('row')

    xmlSet(user, 'Id', uid_re.findall(resp.url)[0])
    xmlSet(user, 'DisplayName', resp.css("h2.user-card-name::text").extract_first().strip())
    xmlSet(user, 'Reputation', re.sub('[^0-9]', '', resp.css('div.reputation::text').extract_first()))
    xmlSet(user, 'CreationDate', resp.css('.user-links li span[title]:not([class])::attr(title)').extract_first())
    xmlSet(user, 'UpVoted', "0")
    xmlSet(user, 'DownVoted', "0")

    n_answers = int(resp.css('.user-stats .answers .number::text').extract_first())
    n_questions = int(resp.css('.user-stats .questions .number::text').extract_first())
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
    xmlSet(user, 'NumComments', re.sub('[^0-9]', '', total))

  def parseBadges(self, user, resp):
    tags = user.get('Tags')
    for sel in resp.css(".user-tags td"):
      tag_name = sel.css("a.post-tag::text").extract_first()
      tag_count = sel.css(".item-multiplier-count::text").extract_first() or 1
      tags += (("<%s>" % tag_name) * int(tag_count))
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
      tags += (("<%s>" % tag_name) * int(tag_count))
    xmlSet(user, 'Tags', tags)

    next_page = resp.css('a[href][rel="next"]::attr(href)').extract_first()
    if next_page:
      yield scrapy.Request(
          resp.urljoin(next_page), callback=partial(self.parseTags, user)
        )

  def parseQuestion(self, resp):
    post = etree.Element('row')

    xmlSet(post, 'Id', qid_re.findall(resp.url)[0])
    xmlSet(post, 'url', resp.url)
    xmlSet(post, 'PostTypeId', "1")
    xmlSet(post, 'AcceptedAnswerId',
      resp.css('.accepted-answer::attr(data-answerid)').extract_first())

    aux = list( resp.css('td[style] p.label-key') )
    xmlSet(post, 'CreationDate', aux[0].css('::attr(title)').extract_first())
    xmlSet(post, 'ViewCount', (aux[1].css('b').re('b>([0-9]+) ')[:1] or [None])[0])

    xmlSet(post, 'Score', resp.css( '#question span.vote-count-post::text').extract_first())
    xmlSet(post, 'Body', getInner(resp.css('.postcell div.post-text').extract_first()))

    xmlSet(post, 'OwnerUserId', (resp.css(
        '.user-details a::attr(href)').re(
            '/users/([0-9]+)/')[:1] or [None])[0])

    #xmlSet(post, 'LastEditorUserId', None)
    xmlSet(post, 'LastEditDate', resp.css('.question .user-action-time a span::attr(title)').extract_first())
    xmlSet(post, 'LastActivityDate', resp.css('.lastactivity-link::attr(title)').extract_first())
    xmlSet(post, 'Title', resp.css('#question-header a::text').extract_first())
    xmlSet(post, 'Tags', ''.join([ '<%s>'%t for t in resp.css('.post-taglist .post-tag::text').extract() ]))
    xmlSet(post, 'AnswerCount', str(len(list(resp.css('.answer')))))
    xmlSet(post, 'CommentCount', str(len(list(resp.css('.question .comment-text')))))
    xmlSet(post, 'FavoriteCount', resp.css('.favoritecount b::text').extract_first())

    # The attributes below are not required by the neural network,
    # So they are of less importance:
    xmlSet(post, 'ownerUserName', resp.css( '.user-details a::text').extract_first())

    aux = resp.css(
        '.reputation-score::text').extract_first().replace(',','')
    if 'k' in aux:
      aux = aux.replace('k', '')
      aux = float(aux)
      aux*= 1000
    else:
      aux = int(aux)
    xmlSet(post, 'authorRep', str(int(aux)))

    # Save that post:
    self.posts.append(post)

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

    if self.refreshQuestions:
      # To write utf-8 files do as described bellow:
      #with codecs.open('data/Posts.xml', 'w', 'utf-8') as file:
      with open('data/Posts.xml', 'wb') as file:
        # text = json.dumps(
        #     self.pages,
        #     indent = 2,
        #     sort_keys=True).decode('raw_unicode_escape')

        xml_text = etree.tostring(
          self.posts, encoding='utf-8', pretty_print=True, xml_declaration=True)
        file.write(xml_text)

        # Using xmldump:
        # header = '<?xml version="1.0" encoding="utf-8"?>\n'
        # text = xmldump.dumps({ 'row': self.pages }, 'pages', indent=2)
        # file.write(header + text)

    with open('data/Users.xml', 'wb') as file:
      xml_text = etree.tostring(
        self.users, encoding='utf-8', pretty_print=True, xml_declaration=True)
      file.write(xml_text)















