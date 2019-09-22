import  os, sys
from subprocess import *
from lib.datasource.datasource import DataSource
from threading import  Thread, Event
import re
from lib.pytidalyse import Tidalyse
import numpy as np
from lib import  constant as const
from PyQt4.QtGui import QFileDialog, QPushButton

class UltraTide(DataSource):
    id="TRINAVTIDE"
    name = "Trinav Tide"
    desc = "Tide Generated From Trinav Prediction"
    version = "1.0"
    datapath = "./data/TrinavTide"
    sourcetype = "FILE"
    bypassdialog = False
    params = const.defaultparams
    def __init__(self,parent=None):
        DataSource.__init__(self,parent)
        self.plottide = QPushButton("Plot TRINAV Tide")
        self.plottide.clicked.connect(self.plotdata)
        self.predictionlayout.addRow(self.plottide)
        self.data = None
    def plotdata(self):
        if not os.path.isfile(self.datasource):
            self.importData()

        self.processdata()
        row, col = self.data.shape
        tide = self.data[:,0]
        xax  = self.data[:,1]+self.datehandler.npdiff.total_seconds()
        self.datasourceplot[self.name] = self.tideplot.plot(xax, tide, pen=(255,128,32))
        self.tideplot.autoRange()
    def asNumpyArray(self):
        tmpdict = {}
        tmparr = []
        for key in sorted(self._data.iterkeys()):
            tmpdict[key] = self._data[key]
        for key, val in tmpdict.items():
            # print val
            curr = []
            curr.append(tmpdict[key][2])
            curr.extend(val)
            tmparr.append(curr)
        print tmparr
        return np.array(tmparr, dtype=float)
    def importData(self):
        options = None# QFileDialog.Options()
        ultratidefile = QFileDialog.getOpenFileName(self,
                "Select Trinav generated Tide File",
                self.datapath,
                "All Files (*);;Text Files (*.txt);;Trinav generatued Tide file (*.tide)", options)
        if ultratidefile:
            self.datasource  = os.path.normpath(str(ultratidefile))
            thread = Thread(target=self.processdata)
            thread.start()
    def predict(self):
        pass
    def processdata(self):
        self.raw = np.loadtxt(self.datasource, usecols=(3,4))
        self.data=self.raw[np.argsort(self.raw[:,1])]  # Sort data by epoch before processing
    def predict(self):
        if not os.path.isfile(self.datasource):
            self.importData()

        self.processdata()
        row, col = self.data.shape

        self.data[:,[0,1]] = self.data[:,[1,0]]
     
        tide = self.data[:,1]
        xax  = self.data[:,0] + self.datehandler.npdiff.total_seconds()
        xmagdata =np.stack((xax, tide), axis=-1)
        tf = Tidalyse(xmagdata=xmagdata)
        tf = Tidalyse(xmagdata=xmagdata)
        tf.scale = self.params['scale']
        tf.days = self.params['days to predict']
        tf.vesselspeed = self.params['vessel speed']
        tf.shift = self.getshift()
        tf.recompute(True)
        self.predictionplot[self.name] = self.predplot.plot(tf.feather, pen=(255,32,32))
        self.predplot.autoRange()

        
