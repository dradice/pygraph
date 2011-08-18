from PyQt4.Qt import QMainWindow
import scidata.xgraph as xg
import os.path

class MainWindow(QMainWindow):
    """
    pygraph main window class

    Members
    * datasets : a dictionary {filename: monodataset} storing the working data
    * settings : a dictionary {option: value} storing the current setttings
    """
    datasets = {}
    settings = {}

    def __init__(self, args=None, options=None, parent=None):
        super(MainWindow, self).__init__(parent)

        for fname in args:
            self.datasets[os.path.basename(fname)] = xg.parsefile(fname)
