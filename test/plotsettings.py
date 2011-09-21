#!/bin/env python

import sys

from PyQt4.Qt import QApplication
from pygraph.plotsettings import PlotSettings

settings = {"xMin":0, "xMax":1, "yMin":0, "yMax":1,
            "xAxisTitle":"X Axis", "yAxisTitle":"Y Axis",
             "xMinEnabled":False, "yMinEnabled":False
           }
app = QApplication(sys.argv)
ps = PlotSettings(settings)
ps.show()
app.exec_()
