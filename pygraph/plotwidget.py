from __future__ import division

from qwt import *
from PyQt5.QtGui import QBrush, QColor, QFont, QPen
from PyQt5.QtWidgets import QRubberBand
from PyQt5.QtCore import QPoint, QRect, QSize, QSizeF, Qt, pyqtSignal

import pygraph.common as common

from copy import deepcopy

def shortText(text, length):
    if len(text) < length:
        return text
    else:
        return text[0:length//2] + "..." + text[-length//2:]

class ZoomStack(object):
    """
        Helper class for zooming on parts of the plot
    """
    def __init__(self):
        """
        parent : PlotWidget
        """
        self.base = (0, 1, 0, 1)
        self.reset()
    def reset(self):
        """
        reset the zoom tool
        """
        self.zoom_stack = []

    def getZoomBase(self):
        return self.base
    def setZoomBase(self, rect):
        """
        Set the base zoom
        """
        self.base = rect

    def addToStack(self, rect):
        """
        Add selection to the zoom stack
        """
        self.zoom_stack.append(rect)

    def getCurrZoom(self):
        """
        Get current zoom level
        """
        try:
            return self.zoom_stack[-1]
        except IndexError:
            return self.base
    def getPrevZoom(self):
        """
        Get previous zoom level
        """
        try:
            self.zoom_stack.pop()
            return self.zoom_stack[-1]
        except IndexError:
            return self.base


class PlotWidget(QwtPlot):
    """
        a class that represents a plot

        acurves     : dictionary of QwtPlotCurves {datafile: curve}
                      used for the show-all feature
        clist       : list of colors
        curves      : dictionary of QwtPlotCurves {datafile: curve}
        grid        : QwtPlotGrid object
        hidden      : dictionary of Bools {datafile: hidden}
        litems      : legend items
        showall     : boolean
        origin      : origin of the rectangular selection
        zstack      : zoom stack
        rubber_band : QRubberBand
    """
    changedStatus = pyqtSignal()
    def __init__(self, parent=None):
        super(PlotWidget, self).__init__(parent)
        self.setCanvasBackground(QColor("white"))

        self.acurves = {}
        self.clist = []
        self.curves = {}
        self.grid = None
        self.hidden = {}
        self.litems = {}
        self.showall = False
        self.zoomer = None

        self.grid = QwtPlotGrid()
        self.grid.attach(self)

        legend = QwtLegend()
        legend.setDefaultItemMode(QwtLegendData.Checkable)
        self.insertLegend(legend, pos=QwtPlot.RightLegend)

        self.zstack = ZoomStack()
        self.origin = QPoint()
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)

        self.clist = deepcopy(common.colors)

        legend.checked.connect(self.toggleVisibility)

        self.setMouseTracking(True)
        self.canvas().setMouseTracking(True)
        self.applySettings()

    def applySettings(self):
        """
            this function applies settings to the plot
        """
        self.setAxisFont(QwtPlot.xBottom, QFont(common.settings["Plot/font"]))
        self.setAxisFont(QwtPlot.yLeft, QFont(common.settings["Plot/font"]))

        if common.settings["Plot/xLogScale"]:
            self.setAxisScaleEngine(QwtPlot.xBottom, QwtLogScaleEngine())
        else:
            self.setAxisScaleEngine(QwtPlot.xBottom, QwtLinearScaleEngine())

        if common.settings["Plot/yLogScale"]:
            self.setAxisScaleEngine(QwtPlot.yLeft, QwtLogScaleEngine())
        else:
            self.setAxisScaleEngine(QwtPlot.yLeft, QwtLinearScaleEngine())

        interval_x = self.axisScaleDiv(QwtPlot.xBottom)
        interval_y = self.axisScaleDiv(QwtPlot.yLeft)
        if interval_x is not None:
            xmin_old = interval_x.lowerBound()
            xmax_old = interval_x.upperBound()
        if interval_y is not None:
            ymin_old = interval_y.lowerBound()
            ymax_old = interval_y.upperBound()

        xmin = common.settings["Plot/xMin"]
        xmax = common.settings["Plot/xMax"]
        ymin = common.settings["Plot/yMin"]
        ymax = common.settings["Plot/yMax"]

        if common.settings["Plot/xLogScale"]:
            xmin = max(xmin, common.settings["Plot/xLogScaleMin"])
        if common.settings["Plot/yLogScale"]:
            ymin = max(ymin, common.settings["Plot/yLogScaleMin"])

        self.setAxisScale(QwtPlot.xBottom, xmin, xmax)
        self.setAxisScale(QwtPlot.yLeft, ymin, ymax)

        txt = QwtText(common.settings["Plot/xAxisTitle"])
        txt.setFont(QFont(common.settings["Plot/font"]))
        self.setAxisTitle(QwtPlot.xBottom, txt)

        txt = QwtText(common.settings["Plot/yAxisTitle"])
        txt.setFont(QFont(common.settings["Plot/font"]))
        self.setAxisTitle(QwtPlot.yLeft, txt)

        self.grid.enableX(common.settings["Plot/xGridEnabled"])
        self.grid.enableY(common.settings["Plot/yGridEnabled"])

        self.grid.setPen(QPen(Qt.DotLine))

        self.replot()

        self.zstack.reset()
        self.zstack.setZoomBase((xmin, xmax, ymin, ymax))

    def getCoordinates(self, pos):
        """
            Computes the coordinates of a given point

            * pos: QPoint
        """
        return (self.invTransform(QwtPlot.xBottom, pos.x() - self.canvas().x()),
                self.invTransform(QwtPlot.yLeft,   pos.y() - self.canvas().y()))

    def mousePressEvent(self, event):
        """
            Left click event: start zoom selection
        """
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.rubber_band.setGeometry(QRect(self.origin, QSize()))
            self.rubber_band.show()
        QwtPlot.mousePressEvent(self, event)
    def mouseMoveEvent(self, event):
        """
            Mouse movement
        """
        if self.rubber_band.isVisible():
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())
        common.status = "{:g} {:g}".format(*self.getCoordinates(event.pos()))
        self.changedStatus.emit()
        QwtPlot.mouseMoveEvent(self, event)
    def mouseReleaseEvent(self, event):
        """
            Mouse release event
            Left click: finish zoom selection
            Right click: previous zoom level
        """
        if event.button() == Qt.LeftButton:
            if self.rubber_band.isVisible():
                x0, y0 = self.getCoordinates(self.origin)
                x1, y1 = self.getCoordinates(event.pos())
                rect_old = self.zstack.getCurrZoom()
                rect_new = tuple(sorted([x0, x1]) + sorted([y0, y1]))

                # Filter out spurious clicks
                F = common.settings["Plot/maxZoomFactor"]
                if (rect_new[1] - rect_new[0]) > (1./F) * (rect_old[1] - rect_old[0]) and \
                   (rect_new[3] - rect_new[2]) > (1./F) * (rect_old[3] - rect_old[2]):
                    self.zstack.addToStack(rect_new)
                    self.setAxisScale(QwtPlot.xBottom, rect_new[0], rect_new[1])
                    self.setAxisScale(QwtPlot.yLeft,   rect_new[2], rect_new[3])
                self.origin = QPoint()
                self.rubber_band.hide()
        elif event.button() == Qt.RightButton:
            rect = self.zstack.getPrevZoom()
            self.setAxisScale(QwtPlot.xBottom, rect[0], rect[1])
            self.setAxisScale(QwtPlot.yLeft,   rect[2], rect[3])
        QwtPlot.mouseReleaseEvent(self, event)
        self.replot()

    def plotAll(self, datasets):
        """this function plots all the frames at once"""
        clist = deepcopy(common.colors)
        self.acurves = {}
        for key in datasets.keys():
            dataset = datasets[key]
            self.acurves[key] = []
            mycolor = clist.pop(0)
            basecolor = QColor(mycolor).toHsv()
            nframe = common.settings["Plot/maxFramesForPlotAll"]
            if nframe < dataset.nframes:
                fac = dataset.nframes//nframe
            else:
                fac = 1
                nframe = dataset.nframes
            for i in range(nframe):
                cf = dataset.frame(i*fac)
                currentColor = QColor()
                currentColor.setHsv(basecolor.hue(), basecolor.saturation(),
                        basecolor.value() * i//nframe,
                        basecolor.alpha())
                qsymbol = QwtSymbol(QwtSymbol.Rect,
                        QBrush(QColor(currentColor)),
                        QPen(QColor(currentColor)), QSizeF(3, 3))
                qcurve = QwtPlotCurve()
                qcurve.setSymbol(qsymbol)
                qcurve.setPen(QPen(QBrush(currentColor), 1))
                qcurve.setData(cf.data_x, cf.data_y)
                qcurve.setItemAttribute(QwtPlotItem.Legend, False)
                qcurve.attach(self)

                qcurve.setVisible(not self.hidden[key])

                self.acurves[key].append(qcurve)

        self.showall = True
        self.replot()

    def plotFrame(self, datasets, title=None):
        """
            this function plots a single frame from the 'data' dictionary
            data has the form {'name':(xp, yp)}L where 'name' is the curve's
            name in the legend and (xp, yp) is a tuple of numpy arrays
            representing the coordinates of the points in the current frame
            WARNING: the 'name' entries have to be unique!!!
        """
        for key in datasets.keys():
            rawdata = datasets[key]
            if key not in self.curves:
                ltext = shortText(key, int(common.settings["Plot/legendTextLength"]))
                ltext = QwtText(ltext)
                ltext.setFont(QFont(common.settings["Plot/font"],
                    common.settings["Plot/legendFontSize"]))
                self.curves[key] = QwtPlotCurve(ltext)

                try:
                    mycolor = self.clist.pop(0)
                except:
                    self.clist = deepcopy(common.colors)
                    mycolor = self.clist.pop(0)
                self.curves[key].setPen(QPen(QBrush(QColor(mycolor)), 1))

                qsymbol = QwtSymbol(QwtSymbol.Rect, QBrush(QColor(mycolor)),
                        QPen(QColor(mycolor)), QSizeF(3, 3))
                self.curves[key].setSymbol(qsymbol)

                self.curves[key].attach(self)
                self.hidden[key] = False

                self.litems[key] = self.legend().legendWidget(self.curves[key])
                self.litems[key].setChecked(True)
            else:
                self.hidden[key] = not self.curves[key].isVisible()

            self.curves[key].setData(rawdata.data_x, rawdata.data_y)

        if title is not None:
            tstring = QwtText(title)
            tstring.setFont(QFont(common.settings["Plot/font"],
                common.settings["Plot/titleFontSize"]))
            self.setTitle(tstring)

        self.replot()

    def resetZoom(self):
        """
            Reset the zoom level of the plot
        """
        rect = self.zstack.getZoomBase()
        self.setAxisScale(QwtPlot.xBottom, rect[0], rect[1])
        self.setAxisScale(QwtPlot.yLeft,   rect[2], rect[3])
        self.zstack.reset()
    resetPlot = resetZoom

    def resetLegend(self):
        """
            Reset the name of the fields in the legend
        """
        for key, item in self.curves.items():
            ltext = shortText(key, int(common.settings["Plot/legendTextLength"]))
            ltext = QwtText(ltext)
            ltext.setFont(QFont(common.settings["Plot/font"],
                    common.settings["Plot/legendFontSize"]))
            item.setTitle(ltext)
        self.updateLayout()

    def toggleVisibility(self, plotItem, status):
        """
            toggles the visibility of a plot item
            (as suggested by PyQwt Source code)
        """
        plotItem.setVisible(status)
        for key, item in self.curves.items():
            if item == plotItem:
                mykey = key
                break
        self.hidden[mykey] = not status
        if self.showall:
            for c in self.acurves[mykey]:
                c.setVisible(status)
        self.replot()

    def unPlotAll(self):
        """docstring for unPlotAll"""
        for c in self.acurves.values():
            for i in c:
                i.detach()
        self.showall = False
        self.replot()
