#!/bin/env python

import sys

from PyQt4.Qt import QApplication
from pygraph.plotwidget import PlotWidget

app = QApplication(sys.argv)
plot = PlotWidget()
plot.show()
app.exec_()
