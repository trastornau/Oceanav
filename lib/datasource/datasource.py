import  math
import  os
import  shelve
from configobj import ConfigObj
from subprocess import Popen, PIPE, call
from lib.ui.formwidget import *
from lib.datetimehandler import DateUtility
#TODO Need to be removed after implementation dscontroller finised

from lib import  constant as const
from lib.datetimehandler import DateUtility
from PyQt4.QtCore import pyqtSignal, QThread, QProcess
from PyQt4.Qt import *
import numpy as np


class DataSource(QDialog):
    id="generic"
    name = "Generic Datasource Processor"
    desc = "Generic Datasource Processor and Formatter"
    version = "1.0"
    datapath = "./data"
    datasource = "./data"
    bypassdialog = False
    _data = {}
    form_spec = {}
    controlarray = []
    ReadDone = pyqtSignal
    constituent = {}
    params = const.defaultparams # Data defined in lib.constant
    datasourceplot ={}
    predictionplot={}
    def __init__(self,parent = None ):
        QDialog.__init__(self,parent)
        self.parent = parent
        self.datehandler = DateUtility(year=1980,month=6,day=1)
        self.np = np
        self.plotparent = self.parent.plot

        self.tideplot = self.plotparent.rawplot
        self.predplot = self.plotparent.fplot

        self.tideplot.enableAutoRange('xy', 0.95)
        self.tideplot.legend.items = []


        self.predplot.enableAutoRange('xy', 0.95)
        self.predplot.legend.items = []


        self.config = ConfigObj(infile='./config/datasource.conf', indent_type='    ')
        #self.storage = shelve.open('./data/{}_Storage'.format(self.id))
        self.path = os.path.join(self.datapath, self.id)
        if not os.path.isdir(self.path):
            os.mkdir(self.path)

        if self.id not in self.config.keys():
            try:
                self.setup_once()
            except Exception as e:
                print ("Error {}".format(e.args))
        else:
            pass
        self.__data= None
        self.ui = self.__ui
        self.dateutil = DateUtility()
        self.dialog = self.makedialog
        self.idialog = self.makedialog
        self.ilayout = QFormLayout()
        self.idialog.setLayout(self.ilayout)
        self.idialog.setWindowTitle("Import {}".format(self.name))


        if self.config.has_key(self.id):
            self.__confToUI(self.idialog)
        else:
            pass

        ok = QPushButton("OK")
        cnc = QPushButton("Cancel")
        cnc.clicked.connect(self.idialog.close)
        self.ilayout.addRow(ok, cnc)

        self.populatedialog()
        self.actions = self.act
        self.options = {}
    def getshift(self):
        """

        :rtype : object
        """
        speed = self.params['vessel speed']
        distance = self.params['streamer']
        timeshift = ((distance/1852)/speed) * 60
        timeshift = timeshift + int(self.params['shift'])
        return timeshift
    def asNumpyArray(self):
        tmpdict = {}
        tmparr = []
        for key in sorted(self._data.iterkeys()):
            tmpdict[key] = self._data[key]
        for key, val in tmpdict.items():
            #print val
            curr = []
            curr.append(key)
            curr.extend(val)
            tmparr.append(curr)
        return np.array(tmparr, dtype=float)

    def save(self):
        arr = self.asNumpyArray()
        filename = os.path.join(self.path,"DB.{}".format(self.id))
        try:
            np.savetxt(filename, arr, fmt='%.2f', delimiter=',')
            print ("{} Data saved".format(self.name))
            #QMessageBox.information(self, "{} data saved".format(self.name))
        except:
            print ("{} Saving Error saved".format(self.name))
            #QMessageBox.critical(self,"Error in saving {}".format(self.name))

    def oswalkCallback(self, arg, directory, files):
        for file in sorted(files):
            self.readdata(os.path.join(directory, file))
    def resetConfig(self):
        self.config[self.id]
        for k,v in self.form_spec.items():
            self.config[self.id][k]=v
        self.config.write()


    def readdata(self,datapath):
        pass
    def dms2dd(self):
        pass
    def dd2dms(self):
        pass
    def dms2grid(self):
        pass
    def setup_once(self):
        pass
    def reader(self):
        pass
    def predict(self):
        pass
    def customPredictionDialog(self,layout):
        pass
    def customImportDialog(self,layout):
        pass
    @property
    def optionparam(self):
        frame = QGroupBox()
        frly = QFormLayout()
        frame.setLayout(frly)
        self.form_spec.clear()
        widgetlist =const.defaultvalue
        for k,v in sorted(widgetlist.items()):
            if k in self.params.keys():
                _tmp_lab = QLabel(k.capitalize())
                _tmp_= QDoubleSpinBox()
                _tmp_.setValue(self.params[k])
                _tmp_.setMinimum(v[0])
                _tmp_.setMaximum(v[1])
                _tmp_.valueChanged.connect(self.parent.btntrigger_click)
                self.form_spec[k] = _tmp_
                frly.addRow(_tmp_lab,_tmp_)
        return frame

    def populatedialog(self):
        di_layout = QFormLayout()
        di_layout.addRow(QLabel("To generate prediction data, please click Predict button bellow!"))
        self.customPredictionDialog(di_layout)
        proc_button = QPushButton("Predict")
        proc_button.clicked.connect(self.initprediction)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.dialog.close)


        di_layout.addRow(cancel_button, proc_button)
        self.dialog.setLayout(di_layout)
    def generateInitialConfig(self):
        __lay = QFormLayout()
        for inp in self.form_spec.items():
            __lay.addRow(QLabel(inp[1][0]))
        return __lay
    @property
    def act(self):
        m = QAction(self.name, self,
                    statusTip=self.desc,
                    triggered=self.bootup)
        return m
    def bootup(self,options={}):
        self.options = options
        self.updateParams()
        if self.bypassdialog:

            self.initprediction()
        else:
            self.dialog.show()
    def updateParams(self):
        for k in self.params.keys():
            val = self.form_spec[k].value()
            self.params[k]=val

    @property
    def makedialog(self):
        startupdalog = QDialog(self)
        startupdalog.setWindowTitle("{} Startup".format(self.name))
        startupdalog.setModal(True)
        return startupdalog

    def xlineMag(self,_mag, _direction, _orientation):
        theta = _direction - _orientation
        return _mag * math.sin(math.radians(theta))
    def shutdown(self):
        pass
    def dataimport(self):
        pass
    def prepare(self):
        pass
    def processdata(self):
        pass
    @property
    def results(self):
        return self.__data
    def clearplot(self):
        for v in self.datasourceplot.values():
            if v:
                self.parent.plot.rawplot.legend.items = []
                self.parent.plot.rawplot.removeItem(v)
        for v in self.predictionplot.values():
            if v:
                self.parent.plot.fplot.legend.items=[]
                self.parent.plot.fplot.removeItem(v)
        self.predictionplot.clear()
        self.datasourceplot.clear()
    def initprediction(self):
        #self.clearplot()
        self.predict()
    def predict(self):
        pass
    def __confToUI(self,dialog):
        for key,val in dict(self.config[self.id]).items():
            if key.startswith("ui"):
                if val['type'] == 'folder':
                    self.controlarray.append(folderinput(val["caption"]))
                elif val['type'] == 'file':
                    self.controlarray.append(fileinput(val["caption"]))
                elif val['type'] == 'boolean':
                    self.controlarray.append(boolinput(val["caption"]))
                elif val['type'] == 'int':
                    pass
                elif val['type'] == 'double':
                    pass
                elif val['type'] == 'options':
                    pass
                elif val['type'] == 'radio':
                    pass
                elif val['type'] == 'multi':
                    pass
        for wd in self.controlarray :
            self.ilayout.addRow(wd.label, wd.widget)
            if wd.trigger:
               self.ilayout.addRow(None, wd.trigger)

    def importData(self):
        self.idialog.setMinimumSize(400,300)
        self.idialog.show()
    @property
    def importer(self):
        btn = QPushButton(self.name)
        btn.clicked.connect(self.importData)
        return btn
    @property
    def __ui(self):
        pass



