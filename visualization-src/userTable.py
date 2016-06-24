import os
import re

from dateutil.parser import parse
from csv import DictWriter, DictReader
from stack_tools import readRows, post_types, vote_types, latest_dump_date

tags_re = re.compile('<([^>]+)>')

class UserTable():

  def __init__(self, xmldir):

    self.xmldir = xmldir
    self.table = []
    self.id_table = {}
    self.tags = set()

    self.buildTable()
    self.parseFeatures()

    # Remove redundant tags from each user:
    for line in self.table:
      line['tags'] = ','.join( set( tags_re.findall( line['tags'] ) ) )
    
  def buildTable(self):
    xml_addr = os.path.join(self.xmldir, 'Users.xml')

    for row in readRows(xml_addr):
      line = {
        'id': row.get('Id'),
        'rep': row.get('Reputation'),
        'account_age': (latest_dump_date-parse(row.get('CreationDate'))).days / 365.2425,
        'num_posts': 0,
        'num_comments': 0,
        'num_upvotes': row.get('UpVotes'),
        'num_downvotes': row.get('DownVotes'),
        'num_upvoted': 0,
        'num_downvoted': 0,
        'tags': ""
      }
      self.table.append(line)
      self.id_table[ line['id'] ] = line

  def parseFeatures(self):
    
    # Temporally track how many votes each post have got:
    votes_per_post = {}

    # Comments features:
    xml_addr = os.path.join(self.xmldir, 'Comments.xml')
    for row in readRows(xml_addr):
      owner_id = row.get('UserId')

      if owner_id:
        self.id_table[owner_id]['num_comments'] += 1

    # Votes features:
    xml_addr = os.path.join(self.xmldir, 'Votes.xml')
    for row in readRows(xml_addr):
      vote_type = row.get('VoteTypeId')
      vote_post_id = row.get('PostId')

      # If everything was found:
      if vote_post_id and vote_type:

        # Make sure there is an entry on the vote tracker:
        if vote_post_id not in votes_per_post:
          votes_per_post[vote_post_id] = { 'up': 0, 'down': 0 }

        # Count this vote:
        if vote_type == '2':
          votes_per_post[vote_post_id]['up'] += 1
        elif vote_type == '3':
          votes_per_post[vote_post_id]['down'] += 1

    # Posts features:
    xml_addr = os.path.join(self.xmldir, 'Posts.xml')
    for row in readRows(xml_addr):
      post_id = row.get('Id')
      owner_id = row.get('OwnerUserId')

      if post_id and owner_id:
        self.id_table[owner_id]['num_posts'] += 1

        if post_id in votes_per_post:
          self.id_table[owner_id]['num_upvoted'] += votes_per_post[post_id]['up']
          self.id_table[owner_id]['num_downvoted'] += votes_per_post[post_id]['down']

        tags = row.get('Tags')
        if tags:
          self.id_table[owner_id]['tags'] += tags

  csvheader = [
    'id', 'rep', 'account_age', 'num_posts',
    'num_comments', 'num_upvotes', 'num_downvotes',
    'num_upvoted', 'num_downvoted', 'tags' ]
  def saveTable(self, addr):
    with open(addr, 'w') as file:
      my_dict = { 'a':10, 'b':5, 'c': 8 }
      w = DictWriter(file, self.csvheader, delimiter='\t')
      w.writeheader()
      w.writerows(self.table)

  def loadTable(self, addr):
    with open('test.csv') as file:
      table = list(DictReader(file, delimiter='\t'))
      self.table = table
      return table
    
