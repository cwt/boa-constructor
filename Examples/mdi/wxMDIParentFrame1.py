#Boa:MDIParent:wxMDIParentFrame1

from wxPython.wx import *
from wxPython.lib.anchors import LayoutAnchors

import wxMDIChildFrame1

def create(parent):
    return wxMDIParentFrame1(parent)

[wxID_WXMDIPARENTFRAME1, wxID_WXMDIPARENTFRAME1SASHLAYOUTWINDOW1, wxID_WXMDIPARENTFRAME1TREECTRL1] = map(lambda _init_ctrls: wxNewId(), range(3))

[wxID_WXMDIPARENTFRAME1MENU1ITEMS0] = map(lambda _init_coll_menu1_Items: wxNewId(), range(1))

class wxMDIParentFrame1(wxMDIParentFrame):
    def _init_coll_menuBar1_Menus(self, parent):

        parent.Append(menu = self.menu1, title = '&File')

    def _init_coll_menu1_Items(self, parent):

        parent.Append(checkable = false, helpString = 'Items0', id = wxID_WXMDIPARENTFRAME1MENU1ITEMS0, item = 'New child window')
        EVT_MENU(self, wxID_WXMDIPARENTFRAME1MENU1ITEMS0, self.OnMenu1items0Menu)

    def _init_utils(self):
        self.menuBar1 = wxMenuBar()

        self.menu1 = wxMenu(title = '')
        self._init_coll_menu1_Items(self.menu1)

        self._init_coll_menuBar1_Menus(self.menuBar1)

    def _init_ctrls(self, prnt):
        wxMDIParentFrame.__init__(self, id = wxID_WXMDIPARENTFRAME1, name = '', parent = prnt, pos = wxPoint(397, 380), size = wxSize(544, 318), style = wxDEFAULT_FRAME_STYLE | wxVSCROLL | wxHSCROLL, title = 'wxMDIParentFrame1')
        self._init_utils()
        self.SetMenuBar(self.menuBar1)
        self.SetAutoLayout(true)
        EVT_SIZE(self, self.OnWxmdiparentframe1Size)

        self.sashLayoutWindow1 = wxSashLayoutWindow(id = wxID_WXMDIPARENTFRAME1SASHLAYOUTWINDOW1, name = 'sashLayoutWindow1', parent = self, pos = wxPoint(0, 0), size = wxSize(137, 272), style = wxCLIP_CHILDREN | wxSW_3D)
        self.sashLayoutWindow1.SetOrientation(wxLAYOUT_VERTICAL)
        self.sashLayoutWindow1.SetAlignment(wxLAYOUT_LEFT)
        self.sashLayoutWindow1.SetSashVisible(wxSASH_RIGHT, true)
        self.sashLayoutWindow1.SetDefaultSize(wxSize(137, 272))
        EVT_SASH_DRAGGED(self.sashLayoutWindow1, wxID_WXMDIPARENTFRAME1SASHLAYOUTWINDOW1, self.OnSashlayoutwindow1SashDragged)

        self.treeCtrl1 = wxTreeCtrl(id = wxID_WXMDIPARENTFRAME1TREECTRL1, name = 'treeCtrl1', parent = self.sashLayoutWindow1, pos = wxPoint(0, 0), size = wxSize(134, 272), style = wxTR_HAS_BUTTONS, validator = wxDefaultValidator)

    def __init__(self, parent):
        self._init_ctrls(parent)
        
        child1 = wxMDIChildFrame1.create(self)
        child1.Show(true)
        
    def OnMenu1items0Menu(self, event):
        wxMDIChildFrame1.create(self).Show(true)

    def OnWxmdiparentframe1Size(self, event):
        wxLayoutAlgorithm().LayoutMDIFrame(self)

    def OnSashlayoutwindow1SashDragged(self, event):
        if event.GetDragStatus() == wxSASH_STATUS_OUT_OF_RANGE:
            return

        eID = event.GetId()
        if eID == wxID_WXMDIPARENTFRAME1SASHLAYOUTWINDOW1:
            self.sashLayoutWindow1.SetDefaultSize(wxSize(event.GetDragRect().width, 0))

        wxLayoutAlgorithm().LayoutMDIFrame(self)
        self.GetClientWindow().Refresh()
