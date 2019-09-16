__private = {'depth':[8,(0.0,200.0)],
              'scale':[1,(-100.0,100.0)],
              'orientation':[90,(0.0,360.0)],
              'days to predict':[7,(1.0,365.0)],
              'shift':[1,(-3600.0,3600.0)],
              'vessel speed':[4.5,(1.2,8.0)],
              'streamer':[0.0,(0.0,30000.0)],
             }
defaultparams={}
defaultvalue={}

for k,v in __private.items():
    defaultparams[k]=v[0]
    defaultvalue[k]=v[1]

