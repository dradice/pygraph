from PyQt4.Qwt5 import *
from PyQt4.Qwt5.qplt import *

from pygraph.data import settings

class PlotWidget(QwtPlot):
    """a class that represents a plot"""
    def __init__(self, parent=None):
        super(PlotWidget, self).__init__(parent)
        self.setCanvasBackground(QColor("white"))

        # the two following variables are meant to avoid misunderstandings
        self.xAxisId = 2
        self.yAxisId = 0

        self.grid = QwtPlotGrid()
        self.grid.attach(self)

        QwtPlotZoomer(self.canvas())
        legend = QwtLegend()
#        self.insertLegend(legend)

        self.applySettings()

        curves = []
        """
            if we want to handle multiple curves, we may want to define this
            list of curves to repeatedly call plot methods on its elements.
        """


    def applySettings(self):
        """
            this function applies settings to the plot
            options expected:
                (float) xMin, xMax, yMin, yMax  :  canvas edges
                (string) xAxisTitle, yAxisTitle  :  axes titles
                (bool) xMinEnabled, yMinEnabled  :  enable minor grids

        """
        self.setAxisScale(self.xAxisId, settings["Plot/xMin"],
                settings["Plot/xMax"])
        self.setAxisScale(self.yAxisId, settings["Plot/yMin"],
                settings["Plot/yMax"])
        self.setAxisTitle(self.xAxisId, settings["Plot/xAxisTitle"])
        self.setAxisTitle(self.yAxisId, settings["Plot/yAxisTitle"])

        self.grid.enableXMin(settings["Plot/xMinEnabled"])
        self.grid.enableYMin(settings["Plot/yMinEnabled"])

        # following option can't be modified, for now
        self.grid.setMinPen(QPen(DashLine))

        self.replot()


    def plotFrame(self, curve, data):
        """
            this function plots a single frame from the 'data' dictionary
            data has the form {'name':(xp, yp)} where 'name' is the curve's
            name in the legend and (xp, yp) is a tuple of numpy arrays
            representing the coordinates of the points in the current frame
        """
        title = data.keys()[0]
        points = data.values()[0]

        curve.setData(points[0], points[1])
        self.replot()

