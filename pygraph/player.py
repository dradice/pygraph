from pygraph.plotwidget import PlotWidget

from PyQt4.Qt import * 
from PyQt4.Qwt5 import *
from PyQt4.Qwt5.qplt import *


class Player(QWidget):
    """Central Widget of Main Window"""

    # this is temporary
    FRAME_NUMBER = 1000
    def __init__(self, parent=None):
        super(Player, self).__init__(parent)

        # create a timer, this regulates the frames playing
        self.timer = QTimer()

        self.plotwidget = PlotWidget()

        # create the buttons that will be in the dialog
        self.startButton = QPushButton("Start")
        self.pauseButton = QPushButton("Pause")
        self.stopButton = QPushButton("Stop")
        self.exitButton = QPushButton("Exit")
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, self.FRAME_NUMBER)
        self.slider.setValue(0)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.startButton)
        buttonLayout.addWidget(self.pauseButton)
        buttonLayout.addWidget(self.slider)
        buttonLayout.addWidget(self.stopButton)
        buttonLayout.addWidget(self.exitButton)

        # create Signals&Slots (who, when, what)
        self.connect(self.startButton, SIGNAL("clicked()"), self.startPressed)
        self.connect(self.pauseButton, SIGNAL("clicked()"), self.pausePressed)
        self.connect(self.stopButton, SIGNAL("clicked()"), self.stopPressed)
        self.connect(self.exitButton, SIGNAL("clicked()"), self.exitPressed)
       
        layout = QVBoxLayout()
        layout.addWidget(self.plotwidget)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

        QObject.connect(self.timer, SIGNAL("timeout()"), self.timeout)


    # timeout is executed each time timer emits "timeout()"
    def timeout(self):
        pass


    def startPressed(self):
        """docstring for startPressed"""
        pass    


    def pausePressed(self):
        """docstring for pausePressed"""
        pass


    def stopPressed(self):
        """docstring for stopPressed"""
        pass


    def exitPressed(self):
        """docstring for exitPressed"""
        pass
