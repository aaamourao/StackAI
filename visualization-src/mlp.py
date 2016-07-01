
from features import Features
from sknn.mlp import Classifier, Layer
from neuralnet import NeuralNet

# Multi-layer perceptron neural network
class Mlp(NeuralNet):

  def buildNet(self, features, train_size=None):

    net = Classifier(
      layers=[
        #Layer("Sigmoid", units=features.ndim),
        Layer("Rectifier", units=features.ndim),
        Layer("Softmax")],
      learning_rate=0.006,
      n_iter=25)
    
    try:
      yt, xt = features.generate(train_size)
      net.fit(xt, yt)
    except KeyboardInterrupt:
      pass

    return net






