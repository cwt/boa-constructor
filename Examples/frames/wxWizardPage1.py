#Boa:WizardPage:wxWizardPage1

from wxPython.wx import *
from wxPython.wizard import *

[wxID_WXWIZARDPAGE1] = map(lambda _init_ctrls: wxNewId(), range(1))

class wxWizardPage1(wxWizardPage):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxWizardPage.__init__(self, bitmap=wxNullBitmap, parent=prnt)
        self.SetSize(wxSize(960, 692))
        self.SetClientSize(wxSize(952, 665))
        self.SetPosition(wxPoint(88, 88))

    def __init__(self, parent):
        self._init_ctrls(parent)
