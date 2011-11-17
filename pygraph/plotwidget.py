from PyQt4.Qwt5.qplt import QwtPlot, QColor, QwtPlotGrid, QwtLegend, Qwt, \
                            QFont, QwtLinearScaleEngine, QwtText, QPen, \
                            DotLine, QwtPlotZoomer, QwtPicker, Qt,\
                            QwtEventPattern, QwtPlotPicker, SIGNAL, \
                            QRectF, QwtPlotCurve, QBrush, QwtSymbol, \
                            QSize

from PyQt4.Qwt5.qplt import QwtLog10ScaleEngine

import pygraph.data as data

from copy import deepcopy

def shortText(text, length):
    if len(text) < length:
        return text
    else:
        return "..." + text[-length+3:-1] + text[-1]

class PlotWidget(QwtPlot):
    """
        a class that represents a plot

        acurves : dictionary of QwtPlotCurves {datafile: curve}
                  used for the show-all feature
        clist   : list of colors
        curves  : dictionary of QwtPlotCurves {datafile: curve}
        grid    : QwtPlotGrid object
        hidden  : dictionary of Bools {datafile: hidden}
        litems  : legend items
        showall : boolean
        zoomer  : QwtPlotZoom object
    """
    acurves = {}
    clist = []
    curves = {}
    grid = None
    hidden = {}
    litems = {}
    showall = False
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

        # Left click  : zoom
        # Right click : previous zoom settings
        # Shift + Right click : next zoom settings
        # Middle click : first zoom settings
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
        picker.setTrackerFont(QFont(data.settings["Plot/font"]))

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
        self.setAxisFont(QwtPlot.xBottom, QFont(data.settings["Plot/font"]))
        self.setAxisFont(QwtPlot.yLeft, QFont(data.settings["Plot/font"]))

        if data.settings["Plot/xLogScale"]:
            self.setAxisScaleEngine(QwtPlot.xBottom, QwtLog10ScaleEngine())
        else:
            self.setAxisScaleEngine(QwtPlot.xBottom, QwtLinearScaleEngine())

        if data.settings["Plot/yLogScale"]:
            self.setAxisScaleEngine(QwtPlot.yLeft, QwtLog10ScaleEngine())
        else:
            self.setAxisScaleEngine(QwtPlot.yLeft, QwtLinearScaleEngine())

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

        if data.settings["Plot/yLogScale"]:
            ymin = max(ymin, data.settings["Plot/yLogScaleMin"])

        self.setAxisScale(QwtPlot.xBottom, xmin, xmax)
        self.setAxisScale(QwtPlot.yLeft, ymin, ymax)

        txt = QwtText(data.settings["Plot/xAxisTitle"])
        txt.setFont(QFont(data.settings["Plot/font"]))
        self.setAxisTitle(QwtPlot.xBottom, txt)

        txt = QwtText(data.settings["Plot/yAxisTitle"])
        txt.setFont(QFont(data.settings["Plot/font"]))
        self.setAxisTitle(QwtPlot.yLeft, txt)

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

    def plotAll(self, datasets):
        """this function plots all the frames at once"""
        clist = deepcopy(data.colors)
        self.acurves = {}
        for key, dataset in datasets.iteritems():
            self.acurves[key] = []
            mycolor = clist.pop(0)
            basecolor = QColor(mycolor).toHsv()
            for i in xrange(dataset.nframes):
                cf = dataset.frame(i)
                currentColor = QColor()
                currentColor.setHsv(basecolor.hue(), basecolor.saturation(),
                        basecolor.value() * i / dataset.nframes,
                        basecolor.alpha())
                qsymbol = QwtSymbol(QwtSymbol.Rect,
                        QBrush(QColor(currentColor)),
                        QPen(QColor(currentColor)), QSize(3, 3))
                qcurve = QwtPlotCurve()
                qcurve.setData(cf.data_x, cf.data_y)
                qcurve.attach(self)
                qcurve.setPen(QPen(QBrush(QColor(currentColor)), 1))
                qcurve.setSymbol(qsymbol)
                self.legend.remove(qcurve)

                qcurve.setVisible(not self.hidden[key])
                self.legend.remove(qcurve)

                self.acurves[key].append(qcurve)

        self.showall = True
        self.replot()

    def plotFrame(self, datasets, title=None):
        """
            this function plots a single frame from the 'data' dictionary
            data has the form {'name':(xp, yp)} where 'name' is the curve's
            name in the legend and (xp, yp) is a tuple of numpy arrays
            representing the coordinates of the points in the current frame

            WARNING: the 'name' entries have to be unique!!!
        """
        for key, rawdata in datasets.iteritems():
            if not self.curves.has_key(key):
                ltext = shortText(key, data.settings["Plot/legendTextLength"])
                ltext = QwtText(ltext)
                ltext.setFont(QFont(data.settings["Plot/font"],
                    data.settings["Plot/legendFontSize"]))
                self.curves[key] = QwtPlotCurve(ltext)
                self.curves[key].attach(self)

                mycolor = self.clist.pop(0)
                self.curves[key].setPen(QPen(QBrush(QColor(mycolor)), 1))

                qsymbol = QwtSymbol(QwtSymbol.Rect, QBrush(QColor(mycolor)),
                        QPen(QColor(mycolor)), QSize(3, 3))
                self.curves[key].setSymbol(qsymbol)

                self.hidden[key] = False
                self.litems[key] = self.legend.find(self.curves[key])
            else:
                self.hidden[key] = not self.curves[key].isVisible()

            self.curves[key].setData(rawdata.data_x, rawdata.data_y)

        for key, litem in self.litems.iteritems():
            litem.setChecked(not self.hidden[key])
            litem.setIdentifierWidth(24)

        if title is not None:
            tstring = QwtText(title)
            tstring.setFont(QFont(data.settings["Plot/font"],
                data.settings["Plot/titleFontSize"]))
            self.setTitle(tstring)

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
        for key, item in self.curves.iteritems():
            if item == plotItem:
                mykey = key
                break
        self.hidden[mykey] = not status
        if self.showall:
            for c in self.acurves[mykey]:
                c.setVisible(status)
                self.legend.remove(c)
        self.replot()


    def unPlotAll(self):
        """docstring for unPlotAll"""
        for c in self.acurves.values():
            for i in c:
                i.detach()
        self.showall = False
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
