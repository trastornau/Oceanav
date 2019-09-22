
import numpy as np
import time
from lib.datetimehandler import DateUtility
from PyQt4.Qt import QTimer
from lib.pyqtgraph import *
from lib.ui.dateaxis import DateAxis
__author__ = 'aco-nav'


class DateAxis(AxisItem):
    def tickStrings(self,values,scale,spacing):
        strns = []
        dtu = DateUtility()
        strns = [dtu.todate(x) for x in values]

        return strns
        #return AxisItem.tickStrings(self, , scale, spacing)
    def _tickStrings(self, values, scale, spacing):
        strns = []
        rng = max(values)-min(values)
        #if rng < 120:
        #    return AxisItem.tickStrings(self, values, scale, spacing)
        if rng < 3600*24:
            string = '%H:%M:%S'
            label1 = '%b %d -'
            label2 = ' %b %d, %Y'
        elif rng >= 3600*24 and rng < 3600*24*30:
            string = '%d'
            label1 = '%b - '
            label2 = '%b, %Y'
        elif rng >= 3600*24*30 and rng < 3600*24*30*24:
            string = '%b'
            label1 = '%Y -'
            label2 = ' %Y'
        elif rng >=3600*24*30*24:
            string = '%Y'
            label1 = ''
            label2 = ''
        for x in values:
            try:
                strns.append(time.strftime(string, time.localtime(x)))
            except ValueError:  ## Windows can't handle dates before 1970
                strns.append('')
        try:
            label = time.strftime(label1, time.localtime(min(values)))+time.strftime(label2, time.localtime(max(values)))
        except ValueError:
            label = ''
        self.setLabel(text=label)
        return strns


class Plotter(GraphicsWindow):
    def __init__(self,parent=None):
        super(Plotter,self).__init__(parent=None,border=(100, 100, 100))
        self.setBackground((0,0,0))
        self.setMinimumHeight(980)
        #self.sizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.dateutil = DateUtility()
        xaxis = DateAxis(orientation='bottom')
        fxaxis = DateAxis(orientation='bottom')

        self._plt = self.addPlot(row=0,col=0,title="Tide and Current",axisItems={'bottom':xaxis})
        self._plt.addLegend()
        self._plt.setLabel("left", "Magnitude")
        pg = GridItem()
        #self._plt.addItem(pg)

        self._fplot = self.addPlot(row=1,col=0,title="Predicted Data",axisItems={'bottom':fxaxis})
        self._fplot.addLegend()
        fg = GridItem()
        self._fplot.addItem(fg)
        #self._fplot.showGrid(x=True, y=True)
        self._plt.showGrid(x=True, y=True)

        self._fplot.setLabel("left","Feather Angle")
        self.region = LinearRegionItem()
        self._plt.addItem(self.region, ignoreBounds=True)
        self.region.setZValue(10)
        self.todaymark = InfiniteLine(angle=90,movable=False, pos=(self.dateutil.currentepoch()),name="Now", pen="g")
        self.todaytide = InfiniteLine(angle=90,movable=False, pos=(self.dateutil.currentepoch()),name="Now", pen="y")
        self.todaymark.setFocus()
        self.todaytide.setFocus()

        self._plt.addItem(self.todaymark,ignoreBounds=True)
        self._fplot.addItem(self.todaytide, ignoreBounds=True)
        self.region.setRegion([int(self.dateutil.currentepoch()-7200),int(self.dateutil.currentepoch()+36000)])
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateUI)
        self.timer.setInterval(10)
        self.timer.start(50)
        
        
        self._plt.sigRangeChanged.connect(self.updateRegion)
        self._plt.setAutoVisible(y=True)
        self.label =LabelItem(justify='left')

        self._plt.setLabel("bottom", "Time Shift")

        self.vLine = InfiniteLine(angle=90, movable=False, pen="r")
        self.hLine = InfiniteLine(angle=0, movable=False, pen="r")
        self._fplot.addItem(self.vLine, ignoreBounds=True)
        self._fplot.addItem(self.hLine, ignoreBounds=True)
        self.addItem(self.label)
        self.vb = self._fplot.vb
        self.region.sigRegionChanged.connect(self.update)
        self.region.setRegion([int(self.dateutil.currentepoch()-18000),int(self.dateutil.currentepoch()+18000)])
        self._fplot.scene().sigMouseMoved.connect(self.mouseMoved)
        self._plt.setXRange(int(self.dateutil.currentepoch()),int(self.dateutil.currentepoch()+18000), padding=0) 
    def updateRegion(self, window, viewRange):
        rgn = viewRange[0]
        #self.region.setRegion(rgn)
    def mouseMoved(self, evt):
        #pos = evt  ## using signal proxy turns original arguments into a tuple
        
        
        if self._fplot.sceneBoundingRect().contains(evt):
            mousePoint = self.vb.mapSceneToView(evt)
            index = int(mousePoint.x())
            lbl =""
            for n,it in enumerate(self._fplot.items):
                
                if type(it) == PlotDataItem:
                    #print type(it)
                    if index > 0 and index < len(it.getData()[1]):
                        try:
                           lbl = lbl+" %0.1f" % (it.getData()[1][index])
                        except:
                            lbl=lbl
            self.label.setText("<span style='font-size: 12pt'>Time %s</span><br/><span style='font-size: 12pt;color: red'>Angle %0.1f</span>" % (self.dateutil.tohour(mousePoint.x()), mousePoint.y()))
            #if index > 0 and index < len(data1):
            #    self.label.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (mousePoint.x(), data1[index], data2[index]))
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())
    def updateUI(self):
        self.todaymark.setPos(self.dateutil.currentepoch())
        self.todaytide.setPos(self.dateutil.currentepoch())
    def update(self):
        self.region.setZValue(10)
        minX, maxX = self.region.getRegion()
        self.fplot.setXRange(minX, maxX, padding=0)
        
    @property
    def xaxis(self):
        ax = DateAxis(orientation='bottom')
        return ax
    @property
    def rawplot(self):
        return self._plt
    @property
    def fplot(self):
        return self._fplot
    def clearPlot(self):
        pass





#plt = Plotter()
#xaxis = DateAxis(orientation='bottom')
#graph = plt.addPlot(row=0,col=0,axisItems={'bottom':xaxis})
#graph.setLabel("left", "Degrees Relative to Orientation")
#graph.showGrid(x=True,y=True)

