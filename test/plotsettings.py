#!/bin/env python

import sys

from PyQt4.QtGui import QApplication
from pygraph.plotsettings import PlotSettings

app = QApplication(sys.argv)
ps = PlotSettings()
ps.show()
app.exec_()
