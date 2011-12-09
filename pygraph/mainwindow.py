from copy import deepcopy
import pygraph.data as data
from pygraph.plotsettings import PlotSettings
from pygraph.plotwidget import PlotWidget
from pygraph.dataeditor import DataEditor, D

import pygraph.resources

from PyQt4.QtCore import Qt
from PyQt4.Qt import SIGNAL, QAction, QFileDialog, QInputDialog, QIcon,\
        QMainWindow, QPoint, QSettings, QSize, QSlider, QString, \
        QTimer, QVariant, QMessageBox
import re
import scidata.carpet.ascii as asc
import scidata.carpet.hdf5 as h5
import scidata.xgraph as xg
import sys
import os

class MainWindow(QMainWindow):
    """
    pygraph main window class

    Members
    * datasets   : a dictionary {filename: monodataset} storing working data
    * plotwidget : the plot widget
    * playAction : the "play" action
    * pauseAction: the "pause" action
    * plotAllFlag: a flag to check wheter plotAll feature is being used or not
    * rawdatasets: a dictionary {filename: monodataset} storing the original
                   data
    * rjustSize  : maximum length of the "time" string
    * tfinal     : final time
    * time       : current (physical) time
    * timer      : QTimer()
    * timestep   : timestep
    * tinit      : initial time
    * transforms : a dictionary {filename: (expr, expr)} storing the
                   transformations
    """
    datasets = {}
    playAction = None
    pauseAction = None
    plotAllFlag = False
    plotwidget = None
    rawdatasets = {}
    tfinal = 0
    time = 0
    timer = None
    timestep = sys.float_info.max
    tinit = 0
    transforms = {}

###############################################################################
# Initialization methods
###############################################################################

    def __init__(self, args=None, options=None, parent=None):
        """
        Setup the main window and import all the given files
        """
        super(MainWindow, self).__init__(parent)

        # Read data
        mergeTarget = None
        for i in range(len(args)):
            if args[i] == '{':
                try:
                    mergeTarget = args[i+1]
                except:
                    print("Unmatched '{' parentesis in command line!")
                    exit(1)
            elif args[i] == '}':
                mergeTarget = None
            else:
                fname = args[i]
                name_re = re.match(r".+\.(\w+)$", fname)
                ext = name_re.group(1)
                if ext == "xg" or ext == "yg":
                    cdataset = xg.parsefile(fname)
                elif ext == "h5":
                    cdataset = h5.parse_1D_file(fname)
                elif ext == "asc":
                    cdataset = asc.parse_1D_file(fname)
                else:
                    print("Unknown file extension '" + ext + "'!")
                    exit(1)

                if mergeTarget == None or mergeTarget == fname:
                    self.rawdatasets[fname] = cdataset
                    self.transforms[fname] = ('x', 'y')
                else:
                    self.rawdatasets[mergeTarget].merge([cdataset])

        if mergeTarget is not None:
            print("Unmatched '{' parentesis in command line!")
            exit(1)

        self.updateData()

        # Restore settings
        qset = QSettings()

        data.settings["Animation/FPS"] = qset.value("Animation/FPS",
                QVariant(data.settings["Animation/FPS"])).toFloat()[0]

        size = qset.value("MainWindow/Size", QVariant(QSize(600,400)))
        self.resize(size.toSize())

        position = qset.value("MainWindow/Position", QVariant(QPoint(0,0)))
        self.move(position.toPoint())

        data.settings["DataEditor/Position"] = qset.value("DataEditor/Position",
                QVariant(data.settings["DataEditor/Position"])).toPoint()
        data.settings["DataEditor/Size"] = qset.value("DataEditor/Size",
                QVariant(data.settings["DataEditor/Size"])).toSize()

        data.settings["Plot/xGridEnabled"] = qset.value(
            "Plot/xGridEnabled", QVariant(QString(str(
                data.settings["Plot/xGridEnabled"])))).toString() == 'True'
        data.settings["Plot/yGridEnabled"] = qset.value(
            "Plot/yGridEnabled", QVariant(QString(str(
                data.settings["Plot/yGridEnabled"])))).toString() == 'True'

        data.settings["PlotSettings/Position"] = qset.value(
                "PlotSettings/Position", QVariant(
                    data.settings["PlotSettings/Position"])).toPoint()
        data.settings["PlotSettings/Size"] = qset.value("PlotSettings/Size",
                QVariant(data.settings["PlotSettings/Size"])).toSize()

        self.timer = QTimer()
        self.timer.setInterval(1000.0/data.settings["Animation/FPS"])

        data.settings["Plot/yLogScale"] = options.logscale

        # Create plot
        self.plotwidget = PlotWidget(self)
        self.setCentralWidget(self.plotwidget)

        # Basic actions
        importDataAction = self.createAction("&Import...", self.importDataSlot,
                "Ctrl+I", "document-open", "Import a data file")
        exportDataAction = self.createAction("&Export...", self.exportFrameSlot,
                "Ctrl+S", "document-save-as", "Export the current frame")
        quitAction = self.createAction("&Quit", self.close,
                "Ctrl+Q", "system-log-out", "Close the application")

        # Edit actions
        dataEditAction = self.createAction("&Data...", self.dataEditSlot,
                "Ctrl+D", None, "Edit the data")
        plotSettingsAction = self.createAction("&Plot...",
                self.plotSettingsSlot, "Ctrl+P", None, "Plot preferences")
        FPSEditAction = self.createAction("&FPS...", self.FPSEditSlot,
                "Ctrl+F", None, "Set the number of frames per second")

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
        fileMenu.addSeparator()
        fileMenu.addAction(quitAction)

        # Edit menu
        editMenu = self.menuBar().addMenu("&Edit")
        editMenu.addAction(dataEditAction)
        editMenu.addAction(plotSettingsAction)
        editMenu.addAction(FPSEditAction)

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
        playToolbar.addAction(gotoStartAction)
        playToolbar.addAction(stepBackwardAction)
        playToolbar.addAction(self.playAction)
        playToolbar.addAction(self.pauseAction)
        playToolbar.addAction(stepForwardAction)
        playToolbar.addAction(gotoEndAction)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setTracking(True)
        self.connect(self.slider, SIGNAL("sliderMoved(int)"), self.sliderSlot)

        playToolbar.addWidget(self.slider)

        self.statusBar()

        if(len(self.datasets) > 0):
            self.setLimits()
            self.setTimer()
            self.plotFrame()

        self.connect(self.timer, SIGNAL("timeout()"), self.timeout)


    def closeEvent(self, event):
        """
        Store the settings
        """
        qset = QSettings()
        qset.setValue("Animation/FPS",
                QVariant(data.settings["Animation/FPS"]))
        qset.setValue("DataEditor/Position",
                QVariant(data.settings["DataEditor/Position"]))
        qset.setValue("DataEditor/Size",
                QVariant(data.settings["DataEditor/Size"]))
        qset.setValue("MainWindow/Size", QVariant(self.size()))
        qset.setValue("MainWindow/Position", QVariant(self.pos()))
        qset.setValue("Plot/xGridEnabled",
                str(data.settings["Plot/xGridEnabled"]))
        qset.setValue("Plot/yGridEnabled",
                str(data.settings["Plot/yGridEnabled"]))
        qset.setValue("PlotSettings/Position",
                QVariant(data.settings["PlotSettings/Position"]))
        qset.setValue("PlotSettings/Size",
                QVariant(data.settings["PlotSettings/Size"]))

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
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def updateData(self):
        """
        Computes the working data from the initial data
        """
        for key, item in self.rawdatasets.iteritems():
            self.datasets[key] = deepcopy(item)
            f = eval('lambda x, y:' + self.transforms[key][0])
            g = eval('lambda x, y:' + self.transforms[key][1])
            self.datasets[key].data_x = f(item.data_x, item.data_y)
            self.datasets[key].data_y = g(item.data_x, item.data_y)

    def setLimits(self):
        """
        Compute the optimial size and location of the axis
        """
        xmin =   sys.float_info.max
        xmax = - sys.float_info.max
        ymin =   sys.float_info.max
        ymax = - sys.float_info.max
        for key, rawdata in self.datasets.iteritems():
            xmin = min(xmin, rawdata.data_x.min())
            xmax = max(xmax, rawdata.data_x.max())
            ymin = min(ymin, rawdata.data_y.min())
            ymax = max(ymax, rawdata.data_y.max())

        size = ymax - ymin

        data.settings['Plot/xMin'] = xmin
        data.settings['Plot/xMax'] = xmax
        data.settings['Plot/yMin'] = ymin - 0.1*size
        data.settings['Plot/yMax'] = ymax + 0.1*size

        self.plotwidget.applySettings()
        self.plotwidget.resetZoomer()

    def setTimer(self):
        """
        Computes initial and final time, as well as the timestep
        """
        # Computes initial and final time
        self.tfinal = max([data.time[-1] for data in self.datasets.values()])
        self.tinit = min([data.time[0] for data in self.datasets.values()])
        self.time = self.tinit

        # Computes timestep
        self.timestep = sys.float_info.max

        for key, item in self.datasets.iteritems():
            dt = [item.time[i] - item.time[i-1] for i in range(1, item.nframes)
                    if item.time[i] - item.time[i-1] > 0]
            if len(dt) > 0:
                self.timestep = min(self.timestep, min(dt))

        # Computes maximum string lenght for the time
        t = self.time
        self.rjustSize = len(str(t))
        while t < self.tfinal:
            t += self.timestep
            self.rjustSize = max(self.rjustSize, len(str(t)))
        self.rjustSize += 1

        self.nframes = int((self.tfinal - self.tinit) / self.timestep)
        self.slider.setRange(0, self.nframes)
        self.slider.setValue(0)

###############################################################################
# File menu
###############################################################################

    def importDataSlot(self):
        """
        Import data using the GUI
        """
        fileFilters = ""
        for key, value in data.formats.iteritems():
            fileFilters += ";;" + key
        filterString = fileFilters[2:]

        dialog = QFileDialog(self)
        dialog.setDirectory(os.curdir)
        dialog.setNameFilter(filterString)
        dialog.selectNameFilter("(*.asc)")
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_():
            files = dialog.selectedFiles()
            fileName  = str(files.first())
            fileFilter = str(dialog.selectedNameFilter())

            try:
                fileType = data.formats[fileFilter]
                if fileType == 'xg':
                    self.rawdatasets[fileName] = xg.parsefile(fileName)
                elif fileType == "asc":
                    self.rawdatasets[fileName] = asc.parse_1D_file(fileName)
                elif fileType == "h5":
                    self.rawdatasets[fileName] = h5.parse_1D_file(fileName)
                self.transforms[fileName] = ('x', 'y')
            except:
                QMessageBox.critical(self, "I/O Error",
                        "Could not read %s" % fileName)

            self.updateData()
            self.setLimits()
            self.setTimer()
            self.plotFrame()

    def exportFrameSlot(self):
        """
        Exports a data frame in ASCII format or as an image
        """
        filterString = "Gnuplot ASCII (*.dat)"

        dialog = QFileDialog(self)
        dialog.setDirectory(os.curdir)
        dialog.setNameFilter(filterString)
        dialog.selectNameFilter("*.dat")
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setConfirmOverwrite(True)

        if dialog.exec_():
            files = dialog.selectedFiles()
            fileName = str(files.first())

            frames = {}
            for key, item in self.datasets.iteritems():
                frames[key] = item.find_frame(self.time)

            L = []
            idx = 0
            for key, item in frames.iteritems():
                L.append("# Index " + str(idx) + ": " + key + ' @ t = ' +
                        str(item.time) + '\n')
                L += item.format()
                L.append("\n\n")
                idx += 1

            f = open(fileName, "w")
            f.writelines(L[:-1])
            f.close()

###############################################################################
# Edit menu
###############################################################################

    def dataEditSlot(self):
        """
        Rescale/shift the data
        """
        if len(self.datasets.keys()) > 0:
            dataedit = DataEditor(self.transforms, self.rawdatasets, self)
            self.connect(dataedit, SIGNAL("changed"), self.updateDataSlot)
            dataedit.show()
        else:
            QMessageBox.warning(self, "No data loaded",
                "You have to import at least one dataset before you can "
                                "edit data.")

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
        self.connect(pltsettings, SIGNAL("changed"),
                self.plotwidget.applySettings)
        pltsettings.show()

    def FPSEditSlot(self):
        """
        Sets the FPS
        """
        fps, ok = QInputDialog.getDouble(self, "Number of frames per second",
                "FPS", data.settings["Animation/FPS"], 1)
        if ok and fps != data.settings["Animation/FPS"]:
            data.settings["Animation/FPS"] = fps
            self.timer.setInterval(1000.0/data.settings["Animation/FPS"])

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
        if self.time - self.timestep >= self.tinit:
            self.time = self.time - self.timestep
            self.plotFrame()

    def stepForwardSlot(self):
        """
        Visualize the next frame
        """
        if self.time + self.timestep <= self.tfinal:
            self.time = self.time + self.timestep
            self.plotFrame()

    def gotoStartSlot(self):
        """
        Go to the first frame
        """
        if self.time != self.tinit:
            self.time = self.tinit
            self.plotFrame()

    def gotoEndSlot(self):
        """
        Go to the last frame
        """
        if self.time != self.tfinal:
            self.time = self.tfinal
            self.plotFrame()

    def gotoTimeSlot(self):
        """
        Go to a given time
        """
        time, ok = QInputDialog.getDouble(self, "Go to time...",
                "Choose a time in the interval [%g, %g]" % (self.tinit,
                    self.tfinal),
                self.time, self.tinit, self.tfinal)
        if ok and self.time != time:
            self.time = time
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
            "<p>Copyright (c) 2011 Massimiliano Leoni and David Radice</p>"
            "<p>Distributed under the GPLv3 license.</p>")

###############################################################################
# Toolbar
###############################################################################

    def sliderSlot(self, value):
        self.time = self.tinit + self.timestep*value
        self.plotFrame()

###############################################################################
# Visualization routines
###############################################################################

    def plotAll(self):
        """
        Toggle the 'show all' feature
        """
        if not self.plotAllFlag:
            self.plotAllFlag = True
            self.pauseSlot()
            self.plotwidget.plotAll(self.datasets)
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
        for key, item in self.datasets.iteritems():
            frames[key] = item.find_frame(self.time)

        self.slider.setValue(int((self.time - self.tinit) / self.timestep))

        tstring = "t = " + str(self.time).rjust(self.rjustSize)
        self.plotwidget.plotFrame(frames, tstring)

    def timeout(self):
        """
        Update the plot
        """
        if data.settings["Animation/FPS"] >= 25:
            self.time += data.settings["Animation/FPS"]/25*self.timestep
        else:
            self.time += self.timestep
        if(self.time > self.tfinal):
            self.pauseSlot()
        else:
            self.plotFrame()
