from copy import deepcopy
import numpy as np
from pygraph.common import debug_print
import pygraph.common as common
from pygraph.dataeditor import DataEditor
from pygraph.hardcopy import Hardcopy
from pygraph.datasets import DataSetType, DataSet
from pygraph.plotsettings import PlotSettings
from pygraph.plotwidget import PlotWidget
from scidata.utils import FileTypeError

import pygraph.resources

from PyQt5.QtCore import Qt, QPoint, QSettings, QSize, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QFileDialog, QInputDialog, \
        QMainWindow, QSlider, QMessageBox, QWidget
import math
import re
import sys
import os

class MainWindow(QMainWindow):
    """
    pygraph main window class

    Members
    * dataset    : a dictionary of DataSets
    * iframe     : currently displayed frame
    * plotwidget : the plot widget
    * playAction : the "play" action
    * pauseAction: the "pause" action
    * plotAllFlag: a flag to check wheter plotAll feature is being used or not
    * rjustSize  : maximum length of the "time" string
    * tfinal     : final time
    * time       : current (physical) time
    * timer      : QTimer()
    * timestep   : timestep
    * tinit      : initial time
    """

###############################################################################
# Initialization methods
###############################################################################

    def __init__(self, args=None, options=None, parent=None):
        """
        Setup the main window and import all the given files
        """
        super(MainWindow, self).__init__(parent)

        self.datasets    = {}
        self.iframe     = 0
        self.playAction  = None
        self.pauseAction = None
        self.plotAllFlag = False
        self.plotwidget  = None
        self.tfinal      = 0
        self.time        = 0
        self.timer       = None
        self.timestep    = sys.float_info.max
        self.tinit       = 0

        # Read data
        self.parseCLI(args, options)
        for key, dset in self.datasets.items():
            try:
                dset.read_data()
            except FileTypeError as e:
                QMessageBox.critical(self, "I/O Error",
                        "Could not read file " + str(e))
                raise
            except:
                QMessageBox.critical(self, "I/O Error",
                        "Coud not read dataset " + key)
                raise
        self.updateData()

        # Restore settings
        qset = QSettings()

        common.settings["Animation/FPS"] = float(qset.value("Animation/FPS",
                common.settings["Animation/FPS"]))
        common.settings["Animation/MaxNFrames"] = int(qset.value(
            "Animation/MaxNFrames", common.settings["Animation/MaxNFrames"]))

        position = qset.value("MainWindow/Position", (QPoint(0,0)))
        self.move(position)
        size = qset.value("MainWindow/Size", (QSize(600,400)))
        self.resize(size)

        common.settings["DataEditor/Position"] = \
                qset.value("DataEditor/Position",
                common.settings["DataEditor/Position"])
        common.settings["DataEditor/Size"] = qset.value("DataEditor/Size",
                common.settings["DataEditor/Size"])

        common.settings["PlotSettings/Position"] = qset.value(
                "PlotSettings/Position",
                common.settings["PlotSettings/Position"])
        common.settings["PlotSettings/Size"] = qset.value(
                "PlotSettings/Size", common.settings["PlotSettings/Size"])

        common.settings["PyGraph/Debug"] = qset.value(
            "PyGraph/Debug", str(common.settings[
                "PyGraph/Debug"])) == 'True'

        common.settings["Plot/legendTextLength"] = qset.value(
            "Plot/legendTextLength", common.settings["Plot/legendTextLength"])
        common.settings["Plot/xGridEnabled"] = qset.value(
            "Plot/xGridEnabled", str(common.settings["Plot/xGridEnabled"])) \
                    == 'True'
        common.settings["Plot/yGridEnabled"] = qset.value(
            "Plot/yGridEnabled", str(common.settings["Plot/yGridEnabled"])) \
                    == 'True'

        common.settings["PlotSettings/Position"] = qset.value(
                "PlotSettings/Position",
                    common.settings["PlotSettings/Position"])
        common.settings["PlotSettings/Size"] = qset.value("PlotSettings/Size",
                common.settings["PlotSettings/Size"])

        self.timer = QTimer()
        self.timer.setInterval(int(1000.0/common.settings["Animation/FPS"]))

        common.settings["Plot/yLogScale"] = options.logscale

        # Create plot
        self.plotwidget = PlotWidget(self)
        self.setCentralWidget(self.plotwidget)
        self.plotwidget.changedStatus.connect(self.updateStatusBar)

        # Basic actions
        importDataAction = self.createAction("&Import...", self.importDataSlot,
                "Ctrl+I", "document-open", "Import a data file")
        exportDataAction = self.createAction("&Export...", self.exportFrameSlot,
                "Ctrl+S", "document-save-as", "Export the current frame")
        hardcopyAction = self.createAction("&Hardcopy", self.hardcopySlot,
                "Ctrl+C", "document-save-as", "Hardcopy")
        quitAction = self.createAction("&Quit", self.close,
                "Ctrl+Q", "system-log-out", "Close the application")

        # Edit actions
        dataEditAction = self.createAction("&Data...", self.dataEditSlot,
                "Ctrl+D", None, "Edit the data")
        plotSettingsAction = self.createAction("&Plot...",
                self.plotSettingsSlot, "Ctrl+P", None, "Plot preferences")
        legendEditAction = self.createAction("&Legend...", self.legendEditSlot,
                "Ctrl+L", None, "Maximum length of the items in the legend")
        FPSEditAction = self.createAction("&FPS...", self.FPSEditSlot,
                "Ctrl+F", None, "Set the number of frames per second")
        resetPlotAction = self.createAction("Reset", self.resetPlotSlot,
                "Esc", None, "Reset plot")
        reloadDataAction = self.createAction("&Reload", self.reloadDataSlot,
                "Ctrl+R", "file-view-refresh", "Reload data")

        # Controls actions
        self.playAction = self.createAction("&Play", self.playSlot,
                "Space", "media-playback-start", "Visualize the data")
        self.pauseAction = self.createAction("&Pause", self.pauseSlot,
                "Space", "media-playback-pause", "Pause the visualization")
        stepBackwardAction = self.createAction("Step &Backward",
                self.stepBackwardSlot, "Left", "media-step-backward",
                "Go back of one frame")
        stepForwardAction = self.createAction("Step &Forward",
                self.stepForwardSlot, "Right", "media-step-forward",
                "Advance of one frame")
        gotoStartAction = self.createAction("&Start", self.gotoStartSlot,
                "Ctrl+Left", "media-skip-backward", "Goto the first frame")
        gotoEndAction = self.createAction("&End", self.gotoEndSlot,
                "Ctrl+Right", "media-skip-forward", "Goto the last frame")
        gotoTimeAction = self.createAction("&Go to...", self.gotoTimeSlot,
                "Ctrl+G", None, "Go to a given point in time")
        plotAllAction = self.createAction("&Show all", self.plotAll,
                "Ctrl+A", None, "Plot/unplot all the frames at once")

        # Help actions
        helpAboutAction = self.createAction("&About pygraph", self.aboutSlot)
        helpHelpAction = self.createAction("&Contents", self.helpSlot,
                "Ctrl+H", "help-browser")

        # File menu
        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction(importDataAction)
        fileMenu.addAction(exportDataAction)
        fileMenu.addAction(hardcopyAction)
        fileMenu.addSeparator()
        fileMenu.addAction(quitAction)

        # Edit menu
        editMenu = self.menuBar().addMenu("&Edit")
        editMenu.addAction(dataEditAction)
        editMenu.addAction(plotSettingsAction)
        editMenu.addAction(legendEditAction)
        editMenu.addAction(FPSEditAction)
        editMenu.addAction(resetPlotAction)
        editMenu.addAction(reloadDataAction)

        # Play menu
        playMenu = self.menuBar().addMenu("&Play")
        playMenu.addAction(self.playAction)
        playMenu.addAction(self.pauseAction)
        playMenu.addSeparator()
        playMenu.addAction(gotoStartAction)
        playMenu.addAction(stepBackwardAction)
        playMenu.addAction(stepForwardAction)
        playMenu.addAction(gotoEndAction)
        playMenu.addSeparator()
        playMenu.addAction(gotoTimeAction)
        playMenu.addSeparator()
        playMenu.addAction(plotAllAction)

        self.playAction.setEnabled(True)
        self.playAction.setVisible(True)
        self.pauseAction.setEnabled(False)
        self.pauseAction.setVisible(False)

        # Help menu
        helpMenu = self.menuBar().addMenu("&Help")
        helpMenu.addAction(helpHelpAction)
        helpMenu.addAction(helpAboutAction)

        # Play toolbar
        playToolbar = self.addToolBar("Play")
        playToolbar.setFloatable(False)
        playToolbar.setMovable(False)
        playToolbar.setObjectName("PlayToolbar")
        playToolbar.setIconSize(common.settings['ToolBar/IconSize'])
        playToolbar.addAction(gotoStartAction)
        playToolbar.addAction(stepBackwardAction)
        playToolbar.addAction(self.playAction)
        playToolbar.addAction(self.pauseAction)
        playToolbar.addAction(stepForwardAction)
        playToolbar.addAction(gotoEndAction)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setTracking(True)
        self.slider.sliderMoved.connect(self.sliderSlot)

        playToolbar.addWidget(self.slider)

        self.statusBar()

        if(len(self.datasets) > 0):
            self.setLimits()
            self.setTimer()
            self.plotFrame()

        self.timer.timeout.connect(self.timeout)

    def parseColNumber(self, args, groupMode):
        if groupMode:
            for arg in args:
                if arg == '}':
                    return None
                elif arg[0] == '^':
                    return int(arg[1:])
            debug_print("Unmatched '{' in command line!")
            exit(1)
        else:
            try:
                if args[0][0] == '^':
                    return int(args[0][1:])
            except IndexError:
                pass
            return None

    def parseCLI(self, args, options):
        """
        Parse the command line options
        """
        currKey   = None
        groupMode = False
        mapMode   = False
        while len(args) > 0:
            arg = args.pop(0)
            if arg == '{':
                debug_print("{")
                if '}' not in args:
                    debug_print("Unmatched '{' in command line!")
                    exit(1)
                groupMode = True
                if not mapMode:
                    currKey = arg = args.pop(0)
                    col = self.parseColNumber(args, groupMode)
                    if col is not None:
                        currKey = arg + "^" + str(col)
                    debug_print("A " + arg)
                    self.datasets[currKey] = DataSet(currKey,
                            DataSetType.guess_from_name(arg), options.reflevel)
                    self.datasets[currKey].add_datafile(arg, None, col)
            elif arg == '@':
                if groupMode:
                    debug_print("'@' inside a '{' '}' block!")
                    exit(1)
                mapMode   = True
            elif arg == '}':
                debug_print("}")
                groupMode = False
                mapMode   = False
            elif arg[0] == '^':
                pass
            else:
                if mapMode:
                    debug_print("M " + arg)
                    col = self.parseColNumber(args, groupMode)
                    self.datasets[currKey].add_mapfile(arg, None, col)
                    if not groupMode:
                        currKey = None
                        mapMode = False
                elif groupMode:
                    debug_print("A " + arg)
                    col = self.parseColNumber(args, groupMode)
                    self.datasets[currKey].add_datafile(arg, None, col)
                else:
                    debug_print("A " + arg)
                    currKey = arg
                    col = self.parseColNumber(args, groupMode)
                    if col is not None:
                        currKey = arg + "^" + str(col)
                    self.datasets[currKey] = DataSet(currKey,
                            DataSetType.guess_from_name(arg), options.reflevel)
                    self.datasets[currKey].add_datafile(arg, None, col)

    def closeEvent(self, event):
        """
        Store the settings
        """
        qset = QSettings()
        qset.setValue("Animation/FPS",
                (common.settings["Animation/FPS"]))
        qset.setValue("Animation/MaxNFrames",
                (common.settings["Animation/MaxNFrames"]))
        qset.setValue("MainWindow/Position", (self.pos()))
        qset.setValue("MainWindow/Size", (self.size()))
        qset.setValue("DataEditor/Position",
                (common.settings["DataEditor/Position"]))
        qset.setValue("DataEditor/Size",
                (common.settings["DataEditor/Size"]))
        qset.setValue("PyGraph/Debug",
                str(common.settings["PyGraph/Debug"]))
        qset.setValue("Plot/legendTextLength",
                (common.settings["Plot/legendTextLength"]))
        qset.setValue("Plot/xGridEnabled",
                str(common.settings["Plot/xGridEnabled"]))
        qset.setValue("Plot/yGridEnabled",
                str(common.settings["Plot/yGridEnabled"]))
        qset.setValue("PlotSettings/Position",
                (common.settings["PlotSettings/Position"]))
        qset.setValue("PlotSettings/Size",
                (common.settings["PlotSettings/Size"]))

###############################################################################
# Utility methods
###############################################################################

    def updateData(self):
        """
        Computes the working data from the initial data
        """
        for dset in self.datasets.values():
            dset.transform_data()

    def setLimits(self):
        """
        Compute the optimial size and location of the axis
        """
        xmin =   sys.float_info.max
        xmax = - sys.float_info.max
        ymin =   sys.float_info.max
        ymax = - sys.float_info.max
        for dset in self.datasets.values():
            xmin = min(xmin, dset.data.data_x.min())
            xmax = max(xmax, dset.data.data_x.max())
            ymin = min(ymin, dset.data.data_y.min())
            ymax = max(ymax, dset.data.data_y.max())

        size = ymax - ymin

        common.settings['Plot/xMin'] = xmin
        common.settings['Plot/xMax'] = xmax
        common.settings['Plot/yMin'] = ymin - 0.1*size
        common.settings['Plot/yMax'] = ymax + 0.1*size

        self.plotwidget.applySettings()

    def setTimer(self):
        """
        Computes initial and final time, as well as the timestep
        """
        self.iframe = 0

        # Computes initial and final time
        self.tfinal = max([dset.data.time[-1] for dset in \
                self.datasets.values()])
        self.tinit = min([dset.data.time[0] for dset in \
                self.datasets.values()])
        self.time = self.tinit

        # Computes timestep
        self.timestep = sys.float_info.max
        for dset in self.datasets.values():
            if len(dset.data.time) > 1:
                t_arr = np.array(dset.data.time)
                dt_arr = np.diff(t_arr)
                idx = dt_arr > 1e-10*t_arr.max()
                dt = dt_arr[idx].max()
            else:
                dt = 1.0
            self.timestep = min(self.timestep, dt)
        self.nframes = int((self.tfinal - self.tinit)/self.timestep) + 1
        self.nframes = min(self.nframes,common.settings["Animation/MaxNFrames"])
        if self.nframes > 1:
            self.timestep = (self.tfinal - self.tinit)/(self.nframes - 1)
        self.slider.setRange(0, self.nframes-1)
        self.slider.setValue(0)

        # Formatting options for the time
        n1 = len(str(int(self.tfinal)))
        st = str(self.timestep)
        idx = st.find('.')
        if idx >= 0:
            n2 = len(st[idx + 1:])
        else:
            n2 = 1
        nt = n1 + n2 + 2
        self.timeFormat = '% ' + str(nt) + '.' + str(n2) + 'f'

    def createAction(self, text, slot=None, shortcut=None, icon=None,
            tip=None, checkable=False, signal="triggered()"):
        """
        Custom wrapper to add and create an action

        From Summerfield 2007
        """
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.svg" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action

###############################################################################
# File menu
###############################################################################

    def importDataSlot(self):
        """
        Import data using the GUI
        """
        fileFilters = ""
        for key, value in common.formats.items():
            fileFilters += ";;" + key
        filterString = fileFilters[2:]

        dialog = QFileDialog(self)
        dialog.setDirectory(os.curdir)
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_():
            files = dialog.selectedFiles()
            fileName  = str(files[0])
            fileFilter = str(dialog.selectedNameFilter())
            try:
                fileType = common.formats[fileFilter]
            except KeyError:
                fileType = None
            self.datasets[fileName] = DataSet(fileName,
                    DataSetType.guess_from_name(fileName))
            self.datasets[fileName].add_datafile(fileName, fileType)

            try:
                self.datasets[fileName].read_data()
            except:
                QMessageBox.critical(self, "I/O Error",
                        "Could not read file " + fileName)
                del self.datasets[fileName]

            self.updateData()
            self.setLimits()
            self.setTimer()
            self.plotFrame()

    def exportFrameSlot(self):
        """
        Exports a data frame in ASCII format or as an image
        """
        filterString = []
        filterString.append("Gnuplot ASCII .dat (*.dat)")
        filterString.append("Portable Network Graphics .png (*.png)")

        dialog = QFileDialog(self)
        dialog.setDirectory(os.curdir)
        dialog.setNameFilters(filterString)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptSave)

        if dialog.exec_():
            files = dialog.selectedFiles()
            fileName = str(files[0])
            extension = dialog.selectedNameFilter()

            if extension == "Gnuplot ASCII .dat (*.dat)":
                frames = {}
                for key, item in self.datasets.items():
                    frames[key] = item.get_frame(self.time)

                L = []
                idx = 0
                for key, item in frames.items():
                    L.append("# Index " + str(idx) + ": " + key + ' @ t = ' +
                            str(item.time) + '\n')
                    L += item.format()
                    L.append("\n\n")
                    idx += 1

                f = open(fileName, "w")
                f.writelines(L[:-1])
                f.close()
            elif extension == "Portable Network Graphics .png (*.png)":
                QWidget.grab(self.plotwidget).save(fileName)

    def hardcopySlot(self):
        """
        Exports all datasets in separated files
        """
        self.pauseSlot()
        timeList = [self.tinit, self.tfinal, self.timestep]
        hardcopy = Hardcopy(timeList)
        hardcopy.exec_()
        startTime = timeList[3]
        endTime = timeList[4]

        if startTime is None and endTime is None:
            return

        dest = QFileDialog.getExistingDirectory(self,
                                    "Choose destination directory", os.curdir)
        if dest:
            frameNumber = int(math.ceil((endTime - startTime) / self.timestep))
            n = len(str(frameNumber))
            t_cur = self.time
            for i in range(frameNumber + 1):
                self.time = startTime + i * self.timestep
                if self.time > endTime:
                    self.time = endTime
                self.plotFrame()
                QWidget.grab(self.plotwidget).save(dest + os.sep
                             + "frame-" + str(i).zfill(n) + ".png")
            self.time = t_cur
            self.plotFrame()

###############################################################################
# Edit menu
###############################################################################

    def dataEditSlot(self):
        """
        Rescale/shift the data
        """
        if len(list(self.datasets.keys())) > 0:
            dataedit = DataEditor(self.datasets, self)
            dataedit.changedPlotData.connect(self.updateDataSlot)
            dataedit.show()
        else:
            QMessageBox.warning(self, "No data loaded",
                "You have to import at least one dataset before you can "
                                "edit data.")

    def resetPlotSlot(self):
        """
        Reset the default zoom level for the plot
        """
        self.plotwidget.resetPlot()

    def reloadDataSlot(self):
        """
        Reloads the data from file
        """
        for dset in self.datasets.values():
            dset.read_data()
        self.updateData()
        self.setLimits()

        old_time = self.time
        self.setTimer()
        self.time = old_time

        self.plotFrame()

    def updateDataSlot(self):
        """
        Transform the data
        """
        self.updateData()
        self.setLimits()
        self.plotFrame()

    def plotSettingsSlot(self):
        """
        Modifies the plot's settings
        """
        pltsettings = PlotSettings(self)
        pltsettings.changedPlotSettings.connect(self.plotwidget.applySettings)
        pltsettings.show()

    def legendEditSlot(self):
        """
        Sets the maximum length of the legend
        """
        length, ok = QInputDialog.getInt(self, "Maximum length of the items " +\
                "in the legend", "Length",
                int(common.settings["Plot/legendTextLength"]), 6, 256, 1)
        if ok and length != int(common.settings["Plot/legendTextLength"]):
            common.settings["Plot/legendTextLength"] = length
            self.plotwidget.resetLegend()

    def FPSEditSlot(self):
        """
        Sets the FPS
        """
        fps, ok = QInputDialog.getDouble(self, "Number of frames per second",
                "FPS", common.settings["Animation/FPS"], 1)
        if ok and fps != common.settings["Animation/FPS"]:
            common.settings["Animation/FPS"] = fps
            self.timer.setInterval(round(1000.0/common.settings["Animation/FPS"]))

###############################################################################
# Play menu
###############################################################################

    def updatePlayMenu(self):
        """
        Re-draw the "play" menu
        """
        self.playMenu.clear()
        if self.timer.isActive():
            self.playMenu.addAction(self.pauseAction)
        else:
            self.playMenu.addAction(self.playAction)

        self.playMenu.addSeparator()

        for action in self.playMenuActions:
            self.playMenu.addAction(action)

    def playSlot(self):
        """
        Start visualizing the data
        """
        self.timer.start()
        self.playAction.setEnabled(False)
        self.playAction.setVisible(False)
        self.pauseAction.setEnabled(True)
        self.pauseAction.setVisible(True)

    def pauseSlot(self):
        """
        Pause the visualization of the data
        """
        self.timer.stop()
        self.playAction.setEnabled(True)
        self.playAction.setVisible(True)
        self.pauseAction.setEnabled(False)
        self.pauseAction.setVisible(False)

    def stepBackwardSlot(self):
        """
        Visualize the previous frame
        """
        if self.iframe > 0:
            self.iframe -= 1
            self.time = self.tinit + self.iframe*self.timestep
            self.plotFrame()

    def stepForwardSlot(self):
        """
        Visualize the next frame
        """
        if self.iframe < self.nframes - 1:
            self.iframe += 1
            self.time = self.tinit + self.iframe*self.timestep
            self.plotFrame()

    def gotoStartSlot(self):
        """
        Go to the first frame
        """
        if self.time != self.tinit:
            self.iframe = 0
            self.time = self.tinit
            self.plotFrame()

    def gotoEndSlot(self):
        """
        Go to the last frame
        """
        if self.time != self.tfinal:
            self.iframe = self.nframes - 1
            self.time = self.tinit + self.iframe*self.timestep
            self.plotFrame()

    def gotoTimeSlot(self):
        """
        Go to a given time
        """
        time, ok = QInputDialog.getDouble(self, "Go to time...",
                "Choose a time in the interval [%g, %g]" % (self.tinit,
                    self.tfinal),
                self.time, self.tinit, self.tfinal, len(str(self.timestep)))
        if ok and self.time != time:
            self.iframe = int(round((time - self.tinit)/self.timestep))
            self.time = self.tinit + self.iframe*self.timestep
            self.plotFrame()

###############################################################################
# Help menu
###############################################################################

    def helpSlot(self):
        """
        Displays the help
        """
        pass

    def aboutSlot(self):
        """
        Displays the credits
        """
        QMessageBox.about(self, "PyGraph",
            "<p>A freely available, lightweight and easy to use visualization "
            "client for viewing 1D data files.</p>"
            "<p>Copyright (c) 2012, 2013, 2014 "
            "Massimiliano Leoni and David Radice</p>"
            "<p>Distributed under the GPLv3 license.</p>")

###############################################################################
# Toolbar
###############################################################################

    def sliderSlot(self, value):
        self.iframe = value
        self.time = self.tinit + self.iframe*self.timestep
        self.plotFrame()

###############################################################################
# Status bar
###############################################################################

    def updateStatusBar(self):
        """
        Updates the status bar message
        """
        self.statusBar().showMessage(common.status)

###############################################################################
# Visualization routines
###############################################################################

    def plotAll(self):
        """
        Show all frames at once
        """
        if not self.plotAllFlag:
            self.plotAllFlag = True
            self.pauseSlot()
            dsets = {}
            for key, item in self.datasets.items():
                dsets[key] = item.data
            self.plotwidget.plotAll(dsets)
        else:
            self.plotAllFlag = False
            self.plotwidget.unPlotAll()

    def unPlotAll(self):
        """
        Don't show all the frames
        """
        if self.plotAllFlag:
            self.plotAllFlag = False
            self.plotwidget.unPlotAll()

    def plotFrame(self):
        """
        Plot the data at the current time
        """
        self.unPlotAll()

        frames = {}
        for key, item in self.datasets.items():
            frames[key] = item.get_frame(self.time)

        self.slider.setValue(self.iframe)

        # Do not update the time stamp, if we have not yet read any data
        try:
            tstring = "t = " + self.timeFormat % self.time
            self.plotwidget.plotFrame(frames, tstring)
        except AttributeError:
            pass

    def timeout(self):
        """
        Update the plot
        """
        if common.settings["Animation/FPS"] >= 25:
            self.iframe += int(common.settings["Animation/FPS"]/25.0)
        else:
            self.iframe += 1
        if(self.iframe > self.nframes):
            self.iframe = self.nframes - 1
            self.time = self.tinit + self.iframe*self.timestep
            self.plotFrame()
            self.pauseSlot()
        else:
            self.time = self.tinit + self.iframe*self.timestep
            self.plotFrame()
