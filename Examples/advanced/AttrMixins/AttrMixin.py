#Boa:Frame:wxFrame1

""" Example module which demonstrates the use of Attribute Mixin classes.

Attribute Mixin classes can be used to centralise attribute declarations
that can be shared between frames.

The mixin class name must end with the postfix _AttrMixin.

"""

from wxPython.wx import *

from AttrMixins import Test_AttrMixin

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1] = map(lambda _init_ctrls: wxNewId(), range(1))

class wxFrame1(wxFrame, Test_AttrMixin):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxFrame.__init__(self, id = wxID_WXFRAME1, name = '', parent = prnt, pos = wxPoint(132, 132), size = wxSize(960, 750), style = wxDEFAULT_FRAME_STYLE, title = self.name2)
        self._init_utils()
        self.SetClientSize(wxSize(952, 723))

    def __init__(self, parent):
        Test_AttrMixin.__init__(self)
        self._init_ctrls(parent)
