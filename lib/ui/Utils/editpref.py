from configobj import ConfigObj
from lib.ui.Utils.utils import Utilities

class EditPref(Utilities):
    title = "Edit Preferences"
    def __init__(self):
        Utilities.__init__(self)
        self.config = ConfigObj("./config/seasnake.conf")