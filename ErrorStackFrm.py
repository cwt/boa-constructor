#-----------------------------------------------------------------------------
# Name:        ErrorStackFrm.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2001
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2005 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
##Boa:Frame:ErrorStackMF
# remove between #-- comments before editing visually

import os, pickle

from wxPython.wx import *
from wxPython.stc import *

import Preferences, Utils

[wxID_EO_LOADHIST, wxID_EO_SAVEHIST, wxID_EO_CLRHIST, wxID_EO_CLOSEDIFF, 
 wxID_EO_CLOSEINPT, wxID_EO_KILLPROC, wxID_EO_CHECKPROCS] = Utils.wxNewIds(7)

[wxID_ERRORSTACKMFSTATUSBAR, wxID_ERRORSTACKMFERRORSTACKTC, wxID_ERRORSTACKMF, 
 wxID_ERRORSTACKMFNOTEBOOK, wxID_ERRORSTACKMFOUTPUTTC, 
 wxID_ERRORSTACKMFERRORTC] = map(lambda _init_ctrls: wxNewId(), range(6))

class ErrorStackMF(wxFrame, Utils.FrameRestorerMixin):
    def _init_coll_notebook_Pages(self, parent):

        parent.AddPage(select = true, imageId = self.tracebackImgIdx, 
              page = self.errorStackTC, text = self.tracebackText)
        parent.AddPage(select = false, imageId = self.outputImgIdx, 
              page = self.outputTC, text = self.outputText)
        parent.AddPage(select = false, imageId = self.errorsImgIdx, 
              page = self.errorTC, text = self.errorsText)

    def _init_coll_statusBar_Fields(self, parent):
        parent.SetFieldsCount(1)

        parent.SetStatusText('', 0)

        parent.SetStatusWidths([-1])

    def _init_utils(self):
        self.images = wxImageList(16, 16)

    def _init_ctrls(self, prnt):
        wxFrame.__init__(self, size = wxSize(330, 443), id = wxID_ERRORSTACKMF,     
              title = 'Traceback and Output browser', parent = prnt, 
              name = 'ErrorStackMF', 
              style = wxDEFAULT_FRAME_STYLE | wxFRAME_TOOL_WINDOW, 
              pos = wxPoint(464, 228))
        self._init_utils()
        EVT_CLOSE(self, self.OnErrorstackmfClose)

        self.notebook = wxNotebook(size = wxSize(330, 418), 
              id = wxID_ERRORSTACKMFNOTEBOOK, parent = self, 
              name = 'notebook', 
              style = self.notebookStyle, pos = wxPoint(0, 0))

        self.statusBar = wxStatusBar(id = wxID_ERRORSTACKMFSTATUSBAR, 
              parent = self, name = 'statusBar', style = 0)
        self.SetStatusBar(self.statusBar)

        self.outputTC = wxTextCtrl(size = wxSize(326, 384), value = '', 
              pos = wxPoint(0, 0), parent = self.notebook, 
              name = 'outputTC', style = wxTE_MULTILINE | wxTE_RICH, 
              id = wxID_ERRORSTACKMFOUTPUTTC)

        self.errorTC = wxTextCtrl(size = wxSize(326, 384), value = '', 
              pos = wxPoint(0, 0), parent = self.notebook, name = 'errorTC', 
              style = wxTE_MULTILINE | wxTE_RICH, id = wxID_ERRORSTACKMFERRORTC)
        self.errorTC.SetForegroundColour(wxColour(64, 0, 0))

        #--
        # Special case to fix GTK redraw problem
        if wxPlatform == '__WXGTK__':
            prxy, errorStackTC = Utils.wxProxyPanel(self.notebook, wxTreeCtrl, 
                  size = wxSize(312, 390), id = wxID_ERRORSTACKMFERRORSTACKTC, 
                  name = 'errorStackTC', validator = wxDefaultValidator, 
                  style = wxTR_HAS_BUTTONS | wxSUNKEN_BORDER, 
                  pos = wxPoint(0, 0))
            self.errorStackTC = prxy
            self._init_coll_notebook_Pages(self.notebook)
            self.errorStackTC = errorStackTC
        else:
            self.errorStackTC = wxTreeCtrl(size = wxSize(312, 390), 
                  id = wxID_ERRORSTACKMFERRORSTACKTC, parent = self.notebook, 
                  name = 'errorStackTC', validator = wxDefaultValidator, 
                  pos = wxPoint(4, 22), 
                  style = wxTR_HAS_BUTTONS | wxSUNKEN_BORDER)
            self._init_coll_notebook_Pages(self.notebook)
        #--

    historySize = 50
    def __init__(self, parent, editor):
        self.notebookStyle = 0
        self.tracebackImgIdx = 0
        self.tracebackText = 'Tracebacks'
        self.outputImgIdx = 1
        self.outputText = 'Output'
        self.errorsImgIdx = 2
        self.errorsText = 'Errors'

        self.processesPage = None
        self.processesImgIdx = 3
        self.processesText = 'Tasks'

        self.diffPage = None
        self.diffImgIdx = 4

        self.inputPage = None
        self.inputImgIdx = 5
        
        self.history = []
        self.historyIdx = None

        if Preferences.eoErrOutNotebookStyle == 'side':
            self.notebookStyle = wxNB_LEFT
            self.tracebackText = '  '
            self.outputText = '  '
            self.errorsText = '  '

        if Preferences.eoErrOutNotebookStyle == 'text':
            self.tracebackImgIdx = self.outputImgIdx = self.errorsImgIdx = \
                  self.diffImgIdx = self.inputImgIdx = self.processesImgIdx = -1

        self._init_ctrls(parent)

        self._init_coll_statusBar_Fields(self.statusBar)
        
        self.outputTC.SetFont(Preferences.eoErrOutFont)
        self.errorTC.SetFont(Preferences.eoErrOutFont)
        self.errorTC.SetForegroundColour(wxColour(64, 0, 0))

        if Preferences.eoErrOutNotebookStyle == 'side':
            self.notebook.SetPadding(wxSize(1, 5))

        if Preferences.eoErrOutNotebookStyle != 'text':
            for img in ('Images/Shared/Traceback.png',
                        'Images/Shared/Info.png',
                        'Images/Shared/Error.png',
                        'Images/Shared/Processes.png',
                        'Images/CvsPics/Diff.png',
                        'Images/Shared/Input.png',
                       ):
                self.images.Add(Preferences.IS.load(img))
            self.notebook.AssignImageList(self.images)

        self.SetIcon(Preferences.IS.load('Images/Icons/OutputError.ico'))

        self.editor = editor
        self.vetoEvents = false
        EVT_TREE_ITEM_ACTIVATED(self.errorStackTC, wxID_ERRORSTACKMFERRORSTACKTC, self.OnErrorstacktcTreeItemActivated)
        EVT_TREE_SEL_CHANGED(self.errorStackTC, wxID_ERRORSTACKMFERRORSTACKTC, self.OnErrorstacktcTreeSelChanged)
        #EVT_LEFT_DOWN(self.errorStackTC, self.OnErrorstacktcLeftDown)

        #self.lastClick = (0, 0)

        self.menu = wxMenu()
        EVT_MENU(self, wxID_EO_LOADHIST, self.OnLoadHistory)
        self.menu.Append(wxID_EO_LOADHIST, 'Load history...')
        EVT_MENU(self, wxID_EO_SAVEHIST, self.OnSaveHistory)
        self.menu.Append(wxID_EO_SAVEHIST, 'Save history...')
        EVT_MENU(self, wxID_EO_CLRHIST, self.OnClearHistory)
        self.menu.Append(wxID_EO_CLRHIST, 'Clear history')
        self.menu.AppendSeparator()
        EVT_MENU(self, wxID_EO_CLOSEDIFF, self.OnCloseDiff)
        self.menu.Append(wxID_EO_CLOSEDIFF, 'Close diff page')
        self.menu.Enable(wxID_EO_CLOSEDIFF, false)
        EVT_MENU(self, wxID_EO_CLOSEINPT, self.OnCloseInput)
        self.menu.Append(wxID_EO_CLOSEINPT, 'Close input page')
        self.menu.Enable(wxID_EO_CLOSEINPT, false)

        EVT_RIGHT_UP(self.notebook, self.OnRightDown)

        self.processesMenu = wxMenu()
        EVT_MENU(self, wxID_EO_KILLPROC, self.OnKillProcess)
        self.processesMenu.Append(wxID_EO_KILLPROC, 'Kill process')
        self.processesMenu.AppendSeparator()
        EVT_MENU(self, wxID_EO_CHECKPROCS, self.OnCheckProcesses)
        self.processesMenu.Append(wxID_EO_CHECKPROCS, 'Check processes')

        self.displayProcesses()
        EVT_RIGHT_DOWN(self.processesPage, self.OnProcessesRightDown)

        self.winConfOption = 'errout'
        if Preferences.eoErrOutDockWindow == 'undocked':
            self.loadDims()

    def setDefaultDimensions(self):
        self.SetDimensions(0,
          Preferences.paletteHeight + Preferences.windowManagerTop + \
          Preferences.windowManagerBottom,
          Preferences.inspWidth,
          Preferences.bottomHeight)

    def addTracebackNode(self, err, parsedTracebacks):
        tree = self.errorStackTC
        root = tree.GetRootItem()
        if err.error and err.stack:
            errTI = tree.AppendItem(root, ' : '.join(err.error).strip())
            for si in err.stack:
                siTI = tree.AppendItem(errTI, '%d: %s: %s' % (si.lineNo,
                      os.path.basename(si.file), si.line.strip()))
                tree.SetPyData(siTI, si)
            if err.stack:
                tree.SetItemHasChildren(errTI, true)
                tree.SetPyData(errTI, err.stack[-1])
                parsedTracebacks += 1
        return parsedTracebacks
        

    def updateCtrls(self, errorList, outputList=None, rootName='Error',
          runningDir='', errRaw=None, addToHistory=true):
        
        if addToHistory:
            if errorList or outputList or errRaw:
                self.history.append( (errorList, outputList, rootName, 
                                      runningDir, errRaw) )
                while len(self.history) > self.historySize:
                    del self.history[0]
                self.historyIdx = None
            
        self.runningDir = runningDir
        self.tracebackType = rootName
        tree = self.errorStackTC
        tree.DeleteAllItems()
        rtTI = tree.AddRoot(rootName+'s')
        parsedTracebacks = 0
        for err in errorList:
            parsedTracebacks += self.addTracebackNode(err, parsedTracebacks)

        tree.SetItemHasChildren(rtTI, true)
        tree.Expand(rtTI)
        firstErr, cookie = tree.GetFirstChild(rtTI)
        if firstErr.IsOk():
            tree.Expand(firstErr)

        if outputList:
            self.outputTC.SetValue(''.join(outputList))
        else:
            self.outputTC.SetValue('')

        if errRaw:
            self.errorTC.SetValue(''.join(errRaw))
        else:
            self.errorTC.SetValue('')

        selIdx = -1
        if parsedTracebacks:
            selIdx = 0
        elif errorList:
            selIdx = 2
        elif outputList:
            selIdx = 1
        elif errRaw:
            selIdx = 2

        if selIdx >= 0:
            self.notebook.SetSelection(selIdx)
        
        tree.Refresh()

        return parsedTracebacks

    def display(self, errs=None):
        # XXX errs not used !
        # docked on this frame
        if self.notebook.GetParent() == self:
            self.Show()
        # docked in inspector
        elif self.notebook.GetGrandParent() == self.editor.inspector.pages:
            inspPages = self.notebook.GetGrandParent()
            inspPages.SetFocus()
            for idx in range(inspPages.GetPageCount()-1, -1, -1):
                if inspPages.GetPageText(idx) == 'ErrOut':
                    inspPages.SetSelection(idx)
                    break
        # docked in editor
        elif self.notebook.GetGrandParent() == self.editor:
            splitter = self.editor.tabsSplitter
            win2 = splitter.GetWindow2()
            if win2 and win2.GetSize().y == splitter.GetMinimumPaneSize():
                splitter.openBottomWindow()

    def appendToTextCtrl(self, tc, txt,
                         TEXTCTRL_MAXLEN=30000, TEXTCTRL_GOODLEN=20000):
        # Before appending to the output, remove old data.
        cursz = tc.GetLastPosition()
        newsz = cursz + len(txt)
        if newsz >= TEXTCTRL_MAXLEN:
            olddata = tc.GetValue()[newsz - TEXTCTRL_GOODLEN:]
            tc.SetValue(olddata)
        tc.SetFocus()
        tc.AppendText(txt)

        # XXX just make editor err out visible for now, the others would be
        # XXX too jarring
        if self.notebook.GetGrandParent() == self.editor:
            splitter = self.editor.tabsSplitter
            win2 = splitter.GetWindow2()
            if win2 and not win2.GetSize().y:
                for i in range(self.notebook.GetPageCount()):
                    # Try to show the tab where the text was just added.
                    if self.notebook.GetPage(i) == tc:
                        self.notebook.SetSelection(i)
                        tc.Refresh()
                        break
                splitter.openBottomWindow()

    def appendToOutput(self, txt):
        self.appendToTextCtrl(self.outputTC, txt)

    def appendToErrors(self, txt):
        self.appendToTextCtrl(self.errorTC, txt)

    def Destroy(self):
        self.menu.Destroy()
        self.vetoEvents = true
        wxFrame.Destroy(self)

    def findPage(self, name):
        for idx in range(self.notebook.GetPageCount()):
            if self.notebook.GetPageText(idx) == name:
                return idx
        return -1

    def displayDiff(self, diffResult):
        if not self.diffPage:
            self.diffPage = wxStyledTextCtrl(self.notebook, -1,
                style=wxSUNKEN_BORDER|wxCLIP_CHILDREN)
            self.diffPage.SetMarginWidth(1, 0)
            self.diffPage.SetLexer(wxSTC_LEX_DIFF)
            self.diffPage.StyleClearAll()
            # XXX Should be moved to StyleEditor
            fontPropStr = 'face:%s,size:%d'%(
                       Preferences.eoErrOutFont.GetFaceName(),
                       Preferences.eoErrOutFont.GetPointSize())
            for num, style in (
                  (wxSTC_DIFF_DEFAULT, fontPropStr),
                  (wxSTC_DIFF_COMMENT,  fontPropStr+',back:#EEEEFF'),      # comment
                  (wxSTC_DIFF_COMMAND,  fontPropStr+',fore:#FFFFCC,back:#000000,bold'), #diff
                  (wxSTC_DIFF_HEADER,   fontPropStr+',back:#FFFFCC'),      #"--- ","+++ ",
                  (wxSTC_DIFF_POSITION, fontPropStr+',back:#CCCCFF,bold'), #'@'
                  (wxSTC_DIFF_DELETED,  fontPropStr+',back:#FFCCCC'),      #'-'
                  (wxSTC_DIFF_ADDED,    fontPropStr+',back:#CCFFCC'),      #'+'
                 ):    
                self.diffPage.StyleSetSpec(num, style)
            self.diffPage.SetText(diffResult)
            self.notebook.AddPage(text='Diffs', select=not not diffResult,
                page=self.diffPage, imageId=self.diffImgIdx)
            self.menu.Enable(wxID_EO_CLOSEDIFF, true)
        else:
            self.diffPage.SetText(diffResult)
            if diffResult:
                pageIdx = self.findPage('Diffs')
                if pageIdx != -1:
                    self.notebook.SetSelection(pageIdx)

        self.display()

    displayPageIdx = 3
    def displayInput(self, display=true):
        if not self.inputPage:
            self.inputPage = wxTextCtrl(self.notebook, -1, value='',
                style=wxTE_MULTILINE|wxTE_RICH|wxSUNKEN_BORDER|wxCLIP_CHILDREN)
            EVT_LEFT_DCLICK(self.inputPage, self.OnInputDoubleClick)
            self.notebook.InsertPage(self.displayPageIdx, self.inputPage, 
                  'Input', true, self.inputImgIdx)
            self.menu.Enable(wxID_EO_CLOSEINPT, true)
        else:
            self.notebook.SetSelection(self.displayPageIdx)
        self.display()

    def displayProcesses(self):
        if not self.processesPage:
            self.processesPage = wxListView(self.notebook, -1, 
                  style=wxLC_LIST | wxLC_ALIGN_TOP)
            self.notebook.AddPage(self.processesPage, self.processesText,
                  false, self.processesImgIdx)
        else:
            pageIdx = self.findPage(self.processesText)
            if pageIdx != -1:
                self.notebook.SetSelection(pageIdx)
    
    def processStarted(self, name, pid, script='', processType=''):
        if self.processesPage:
            idx = self.processesPage.GetItemCount()
            if script:
                name = '%s (%s)'%(name, script)
            self.processesPage.InsertStringItem(idx, '%s : %s'%(name, pid))
            self.processesPage.SetItemData(idx, pid)
            
            self.checkProcesses()

    def processFinished(self, pid):
        if self.processesPage:
            for idx in range(self.processesPage.GetItemCount()):
                if self.processesPage.GetItemData(idx) == pid:
                    self.processesPage.DeleteItem(idx)
                    break
            self.checkProcesses()

    
    def checkProcesses(self):
        if self.processesPage:
            idxs = range(self.processesPage.GetItemCount())
            idxs.reverse()
            for idx in idxs:
                pid = self.processesPage.GetItemData(idx)
                if not wxProcess_Exists(pid):
                    self.processesPage.DeleteItem(idx)
    
    def killProcess(self, pid):
        res = wxProcess_Kill(pid, wxSIGTERM)
        if res == wxKILL_ERROR:
            res = wxProcess_Kill(pid, wxSIGKILL)
            if res == wxKILL_ERROR:
                wxLogError('Cannot kill process %d.'%pid)
                
        if res == wxKILL_ACCESS_DENIED:
            wxLogError('Cannot kill process %d, access denied.'%pid)
        elif res == wxKILL_OK:
            self.editor.setStatus('Killed process %d.'%pid) 
        
    def checkProcessesAtExit(self):
        if self.processesPage:
            self.checkProcesses()
            wxYield()
            cnt = self.processesPage.GetItemCount()
            if cnt:
                self.display()
                pageIdx = self.findPage(self.processesText)
                self.notebook.SetSelection(pageIdx)
                
                if wxMessageBox('There are still running processes that were '
                             'started from Boa, please close or kill them '
                             'before quitting.\n\nClick Cancel to quit anyway.', 
                             'Child processes running',
                             wxICON_WARNING | wxOK | wxCANCEL) == wxCANCEL:
                    return true
                return false
        return true
    
    def stepBackInHistory(self):
        if len(self.history) > 1:
            if self.historyIdx is None:
                self.historyIdx = max(len(self.history)-2, 0)
            else:
                self.historyIdx = max(self.historyIdx - 1, 0)

            self.updateCtrls(
                  *(self.history[self.historyIdx]+(false,)))

    def stepFwdInHistory(self):
        if len(self.history) > 1 and self.historyIdx is not None:
            self.historyIdx = min(self.historyIdx + 1, len(self.history)-1)

            self.updateCtrls(
                  *(self.history[self.historyIdx]+(false,)))
                
    def OnErrorstacktcTreeItemActivated(self, event):
        data = self.errorStackTC.GetPyData(event.GetItem())
        if data is None:
            return
        if data.file.find('://') != -1 or os.path.isabs(data.file):
            fn = data.file
#            elif self.app:
#                fn = os.path.join(os.path.dirname(self.app.filename), data.file)
        elif self.runningDir:
            fn = os.path.join(self.runningDir, data.file)
        else:
            print 'no running dir for relative path'
            fn = os.path.abspath(data.file)

        model, controller = self.editor.openOrGotoModule(fn)#, self.app)
        srcView = model.getSourceView()
        srcView.focus()
        srcView.gotoLine(data.lineNo - 1)
        srcView.setLinePtr(data.lineNo - 1)
        self.editor.setStatus(' : '.join(data.error), self.tracebackType)

    def OnErrorstackmfClose(self, event):
        self.Show(true)
        self.Show(false)

    def OnErrorstacktcTreeSelChanged(self, event):
        if self.vetoEvents: return
        selLine = self.errorStackTC.GetItemText(event.GetItem())
        if wxPlatform == '__WXGTK__':
            self.errorStackTC.SetToolTipString(selLine)
        self.statusBar.SetStatusText(selLine)

##    def OnErrorstacktcLeftDown(self, event):
##        self.lastClick = event.GetPosition().asTuple()
##        event.Skip()

    def OnInputDoubleClick(self, event):
        filename = self.editor.openFileDlg()
        if filename:
            from Explorers import Explorer
            self.inputPage.SetValue(Explorer.openEx(filename).load())

    def OnRightDown(self, event):
        sp = self.notebook.ClientToScreen(event.GetPosition())
        mp = self.ScreenToClient(sp)
        self.PopupMenu(self.menu, mp)

    def OnLoadHistory(self, event):
        fn = self.editor.openFileDlg('AllFiles')
        if fn:
            from Explorers import Explorer
            data = Explorer.openEx(fn).load()
            self.history = pickle.loads(data)

    def OnSaveHistory(self, event):
        fn, ok = self.editor.saveAsDlg('history.pcl', 'AllFiles')
        if ok:
            data = pickle.dumps(self.history)
            from Explorers import Explorer
            n = Explorer.openEx(fn)
            n.save(n.resourcepath, data)
            
    def OnCloseDiff(self, event):
        if self.diffPage:
            pageIdx = self.findPage('Diffs')
            if pageIdx != -1:
                self.notebook.DeletePage(pageIdx)
                self.diffPage = None
                self.menu.Enable(wxID_EO_CLOSEDIFF, false)

    def OnCloseInput(self, event):
        if self.inputPage:
            self.notebook.DeletePage(3)
            self.inputPage = None
            self.menu.Enable(wxID_EO_CLOSEINPT, false)
            

    def OnClearHistory(self, event):
        self.updateCtrls([], addToHistory=false)
        self.history = []
        self.historyIdx = None
        
        self.editor.setStatus('History cleared.')

    def OnProcessesRightDown(self, event):
##        event.Skip()
##        wxYield()
        sp = self.processesPage.ClientToScreen(event.GetPosition())
        mp = self.ScreenToClient(sp)
        self.PopupMenu(self.processesMenu, mp)

    def OnKillProcess(self, event):
        if self.processesPage:
            idx = self.processesPage.GetFirstSelected()
            while idx != -1:
                pid = self.processesPage.GetItemData(idx)
                self.killProcess(pid)
                
                idx = self.processesPage.GetNextSelected(idx)

        self.checkProcesses()

    def OnCheckProcesses(self, event):
        if self.processesPage:
            self.checkProcesses()


if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    frame = ErrorStackMF(None, None)
    frame.Show(true)
    app.MainLoop()
