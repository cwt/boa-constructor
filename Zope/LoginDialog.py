#-----------------------------------------------------------------------------
# Name:        LoginDialog.py                                                 
# Purpose:     Dialog to get zope detail                                      
#                                                                             
# Author:      Riaan Booysen                                                  
#                                                                             
# Created:     2000/05/06                                                     
# RCS-ID:      $Id$                                           
# Copyright:   (c) 1999, 2000 Riaan Booysen                                   
# Licence:     GPL                                                            
#-----------------------------------------------------------------------------
#Boa:Dialog:LoginDialog

from wxPython.wx import *

def create(parent):
    return LoginDialog(parent)

[wxID_LOGINDIALOG, wxID_LOGINDIALOGPANEL1, wxID_LOGINDIALOGSTATICTEXT2, wxID_LOGINDIALOGSTATICTEXT3, wxID_LOGINDIALOGSTATICTEXT4, wxID_LOGINDIALOGSTATICTEXT5, wxID_LOGINDIALOGHOSTTC, wxID_LOGINDIALOGFTPPORTTC, wxID_LOGINDIALOGUSERNAMETC, wxID_LOGINDIALOGPASSWORDTC, wxID_LOGINDIALOGBUTTON1, wxID_LOGINDIALOGBUTTON2, wxID_LOGINDIALOGSTATICTEXT1, wxID_LOGINDIALOGHTTPPORTTC] = map(lambda _init_ctrls: NewId(), range(14))

class LoginDialog(wxDialog):
    def _init_utils(self): 
        pass

    def _init_ctrls(self, prnt): 
        wxDialog.__init__(self, size = wxSize(239, 215), id = wxID_LOGINDIALOG, title = 'Open connection', parent = prnt, name = 'LoginDialog', style = wxDEFAULT_DIALOG_STYLE, pos = wxPoint(421, 324))
        self.SetClientSize(wxSize(231, 188))

        self.panel1 = wxPanel(size = wxSize(232, 188), parent = self, id = wxID_LOGINDIALOGPANEL1, name = 'panel1', style = wxTAB_TRAVERSAL, pos = wxPoint(0, 0))

        self.staticText2 = wxStaticText(label = 'Host:', id = wxID_LOGINDIALOGSTATICTEXT2, parent = self.panel1, name = 'staticText2', size = wxSize(24, 12), style = 0, pos = wxPoint(8, 12))

        self.staticText3 = wxStaticText(label = 'FTP Port:', id = wxID_LOGINDIALOGSTATICTEXT3, parent = self.panel1, name = 'staticText3', size = wxSize(52, 12), style = 0, pos = wxPoint(8, 40))

        self.staticText4 = wxStaticText(label = 'User name:', id = wxID_LOGINDIALOGSTATICTEXT4, parent = self.panel1, name = 'staticText4', size = wxSize(56, 12), style = 0, pos = wxPoint(8, 96))

        self.staticText5 = wxStaticText(label = 'Password:', id = wxID_LOGINDIALOGSTATICTEXT5, parent = self.panel1, name = 'staticText5', size = wxSize(48, 12), style = wxTE_PASSWORD, pos = wxPoint(8, 124))

        self.hostTC = wxTextCtrl(size = wxSize(148, 24), value = '127.0.0.1', pos = wxPoint(72, 4), parent = self.panel1, name = 'hostTC', style = 0, id = wxID_LOGINDIALOGHOSTTC)

        self.ftpPortTC = wxTextCtrl(size = wxSize(148, 24), value = '8021', pos = wxPoint(72, 32), parent = self.panel1, name = 'ftpPortTC', style = 0, id = wxID_LOGINDIALOGFTPPORTTC)

        self.usernameTC = wxTextCtrl(size = wxSize(148, 24), value = '', pos = wxPoint(72, 88), parent = self.panel1, name = 'usernameTC', style = 0, id = wxID_LOGINDIALOGUSERNAMETC)

        self.passwordTC = wxTextCtrl(size = wxSize(148, 24), value = '', pos = wxPoint(72, 116), parent = self.panel1, name = 'passwordTC', style = wxTE_PASSWORD, id = wxID_LOGINDIALOGPASSWORDTC)

        self.button1 = wxButton(label = 'OK', id = wxID_LOGINDIALOGBUTTON1, parent = self.panel1, name = 'button1', size = wxSize(76, 24), style = 0, pos = wxPoint(36, 156))
        EVT_BUTTON(self.button1,  wxID_LOGINDIALOGBUTTON1, self.OnButton1Button)

        self.button2 = wxButton(label = 'Cancel', id = wxID_LOGINDIALOGBUTTON2, parent = self.panel1, name = 'button2', size = wxSize(76, 24), style = 0, pos = wxPoint(116, 156))
        EVT_BUTTON(self.button2,  wxID_LOGINDIALOGBUTTON2, self.OnButton2Button)

        self.staticText1 = wxStaticText(label = 'HTTP Port:', id = wxID_LOGINDIALOGSTATICTEXT1, parent = self.panel1, name = 'staticText1', size = wxSize(56, 12), style = 0, pos = wxPoint(8, 68))

        self.httpPortTC = wxTextCtrl(size = wxSize(148, 24), value = '8080', pos = wxPoint(72, 60), parent = self.panel1, name = 'httpPortTC', style = 0, id = wxID_LOGINDIALOGHTTPPORTTC)


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







