#!/bin/env python

import sys

from qwt import QwtPlot
from pygraph.plotwidget import PlotWidget
from PyQt4.QtGui import QApplication

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

datasets = {"first.dataset":wrapper(x1, y1), "second.dataset": wrapper(x2, y2)}
plot.plotFrame(datasets.keys(), datasets, "t = 0.5")
plot.setAxisScale(QwtPlot.xBottom, 0, 5)
plot.setAxisScale(QwtPlot.yLeft, 0, 5**3)
plot.updateAxes()

plot.show()
app.exec_()
