
from features import Features

# Multi-layer perceptron neural network
class NeuralNet():

  # @args:
  #   - features should be a Features instance
  #   - train_size indicates how many lines
  #   - should be generated for the traning
  def __init__(self, features, train_size=None):
    self.features = features
    self.net = self.buildNet(features, train_size)
  
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

  def test(self, test_size=100, match=None):
    yt, xt = self.features.generate(test_size, match)

    true_p = 0.; true_n = 0.; fake_p = 0.; fake_n = 0.
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

    true_p /= test_size
    fake_p /= test_size
    true_n /= test_size
    fake_n /= test_size

    print("""
     \ttrue\tfalse
    p\t%s\t%s
    n\t%s\t%s
    """ % (true_p, fake_p, true_n, fake_n))

    print("Precision: %s" %
      ((true_p / (true_p+fake_p)) if true_p else 0) )
    print("Recall: %s" %
      ((true_p / (true_p+fake_n)) if true_p else 0) )




