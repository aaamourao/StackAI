from .features import Features
from .neuralnet import NeuralNet

from sknn.mlp import Classifier, Layer

# Multi-layer perceptron neural network
class Softmax(NeuralNet):

  def buildNet(self):

    net = Classifier(
      layers=[
        Layer("Softmax")],
      learning_rate=0.001,
      n_iter=25)
    
    return net





