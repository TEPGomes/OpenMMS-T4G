from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg


class GraphsWidget (QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super(GraphsWidget, self).__init__(*args, **kwargs)
      
        self.mainbox = QtWidgets.QWidget()
        self.canvas = pg.GraphicsLayoutWidget()
        lay = QtWidgets.QVBoxLayout(self.mainbox)
        lay.addWidget(self.canvas)

        self.setLayout(lay)