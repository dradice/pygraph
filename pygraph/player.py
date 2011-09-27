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

        self.timer = parent.timer

        self.plotwidget = PlotWidget(self)

        # create the buttons that will be in the dialog
        self.startButton = QPushButton(QIcon("media-playback-start"),"Start")
        self.pauseButton = QPushButton(QIcon("media-playback-pause"),"Pause")
        self.stopButton = QPushButton(QIcon("media-playback-stop"),"Stop")
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, self.FRAME_NUMBER)
        self.slider.setValue(0)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.startButton)
        buttonLayout.addWidget(self.pauseButton)
        buttonLayout.addWidget(self.slider)
        buttonLayout.addWidget(self.stopButton)

        # create Signals&Slots (who, when, what)
        self.connect(self.startButton, SIGNAL("clicked()"), self.startPressed)
        self.connect(self.pauseButton, SIGNAL("clicked()"), self.pausePressed)
        self.connect(self.stopButton, SIGNAL("clicked()"), self.stopPressed)
       
        layout = QVBoxLayout()
        layout.addWidget(self.plotwidget)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)


    def startPressed(self):
        self.timer.start()
        pass    


    def pausePressed(self):
        """docstring for pausePressed"""
        pass


    def stopPressed(self):
        self.timer.stop()
        pass

