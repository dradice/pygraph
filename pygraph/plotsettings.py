from PyQt4.QtGui import *
from PyQt4.QtCore import *

class PlotSettings(QDialog):
    """A dialog to change plotting preferences"""
    def __init__(self, parent=None):
        super(PlotSettings, self).__init__(parent)
        self.parent = parent
        currentSettings = self.parent.settings
        
        xAxisLabel = QLabel("X Axis")
        self.xMinLabelLine = LabelLine("Min", currentSettings["xMin"])
        self.xMaxLabelLine = LabelLine("Max", currentSettings["xMax"])
        self.xTitleLabelLine = LabelLine("Title", currentSettings["xAxisTitle"])
        self.xMinGridCheck = QCheckBox("X Axis Minor Grid")
        self.xMinGridCheck.setChecked(currentSettings["xMinEnabled"])

        xAxisLayout = QGridLayout()
        xAxisLayout.addWidget(xAxisLabel, 0, 1)
        xAxisLayout.addWidget(self.xMinLabelLine, 1, 0, 1, 3)
        xAxisLayout.addWidget(self.xMaxLabelLine, 2, 0, 1, 3)
        xAxisLayout.addWidget(self.xTitleLabelLine, 3, 0, 1, 3)
        xAxisLayout.addWidget(self.xMinGridCheck, 4, 0, 1, 3)
        
        yAxisLabel = QLabel("Y Axis")
        self.yMinLabelLine = LabelLine("Min", currentSettings["yMin"])
        self.yMaxLabelLine = LabelLine("Max", currentSettings["yMax"])
        self.yTitleLabelLine = LabelLine("Title", currentSettings["yAxisTitle"])
        self.yMinGridCheck = QCheckBox("Y Axis Minor Grid")
        self.yMinGridCheck.setChecked(currentSettings["yMinEnabled"])

        yAxisLayout = QGridLayout()
        yAxisLayout.addWidget(yAxisLabel, 0, 1)
        yAxisLayout.addWidget(self.yMinLabelLine, 1, 0, 1, 3)
        yAxisLayout.addWidget(self.yMaxLabelLine, 2, 0, 1, 3)
        yAxisLayout.addWidget(self.yTitleLabelLine, 3, 0, 1, 3)
        yAxisLayout.addWidget(self.yMinGridCheck, 4, 0, 1, 3)
        
        applyButton = QPushButton("Apply")
        closeButton = QPushButton("Close")
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(applyButton)
        buttonLayout.addWidget(closeButton)

        layout = QGridLayout()
        layout.addLayout(xAxisLayout, 0, 0)
        layout.addLayout(yAxisLayout, 0, 1)
        layout.addLayout(buttonLayout, 1, 1)

        self.setLayout(layout)
     
        self.connect(applyButton, SIGNAL("clicked()"), self.returnSettings)
        self.connect(closeButton, SIGNAL("clicked()"), self.close)


    def returnSettings(self):
        """returns settings dictionary to be applied to the plot"""
        try:
            settings = {
                "xMin":float(
                    self.xMinLabelLine.lineEdit.text().replace(",",".")),
                "xMax":float(
                    self.xMaxLabelLine.lineEdit.text().replace(",",".")),
                "yMin":float(
                    self.yMinLabelLine.lineEdit.text().replace(",",".")),
                "yMax":float(
                    self.yMaxLabelLine.lineEdit.text().replace(",",".")),
                "xAxisTitle":unicode(self.xTitleLabelLine.lineEdit.text()),
                "yAxisTitle":unicode(self.yTitleLabelLine.lineEdit.text()),
                "xMinEnabled":self.xMinGridCheck.isChecked(),
                "yMinEnabled":self.yMinGridCheck.isChecked()
                  }
            self.parent.settings = settings.copy()
        except ValueError:
            QMessageBox.critical(self, "Value Error",
                               "There were some errors reading "
                               "the data you specified.\n"
                               "Please check typos and try again."
                                )
        self.close()

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

