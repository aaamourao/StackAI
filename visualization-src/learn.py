from random import randint

# For python3 compatibility
if 'xrange' not in globals():
  xrange = range

class Learn():

  tags_header = None
  
  # @args:
  # - users should be a UserTable instance
  # - posts should be a PostTable instance
  # - tags should be a Tags instance
  def __init__(self, users, posts, tags):
    self.users = users
    self.posts = posts
    self.tags = tags
    self.tags_header = tags.getTags()

  def generateFeatures(self, train_size=None):
    if not train_size:
      train_size = len(self.posts.table)

    for num in xrange(train_size):
      yield self.makeFeatureVectorPair()

  def makeFeatureVectorPair(self):
    p_len = len(self.posts.table)
    u_len = len(self.users.table)

    # Choose a matching pair with 50% change:
    if randint(0,1) == 0:
      post = self.posts.table[ randint(0, p_len-1) ]
      pu_len = len(post['users'])
      user_id = post['users'][randint(0, pu_len-1)]
      user = self.users.id_table[user_id]
    else:
    # Choose a pair randomly
      post = self.posts.table[ randint(0, p_len-1) ]
      user = self.users.table[ randint(0, u_len-1) ]

    print('user tags', user['tags'])

    # This is the class of the feature vector:
    ismatch = user['id'] in post['users']

    return [ ismatch ] + self.makeFeatureVector(user, post)

  def makeFeatureVector(self, user, post):
    # Return a vector with sum == 1 indicating the tag distribution of a user
    u_tags = self.tags.makeFeatureVector(user['tags'])

    # Return a binary list X where Xi indicates the presence
    # or abscence of the tag i on tags_list
    p_tags = self.tags.makeBinaryVector(post['tags'])

    # Tags features:
    f_vec = [self.tag_correlation(u_tags, p_tags), u_tags, p_tags ]
    # User profile features:
    f_vec += [ self.users.makeFeatureVector(user) ]

    return f_vec

  # Calculate a factor between 0 and 1 indicating the direct
  # correlation between the user tags and the post tags.
  def tag_correlation(self, user_tags, post_tags):
    return sum([x*y for x,y in zip(user_tags, post_tags)])



    
