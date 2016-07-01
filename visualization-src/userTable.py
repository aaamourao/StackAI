import os

from dateutil.parser import parse
from csv import DictWriter, DictReader

from postTable import PostTable
from stack_tools import readRows, latest_dump_date, tags_re

class UserTable():

  def __init__(self, xmldir, post_t=None):

    self.xmldir = xmldir
    self.table = []
    self.id_table = {}
    self.tags = set()

    if post_t:
      self.post_t = post_t
    else:
      self.post_t = PostTable(xmldir)

    self.buildTable()
    self.parseFeatures()
    self.max_vec = self.buildMaxVec()
    self.ndim = len( self.relative_keys ) + len( self.profile_keys )
    
  def buildTable(self):
    xml_addr = os.path.join(self.xmldir, 'Users.xml')

    for row in readRows(xml_addr):
      line = {
        'id': row.get('Id'),
        'rep': int(row.get('Reputation')),
        'account_age': (latest_dump_date-parse(row.get('CreationDate'))).days / 365.2425,
        'num_posts': 0,
        'num_comments': 0.,
        'num_upvotes': float(row.get('UpVotes')),
        'num_downvotes': float(row.get('DownVotes')),
        'num_upvoted': 0.,
        'num_downvoted': 0.,
        'tags': [],
        'badges': []
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

    # Badge features:
    xml_addr = os.path.join(self.xmldir, 'Badges.xml')
    for row in readRows(xml_addr):
      owner_id = row.get('UserId')
      name = row.get('Name')

      if owner_id and name:
        self.id_table[owner_id]['badges'].append(name)

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

    for line in self.post_t.table:
      for uid in line['users']:
        self.id_table[uid]['tags'].extend( line['tags'] )

  csvheader = [
    'id', 'rep', 'account_age', 'num_posts',
    'num_comments', 'num_upvotes', 'num_downvotes',
    'num_upvoted', 'num_downvoted', 'tags', 'badges' ]
  def saveTable(self, addr):
    with open(addr, 'w') as file:
      w = DictWriter(file, self.csvheader, delimiter='\t')
      w.writeheader()
      w.writerows(self.table)

  def loadTable(self, addr=None, table=None):
    if addr:
      with open('test.csv') as file:
        table = list(DictReader(file, delimiter='\t'))
        self.table = table
    elif table:
      self.table = table

    self.max_vec = self.buildMaxVec()

    return table

  relative_keys = [
    'rep', 'account_age', 'num_posts', 'num_comments' ]
  profile_keys = [
    'num_upvotes', 'num_downvotes', 'num_upvoted', 'num_downvoted' ]
  # Return a list with values between 0 and 1 describing the user
  def makeFeatureVector(self, user):
    # Get the distribution of the profile features from the user:
    total = 0
    profile = []
    for key in self.profile_keys:
      total += user[key]
      profile.append( user[key] )

    # Check to avoid division for 0:
    if total != 0:
      profile = [ k/total for k in profile ]

    # Get the fraction in relation to other users of the relative keys:
    relation = []
    max_vec = self.max_vec
    for key in self.relative_keys:
      value = user[key] / max_vec[key]
      relation.append( value )

    return profile + relation

  def buildMaxVec(self):
    max_vec = {
      'rep': 0. , 'account_age': 0.,
      'num_posts': 0., 'num_comments': 0.
    }
    
    for line in self.table:
      for key in max_vec:
        max_vec[key] = max( max_vec[key], float(line[key]) )

    return max_vec

    
    










    
