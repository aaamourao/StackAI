
from .features import Features
from .neuralnet import NeuralNet

from sklearn import svm
from sklearn import linear_model
  
class Svm(NeuralNet):
  
  def buildNet(self):
    
    net = linear_model.SGDRegressor(
      n_iter = 1,
      alpha = 0.0001,
      shuffle=False
    )

    return net

