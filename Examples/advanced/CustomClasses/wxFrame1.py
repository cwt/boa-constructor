#Boa:Frame:wxFrame1

from wxPython.wx import *

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1, wxID_WXFRAME1TREECTRL1] = map(lambda _init_ctrls: wxNewId(), range(2))

class wxFrame1(wxFrame):
    _custom_classes = {'wxTreeCtrl': ['MyTreeCtrl']}
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxFrame.__init__(self, id = wxID_WXFRAME1, name = '', parent = prnt, pos = wxPoint(154, 154), size = wxSize(488, 258), style = wxDEFAULT_FRAME_STYLE, title = 'wxFrame1')
        self._init_utils()

        self.treeCtrl1 = MyTreeCtrl(id = wxID_WXFRAME1TREECTRL1, name = 'treeCtrl1', parent = self, pos = wxPoint(0, 0), size = wxSize(480, 231), style = wxTR_HAS_BUTTONS, validator = wxDefaultValidator)

    def __init__(self, parent):
        self._init_ctrls(parent)


class MyTreeCtrl(wxTreeCtrl):
    pass
