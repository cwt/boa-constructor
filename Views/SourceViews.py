#----------------------------------------------------------------------
# Name:        SourceViews.py
# Purpose:     Views for editing source code
#
# Author:      Riaan Booysen
#
# Created:     2000/05/05
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2001 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

import os, string, time

from wxPython.wx import *
from wxPython.stc import *

import EditorViews, ProfileView, Search, Help, Preferences, Utils
from StyledTextCtrls import PythonStyledTextCtrlMix, BrowseStyledTextCtrlMix, \
      HTMLStyledTextCtrlMix, XMLStyledTextCtrlMix, FoldingStyledTextCtrlMix, \
      CPPStyledTextCtrlMix, TextSTCMix, ConfigSTCMix, idWord, object_delim
from Preferences import keyDefs
import Utils

endOfLines = {  wxSTC_EOL_CRLF : '\r\n',
                wxSTC_EOL_CR : '\r',
                wxSTC_EOL_LF : '\n'}

brkPtMrk, stepPosMrk, tmpBrkPtMrk, markPlaceMrk = range(1, 5)

[wxID_CPPSOURCEVIEW, wxID_HTMLSOURCEVIEW, wxID_XMLSOURCEVIEW, wxID_TEXTVIEW,
 wxID_CONFIGVIEW, wxID_SOURCECUT, wxID_SOURCECOPY, wxID_SOURCEPASTE, 
 wxID_SOURCEUNDO, wxID_SOURCEREDO] \
 = Utils.wxNewIds(10)

class EditorStyledTextCtrl(wxStyledTextCtrl, EditorViews.EditorView):
    refreshBmp = 'Images/Editor/Refresh.bmp'
    undoBmp = 'Images/Shared/Undo.bmp'
    redoBmp = 'Images/Shared/Redo.bmp'
    cutBmp = 'Images/Shared/Cut.bmp'
    copyBmp = 'Images/Shared/Copy.bmp'
    pasteBmp = 'Images/Shared/Paste.bmp'
    findBmp = 'Images/Shared/Find.bmp'
    findAgainBmp = 'Images/Shared/FindAgain.bmp'
    def __init__(self, parent, wId, model, actions, defaultAction = -1):
        wxStyledTextCtrl.__init__(self, parent, wId, style = wxCLIP_CHILDREN | wxSUNKEN_BORDER)
        a =  (('Refresh', self.OnRefresh, self.refreshBmp, keyDefs['Refresh']),
              ('-', None, '', ()),
              ('Undo', self.OnEditUndo, self.undoBmp, ()),
              ('Redo', self.OnEditRedo, self.redoBmp, ()),
              ('-', None, '', ()),
              ('Cut', self.OnEditCut, self.cutBmp, ()),
              ('Copy', self.OnEditCopy, self.copyBmp, ()),
              ('Paste', self.OnEditPaste, self.pasteBmp, ()),
              ('-', None, '', ()),
              ('Find', self.OnFind, self.findBmp, keyDefs['Find']),
              ('Find again', self.OnFindAgain, self.findAgainBmp, keyDefs['FindAgain']),
              ('Mark place', self.OnMarkPlace, '-', keyDefs['MarkPlace']),
              ('Goto line', self.OnGotoLine, '-', keyDefs['GotoLine']),
              )

        EditorViews.EditorView.__init__(self, model, a + actions, defaultAction)

        self.SetEOLMode(wxSTC_EOL_LF)
        self.eol = endOfLines[self.GetEOLMode()]

        self.pos = 0
        self.stepPos = 0
        self.nonUserModification  = false

        self.lastSearchResults = []
        self.lastSearchPattern = ''
        self.lastMatchPosition = None

        ## Install the handler for refreshs.
        if wxPlatform == '__WXGTK__':
            self.paint_handler = Utils.PaintEventHandler(self)

        self.lastStart = 0
        self._blockUpdate = false
        self._marking = false
        
        #self.findReplacer = FindReplace.STCFindReplacer(self)

        markIdnt, markBorder, markCenter = Preferences.STCMarkPlaceMarker
        self.MarkerDefine(markPlaceMrk, markIdnt, markBorder, markCenter)

    def getModelData(self):
        return self.model.data

    def setModelData(self, data):
        self.model.data = data
    
    def saveNotification(self):
        if not Preferences.neverEmptyUndoBuffer:
            self.EmptyUndoBuffer()

    def refreshCtrl(self):
        #print 'refreshCtrl'
        if wxPlatform == '__WXGTK__':
            self.NoUpdateUI = 1  ## disable event handler
        # set whole document to current EOL style fixing mixed CRLF/LF code that
        # can be introduced by pasting from the clipboard
###       doesn't work in the wxSTC yet
##        print 'converting', self.GetEOLMode()
##        self.ConvertEOLs()
        self.pos = self.GetCurrentPos()

        ## This code prevents circular updates on GTK
        ## It is not important under windows as the windows refresh
        ## code is more efficient.
        try:
            if self.noredraw == 1: redraw = 0
            else: redraw = 1
        except:
            redraw=1
        if redraw == 1:
            prevVsblLn = self.GetFirstVisibleLine()
            self._blockUpdate = true
            try:
                newData = self.getModelData()
                txtLen = self.GetTextLength()
                if txtLen and newData[:-1] != self.GetText() or not txtLen:
                    self.SetText(newData)
                    # prevent blank editor in undo history
                    if not txtLen:
                        self.EmptyUndoBuffer()
                self.GotoPos(self.pos)
                curVsblLn = self.GetFirstVisibleLine()
                self.LineScroll(0, prevVsblLn - curVsblLn)
            finally:
                self._blockUpdate = false

            #self.EmptyUndoBuffer()

        self.SetSavePoint()
        self.nonUserModification = false
        self.updatePageName()
        self.NoUpdateUI = 0  ## Enable event handler

        if self.model.transport:
            self.SetReadOnly(self.model.transport.stdAttrs['read-only'])

    def refreshModel(self):
        if self.isModified():
            self.model.modified = true
        self.nonUserModification = false
    
        pos = self.GetCurrentPos()
        prevVsblLn = self.GetFirstVisibleLine()

        # hack to stop wxSTC from eating the last character
        self.InsertText(self.GetTextLength(), ' ')
        self.setModelData(self.GetText())
        self.Undo()
        
        self.GotoPos(pos)
        curVsblLn = self.GetFirstVisibleLine()
        self.LineScroll(0, prevVsblLn - curVsblLn)
        
        self.SetSavePoint()
        if wxPlatform == '__WXGTK__':
            # We are updating the model from the editor view.
            # this flag is to prevent  the model updating the view
            self.noredraw = 1
        EditorViews.EditorView.refreshModel(self)
        self.noredraw = 0

        # Remove from modified views list
        if self.model.viewsModified.count(self.viewName):
            self.model.viewsModified.remove(self.viewName)

        self.updateEditor()

    def gotoLine(self, lineno, offset = -1):
        self.GotoLine(lineno)
        vl = self.GetFirstVisibleLine()
        self.LineScroll(0, lineno -  vl)
        if offset != -1: self.SetCurrentPos(self.GetCurrentPos()+offset+1)

    def selectSection(self, lineno, start, word):
        self.gotoLine(lineno)
        length = len(word)
        startPos = self.PositionFromLine(lineno) + start
        endPos = startPos + length
        self.SetSelection(startPos, endPos)

        self.SetFocus()

    def selectLine(self, lineno):
        self.GotoLine(lineno)
        sp = self.PositionFromLine(lineno)
        ep = self.PositionFromLine(lineno+1)-1
        self.SetSelection(sp, ep)

    def updatePageName(self):
        if hasattr(self, 'notebook'):
            currName = self.notebook.GetPageText(self.pageIdx)
            
            if self.isModified(): newName = '~%s~' % self.viewName
            else: newName = self.viewName
    
            if currName != newName:
                if newName == self.viewName:
                    if self.model.viewsModified.count(self.viewName):
                        self.model.viewsModified.remove(self.viewName)
                else:
                    if not self.model.viewsModified.count(self.viewName):
                        self.model.viewsModified.append(self.viewName)
                self.notebook.SetPageText(self.pageIdx, newName)
    # XXX check if this makes a difference
    #            self.notebook.Refresh()
                self.updateEditor()

##    def updateStatusBar(self):
##        pos = self.GetCurrentPos()
##        ln = self.LineFromPosition(pos)
##        st = pos - self.PositionFromLine(ln)

    def updateEditor(self):
        self.model.editor.updateModulePage(self.model)
        self.model.editor.updateTitle()

    def updateViewState(self):
        self.updatePageName()

    def insertCodeBlock(self, text):
        cp = self.GetCurrentPos()
        ln = self.LineFromPosition(cp)
        indent = cp - self.PositionFromLine(ln)
        lns = string.split(text, self.eol)
        # XXX adapt for tab mode
        text = string.join(lns, self.eol+indent*' ')

        selTxtPos = string.find(text, '# Your code')
        self.InsertText(cp, text)
        self.nonUserModification = true
        self.updateViewState()
        self.SetFocus()
        if selTxtPos != -1:
            self.SetSelection(cp + selTxtPos, cp + selTxtPos + 11)

    def isModified(self):
        return self.GetModify() or self.nonUserModification

#---Block commands----------------------------------------------------------

    def reselectSelectionAsBlock(self):
        selStartPos, selEndPos = self.GetSelection()
        selStartLine = self.LineFromPosition(selStartPos)
        startPos = self.PositionFromLine(selStartLine)
        selEndLine = self.LineFromPosition(selEndPos)
        if selEndPos != self.PositionFromLine(selEndLine):
            selEndLine = selEndLine + 1
        endPos = self.PositionFromLine(selEndLine)
        self.SetSelection(startPos, endPos)
        return selStartLine, selEndLine

    def processSelectionBlock(self, func):
        if self.GetUseTabs():
            indtBlock = '\t'
        else:
            indtBlock = self.GetTabWidth()*' '
            
        self.BeginUndoAction()
        try:
            sls, sle = self.reselectSelectionAsBlock()
            textLst = func(string.split(self.GetSelectedText(), self.eol), indtBlock)[:-1]
            self.ReplaceSelection(string.join(textLst, self.eol)+self.eol)
            if sle > sls:
                self.SetSelection(self.PositionFromLine(sls),
                  self.PositionFromLine(sle)-1)
        finally:
            self.EndUndoAction()

    def getSelectionAsLineNumbers(self):
        selStartPos, selEndPos = self.GetSelection()
        selStartLine = self.LineFromPosition(selStartPos)
        selEndLine = self.LineFromPosition(selEndPos)
        
        return range(self.LineFromPosition(selStartPos), 
              self.LineFromPosition(selEndPos))
        
#-------Canned events-----------------------------------------------------------

    def OnRefresh(self, event):
        self.refreshModel()

    def OnEditCut(self, event):
        self.Cut()

    def OnEditCopy(self, event):
        self.Copy()

    def OnEditPaste(self, event):
        self.Paste()

    def OnEditUndo(self, event):
        self.Undo()

    def OnEditRedo(self, event):
        self.Redo()

    # XXX
    def doFind(self, pattern):
        self.lastSearchResults = Search.findInText(\
          string.split(self.GetText(), self.eol), pattern, false)
        self.lastSearchPattern = pattern
        if len(self.lastSearchResults):
            self.lastMatchPosition = 0

    def doNextMatch(self):
        if self.lastMatchPosition is not None and \
          len(self.lastSearchResults) > self.lastMatchPosition:
            pos = self.lastSearchResults[self.lastMatchPosition]
            self.model.editor.addBrowseMarker(self.GetCurrentLine())
            self.selectSection(pos[0], pos[1], self.lastSearchPattern)
            self.lastMatchPosition = self.lastMatchPosition + 1
        else:
            dlg = wxMessageDialog(self.model.editor,
                  'No%smatches'% (self.lastMatchPosition is not None and ' further ' or ' '),
                  'Find in module', wxOK | wxICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.lastMatchPosition = None

    def OnFind(self, event):
        import FindReplaceDlg
        FindReplaceDlg.find(self, self.model.editor.finder, self)

    def OnFindAgain(self, event):
        import FindReplaceDlg
        FindReplaceDlg.findAgain(self, self.model.editor.finder, self)
        
##        if self.model.editor.finder.lastFind == "":
##            self.OnFind(event)
##        else:
##            self.model.editor.finder.findNextInSource(self)

##    def OnFind(self, event):
##        s, e = self.GetSelection()
##        if s == e:
##            txt = self.lastSearchPattern
##        else:
##            txt = self.GetSelectedText()
##        self.findReplacer.Find(txt)
##
##    def OnFindAgain(self, event):
##        self.findReplacer.FindNext()

    def OnMarkPlace(self, event):
        if self._marking : return
        self._marking = true
        try:
            lineno = self.LineFromPosition(self.GetCurrentPos())
            self.MarkerAdd(lineno, markPlaceMrk)
            self.model.editor.addBrowseMarker(lineno)
            # Encourage a redraw
            wxYield()
            self.MarkerDelete(lineno, markPlaceMrk)
        finally:
            self._marking = false
            

    def OnGotoLine(self, event):
        dlg = wxTextEntryDialog(self, 'Enter line number:', 'Goto line', '')
        try:
            if dlg.ShowModal() == wxID_OK:
                if dlg.GetValue():
                    self.GotoLine(int(dlg.GetValue()))
        finally:
            dlg.Destroy()

    def OnUpdateUI(self, event):
        if hasattr(self, 'pageIdx'):
            self.updateViewState()

class PythonDisView(EditorStyledTextCtrl, PythonStyledTextCtrlMix):
    viewName = 'Disassemble'
    breakBmp = 'Images/Debug/Breakpoints.bmp'
    def __init__(self, parent, model):
        wxID_PYTHONDISVIEW = wxNewId()

        EditorStyledTextCtrl.__init__(self, parent, wxID_PYTHONDISVIEW,
          model, (), -1)
        PythonStyledTextCtrlMix.__init__(self, wxID_PYTHONDISVIEW, -1)

        self.SetReadOnly(true)
        self.active = true

    def refreshModel(self):
        # Do not update model
        pass

    def getModelData(self):
        return self.model.disassembleSource()

    def setModelData(self, data):
        pass

class HTMLSourceView(EditorStyledTextCtrl, HTMLStyledTextCtrlMix):
    viewName = 'HTML'
    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_HTMLSOURCEVIEW,
          model, (), -1)
        HTMLStyledTextCtrlMix.__init__(self, wxID_HTMLSOURCEVIEW)
        self.active = true

class XMLSourceView(EditorStyledTextCtrl, XMLStyledTextCtrlMix):
    viewName = 'XML'
    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_XMLSOURCEVIEW,
          model, (), -1)
        XMLStyledTextCtrlMix.__init__(self, wxID_XMLSOURCEVIEW)
        self.active = true

class CPPSourceView(EditorStyledTextCtrl, CPPStyledTextCtrlMix):
    viewName = 'Source'
    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_CPPSOURCEVIEW,
          model, (), -1)
        CPPStyledTextCtrlMix.__init__(self, wxID_CPPSOURCEVIEW)
        self.active = true

class HPPSourceView(CPPSourceView):
    viewName = 'Header'
    def __init__(self, parent, model):
        CPPSourceView.__init__(self, parent, model)

    def refreshCtrl(self):
        self.pos = self.GetCurrentPos()
        prevVsblLn = self.GetFirstVisibleLine()

        self.SetText(self.model.headerData)
        self.EmptyUndoBuffer()
        self.GotoPos(self.pos)
        curVsblLn = self.GetFirstVisibleLine()
        self.LineScroll(0, prevVsblLn - curVsblLn)

        self.nonUserModification = false
        self.updatePageName()


class TextView(EditorStyledTextCtrl, TextSTCMix):
    viewName = 'Text'
    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_TEXTVIEW, model, (), -1)
        TextSTCMix.__init__(self, wxID_TEXTVIEW)
        self.active = true

class ConfigView(EditorStyledTextCtrl, ConfigSTCMix):
    viewName = 'Config'
    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_CONFIGVIEW, model, (), -1)
        ConfigSTCMix.__init__(self, wxID_CONFIGVIEW)
        self.active = true
