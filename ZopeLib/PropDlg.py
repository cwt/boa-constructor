#Boa:Dialog:NewPropDlg

from wxPython.wx import *

def create(parent):
    return NewPropDlg(parent)

[wxID_NEWPROPDLG, wxID_NEWPROPDLGBTCANCEL, wxID_NEWPROPDLGBTOK,
 wxID_NEWPROPDLGCHTYPE, wxID_NEWPROPDLGPANEL1, wxID_NEWPROPDLGSTATICTEXT1,
 wxID_NEWPROPDLGSTATICTEXT2, wxID_NEWPROPDLGSTATICTEXT3,
 wxID_NEWPROPDLGTCPROPNAME, wxID_NEWPROPDLGTCVALUE,
] = map(lambda _init_ctrls: wxNewId(), range(10))

class NewPropDlg(wxDialog):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_NEWPROPDLG, name='NewPropDlg',
              parent=prnt, pos=wxPoint(359, 240), size=wxSize(221, 169),
              style=wxDEFAULT_DIALOG_STYLE, title='New property')
        self._init_utils()
        self.SetClientSize(wxSize(213, 142))

        self.panel1 = wxPanel(id=wxID_NEWPROPDLGPANEL1, name='panel1',
              parent=self, pos=wxPoint(0, 0), size=wxSize(213, 142),
              style=wxTAB_TRAVERSAL)

        self.staticText1 = wxStaticText(id=wxID_NEWPROPDLGSTATICTEXT1,
              label='Name:', name='staticText1', parent=self.panel1,
              pos=wxPoint(8, 16), size=wxSize(40, 16), style=0)

        self.tcPropName = wxTextCtrl(id=wxID_NEWPROPDLGTCPROPNAME,
              name='tcPropName', parent=self.panel1, pos=wxPoint(56, 8),
              size=wxSize(144, 24), style=0, value='')

        self.staticText3 = wxStaticText(id=wxID_NEWPROPDLGSTATICTEXT3,
              label='Value:', name='staticText3', parent=self.panel1,
              pos=wxPoint(8, 48), size=wxSize(40, 13), style=0)

        self.tcValue = wxTextCtrl(id=wxID_NEWPROPDLGTCVALUE, name='tcValue',
              parent=self.panel1, pos=wxPoint(56, 40), size=wxSize(144, 24),
              style=0, value='')

        self.staticText2 = wxStaticText(id=wxID_NEWPROPDLGSTATICTEXT2,
              label='Type:', name='staticText2', parent=self.panel1,
              pos=wxPoint(8, 80), size=wxSize(40, 13), style=0)

        self.chType = wxChoice(choices=['boolean', 'date', 'float', 'int',
              'lines', 'long', 'string', 'text', 'tokens', 'selection',
              'multiple selection'], id=wxID_NEWPROPDLGCHTYPE, name='chType',
              parent=self.panel1, pos=wxPoint(56, 72), size=wxSize(144, 21),
              style=0, validator=wxDefaultValidator)
        self.chType.SetSelection(6)
        self.chType.SetToolTipString('Property type')

        self.btOK = wxButton(id=wxID_NEWPROPDLGBTOK, label='OK', name='btOK',
              parent=self.panel1, pos=wxPoint(48, 112), size=wxSize(72, 24),
              style=0)
        EVT_BUTTON(self.btOK, wxID_NEWPROPDLGBTOK, self.OnBtokButton)

        self.btCancel = wxButton(id=wxID_NEWPROPDLGBTCANCEL, label='Cancel',
              name='btCancel', parent=self.panel1, pos=wxPoint(128, 112),
              size=wxSize(72, 24), style=0)
        EVT_BUTTON(self.btCancel, wxID_NEWPROPDLGBTCANCEL,
              self.OnBtcancelButton)

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
