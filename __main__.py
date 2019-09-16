#!/usr/bin/env python2.7


import os
import sys
import argparse
import numpy as np
from configobj import ConfigObj
from threading import  Thread
from PyQt4.Qt import  QApplication
from PyQt4 import QtGui
from lib.ui.Utils import  *
from lib.ui.base import MainWindow
from lib.pytidalyse import Tidalyse
from lib.database import  dbapp

def predict_init():
    pass

if __name__  == '__main__':

    QtGui.QApplication.setGraphicsSystem('native')
    app = QApplication(sys.argv)
    config = dbapp()
    #tyd = Tidalyse()
    mw = MainWindow()
    # Initializing Available datasource
    #modectl = [dsc(parent=mw) for dsc in datasource.DataSource.__subclasses__()]
    # Getting all the utilies available
    tools= [utl() for utl in utils.Utilities.__subclasses__()]
    #mw.setPlugins(modectl)
    mw.setWindowTitle("SeaSnake: Tide and Untide")
    filemenu = mw.menubar.addMenu("&File")

    #x2 = np.linspace(-100, 100, 1000)
    #data2 = np.sin(x2) / x2
    #p0=mw.plot.addPlot(row=0,col=0)
    #p0.showGrid(x=True,y=True)


    #c1=p0.plot(data2,pen=(255,255,0),name="Whatever")
    #c2=p0.plot(data2*np.sin(x2),pen=(255,0,255),name="Spectrum")
    #mw.plot.nextRow()
    #text = """The value shown above is the result of the tidal prediction of the currentplease consult the regime condition and operation specific area"""
    #mw.plot.addLabel(text, col=0, colspan=4)
    # for dsc in modectl:
    #     mw.mode_opts.addItem(dsc.name)
    #     mw.importerlayout.addWidget(dsc.importer)
    #     for k,v in dsc._data.items():
    #         print v[13]

    if len(tools)>0:
        utilmenu = mw.menubar.addMenu("&Tools")
        for mnu in tools:
            utilmenu.addAction(mnu.ui)
    mw.show()
    sys.exit(app.exec_())