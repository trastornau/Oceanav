from datetime import  datetime, date, timedelta
import numpy as np

class DateUtility(object):
    def __init__(self, **kwargs):
        
        self.npdiff = (np.datetime64('1980-01-06T00:00:00Z','s')-np.datetime64('1970-01-01T00:00:00Z','s')).astype(datetime)#/np.timedelta64(1, 's')
        self.epoch = datetime(year=1980,month=1,day=6)
        self.moduletime = None
        if 'date' not in kwargs.keys():
            pass
        for k,v in kwargs.items():
            if k == 'datetime':
                self.datetime = v

    def __call__(self, *args, **kwargs):
        return  self
    
    def add(self, t):
        self.moduletime = t + self.npdiff#datetime.strptime(strtime, "%d/%m/%y %H:%M:%S")
    def roundtime(self,sec):
        interval = 360
        return sec - (sec % interval)
    def getgpstime(self):
        td = (self.moduletime - self.epoch)
        return self.roundtime((td.seconds + td.days * 24 * 3600))
        #return self.roundtime(td.seconds)
    def togps(self, deltatime):
        td = (deltatime - self.epoch+self.npdiff)
        return (td.seconds + td.days * 24 * 3600)
    def getdate(self):
        return self.todate(self.getgpstime())
    def todate(self,gpsepoc):
        return datetime.fromtimestamp(gpsepoc)
        
    def todatestr(self, gpsepoc):
        #
        return datetime.strftime(self.epoch+ timedelta(seconds=int(gpsepoc)) ,"%d/%m/%Y %H:%M:%S")
    def currentepoch(self):
        dt = datetime.utcnow() - self.epoch + self.npdiff
        return  (dt.seconds + dt.days * 24 * 3600)

