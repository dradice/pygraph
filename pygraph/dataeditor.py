from PyQt4.QtGui import QDialog, QListWidgetItem, QListWidget, \
                        QAbstractItemView, QLabel, QLineEdit, \
                        QToolButton, QIcon, QPushButton, \
                        QHBoxLayout, QGridLayout, QMessageBox
from PyQt4.QtCore import QString, SIGNAL
from numpy import *

import pygraph.database as data

def D(x):
    q = diff(x)
    return array([q[0]] + list(q))

class DataEditor(QDialog):
    """
    A dialog to transform datasets
    """

    def __init__(self, transforms, rawdatasets, parent=None):
        super(DataEditor, self).__init__(parent)

        self.dataList = None
        self.xTransf = None
        self.yTransf = None
        self.transforms = None

        self.xOldText = ''
        self.yOldText = ''
        self.clean = []
        self.previous = None

        self.setWindowTitle(QString("Data Editor"))
        self.resize(data.settings["DataEditor/Size"])
        self.move(data.settings["DataEditor/Position"])

        self.transforms = transforms

        self.dataList = QListWidget()
        self.dataList.setSelectionMode(QAbstractItemView.SingleSelection)

        items = []
        for key, transf in transforms.iteritems():
            items.append(ListObj(key, transf, rawdatasets[key]))

        for it in items:
            self.dataList.addItem(it)
            self.clean += 2 * [1]
        self.dataList.setCurrentItem(items[0])

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

        self.connect(applyButton, SIGNAL("clicked()"), self.applyTransf)
        self.connect(closeButton, SIGNAL("clicked()"), self.close)

        self.connect(self.xTransf, SIGNAL("editingFinished()"),
                self.xTransfValidate)
        self.connect(self.yTransf, SIGNAL("editingFinished()"),
                self.yTransfValidate)
        self.connect(self.xCheck, SIGNAL("clicked()"), self.ParsingError)
        self.connect(self.yCheck, SIGNAL("clicked()"), self.ParsingError)

        self.connect(self.dataList, SIGNAL("currentItemChanged("
            "QListWidgetItem*, QListWidgetItem*)"), self.update_Ui)

    def applyTransf(self):
        """docstring for applyTransf"""
        if all(self.clean):
            tnew = {}
            for idx in range(self.dataList.count()):
                dataset = self.dataList.item(idx)
                tnew[dataset.name] = dataset.transf

            self.transforms.update(tnew)

            self.emit(SIGNAL("changed"))
        else:
            QMessageBox.critical(self, "Parsing Errors",
                              "There were parsing errors reading the "
                              "transformations you specified. \n\n"
                              "Please check for typing errors and retry.")

    def xTransfValidate(self):
        """Validate x-axis transformation"""
        i = self.dataList.currentItem()
        row = self.dataList.currentRow()
        expr = str(self.xTransf.text())

        if 'x' not in expr:
            expr += " + 0*x"

        try:
            s = 'lambda x,y,t:' + expr
            f = eval(s)
            p = f(i.data.data_x, i.data.data_y, 0)
            i.transf = (expr, i.transf[1])
            self.xCheck.setVisible(False)
            self.clean[row] = 1
        except:
            self.xCheck.setVisible(True)
            i.transf = (expr, i.transf[1])
            self.clean[row] = 0

    def yTransfValidate(self):
        """Validate y-axis transformation"""
        i = self.dataList.currentItem()
        row = self.dataList.currentRow()
        expr = str(self.yTransf.text())

        if 'y' not in expr:
            expr += " + 0*y"

        try:
            s = 'lambda x,y,t:' + expr
            f = eval(s)
            p = f(i.data.data_x, i.data.data_y, 0)
            i.transf = (i.transf[0], expr)
            self.yCheck.setVisible(False)
            self.clean[row + 1] = 1
        except:
            self.yCheck.setVisible(True)
            i.transf = (i.transf[0], expr)
            self.clean[row + 1] = 0

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
        data.settings.update({"DataEditor/Position": self.pos()})
        data.settings.update({"DataEditor/Size": self.size()})

class ListObj(QListWidgetItem):
    """a List Widget equipped with extra infos"""
    def __init__(self, name, transformation, data):
        super(ListObj, self).__init__(name)

        self.name = name
        self.transf = transformation
        self.data = data
