#Boa:Frame:wxFrame2

from wxPython.wx import *
from wxPython.help import *

def create(parent):
    return wxFrame2(parent)

[wxID_WXFRAME2, wxID_WXFRAME2CONTEXTHELPBUTTON1, wxID_WXFRAME2PANEL1, 
 wxID_WXFRAME2TEXTCTRL1, 
] = map(lambda _init_ctrls: wxNewId(), range(4))

class wxFrame2(wxFrame):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxFrame.__init__(self, id=wxID_WXFRAME2, name='', parent=prnt,
              pos=wxPoint(176, 176), size=wxSize(266, 64),
              style=wxDEFAULT_FRAME_STYLE,
              title='Minimal context help example')
        self._init_utils()
        self.SetClientSize(wxSize(258, 37))

        self.panel1 = wxPanel(id=wxID_WXFRAME2PANEL1, name='panel1',
              parent=self, pos=wxPoint(0, 0), size=wxSize(258, 37),
              style=wxTAB_TRAVERSAL)

        self.textCtrl1 = wxTextCtrl(id=wxID_WXFRAME2TEXTCTRL1, name='textCtrl1',
              parent=self.panel1, pos=wxPoint(8, 8), size=wxSize(192, 21),
              style=0, value='textCtrl1')
        self.textCtrl1.SetHelpText('Here be expansive')
        self.textCtrl1.SetToolTipString('Here be spartan')

        self.contextHelpButton1 = wxContextHelpButton(parent=self.panel1,
              pos=wxPoint(224, 8), size=wxSize(20, 19), style=wxBU_AUTODRAW)

    def __init__(self, parent):
        self._init_ctrls(parent)


if __name__ == '__main__':
    app = wxPySimpleApp()
    # Note this help provider is needed and was added by hand
    provider = wxSimpleHelpProvider()
    wxHelpProvider_Set(provider)

    wxToolTip_Enable(true)
    frame = create(None)
    frame.Show(true)

    app.MainLoop()
