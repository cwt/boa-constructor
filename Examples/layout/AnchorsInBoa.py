#Boa:Frame:wxFrame1

from wxPython.wx import *
from wxPython.lib.anchors import LayoutAnchors

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1, wxID_WXFRAME1BUTTON1, wxID_WXFRAME1BUTTON2, wxID_WXFRAME1STATICTEXT1, wxID_WXFRAME1TEXTCTRL1] = map(lambda _init_ctrls: wxNewId(), range(5))

class wxFrame1(wxFrame):
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxFrame.__init__(self, id = wxID_WXFRAME1, name = '', parent = prnt, pos = wxPoint(173, 135), size = wxSize(417, 149), style = wxDEFAULT_FRAME_STYLE, title = 'wxFrame1')
        self._init_utils()
        self.SetAutoLayout(true)

        self.staticText1 = wxStaticText(id = wxID_WXFRAME1STATICTEXT1, label = 'staticText1', name = 'staticText1', parent = self, pos = wxPoint(23, 25), size = wxSize(52, 13), style = 0)

        self.textCtrl1 = wxTextCtrl(id = wxID_WXFRAME1TEXTCTRL1, name = 'textCtrl1', parent = self, pos = wxPoint(96, 25), size = wxSize(288, 23), style = 0, value = 'textCtrl1')
        self.textCtrl1.SetConstraints(LayoutAnchors(self.textCtrl1, true, true, true, true))

        self.button1 = wxButton(id = wxID_WXFRAME1BUTTON1, label = 'button1', name = 'button1', parent = self, pos = wxPoint(216, 72), size = wxSize(72, 24), style = 0)
        self.button1.SetConstraints(LayoutAnchors(self.button1, false, false, true, true))

        self.button2 = wxButton(id = wxID_WXFRAME1BUTTON2, label = 'button2', name = 'button2', parent = self, pos = wxPoint(312, 72), size = wxSize(72, 24), style = 0)
        self.button2.SetConstraints(LayoutAnchors(self.button2, false, false, true, true))

    def __init__(self, parent):
        self._init_ctrls(parent)


if __name__ == '__main__':
    app = wxPySimpleApp()
    frame = create(None)
    frame.Show(true)
    app.MainLoop()
