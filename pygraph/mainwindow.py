import os.path

from pygraph.plotwidget import PlotWidget
from pygraph.plotsettings import PlotSettings
import pygraph.resources

import scidata.xgraph as xg
from PyQt4.Qt import SIGNAL, QAction, QIcon, QMainWindow, QSettings,\
        QSize, QPoint, QVariant

class MainWindow(QMainWindow):
    """
    pygraph main window class

    Members
    * datasets   : a dictionary {filename: monodataset} storing working data
    * plotwidget : the plot widget
    * settings   : a dictionary {option: value} storing current settings
    """
    datasets = {}
    plotwidget = None
    settings = {"xMin":0, "xMax":1, "yMin":0, "yMax":1,
                "xAxisTitle":"X Axis", "yAxisTitle":"Y Axis",
               "xMinEnabled":False, "yMinEnabled":False
               }

    def __init__(self, args=None, options=None, parent=None):
        """
        Setup the main window and import all the given files
        """
        super(MainWindow, self).__init__(parent)

        # Read data
        for fname in args:
            self.datasets[os.path.basename(fname)] = xg.parsefile(fname)

        # Restore settings
        qset = QSettings()

        size = qset.value("MainWindow/Size", QVariant(QSize(600,400)))
        self.resize(size.toSize())

        position = qset.value("MainWindow/Position", QVariant(QPoint(0,0)))
        self.move(position.toPoint())

        # Create plot
        self.plotwidget = PlotWidget(self.settings, self)
        self.setCentralWidget(self.plotwidget)

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


    def closeEvent(self, event):
        """
        Store the settings
        """
        qset = QSettings()
        qset.setValue("MainWindow/Size", QVariant(self.size()))
        qset.setValue("MainWindow/Position", QVariant(self.pos()))

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
        pass

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

    def plotSettingsSlot(self):
        """
        Modify the properties of the plot
        """
        PlotSettings(self).exec_()
        self.plotwidget.applySettings(self.settings)

    def helpSlot(self):
        """
        Displays the help
        """
        pass

    def aboutSlot(self):
        """
        Displays the credits
        """
        pass

