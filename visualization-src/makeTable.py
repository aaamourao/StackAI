#!/usr/bin/env python2

from userTable import UserTable, tags_re

if __name__ == '__main__':
  user_t = UserTable('../stackexchange')

  table = []
  for idx, line in enumerate(user_t.table):
    if line['tags'] != "":
      table.append(line)
  user_t.table = table

  user_t.saveTable('full_table.csv')

  # collect all tag names:
  print "table len", len(user_t.table)
  tags = set()
  for line in user_t.table:
    tags = tags.union(line['tags'].split(','))
  tags.discard("")

  print "tags len", len(tags)
  with open('full_categories.csv', 'w') as file:
    file.write( '\t'.join(tags) )
