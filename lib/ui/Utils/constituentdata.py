from configobj import ConfigObj
from lib.ui.Utils.utils import Utilities
from PyQt4.Qt import  *

class ConstituentData(Utilities):
    title = "Edit Constituent Data"
    def __init__(self):
        Utilities.__init__(self)
        self.dialog.setWindowTitle(self.title)
        self.constlayout = QFormLayout()
        self.clistlayout = QFormLayout()
        self.config = ConfigObj("./config/seasnake.conf")
        self.constituents = self.config['constituent']

        self.initialize()
        self.populatedialog()


    def populatedialog(self):

        self.storage.clear()
        ___outer = QVBoxLayout()
        ___outer.setAlignment(Qt.AlignTop)
        ___outer.addLayout(self.constlayout)

        self.dialog.setLayout(___outer)
        btndel = QPushButton("Delete Selected")
        btnaddnew = QPushButton("Add New")
        btndel.clicked.connect(self.on_del)
        btnaddnew.clicked.connect(self.on_addnew)

        btnok = QPushButton("OK")
        btnok.clicked.connect(self.on_ok)
        btncancel = QPushButton("Cancel")
        self.constlayout.addRow(self.clistlayout)
        self.constlayout.addRow(btndel,btnaddnew)
        self.constlayout.addRow(btncancel,btnok)
    def initialize(self):
        self.newformlayout = None
        self.newform = self.addnewform
        self.storage = {}
        self.const_chcekbox={}

        for i in reversed(range(self.clistlayout.count())):
            self.clistlayout.takeAt(i).widget().setParent(None)
        for k,v in self.constituents.items():
            self.const_chcekbox[k] = QCheckBox(k)
            self.storage[k] = QLineEdit(text=v)
            self.storage[k].setObjectName(k)
            self.clistlayout.addRow(self.const_chcekbox[k],self.storage[k])
    @property
    def addnewform(self):
        self.newformlayout = QFormLayout()
        lblconst = QLabel("Constituent label")
        lblval = QLabel("Consttituent Value")
        constEdit = QLineEdit()
        valEdit = QLineEdit()
        msg = QLabel()

        btnsave = QPushButton("Save")
        btndiscard=QPushButton("Discard")
        def saveConstituent():
            if not constEdit.text() or not valEdit.text():
                msg.setText("Error Empty")
            else:
                self.constituents[str(constEdit.text())]=str(valEdit.text())
                self.config.write()
                self.closeNewPane()
                self.initialize()
                msg.setText("Config Saved")

        btndiscard.clicked.connect(self.removeNewConstituent)
        btnsave.clicked.connect(saveConstituent)
        self.newformlayout.addRow(lblconst, constEdit)
        self.newformlayout.addRow(lblval, valEdit)
        self.newformlayout.addRow(btndiscard,btnsave)
        self.newformlayout.addRow(None,msg)
        return self.newformlayout
    def closeNewPane(self):
        for i in reversed(range(self.newformlayout.count())):
            self.newformlayout.takeAt(i).widget().setParent(None)
    def removeNewConstituent(self):
        self.closeNewPane()
    def on_del(self):
        for k,v in self.const_chcekbox.items():
            if v.isChecked():
                del self.constituents[k]
        self.config.write()
        self.initialize()
    def on_addnew(self):
        try:
            self.constlayout.addRow(None,self.newform)
        except:
            pass


    def on_ok(self):
        #chld = self.dialog.children()
        #for wgt in chld:
        #    print wgt.__getattr__
        self.config.write()
        self.dialog.close()
