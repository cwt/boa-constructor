#Boa:FramePanel:wxPanel1

from wxPython.wx import *

def create(parent):
    return wxPanel1(parent)

[wxID_WXPANEL1, wxID_WXPANEL1STATICTEXT1, wxID_WXPANEL1TEXTCTRL1] = map(lambda _init_ctrls: wxNewId(), range(3))

class wxPanel1(wxPanel):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxPanel.__init__(self, id = wxID_WXPANEL1, name = '', parent = prnt, pos = wxPoint(352, 271), size = wxSize(293, 224), style = wxTAB_TRAVERSAL)
        self._init_utils()

        self.staticText1 = wxStaticText(id = wxID_WXPANEL1STATICTEXT1, label = 'wxPanel1', name = 'staticText1', parent = self, pos = wxPoint(8, 16), size = wxSize(46, 13), style = 0)

        self.textCtrl1 = wxTextCtrl(id = wxID_WXPANEL1TEXTCTRL1, name = 'textCtrl1', parent = self, pos = wxPoint(8, 40), size = wxSize(100, 21), style = 0, value = 'textCtrl1')

    def __init__(self, parent, id, pos, size, style, name):
        self._init_ctrls(parent)
