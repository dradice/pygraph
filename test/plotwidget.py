#!/bin/env python

import sys

from PyQt4.Qt import QApplication
from PyQt4.Qwt5 import *
from pygraph.plotwidget import PlotWidget

import numpy as np

x1 = np.arange(0, 5, 0.01)
y1 = x1**2

x2 = np.arange(0, 5, 0.02)
y2 = x2**3

app = QApplication(sys.argv)
plot = PlotWidget()

plot.plotFrame({"Uno":(x1, y1), "Due": (x2, y2)})

plot.show()
app.exec_()
