#Boa:Frame:wxFrame1

""" This example demonstrates how to load .xrc files created e.g. by XRCed.

Support only allows creating/linking the components. The contents of the
xcr file is not displayed at design-time and can certainly not be managed in 
the Designer.

Note that the XRCSupport plug-in must be installed. """ 

from wxPython.wx import *
from wxPython.xrc import *

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1, wxID_WXFRAME1BOAXRCPANEL, wxID_WXFRAME1BUTTON1, wxID_WXFRAME1PANEL1] = map(lambda _init_ctrls: wxNewId(), range(4))

class wxFrame1(wxFrame):
    def _init_utils(self):
        # generated method, don't edit
        self.xmlResource1 = wxXmlResource(filemask = 'Input.xrc')

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxFrame.__init__(self, id = wxID_WXFRAME1, name = '', parent = prnt, pos = wxPoint(250, 248), size = wxSize(240, 165), style = wxDEFAULT_FRAME_STYLE, title = 'wxFrame1')
        self._init_utils()
        self.SetClientSize(wxSize(232, 138))

        self.panel1 = wxPanel(id = wxID_WXFRAME1PANEL1, name = 'panel1', parent = self, pos = wxPoint(0, 0), size = wxSize(232, 138), style = wxTAB_TRAVERSAL)

        self.boaXrcPanel = self.xmlResource1.LoadPanel(name = 'boaXrcPanel', parent = self.panel1)
        self.boaXrcPanel.SetSize(wxSize(216, 88))
        self.boaXrcPanel.SetPosition(wxPoint(8, 8))

        self.button1 = wxButton(id = wxID_WXFRAME1BUTTON1, label = 'OK', name = 'button1', parent = self.panel1, pos = wxPoint(144, 104), size = wxSize(75, 23), style = 0)
        EVT_BUTTON(self.button1, wxID_WXFRAME1BUTTON1, self.OnButton1Button)

    def __init__(self, parent):
        self._init_ctrls(parent)

        # to reference an xrc control
        self.xrcLabel = XRCCTRL(self, 'inputLbl')
        self.xrcTextCtrl = XRCCTRL(self, 'inputCtrl')
        self.xrcCheck = XRCCTRL(self, 'inputCheck')
        # to bind an event to an xrc control
        EVT_CHECKBOX(self, self.xrcCheck.GetId(), self.OnCheckbox)

    def OnButton1Button(self, event):
        print 'Entered %s'%self.xrcTextCtrl.GetValue()
        self.Close()

    def OnCheckbox(self, event):
        print 'Checkbox clicked'


if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    frame = create(None)
    frame.Show()
    app.MainLoop()
