#!/bin/env python

import sys

from PyQt4.Qt import QApplication
from pygraph.plotwidget import PlotWidget

defaultOptions = {"xMin":0, "xMax":1, "yMin":0, "yMax":1,
                  "xAxisTitle":"X Axis", "yAxisTitle":"Y Axis",
                  "xMinEnabled":False, "yMinEnabled":False
                 } 
app = QApplication(sys.argv)
plot = PlotWidget()
plot.applysettings(defaultOptions)
plot.show()
app.exec_()
