#Boa:Frame:wxFrame2

from wxPython.wx import *

def create(parent):
    return wxFrame2(parent)

[wxID_WXFRAME2] = map(lambda _init_ctrls: wxNewId(), range(1))

class wxFrame2(wxFrame):
    """ A reference to this frame is kept in frame1 therefor we have to
        stop the frame from being destroyed when it is closed. This is done
        by connecting to the close event and hiding the form """
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxFrame.__init__(self, id=wxID_WXFRAME2, name='', parent=prnt,
              pos=wxPoint(198, 198), size=wxSize(342, 146),
              style=wxDEFAULT_FRAME_STYLE, title='wxFrame2')
        self._init_utils()
        self.SetClientSize(wxSize(334, 119))
        EVT_CLOSE(self, self.OnWxframe2Close)

    def __init__(self, parent):
        self._init_ctrls(parent)

    def OnWxframe2Close(self, event):
        self.Show(false)
