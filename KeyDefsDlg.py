#Boa:Dialog:wxDialog1

from wxPython.wx import *

def create(parent):
    return wxDialog1(parent)

[wxID_WXDIALOG1, wxID_WXDIALOG1CANCELBTN, wxID_WXDIALOG1CHECKBOX1, wxID_WXDIALOG1CHECKBOX2, wxID_WXDIALOG1CHECKBOX3, wxID_WXDIALOG1CHECKBOX4, wxID_WXDIALOG1COMBOBOX1, wxID_WXDIALOG1OKBTN, wxID_WXDIALOG1STATICBOX1, wxID_WXDIALOG1STATICTEXT1, wxID_WXDIALOG1STATICTEXT2, wxID_WXDIALOG1TEXTCTRL1] = map(lambda _init_ctrls: wxNewId(), range(12))

class wxDialog1(wxDialog):
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxDialog.__init__(self, id = wxID_WXDIALOG1, name = '', parent = prnt, pos = wxPoint(430, 271), size = wxSize(298, 191), style = wxDEFAULT_DIALOG_STYLE, title = 'Key binding definition')
        self._init_utils()
        self.SetClientSize(wxSize(290, 164))

        self.staticBox1 = wxStaticBox(id = wxID_WXDIALOG1STATICBOX1, label = 'Flags', name = 'staticBox1', parent = self, pos = wxPoint(8, 8), size = wxSize(136, 112), style = 0)

        self.checkBox1 = wxCheckBox(id = wxID_WXDIALOG1CHECKBOX1, label = 'wxACCEL_NORMAL', name = 'checkBox1', parent = self, pos = wxPoint(16, 24), size = wxSize(120, 19), style = 0)

        self.checkBox2 = wxCheckBox(id = wxID_WXDIALOG1CHECKBOX2, label = 'wxACCEL_CTRL', name = 'checkBox2', parent = self, pos = wxPoint(16, 48), size = wxSize(112, 19), style = 0)

        self.checkBox3 = wxCheckBox(id = wxID_WXDIALOG1CHECKBOX3, label = 'wxACCEL_ALT', name = 'checkBox3', parent = self, pos = wxPoint(16, 72), size = wxSize(112, 19), style = 0)

        self.checkBox4 = wxCheckBox(id = wxID_WXDIALOG1CHECKBOX4, label = 'wxACCEL_SHIFT', name = 'checkBox4', parent = self, pos = wxPoint(16, 96), size = wxSize(112, 19), style = 0)

        self.comboBox1 = wxComboBox(choices = self.preDefKeys, id = wxID_WXDIALOG1COMBOBOX1, name = 'comboBox1', parent = self, pos = wxPoint(152, 32), size = wxSize(125, 21), style = 0, validator = wxDefaultValidator, value = '')

        self.staticText1 = wxStaticText(id = wxID_WXDIALOG1STATICTEXT1, label = 'Key:', name = 'staticText1', parent = self, pos = wxPoint(152, 16), size = wxSize(21, 13), style = 0)

        self.staticText2 = wxStaticText(id = wxID_WXDIALOG1STATICTEXT2, label = 'Shortcut text:', name = 'staticText2', parent = self, pos = wxPoint(152, 64), size = wxSize(63, 13), style = 0)

        self.textCtrl1 = wxTextCtrl(id = wxID_WXDIALOG1TEXTCTRL1, name = 'textCtrl1', parent = self, pos = wxPoint(152, 80), size = wxSize(124, 21), style = 0, value = '')

        self.okBtn = wxButton(id = wxID_WXDIALOG1OKBTN, label = 'OK', name = 'okBtn', parent = self, pos = wxPoint(120, 128), size = wxSize(75, 23), style = 0)
        EVT_BUTTON(self.okBtn, wxID_WXDIALOG1OKBTN, self.OnOkbtnButton)

        self.cancelBtn = wxButton(id = wxID_WXDIALOG1CANCELBTN, label = 'Cancel', name = 'cancelBtn', parent = self, pos = wxPoint(200, 128), size = wxSize(75, 23), style = 0)
        EVT_BUTTON(self.cancelBtn, wxID_WXDIALOG1CANCELBTN, self.OnCancelbtnButton)

    def __init__(self, parent):
        self.preDefKeys = []
        self.preDefKeys = specialKeys.keys() + otherKeys
        self._init_ctrls(parent)

    def OnOkbtnButton(self, event):
        self.EndModal(wxID_OK)

    def OnCancelbtnButton(self, event):
        self.EndModal(wxID_CANCEL)

specialKeys = {'WXK_BACK': 8, 'WXK_TAB': 9, 'WXK_RETURN': 13, 'WXK_ESCAPE': 27,
               'WXK_SPACE': 32, 'WXK_DELETE': 127}
otherKeys = ['WXK_START', 'WXK_LBUTTON', 'WXK_RBUTTON', 'WXK_CANCEL', 'WXK_MBUTTON', 
 'WXK_CLEAR', 'WXK_SHIFT', 'WXK_CONTROL', 'WXK_MENU', 'WXK_PAUSE', 'WXK_CAPITAL',
 'WXK_PRIOR', 'WXK_NEXT', 'WXK_END', 'WXK_HOME', 'WXK_LEFT', 'WXK_UP', 'WXK_RIGHT',
 'WXK_DOWN', 'WXK_SELECT', 'WXK_PRINT', 'WXK_EXECUTE', 'WXK_SNAPSHOT', 'WXK_INSERT',
 'WXK_HELP', 'WXK_NUMPAD0', 'WXK_NUMPAD1', 'WXK_NUMPAD2', 'WXK_NUMPAD3', 'WXK_NUMPAD4',
 'WXK_NUMPAD5', 'WXK_NUMPAD6', 'WXK_NUMPAD7', 'WXK_NUMPAD8', 'WXK_NUMPAD9', 
 'WXK_MULTIPLY', 'WXK_ADD', 'WXK_SEPARATOR', 'WXK_SUBTRACT', 'WXK_DECIMAL', 
 'WXK_DIVIDE', 'WXK_F1', 'WXK_F2', 'WXK_F3', 'WXK_F4', 'WXK_F5', 'WXK_F6', 
 'WXK_F7', 'WXK_F8', 'WXK_F9', 'WXK_F10', 'WXK_F11', 'WXK_F12', 'WXK_F13', 
 'WXK_F14', 'WXK_F15', 'WXK_F16', 'WXK_F17', 'WXK_F18', 'WXK_F19', 'WXK_F20', 
 'WXK_F21', 'WXK_F22', 'WXK_F23', 'WXK_F24', 'WXK_NUMLOCK', 'WXK_SCROLL']
 

if __name__ == '__main__':
    app = wxPySimpleApp()
    dlg = create(None)
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()
