#----------------------------------------------------------------------
# Name:        Infofields.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
#Boa:Frame:wxFrame1

from wxPython.wx import *

def create(parent):
    return wxFrame1(parent)

class wxFrame1(wxFrame):
    def _init_utils(self): 
        pass

    def _init_ctrls(self, prnt): 
        wxFrame.__init__(self, size = wxSize(322, 258), id = -1, title = '', parent = prnt, name = '', style = wxDEFAULT_FRAME_STYLE, pos = wxPoint(264, 221))
        self.SetClientSize(wxSize(314, 231))

        self.panel1 = wxPanel(size = wxSize(315, 231), id = 193, parent = self, name = 'panel1', style = wxTAB_TRAVERSAL, pos = wxPoint(0, 0))
        self.panel1.SetClientSize(wxSize(315, 231))

        self.staticText1 = wxStaticText(label = 'Name:', id = 223, parent = self.panel1, name = 'staticText1', size = wxSize(31, 13), style = 0, pos = wxPoint(10, 11))
        self.staticText1.SetClientSize(wxSize(31, 13))

        self.staticText2 = wxStaticText(label = 'Purpose:', id = 231, parent = self.panel1, name = 'staticText2', size = wxSize(42, 13), style = 0, pos = wxPoint(8, 33))
        self.staticText2.SetClientSize(wxSize(42, 13))

        self.staticText3 = wxStaticText(label = 'Author:', id = 239, parent = self.panel1, name = 'staticText3', size = wxSize(34, 13), style = 0, pos = wxPoint(10, 77))
        self.staticText3.SetClientSize(wxSize(34, 13))

        self.staticText4 = wxStaticText(label = 'Created:', id = 247, parent = self.panel1, name = 'staticText4', size = wxSize(40, 13), style = 0, pos = wxPoint(10, 105))
        self.staticText4.SetClientSize(wxSize(40, 13))

        self.staticText5 = wxStaticText(label = 'RCS-ID:', id = 255, parent = self.panel1, name = 'staticText5', size = wxSize(39, 13), style = 0, pos = wxPoint(12, 134))
        self.staticText5.SetClientSize(wxSize(39, 13))

        self.staticText6 = wxStaticText(label = 'Copyright:', id = 263, parent = self.panel1, name = 'staticText6', size = wxSize(47, 13), style = 0, pos = wxPoint(13, 157))
        self.staticText6.SetClientSize(wxSize(47, 13))

        self.staticText7 = wxStaticText(label = 'Licence:', id = 271, parent = self.panel1, name = 'staticText7', size = wxSize(41, 13), style = 0, pos = wxPoint(13, 184))
        self.staticText7.SetClientSize(wxSize(41, 13))

        self.textCtrl1 = wxTextCtrl(size = wxSize(200, 19), value = 'textCtrl1', pos = wxPoint(68, 8), parent = self.panel1, name = 'textCtrl1', style = 0, id = 280)
        self.textCtrl1.SetClientSize(wxSize(194, 13))

    def __init__(self, parent): 
        self._init_utils()
        self._init_ctrls(parent)
