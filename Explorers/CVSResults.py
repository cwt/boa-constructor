#Boa:Dialog:CVSResultsDlg

from wxPython.wx import *

def create(parent):
    return CVSResultsDlg(parent)

[wxID_CVSRESULTSDLGTEXTCTRL1, wxID_CVSRESULTSDLGBUTTON3, wxID_CVSRESULTSDLGBUTTON1, wxID_CVSRESULTSDLGBUTTON2, wxID_CVSRESULTSDLG] = map(lambda _init_ctrls: wxNewId(), range(5))

class CVSResultsDlg(wxDialog):
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxDialog.__init__(self, size = wxSize(488, 323), id = wxID_CVSRESULTSDLG, title = 'CVS Results', parent = prnt, name = 'CVSResultsDlg', style = wxDEFAULT_DIALOG_STYLE, pos = wxPoint(138, 124))
        self._init_utils()

        self.textCtrl1 = wxTextCtrl(size = wxSize(480, 256), value = 'textCtrl1', pos = wxPoint(0, 0), parent = self, name = 'textCtrl1', style = 0, id = wxID_CVSRESULTSDLGTEXTCTRL1)

        self.button1 = wxButton(label = 'Close', id = wxID_CVSRESULTSDLGBUTTON1, parent = self, name = 'button1', size = wxSize(72, 24), style = 0, pos = wxPoint(176, 264))

        self.button2 = wxButton(label = 'Copy', id = wxID_CVSRESULTSDLGBUTTON2, parent = self, name = 'button2', size = wxSize(72, 24), style = 0, pos = wxPoint(256, 264))

        self.button3 = wxButton(label = 'Decorate open modules', id = wxID_CVSRESULTSDLGBUTTON3, parent = self, name = 'button3', size = wxSize(136, 24), style = 0, pos = wxPoint(336, 264))

    def __init__(self, parent):
        self._init_ctrls(parent)
