#Boa:Dialog:AttachDlg

from wxPython.wx import *

def create(parent):
    return AttachDlg(parent)

[wxID_ATTACHDLGPORT_CTRL,
 wxID_ATTACHDLGHOST_CTRL,
 wxID_ATTACHDLGPASSWORD_CTRL,
 wxID_ATTACHDLGUSERNAME_CTRL,
 wxID_ATTACHDLGSTATICTEXT1,
 wxID_ATTACHDLGSTATICTEXT3,
 wxID_ATTACHDLGSTATICTEXT2,
 wxID_ATTACHDLGHELP_BUTTON,
 wxID_ATTACHDLGSTATICTEXT4,
 wxID_ATTACHDLGCANCEL_BUTTON,
 wxID_ATTACHDLGOK_BUTTON,
 wxID_ATTACHDLG] = map(lambda _init_ctrls: wxNewId(), range(12))

class AttachDlg(wxDialog):
    def _init_utils(self): 
        pass

    def _init_ctrls(self, prnt): 
        wxDialog.__init__(self, size = wxSize(288, 227), id = wxID_ATTACHDLG, title = 'Attach to debugger', parent = prnt, name = 'AttachDlg', style = wxDEFAULT_DIALOG_STYLE, pos = wxPoint(344, 237))
        self._init_utils()
        EVT_CLOSE(self, self.OnCloseWindow)

        self.staticText1 = wxStaticText(label = 'Host', id = wxID_ATTACHDLGSTATICTEXT1, parent = self, name = 'staticText1', size = wxSize(56, 16), style = 0, pos = wxPoint(16, 24))

        self.staticText2 = wxStaticText(label = 'Port', id = wxID_ATTACHDLGSTATICTEXT2, parent = self, name = 'staticText2', size = wxSize(56, 16), style = 0, pos = wxPoint(16, 56))

        self.staticText3 = wxStaticText(label = 'Username', id = wxID_ATTACHDLGSTATICTEXT3, parent = self, name = 'staticText3', size = wxSize(56, 16), style = 0, pos = wxPoint(16, 88))

        self.staticText4 = wxStaticText(label = 'Password', id = wxID_ATTACHDLGSTATICTEXT4, parent = self, name = 'staticText4', size = wxSize(56, 16), style = 0, pos = wxPoint(16, 120))

        self.host_ctrl = wxTextCtrl(size = wxSize(160, 24), value = 'localhost', pos = wxPoint(80, 16), parent = self, name = 'host_ctrl', style = 0, id = wxID_ATTACHDLGHOST_CTRL)

        self.port_ctrl = wxTextCtrl(size = wxSize(48, 24), value = '8080', pos = wxPoint(80, 48), parent = self, name = 'port_ctrl', style = 0, id = wxID_ATTACHDLGPORT_CTRL)

        self.username_ctrl = wxTextCtrl(size = wxSize(96, 24), value = '', pos = wxPoint(80, 80), parent = self, name = 'username_ctrl', style = 0, id = wxID_ATTACHDLGUSERNAME_CTRL)

        self.password_ctrl = wxTextCtrl(size = wxSize(96, 24), value = '', pos = wxPoint(80, 112), parent = self, name = 'password_ctrl', style = wxTE_PASSWORD, id = wxID_ATTACHDLGPASSWORD_CTRL)

        self.ok_button = wxButton(label = 'Ok', id = wxID_ATTACHDLGOK_BUTTON, parent = self, name = 'ok_button', size = wxSize(72, 24), style = 0, pos = wxPoint(24, 160))
        EVT_BUTTON(self.ok_button, wxID_ATTACHDLGOK_BUTTON, self.OnOkButton)

        self.cancel_button = wxButton(label = 'Cancel', id = wxID_ATTACHDLGCANCEL_BUTTON, parent = self, name = 'cancel_button', size = wxSize(72, 24), style = 0, pos = wxPoint(104, 160))
        EVT_BUTTON(self.cancel_button, wxID_ATTACHDLGCANCEL_BUTTON, self.OnCancelButton)

        self.help_button = wxButton(label = 'Help', id = wxID_ATTACHDLGHELP_BUTTON, parent = self, name = 'help_button', size = wxSize(72, 24), style = 0, pos = wxPoint(184, 160))
        EVT_BUTTON(self.help_button, wxID_ATTACHDLGHELP_BUTTON, self.OnHelpButton)

    def __init__(self, editor): 
        self._init_ctrls(editor)
        self.editor = editor

    def OnOkButton(self, event):
        host = self.host_ctrl.GetValue()
        port = self.port_ctrl.GetValue()
        user = self.username_ctrl.GetValue()
        pw = self.password_ctrl.GetValue()

        from Debugger import DebuggerFrame
        from RemoteClient import RemoteClient

        debugger = DebuggerFrame(self.editor, slave_mode=0)
        client = RemoteClient(debugger, host, port, user, pw)
        debugger.setDebugClient(client)
        if user:
            debugger.setTitleInfo('%s@%s:%s' % (user, host, port))
        else:
            debugger.setTitleInfo('%s:%s' % (host, port))
            
        self.editor.debugger = debugger
        debugger.Show(true)
        debugger.requestDebuggerStatus()
        self.Close()

    def OnCancelButton(self, event):
        self.Close()

    def OnHelpButton(self, event):
        pass

    def OnCloseWindow(self, event):
        self.editor = None
        self.Destroy()
        event.Skip()
