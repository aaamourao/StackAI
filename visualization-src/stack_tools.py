
import re
from collections import Counter
from dateutil.parser import parse
from lxml import etree

# Used to extract tags from `Posts.xml`
tags_re = re.compile('<([^>]+)>')

# Iterate over all the file rows
# Yield an etree.Element of the line.
def readRows(addr):
  with open(addr) as file:
    line = file.readline()

    while line:
      if line[:6] == '  <row':
        yield etree.XML(line)
      line = file.readline()

def normalize_tags(tag_count):
  total = sum(tag_count)
  return [ x/total for x in tag_count ]

# Table must be iterable
# and return a dict on each iteration.
def expandTableRows(table, col_name, col_set, delim=','):
  for line in table:
    # Extract and split the selected column:
    values = normalize_tags(
        Counter(line.pop(col_name).split(delim))
      )
    # Reinsert it in by the number of ocurrencies:
    for key in col_set:
      line[key] = values[key]
    # return it:
    yield line

# Expect user_tags to be filled with the normalized tag count values
# between 0 and 1 whose sum equals 1, and post_tags to be filled with
# integer values in the same range (0,1) indicating if the tag belongs
# or not to the post.
# This function should return a number between 0 and 1.
def tag_correlation(user_tags, post_tags):
  sum([x*y for x,y in zip(user_tags, post_tags)])

# expect user_table to contain only the tags and badges field.
def buildFeatures(user_table, post_table, tag_set, badge_set):
  table = expandTableRows(
    expandTableRows(user_table, 'tags', tag_set), 'badges', badge_set)

  for row in table:
    yield row + post_table + [ tag_correlation(user_table, post_table) ]

latest_dump_date = parse("2016-06-13")

# Post types allowed
post_types = {
  '1': 'Question',
  '2': 'Answer'
}

# Vote types allowed
vote_types = {
  '1': 'AcceptedByOriginator',
  '2': 'UpMod',
  '3': 'DownMod',
  '4': 'Offensive',
  '5': 'Favorite',
  '6': 'Close',
  '7': 'Reopen',
  '8': 'BountyStart',
  '9': 'BountyClose',
  '10': 'Deletion',
  '11': 'Undeletion',
  '12': 'Spam',
  '13': 'InfoModerator'
}
