#Boa:Frame:wxFrame1

from wxPython.wx import *

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1, wxID_WXFRAME1BUTTON1, wxID_WXFRAME1BUTTON2, 
 wxID_WXFRAME1STATICTEXT1, wxID_WXFRAME1TEXTCTRL1, 
] = map(lambda _init_ctrls: wxNewId(), range(5))

class wxFrame1(wxFrame):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxFrame.__init__(self, id=wxID_WXFRAME1, name='', parent=prnt,
              pos=wxPoint(173, 135), size=wxSize(417, 149),
              style=wxDEFAULT_FRAME_STYLE, title='wxFrame1')
        self._init_utils()
        self.SetClientSize(wxSize(409, 122))

        self.staticText1 = wxStaticText(id=wxID_WXFRAME1STATICTEXT1,
              label='staticText1', name='staticText1', parent=self,
              pos=wxPoint(23, 25), size=wxSize(52, 13), style=0)

        self.textCtrl1 = wxTextCtrl(id=wxID_WXFRAME1TEXTCTRL1, name='textCtrl1',
              parent=self, pos=wxPoint(96, 25), size=wxSize(288, 23), style=0,
              value='textCtrl1')

        self.button1 = wxButton(id=wxID_WXFRAME1BUTTON1, label='button1',
              name='button1', parent=self, pos=wxPoint(216, 72), size=wxSize(72,
              24), style=0)

        self.button2 = wxButton(id=wxID_WXFRAME1BUTTON2, label='button2',
              name='button2', parent=self, pos=wxPoint(312, 72), size=wxSize(72,
              24), style=0)

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
