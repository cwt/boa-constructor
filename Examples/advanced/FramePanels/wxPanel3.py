#Boa:FramePanel:wxPanel3

from wxPython.wx import *

def create(parent):
    return wxPanel3(parent)

[wxID_WXPANEL3, wxID_WXPANEL3BUTTON1, wxID_WXPANEL3STATICTEXT1, 
] = map(lambda _init_ctrls: wxNewId(), range(3))

class wxPanel3(wxPanel):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxPanel.__init__(self, id=wxID_WXPANEL3, name='', parent=prnt,
              pos=wxPoint(198, 198), size=wxSize(200, 100), style=self.style)
        self._init_utils()
        self.SetClientSize(wxSize(192, 73))

        self.staticText1 = wxStaticText(id=wxID_WXPANEL3STATICTEXT1,
              label='wxPanel3', name='staticText1', parent=self, pos=wxPoint(8,
              8), size=wxSize(46, 13), style=0)

        self.button1 = wxButton(id=wxID_WXPANEL3BUTTON1, label='button1',
              name='button1', parent=self, pos=wxPoint(8, 32), size=wxSize(75,
              23), style=0)
        EVT_BUTTON(self.button1, wxID_WXPANEL3BUTTON1, self.OnButton1Button)

    def __init__(self, parent, id, pos, size, style, name):
        # style is added as a 'frame attribute' because many styles cannot be
        # changed after creation.
        self.style = wxTAB_TRAVERSAL
        self.style = style

        self._init_ctrls(parent)

        # This code must be added manually to override the design-time values
        # This is only needed for those FramePanels that are not directly
        # contained (when it's parent sizes it)
        self.SetPosition(pos)
        self.SetSize(size)

    def OnButton1Button(self, event):
        self.staticText1.SetLabel('Click!')
