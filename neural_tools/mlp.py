
from .features import Features
from .neuralnet import NeuralNet

from sknn.mlp import Classifier, Layer

# Multi-layer perceptron neural network
class Mlp(NeuralNet):

  def buildNet(self):

    net = Classifier(
      layers=[
        #Layer("Sigmoid", units=features.ndim),
        Layer("Rectifier", units=features.ndim),
        Layer("Softmax")],
      learning_rate=0.006,
      n_iter=25)
    
    return net






