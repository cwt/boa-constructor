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
#Boa:Frame:HelpFrame

from wxPython.wx import *
from wxPython.html import *
from Preferences import IS, flatTools
import Preferences, Search
from PrefsKeys import keyDefs
import os
from os import path
from Utils import AddToolButtonBmpFile

def tagEater(strg):
    res = ''
    inTag = 0
    for i in range(len(strg)-1, -1, -1):
        if strg[i] == '>':
            inTag = 1
            continue
        elif strg[i] == '<':
            inTag = 0
            continue
        if not inTag:
            res = strg[i] + res
    return res

def showHelp(parent, helpClass, filename, toolbar = None):
    help = helpClass(parent, toolbar)
    help.loadPage(filename)
    help.Show(true)

def showContextHelp(parent, toolbar, word):
    print 'looking up help for', word
    from Companions import HelpCompanions
    helpStr = word+'Docs'
    if HelpCompanions.__dict__.has_key(helpStr):
        print 'loading wxWin help', HelpCompanions.__dict__[helpStr]
        showHelp(parent, wxWinHelpFrame, HelpCompanions.__dict__[helpStr], toolbar)
    elif HelpCompanions.libRefDocs.has_key(word):
        print 'loading python lib ref help', HelpCompanions.libRefDocs[word]
        showHelp(parent, PythonHelpFrame, HelpCompanions.libRefDocs[word], toolbar)
    elif HelpCompanions.modRefDocs.has_key(word):
        print 'loading python mod idx help', HelpCompanions.modRefDocs[word]
        showHelp(parent, PythonHelpFrame, HelpCompanions.modRefDocs[word], toolbar)
    else:
        print 'No help found'

[wxID_HELPFRAME] = map(lambda _init_ctrls: wxNewId(), range(1))
[wxID_HELPFIND, wxID_HELPCLOSE] = map(lambda help: wxNewId(), range(2))

class HelpFrame(wxFrame):
    """ Base class for help defining a home page and search facilities. """
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxFrame.__init__(self, size = (-1, -1), id = wxID_HELPFRAME, title = 'Help', parent = prnt, name = 'HelpFrame', style = wxDEFAULT_FRAME_STYLE | wxTAB_TRAVERSAL, pos = (-1, -1))

    def __init__(self, parent, home, index, icon, paletteToolbar = None):
        self._init_ctrls(parent)
        self._init_utils()
        self.SetDimensions(120, 75, Preferences.wxDefaultFrameSize.x,
          Preferences.wxDefaultFrameSize.y)

        if wxPlatform == '__WXMSW__':
            self.SetIcon(IS.load('Images/Icons/'+icon))

        self.html = wxHtmlWindow(self)
        self.home = home
        self.index = index

        # This is disabled until wxPython bug is fixed or a workaround is implemented
        paletteToolbar = None

        self.paletteToolbar = paletteToolbar

        self.statusBar = self.CreateStatusBar()

        self.html.SetRelatedFrame(self, 'Help - %s')
        self.html.SetRelatedStatusBar(0)

        self.toolBar = self.CreateToolBar(style = \
              wxTB_HORIZONTAL|wxNO_BORDER|wxTAB_TRAVERSAL|flatTools)

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
        wxID_SEARCHCTRL = wxNewId()
        self.searchCtrl = wxTextCtrl(self.toolBar, wxID_SEARCHCTRL, "",
          size=(150, -1), style = wxTE_PROCESS_ENTER)#self.toolBar.GetSize().y))# - Preferences.srchCtrlOffset))wxTE_PROCESS_ENTER
        self.searchCtrl.SetToolTipString('Enter text to search')
        self.toolBar.AddControl(self.searchCtrl)
        EVT_TEXT_ENTER(self, wxID_SEARCHCTRL, self.OnSearchEnter)
        AddToolButtonBmpFile(self, self.toolBar,
          path.join(Preferences.pyPath, 'Images','Shared', 'Find.bmp'),
          'Search', self.OnSearchEnter)
        self.toolBar.AddSeparator()
        wxID_RESULTSCTRL = wxNewId()
        self.resultsCtrl = wxComboBox(self.toolBar, wxID_RESULTSCTRL, "",
          choices=['', '(Results)', '1', '2', '3', '4'], size=(175,-1),
          style=wxCB_DROPDOWN | wxCB_READONLY)
        self.resultsCtrl.SetToolTipString('Matched files\nNumber of matches :: Filename')
        self.resultsCtrl.Clear()
        self.toolBar.AddControl(self.resultsCtrl)
        EVT_COMBOBOX(self, wxID_RESULTSCTRL, self.OnResultSelect)
#        EVT_TEXT_ENTER(self, wxID_RESULTSCTRL, self.OnSearchEnter)

        wxID_SUBRESULTSCTRL = wxNewId()
        self.subResultsCtrl = wxComboBox(self.toolBar, wxID_SUBRESULTSCTRL, "",
          choices=['', '(Results)', '1', '2', '3', '4'], size=(275,-1),
          style=wxCB_DROPDOWN | wxCB_READONLY)
        self.subResultsCtrl.SetToolTipString('Matches in file')
        self.subResultsCtrl.Clear()
        self.toolBar.AddControl(self.subResultsCtrl)
        EVT_COMBOBOX(self, wxID_SUBRESULTSCTRL, self.OnSubResultSelect)

        self.toolBar.Realize()

        if paletteToolbar:
            self.toolIdx = wxNewId()
            paletteToolbar.AddTool(self.toolIdx, IS.load(self.toolBmp),
              shortHelpString = self.helpStr)
            EVT_TOOL(paletteToolbar.GetParent(), self.toolIdx, self.OnSelect)
            paletteToolbar.Realize()
        else:
            self.toolIdx = None

        EVT_MENU(self, wxID_HELPFIND, self.OnFindFocus)
        EVT_MENU(self, wxID_HELPCLOSE, self.OnCloseHelp)
        accLst = []
        for (ctrlKey, key, code), wId in \
                ( (keyDefs['Find'], wxID_HELPFIND),
                  (keyDefs['Escape'], wxID_HELPCLOSE) ):
            accLst.append( (ctrlKey, key, wId) )

        self.SetAcceleratorTable(wxAcceleratorTable(accLst))
        EVT_CLOSE(self, self.OnCloseWindow)

    def loadPage(self, filename = '', highlight = ''):
        if filename:
            fn = path.normpath(path.join(self.home, filename))
        else:
            fn = path.normpath(path.join(self.home, self.index))

        mn = 0
        self.subResults = []
        if highlight:
            page = open(fn).read()

            lst = string.split(page, highlight)
            np = ''
            for s in lst[:-1]:
                anchStr = ''
                matchAnchor = '<a NAME="result_match_%d"></a>' % mn
                matchStr = (tagEater(s[-100:])+highlight)[-50:]
                matchStr = string.replace(matchStr, '\r\n', ' ')
                matchStr = string.replace(matchStr, '\n', ' ')
                self.subResults.append(matchStr)
                for i in xrange(len(np)-1, -1, -1):
                    if np[i] == '<':
                        anchStr = s[:-i] + matchAnchor + s[-i:]
                        break
                    elif np[i] == '>':
                        anchStr = s + matchAnchor
                        break
                if not anchStr:
                    anchStr = s + matchAnchor

                np = '%s%s<font size="+2" color="#00AA00">%s</font>' % (np, anchStr, highlight)
                mn = mn + 1
            np = np + lst[-1]

##            page = string.replace(page, highlight,
##              '<font size="+2" color="#00AA00">%s</font>'%highlight)

            self.html.SetPage(np)
        else:
            self.html.LoadPage(fn)
        self.subResultsCount = mn

    def OnCloseWindow(self, event):
#        print 'Close help', self.toolIdx, self.paletteToolbar

        if self.paletteToolbar:
            print self.paletteToolbar.DeleteTool(self.toolIdx)
            self.paletteToolbar.Realize()

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
        results =  Search.findInFiles(self, self.home,
          self.searchCtrl.GetValue(), self.progressCallback)

        self.resultsCtrl.Clear()
        self.subResultsCtrl.Clear()
        results.sort()
        results.reverse()
        for ocs, result in results:
            self.resultsCtrl.Append('%d :: %s' %(ocs, result))
        self.Raise()
        self.resultsCtrl.SetFocus()

    def OnResultSelect(self, event):
        pge = string.split(self.resultsCtrl.GetValue(), ' :: ')[1]
        self.loadPage(pge, self.searchCtrl.GetValue())

        self.subResultsCtrl.Clear()
        for res in self.subResults:
            self.subResultsCtrl.Append(res)
        event.Skip()

    def OnSubResultSelect(self, event):
        self.html.LoadPage('#result_match_%d'%self.subResultsCtrl.GetSelection())
        #self.html.Scroll(0, -1)

        event.Skip()

    def OnHome(self, event):
        self.loadPage()

    def OnSelect(self, event):
        self.Show(true)
        if self.IsIconized():
            self.Iconize(false)
        self.Raise()

    def OnFindFocus(self, event):
        self.searchCtrl.SetFocus()

    def OnCloseHelp(self, event):
        self.Close()

class BoaHelpFrame(HelpFrame):
    toolBmp = 'Images/Shared/Help.bmp'
    helpStr = 'Boa help'
    def __init__(self, parent, paletteToolbar = None):
        HelpFrame.__init__(self, parent, path.join(Preferences.pyPath, 'Docs'), 'index.html',
          'Help.ico', paletteToolbar)

class wxWinHelpFrame(HelpFrame):
    toolBmp = 'Images/Shared/wxWinHelp.bmp'
    helpStr = 'wxWindows help'
    def __init__(self, parent, paletteToolbar = None):
        HelpFrame.__init__(self, parent, Preferences.wxWinDocsPath, 'wx.htm',
          'wxWinHelp.ico', paletteToolbar)

class PythonHelpFrame(HelpFrame):
    toolBmp = 'Images/Shared/PythonHelp.bmp'
    helpStr = 'Python help'
    def __init__(self, parent, paletteToolbar = None):
        HelpFrame.__init__(self, parent, Preferences.pythonDocsPath, 'index.html',
          'PythonHelp.ico', paletteToolbar)

class CustomHelpFrame(HelpFrame):
    toolBmp = 'Images/Shared/CustomHelp.bmp'
    helpStr = 'Python help'
    def __init__(self, parent, helpRoot, indexDoc, paletteToolbar = None):
        HelpFrame.__init__(self, parent, helpRoot, indexDoc,
          'CustomHelp.ico', paletteToolbar)
