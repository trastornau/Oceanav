from lib.pytidalyse import Tidalyse

class MultiConstituent():
    const_group=[]
    def __init__(self):
        pass
    def addConstituent(self, cons=['M0,K0,S0']):
        self.const_group.append(cons)
    def GeneratePrediction(self,hrs_duration=24):
        pass

