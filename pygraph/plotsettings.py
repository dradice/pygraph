from PyQt4.QtGui import *
from PyQt4.QtCore import *

from pygraph.data import settings

class PlotSettings(QDialog):
    """A dialog to change plotting preferences"""
    def __init__(self, parent=None):
        super(PlotSettings, self).__init__(parent)
        self.parent = parent
        currentSettings = settings.copy()

        xAxisLabel = QLabel("X Axis")
        self.xMinLabelLine = LabelLine("Min", currentSettings["Plot/xMin"])
        self.xMaxLabelLine = LabelLine("Max", currentSettings["Plot/xMax"])
        self.xTitleLabelLine = LabelLine("Title",
                currentSettings["Plot/xAxisTitle"])
        self.xLogScale = QCheckBox("Log Scale")
        self.xLogScale.setChecked(currentSettings["Plot/xLogScale"])
        self.xGridCheck = QCheckBox("Grid")
        self.xGridCheck.setChecked(currentSettings["Plot/xGridEnabled"])

        xAxisLayout = QGridLayout()
        xAxisLayout.addWidget(xAxisLabel, 0, 1)
        xAxisLayout.addWidget(self.xMinLabelLine, 1, 0, 1, 3)
        xAxisLayout.addWidget(self.xMaxLabelLine, 2, 0, 1, 3)
        xAxisLayout.addWidget(self.xTitleLabelLine, 3, 0, 1, 3)
        xAxisLayout.addWidget(self.xLogScale, 4, 0, 1, 3)
        xAxisLayout.addWidget(self.xGridCheck, 5, 0, 1, 3)

        yAxisLabel = QLabel("Y Axis")
        self.yMinLabelLine = LabelLine("Min", currentSettings["Plot/yMin"])
        self.yMaxLabelLine = LabelLine("Max", currentSettings["Plot/yMax"])
        self.yTitleLabelLine = LabelLine("Title",
                currentSettings["Plot/yAxisTitle"])
        self.yLogScale = QCheckBox("Log Scale")
        self.yLogScale.setChecked(currentSettings["Plot/xLogScale"])
        self.yGridCheck = QCheckBox("Grid")
        self.yGridCheck.setChecked(currentSettings["Plot/yGridEnabled"])

        yAxisLayout = QGridLayout()
        yAxisLayout.addWidget(yAxisLabel, 0, 1)
        yAxisLayout.addWidget(self.yMinLabelLine, 1, 0, 1, 3)
        yAxisLayout.addWidget(self.yMaxLabelLine, 2, 0, 1, 3)
        yAxisLayout.addWidget(self.yTitleLabelLine, 3, 0, 1, 3)
        yAxisLayout.addWidget(self.yLogScale, 4, 0, 1, 3)
        yAxisLayout.addWidget(self.yGridCheck, 5, 0, 1, 3)

        applyButton = QPushButton("Apply")
        closeButton = QPushButton("Close")

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(applyButton)
        buttonLayout.addWidget(closeButton)

        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        lineLayout = QVBoxLayout()
        lineLayout.addWidget(line)

        layout = QGridLayout()
        layout.addLayout(xAxisLayout, 0, 0)
        layout.addLayout(lineLayout, 0, 1)
        layout.addLayout(yAxisLayout, 0, 2)
        layout.addLayout(buttonLayout, 1, 2)

        self.setLayout(layout)

        self.connect(applyButton, SIGNAL("clicked()"), self.returnSettings)
        self.connect(closeButton, SIGNAL("clicked()"), self.close)


    def returnSettings(self):
        """returns settings dictionary to be applied to the plot"""
        try:
            plotSettings = {
                "Plot/xMin":float(
                    self.xMinLabelLine.lineEdit.text().replace(",",".")),
                "Plot/xMax":float(
                    self.xMaxLabelLine.lineEdit.text().replace(",",".")),
                "Plot/xLogScale":self.xLogScale.isChecked(),
                "Plot/xGridEnabled":self.xGridCheck.isChecked(),
                "Plot/yMin":float(
                    self.yMinLabelLine.lineEdit.text().replace(",",".")),
                "Plot/yMax":float(
                    self.yMaxLabelLine.lineEdit.text().replace(",",".")),
                "Plot/xAxisTitle":unicode(self.xTitleLabelLine.lineEdit.text()),
                "Plot/yAxisTitle":unicode(self.yTitleLabelLine.lineEdit.text()),
                "Plot/yLogScale":self.yLogScale.isChecked(),
                "Plot/yGridEnabled":self.yGridCheck.isChecked()
                  }
            settings.update(plotSettings)
            self.emit(SIGNAL("changed"))
        except ValueError:
            QMessageBox.critical(self, "Value Error",
                               "There were some errors reading "
                               "the data you specified.\n"
                               "Please check typos and try again."
                                )

class LabelLine(QWidget):
    """A class that represents a widget for a label and its line edit
        Label is a string that represents the label's text
        LineEdit is a string that represents the line edit's default text

        for our purpose, lineedit widget has double length than label widget
    """
    def __init__(self, Label="Label", LineEdit="", parent=None):
        super(LabelLine, self).__init__(parent)
        label = QLabel(Label)
        self.lineEdit = QLineEdit(str(LineEdit))
        label.setBuddy(self.lineEdit)

        layout = QGridLayout()
        layout.addWidget(label, 0, 0)
        layout.addWidget(self.lineEdit, 0, 1, 1, 2)

        self.setLayout(layout)

