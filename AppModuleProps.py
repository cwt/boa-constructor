#----------------------------------------------------------------------
# Name:        AppModuleProps.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

#Boa:Dialog:wxDialog1

from wxPython.wx import *

def create(parent):
    return wxDialog1(parent)

class wxDialog1(wxDialog):
    def _init_utils(self): 
        pass

    def _init_ctrls(self, prnt): 
        wxDialog.__init__(self, size = wxSize(282, 173), id = -1, title = 'Module properties', parent = prnt, name = '', style = wxDEFAULT_DIALOG_STYLE, pos = wxPoint(315, 277))

        self.panel1 = wxPanel(size = wxSize(272, 143), parent = self, id = 175, name = 'panel1', style = wxTAB_TRAVERSAL, pos = wxPoint(0, 0))

        self.moduleName = wxStaticText(label = 'Module name', id = 200, parent = self.panel1, name = 'moduleName', size = wxSize(64, 13), style = 0, pos = wxPoint(10, 8))

        self.moduleAutoCreate = wxCheckBox(label = 'Auto create', id = 209, parent = self.panel1, name = 'moduleAutoCreate', size = wxSize(75, 20), style = 0, pos = wxPoint(9, 26))

        self.moduleDesc = wxStaticText(label = 'Description:', id = 219, parent = self.panel1, name = 'moduleDesc', size = wxSize(56, 13), style = 0, pos = wxPoint(10, 50))

        self.textCtrl1 = wxTextCtrl(size = wxSize(250, 23), value = '', pos = wxPoint(9, 65), style = 0, parent = self.panel1, id = 229)

        self.button1 = wxButton(label = 'OK', id = 190, parent = self.panel1, name = 'button1', size = wxDefaultSize, style = 0, pos = wxPoint(89, 103))
        EVT_BUTTON(self.button1, self.OnButton1Button)

        self.button2 = wxButton(label = 'Cancel', id = 197, parent = self.panel1, name = 'button2', size = wxDefaultSize, style = 0, pos = wxPoint(176, 103))
        EVT_BUTTON(self.button2, self.OnButton2Button)

    def __init__(self, parent): 
        self._init_utils()
        self._init_ctrls(parent)

    def OnButton1Button(self, event):
        self.EndModal(wxOK)

    def OnButton2Button(self, event):
        self.EndModal(wxCANCEL)
