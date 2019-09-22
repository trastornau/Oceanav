
import  os
import sys
import numpy as np
import  math
from PyQt4.QtGui import QMessageBox
from threading import Thread, Event
from datetime import  datetime
from datetime import timedelta
from pytides.tide import Tide, d2r, r2d
from pytides.constituent import  *
from lib.datetimehandler import DateUtility


class Tidalyse():
    _scale = 1
    _shift = 0
    _days = 3
    _vesselspeed = 4.5
    all_const = noaa
    default_const = ['M2', 'S2' ,'K1' ,'O1', 'F4' ,'F6']
    constituent = {}
    tidedata={}
    predictiondata={}
    prediction_interval = 0.1

    _predictionparams={}


    # def __init__(self, time=[], xmagnitude=[], days = 7, shift=0, scale = 1):
    #     self.epochlist = time
    #     self.dtime = np.asarray(time, dtype='datetime64[s]')
    #     self.time = np.array(self.dtime[::10])
    #     self.xmag = np.array(xmagnitude[::10])
    #     self.scale = scale
    #     self.days = int(days)
    def __init__(self, xmagdata=[], days = 10, shift=0, scale = 1):
        #npdiff = (np.datetime64('1980-01-01T00:00:00Z','s')-np.datetime64('1970-01-01T00:00:00Z','s')).astype(datetime)#/np.timedelta64(1, 's')
        self.epochlist = xmagdata[:,0] #+npdiff.total_seconds()
        self.dtime = np.asarray(self.epochlist, dtype='datetime64[s]')
        self.time = np.array(self.dtime[::20])
        self.xmag =xmagdata[::20,1] #np.array(xmagdata[::10,1])
        self.scale = scale
        self.dateutil = DateUtility(year=1980,month=6,day=2)
        self.days = int(days)

    @property
    def predictionparams(self):
        return self._predictionparams
    @predictionparams.setter
    def predictionparams(self,params):
        self._predictionparams = params
        for k,v in self.predictionparams.items():
            if k == 'vessel speed':
                self.vesselspeed = v
            if k == 'scale':
                self.scale = v
            if k == 'shift':
                self.shift = v
            if k == 'days to predict':
                self.days = v

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, timearray=[]):
        """
        Setting time array for the prediction, this is a 1 dimension numpy array type
        :param timearray:
        :return:
        """
        # TODO No input validation as yet
        self._time = timearray

    @property
    def vesselspeed(self):
        return self._vesselspeed

    @vesselspeed.setter
    def vesselspeed(self, speed=1):
        try:
            assert isinstance(speed, (int, long, float))
            self._vesselspeed = speed
        except ValueError:
            print ("Tidalyse vesselspeed only accept number")

    @property
    def days(self):
        return self._days

    @days.setter
    def days(self, no_of_days=1):
        try:
            assert isinstance(no_of_days, (int, long, float))
            self._days = no_of_days
        except ValueError:
            print ("Tidalyse days only accept number")

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, xscale=1):
        try:
            assert isinstance(xscale, (int, long, float))
            self._scale = xscale
        except ValueError:
            print ("Tidalyse scale only accept number")

    @property
    def shift(self):
        return self._shift

    @shift.setter
    def shift(self, shift=1):
        try:
            assert isinstance(shift, (int, long, float))
            self._shift = shift
        except ValueError:
            print ("Tidalyse shift only accept number")
    @property
    def _computegeneric(self):
        name = "generic"
        self.tidedata ={}
        self.predictiondata={}
        self.last_time = np.max(self.epochlist)
        t0 = self.time.tolist()[0]
        self.dateutil.add(t0)
        hours =(self.prediction_interval * np.arange((self.days+(self.dateutil.currentepoch() - self.dateutil.getgpstime())/86400) * 24 * 10))
        self.times  = Tide._times(t0, hours)
        data = Tide.decompose(self.xmag, self.time.tolist())
        self.tidedata[name] = data
        pred = self.tidedata[name].at(self.times)
        self.predictiondata[name] = pred * self.scale
        return self.predictiondata
    def recompute(self, ignoreconstituent=False):
        if not ignoreconstituent:
            return  self._compute
            try:
                pass
            except:
                print "Error Occured"
                print "Value of self.time\n",self.time
                print "Value of self.xmag\n",self.xmag
                print "Value of self.dtime\n",self.dtime
        else:
            return self._computegeneric
    def addConstituent(self, newconst ={'default':"M2 N2 S2"}):
        self.constituent.clear()
        for k,v in newconst.items():
            temp_constituent = []
            t_const = v.split()
            if len(t_const)>0:
                for const in self.all_const:
                    if const.name in t_const:
                        temp_constituent.append(const)
                self.constituent[k]= temp_constituent


    @property
    def _compute(self):
        
        self.tidedata ={}
        self.predictiondata={}
        self.last_time = np.max(self.epochlist)
        for name, const in self.constituent.items():
            t0 = self.time.tolist()[0]
            self.dateutil.add(t0)
            hours =(self.prediction_interval * np.arange((self.days+(self.dateutil.currentepoch() - self.dateutil.getgpstime())/86400) * 24 * 10))
            self.times  = Tide._times(t0, hours)
            data = Tide.decompose(self.xmag, self.time.tolist(), None, None, self.constituent[name])
            self.tidedata[name] = data
            pred = self.tidedata[name].at(self.times)
            self.predictiondata[name] = pred * self.scale
        return self.predictiondata
    def __shift_times(self, Dt, shift):
        return Dt + timedelta(minutes=shift)
    @property
    def current(self):
        return self.tidearray
    @property
    def feather(self):
        tidedata = self.tidearray
        row,col = tidedata.shape
        colstart = 1
        #print "Current {}".format(tidedata)
        for i in range(colstart,col,1):
            tidedata[:,i]=np.degrees(np.sin(tidedata[:,i]/self.vesselspeed))
        #print "Feather {}".format(tidedata)

        return tidedata

    @property
    def tidestring(self):
        tidedata = self.tidearray
        stringtide = ""
        for i in tidedata:
            stringtide += "{} {}\n".format(i[0].strftime("%Y-%m-%d %H:%M"),i[1])
        return stringtide
    def savefeather(self,filename):
        data=self.feather
        if not filename:
            return
        else:
            try:
                np.savetxt(filename, data, fmt='%.2f', delimiter=',')
                QMessageBox.information(self,"Feather prediction data saved")
            except:
                QMessageBox.critical(self,"Error saving feather prediction data")
    def savecurrent(self,filename):
        data = self.tidearray
        if not filename:
            return
        else:
            try:
                np.savetxt(filename, data, fmt='%.2f', delimiter=',')
                QMessageBox.Information("Prediction data saved")
            except:
                QMessageBox.Information("Error saving prediction data")
    @property
    def tidearray(self):
        c = 1

        t = self.__shift_times(self.times,self.shift)
        #dt64 = np.datetime64(np.array(t,dtype='datetime64[ns]'))
        # Store time data back as float epoch np.array(t,dtype='datetime64[s]')
        ts = (
                t.astype('datetime64[s]')  - np.datetime64('1970-01-01T00:00:00Z')
             ) / np.timedelta64(1, 's')
        s=len(self.predictiondata.keys()) + 1
        #try:
        el=len(self.predictiondata.values()[0])
        tideitems = np.zeros((el,s),dtype=np.float)
        tideitems[:, 0] = tideitems[:, 0] + ts
        for val in self.predictiondata.values():
            tideitems[:,c] = tideitems[:,c] + val
            c+=1
        return tideitems
        #except:
        #    print "Value of prediction data\n",self.predictiondata
        #    return np.zeros((2,2),dtype=np.float)
