#----------------------------------------------------------------------
# Name:        Help.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
from wxPython.wx import *
from wxPython.html import *
#from Preferences import 
import Preferences, Search
import os
from os import path
from Utils import AddToolButtonBmpFile

def showHelp(parent, helpClass, filename):
    help = helpClass(parent)
    help.loadPage(filename)
    help.Show(true)
    
class HelpFrame(wxFrame):
    """ Base class for help defining a home page and search facilities. """
    def __init__(self, parent, home, index, icon):
        wxFrame.__init__(self, parent, -1, 'Help',
                         wxPoint(120, 75), Preferences.wxDefaultFrameSize)#wxSize(560, 400))
	if wxPlatform == '__WXMSW__':
	    self.icon = wxIcon(Preferences.toPyPath('Images\\Icons\\'+icon), wxBITMAP_TYPE_ICO)
	    self.SetIcon(self.icon)

        self.html = wxHtmlWindow(self)
        self.home = home 
        self.index = index

        self.statusBar = self.CreateStatusBar()
        
        self.html.SetRelatedFrame(self, 'Help - %s')
        self.html.SetRelatedStatusBar(0)

        self.toolBar = self.CreateToolBar(wxTB_HORIZONTAL|wxNO_BORDER)#|wxTB_FLAT
#        self.toolBar.SetToolBitmapSize((18, 20))        
        
        AddToolButtonBmpFile(self, self.toolBar, 
          path.join(Preferences.pyPath, 'Images','Shared', 'Previous.bmp'), 
          'Previous', self.OnPrevious)
        AddToolButtonBmpFile(self, self.toolBar, 
          path.join(Preferences.pyPath, 'Images','Shared', 'Next.bmp'), 
          'Next', self.OnNext)
        AddToolButtonBmpFile(self, self.toolBar, 
          path.join(Preferences.pyPath, 'Images','Shared', 'Home.bmp'), 
          'home', self.OnHome)

        self.toolBar.AddSeparator()
        wxID_SEARCHCTRL = NewId()
        self.searchCtrl = wxTextCtrl(self.toolBar, wxID_SEARCHCTRL, "",
          size=(150, -1))#self.toolBar.GetSize().y))# - Preferences.srchCtrlOffset))
        self.toolBar.AddControl(self.searchCtrl)
        EVT_TEXT_ENTER(self, wxID_SEARCHCTRL, self.OnSearchEnter)
        AddToolButtonBmpFile(self, self.toolBar, 
          path.join(Preferences.pyPath, 'Images','Shared', 'Find.bmp'), 
          'Search', self.OnSearchEnter)
        self.toolBar.AddSeparator()
        wxID_RESULTSCTRL = NewId()
        self.resultsCtrl = wxComboBox(self.toolBar, wxID_RESULTSCTRL, "", 
          choices=['', '(Results)', '1', '2', '3', '4'], size=(300,-1), 
          style=wxCB_DROPDOWN | wxCB_READONLY)
        self.resultsCtrl.Clear()  
        self.toolBar.AddControl(self.resultsCtrl)
        EVT_COMBOBOX(self, wxID_RESULTSCTRL, self.OnResultSelect)
#        EVT_TEXT_ENTER(self, wxID_RESULTSCTRL, self.OnSearchEnter)
        
        self.toolBar.Realize()

    def loadPage(self, filename = ''):
        if filename:
            self.html.LoadPage(self.home+'/'+filename)
        else:
            self.html.LoadPage(self.home+'/'+self.index)

    def OnCloseWindow(self, event):
        self.Destroy()

    def OnPrevious(self, event):
        if not self.html.HistoryBack():
            wxMessageBox('No more items in history')

    def OnNext(self, event):
        if not self.html.HistoryForward():
            wxMessageBox('No more items in history')

    def progressCallback(self, dlg, count, file, msg):
        dlg.Update(count, msg +' '+ file)
        
    def OnSearchEnter(self, event):
##        max = len(os.listdir(self.home))
##        dlg = wxProgressDialog('Search help files...',
##                               'Searching...',
##                               max,
##                               self,
##                               wxPD_CAN_ABORT | wxPD_APP_MODAL)
##        try:
        results =  Search.findInFiles(self, self.home, 
          self.searchCtrl.GetValue(), self.progressCallback)
##        finally:
##            dlg.Destroy()
                    
        self.resultsCtrl.Clear()
        results.sort()
        results.reverse()
        for ocs, result in results:
            self.resultsCtrl.Append('%d :: %s' %(ocs, result))
    
    def OnResultSelect(self, event):
        pge = string.split(self.resultsCtrl.GetValue(), ' :: ')[1]
        self.loadPage(pge)
        event.Skip()

    def OnHome(self, event):
        self.loadPage()

        
class BoaHelpFrame(HelpFrame):
    def __init__(self, parent):
        HelpFrame.__init__(self, parent, Preferences.toPyPath('Docs'), 'Boa.html',
          'Help.ico')

class wxWinHelpFrame(HelpFrame):
    def __init__(self, parent):
        HelpFrame.__init__(self, parent, Preferences.wxWinDocsPath, 'wx.htm',
          'wxWinHelp.ico')

class PythonHelpFrame(HelpFrame):
    def __init__(self, parent):
        HelpFrame.__init__(self, parent, Preferences.pythonDocsPath, 'index.html',
          'PythonHelp.ico')
        
