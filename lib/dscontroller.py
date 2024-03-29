import sys, os
import configobj
from lib.datasource import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *



__author__ = 'aco-nav'

class DataSourceController(QWidget):
    def __init__(self,parent=0):
        super(DataSourceController, self).__init__(parent)
        self.parent = parent
        ds =  [dsc(parent=parent) for dsc in datasource.DataSource.__subclasses__()]

        self._datasource = {}
        self.pluginparamlayout = QVBoxLayout()
        self.container = QVBoxLayout()
        self.dscheckbox = QComboBox()
        self.paramgb = QGroupBox("Prediction Parameters:")
        self.paramgb.setLayout(self.pluginparamlayout)
        self.dscheckbox.currentIndexChanged[str].connect(self.dscheckbox_changed)

        for dso in ds:
            self._datasource[dso.name] = dso
            self.dscheckbox.addItem(dso.name)
            self.parent.importerlayout.addWidget(dso.importer)

        self.container.addWidget(self.dscheckbox)
        self.setLayout(self.container)
    def clearplot(self):
        for v in self.getmember.values():
            v.clearplot()

    @pyqtSlot(str)
    def dscheckbox_changed(self,label):
        for i in reversed(range(self.pluginparamlayout.count())):
            self.pluginparamlayout.takeAt(i).widget().setParent(None)
        self.pluginparamlayout.addWidget(self._datasource[str(label)].optionparam)


    @property
    def getmember(self):
        return self._datasource
    @property
    def selected(self):
        sel = self.dscheckbox.currentText()
        return self._datasource[str(sel)]


