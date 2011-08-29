from PyQt4.Qwt5 import *
from PyQt4.Qwt5.qplt import *

class PlotWidget(QwtPlot):
    """a class that represents a plot"""
    def __init__(self, parent=None):
        super(PlotWidget, self).__init__(parent)
        self.setCanvasBackground(QColor("white"))
        self.setAxisScale(2, 0, 1)
        self.setAxisTitle(2, "X Axis")
        self.setAxisScale(0, 0, 1)
        self.setAxisTitle(0, "Y Axis")

        grid = QwtPlotGrid()
        grid.enableYMin(True)
        grid.setMinPen(QPen(DashLine))
        grid.attach(self)
