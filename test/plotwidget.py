#!/bin/env python

import sys

from PyQt4.Qt import QApplication
from PyQt4.Qwt5 import *
from pygraph.plotwidget import PlotWidget

import numpy as np

defaultSettings = {"xMin":0, "xMax":5, "yMin":0, "yMax":25,
                  "xAxisTitle":"X Axis", "yAxisTitle":"Y Axis",
                  "xMinEnabled":False, "yMinEnabled":False
                 } 

x = np.arange(0, 5, 0.01)
y = x**2

app = QApplication(sys.argv)
plot = PlotWidget(defaultSettings)
curve = QwtPlotCurve()
curve.attach(plot)

plot.plotFrame(curve, {"test":(x,y)})

plot.show()
app.exec_()
