from random import randint
from numpy import array

from sknn.mlp import Classifier, Layer

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

  def genData(self, size=None, match=None):
    if not size:
      size = len(self.posts.table)

    y_train = []
    x_train = []
    for num in xrange(size):
      y, x = self.makeFeatureVectorPair(match)
      y_train.append(y)
      x_train.append(x)

    return array(y_train), array(x_train)

  def train(self, train_size=None):
    y_train, x_train = self.genData(train_size)

    self.net = Classifier(
      layers=[
        Layer("Sigmoid", units=100),
        Layer("Softmax")],
      learning_rate=0.001,
      n_iter=25)
    
    self.net.fit(x_train, y_train)

  def test(self, test_size=100, match=None):
    y_test, x_test = self.genData(test_size, match)

    true_p = 0.; true_n = 0.; fake_p = 0.; fake_n = 0.
    for guess, y in zip(self.net.predict(x_test), y_test):
      if guess == 1 and y == 1:
        true_p += 1
      if guess == 1 and y == 0:
        fake_p += 1
      if guess == 0 and y == 0:
        true_n += 1
      if guess == 0 and y == 1:
        fake_n += 1

    true_p /= test_size
    fake_p /= test_size
    true_n /= test_size
    fake_n /= test_size

    print("""
     \ttrue\tfalse
    p\t%s\t%s
    n\t%s\t%s
    """ % (true_p, fake_p, true_n, fake_n))

    print("Precision: %s" % ((true_p / (true_p+fake_p)) if true_p else 0) )
    print("Recall: %s" % ((true_p / (true_p+fake_n)) if true_p else 0) )

  def makeFeatureVectorPair(self, match=None):
    p_len = len(self.posts.table)
    u_len = len(self.users.table)
    
    if match == None:
      match = randint(0,1)

    # Choose a matching pair with 50% change:
    if match:
      post = self.posts.table[ randint(0, p_len-1) ]
      pu_len = len(post['users'])
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

  # Calculate a factor between 0 and 1 indicating the direct
  # correlation between the user tags and the post tags.
  def tag_correlation(self, user_tags, post_tags):
    return sum([x*y for x,y in zip(user_tags, post_tags)])



    
