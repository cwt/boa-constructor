#Boa:Frame:wxFrame1

from wxPython.wx import *

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1STATICTEXT1, wxID_WXFRAME1TEXTCTRL1, wxID_WXFRAME1BUTTON1, wxID_WXFRAME1BUTTON2, wxID_WXFRAME1] = map(lambda _init_ctrls: wxNewId(), range(5))

class wxFrame1(wxFrame):
    def _init_utils(self): 
        pass

    def _init_ctrls(self, prnt): 
        wxFrame.__init__(self, size = wxSize(417, 149), id = wxID_WXFRAME1, title = 'wxFrame1', parent = prnt, name = '', style = wxDEFAULT_FRAME_STYLE, pos = wxPoint(173, 135))
        self._init_utils()

        self.staticText1 = wxStaticText(label = 'staticText1', id = wxID_WXFRAME1STATICTEXT1, parent = self, name = 'staticText1', size = wxSize(52, 13), style = 0, pos = wxPoint(23, 25))

        self.textCtrl1 = wxTextCtrl(size = wxSize(288, 23), value = 'textCtrl1', pos = wxPoint(96, 25), parent = self, name = 'textCtrl1', style = 0, id = wxID_WXFRAME1TEXTCTRL1)

        self.button1 = wxButton(label = 'button1', id = wxID_WXFRAME1BUTTON1, parent = self, name = 'button1', size = wxSize(72, 24), style = 0, pos = wxPoint(216, 72))

        self.button2 = wxButton(label = 'button2', id = wxID_WXFRAME1BUTTON2, parent = self, name = 'button2', size = wxSize(72, 24), style = 0, pos = wxPoint(312, 72))

    def __init__(self, parent): 
        self._init_ctrls(parent)

        self.box1 = wxBoxSizer(wxVERTICAL)

        self.box2 = wxBoxSizer(wxHORIZONTAL)
        self.box2.Add(self.staticText1, 0, wxALL, 10)
        self.box2.Add(self.textCtrl1, 1, wxALL | wxEXPAND, 10)

        self.box3 = wxBoxSizer(wxHORIZONTAL)
        self.box3.Add(0, 1, wxEXPAND)
        self.box3.Add(self.button1, 0, wxALIGN_RIGHT | wxALL, 10)
        self.box3.Add(self.button2, 0, wxALIGN_RIGHT | wxALL, 10)

        self.box1.Add(self.box2, 1, wxEXPAND)
        self.box1.Add(self.box3, 0, wxEXPAND)
        
        self.SetAutoLayout(true)
        self.SetSizer(self.box1)


if __name__ == '__main__':
    app = wxPySimpleApp()
    frame = create(None)
    frame.Show(true)
    app.MainLoop()