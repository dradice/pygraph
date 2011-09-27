#!/bin/env python

import sys

from PyQt4.Qt import QApplication
from PyQt4.Qwt5 import *
from pygraph.plotwidget import PlotWidget

import numpy as np

class wrapper:
    def __init__(self, x, y):
        self.data_x = x
        self.data_y = y

x1 = np.arange(0, 5, 0.01)
y1 = x1**2

x2 = np.arange(0, 5, 0.02)
y2 = x2**3

app = QApplication(sys.argv)
plot = PlotWidget()

plot.plotFrame({"Uno":wrapper(x1, y1), "Due": wrapper(x2, y2)})

plot.show()
app.exec_()
