#Boa:Frame:wxFrame3

from wxPython.wx import *

def create(parent):
    return wxFrame3(parent)

[wxID_WXFRAME3] = map(lambda _init_ctrls: wxNewId(), range(1))

class wxFrame3(wxFrame):
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxFrame.__init__(self, size = (-1, -1), id = wxID_WXFRAME3, pos = (-1, -1), title = 'wxFrame3', parent = prnt, name = '', style = wxDEFAULT_FRAME_STYLE)
        self._init_utils()

    def __init__(self, parent):
        self._init_ctrls(parent)
