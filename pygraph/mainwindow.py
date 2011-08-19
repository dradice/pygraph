from pygraph.plotwidget import PlotWidget
from PyQt4.Qt import QMainWindow, QSettings, QSize, QPoint, QVariant
import scidata.xgraph as xg
import os.path

class MainWindow(QMainWindow):
    """
    pygraph main window class

    Members
    * datasets   : a dictionary {filename: monodataset} storing the working data
    * plotwidget : the plot widget
    * settings   : a dictionary {option: value} storing the current setttings
    """
    datasets = {}
    plotwidget = None
    settings = {}

    def __init__(self, args=None, options=None, parent=None):
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
        self.plotwidget = PlotWidget(self)
        self.setCentralWidget(self.plotwidget)

    def closeEvent(self, event):
        qset = QSettings()
        qset.setValue("MainWindow/Size", QVariant(self.size()))
        qset.setValue("MainWindow/Position", QVariant(self.pos()))
