#Boa:Frame:wxFrame3

from wxPython.wx import *

def create(parent):
    return wxFrame3(parent)

[wxID_WXFRAME3] = map(lambda _init_ctrls: wxNewId(), range(1))

class wxFrame3(wxFrame):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxFrame.__init__(self, id=wxID_WXFRAME3, name='', parent=prnt,
              pos=wxPoint(176, 176), size=wxSize(960, 692),
              style=wxDEFAULT_FRAME_STYLE, title='wxFrame3')
        self._init_utils()
        self.SetClientSize(wxSize(952, 665))

    def __init__(self, parent):
        self._init_ctrls(parent)
