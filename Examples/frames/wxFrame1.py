#Boa:Frame:wxFrame1

from wxPython.wx import *

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1, wxID_WXFRAME1BUTTON1, wxID_WXFRAME1BUTTON2,
] = map(lambda _init_ctrls: wxNewId(), range(3))

class wxFrame1(wxFrame):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxFrame.__init__(self, id=wxID_WXFRAME1, name='', parent=prnt,
              pos=wxPoint(299, 227), size=wxSize(370, 114),
              style=wxDEFAULT_FRAME_STYLE, title='wxFrame1')
        self._init_utils()
        self.SetClientSize(wxSize(362, 87))

        self.button1 = wxButton(id=wxID_WXFRAME1BUTTON1, label='Show Frame 2',
              name='button1', parent=self, pos=wxPoint(112, 16),
              size=wxSize(152, 23), style=0)
        EVT_BUTTON(self.button1, wxID_WXFRAME1BUTTON1, self.OnButton1Button)

        self.button2 = wxButton(id=wxID_WXFRAME1BUTTON2, label='Show Frame 3',
              name='button2', parent=self, pos=wxPoint(112, 48),
              size=wxSize(152, 23), style=0)
        EVT_BUTTON(self.button2, wxID_WXFRAME1BUTTON2, self.OnButton2Button)

    def __init__(self, parent):
        self._init_ctrls(parent)

        import wxFrame2
        self.frame2 = wxFrame2.create(self)

    def OnButton1Button(self, event):
        """ Example of a frame kept as a reference

        Note it was created in __init__
        """
        self.frame2.Show(true)

    def OnButton2Button(self, event):
        """ Example of a dynamic unreferenced frame """
        import wxFrame3
        wxFrame3.create(self).Show(true)
