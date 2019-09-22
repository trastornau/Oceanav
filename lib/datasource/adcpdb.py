import  os, sys
import math
import re
from datetime import datetime
import  numpy as np
from PyQt4.Qt import  *
from lib.ui.linelist import *
from threading import Thread, Event
from lib.datasource.datasource import DataSource
from lib.pytidalyse import Tidalyse



class ADCPDB(DataSource):
    id = "ADCPDB"
    name = "ADCP Data"
    desc = "ADCP Current Meter data Processor"
    version = "1.0"
    datapath = "./data"
    constituent_required = True
    bypassdialog = True
    sourcetype = "FILE"
    params = {'depth':15,
              'scale':1,
              'orientation':24.0,
              'days to predict':3,
              'vessel speed':4.3,
              'streamer':8000.0,
              'shift':0.0
              }

    def __init__(self,parent=None):
        DataSource.__init__(self,parent)
        
        self.data  = None
    def importData(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,"Select ADCP SUM folder..",self.datapath, options=options)
        if directory:
            self.datasource  = os.path.normpath(str(directory))
            thread = Thread(target=self.processdata)
            thread.start()
    def predict(self):
        
        self.raw = np.array(np.loadtxt(os.path.join(self.path,'DB.{}'.format(self.id)),delimiter=','))
        self.data=self.raw[np.argsort(self.raw[:,0])]  # Sort data by epoch before processing

        fpath = os.path.join(self.datapath, 'FEATHER/')
        self.fdata = np.array(np.loadtxt(os.path.join(fpath, 'DB.FEATHER'), delimiter=','))
        plots={} # Plot container
        curr={} # Data container
        datastart = 10 # Do not change this
        depthstart = 8 # And this.
        indepth = datastart+(
            (
                                 int(self.params['depth'])-depthstart
            )*3
                             ) # Every set consist of 3 colunmns
        mag = self.data[:,indepth+1]
        dir = self.data[:,indepth+2]
        xmag = mag * np.sin(np.radians((dir - self.params['orientation'])))
        epoch = np.array(self.data[:,0],dtype=int)
        xmagdata = np.stack([epoch.tolist(), xmag.tolist()],axis=-1)

        # Tidalyse Object and routine
        #pt = Tidalyse(epoch,xmag)
        pt = Tidalyse(xmagdata=xmagdata)
        pt.scale = self.params['scale']
        pt.days = self.params['days to predict']
        pt.vesselspeed = self.params['vessel speed']
        pt.shift = self.getshift()
        pt.addConstituent(self.constituent)    
        pt.recompute()

        # Plotting block
        #self.parent.plot.clear()
        #p0 = self.parent.plot.addPlot(row=0,col=0,axisItems={'bottom':self.parent.xaxis})
        self.tideplot.setLabel("bottom", "Time Shifted by {:02d}:{:02d} mins".format(*divmod(int(pt.shift), 60))) #'{:02d}:{:02d}'.format(*divmod(minutes, 60))'02:15'
        self.tideplot.setLabel("left", "Magnitude - Height (tide)")
        #p0.showGrid(x=True,y=True)

        rows, cols = pt.feather.shape
        for i in xrange(1,cols,1):
            self.predictionplot['feat{}'.format(i)] = self.predplot.plot(pt.feather[:, 0], pt.feather[:, i], brush=((60*i), 32, 60*i, 100), pen=((32*i), (32*2*i), 172), fillLevel=0, name="Feather {}".format(pt.constituent.keys()[i - 1]))
            self.datasourceplot['tides{}'.format(i)] = self.tideplot.plot(pt.current[:, 0], pt.current[:, i], pen=(i * 32, 255/i, 16), name="Tides at {}".format(pt.constituent.keys()[i - 1]))
        
        self.datasourceplot['CurrentMeter']=self.tideplot.plot(xmagdata, pen=(125, 100, 25), name="Current Meter")
        self.tideplot.autoRange()
        self.tideplot.setXRange(int(xmagdata[:,0][-1]-18000),int(self.dateutil.currentepoch()+72000), padding=0)
        self.plotparent.region.setRegion([int(self.dateutil.currentepoch()-18000),int(self.dateutil.currentepoch()+18000)])
        def worker():
            print('Recalculating..')
        
        pthread = Thread(target=worker)
        pthread.start()
        self.dialog.close()

    def oswalkCallback(self, arg, directory, files):
        for file in sorted(files) :
            if file[3:6]=="SUM":
                self.readdata(os.path.join(directory,file))
                #self.parent.setStatusTip("Importing {}, Please wait..".format(file))
                print "Importing .. {}".format(file)

    def processdata(self):
        os.path.walk(self.datasource,self.oswalkCallback,None)
        self.save()
    def readdata(self,filepath):
        insideblock = False
        appear = False
        blockcount = 0
        _component = []
        __curindept = []
        with open(filepath) as f:

            for i, line in enumerate(f):
                if "Temp" in line:
                    insideblock = False
                    appear = False
                    _component = []
                    __curindept = []

                    blockcount += 1
                    (date, time, sp, TempLabel, temp, PitchLabel, pitch, RollLabel, roll, headstr, unused) = re.split(
                        r'\s+', line)
                    (headLabel, heading) = headstr.split(':')
                    self.datehandler.add(datetime.strptime(' '.join([date,time]), "%d/%m/%y %H:%M:%S"))
                    self._data[self.datehandler.getgpstime()] = [int(sp), float(temp), float(pitch), float(roll), float(heading)]
                    # print "{} {} {} {}".format(self.datehandler.getdate(), time, heading, blockcount)
                if 'UPtime' in line:
                    insideblock = True
                    continue

                if insideblock == True:

                    w = re.findall(r'\d\s[NSEW]{1}', line)
                    if len(w) > 0:
                        (t_date, t_time, vesselBSP, vesselCourse, lat, latmark, lon, lonmark, unused) = re.split(r'\s+',
                                                                                                                 line)
                        _temp = [float(vesselBSP), float(vesselCourse)]#, "{} {}".format(lat, latmark), "{} {}".format(lon, lonmark)]
                        if appear == False:
                            self._data[int(self.datehandler.getgpstime())].extend(_temp)
                            appear = True
                            # print '{} {} {} {} {} {}'.format(lat,latmark,lon,lonmark,vesselBSP,vesselCourse)
                    elif "Profile" in line:

                        (bins, binsize) = re.findall(r'\d+', line)
                        __temp = [bins, binsize]
                        self._data[int(self.datehandler.getgpstime())].extend(__temp)

                    else:
                        if line.startswith("*"):

                            continue

                        bindata = line.split()
                        inc = 0
                        ___temp = []

                        for i in range(1, len(bindata) - 1, 2):
                            # binstart = int(re.findall(r'\d{4}',bindata[0])[0])+ inc
                            atbin1 = atbin2 = 000.00
                            if re.findall(r'\*',bindata[i]):
                                atbin1 = 00.00
                            else:
                                atbin1 = bindata[i]

                            if re.findall(r'\*',bindata[i+1]):
                                atbin2 = 000.00
                            else:
                                atbin2 = bindata[i+1]
                            depthc = "{} {} {}".format(int(re.findall(r'\d{4}', bindata[0])[0]) + inc, float(atbin1),
                                                       float(atbin2))
                            inc += int(binsize)
                            ___temp.extend(depthc.split())

                        self._data[self.datehandler.getgpstime()].extend(___temp)
        f.close()

    def setup_once(self):
        self.config[self.id] ={}
        self.config[self.id]['uidatafolder']={'type':'folder',
                                            'caption':'Select SUM Folder',
                                            'value':'','required': 'False',
                                            'disabled':'False',
                                            }
        self.config[self.id]['uialwaysgps']= {'type': 'boolean',
                                              'caption': 'Keep time in EPOCH',
                                              'value': '', 'required': 'False',
                                              'disabled': 'False',
                                              }

        self.config.write()

