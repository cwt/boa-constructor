#Boa:Frame:AttrMixinFrame

""" Example module which demonstrates the use of Attribute Mixin classes.

Attribute Mixin classes can be used to centralise attribute declarations
that can be shared between frames.

The mixin class name must end with the postfix _AttrMixin.

"""

from wxPython.wx import *

# Note: The AttrMixin class must be imported in this form and it's module must
#       be in the same directory as the frame module
from AttrMixins import Test_AttrMixin

def create(parent):
    return AttrMixinFrame(parent)

[wxID_ATTRMIXINFRAME, wxID_ATTRMIXINFRAMEBUTTON1] = map(lambda _init_ctrls: wxNewId(), range(2))

# Note: Inherits from the AttrMixin class after wxFrame
class AttrMixinFrame(wxFrame, Test_AttrMixin):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxFrame.__init__(self, id = wxID_ATTRMIXINFRAME, name = 'AttrMixinFrame', parent = prnt, pos = wxPoint(352, 222), size = wxSize(201, 104), style = wxDEFAULT_FRAME_STYLE, title = self.frameTitle)
        self._init_utils()
        self.SetClientSize(wxSize(193, 77))

        self.button1 = wxButton(id = wxID_ATTRMIXINFRAMEBUTTON1, label = self.buttonLabel, name = 'button1', parent = self, pos = wxPoint(0, 0), size = wxSize(193, 77), style = 0)

    def __init__(self, parent):
        # Note: Call inherited mixin constructor before _init_ctrls
        Test_AttrMixin.__init__(self)

        self._init_ctrls(parent)


if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    frame = create(None)
    frame.Show();frame.Hide();frame.Show() #workaround for running in wxProcess
    app.MainLoop()
