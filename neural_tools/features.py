from random import randint
from numpy import array

# For python3 compatibility
if 'xrange' not in globals():
  xrange = range

# Join the tables from users, posts and tags
# to built feature tables.
class Features():
  ndim = 0

  # @args:
  # - users should be a UserTable instance
  # - posts should be a PostTable instance
  # - tags should be a Tags instance
  def __init__(self, users, posts, tags):
    self.users = users
    self.posts = posts
    self.tags = tags
    self.ndim = tags.ndim*2 + users.ndim + 1

  def generate(self, size=None, match=None, no_class=False):
    if not size:
      size = len(self.posts.table)

    y_train = []
    x_train = []
    for num in xrange(size):
      y, x = self.makeFeatureVectorPair(match)
      y_train.append(y)
      x_train.append(x)

    if no_class:
      return array(x_train)
    else:
      return array(y_train), array(x_train)

  def makeFeatureVectorPair(self, match=None):
    p_len = len(self.posts.table)
    u_len = len(self.users.table)
    
    if match == None:
      match = randint(0,1)
    user = None
    count = 0

    # Choose a matching pair with 50% change:
    if match:
      while not user:
        if count == 100:
          raise Exception("Exceeded the maximum lookups for post/user pair!")
        else:
          count += 1

        post = self.posts.table[ randint(0, p_len-1) ]
        pu_len = len(post['users'])
        # Check if ths post was anonimous:
        if pu_len > 0:
          user_id = post['users'][randint(0, pu_len-1)]
          user = self.users.id_table[user_id]
    else:
    # Choose a pair randomly
      post = self.posts.table[ randint(0, p_len-1) ]
      user = self.users.table[ randint(0, u_len-1) ]

    # This is the class of the feature vector:
    ismatch = int(user['id'] in post['users'])

    return ismatch, self.makeFeatureVector(user, post)

  def makeFeatureVector(self, user, post):
    # Return a vector with sum == 1 indicating the tag distribution of a user
    u_tags = self.tags.makeFeatureVector(user['tags'])

    # Return a binary list X where Xi indicates the presence
    # or abscence of the tag i on tags_list
    p_tags = self.tags.makeBinaryVector(post['tags'])

    # Tags features:
    f_vec = [self.tag_correlation(u_tags, p_tags)] + u_tags + p_tags
    # User profile features:
    f_vec += self.users.makeFeatureVector(user)

    return f_vec

  def makeUserFeatureTable(self, user):

    table = []
    for post in self.posts.table:
      table.append( self.makeFeatureVector(user, post) )
    
    return array(table)

  # Calculate a factor between 0 and 1 indicating the direct
  # correlation between the user tags and the post tags.
  def tag_correlation(self, user_tags, post_tags):
    return sum([x*y for x,y in zip(user_tags, post_tags)])



    
