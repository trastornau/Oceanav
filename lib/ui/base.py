from PyQt4.QtCore import (Qt)
from PyQt4.QtGui import  *
from PyQt4.Qt import *
from lib.pyqtgraph import *
from lib.dscontroller import *
from lib.datetimehandler import *
from lib.ui.linelist import LineFeather
from lib.plotter import Plotter, DateAxis
from configobj import ConfigObj
class StatusBar(QStatusBar):
    def __init__(self,parent=None):
        super(StatusBar,self).__init__(parent)


class MainWindow(QMainWindow):
    constcheck = {}
    def __init__(self):
        QMainWindow.__init__(self)
        self.__config = ConfigObj("./config/seasnake.conf")
        self.setMinimumSize(QSize(int(self.__config['general']['win_width']),int(self.__config['general']['win_height'])))
        self.dateutil = DateUtility()
        #print self.dateutil.todate(self.dateutil.currentepoch()), self.dateutil.currentepoch()
        self.plugins = []
        self.plot=Plotter()
        self.plot.setMinimumHeight(600)
        self.linelist = LineFeather(self)
        self.todaymark = InfiniteLine(angle=90,movable=False, pos=(self.dateutil.currentepoch()),name="Now", pen="g")
        self.todaymark.setFocus()
        self.plot._plt.addItem(self.todaymark,ignoreBounds=True)
        self.plot.region.setRegion([int(self.dateutil.currentepoch()-7200),int(self.dateutil.currentepoch()+36000)])
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateUI)
        self.timer.setInterval(10)
        self.timer.start(50)
        self.status = StatusBar()
        self.setStatusBar(self.status)
        self.statuslayout = QHBoxLayout()
        self.__maindisplay=QGroupBox()
        self.mainlayout= QFormLayout()
        self.mainlayout.expandingDirections()
        self.__maindisplay.setLayout(self.mainlayout)
        self.mainlayout.addRow(self.linelist, self.plot)
        self.mainlayout.addRow(self.linelist.chkplot,self.linelist.chkfpredict )
        self.datapanel= QFormLayout()
        self.dslayout = QVBoxLayout()
        self.importerlayout = QVBoxLayout()
        self.importerlayout.setAlignment(Qt.AlignTop)
        self.importerdock = self.__build_dock
        self.importerdock.setLayout(self.importerlayout)

        self.progressbar = QProgressBar()
        self.progressbar.setMaximumWidth(100)
        self.progressbar.setMaximum(100)
        self.status.addPermanentWidget(self.progressbar)

        self.btntrigger = QPushButton("Start Prediction")
        self.btntrigger.clicked.connect(self.btntrigger_click)
        self.constituent_opts = QComboBox()

        self.datasource = DataSourceController(self)

        for k,v in self.__config['constituent'].items():
            self.constituent_opts.addItem(k)
            self.constcheck[k]= QCheckBox(k)
            self.constcheck[k].toggled.connect(self.btntrigger_click)


        self.dock = self.__dock
        self.dock.setWindowTitle("Options")
        self.tab = QTabWidget()
        self.tab.addTab(self.importerdock, "Importer")
        self.tab.addTab(self.__build_dspanel,"Datasource")
        self.tab.addTab(self.__build_dock, "Utilities")
        self.tab.addTab(self.__build_dock, "About")
        self.tab.setCurrentIndex(1)
        self.dock.setWidget(self.tab)
        self.addDockWidget(Qt.LeftDockWidgetArea,self.dock)
        self.setCentralWidget(self.__maindisplay)
    def updateUI(self):
        self.todaymark.setPos(self.dateutil.currentepoch())
        #print self.todaymark.getPos()
    @property
    def xaxis(self):
        ax = DateAxis(orientation='bottom')
        return ax
    def setPlugins(self,pluginarray=[]):
        self.plugins = pluginarray
    def btntrigger_click(self):
         self.datasource.selected.constituent = {}
         self.datasource.clearplot()
         for k,v in self.constcheck.items():
             if self.constcheck[k].isChecked():
                 self.datasource.selected.constituent[k] = self.__config['constituent'][str(v.text())]

         if len(self.datasource.selected.constituent.keys()) != 0:
            self.datasource.selected.bootup()
    @property
    def __build_dspanel(self):
        gb = QGroupBox()
        gb.setAlignment(Qt.AlignCenter)
        gblayout = QVBoxLayout()
        gblayout.addWidget(self.datasource.dscheckbox)
        for i in self.constcheck.values():
            gblayout.addWidget(i)
        gblayout.addWidget(self.datasource.paramgb)
        gblayout.addWidget(self.btntrigger)
        gb.setLayout(gblayout)
        return gb
    @property
    def __build_dock(self):
        gb = QGroupBox()
        return  gb
    @property
    def __dock(self):
        dock = QDockWidget(self)
        dock.setMinimumWidth(300)
        dock.setMinimumHeight(100)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        return dock
    @property
    def menubar(self):
        return self.menuBar()
    @property
    def toolbar(self):
        return  self.toolButtonStyle()

