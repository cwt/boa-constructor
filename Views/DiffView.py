#-----------------------------------------------------------------------------
# Name:        DiffView.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2000/17/07
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------

from ExternalLib import ndiff
from EditorViews import EditorView, ClosableViewMix
from wxPython.stc import *
from ShellEditor import PseudoFile
from StyledTextCtrls import PythonStyledTextCtrlMix
from PrefsKeys import keyDefs
from wxPython import wx
import Preferences, Utils
import sys, linecache, traceback, shutil

uniqueFile1Mrk = 1
uniqueFile2Mrk = 2
newToBothMrk = 3
maskMarkSet = 1 << uniqueFile1Mrk | 1 << uniqueFile2Mrk | 1 << newToBothMrk

class DiffPSOut(PseudoFile):
    def write(self, s):
##        cp = self.output.GetCurrentPos()
##        cl = self.output.GetLineFromPos(cp)
##        mrk = self.output.MarkerGet(cl)
        if s not in ('+', '-', ' ', '?'):
            self.output.AddText(s)
        elif s[0] == '+':
            self.output.MarkerAdd(self.output.GetLineCount()-1, uniqueFile2Mrk)
        elif s[0] == '-':
            self.output.MarkerAdd(self.output.GetLineCount()-1, uniqueFile1Mrk)
        elif s[0] == '?':
            self.output.MarkerAdd(self.output.GetLineCount()-1, newToBothMrk)

class DiffView(EditorView):
    def genCustomPage(self, page):
        return self.report

class PythonSourceDiffView(wxStyledTextCtrl, EditorView, PythonStyledTextCtrlMix, ClosableViewMix):
    viewName = 'Diff'
    refreshBmp = 'Images/Editor/Refresh.bmp'
    prevBmp = 'Images/Shared/Previous.bmp'
    nextBmp = 'Images/Shared/Next.bmp'
    def __init__(self, parent, model):
        wxID_PYTHONSOURCEDIFFVIEW = wxNewId()

        wxStyledTextCtrl.__init__(self, parent, wxID_PYTHONSOURCEDIFFVIEW,
          style = wx.wxCLIP_CHILDREN)
        PythonStyledTextCtrlMix.__init__(self, wxID_PYTHONSOURCEDIFFVIEW, 0)
        ClosableViewMix.__init__(self, 'diffs')
        EditorView.__init__(self, model,
          ( ('Refresh', self.OnRefresh, self.refreshBmp, keyDefs['Refresh']), ) +
            self.closingActionItems +
          ( ('-', None, '', ()),
            ('Previous difference', self.OnPrev, self.prevBmp, ()),
            ('Next difference', self.OnNext, self.nextBmp, ()),
            ('Apply all changes', self.OnApplyAllChanges, '-', ()) ), -1)

        self.SetMarginType(1, wxSTC_MARGIN_SYMBOL)
        self.SetMarginWidth(1, 16)
        self.MarkerDefine(uniqueFile1Mrk, wxSTC_MARK_MINUS, 'BLACK', 'WHITE')
        self.MarkerDefine(uniqueFile2Mrk, wxSTC_MARK_PLUS, 'BLACK', 'WHITE')
        self.MarkerDefine(newToBothMrk, wxSTC_MARK_SMALLRECT, 'BLACK', 'WHITE')

        self.SetMarginSensitive(1, wx.true)
        EVT_STC_MARGINCLICK(self, wxID_PYTHONSOURCEDIFFVIEW, self.OnMarginClick)

        self.tabName = 'Diff'
        self.diffWith = ''
        self.currSearchLine = 1

        ## Install the handler for refreshs.
        if wx.wxPlatform == '__WXGTK__':
            self.paint_handler = Utils.PaintEventHandler(self)

        self.active = wx.true

        self.lineIndex = []

    def refreshCtrl(self):
        self.SetReadOnly(wx.false)
        self.ClearAll()
        if self.diffWith:
            saveout = sys.stdout
            try:
                sys.stdout = DiffPSOut(self)
                try:
#                    self.model.editor.app.saveStdio = sys.stdout, sys.stderr
                    ndiff.fcompare(self.model.filename, self.diffWith)
                except:
                    (sys.last_type, sys.last_value,
                     sys.last_traceback) = sys.exc_info()
                    linecache.checkcache()
                    traceback.print_exc()
            finally:
                sys.stdout = saveout
        self.SetReadOnly(wx.true)

    def gotoLine(self, lineno, offset = -1):
        self.GotoLine(lineno)
        vl = self.GetFirstVisibleLine()
        self.ScrollBy(0, lineno -  vl)
        if offset != -1: self.SetCurrentPosition(self.GetCurrentPos()+offset+1)

    def OnUpdateUI(self, event):
        if Preferences.braceHighLight:
            PythonStyledTextCtrlMix.OnUpdateUI(self, event)

    def OnRefresh(self, event):
        self.refreshModel()

    def OnMarginClick(self, event):
        if event.GetMargin() == 1:
            ln = self.GetLineFromPos(event.GetPosition())
#            ln = event.GetLine()
            print ln, self.MarkerGet(ln)

    def OnPrev(self, event):
        self.currSearchLine = self.MarkerGetPrevLine(self.currSearchLine,
          maskMarkSet) - 1
#        self.SetFocus()
#        self.EnsureVisible(self.currSearchLine)
        self.gotoLine(self.currSearchLine + 1)

    def OnNext(self, event):
        self.currSearchLine = self.MarkerGetNextLine(self.currSearchLine,
          maskMarkSet) + 1
#        self.SetFocus()
        self.gotoLine(self.currSearchLine - 1)
#        self.EnsureVisible(self.currSearchLine)

    def OnApplyAllChanges(self, event):
        if self.diffWith and Utils.yesNoDialog(self, 'Are you sure?',
          'Replace %s with %s?'% (self.model.filename, self.diffWith)):
            shutil.copyfile(self.diffWith, self.model.filename)
            self.model.load()
            self.deleteFromNotebook('Source', self.tabName)
