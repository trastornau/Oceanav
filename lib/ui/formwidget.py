from PyQt4.Qt import *

class BaseForm(QHBoxLayout):
    label = ""
    val = ""
    def __init__(self):
        super(BaseForm,self).__init__()
        self.widget = QLabel("Default Widget")
        self.label = QLabel("")
        self.trigger = None
        if self.trigger:
            self.trigger.clicked.connect(self.triggered)
    @property
    def get_value(self):
        return self.val
    def set_value(self,val=''):
        self.val = val
    def component(self):
        return (self.label,self)
    def triggered(self):
        print ("Button triggered")
class boolinput(BaseForm):
    def __init__(self,label="",default=[]):
        super(boolinput, self).__init__()
        self.widget = QCheckBox(label)
        self.addWidget(self.widget)

    @property
    def get_value(self):
        return  self.widget.isChecked()

class lineinput(BaseForm):
    def __init__(self,label="",default=[]):
        super(lineinput, self).__init__()
        self.widget = QLabel(label)
        self.label = QLabel(label)
        self.addWidget(self.label)
        self.addWidget(self.widget)

    @property
    def get_value(self):
        return  self.widget.text()
class folderinput(BaseForm):
    def __init__(self,label="",default=[]):
        super(folderinput,self).__init__()
        self.trigger = QPushButton("&Browse Folder..")
        self.trigger.clicked.connect(self.triggered)
        self.label = QLabel(label)
        self.widget = QLabel(self.val)
        self.addWidget(self.label)
        self.addWidget(self.widget)
        self.addWidget(self.trigger)
    @property
    def get_value(self):
        return  self.widget.text()
    def triggered(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(None, "Select Folder..","Select Folder", options=options)
        if directory:
            self.widget.setText(directory)
class fileinput(BaseForm):
    def __init__(self,label="",default=[]):
        super(fileinput, self).__init__()
        self.trigger = QPushButton("Browse File..")
        self.trigger.clicked.connect(self.triggered)
        self.label = QLabel(label)
        self.widget = QLabel(self.val)
        self.addWidget(self.label)
        self.addWidget(self.widget)
        self.addWidget(self.trigger)
    @property
    def get_value(self):
        return  self.widget.text()

    def triggered(self):
        options = QFileDialog.Options()
        if not self.native.isChecked():
            options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,
                                                  "Select file", "Select File",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            self.widget.setText(fileName)







