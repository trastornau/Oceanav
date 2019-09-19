import  os, sys
from subprocess import *
from lib.datasource.datasource import DataSource
from threading import  Thread, Event
import re
from lib.pytidalyse import Tidalyse
import numpy as np
from PyQt4.QtGui import QFileDialog

class UltraTide(DataSource):
    id="ULTRATIDE"
    name = "Ultra Tide File"
    desc = "Tide Generated from VERIPOS"
    version = "1.0"
    sourcetype = "FILE"
    params = {'depth': 8,
              'scale': 1,
              'orientation': 90,
              'days to predict': 7,
              'vessel speed': 4.5,
              'streamer': 0.0
              }
    def __init__(self,parent=None):
        DataSource.__init__(self,parent)
        self.data = None

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
                "Select Ultra Tide Generated File",
                ".",
                "All Files (*);;Text Files (*.txt);;Ultra Tide File (*.ultra)", options)
        if ultratidefile:
            self.datasource  = os.path.normpath(str(ultratidefile))
            thread = Thread(target=self.processdata)
            thread.start()
    def predict(self):
        pass
    def processdata(self):
        print self.datasource
