#Boa:MDIChild:wxMDIChildFrame1

from wxPython.wx import *

def create(parent):
    return wxMDIChildFrame1(parent)

[wxID_WXMDICHILDFRAME1, wxID_WXMDICHILDFRAME1BUTTON1, wxID_WXMDICHILDFRAME1RADIOBUTTON1] = map(lambda _init_ctrls: wxNewId(), range(3))

class wxMDIChildFrame1(wxMDIChildFrame):
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxMDIChildFrame.__init__(self, id = wxID_WXMDICHILDFRAME1, name = '', parent = prnt, pos = wxPoint(38, 49), size = wxSize(326, 158), style = wxDEFAULT_FRAME_STYLE, title = 'wxMDIChildFrame1')
        self._init_utils()

        self.button1 = wxButton(id = wxID_WXMDICHILDFRAME1BUTTON1, label = 'button1', name = 'button1', parent = self, pos = wxPoint(8, 8), size = wxSize(75, 23), style = 0)

        self.radioButton1 = wxRadioButton(id = wxID_WXMDICHILDFRAME1RADIOBUTTON1, label = 'radioButton1', name = 'radioButton1', parent = self, pos = wxPoint(8, 40), size = wxSize(80, 20), style = 0)

    def __init__(self, parent):
        self._init_ctrls(parent)
