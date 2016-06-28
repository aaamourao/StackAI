#!/usr/bin/env python2

from tags import Tags
from stack_tools import tags_re
from userTable import UserTable
from postTable import PostTable
from learn import Learn

from collections import Counter

def makeTable():
  post_t = PostTable('../stackexchange')
  user_t = UserTable('../stackexchange', post_t)

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

  return Learn(user_t, post_t, tags)

if __name__ == '__main__':
  makeTable()

