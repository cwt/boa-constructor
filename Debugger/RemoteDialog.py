#Boa:Dialog:AttachDlg

from wxPython.wx import *

import Preferences

def create(parent):
    return AttachDlg(parent)

[wxID_ATTACHDLG, wxID_ATTACHDLGCANCEL_BUTTON, wxID_ATTACHDLGHELP_BUTTON, 
 wxID_ATTACHDLGHOST_CTRL, wxID_ATTACHDLGOK_BUTTON, 
 wxID_ATTACHDLGPASSWORD_CTRL, wxID_ATTACHDLGPORT_CTRL, 
 wxID_ATTACHDLGREM_PASS_CTRL, wxID_ATTACHDLGSTATICTEXT1, 
 wxID_ATTACHDLGSTATICTEXT2, wxID_ATTACHDLGSTATICTEXT3, 
 wxID_ATTACHDLGSTATICTEXT4, wxID_ATTACHDLGUSERNAME_CTRL, 
] = map(lambda _init_ctrls: wxNewId(), range(13))

class AttachDlg(wxDialog):
    rem_host = None
    rem_port = None
    rem_user = None
    rem_pass = None
    
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_ATTACHDLG, name='AttachDlg',
              parent=prnt, pos=wxPoint(344, 237), size=wxSize(288, 227),
              style=wxDEFAULT_DIALOG_STYLE, title='Attach to debugger')
        self._init_utils()
        self.SetClientSize(wxSize(280, 200))
        EVT_CLOSE(self, self.OnCloseWindow)

        self.staticText1 = wxStaticText(id=wxID_ATTACHDLGSTATICTEXT1,
              label='Host', name='staticText1', parent=self, pos=wxPoint(16,
              24), size=wxSize(56, 16), style=0)

        self.staticText2 = wxStaticText(id=wxID_ATTACHDLGSTATICTEXT2,
              label='Port', name='staticText2', parent=self, pos=wxPoint(16,
              56), size=wxSize(56, 16), style=0)

        self.staticText3 = wxStaticText(id=wxID_ATTACHDLGSTATICTEXT3,
              label='Username', name='staticText3', parent=self, pos=wxPoint(16,
              88), size=wxSize(56, 16), style=0)

        self.staticText4 = wxStaticText(id=wxID_ATTACHDLGSTATICTEXT4,
              label='Password', name='staticText4', parent=self, pos=wxPoint(16,
              120), size=wxSize(56, 16), style=0)

        self.host_ctrl = wxTextCtrl(id=wxID_ATTACHDLGHOST_CTRL,
              name='host_ctrl', parent=self, pos=wxPoint(80, 16),
              size=wxSize(160, 24), style=0, value=self.host)

        self.port_ctrl = wxTextCtrl(id=wxID_ATTACHDLGPORT_CTRL,
              name='port_ctrl', parent=self, pos=wxPoint(80, 48),
              size=wxSize(48, 24), style=0, value=self.port)

        self.username_ctrl = wxTextCtrl(id=wxID_ATTACHDLGUSERNAME_CTRL,
              name='username_ctrl', parent=self, pos=wxPoint(80, 80),
              size=wxSize(96, 24), style=0, value=self.user)

        self.password_ctrl = wxTextCtrl(id=wxID_ATTACHDLGPASSWORD_CTRL,
              name='password_ctrl', parent=self, pos=wxPoint(80, 112),
              size=wxSize(96, 24), style=wxTE_PASSWORD, value=self.pwd)

        self.ok_button = wxButton(id=wxID_ATTACHDLGOK_BUTTON, label='Ok',
              name='ok_button', parent=self, pos=wxPoint(24, 160),
              size=wxSize(72, 24), style=0)
        EVT_BUTTON(self.ok_button, wxID_ATTACHDLGOK_BUTTON, self.OnOkButton)

        self.cancel_button = wxButton(id=wxID_ATTACHDLGCANCEL_BUTTON,
              label='Cancel', name='cancel_button', parent=self,
              pos=wxPoint(104, 160), size=wxSize(72, 24), style=0)
        EVT_BUTTON(self.cancel_button, wxID_ATTACHDLGCANCEL_BUTTON,
              self.OnCancelButton)

        self.help_button = wxButton(id=wxID_ATTACHDLGHELP_BUTTON, label='Help',
              name='help_button', parent=self, pos=wxPoint(184, 160),
              size=wxSize(72, 24), style=0)
        EVT_BUTTON(self.help_button, wxID_ATTACHDLGHELP_BUTTON,
              self.OnHelpButton)

        self.rem_pass_ctrl = wxCheckBox(id=wxID_ATTACHDLGREM_PASS_CTRL,
              label='Remember', name='rem_pass_ctrl', parent=self,
              pos=wxPoint(184, 120), size=wxSize(73, 13), style=0)
        self.rem_pass_ctrl.SetValue(False)

    def __init__(self, editor):
        host, port, user, pwd = \
              self.rem_host, self.rem_port, self.rem_user, self.rem_pass

        self.host = '127.0.0.1'
        if host is not None: self.host = host

        self.port = '26200'
        if port is not None: self.port = port
        
        self.user = ''
        if user is not None: self.user = user
        
        self.pwd = ''
        if pwd is not None: self.pwd = pwd
        
        self._init_ctrls(editor)
        self.editor = editor
        
        self.SetIcon(Preferences.IS.load('Images/Icons/Debug.ico'))

    def OnOkButton(self, event):
        host = self.host_ctrl.GetValue()
        port = self.port_ctrl.GetValue()
        user = self.username_ctrl.GetValue()
        pw = self.password_ctrl.GetValue()

        AttachDlg.rem_host = host
        AttachDlg.rem_port = port
        AttachDlg.rem_user = user
        if self.rem_pass_ctrl.GetValue():
            AttachDlg.rem_pass = pw
        else:
            AttachDlg.rem_pass = None

        self.Close()
        return
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
        debugger.doDebugStep()
        debugger.Show(true)
        self.EndModal(wxOK)

    def OnCancelButton(self, event):
        #self.Close()
        self.EndModal(wxCANCEL)

    def OnHelpButton(self, event):
        pass

    def OnCloseWindow(self, event):
        self.editor = None
        self.Destroy()
        event.Skip()


if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    dlg = create(None)
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()

    app.MainLoop()
