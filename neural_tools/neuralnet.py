
from .features import Features

# Multi-layer perceptron neural network
class NeuralNet():

  # @args:
  #   - features should be a Features instance
  #   - train_size indicates how many lines
  #   - should be generated for the traning
  def __init__(self, features=None,
      train_size=None, chunk_size=None, net=None):

    self.features = features

    if net:
      self.net = net
    else:
      self.net = self.buildNet()
      self.train_net(train_size, chunk_size)

  def train_net(self, train_size, chunk_size):
    if chunk_size == None:
      chunk_size = train_size

    chunks = train_size // chunk_size
    try:
      for chunk in range(1, chunks+1):
        print('Chunk %s/%s...' % (chunk,chunks))
        yt, xt = self.features.generate(chunk_size)
        self.net.partial_fit(xt, yt)

      final_chunk = train_size % chunk_size
      if final_chunk > 0:
        print('Final chunk')
        print('  size: %s' % final_chunk)
        yt, xt = self.features.generate(final_chunk)
        self.net.partial_fit(xt, yt)
    except KeyboardInterrupt:
      pass
  
  # This function should return a classifier
  # with the a predict method that expects
  # a table of features as input, i.e.:
  #
  #   buildNet(...).predict( features.generate() )
  #
  # And return a list of classes in a numpy.ndarray
  def buildNet(self, features, train_size=None):
    raise Exception("Unimplemented please overwrite")

  def predict(self, x_test):
    return self.net.predict(x_test)

  def test(self, test_size=100, chunk_size=1000, match=None):

    chunks = test_size // chunk_size
    true_p = 0.;true_n = 0.;fake_p = 0.;fake_n = 0.

    for chunk in range(1, chunks+1):
      yt,xt=self.features.generate(chunk_size,match)

      print('Chunk %s/%s...' % (chunk, chunks))

      for guess, y in zip(self.predict(xt), yt):
        if guess >= .5 and y >= .5:
          true_p += 1
        if guess >= .5 and y < .5:
          fake_p += 1
        if guess < .5 and y < .5:
          true_n += 1
        if guess < .5 and y >= .5:
          fake_n += 1
    print('last guess/class:', guess, '/', y)

    test_size = chunks * chunk_size
    true_p *= 100/test_size
    fake_p *= 100/test_size
    true_n *= 100/test_size
    fake_n *= 100/test_size

    print("""
     \ttrue\tfalse
    p\t% 4.1f%%\t% 4.1f%%
    n\t% 4.1f%%\t% 4.1f%%
    """ % (true_p, fake_p, true_n, fake_n))

    print("Precision: %s" %
      ((true_p / (true_p+fake_p)) if true_p else 0) )
    print("Recall: %s" %
      ((true_p / (true_p+fake_n)) if true_p else 0) )




