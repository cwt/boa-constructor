#Boa:PyWizardPage:wxPyWizardPage2

from wxPython.wx import *
from wxPython.wizard import *

[wxID_WXPYWIZARDPAGE2, wxID_WXPYWIZARDPAGE2BUTTON1, 
 wxID_WXPYWIZARDPAGE2BUTTON2, 
] = map(lambda _init_ctrls: wxNewId(), range(3))

class wxPyWizardPage2(wxPyWizardPage):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxPyWizardPage.__init__(self, bitmap=wxNullBitmap, parent=prnt,
              resource='')
        self.SetName('wxPyWizardPage2')
        self.SetBackgroundColour(wxColour(128, 128, 255))

        self.button1 = wxButton(id=wxID_WXPYWIZARDPAGE2BUTTON1, label='button1',
              name='button1', parent=self, pos=wxPoint(8, 8), size=wxSize(75,
              23), style=0)

        self.button2 = wxButton(id=wxID_WXPYWIZARDPAGE2BUTTON2, label='button2',
              name='button2', parent=self, pos=wxPoint(184, 224),
              size=wxSize(75, 23), style=0)

    def __init__(self, parent):
        self._init_ctrls(parent)

    _next = None
    def GetNext(self):
        return self._next

    _prev = None
    def GetPrev(self):
        return self._prev
