#-----------------------------------------------------------------------------
# Name:        DiffView.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2000/17/07
# RCS-ID:      $Id$
# Copyright:   (c) 2000 - 2004 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------

import sys, linecache, traceback, shutil
from cStringIO import StringIO

from wxPython import wx
from wxPython.stc import *

from ExternalLib import ndiff
from EditorViews import EditorView, CloseableViewMix
from StyledTextCtrls import PythonStyledTextCtrlMix
import Preferences, Utils

uniqueFile1Mrk = 1
uniqueFile2Mrk = 2
newToBothMrk = 3
maskMarkSet = 1 << uniqueFile1Mrk | 1 << uniqueFile2Mrk | 1 << newToBothMrk

def ndiff_lcompare(a, b):
    """ Copy of ndiff.fcompare, works on lines instread of files """

    cruncher = ndiff.SequenceMatcher(ndiff.IS_LINE_JUNK, a, b)
    for tag, alo, ahi, blo, bhi in cruncher.get_opcodes():
        if tag == 'replace':
            ndiff.fancy_replace(a, alo, ahi, b, blo, bhi)
        elif tag == 'delete':
            ndiff.dump('-', a, alo, ahi)
        elif tag == 'insert':
            ndiff.dump('+', b, blo, bhi)
        elif tag == 'equal':
            ndiff.dump(' ', a, alo, ahi)
        else:
            raise ValueError, 'unknown tag ' + `tag`

    return 1


class DiffPSOut(Utils.PseudoFile):
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

class PythonSourceDiffView(wxStyledTextCtrl, EditorView, PythonStyledTextCtrlMix, CloseableViewMix):
    viewName = 'Diff'
    refreshBmp = 'Images/Editor/Refresh.png'
    prevBmp = 'Images/Shared/Previous.png'
    nextBmp = 'Images/Shared/Next.png'
    def __init__(self, parent, model):
        wxID_PYTHONSOURCEDIFFVIEW = wxNewId()

        wxStyledTextCtrl.__init__(self, parent, wxID_PYTHONSOURCEDIFFVIEW,
          style = wx.wxCLIP_CHILDREN | wx.wxSUNKEN_BORDER)
        PythonStyledTextCtrlMix.__init__(self, wxID_PYTHONSOURCEDIFFVIEW, 0)
        CloseableViewMix.__init__(self, 'diffs')
        EditorView.__init__(self, model,
          ( ('Refresh', self.OnRefresh, self.refreshBmp, 'Refresh'), ) +
            self.closingActionItems +
          ( ('-', None, '', ''),
            ('Previous difference', self.OnPrev, self.prevBmp, ''),
            ('Next difference', self.OnNext, self.nextBmp, ''),
            ('Apply all changes', self.OnApplyAllChanges, '-', '') ), -1)

        self.SetMarginType(1, wxSTC_MARGIN_SYMBOL)
        self.SetMarginWidth(1, 16)
        markIdnt, markBorder, markCenter = Preferences.STCDiffRemovedMarker
        self.MarkerDefine(uniqueFile1Mrk, markIdnt, markBorder, markCenter)
        markIdnt, markBorder, markCenter = Preferences.STCDiffAddedMarker
        self.MarkerDefine(uniqueFile2Mrk, markIdnt, markBorder, markCenter)
        markIdnt, markBorder, markCenter = Preferences.STCDiffChangesMarker
        self.MarkerDefine(newToBothMrk, markIdnt, markBorder, markCenter)

        self.SetMarginSensitive(1, wx.true)
        EVT_STC_MARGINCLICK(self, wxID_PYTHONSOURCEDIFFVIEW, self.OnMarginClick)

        self.tabName = 'Diff'
        self.diffWith = ''
        self.currSearchLine = 1

        ## Install the handler for refreshs.
        if wx.wxPlatform == '__WXGTK__' and Preferences.edUseCustomSTCPaintEvtHandler:
            self.paint_handler = Utils.PaintEventHandler(self)

        self.active = wx.true

        self.lineIndex = []

    def refreshCtrl(self):
        from Explorers.Explorer import openEx
        self.SetReadOnly(wx.false)
        self.ClearAll()
        if self.diffWith:
            saveout = sys.stdout
            try:
                sys.stdout = DiffPSOut(self)
                try:
                    src = StringIO(self.model.data).readlines()
                    # XXX could sometimes use data from file open in IDE ???
                    dst = StringIO(openEx(self.diffWith).load('rb')).readlines()
#                    self.model.editor.app.saveStdio = sys.stdout, sys.stderr
                    ndiff_lcompare(src, dst)
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
        self.LineScroll(0, lineno -  vl)
        if offset != -1: self.SetCurrentPos(self.GetCurrentPos()+offset+1)

    def OnUpdateUI(self, event):
        if Preferences.braceHighLight:
            PythonStyledTextCtrlMix.OnUpdateUI(self, event)

    def OnRefresh(self, event):
        self.refreshModel()

    def OnMarginClick(self, event):
        if event.GetMargin() == 1:
            ln = self.LineFromPosition(event.GetPosition())

    def OnPrev(self, event):
        self.currSearchLine = self.MarkerPrevious(self.currSearchLine,
          maskMarkSet) - 1
        self.gotoLine(self.currSearchLine + 1)

    def OnNext(self, event):
        self.currSearchLine = self.MarkerNext(self.currSearchLine,
          maskMarkSet) + 1
        self.gotoLine(self.currSearchLine - 1)

    def OnApplyAllChanges(self, event):
        filename = self.model.assertLocalFile()
        if self.diffWith and Utils.yesNoDialog(self, 'Are you sure?',
              'Replace %s with %s?'% (filename, self.diffWith)):
            shutil.copyfile(self.diffWith, filename)
            # reload
            self.model.load()
            self.deleteFromNotebook('Source', self.tabName)
