#Boa:PyWizardPage:wxPyWizardPage1

from wxPython.wx import *
from wxPython.wizard import *

[wxID_WXPYWIZARDPAGE1, wxID_WXPYWIZARDPAGE1BUTTON1, 
 wxID_WXPYWIZARDPAGE1BUTTON2, wxID_WXPYWIZARDPAGE1STATICTEXT1, 
] = map(lambda _init_ctrls: wxNewId(), range(4))

class wxPyWizardPage1(wxPyWizardPage):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxPyWizardPage.__init__(self, bitmap=wxNullBitmap, parent=prnt,
              resource='')

        self.staticText1 = wxStaticText(id=wxID_WXPYWIZARDPAGE1STATICTEXT1,
              label='PyWizardPage1', name='staticText1', parent=self,
              pos=wxPoint(8, 8), size=wxSize(76, 13), style=0)

        self.button1 = wxButton(id=wxID_WXPYWIZARDPAGE1BUTTON1, label='button1',
              name='button1', parent=self, pos=wxPoint(8, 32), size=wxSize(75,
              23), style=0)
        EVT_BUTTON(self.button1, wxID_WXPYWIZARDPAGE1BUTTON1,
              self.OnButton1Button)

        self.button2 = wxButton(id=wxID_WXPYWIZARDPAGE1BUTTON2, label='button2',
              name='button2', parent=self, pos=wxPoint(400, 88), size=wxSize(75,
              23), style=0)

    def __init__(self, parent):
        self._init_ctrls(parent)

    _next = None
    def GetNext(self):
        return self._next
    def SetNext(self, value):
        self._next = value
    Next = property(GetNext, SetNext)

    _prev = None
    def GetPrev(self):
        return self._prev
    def SetPrev(self, value):
        self._prev = value
    Prev = property(GetPrev, SetPrev)

    def OnButton1Button(self, event):
        self.staticText1.SetLabel(`self.GetSize()`)
