#Boa:Dialog:CreationOrderDlg

from wxPython.wx import *

def create(parent):
    return CreationOrderDlg(parent)

[wxID_CREATIONORDERDLGBBUP, wxID_CREATIONORDERDLGBBDOWN, wxID_CREATIONORDERDLGSTATICBOX1, wxID_CREATIONORDERDLGPANEL1, wxID_CREATIONORDERDLGLISTBOX1, wxID_CREATIONORDERDLGBTOK, wxID_CREATIONORDERDLGBTCANCEL, wxID_CREATIONORDERDLG] = map(lambda _init_ctrls: wxNewId(), range(8))

class CreationOrderDlg(wxDialog):
    def _init_utils(self): 
        pass

    def _init_ctrls(self, prnt): 
        wxDialog.__init__(self, size = wxSize(280, 281), id = wxID_CREATIONORDERDLG, title = 'Change creation order', parent = prnt, name = 'CreationOrderDlg', style = wxDEFAULT_DIALOG_STYLE, pos = wxPoint(230, 132))
        self._init_utils()

        self.panel1 = wxPanel(size = wxSize(272, 256), id = wxID_CREATIONORDERDLGPANEL1, pos = wxPoint(0, 0), parent = self, name = 'panel1', style = wxTAB_TRAVERSAL)

        self.staticBox1 = wxStaticBox(label = 'Current creation/tab order', id = wxID_CREATIONORDERDLGSTATICBOX1, parent = self.panel1, name = 'staticBox1', size = wxSize(256, 208), style = 0, pos = wxPoint(8, 0))

        self.listBox1 = wxListBox(size = wxSize(200, 184), id = wxID_CREATIONORDERDLGLISTBOX1, choices = [], parent = self.panel1, name = 'listBox1', validator = wxDefaultValidator, style = 0, pos = wxPoint(16, 16))

        self.bbUp = wxBitmapButton(bitmap = wxBitmap('D:\\Dev\\CVSFiles\\boa\\Images\\Shared\\Up.bmp', wxBITMAP_TYPE_BMP), id = wxID_CREATIONORDERDLGBBUP, validator = wxDefaultValidator, parent = self.panel1, name = 'bbUp', size = wxSize(24, 24), style = wxBU_AUTODRAW, pos = wxPoint(224, 72))
        EVT_BUTTON(self.bbUp, wxID_CREATIONORDERDLGBBUP, self.OnBbupButton)

        self.bbDown = wxBitmapButton(bitmap = wxBitmap('D:\\Dev\\CVSFiles\\boa\\Images\\Shared\\Down.bmp', wxBITMAP_TYPE_BMP), id = wxID_CREATIONORDERDLGBBDOWN, validator = wxDefaultValidator, parent = self.panel1, name = 'bbDown', size = wxSize(24, 24), style = wxBU_AUTODRAW, pos = wxPoint(224, 104))
        EVT_BUTTON(self.bbDown, wxID_CREATIONORDERDLGBBDOWN, self.OnBbdownButton)

        self.btOK = wxButton(label = 'OK', id = wxID_CREATIONORDERDLGBTOK, parent = self.panel1, name = 'btOK', size = wxSize(72, 24), style = 0, pos = wxPoint(112, 224))
        EVT_BUTTON(self.btOK, wxID_CREATIONORDERDLGBTOK, self.OnBtokButton)

        self.btCancel = wxButton(label = 'Cancel', id = wxID_CREATIONORDERDLGBTCANCEL, parent = self.panel1, name = 'btCancel', size = wxSize(72, 24), style = 0, pos = wxPoint(192, 224))
        EVT_BUTTON(self.btCancel, wxID_CREATIONORDERDLGBTCANCEL, self.OnBtcancelButton)

    def __init__(self, parent): 
        self._init_ctrls(parent)

    def OnBbupButton(self, event):
        pass

    def OnBbdownButton(self, event):
        pass

    def OnBtokButton(self, event):
        pass

    def OnBtcancelButton(self, event):
        pass
