#-----------------------------------------------------------------------------
# Name:        ErrorStackFrm.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2001
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2002 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
##Boa:Frame:ErrorStackMF
# remove between #-- comments before editing visually

import os, string

from wxPython.wx import *
from wxPython.stc import *

import Preferences, Utils

[wxID_ERRORSTACKMFSTATUSBAR, wxID_ERRORSTACKMFERRORSTACKTC, wxID_ERRORSTACKMF, wxID_ERRORSTACKMFNOTEBOOK1, wxID_ERRORSTACKMFOUTPUTTC, wxID_ERRORSTACKMFERRORTC] = map(lambda _init_ctrls: wxNewId(), range(6))

class ErrorStackMF(wxFrame, Utils.FrameRestorerMixin):
    def _init_coll_notebook1_Pages(self, parent):

        parent.AddPage(strText = self.tracebackText, bSelect = true, pPage = self.errorStackTC, imageId = self.tracebackImgIdx)
        parent.AddPage(strText = self.outputText, bSelect = false, pPage = self.outputTC, imageId = self.outputImgIdx)
        parent.AddPage(strText = self.errorsText, bSelect = false, pPage = self.errorTC, imageId = self.errorsImgIdx)

    def _init_coll_statusBar_Fields(self, parent):
        parent.SetFieldsCount(1)

        parent.SetStatusText(text = '', i = 0)

        parent.SetStatusWidths([-1])

    def _init_utils(self):
        self.images = wxImageList(16, 16)

    def _init_ctrls(self, prnt):
        wxFrame.__init__(self, size = wxSize(330, 443), id = wxID_ERRORSTACKMF, title = 'Traceback and Output browser', parent = prnt, name = 'ErrorStackMF', style = wxDEFAULT_FRAME_STYLE | wxFRAME_TOOL_WINDOW, pos = wxPoint(464, 228))
        self._init_utils()
        EVT_CLOSE(self, self.OnErrorstackmfClose)

        self.notebook1 = wxNotebook(size = wxSize(330, 418), id = wxID_ERRORSTACKMFNOTEBOOK1, parent = self, name = 'notebook1', style = self.notebookStyle, pos = wxPoint(0, 0))

        self.statusBar = wxStatusBar(id = wxID_ERRORSTACKMFSTATUSBAR, parent = self, name = 'statusBar', style = 0)
        self._init_coll_statusBar_Fields(self.statusBar)
        self.SetStatusBar(self.statusBar)

        self.outputTC = wxTextCtrl(size = wxSize(326, 384), value = '', pos = wxPoint(0, 0), parent = self.notebook1, name = 'outputTC', style = wxTE_MULTILINE | wxTE_RICH, id = wxID_ERRORSTACKMFOUTPUTTC)

        self.errorTC = wxTextCtrl(size = wxSize(326, 384), value = '', pos = wxPoint(0, 0), parent = self.notebook1, name = 'errorTC', style = wxTE_MULTILINE | wxTE_RICH, id = wxID_ERRORSTACKMFERRORTC)
        self.errorTC.SetForegroundColour(wxColour(64, 0, 0))

        #--
        # Special case to fix GTK redraw problem
        if wxPlatform == '__WXGTK__':
            prxy, errorStackTC = Utils.wxProxyPanel(self.notebook1, wxTreeCtrl, size = wxSize(312, 390), id = wxID_ERRORSTACKMFERRORSTACKTC, name = 'errorStackTC', validator = wxDefaultValidator, style = wxTR_HAS_BUTTONS | wxSUNKEN_BORDER, pos = wxPoint(0, 0))
            self.errorStackTC = prxy
            self._init_coll_notebook1_Pages(self.notebook1)
            self.errorStackTC = errorStackTC
        else:
            self.errorStackTC = wxTreeCtrl(size = wxSize(312, 390), id = wxID_ERRORSTACKMFERRORSTACKTC, parent = self.notebook1, name = 'errorStackTC', validator = wxDefaultValidator, pos = wxPoint(4, 22))
            self._init_coll_notebook1_Pages(self.notebook1)
        #--

    def __init__(self, parent, editor):
        self.notebookStyle = 0
        self.tracebackImgIdx = 0
        self.tracebackText = 'Tracebacks'
        self.outputImgIdx = 1
        self.outputText = 'Output'
        self.errorsImgIdx = 2
        self.errorsText = 'Errors'
        
        self.diffPage = None
        self.diffImgIdx = 3

        #Preferences.childFrameStyle
        if Preferences.eoErrOutNotebookStyle == 'side':
            self.notebookStyle = wxNB_LEFT
            self.tracebackText = '  '
            self.outputText = '  '
            self.errorsText = '  '

        if Preferences.eoErrOutNotebookStyle == 'text':
            self.tracebackImgIdx = self.outputImgIdx = self.errorsImgIdx = \
                  self.diffImgIdx = -1

        self._init_ctrls(parent)

        if Preferences.eoErrOutNotebookStyle == 'side':
            self.notebook1.SetPadding(wxSize(1, 5))

        if Preferences.eoErrOutNotebookStyle != 'text':
            for img in ('Images/Shared/Traceback.png',
                        'Images/Shared/Info.png',
                        'Images/Shared/Error.png',
                        'Images/CVSPics/Diff.png'):
                self.images.Add(Preferences.IS.load(img))
            self.notebook1.AssignImageList(self.images)

        self.SetIcon(Preferences.IS.load('Images/Icons/OutputError.ico'))

        self.app = None
        self.editor = editor
        self.vetoEvents = false
        EVT_TREE_ITEM_ACTIVATED(self.errorStackTC, wxID_ERRORSTACKMFERRORSTACKTC, self.OnErrorstacktcTreeItemActivated)
        EVT_TREE_SEL_CHANGED(self.errorStackTC, wxID_ERRORSTACKMFERRORSTACKTC, self.OnErrorstacktcTreeSelChanged)
        EVT_LEFT_DOWN(self.errorStackTC, self.OnErrorstacktcLeftDown)

        self.winConfOption = 'errout'
        self.loadDims()
        
        self.lastClick = (0, 0)

    def setDefaultDimensions(self):
        self.SetDimensions(0,
          Preferences.paletteHeight + Preferences.windowManagerTop + \
          Preferences.windowManagerBottom,
          Preferences.inspWidth,
          Preferences.bottomHeight)

    def updateCtrls(self, errorList, outputList=None, rootName='Error',
          runningDir='', errRaw=None):
        self.runningDir = runningDir
        self.tracebackType = rootName
        tree = self.errorStackTC
        tree.DeleteAllItems()
        rtTI = tree.AddRoot(rootName+'s')
        parsedTracebacks = 0
        for err in errorList:
            if err.error and err.stack:
                errTI = tree.AppendItem(rtTI, string.strip(string.join(err.error, ' : ')))
                for si in err.stack:
                    siTI = tree.AppendItem(errTI, '%d: %s: %s' % (si.lineNo,
                          os.path.basename(si.file), string.strip(si.line)))
                    tree.SetPyData(siTI, si)
                if err.stack:
                    tree.SetItemHasChildren(errTI, true)
                    tree.SetPyData(errTI, err.stack[-1])
                    parsedTracebacks = parsedTracebacks + 1
                    
        tree.SetItemHasChildren(rtTI, true)
        tree.Expand(rtTI)
        cookie = 0; firstErr, cookie = tree.GetFirstChild(rtTI, cookie)
        if firstErr.IsOk():
            tree.Expand(firstErr)

        if outputList:
            self.outputTC.SetValue(string.join(outputList, ''))
        else:
            self.outputTC.SetValue('')

        if errRaw:
            self.errorTC.SetValue(string.join(errRaw, ''))
        else:
            self.errorTC.SetValue('')

        if parsedTracebacks: 
            selIdx = 0
        elif errorList:
            selIdx = 2
        else:
            selIdx = 1
        self.notebook1.SetSelection(selIdx)
        
        return parsedTracebacks

    def display(self, errs):
        # XXX errs not used !
        # docked on this frame
        if self.notebook1.GetParent() == self:
            self.Show()
        # docked in inspector
        elif self.notebook1.GetGrandParent() == self.editor.inspector.pages:
            inspPages = self.notebook1.GetGrandParent()
            inspPages.SetFocus()
            for idx in range(inspPages.GetPageCount()-1, -1, -1):
                if inspPages.GetPageText(idx) == 'ErrOut':
                    inspPages.SetSelection(idx)
                    break
        # docked in editor
        elif self.notebook1.GetGrandParent() == self.editor:
            splitter = self.editor.tabsSplitter
            win2 = splitter.GetWindow2()
            if win2 and not win2.GetSize().y:
                splitter.openBottomWindow()

    def Destroy(self):
        self.vetoEvents = true
        wxFrame.Destroy(self)

    def displayDiff(self, diffResult):
        if not self.diffPage:
            self.diffPage = wxStyledTextCtrl(self.notebook1, -1)
            self.diffPage.SetMarginWidth(1, 0)
            self.diffPage.SetLexer(wxSTC_LEX_DIFF)
            self.diffPage.StyleClearAll()
            for num, style in (
                  (2, 'fore:#FFFFCC,back:#000000,bold'), #diff
                  (3, 'back:#FFFFCC'), #"--- ","+++ ",
                  (4, 'back:#CCCCFF,bold'),#'@'
                  (5, 'back:#FFCCCC'),#'-'
                  (6, 'back:#CCFFCC') ): #'+'
                self.diffPage.StyleSetSpec(num, style)
            self.diffPage.SetText(diffResult)
            self.notebook1.AddPage(strText='Diffs', bSelect=true, 
                pPage=self.diffPage, imageId=self.diffImgIdx)
        else:
            self.diffPage.SetText(diffResult)
            self.notebook1.SetSelection(3)

    def OnErrorstacktcTreeItemActivated(self, event):
        try:
            data = self.errorStackTC.GetPyData(event.GetItem())
            if data is None:
                return
            if self.app:
                fn = os.path.join(os.path.dirname(self.app.filename), data.file)
            elif self.runningDir:
                fn = os.path.join(self.runningDir, data.file)
            else:
                fn = os.path.abspath(data.file)
            model, controller = self.editor.openOrGotoModule(fn, self.app)
            model.views['Source'].focus()
            model.views['Source'].SetFocus()
            model.views['Source'].gotoLine(data.lineNo - 1)
            model.views['Source'].setLinePtr(data.lineNo - 1)
            self.editor.statusBar.setHint(string.join(data.error, ' : '),
                self.tracebackType)
#            self.Lower()
#            self.editor.Raise()
#            self.editor.Focus()
#                self.editor.statusBar.setHint('%s: %s'% (err[-1].error[0], err[-1].error[0])
        finally:
#            pass
            event.Skip()

    def OnErrorstackmfClose(self, event):
        self.Show(true)
        self.Show(false)

    def OnErrorstacktcTreeSelChanged(self, event):
        if self.vetoEvents: return
        selLine = self.errorStackTC.GetItemText(event.GetItem())
        if wxPlatform == '__WXGTK__':
            self.errorStackTC.SetToolTipString(selLine)
        self.statusBar.SetStatusText(selLine)

    def OnErrorstacktcLeftDown(self, event):
        self.lastClick = event.GetPosition().asTuple()
        event.Skip()


if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    frame = ErrorStackMF(None, None)
    frame.Show(true)
    app.MainLoop()
