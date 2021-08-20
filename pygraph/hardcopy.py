from PyQt5.QtWidgets import QDialog, QLabel, QPushButton,\
        QGridLayout, QDoubleSpinBox

class Hardcopy(QDialog):
    """
    A dialog to specify hardcopy range
    """
    def __init__(self, timeList, parent=None):
        super(Hardcopy, self).__init__(parent)

        self.timeList = timeList

        minTime = self.timeList[0]
        maxTime = self.timeList[1]
        timestep = self.timeList[2]

        self.setWindowTitle(("Hardcopy"))

        startLabel = QLabel("Starting time")
        self.startDoubleSpinBox = QDoubleSpinBox()
        self.startDoubleSpinBox.setRange(minTime, maxTime)
        self.startDoubleSpinBox.setValue(minTime)
        self.startDoubleSpinBox.setSingleStep(timestep)
        startLabel.setBuddy(self.startDoubleSpinBox)

        endLabel = QLabel("Ending time")
        self.endDoubleSpinBox = QDoubleSpinBox()
        self.endDoubleSpinBox.setRange(minTime, maxTime)
        self.endDoubleSpinBox.setValue(maxTime)
        self.endDoubleSpinBox.setSingleStep(timestep)
        endLabel.setBuddy(self.endDoubleSpinBox)

        okButton = QPushButton("Ok")
        cancelButton = QPushButton("Cancel")

        layout = QGridLayout()
        layout.addWidget(startLabel, 0, 0)
        layout.addWidget(self.startDoubleSpinBox, 0, 1, 1, 2)
        layout.addWidget(endLabel, 1, 0)
        layout.addWidget(self.endDoubleSpinBox, 1, 1, 1, 2)
        layout.addWidget(okButton, 2, 1)
        layout.addWidget(cancelButton, 2, 2)

        self.setLayout(layout)

        okButton.clicked.connect(self.okSlot)
        cancelButton.clicked.connect(self.cancelEvent)

    def okSlot(self):
        """docstring for applySlot"""
        self.timeList.append(self.startDoubleSpinBox.value())
        self.timeList.append(self.endDoubleSpinBox.value())
        self.close()

    def cancelEvent(self):
        """Store the settings"""
        self.timeList.append(None)
        self.timeList.append(None)
        self.close()
