from PyQt4.QtGui import *
from PyQt4.QtCore import *

from numpy import *


class DataEditor(QDialog):
    """
    A dialog to transform datasets
    """
    dataList = None
    xTransf = None
    yTransf = None
    transforms = None

    xDirty = False
    yDirty = False
    xOldText = ''
    yOldText = ''

    previous = None
    def __init__(self, transforms, rawdatasets, parent=None):
        super(DataEditor, self).__init__(parent)

        self.transforms = transforms

        self.dataList = QListWidget()
        self.dataList.setSelectionMode(QAbstractItemView.SingleSelection)

        items = []
        for key, transf in transforms.iteritems():
            items.append(ListObj(key, transf, rawdatasets[key]))

        for it in items:
            self.dataList.addItem(it)
        self.dataList.setCurrentItem(items[0])

        xLabel = QLabel("x' = ")
        self.xTransf = QLineEdit()
        self.xTransf.setText(self.dataList.currentItem().transf[0])
        xLabel.setBuddy(self.xTransf)

        yLabel = QLabel("y' = ")
        self.yTransf = QLineEdit()
        self.yTransf.setText(self.dataList.currentItem().transf[1])
        yLabel.setBuddy(self.yTransf)

        applyButton = QPushButton("Apply")
        closeButton = QPushButton("Close")

        transfLayout = QGridLayout()
        transfLayout.addWidget(xLabel, 0, 0)
        transfLayout.addWidget(self.xTransf, 0, 1)
        transfLayout.addWidget(yLabel, 1, 0)
        transfLayout.addWidget(self.yTransf, 1, 1)

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
        self.connect(self.dataList,SIGNAL("itemSelectionChanged()"),
                self.selectionChangedSlot)

        self.connect(self.dataList, SIGNAL("currentItemChanged("
            "QListWidgetItem*, QListWidgetItem*)"), self.update_Ui)

    def applyTransf(self):
        """docstring for applyTransf"""
        tnew = {}
        for idx in range(self.dataList.count()):
            dataset = self.dataList.item(idx)
            tnew[dataset.name] = dataset.transf

        self.transforms.update(tnew)

        self.emit(SIGNAL("changed"))

    def xTransfValidate(self):
        """Validate x-axis transformation"""
        try:
            s = 'lambda x,y:' + str(self.xTransf.text())
            f = eval(s)
            i = self.dataList.currentItem()
            p = f(i.data.data_x, i.data.data_y)
            i.transf = (str(self.xTransf.text()), i.transf[1])

            self.xDirty = False
        except:
            QMessageBox.critical(self, "Syntax Error",
                    "Cannot parse the transformation specified for the x-axis")
            self.xTransf.setFocus(Qt.OtherFocusReason)
            self.xTransf.selectAll()

            self.xOldText = str(self.xTransf.text())
            self.yOldText = str(self.yTransf.text())
            self.xDirty = True

    def yTransfValidate(self):
        """Validate y-axis transformation"""
        try:
            s = 'lambda x,y:' + str(self.yTransf.text())
            f = eval(s)
            i = self.dataList.currentItem()
            p = f(i.data.data_x, i.data.data_y)
            i.transf = (i.transf[0], str(self.yTransf.text()))

            self.yDirty = False
        except:
            QMessageBox.critical(self, "Syntax Error",
                    "Cannot parse the transformation specified for the y-axis")
            self.yTransf.setFocus(Qt.OtherFocusReason)
            self.yTransf.selectAll()

            self.xOldText = str(self.xTransf.text())
            self.yOldText = str(self.yTransf.text())
            self.yDirty = True

    def selectionChangedSlot(self):
        """
        Revert the selection if the previous transformations where not correct
        """
        if self.xDirty:
            self.dataList.setCurrentItem(self.previous)
            self.xTransf.setText(self.xOldText)
            self.yTransf.setText(self.yOldText)
            self.xTransf.setFocus(Qt.OtherFocusReason)
            self.xTransf.selectAll()
        if self.yDirty:
            self.dataList.setCurrentItem(self.previous)
            self.xTransf.setText(self.xOldText)
            self.yTransf.setText(self.yOldText)
            self.yTransf.setFocus(Qt.OtherFocusReason)
            self.yTransf.selectAll()

    def update_Ui(self, current, previous):
        """Updates the GUI"""
        self.previous = previous
        self.xTransf.setText(current.transf[0])
        self.yTransf.setText(current.transf[1])

class ListObj(QListWidgetItem):
    """a List Widget equipped with extra infos"""
    def __init__(self, name, transformation, data):
        super(ListObj, self).__init__(name)

        self.name = name
        self.transf = transformation
        self.data = data
