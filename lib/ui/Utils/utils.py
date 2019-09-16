import os, sys
from subprocess import  Popen, PIPE
from PyQt4.Qt import  *
from configobj import  ConfigObj



class Utilities(QWidget,object):
    config = None
    title = "Generic Utilities"
    def __init__(self,parent=None):
        self.parent = parent
        QWidget.__init__(self,self.parent)
        self.ui = self.act
        self.dialog = self.makedialog
    def invoke(self):
        self.dialog.show()
    @property
    def act(self):
        m = QAction(self.title, self,
                statusTip="Cut the current selection's contents to the clipboard",
                triggered=self.invoke)
        return m

    @property
    def makedialog(self):
        startupdialog = QDialog(self)
        startupdialog.setWindowTitle("Preferences")
        startupdialog.setModal(True)
        startupdialog.setMinimumWidth(400)
        return startupdialog