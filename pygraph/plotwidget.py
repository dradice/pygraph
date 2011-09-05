from PyQt4.Qwt5 import *
from PyQt4.Qwt5.qplt import *

class PlotWidget(QwtPlot):
    """a class that represents a plot"""
    def __init__(self, settings, parent=None):
        super(PlotWidget, self).__init__(parent)
        self.setCanvasBackground(QColor("white"))

        # the two following variables are meant to avoid misunderstandings
        self.xAxisId = 2
        self.yAxisId = 0

        self.grid = QwtPlotGrid()
        self.grid.attach(self)

        QwtPlotZoomer(self.canvas())

        self.applySettings(settings)


    def applySettings(self, settings):
        """
            this function applies settings to the plot
            options expected:
                (float) xMin, xMax, yMin, yMax  :  canvas edges
                (string) xAxisTitle, yAxisTitle  :  axes titles
                (bool) xMinEnabled, yMinEnabled  :  enable minor grids
        
        """
        self.setAxisScale(self.xAxisId, settings["xMin"], settings["xMax"])
        self.setAxisScale(self.yAxisId, settings["yMin"], settings["yMax"])
        self.setAxisTitle(self.xAxisId, settings["xAxisTitle"])
        self.setAxisTitle(self.yAxisId, settings["yAxisTitle"])
        
        self.grid.enableXMin(settings["xMinEnabled"])
        self.grid.enableYMin(settings["yMinEnabled"])

        # following option can't be modified, for now
        self.grid.setMinPen(QPen(DashLine))

        self.replot()
