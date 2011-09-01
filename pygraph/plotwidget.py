from PyQt4.Qwt5 import *
from PyQt4.Qwt5.qplt import *

class PlotWidget(QwtPlot):
    """a class that represents a plot"""
    def __init__(self, parent=None):
        super(PlotWidget, self).__init__(parent)
        self.setCanvasBackground(QColor("white"))
        xMin = 0
        xMax = 1
        yMin = 0
        yMax = 1
        self.setAxisScale(2, xMin, xMax)
        self.setAxisTitle(2, "X Axis")
        self.setAxisScale(0, yMin, yMax)
        self.setAxisTitle(0, "Y Axis")

        grid = QwtPlotGrid()
        grid.enableYMin(True)
        grid.setMinPen(QPen(DashLine))
        grid.attach(self)

        QwtPlotZoomer(self.canvas())
