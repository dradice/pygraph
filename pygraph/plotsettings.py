from PyQt4.QtGui import *
from PyQt4.QtCore import *

class PlotSettings(QDialog):
    """A dialog to change plotting preferences"""
    def __init__(self, parent=None):
        super(PlotSettings, self).__init__(parent)
        
        xAxisLabel = QLabel("X Axis")
        xMinLabelLine = LabelLine("x Min")
        xMaxLabelLine = LabelLine("x Max")
        xTitleLabelLine = LabelLine("Title")
        xMinGridCheck = QCheckBox("X Axis Minor Grid")

        xAxisLayout = QGridLayout()
        xAxisLayout.addWidget(xAxisLabel, 0, 1)
        xAxisLayout.addWidget(xMinLabelLine, 1, 0, 1, 3)
        xAxisLayout.addWidget(xMaxLabelLine, 2, 0, 1, 3)
        xAxisLayout.addWidget(xTitleLabelLine, 3, 0, 1, 3)
        xAxisLayout.addWidget(xMinGridCheck, 4, 0, 1, 3)
        
        yAxisLabel = QLabel("Y Axis")
        yMinLabelLine = LabelLine("y Min")
        yMaxLabelLine = LabelLine("y Max")
        yTitleLabelLine = LabelLine("Title")
        yMinGridCheck = QCheckBox("Y Axis Minor Grid")

        yAxisLayout = QGridLayout()
        yAxisLayout.addWidget(yAxisLabel, 0, 1)
        yAxisLayout.addWidget(yMinLabelLine, 1, 0, 1, 3)
        yAxisLayout.addWidget(yMaxLabelLine, 2, 0, 1, 3)
        yAxisLayout.addWidget(yTitleLabelLine, 3, 0, 1, 3)
        yAxisLayout.addWidget(yMinGridCheck, 4, 0, 1, 3)

        applyButton = QPushButton("Apply")
        defaultButton = QPushButton("Default")
        closeButton = QPushButton("Close")
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(applyButton)
#        buttonLayout.addWidget(defaultButton)
        buttonLayout.addWidget(closeButton)

        layout = QGridLayout()
        layout.addLayout(xAxisLayout, 0, 0)
        layout.addLayout(yAxisLayout, 0, 1)
        layout.addLayout(buttonLayout, 1, 1)

        self.setLayout(layout)

class LabelLine(QWidget):
    """A class that represents a widget for a label and its line edit
        Label is a string that represents the label's text
        LineEdit is a string that represents the line edit's default text

        for our purpose, the lineedit widget has double length than label widget
    """
    def __init__(self, Label="Label", LineEdit="", parent=None):
        super(LabelLine, self).__init__(parent)
        label = QLabel(Label)
        lineEdit = QLineEdit(LineEdit)
        label.setBuddy(lineEdit)

        layout = QGridLayout()
        layout.addWidget(label, 0, 0)
        layout.addWidget(lineEdit, 0, 1, 1, 2)

        self.setLayout(layout)

