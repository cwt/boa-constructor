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

import os, string, time, dis

from wxPython.wx import *
from wxPython.stc import *

import EditorViews, ProfileView, Search, Help, Preferences, Utils
from StyledTextCtrls import PythonStyledTextCtrlMix, BrowseStyledTextCtrlMix, HTMLStyledTextCtrlMix, XMLStyledTextCtrlMix, FoldingStyledTextCtrlMix, CPPStyledTextCtrlMix, idWord, new_stc, old_stc, object_delim
from PrefsKeys import keyDefs

indentLevel = 4
endOfLines = {  wxSTC_EOL_CRLF : '\r\n',
                wxSTC_EOL_CR : '\r',
                wxSTC_EOL_LF : '\n'}

brkPtMrk = 1
stepPosMrk = 2
tmpBrkPtMrk = 3
markPlaceMrk = 4
#brwsIndc = 0

#wxID_PYTHONSOURCEVIEW,
[wxID_CPPSOURCEVIEW, wxID_HTMLSOURCEVIEW, wxID_XMLSOURCEVIEW, wxID_TEXTVIEW,
 wxID_SOURCECUT, wxID_SOURCECOPY, wxID_SOURCEPASTE, wxID_SOURCEUNDO,
 wxID_SOURCEREDO] \
 = map(lambda x: wxNewId(), range(9))

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

        #self.SetCaretPeriod(0)

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

        self.MarkerDefine(markPlaceMrk, wxSTC_MARK_SHORTARROW, 'NAVY', 'YELLOW')


    def setReadOnly(self, val):
        EditorViews.EditorView.readOnly(self, val)
        self.SetEditable(val)

    def getModelData(self):
        return self.model.data

    def setModelData(self, data):
        self.model.data = data

    def refreshCtrl(self):
        if wxPlatform == '__WXGTK__':
            self.NoUpdateUI = 1  ## disable event handler
        # set whole document to current EOL style fixing mixed CRLF/LF code that
        # can be introduced by pasting from the clipboard
##        print 'converting', self.GetEOLMode()
##        self.ConvertEOLs()
        self.pos = self.GetCurrentPos()
#        line = self.GetCurrentLine()

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
            self.SetText(self.getModelData())
            self.EmptyUndoBuffer()
            self.GotoPos(self.pos)
            curVsblLn = self.GetFirstVisibleLine()
            self.ScrollBy(0, prevVsblLn - curVsblLn)

        self.nonUserModification = false
        self.updatePageName()
        self.NoUpdateUI = 0  ## Enable event handler

    def refreshModel(self):
        if self.isModified():
            self.model.modified = true
        self.nonUserModification = false

        # hack to stop wxSTC from eating the last character
        self.InsertText(self.GetTextLength(), ' ')

        self.setModelData(self.GetText())
        self.EmptyUndoBuffer()
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
        self.ScrollBy(0, lineno -  vl)
        if offset != -1: self.SetCurrentPosition(self.GetCurrentPos()+offset+1)

    def selectSection(self, lineno, start, word):
        self.gotoLine(lineno)
        length = len(word)
        startPos = self.GetLineStartPos(lineno) + start
        endPos = startPos + length
        self.SetSelection(startPos, endPos)

        self.SetFocus()

    def selectLine(self, lineno):
        self.GotoLine(lineno)
        sp = self.GetLineStartPos(lineno)
        ep = self.GetLineStartPos(lineno+1)-1
        self.SetSelection(sp, ep)

    def updatePageName(self):
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

    def updateStatusBar(self):
        pos = self.GetCurrentPos()
        ln = self.GetLineFromPos(pos)
        st = pos - self.GetLineStartPos(ln)
#        self.model.editor.updateStatusRowCol(st + 1, ln + 1)

    def updateEditor(self):
        self.model.editor.updateModulePage(self.model)
        self.model.editor.updateTitle()

    def updateViewState(self):
        self.updatePageName()
#        self.updateStatusBar()

    def insertCodeBlock(self, text):
        cp = self.GetCurrentPos()
        ln = self.GetLineFromPos(cp)
        indent = cp - self.GetLineStartPos(ln)
        lns = string.split(text, self.eol)
        text = string.join(lns, self.eol+indent*' ')

        selTxtPos = string.find(text, '# Your code')
        self.InsertText(cp, text)
        self.nonUserModification = true
        self.updateViewState()
        self.SetFocus()
        if selTxtPos != -1:
            self.SetSelection(cp + selTxtPos, cp + selTxtPos + 11)

    def isModified(self):
        return self.GetModified() or self.nonUserModification

#---Block commands----------------------------------------------------------

    def reselectSelectionAsBlock(self):
        selStartPos, selEndPos = self.GetSelection()
        selStartLine = self.GetLineFromPos(selStartPos)
        startPos = self.GetLineStartPos(selStartLine)
        selEndLine = self.GetLineFromPos(selEndPos)
        if selEndPos != self.GetLineStartPos(selEndLine):
            selEndLine = selEndLine + 1
        endPos = self.GetLineStartPos(selEndLine)
#        if endPos > startPos: endPos = endPos -1
        self.SetSelection(startPos, endPos)
        return selStartLine, selEndLine

    def processSelectionBlock(self, func):
        self.BeginUndoAction()
        try:
            sls, sle = self.reselectSelectionAsBlock()
            textLst = func(string.split(self.GetSelectedText(), self.eol))[:-1]
            self.ReplaceSelection(string.join(textLst, self.eol)+self.eol)
            if sle > sls:
                self.SetSelection(self.GetLineStartPos(sls),
                  self.GetLineStartPos(sle)-1)
        finally:
            self.EndUndoAction()

#-------Canned events-----------------------------------------------------------

    def OnRefresh(self, event):
        self.refreshModel()

    def OnEditCut(self, event):
        self.Cut()

    def OnEditCopy(self, event):
        self.Copy()

    def OnEditPaste(self, event):
        # Fix the eol characters
        # XXX THis is not useful as a paste from the keyboard does not trigger this
##        text = Utils.readTextFromClipboard()
##        newText = string.replace(text, '\r\n', '\n')
##        if newText != text:
##            Utils.writeTextToClipboard(newText)

        self.Paste()

    def OnEditUndo(self, event):
        self.Undo()

    def OnEditRedo(self, event):
        self.Redo()

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
        s, e = self.GetSelection()
        if s == e:
            txt = self.lastSearchPattern
        else:
            txt = self.GetSelectedText()
        dlg = wxTextEntryDialog(self.model.editor, 'Enter text:',
          'Find in module', txt)
        try:
            if wxPlatform == '__WXMSW__':
                te = Utils.getCtrlsFromDialog(dlg, 'wxTextCtrlPtr')[0]
                te.SetSelection(0, len(txt))
            if dlg.ShowModal() == wxID_OK:
                self.doFind(dlg.GetValue())
            else:
                return
        finally:
            dlg.Destroy()

        self.doNextMatch()

    def OnFindAgain(self, event):
        if self.lastMatchPosition is None:
            self.OnFind(event)
        else:
            self.doNextMatch()

    def OnMarkPlace(self, event):
        lineno = self.GetLineFromPos(self.GetCurrentPos())
        self.MarkerAdd(lineno, markPlaceMrk)
        self.model.editor.addBrowseMarker(lineno)
        # Encourage a redraw
        wxYield()
        self.MarkerDelete(lineno, markPlaceMrk)

    def OnGotoLine(self, event):
        dlg = wxTextEntryDialog(self, 'Enter line number:', 'Goto line', '')
        try:
            if dlg.ShowModal() == wxID_OK:
                if dlg.GetValue():
                    self.GotoLine(int(dlg.GetValue()))
        finally:
            dlg.Destroy()


class PythonDisView(EditorStyledTextCtrl, PythonStyledTextCtrlMix):#, BrowseStyledTextCtrlMix, FoldingStyledTextCtrlMix):
    viewName = 'Disassemble'
    breakBmp = 'Images/Debug/Breakpoints.bmp'
    def __init__(self, parent, model):
        wxID_PYTHONDISVIEW = wxNewId()

        EditorStyledTextCtrl.__init__(self, parent, wxID_PYTHONDISVIEW,
          model, (), -1)
        PythonStyledTextCtrlMix.__init__(self, wxID_PYTHONDISVIEW, -1)

##        self.SetMarginType(1, wxSTC_MARGIN_SYMBOL)
##        self.SetMarginWidth(1, 12)
##        self.SetMarginSensitive(1, true)
##        self.MarkerDefine(brkPtMrk, wxSTC_MARK_CIRCLE, 'BLACK', 'RED')
##        self.MarkerDefine(stepPosMrk, wxSTC_MARK_SHORTARROW, 'NAVY', 'BLUE')
##        self.MarkerDefine(tmpBrkPtMrk, wxSTC_MARK_CIRCLE, 'BLACK', 'BLUE')
#        self.setReadOnly(true)
        self.active = true

    def refreshModel(self):
        # Do not update model
        pass

    def getModelData(self):
        try:
            code = compile(self.model.data, self.model.filename, 'exec')
        except:
            oldOut = sys.stdout
            sys.stdout = Utils.PseudoFileOutStore()
            try:
                print "''' Code does not compile\n\n    Disassembly of Traceback:\n'''"
                try:
                    dis.distb(sys.exc_info()[2])
                except:
                    print "''' Could not disassemble traceback '''\n"
                return sys.stdout.read()
            finally:
                sys.stdout = oldOut

        oldOut = sys.stdout
        sys.stdout = Utils.PseudoFileOutStore()
        try:
            try:
                dis.disco(code)
            except:
                raise
            return sys.stdout.read()
        finally:
            sys.stdout = oldOut

        return 'Invisible code'

    def setModelData(self, data):
        pass

class HTMLSourceView(EditorStyledTextCtrl, HTMLStyledTextCtrlMix):
    viewName = 'HTML'
    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_HTMLSOURCEVIEW,
          model, (('Refresh', self.OnRefresh, '-', keyDefs['Refresh']),), -1)
        HTMLStyledTextCtrlMix.__init__(self, wxID_HTMLSOURCEVIEW)
        self.active = true

    def OnUpdateUI(self, event):
        if hasattr(self, 'pageIdx'):
            self.updateViewState()

class XMLSourceView(EditorStyledTextCtrl, XMLStyledTextCtrlMix):
    viewName = 'XML'
    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_XMLSOURCEVIEW,
          model, (('Refresh', self.OnRefresh, '-', keyDefs['Refresh']),), -1)
        XMLStyledTextCtrlMix.__init__(self, wxID_XMLSOURCEVIEW)
        self.active = true

    def OnUpdateUI(self, event):
        if hasattr(self, 'pageIdx'):
            self.updateViewState()

class CPPSourceView(EditorStyledTextCtrl, CPPStyledTextCtrlMix):
    viewName = 'Source'
    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_CPPSOURCEVIEW,
          model, (('Refresh', self.OnRefresh, '-', keyDefs['Refresh']),), -1)
        CPPStyledTextCtrlMix.__init__(self, wxID_CPPSOURCEVIEW)
        self.active = true

    def OnUpdateUI(self, event):
        # don't update if not fully initialised
        if hasattr(self, 'pageIdx'):
            self.updateViewState()
##        CPPStyledTextCtrlMix.OnUpdateUI(self, event)

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
        self.ScrollBy(0, prevVsblLn - curVsblLn)

        self.nonUserModification = false
        self.updatePageName()


class TextView(EditorStyledTextCtrl):
    viewName = 'Text'
    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_TEXTVIEW,
          model, (), 0)
        self.active = true
        EVT_STC_UPDATEUI(self, wxID_TEXTVIEW, self.OnUpdateUI)

    def OnUpdateUI(self, event):
        if hasattr(self, 'pageIdx'):
            self.updateViewState()

class TstPythonSourceView(EditorStyledTextCtrl, PythonStyledTextCtrlMix, BrowseStyledTextCtrlMix):
    viewName = 'Source'
    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_PYTHONSOURCEVIEW,
          model, (), 0)
        PythonStyledTextCtrlMix.__init__(self)
        BrowseStyledTextCtrlMix.__init__(self)
        self.active = true
        EVT_STC_UPDATEUI(self, wxID_PYTHONSOURCEVIEW, self.OnUpdateUI)
        EVT_STC_CHARADDED(self, wxID_PYTHONSOURCEVIEW, self.OnAddChar)

    def OnUpdateUI(self, event):
        if hasattr(self, 'pageIdx'):
            self.updateViewState()

    def setStepPos(self, lineNo):
        pass

    def OnAddChar(self, event):
        char = event.GetKey()
        lineNo = self.GetCurrentLine()
        pos = self.GetCurrentPos()
        # On enter indent to same indentation as line above
        # If ends in : indent xtra block
        if char == 10:
            prevline = self.GetLine(lineNo -1)[:-1*len(self.eol)]
            i = 0
            if string.strip(prevline):
                while prevline[i] in (' ', '\t'): i = i + 1
                indent = prevline[:i]
            else:
                indent = prevline
            if string.rstrip(prevline)[-1:] == ':':
                indent = indent + (indentLevel*' ')
            self.BeginUndoAction()
            try:
                self.InsertText(pos, indent)
                self.GotoPos(pos + len(indent))
            finally:
                self.EndUndoAction()

    def OnKeyDown(self, event):
        key = event.KeyCode()
        if key == 32 and event.ControlDown():
            pos = self.GetCurrentPos()
            # Tips
            if event.ShiftDown():
                self.CallTipShow(pos, 'param1, param2')
            # Code completion
            else:
                module = self.model.getModule()
                self.AutoCompShow(string.join(module.classes.keys(),
                  ' '))
        elif key == 9:
            pos = self.GetCurrentPos()
            self.InsertText(pos, indentLevel*' ')
            self.SetCurrentPosition(pos + indentLevel)
            return
        elif key == 8:
            line = self.GetCurrentLineText()
            if len(line): line = line[0]
            else: line = ''
            pos = self.GetCurrentPos()
            #ignore indenting when at start of line
            if self.GetLineStartPos(self.GetLineFromPos(pos)) != pos:
                pos = pos -1
                ln = self.GetLineFromPos(pos)
                ls = self.GetLineStartPos(ln)
                st = pos - ls
                if not string.strip(line[:st]):
                    self.SetSelection(ls + st/4*4, pos+1)
                    self.ReplaceSelection('')
                    return
        event.Skip()
        BrowseStyledTextCtrlMix.OnKeyDown(self, event)
