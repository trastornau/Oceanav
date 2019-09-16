import  os, sys
from subprocess import *
from lib.datasource.datasource import DataSource

class NOOA(DataSource):
    id="NOAA"
    name = "NOAA Data From Internet (Unimplemented)"
    desc = "Download NOAA Data from Internet"
    version = "1.0"
    sourcetype = "FILE"
    def __init__(self,parent=None):
        DataSource.__init__(self,parent)

