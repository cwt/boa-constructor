#Boa:Frame:wxFrame1

from wxPython.wx import *

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1, wxID_WXFRAME1PANEL1, wxID_WXFRAME1SASHLAYOUTWINDOW1, 
 wxID_WXFRAME1SASHLAYOUTWINDOW2, wxID_WXFRAME1SASHLAYOUTWINDOW3, 
 wxID_WXFRAME1SASHLAYOUTWINDOW4, wxID_WXFRAME1STATICTEXT1, 
 wxID_WXFRAME1TEXTCTRL1, wxID_WXFRAME1TEXTCTRL2, 
] = map(lambda _init_ctrls: wxNewId(), range(9))

class wxFrame1(wxFrame):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxFrame.__init__(self, id=wxID_WXFRAME1, name='', parent=prnt,
              pos=wxPoint(327, 136), size=wxSize(518, 376),
              style=wxDEFAULT_FRAME_STYLE, title='Sash layout')
        self._init_utils()
        self.SetClientSize(wxSize(510, 349))
        EVT_SIZE(self, self.OnWxframe1Size)

        self.panel1 = wxPanel(id=wxID_WXFRAME1PANEL1, name='panel1',
              parent=self, pos=wxPoint(248, 50), size=wxSize(262, 234),
              style=wxTAB_TRAVERSAL)

        self.sashLayoutWindow1 = wxSashLayoutWindow(id=wxID_WXFRAME1SASHLAYOUTWINDOW1,
              name='sashLayoutWindow1', parent=self, pos=wxPoint(0, 0),
              size=wxSize(510, 50), style=wxCLIP_CHILDREN | wxSW_3D)
        self.sashLayoutWindow1.SetBackgroundColour(wxColour(255, 0, 0))
        self.sashLayoutWindow1.SetOrientation(wxLAYOUT_HORIZONTAL)
        self.sashLayoutWindow1.SetAlignment(wxLAYOUT_TOP)
        self.sashLayoutWindow1.SetSashVisible(wxSASH_BOTTOM, true)
        self.sashLayoutWindow1.SetDefaultSize(wxSize(510, 50))
        EVT_SASH_DRAGGED(self.sashLayoutWindow1, wxID_WXFRAME1SASHLAYOUTWINDOW1,
              self.OnSashlayoutwindow1SashDragged)

        self.sashLayoutWindow4 = wxSashLayoutWindow(id=wxID_WXFRAME1SASHLAYOUTWINDOW4,
              name='sashLayoutWindow4', parent=self, pos=wxPoint(0, 284),
              size=wxSize(510, 65), style=wxCLIP_CHILDREN | wxSW_3D)
        self.sashLayoutWindow4.SetBackgroundColour(wxColour(0, 0, 255))
        self.sashLayoutWindow4.SetAlignment(wxLAYOUT_BOTTOM)
        self.sashLayoutWindow4.SetSashVisible(wxSASH_TOP, true)
        self.sashLayoutWindow4.SetOrientation(wxLAYOUT_HORIZONTAL)
        self.sashLayoutWindow4.SetDefaultSize(wxSize(308, 65))
        self.sashLayoutWindow4.SetExtraBorderSize(10)
        EVT_SASH_DRAGGED(self.sashLayoutWindow4, wxID_WXFRAME1SASHLAYOUTWINDOW4,
              self.OnSashlayoutwindow4SashDragged)

        self.sashLayoutWindow2 = wxSashLayoutWindow(id=wxID_WXFRAME1SASHLAYOUTWINDOW2,
              name='sashLayoutWindow2', parent=self, pos=wxPoint(0, 50),
              size=wxSize(112, 234), style=wxCLIP_CHILDREN | wxSW_3D)
        self.sashLayoutWindow2.SetBackgroundColour(wxColour(128, 255, 0))
        self.sashLayoutWindow2.SetExtraBorderSize(20)
        self.sashLayoutWindow2.SetAlignment(wxLAYOUT_LEFT)
        self.sashLayoutWindow2.SetOrientation(wxLAYOUT_VERTICAL)
        self.sashLayoutWindow2.SetSashVisible(wxSASH_RIGHT, true)
        self.sashLayoutWindow2.SetDefaultSize(wxSize(112, 113))
        EVT_SASH_DRAGGED(self.sashLayoutWindow2, wxID_WXFRAME1SASHLAYOUTWINDOW2,
              self.OnSashlayoutwindow2SashDragged)

        self.sashLayoutWindow3 = wxSashLayoutWindow(id=wxID_WXFRAME1SASHLAYOUTWINDOW3,
              name='sashLayoutWindow3', parent=self, pos=wxPoint(112, 50),
              size=wxSize(136, 234), style=wxCLIP_CHILDREN | wxSW_3D)
        self.sashLayoutWindow3.SetBackgroundColour(wxColour(0, 255, 255))
        self.sashLayoutWindow3.SetAlignment(wxLAYOUT_LEFT)
        self.sashLayoutWindow3.SetOrientation(wxLAYOUT_VERTICAL)
        self.sashLayoutWindow3.SetSashVisible(wxSASH_RIGHT, true)
        self.sashLayoutWindow3.SetDefaultSize(wxSize(136, 234))
        EVT_SASH_DRAGGED(self.sashLayoutWindow3, wxID_WXFRAME1SASHLAYOUTWINDOW3,
              self.OnSashlayoutwindow3SashDragged)

        self.textCtrl1 = wxTextCtrl(id=wxID_WXFRAME1TEXTCTRL1, name='textCtrl1',
              parent=self.sashLayoutWindow2, pos=wxPoint(20, 20),
              size=wxSize(69, 194), style=0, value='textCtrl1')

        self.staticText1 = wxStaticText(id=wxID_WXFRAME1STATICTEXT1,
              label='staticText1', name='staticText1', parent=self.panel1,
              pos=wxPoint(16, 16), size=wxSize(52, 13), style=0)

        self.textCtrl2 = wxTextCtrl(id=wxID_WXFRAME1TEXTCTRL2, name='textCtrl2',
              parent=self.sashLayoutWindow4, pos=wxPoint(10, 13),
              size=wxSize(490, 42), style=0, value='textCtrl2')

    def __init__(self, parent):
        self._init_ctrls(parent)

    def checkStatusRange(self, event):
        return event.GetDragStatus() != wxSASH_STATUS_OUT_OF_RANGE

    def doLayout(self):
        wxLayoutAlgorithm().LayoutWindow(self, self.panel1)
        self.panel1.Refresh()

    def OnWxframe1Size(self, event):
        self.doLayout()

    def OnSashlayoutwindow1SashDragged(self, event):
        if self.checkStatusRange(event):
            self.sashLayoutWindow1.SetDefaultSize(wxSize(1000, event.GetDragRect().height))
            self.doLayout()

    def OnSashlayoutwindow2SashDragged(self, event):
        if self.checkStatusRange(event):
            self.sashLayoutWindow2.SetDefaultSize(wxSize(event.GetDragRect().width, 1000))
            self.doLayout()

    def OnSashlayoutwindow3SashDragged(self, event):
        if self.checkStatusRange(event):
            self.sashLayoutWindow3.SetDefaultSize(wxSize(event.GetDragRect().width, 1000))
            self.doLayout()

    def OnSashlayoutwindow4SashDragged(self, event):
        if self.checkStatusRange(event):
            self.sashLayoutWindow4.SetDefaultSize(wxSize(1000, event.GetDragRect().height))
            self.doLayout()


if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    frame = create(None)
    frame.Show()
    app.MainLoop()
