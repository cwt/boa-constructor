#Boa:Dialog:NewPropDlg

from wxPython.wx import *

def create(parent):
    return NewPropDlg(parent)

[wxID_NEWPROPDLGPANEL1, wxID_NEWPROPDLGTCVALUE, wxID_NEWPROPDLGBUTTON1, wxID_NEWPROPDLGBUTTON2, wxID_NEWPROPDLGSTATICTEXT1, wxID_NEWPROPDLGSTATICTEXT3, wxID_NEWPROPDLGSTATICTEXT2, wxID_NEWPROPDLGTCPROPNAME, wxID_NEWPROPDLGCHTYPE, wxID_NEWPROPDLG] = map(lambda _init_ctrls: wxNewId(), range(10))

[wxID_NEWPROPDLGPANEL1, wxID_NEWPROPDLGTCVALUE, wxID_NEWPROPDLGSTATICTEXT1, wxID_NEWPROPDLGSTATICTEXT3, wxID_NEWPROPDLGSTATICTEXT2, wxID_NEWPROPDLGTCPROPNAME, wxID_NEWPROPDLGBTCANCEL, wxID_NEWPROPDLGCHTYPE, wxID_NEWPROPDLGBTOK, wxID_NEWPROPDLG] = map(lambda _init_ctrls: wxNewId(), range(10))

[wxID_NEWPROPDLGSTATICTEXT1, wxID_NEWPROPDLGSTATICTEXT3, wxID_NEWPROPDLGSTATICTEXT2, wxID_NEWPROPDLGTCPROPNAME, wxID_NEWPROPDLGPANEL1, wxID_NEWPROPDLGCHTYPE, wxID_NEWPROPDLGBTOK, wxID_NEWPROPDLGBTCANCEL, wxID_NEWPROPDLGTCVALUE, wxID_NEWPROPDLG] = map(lambda _init_ctrls: wxNewId(), range(10))

[wxID_NEWPROPDLGSTATICTEXT1, wxID_NEWPROPDLGCHTYPE, wxID_NEWPROPDLGSTATICTEXT2, wxID_NEWPROPDLGTCPROPNAME, wxID_NEWPROPDLGPANEL1, wxID_NEWPROPDLGSTATICTEXT3, wxID_NEWPROPDLGBTOK, wxID_NEWPROPDLGBTCANCEL, wxID_NEWPROPDLGTCVALUE, wxID_NEWPROPDLG] = map(lambda _init_ctrls: wxNewId(), range(10))

class NewPropDlg(wxDialog):
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxDialog.__init__(self, size = wxSize(221, 169), id = wxID_NEWPROPDLG, title = 'New property', parent = prnt, name = 'NewPropDlg', style = wxDEFAULT_DIALOG_STYLE, pos = wxPoint(359, 240))
        self._init_utils()

        self.panel1 = wxPanel(size = wxSize(216, 144), parent = self, id = wxID_NEWPROPDLGPANEL1, name = 'panel1', style = wxTAB_TRAVERSAL, pos = wxPoint(0, 0))

        self.staticText1 = wxStaticText(label = 'Name:', id = wxID_NEWPROPDLGSTATICTEXT1, parent = self.panel1, name = 'staticText1', size = wxSize(32, 16), style = 0, pos = wxPoint(8, 16))

        self.tcPropName = wxTextCtrl(size = wxSize(144, 24), value = '', pos = wxPoint(56, 8), parent = self.panel1, name = 'tcPropName', style = 0, id = wxID_NEWPROPDLGTCPROPNAME)

        self.staticText3 = wxStaticText(label = 'Value:', id = wxID_NEWPROPDLGSTATICTEXT3, parent = self.panel1, name = 'staticText3', size = wxSize(30, 13), style = 0, pos = wxPoint(8, 48))

        self.tcValue = wxTextCtrl(size = wxSize(144, 24), value = '', pos = wxPoint(56, 40), parent = self.panel1, name = 'tcValue', style = 0, id = wxID_NEWPROPDLGTCVALUE)

        self.staticText2 = wxStaticText(label = 'Type:', id = wxID_NEWPROPDLGSTATICTEXT2, parent = self.panel1, name = 'staticText2', size = wxSize(27, 13), style = 0, pos = wxPoint(8, 80))

        self.chType = wxChoice(size = wxSize(144, 21), id = wxID_NEWPROPDLGCHTYPE, choices = ['boolean', 'date', 'float', 'int', 'lines', 'long', 'string', 'text', 'tokens', 'selection', 'multiple selection'], parent = self.panel1, name = 'chType', validator = wxDefaultValidator, style = 0, pos = wxPoint(56, 72))

        self.btOK = wxButton(label = 'OK', id = wxID_NEWPROPDLGBTOK, parent = self.panel1, name = 'btOK', size = wxSize(72, 24), style = 0, pos = wxPoint(48, 112))
        EVT_BUTTON(self.btOK, wxID_NEWPROPDLGBTOK, self.OnBtokButton)

        self.btCancel = wxButton(label = 'Cancel', id = wxID_NEWPROPDLGBTCANCEL, parent = self.panel1, name = 'btCancel', size = wxSize(72, 24), style = 0, pos = wxPoint(128, 112))
        EVT_BUTTON(self.btCancel, wxID_NEWPROPDLGBTCANCEL, self.OnBtcancelButton)

    def __init__(self, parent):
        self._init_ctrls(parent)

    def OnBtokButton(self, event):
        self.EndModal(wxID_OK)

    def OnBtcancelButton(self, event):
        self.EndModal(wxID_CANCEL)


if __name__ == '__main__':
    app = wxPySimpleApp()
    frame = create(None)
    frame.Show(true)
    app.MainLoop()
