from PyQt4.Qwt5 import *
from PyQt4.Qwt5.qplt import *

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


        self.defaultOptions = {"xMin":0, "xMax":1, "yMin":0, "yMax":1,
                          "xAxisTitle":"X Axis", "yAxisTitle":"Y Axis",
                          "xMinEnabled":False, "yMinEnabled":False,
                         } 
        self.applyOptions()


    def applyOptions(self, options=None):
        """
            this function applies options to the plot
            options expected:
                (double) xMin, xMax, yMin, yMax  :  canvas edges
                (string) xAxisTitle, yAxisTitle  :  axes titles
                (bool) xMinEnabled, yMinEnabled  :  enable minor grid
        
        """
        if options == None:
            self.applyOptions(self.defaultOptions)
            return

            self.setAxisScale(self.xAxisId, options["xMin"], options["xMax"])
            self.setAxisScale(self.yAxisId, options["yMin"], options["yMax"])
            self.setAxisTitle(self.xAxisId, options["xAxisTitle"])
            self.setAxisTitle(self.yAxisId, options["yAxisTitle"])
            
            self.grid.enableXMin(options["xMinEnabled"])
            self.grid.enableYMin(options["yMinEnabled"])

            # following option can't be modified, for now
            self.grid.setMinPen(QPen(DashLine))

        self.replot()
