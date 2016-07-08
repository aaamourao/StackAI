#!/usr/bin/env python2

import os
import pickle
from matplotlib import pyplot as plt
from collections import Counter
from os.path import isfile, join
from time import clock

from neural_tools.tags import Tags
from neural_tools.stack_tools import tags_re
from neural_tools.userTable import UserTable
from neural_tools.postTable import PostTable
from neural_tools.features import Features

from neural_tools.mlp import Mlp
from neural_tools.softmax import Softmax
from neural_tools.svm import Svm

from numpy import mean

def saveFile(item, path, name):
  addr = join(path, name)
  with open(addr, 'wb') as file:
    file.write(pickle.dumps(item, 2))

def buildGraph(tags, uncommon_min):
  mc = tags.count.most_common()
  graph = [ y[1] for y in mc ]
  ntags = len(graph)
  total = sum(graph)
  filtered=list(y for y in graph if y >= uncommon_min)
  remain = ntags - len( filtered )
  loss = total - sum( filtered )
  plt.bar(
    range(ntags), graph, 1,
    label="Tag Count",
    edgecolor="b",
    color='b')
  for idx, val in enumerate(graph):
    if val < uncommon_min:
      break
  plt.bar(
    [idx], graph[idx], 1,
    color='r')
  plt.plot(
    [uncommon_min] * ntags,
    linewidth=2, label="Cut Threshold",
    color='r')
  plt.xlabel('Tags')
  plt.ylabel('N° Ocurrencies')
  plt.legend()

  text = ('Cut threshold: %d\n' % int(uncommon_min))
  text += ('Data Loss: %.1f%%\n' % (100.*loss/total) )
  text += ('Tag Reduction: %.1f%%' %
    (100.*remain/ntags))
  plt.text(len(graph)*.35, max(graph)*.45/4, text,
    fontsize=18, color='green', ha='center',
    style='oblique')

  x1,x2,y1,y2 = plt.axis()
  plt.axis((x1,x2,y1/4,y2/4))
  plt.savefig('count.png')

def makeTable(
  path='../stackexchange',
  refresh=False,
  uncommon_min=None):
  source_files = {
    'user': join(path, 'user.p'),
    'post': join(path, 'post.p'),
    'tags': join(path, 'tags.p'),
  }

  for val in source_files.values():
    if not isfile(val):
      refresh = True
  
  if refresh:
    print("Collecting data from XML files...")
    post_t = PostTable(path)
    user_t = UserTable(path, post_t)

    table = []
    # Normalize some columns and remove some lines:
    for idx, line in enumerate(user_t.table):
      # Ignore users with no tags attached to it:
      if len(line['tags']) != 0 and line['num_posts'] > 0:
        table.append(line)
        # Normalize some values according to the number of posts:
        for key in line:
          if key not in ['badges', 'tags', 'id', 'account_age', 'num_posts']:
            line[key] = float(line[key]) / line['num_posts']

    print("Table len", len(table))

    # Collect information about all the tags
    # and remove lines with too uncommon tags
    # from the table
    tags = Tags(
        table, min_count=20,
        ban_tags=['identification-request'], filter=True)

    if uncommon_min == None:
      uncommon_min = mean(list(tags.count.values()))*.8

    print("Cut threshold: %d" % int(uncommon_min))

    print("Building tags graph...")
    buildGraph(tags, uncommon_min)

    print("Dropping uncommon tags...")
    tags.dropUncommon(uncommon_min)
    tags.filterSelf()

    post_t.table, _ = tags.filterTable(table=post_t.table)

    tags.saveTags('all_tags.csv', save_counts=False)

    print("Tags len:", len(tags.count))

    badges = Tags(tags.table, col='badges')
    badges.saveTags('all_badges.csv', save_counts=False)

    print("Badges len:", len(badges.count))

    print("Filtered table len", len(tags.table))
    user_t.loadTable(table=tags.table)
    user_t.saveTable('full_table.csv')
    post_t.saveTable('Posts.csv')

    # Save the files:
    saveFile(user_t, path, 'user.p')
    saveFile(post_t, path, 'post.p')
    saveFile(tags, path, 'tags.p')
  else:
    print("Loading data from pickle files...")
    # Load the files:
    with open(source_files['user'], 'rb') as file:
      user_t = pickle.load(file)
    with open(source_files['post'], 'rb') as file:
      post_t = pickle.load(file)
    with open(source_files['tags'], 'rb') as file:
      tags = pickle.load(file)

  return Features(user_t, post_t, tags)

def main():

  #path = '../stackexchange'
  path = '/home/fox/adados/superuser_data'

  # Loading data:
  features = makeTable(path)


  print("Training MLP...")
  start = clock()

  with open(path+'/svm.p', 'rb') as file:
    net = pickle.load(file)
    net = Svm(features, net=net)
  #net = Svm(features, 400000, 1000)
  #net = Softmax(features, 2000, 500)
  #net = Mlp(features, 2000, 500)
  saveFile(net.net, path, 'svm.p')
  print("Time: %.1fmin"%((clock()-start)/60))

  start = clock()
  print("\nTesting 50% match vs 50% random:")
  net.test(40000, 1000)
  print("Time: %ds" %(clock()-start))

  start = clock()
  print("\nTesting 100% random:")
  net.test(40000, 1000, match=False)
  print("Time: %ds" %(clock()-start))

  print("")

  return net

if __name__ == '__main__':
  main()







