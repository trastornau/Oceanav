import  os, sys
from subprocess import *
from PyQt4.Qt import *
from lib.datasource.datasource import DataSource
from threading import  Thread, Event
import re
from lib.pytidalyse import Tidalyse

import numpy as np

class FeatherDB(DataSource):
    id="FEATHER"
    name = "Feather From TRINAV (Unimplemented)"
    desc = "Feather Dumped data Processor"
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
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,"Select TRINAV Exported Feather folder..",options=options)
        if directory:
            self.datasource  = os.path.normpath(str(directory))
            thread = Thread(target=self.processdata)
            thread.start()
    def predict(self):
        self.raw = np.array(np.loadtxt(os.path.join(self.path, 'DB.{}'.format(self.id)), delimiter=','))
        self.data = self.raw[np.argsort(self.raw[:, 0])]  # Sort data by epoch before processing

        plots={}
        feat={}
        mag = np.asarray(self.data[:,6],dtype=float)
        xmag = mag * np.sin(np.radians((180 - self.params['orientation'])))
        epoch = np.array(self.data[:, 0], dtype=int)
        dtime = np.asarray(epoch, dtype='datetime64[s]')
        print dtime
        pt = Tidalyse(epoch,xmag )

        print self.data[:,6]

        pt.addConstituent(self.constituent)
        pt.recompute()
        self.parent.plot.clear()
        p0 = self.parent.plot.addPlot(row=0, col=0)
        p0.showGrid(x=True, y=True)
        rows, cols = pt.feather.shape
        # xm = p0.plot(epoch,dir,pen=(255,128,255))
        for i in xrange(1, cols, 1):
            plots[i] = p0.plot(pt.feather[:, 0], pt.feather[:, i], pen=(255, 128 / i, 255 / i))
            feat[i] = p0.plot(pt.current[:, 0], pt.current[:, i], pen=(255 / i, 128, 255))
        xax = p0.getAxis('bottom')
        # ttick =[]
        # for i in  pt.time.tolist():
        #   ttick.append((np.arange(rows),i.strftime('%m/%d/%Y')))
        # xax.setTicks([(it, it.strftime('%m/%d/%Y')) for it in [pt.time.tolist()]]) #t.strftime('%m/%d/%Y')
        # xax.setTicks(ttick)
    def processdata(self):
        os.path.walk(self.datasource,self.oswalkCallback,None)
        self.save()
    def oswalkCallback(self, arg, directory, files):
        for file in sorted(files):
            self.readdata(os.path.join(directory, file))
    def readdata(self,datapath):


        with open(datapath) as f:
            for i,line in  enumerate(f):
                if str(line).startswith('Line'):
                    pass
                else:
                    #print re.split(r',',re.sub(r'\n','',line))
                    preplot,shot,time,minF,maxF,avgF =re.split(r',',re.sub(r'\n','',line))
                    self._data[int(shot)] = re.split(r',',re.sub(r'\n','',line))




        f.close()


