import pygraph.data as data
from pygraph.plotsettings import PlotSettings
import pygraph.resources
from pygraph.player import Player

from PyQt4.Qt import SIGNAL, QAction, QIcon, QMainWindow, QFileDialog,\
        QPoint, QSettings, QString, QSize, QTimer, QVariant, QMessageBox
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
    * index      : a dictionary {filename: idx} storing the frame indices
    * frames     : a dictionary {filename: frame} storing the current frame
    * plotwidget : the plot widget
    * tfinal     : final time
    * time       : current (physical) time
    * timer      : QTimer()
    * timestep   : timestep
    """
    datasets = {}
    indices = {}
    frames = {}
    plotwidget = None
    tfinal = 0
    time = 0
    timer = None
    timestep = sys.float_info.max

    def __init__(self, args=None, options=None, parent=None):
        """
        Setup the main window and import all the given files
        """
        super(MainWindow, self).__init__(parent)

        # Read data
        for fname in args:
            name_re = re.match(r".+\.(\w+)$", fname)
            ext = name_re.group(1)
            if ext == "xg" or ext == "yg":
                self.datasets[fname] = xg.parsefile(fname)
            elif ext == "h5":
                self.datasets[fname] = h5.parse_1D_file(fname)
            elif ext == "asc":
                self.datasets[fname] = asc.parse_1D_file(fname)
            else:
                print("Unknown file extension '" + ext + "'!")
                exit(1)
            self.indices[fname] = 0
            self.frames[fname] = self.datasets[fname].frame(0)

        # Restore settings
        qset = QSettings()

        size = qset.value("MainWindow/Size", QVariant(QSize(600,400)))
        self.resize(size.toSize())

        position = qset.value("MainWindow/Position", QVariant(QPoint(0,0)))
        self.move(position.toPoint())

        data.settings["Plot/xGridEnabled"] = qset.value(
            "Plot/xGridEnabled", QVariant(QString(str(
                data.settings["Plot/xGridEnabled"])))).toString() == 'True'
        data.settings["Plot/yGridEnabled"] = qset.value(
            "Plot/yGridEnabled", QVariant(QString(str(
                data.settings["Plot/yGridEnabled"])))).toString() == 'True'

        # I need the timer to be created before the player is
        self.timer = QTimer()

        # Create plot
        self.player = Player(self)
        self.setCentralWidget(self.player)

        # Actions
        importDataAction = self.createAction("&Import...", self.importDataSlot,
                "Ctrl+I", "document-open", "Import a data file")
        exportDataAction = self.createAction("&Export...", self.exportFrameSlot,
                "Ctrl+S", "document-save-as", "Export the current frame")
        quitAction = self.createAction("&Quit", self.close,
                "Ctrl+Q", "system-log-out", "Close the application")

        dataEditAction = self.createAction("&Data...", self.dataEditSlot,
                "Ctrl+E", None, "Edit the data")
        plotSettingsAction = self.createAction("&Plot...",
                self.plotSettingsSlot, "Ctrl+P", None, "Plot preferences")

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

        # Help menu
        helpMenu = self.menuBar().addMenu("&Help")
        helpMenu.addAction(helpHelpAction)
        helpMenu.addAction(helpAboutAction)

        if(len(self.datasets) > 0):
            self.setLimits()
            self.setTime()
            self.setTimeStep()
            self.plotFrame()

        #self.timer.start()
        self.connect(self.timer, SIGNAL("timeout()"), self.timeout)

    def closeEvent(self, event):
        """
        Store the settings
        """
        qset = QSettings()
        qset.setValue("MainWindow/Size", QVariant(self.size()))
        qset.setValue("MainWindow/Position", QVariant(self.pos()))
        qset.setValue("Plot/xGridEnabled",
                str(data.settings["Plot/xGridEnabled"]))
        qset.setValue("Plot/yGridEnabled",
                str(data.settings["Plot/yGridEnabled"]))

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

            fileType = data.formats[fileFilter]
            if fileType == 'xg':
                self.datasets[fileName] = xg.parsefile(fileName)
            elif fileType == "asc":
                self.datasets[fileName] = asc.parse_1D_file(fileName)
            elif fileType == "h5":
                self.datasets[fileName] = h5.parse_1D_file(fileName)
            self.indices[fileName] = 0
            self.frames[fileName] = self.datasets[fileName].frame(0)

        self.setLimits()
        self.setTime()
        self.setTimeStep()
        self.plotFrame()

    def exportFrameSlot(self):
        """
        Exports a data frame in ASCII format or as an image
        """
        pass

    def dataEditSlot(self):
        """
        Rescale/shift the data
        """
        pass

    def plotFrame(self):
        """
        Plot the data at the current time
        """
        for key, item in self.datasets.iteritems():
            try:
                if item.time[self.indices[key] + 1] >= self.time:
                    self.indices[key] += 1
                    self.frames[key] = item.frame(self.indices[key])
            except IndexError:
                pass
        self.player.plotwidget.plotFrame(self.frames)

    def plotSettingsSlot(self):
        """
        Modifies the plot's settings
        """
        pltsettings = PlotSettings(self)
        self.connect(pltsettings, SIGNAL("changed"),
                self.player.plotwidget.applySettings)
        pltsettings.show()

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

        self.player.plotwidget.applySettings()
        # Reset the zoomer
        self.player.plotwidget.zoomer.setZoomBase(True)

    def setTime(self):
        """
        Initialize time
        """
        self.tfinal = max([data.time[-1] for data in self.datasets.values()])
        self.time = min([data.time[0] for data in self.datasets.values()])

    def setTimeStep(self):
        """
        Computes the optimal timestep
        """
        self.timestep = sys.float_info.max

        for key, item in self.datasets.iteritems():
            dt = [item.time[i] - item.time[i-1] for i in range(1, item.nframes)
                    if item.time[i] - item.time[i-1] > 0]
            if len(dt) > 0:
                self.timestep = min(self.timestep, min(dt))

    def timeout(self):
        """
        Update the plot
        """
        self.time += self.timestep
        if(self.time > self.tfinal):
            self.timer.stop()
        else:
            self.plotFrame()

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

