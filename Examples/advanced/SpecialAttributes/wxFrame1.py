#Boa:Frame:wxFrame1

from wxPython.wx import *

def create(parent, title):
    return wxFrame1(parent, title)

[wxID_WXFRAME1, wxID_WXFRAME1BUTTON1, wxID_WXFRAME1SPLITTERWINDOW1, wxID_WXFRAME1TEXTCTRL1, wxID_WXFRAME1TEXTCTRL2, wxID_WXFRAME1TEXTCTRL3] = map(lambda _init_ctrls: wxNewId(), range(6))

class wxFrame1(wxFrame):
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxFrame.__init__(self, id = wxID_WXFRAME1, name = '', parent = prnt, pos = wxPoint(286, 235), size = wxSize(307, 300), style = wxDEFAULT_FRAME_STYLE, title = self.frameTitle)
        self._init_utils()
        self.SetClientSize(wxSize(299, 273))

        self.button1 = wxButton(id = wxID_WXFRAME1BUTTON1, label = self.buttonLabel, name = 'button1', parent = self, pos = wxPoint(96, 104), size = wxSize(104, 24), style = 0)
        EVT_BUTTON(self.button1, wxID_WXFRAME1BUTTON1, self.OnButton1Button)

        self.textCtrl1 = wxTextCtrl(id = wxID_WXFRAME1TEXTCTRL1, name = 'textCtrl1', parent = self, pos = wxPoint(8, 8), size = wxSize(280, 72), style = 0, value = 'textCtrl1')

        self.splitterWindow1 = wxSplitterWindow(id = wxID_WXFRAME1SPLITTERWINDOW1, name = 'splitterWindow1', parent = self, point = wxPoint(8, 144), size = wxSize(280, 120), style = wxSP_3D)

        self.textCtrl2 = wxTextCtrl(id = wxID_WXFRAME1TEXTCTRL2, name = 'textCtrl2', parent = self.splitterWindow1, pos = wxPoint(2, 2), size = wxSize(138, 116), style = 0, value = 'textCtrl2')

        self.textCtrl3 = wxTextCtrl(id = wxID_WXFRAME1TEXTCTRL3, name = 'textCtrl3', parent = self.splitterWindow1, pos = wxPoint(147, 2), size = wxSize(131, 116), style = 0, value = 'textCtrl3')
        self.splitterWindow1.SplitVertically(self.textCtrl2, self.textCtrl3, self.splitSize)

    def __init__(self, parent, frameTitle):
        self.frameTitle = 'Frame Caption'
        self.frameTitle = frameTitle
        self.buttonLabel = 'Press Me!'
        self.splitSize = 150
        self._init_ctrls(parent)

    def OnButton1Button(self, event):
        self.Close()


if __name__ == '__main__':
    app = wxPySimpleApp()
    frame = create(None, 'Hello World')
    frame.Show(true)
    app.MainLoop()
