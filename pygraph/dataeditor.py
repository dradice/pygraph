from copy import deepcopy
from PyQt5.QtWidgets import QDialog, QListWidgetItem, QListWidget, \
                        QAbstractItemView, QLabel, QLineEdit, \
                        QToolButton, QPushButton, \
                        QHBoxLayout, QGridLayout, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal
from numpy import *

import pygraph.common as common
from pygraph.datasets import D

class DataEditor(QDialog):
    """
    A dialog to transform datasets
    """

    changedPlotData = pyqtSignal()

    def __init__(self, datasets, parent=None):
        super(DataEditor, self).__init__(parent)

        self.dataList = None
        self.xTransf  = None
        self.yTransf  = None

        self.xOldText = ''
        self.yOldText = ''
        # Flags invalid transformations
        self.clean    = []
        self.previous = None

        self.setWindowTitle(("Data Editor"))
        self.resize(common.settings["DataEditor/Size"])
        self.move(common.settings["DataEditor/Position"])

        self.datasets = datasets

        # Local copy of the transfomations
        self.dataList = QListWidget()
        self.dataList.setSelectionMode(QAbstractItemView.SingleSelection)

        for key, dset in datasets.items():
            self.dataList.addItem(ListObj(key, deepcopy(dset.transform)))
            self.clean += 2 * [True]
        self.dataList.setCurrentItem(self.dataList.item(0))

        xLabel = QLabel("x' = ")
        self.xTransf = QLineEdit()
        self.xCheck = QToolButton()
        self.xCheck.setVisible(False)
        self.xCheck.setIcon(QIcon(":/dialog-error.svg"))
        self.xTransf.setText(self.dataList.currentItem().transf[0])
        xLabel.setBuddy(self.xTransf)

        yLabel = QLabel("y' = ")
        self.yTransf = QLineEdit()
        self.yCheck = QToolButton()
        self.yCheck.setVisible(False)
        self.yCheck.setIcon(QIcon(":/dialog-error.svg"))
        self.yTransf.setText(self.dataList.currentItem().transf[1])
        yLabel.setBuddy(self.yTransf)

        applyButton = QPushButton("Apply")
        closeButton = QPushButton("Close")

        lineXLayout = QHBoxLayout()
        lineXLayout.addWidget(self.xTransf)
        lineXLayout.addWidget(self.xCheck)

        lineYLayout = QHBoxLayout()
        lineYLayout.addWidget(self.yTransf)
        lineYLayout.addWidget(self.yCheck)

        transfLayout = QGridLayout()
        transfLayout.addWidget(xLabel, 0, 0)
        transfLayout.addLayout(lineXLayout, 0, 1)
        transfLayout.addWidget(yLabel, 1, 0)
        transfLayout.addLayout(lineYLayout, 1, 1)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(applyButton)
        buttonLayout.addWidget(closeButton)

        layout = QGridLayout()
        layout.addWidget(self.dataList, 0, 0, 3, 1)
        layout.addLayout(transfLayout, 1, 1)
        layout.addLayout(buttonLayout, 3, 1)

        self.setLayout(layout)

        applyButton.clicked.connect(self.applyTransf)
        closeButton.clicked.connect(self.close)

        self.xTransf.editingFinished.connect(self.xTransfValidate)
        self.yTransf.editingFinished.connect(self.yTransfValidate)
        self.xCheck.clicked.connect(self.ParsingError)
        self.yCheck.clicked.connect(self.ParsingError)

        self.dataList.currentItemChanged.connect(self.update_Ui)

    def applyTransf(self):
        """docstring for applyTransf"""
        self.xTransfValidate()
        self.yTransfValidate()
        if all(self.clean):
            for idx in range(self.dataList.count()):
                item = self.dataList.item(idx)
                self.datasets[item.name].transform = item.transf

            self.changedPlotData.emit()
        else:
            QMessageBox.critical(self, "Parsing Errors",
                              "There were parsing errors reading the "
                              "transformations you specified. \n\n"
                              "Please check for typing errors and retry.")

    def xTransfValidate(self):
        """Validate x-axis transformation"""
        item = self.dataList.currentItem()
        row  = self.dataList.currentRow()
        expr = str(self.xTransf.text())
        dset = self.datasets[item.name].data

        if 'x' not in expr:
            expr += " + 0*x"

        try:
            s = 'lambda x,y,t:' + expr
            f = eval(s)
            p = f(dset.data_x, dset.data_y, 0)
            item.transf = (expr, item.transf[1])
            self.xCheck.setVisible(False)
            self.clean[row] = True
        except:
            self.xCheck.setVisible(True)
            item.transf = (expr, item.transf[1])
            self.clean[row] = False

    def yTransfValidate(self):
        """Validate y-axis transformation"""
        item = self.dataList.currentItem()
        row  = self.dataList.currentRow()
        expr = str(self.yTransf.text())
        dset = self.datasets[item.name].data

        if 'y' not in expr:
            expr += " + 0*y"

        try:
            s = 'lambda x,y,t:' + expr
            f = eval(s)
            p = f(dset.data_x, dset.data_y, 0)
            item.transf = (item.transf[0], expr)
            self.yCheck.setVisible(False)
            self.clean[row + 1] = True
        except:
            self.yCheck.setVisible(True)
            item.transf = (item.transf[0], expr)
            self.clean[row + 1] = False

    def ParsingError(self):
        """docstring for ParsingError"""
        QMessageBox.critical(self, "Parsing Error",
                             "This line could not be read and might contain "
                             "typing errors.")

    def update_Ui(self, current, previous):
        """Updates the GUI"""
        self.previous = previous
        self.xTransf.setText(current.transf[0])
        self.yTransf.setText(current.transf[1])
        self.xTransfValidate()
        self.yTransfValidate()

    def closeEvent(self, event):
        """Store the settings"""
        common.settings.update({"DataEditor/Position": self.pos()})
        common.settings.update({"DataEditor/Size": self.size()})

class ListObj(QListWidgetItem):
    """a List Widget equipped with extra infos"""
    def __init__(self, name, transf):
        super(ListObj, self).__init__(name)

        self.name   = name
        self.transf = transf
