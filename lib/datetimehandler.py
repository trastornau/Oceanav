from datetime import  datetime, date, timedelta
import numpy as np

class DateUtility(object):
    def __init__(self, **kwargs):
        """
        Datetime utility
        we need to correct the time epoch differences between numpy and trinav
        trinav started from 06-01-1980 while numpy started from 01-01-1970
        so we need to make correcttion value to it
        """
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
    def add(self, *args , **kwargs):
        """
        Set the date of the modules
        params: dt
        params: date and time 
        
        """
        
        if len(args) == 1:
            if type(args[0]) == datetime:
                    self.moduletime = args[0] + self.npdiff
            else:
                try:
                    self.moduletime = datetime.strptime(args[0],"%d/%m/%y %H:%M:%S") + self.npdiff
                except:
                    raise("Wrong datetime string format, please use dd/mm/yyyy hh:mm:ss")
                finally:
                    self.moduletime = datetime.strptime(args[0],"%d/%m/%y %H:%M:%S") + self.npdiff
        elif len(args) ==2:
            self.moduletime = datetime.strptime(' '.join(args[0],args[1]),"%d/%m/%y %H:%M:%S") + self.npdiff
        else:
            if 'dt' in kwargs:
                if type(kwargs['dt']) == datetime:
                    self.moduletime = kwargs['dt'] + self.npdiff
                else:
                    try:
                        self.moduletime = datetime.strptime(kwargs['dt'],"%d/%m/%y %H:%M:%S") + self.npdiff
                    except:
                        raise("Wrong datetime string format, please use dd/mm/yyyy hh:mm:ss")
                    finally:
                        self.moduletime = datetime.strptime(kwargs['dt'],"%d/%m/%y %H:%M:%S") + self.npdiff
            elif 'date' in kwargs:
                if 'time' in kwargs:
                    self.moduletime = datetime.strptime(' '.join([kwargs['date'], kwargs['time']]),"%d/%m/%y %H:%M:%S") + self.npdiff
                else:
                    self.moduletime = datetime.strptime(' '.join([kwargs['date'], "00:00:00"]),"%d/%m/%y %H:%M:%S") + self.npdiff
            else:
                self.moduletime = datetime(year=1980, month=1, day=6) + self.npdiff
        
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

