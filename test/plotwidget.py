#!/bin/env python

import sys

from PyQt4.Qt import QApplication
from PyQt4.Qwt5 import *
from pygraph.plotwidget import PlotWidget

import numpy as np

x = np.arange(0, 5, 0.01)
y = x**2

app = QApplication(sys.argv)
plot = PlotWidget()
curve = QwtPlotCurve()
curve.attach(plot)

plot.plotFrame(curve, {"test":(x,y)})

plot.show()
app.exec_()
