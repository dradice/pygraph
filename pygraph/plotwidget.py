from PyQt4.Qwt5 import *
from PyQt4.Qwt5.qplt import *

import pygraph.data as data

from copy import deepcopy

class PlotWidget(QwtPlot):
    """
        a class that represents a plot

        clist  : list of colors
        curves : dictionary of QwtPlotCurves {datafile: curve}
        grid   : QwtPlotGrid object
    """
    clist = []
    curves = {}
    grid = None
    zoomer = None

    def __init__(self, parent=None):
        super(PlotWidget, self).__init__(parent)
        self.setCanvasBackground(QColor("white"))

        self.grid = QwtPlotGrid()
        self.grid.attach(self)

        # Using a name in legend: 
        # all the work was adding "key" as an argument of QwtPlotCurve()
        # constructor at line ~128
        self.legend = QwtLegend()
        self.legend.setItemMode(Qwt.QwtLegend.CheckableItem)
        self.insertLegend(self.legend, Qwt.QwtPlot.RightLegend)
        
        self.applySettings()

        self.zoomer = QwtPlotZoomer(QwtPlot.xBottom, QwtPlot.yLeft,
                QwtPicker.DragSelection, QwtPicker.AlwaysOff, self.canvas())
        self.zoomer.setRubberBandPen(QPen(Qt.green))

        pattern = [
            QwtEventPattern.MousePattern(Qt.LeftButton, Qt.NoModifier),
            QwtEventPattern.MousePattern(Qt.MidButton, Qt.NoModifier),
            QwtEventPattern.MousePattern(Qt.RightButton, Qt.NoModifier),
            QwtEventPattern.MousePattern(Qt.LeftButton, Qt.ShiftModifier),
            QwtEventPattern.MousePattern(Qt.MidButton, Qt.ShiftModifier),
            QwtEventPattern.MousePattern(Qt.RightButton, Qt.ShiftModifier),
            ]
        self.zoomer.setMousePattern(pattern)

        picker = QwtPlotPicker(QwtPlot.xBottom, QwtPlot.yLeft,
                QwtPicker.NoSelection, QwtPlotPicker.CrossRubberBand,
                QwtPicker.AlwaysOn, self.canvas())
        picker.setTrackerPen(QPen(Qt.red))

        self.clist = deepcopy(data.colors)

        self.connect(self,
                     SIGNAL("legendChecked(QwtPlotItem*, bool)"),
                     self.toggleVisibility)

        self.connect(self.zoomer, SIGNAL("zoomed(const QwtDoubleRect &)"),
                self.updateSize)


    def applySettings(self):
        """
            this function applies settings to the plot
            options expected:
                (float) Plot/xMin, Plot/xMax, Plot/yMin, Plot/yMax: canvas edges
                (string) Plot/xAxisTitle, Plot/yAxisTitle:  axes titles
                (bool) Plot/xMinEnabled, Plot/yMinEnabled:  enable minor grids

        """
        interval_x = self.axisScaleDiv(QwtPlot.xBottom)
        interval_y = self.axisScaleDiv(QwtPlot.yLeft)

        xmin_old = interval_x.lowerBound()
        xmax_old = interval_x.upperBound()
        ymin_old = interval_y.lowerBound()
        ymax_old = interval_y.upperBound()

        xmin = data.settings["Plot/xMin"]
        xmax = data.settings["Plot/xMax"]

        ymin = data.settings["Plot/yMin"]
        ymax = data.settings["Plot/yMax"]

        self.setAxisScale(QwtPlot.xBottom, xmin, xmax)
        self.setAxisScale(QwtPlot.yLeft, ymin, ymax)
        self.setAxisTitle(QwtPlot.xBottom, data.settings["Plot/xAxisTitle"])
        self.setAxisTitle(QwtPlot.yLeft, data.settings["Plot/yAxisTitle"])

        self.grid.enableX(data.settings["Plot/xGridEnabled"])
        self.grid.enableY(data.settings["Plot/yGridEnabled"])

        # following option can't be modified, for now
        self.grid.setPen(QPen(DotLine))

        self.replot()

        # Add the new zoom to the zoomstack
        # this should not be executed when this method is called by __init__
        # i.e. when self.zoomer is None
        if self.zoomer is not None and (
                xmin_old != xmin or xmax_old != xmax or
                ymin_old != ymin or ymax_old != ymax):
            zoomStack = self.zoomer.zoomStack()
            zoomStack.append(QRectF(xmin, ymin, xmax-xmin, ymax-ymin))
            self.zoomer.setZoomStack(zoomStack)

        # this sets the current axis as zoom base
        #self.zoomer.setZoomBase(True)


    def plotFrame(self, data, title=None):
        """
            this function plots a single frame from the 'data' dictionary
            data has the form {'name':(xp, yp)} where 'name' is the curve's
            name in the legend and (xp, yp) is a tuple of numpy arrays
            representing the coordinates of the points in the current frame

            WARNING: the 'name' entries have to be unique!!!
        """
        for key, rawdata in data.iteritems():
            if not self.curves.has_key(key):
                self.curves[key] = QwtPlotCurve(key)
                self.curves[key].attach(self)

                mycolor = self.clist.pop(0)
                self.curves[key].setPen(QPen(QBrush(QColor(mycolor)), 1))

                qsymbol = QwtSymbol(QwtSymbol.Rect, QBrush(QColor(mycolor)),
                        QPen(QColor(mycolor)), QSize(3, 3))
                self.curves[key].setSymbol(qsymbol)
                
            self.curves[key].setData(rawdata.data_x, rawdata.data_y)

        for litem in self.legend.legendItems():
            litem.setChecked(True)
            litem.setIdentifierWidth(24)

        if title is not None:
            self.setTitle(title)

        self.replot()


    def resetZoomer(self):
        """
            Reset the zoomer stack
        """
        self.zoomer.setZoomBase(True)


    def toggleVisibility(self, plotItem, status):
        """
            toggles the visibility of a plot item
            (as suggested by PyQwt Source code)
        """
        plotItem.setVisible(status)
        self.replot()


    def updateSize(self):
        """
            Update the plot ranges after a zoom
        """
        interval_x = self.axisScaleDiv(QwtPlot.xBottom)
        interval_y = self.axisScaleDiv(QwtPlot.yLeft)

        data.settings["Plot/xMin"] = interval_x.lowerBound()
        data.settings["Plot/xMax"] = interval_x.upperBound()
        data.settings["Plot/yMin"] = interval_y.lowerBound()
        data.settings["Plot/yMax"] = interval_y.upperBound()
