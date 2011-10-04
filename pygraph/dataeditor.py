from PyQt4.QtGui import *
from PyQt4.QtCore import *

from numpy import *


class DataEditor(QDialog):
    """
    A dialog to transform datasets
    """
    def __init__(self, datasets, parent=None):
        super(DataEditor, self).__init__(parent)
        
        self.dataList = QListWidget()

        self.datasets = datasets

        for name, data in self.datasets.iteritems():
            self.dataList.addItem(ListObj(name, data))
            print "in for"
            print id(data.data_y)
        
        xLabel = QLabel("X data transformation")
        self.xTransf = QLineEdit()
        xLabel.setBuddy(self.xTransf)
        self.xTransf.setPlaceholderText("NumPy Expression")

        yLabel = QLabel("Y data transformation")
        self.yTransf = QLineEdit()
        yLabel.setBuddy(self.yTransf)
        self.yTransf.setPlaceholderText("NumPy Expression")

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

        self.connect(self.dataList,SIGNAL("currentItemChanged(QListWidgetItem*,"
                                          +"QListWidgetItem*)"), self.update_Ui)

        
    def applyTransf(self):
        """docstring for applyTransf"""
        for index in xrange(self.dataList.count()):
            dataset = self.dataList.item(index)
            if self.xTransf.text() != "":
                dataset.x = eval(str(self.xTransf.text()).replace("x", "dataset.x"))
            if self.yTransf.text() != "":
                print "in applytransf"
                print dataset.y
                print id(dataset.y)
                print type(dataset.y)
                #XXX: problem: the following instruction creates a new variable
                # instead of modifying the one that was referenced so far!
                dataset.dataset.data_y = eval(str(self.yTransf.text()).replace("y",
                                                      "dataset.y"))
                print id(dataset.y)
                print type(dataset.y)
                print dataset.dataset.data_y


#        self.xTransf.setText("")
#        self.yTransf.setText("")

        self.emit(SIGNAL("changed"))


    def update_Ui(self, current, previous):
        """updates the gui keeping memory"""
        if current == None or previous == None:
            return

        previous.xTransf = self.xTransf.text()
        previous.yTransf = self.yTransf.text()

        self.xTransf.setText(current.xTransf)
        self.yTransf.setText(current.yTransf)

 
class ListObj(QListWidgetItem):
    """a List Widget equipped with extra infos"""
    def __init__(self, name, data):
        super(ListObj, self).__init__(name)

        self.xTransf = ""
        self.yTransf = ""

        self.dataset = data
        self.x = data.data_x
        self.y = data.data_y

        print "in ListObj"
        print id(data.data_y)
        print id(self.y)



        
