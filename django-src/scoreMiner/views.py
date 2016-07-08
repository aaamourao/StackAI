import sys
import subprocess
import threading

from django.shortcuts import render
from django.http import HttpResponse

from neural_tools.stack_tools import readRows, tags_re
from neural_tools.features import Features

from neural_tools.userTable import UserTable
from neural_tools.postTable import PostTable
from neural_tools.tags import Tags
from neural_tools.svm import Svm

import pickle

print ('Loading Svm and Tags struct with Pickle...')
with open('superuser_data/svm.p', 'rb') as file:
  svm = Svm(net=pickle.load(file))

with open('superuser_data/tags.p', 'rb') as file:
  tags = pickle.load(file)

with open('superuser_data/user.p', 'rb') as file:
  user_t = pickle.load(file)

def popenAndCall(onExit, popenArgs):
  def runInThread(onExit, popenArgs):
    proc = subprocess.Popen(popenArgs)
    proc.wait()
    onExit()
    return
  thread = threading.Thread(target=runInThread, args=(onExit, popenArgs))
  thread.start()
  # returns immediately after the thread starts
  return thread

# Create your views here.
def index(request):
  return HttpResponse("Hello World!")

def callback():
  print("Loading crawled posts...")
  post_t = PostTable('data', saveUrl=True)
  print('Num posts:', len(post_t.table))
  
  # Build the crawled user:
  print("Loading crawled user data...")
  user = user_t.loadCrawledUsers('data/Users.xml')[0]
  
  # Build the features class with the crawled posts,
  # and the user_table and tags from training:
  print("Building feature generator...")
  svm.features = Features(user_t, post_t, tags)
  
  # Build a feature table for this user:
  print("Generating features for each post/user...")
  f_table = svm.features.makeUserFeatureTable(user)
  print('table len:', len(f_table))

  print("Predicting classes...")
  y_values = svm.predict(f_table)

  print("Sorting results...")
  print(post_t.table[0])
  posts = [ (p['url'], p['title']) for p in post_t.table ]
  suggestions = sorted(
    zip(posts, y_values), key=lambda x : -x[1])

  return suggestions

def postList(request, uid):
  urls = []
  def response():
    r = callback()
    print("Return from callback")
    urls.extend(r)

  print("Starting Crawler... UID: %s" % uid)
  cmdline = ("scrapy runspider crawler/crawlUser.py -a uid=%s" % uid)
  print("cmdline: %s" % cmdline)
  thread = popenAndCall(response,
      cmdline.split()
    )
  thread.join(10)

  urls = [ ('%s: <a href=%s>%s</a> %.1f%%' % (idx,p[0],p[1][:40],score*100)) for idx, (p,score) in enumerate(urls[:15]+urls[-15:]) ]
  #print('callback urls:', urls)

  resp = '<br>'.join(urls)
  return HttpResponse(
      "The user id is: %s<br><br>%s" % (uid, resp))

if __name__ == '__main__':
  callback()




