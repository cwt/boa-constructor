#Boa:Frame:wxFrame1

from wxPython.wx import *

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1STATICTEXT1, wxID_WXFRAME1TEXTCTRL1, wxID_WXFRAME1BUTTON1, wxID_WXFRAME1BUTTON2, wxID_WXFRAME1] = map(lambda _init_ctrls: wxNewId(), range(5))

class wxFrame1(wxFrame):
    def _init_coll_textCtrl1_Constraints(self, parent):
        item = wxLayoutConstraints()

        item.left.Set(rel = wxAsIs, otherWin = None, value = 0, margin = 0, otherEdge = wxLeft)
        item.right.Set(rel = wxLeftOf, otherWin = self, value = 0, margin = 24, otherEdge = wxRight)
        item.top.Set(rel = wxAsIs, otherWin = None, value = 0, margin = 0, otherEdge = wxLeft)
        item.bottom.Set(rel = wxBelow, otherWin = self, value = 0, margin = 72, otherEdge = wxBottom)

        return item

    def _init_coll_button2_Constraints(self, parent):
        item = wxLayoutConstraints()

        item.right.Set(rel = wxLeftOf, value = 0, otherWin = self, margin = 112, otherEdge = wxRight)
        item.bottom.Set(rel = wxBelow, value = 0, otherWin = self, margin = 24, otherEdge = wxBottom)
        item.width.Set(rel = wxAsIs, value = 0, otherWin = None, margin = 0, otherEdge = 0)
        item.height.Set(rel = wxAsIs, value = 0, otherWin = None, margin = 0, otherEdge = 0)

        return item

    def _init_coll_button1_Constraints(self, parent):
        item = wxLayoutConstraints()

        item.right.Set(rel = wxLeftOf, value = 0, otherWin = self, margin = 24, otherEdge = wxRight)
        item.bottom.Set(rel = wxBelow, value = 0, otherWin = self, margin = 24, otherEdge = wxBottom)
        item.width.Set(rel = wxAsIs, value = 0, otherWin = None, margin = 0, otherEdge = 0)
        item.height.Set(rel = wxAsIs, value = 0, otherWin = None, margin = 0, otherEdge = 0)

        return item

    def _init_utils(self): 
        pass

    def _init_ctrls(self, prnt): 
        wxFrame.__init__(self, size = wxSize(418, 149), id = wxID_WXFRAME1, title = 'wxFrame1', parent = prnt, name = '', style = wxDEFAULT_FRAME_STYLE, pos = wxPoint(173, 135))
        self._init_utils()
        self.SetAutoLayout(true)

        self.staticText1 = wxStaticText(label = 'staticText1', id = wxID_WXFRAME1STATICTEXT1, parent = self, name = 'staticText1', size = wxSize(52, 13), style = 0, pos = wxPoint(23, 25))

        self.textCtrl1 = wxTextCtrl(size = wxSize(288, 23), value = 'textCtrl1', pos = wxPoint(96, 25), parent = self, name = 'textCtrl1', style = 0, id = wxID_WXFRAME1TEXTCTRL1)
        self.textCtrl1.SetConstraints(self._init_coll_textCtrl1_Constraints(self.textCtrl1))

        self.button1 = wxButton(label = 'button2', id = wxID_WXFRAME1BUTTON1, parent = self, name = 'button1', size = wxSize(73, 26), style = 0, pos = wxPoint(313, 72))
        self.button1.SetConstraints(self._init_coll_button1_Constraints(self.button1))

        self.button2 = wxButton(label = 'button1', id = wxID_WXFRAME1BUTTON2, parent = self, name = 'button2', size = wxSize(72, 26), style = 0, pos = wxPoint(226, 72))
        self.button2.SetConstraints(self._init_coll_button2_Constraints(self.button2))

    def __init__(self, parent): 
        self._init_ctrls(parent)

if __name__ == '__main__':
    app = wxPySimpleApp()
    frame = create(None)
    frame.Show(true)
    app.MainLoop()