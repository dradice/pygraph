import sys

from PyQt4.Qwt5 import *
from PyQt4.Qwt5.qplt import *


class PlotWidget(QwtPlot):
    """a class that represents a plot"""
    def __init__(self, parent=None):
        super(PlotWidget, self).__init__(parent)
        self.setCanvasBackground(QColor("white"))
        self.setMinimumSize(640,480)

        grid = QwtPlotGrid()
#        grid.enableYMin(True)
        grid.setMinPen(QPen(DashLine))
        grid.attach(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    plot = PlotWidget()
    plot.show()
    app.exec_()

