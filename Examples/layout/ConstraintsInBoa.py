#Boa:Frame:wxFrame1

from wxPython.wx import *

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1, wxID_WXFRAME1BUTTON1, wxID_WXFRAME1BUTTON2, wxID_WXFRAME1STATICTEXT1, wxID_WXFRAME1TEXTCTRL1] = map(lambda _init_ctrls: wxNewId(), range(5))

class wxFrame1(wxFrame):
    def _init_coll_button2_Constraints(self, parent):
        item = wxLayoutConstraints()

        item.right.Set(margin = 112, otherEdge = wxRight, otherWin = self, rel = wxLeftOf, value = 0)
        item.bottom.Set(margin = 24, otherEdge = wxBottom, otherWin = self, rel = wxBelow, value = 0)
        item.width.Set(margin = 0, otherEdge = 0, otherWin = None, rel = wxAsIs, value = 0)
        item.height.Set(margin = 0, otherEdge = 0, otherWin = None, rel = wxAsIs, value = 0)

        return item

    def _init_coll_button1_Constraints(self, parent):
        item = wxLayoutConstraints()

        item.right.Set(margin = 24, otherEdge = wxRight, otherWin = self, rel = wxLeftOf, value = 0)
        item.bottom.Set(margin = 24, otherEdge = wxBottom, otherWin = self, rel = wxBelow, value = 0)
        item.width.Set(margin = 0, otherEdge = 0, otherWin = None, rel = wxAsIs, value = 0)
        item.height.Set(margin = 0, otherEdge = 0, otherWin = None, rel = wxAsIs, value = 0)

        return item

    def _init_coll_textCtrl1_Constraints(self, parent):
        item = wxLayoutConstraints()

        item.left.Set(margin = 0, otherEdge = wxLeft, otherWin = None, rel = wxAsIs, value = 0)
        item.right.Set(margin = 24, otherEdge = wxRight, otherWin = self, rel = wxLeftOf, value = 0)
        item.top.Set(margin = 0, otherEdge = wxLeft, otherWin = None, rel = wxAsIs, value = 0)
        item.bottom.Set(margin = 72, otherEdge = wxBottom, otherWin = self, rel = wxBelow, value = 0)

        return item

    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxFrame.__init__(self, id = wxID_WXFRAME1, name = '', parent = prnt, pos = wxPoint(173, 135), size = wxSize(418, 149), style = wxDEFAULT_FRAME_STYLE, title = 'wxFrame1')
        self._init_utils()
        self.SetAutoLayout(true)

        self.staticText1 = wxStaticText(id = wxID_WXFRAME1STATICTEXT1, label = 'staticText1', name = 'staticText1', parent = self, pos = wxPoint(23, 25), size = wxSize(52, 13), style = 0)

        self.textCtrl1 = wxTextCtrl(id = wxID_WXFRAME1TEXTCTRL1, name = 'textCtrl1', parent = self, pos = wxPoint(96, 25), size = wxSize(290, 25), style = 0, value = 'textCtrl1')
        self.textCtrl1.SetConstraints(self._init_coll_textCtrl1_Constraints(self.textCtrl1))

        self.button1 = wxButton(id = wxID_WXFRAME1BUTTON1, label = 'button2', name = 'button1', parent = self, pos = wxPoint(313, 72), size = wxSize(73, 26), style = 0)
        self.button1.SetConstraints(self._init_coll_button1_Constraints(self.button1))

        self.button2 = wxButton(id = wxID_WXFRAME1BUTTON2, label = 'button1', name = 'button2', parent = self, pos = wxPoint(226, 72), size = wxSize(72, 26), style = 0)
        self.button2.SetConstraints(self._init_coll_button2_Constraints(self.button2))

    def __init__(self, parent):
        self._init_ctrls(parent)

if __name__ == '__main__':
    app = wxPySimpleApp()
    frame = create(None)
    frame.Show(true)
    app.MainLoop()
