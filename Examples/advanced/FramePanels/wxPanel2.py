#Boa:FramePanel:wxPanel2

from wxPython.wx import *

def create(parent):
    return wxPanel2(parent)

[wxID_WXPANEL2, wxID_WXPANEL2CHECKBOX1, wxID_WXPANEL2STATICTEXT1, 
] = map(lambda _init_ctrls: wxNewId(), range(3))

class wxPanel2(wxPanel):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxPanel.__init__(self, id=wxID_WXPANEL2, name='', parent=prnt,
              pos=wxPoint(356, 242), size=wxSize(331, 263),
              style=wxTAB_TRAVERSAL)
        self._init_utils()
        self.SetClientSize(wxSize(323, 236))

        self.staticText1 = wxStaticText(id=wxID_WXPANEL2STATICTEXT1,
              label='wxPanel2', name='staticText1', parent=self, pos=wxPoint(16,
              16), size=wxSize(46, 13), style=0)

        self.checkBox1 = wxCheckBox(id=wxID_WXPANEL2CHECKBOX1,
              label='checkBox1', name='checkBox1', parent=self, pos=wxPoint(16,
              40), size=wxSize(73, 13), style=0)

    def __init__(self, parent, id, pos, size, style, name):
        self._init_ctrls(parent)
