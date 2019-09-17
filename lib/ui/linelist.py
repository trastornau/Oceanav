import  sys,os
import re
from PyQt4.QtGui import  *
from PyQt4.QtCore import *
from functools import  partial
from collections import OrderedDict
from threading import Thread
import numpy as np
from lib.pyqtgraph import *
from lib.pytidalyse import Tidalyse
from lib.datetimehandler import DateUtility



class LineFeather(QTableWidget):
    params = {'depth':15,
              'scale':-0.15,
              'orientation':24,
              'days to predict':20,
              'vessel speed':4.3,
              'streamer':8000.0,
              'shift':0.0
              }
    def __init__(self, parent = 0):
        super(LineFeather,self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.parent=parent
        self.plotitem = {}
        self.arrow={}
        self.arrowlabel={}
        self.filelist = []
        self.filecheck = {}
        self.forpredict = {}
        self.trinavfeather = np.array([[0,0]])
        self.chkplot = QCheckBox("Plot All TRINAV Feather")
        self.chkfpredict = QCheckBox("Plot Predicted Feather")
        self.chkplot.toggled.connect(partial(self.plotall,self.chkplot))
        self.chkfpredict.toggled.connect(partial(self.predictandplot,self.chkfpredict))
        self.dateutil = DateUtility()
        self.TRINAVFeather()
        self.LineFeather = OrderedDict(
            [('Feather Fetched From TRINAV',self.filecheck),
             #('Preplot', []),
             #('Direction',[]),
             #('FSP',[]),
             #('LSP',[]),
             #('SOL',[]),
             #('EOL',[]),
             #('P190 Imported?', [])

             ])
        self.setColumnCount(len(self.LineFeather))
        self.setRowCount(len(self.filelist))
        self.resizeRowsToContents()
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(23)
        self.setSortingEnabled(True)
        self.setHorizontalHeaderLabels(self.LineFeather.keys())
        self.horizontalHeader().resizeSection(0, 158)
        self.horizontalHeader().resizeSection(1, 80)
        self.setMinimumHeight(300)
        self.setMaximumWidth(250)
        self.resizeRowsToContents()
        # add all widgets in Qtable 2 plugin
        Headers = []
        for n, key in enumerate(self.LineFeather.keys()): #collections.OrderedDict(sorted(d.items()))
            Headers.append(key)
            for m, item in enumerate(self.LineFeather[key]):
                if type(self.LineFeather[key][item]) == type(QCheckBox()) or type(self.LineFeather[key][item]) == type(QPushButton()):
                    self.setCellWidget(m, n, self.LineFeather[key][item])
                else:
                    item = QTableWidgetItem(self.LineFeather[key][item])
                    self.setItem(m, n, self.LineFeather[key][item])
        self.selectable={}
        for i in self.LineFeather.keys():
            self.selectable[i]=QCheckBox(i)
        self.setHorizontalHeaderLabels(self.selectable.keys())
    #@pyqtSlot(str)
    def fileSelected(self,obj):
        val = str(obj.objectName())
        if obj.isChecked():
            self.forpredict[val]=""
            with open(val) as f:
                lines=f.readlines()

                feather =np.loadtxt(lines,delimiter=',',skiprows=1)
                row,col = feather.shape
                preplot = feather[1,0]
                xax = feather[:,2] + self.dateutil.npdiff.total_seconds()
                fsp = feather[0,1]
                lsp = feather[row-1,1]
                brush =(0,255,0)
                alphavalue = 200
                fth = feather[:,5]
                if fsp > lsp :
                    #Downline
                    fth =np.negative(fth)
                    brush =(255,0,0,alphavalue )
                elif fsp < lsp:
                    #Upline

                    brush =(0,50,255,alphavalue )
                else:
                    brush =(0,255,0,alphavalue )


                self.plotitem[val]=self.parent.plot.plotter.plot(xax,fth , pen=brush)
                self.arrow[val] =CurvePoint(self.plotitem[val],pos=(float(xax.min())))
                self.arrowlabel[val]=TextItem(anchor=(0,0))
                self.arrowlabel[val].setText(str(int(preplot)))
                self.arrowlabel[val].setPos(xax.min(), fth[0])
                self.arrowlabel[val].setParentItem(self.arrow[val])
                self.parent.plot.plotter.addItem(self.arrow[val])
                self.parent.plot.plotter.addItem(self.arrowlabel[val])

            f.close()
        else:
            self.parent.plot.plotter.removeItem(self.plotitem[val])
            self.parent.plot.plotter.removeItem(self.arrow[val])
            self.parent.plot.plotter.removeItem(self.arrowlabel[val])
            del self.forpredict[val]

    def getshift(self):
        """

        :rtype : object
        """
        speed = self.params['vessel speed']
        distance = self.params['streamer']
        timeshift = ((distance/1852)/speed) * 60
        timeshift = timeshift + int(self.params['shift'])
        return timeshift

    def predictandplot(self,obj):
        flag = 0
        if obj.isChecked():
            for f, v in self.forpredict.items():
                with open(f) as fc:
                    lines  = fc.readlines()
                    fdata = np.loadtxt(lines,delimiter=',',skiprows=1)
                    fepoch = np.stack([fdata[:,2]+self.dateutil.npdiff.total_seconds(), fdata[:,5]], axis=-1)
                    
                    if not flag:
                        self.trinavfeather = fepoch
                        flag = 1
                    else:
                        self.trinavfeather = np.append(self.trinavfeather,fepoch, axis=0)
                        
                    
            
            xmagdata = self.trinavfeather[np.argsort(self.trinavfeather[:,0])]
            pf = Tidalyse(xmagdata = xmagdata)
            pf.scale = self.params['scale']
            pf.days = self.params['days to predict']
            pf.vesselspeed = self.params['vessel speed']
            pf.shift = self.getshift()
            pf.addConstituent({'FeatherPredict': 'M2 S2 K1 O1 F4 F6'})
            pf.recompute()
            
            
            self.plotitem["Predicted Feather"]=self.parent.plot.plotter.plot(pf.feather , pen=(255,80,125 ))
        else:
            #print dir(self.plotitem["Predicted Feather"])
            self.parent.plot.plotter.removeItem(self.plotitem["Predicted Feather"])
            #for i in self.parent.plot.plotter.legend.items:
            #    print dir(i)
        
        
        
    def plotall(self,obj):
        def worker():
            if obj.isChecked():
                for v in self.filecheck.values():
                    v.setChecked(True)
            else:
                for v in self.filecheck.values():
                    v.setChecked(False)

        thread = Thread(target=worker)
        thread.start()
        thread.join()

    def TRINAVFeather(self):
        os.path.walk('./data/TrinavAttrFetched',self.oswalkCallback,None)
        self.filecheck = OrderedDict(sorted(self.filecheck.items()))

    def oswalkCallback(self, arg, directory, files):
        for file in sorted(files):
            if re.search('feather',file):
                keyf=int(file.split('_')[0][-3:])
                self.filecheck[file.split('_')[0][-3:]] = QCheckBox("Sequence {}".format(file.split('_')[0][-3:]))
                self.filecheck[file.split('_')[0][-3:]].setObjectName("{}".format(os.path.join(os.path.abspath(directory),file)))
                self.filecheck[file.split('_')[0][-3:]].toggled.connect(partial(self.fileSelected,self.filecheck[file.split('_')[0][-3:]]))
                self.filelist.append(self.filecheck[file.split('_')[0][-3:]])



class TRINAVFeatherDump():
    def __init__(self):
        pass

    @property
    def getfiles(self):
        pass
    def oswalkcallback(self):
        pass


