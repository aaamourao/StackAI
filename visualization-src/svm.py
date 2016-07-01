
from features import Features
from sknn.mlp import Classifier, Layer
from neuralnet import NeuralNet

from sklearn import svm
  
class Svm(NeuralNet):
  
  def buildNet(self , features, train_size=None):
    
    net = svm.SVR()

    try:
      yt, xt = features.generate(train_size)
      net.fit(xt, yt)
    except KeyboardInterrupt:
      pass

    return net

