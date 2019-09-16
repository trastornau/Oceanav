from datetime import  datetime, date, timedelta

class DateUtility(object):
    def __init__(self, **kwargs):
        self.epoch = datetime(year=1980,month=1,day=6)
        self.moduletime = None
        if 'date' not in kwargs.keys():
            pass
        for k,v in kwargs.items():
            if k == 'datetime':
                self.datetime = v

    def __call__(self, *args, **kwargs):
        return  self
    def add(self,date='06/01/1980',time='00:00:00'):
        strtime = ' '.join([date,time])
        self.moduletime = datetime.strptime(strtime, "%d/%m/%y %H:%M:%S")
    def roundtime(self,sec):
        interval = 360
        return sec - (sec % interval)
    def getgpstime(self):
        td = (self.moduletime - self.epoch)
        dir(td)
        return self.roundtime((td.seconds + td.days * 24 * 3600))
        #return self.roundtime(td.seconds)
    def togps(self, deltatime):
        td = (deltatime - self.epoch)
        return (td.seconds + td.days * 24 * 3600)
    def getdate(self):
        return self.todate(self.getgpstime())
    def todate(self,gpsepoc):
        #
        return datetime.strftime(self.epoch+ timedelta(seconds=int(gpsepoc)) ,"%d/%m/%Y %H:%M:%S")
    def currentepoch(self):
        dt = datetime.utcnow() - self.epoch
        return  (dt.seconds + dt.days * 24 * 3600)

