#-----------------------------------------------------------------------------
# Name:        LoginDialog.py
# Purpose:     Dialog to get zope detail
#
# Author:      Riaan Booysen
#
# Created:     2000/05/06
# RCS-ID:      $Id$
# Copyright:   (c) 2000 - 2004 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:LoginDialog

from wxPython.wx import *

def create(parent):
    return LoginDialog(parent)

[wxID_LOGINDIALOG, wxID_LOGINDIALOGBUTTON1, wxID_LOGINDIALOGBUTTON2,
 wxID_LOGINDIALOGFTPPORTTC, wxID_LOGINDIALOGHOSTTC,
 wxID_LOGINDIALOGHTTPPORTTC, wxID_LOGINDIALOGPANEL1,
 wxID_LOGINDIALOGPASSWORDTC, wxID_LOGINDIALOGSTATICTEXT1,
 wxID_LOGINDIALOGSTATICTEXT2, wxID_LOGINDIALOGSTATICTEXT3,
 wxID_LOGINDIALOGSTATICTEXT4, wxID_LOGINDIALOGSTATICTEXT5,
 wxID_LOGINDIALOGUSERNAMETC,
] = map(lambda _init_ctrls: wxNewId(), range(14))

class LoginDialog(wxDialog):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_LOGINDIALOG, name='LoginDialog',
              parent=prnt, pos=wxPoint(421, 324), size=wxSize(239, 215),
              style=wxDEFAULT_DIALOG_STYLE, title='Open connection')
        self._init_utils()
        self.SetClientSize(wxSize(231, 188))

        self.panel1 = wxPanel(id=wxID_LOGINDIALOGPANEL1, name='panel1',
              parent=self, pos=wxPoint(0, 0), size=wxSize(231, 188),
              style=wxTAB_TRAVERSAL)

        self.staticText2 = wxStaticText(id=wxID_LOGINDIALOGSTATICTEXT2,
              label='Host:', name='staticText2', parent=self.panel1,
              pos=wxPoint(8, 12), size=wxSize(24, 12), style=0)

        self.staticText3 = wxStaticText(id=wxID_LOGINDIALOGSTATICTEXT3,
              label='FTP Port:', name='staticText3', parent=self.panel1,
              pos=wxPoint(8, 40), size=wxSize(52, 12), style=0)

        self.staticText4 = wxStaticText(id=wxID_LOGINDIALOGSTATICTEXT4,
              label='User name:', name='staticText4', parent=self.panel1,
              pos=wxPoint(8, 96), size=wxSize(56, 12), style=0)

        self.staticText5 = wxStaticText(id=wxID_LOGINDIALOGSTATICTEXT5,
              label='Password:', name='staticText5', parent=self.panel1,
              pos=wxPoint(8, 124), size=wxSize(48, 12), style=wxTE_PASSWORD)

        self.hostTC = wxTextCtrl(id=wxID_LOGINDIALOGHOSTTC, name='hostTC',
              parent=self.panel1, pos=wxPoint(72, 4), size=wxSize(148, 24),
              style=0, value='127.0.0.1')

        self.ftpPortTC = wxTextCtrl(id=wxID_LOGINDIALOGFTPPORTTC,
              name='ftpPortTC', parent=self.panel1, pos=wxPoint(72, 32),
              size=wxSize(148, 24), style=0, value='8021')

        self.usernameTC = wxTextCtrl(id=wxID_LOGINDIALOGUSERNAMETC,
              name='usernameTC', parent=self.panel1, pos=wxPoint(72, 88),
              size=wxSize(148, 24), style=0, value='')

        self.passwordTC = wxTextCtrl(id=wxID_LOGINDIALOGPASSWORDTC,
              name='passwordTC', parent=self.panel1, pos=wxPoint(72, 116),
              size=wxSize(148, 24), style=wxTE_PASSWORD, value='')

        self.button1 = wxButton(id=wxID_LOGINDIALOGBUTTON1, label='OK',
              name='button1', parent=self.panel1, pos=wxPoint(36, 156),
              size=wxSize(76, 24), style=0)
        EVT_BUTTON(self.button1, wxID_LOGINDIALOGBUTTON1, self.OnButton1Button)

        self.button2 = wxButton(id=wxID_LOGINDIALOGBUTTON2, label='Cancel',
              name='button2', parent=self.panel1, pos=wxPoint(116, 156),
              size=wxSize(76, 24), style=0)
        EVT_BUTTON(self.button2, wxID_LOGINDIALOGBUTTON2, self.OnButton2Button)

        self.staticText1 = wxStaticText(id=wxID_LOGINDIALOGSTATICTEXT1,
              label='HTTP Port:', name='staticText1', parent=self.panel1,
              pos=wxPoint(8, 68), size=wxSize(56, 12), style=0)

        self.httpPortTC = wxTextCtrl(id=wxID_LOGINDIALOGHTTPPORTTC,
              name='httpPortTC', parent=self.panel1, pos=wxPoint(72, 60),
              size=wxSize(148, 24), style=0, value='8080')

    def __init__(self, parent):
        self._init_utils()
        self._init_ctrls(parent)
        self.Centre(wxBOTH)

    def setup(self, host, ftpport, httpport, username, password):
        self.hostTC.SetValue(host)
        self.ftpPortTC.SetValue(str(ftpport))
        self.httpPortTC.SetValue(str(httpport))
        self.usernameTC.SetValue(username)
        self.passwordTC.SetValue(password)

    def getup(self):
        return self.hostTC.GetValue(), int(self.ftpPortTC.GetValue()), \
          int(self.httpPortTC.GetValue()), self.usernameTC.GetValue(), \
          self.passwordTC.GetValue()


    def OnButton1Button(self, event):
        self.EndModal(wxOK)

    def OnButton2Button(self, event):
        self.EndModal(wxCANCEL)
