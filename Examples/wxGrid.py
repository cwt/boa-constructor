#Boa:Frame:wxFrame1

from wxPython.wx import *
from wxPython.grid import *

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1, wxID_WXFRAME1GRID1,
] = map(lambda _init_ctrls: wxNewId(), range(2))

class wxFrame1(wxFrame):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxFrame.__init__(self, id=wxID_WXFRAME1, name='', parent=prnt,
              pos=wxPoint(318, 214), size=wxSize(432, 242),
              style=wxDEFAULT_FRAME_STYLE, title='wxFrame1')
        self._init_utils()
        self.SetClientSize(wxSize(424, 215))

        self.grid1 = wxGrid(id=wxID_WXFRAME1GRID1, name='grid1', parent=self,
              pos=wxPoint(0, 0), size=wxSize(424, 215), style=0)
        self.grid1.EnableGridLines(true)

    def __init__(self, parent):
        self._init_ctrls(parent)

        # Either CreateGrid or SetTable must be manually added in your code
        # before you populate the grid
        self.grid1.CreateGrid(3, 3)


if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    frame = create(None)
    frame.Show()
    app.MainLoop()
