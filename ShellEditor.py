#-----------------------------------------------------------------------------
# Name:        ShellEditor.py
# Purpose:     Interactive interpreter
#
# Author:      Riaan Booysen
#
# Created:     2000/06/19
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------

from wxPython.wx import *
from Views.StyledTextCtrls import PythonStyledTextCtrlMix, STCLinesList
from wxPython.stc import *
from ExternalLib.PythonInterpreter import PythonInterpreter
import string, os
import Preferences
from PrefsKeys import keyDefs
from Utils import PseudoFile
echo = true

ps1 = '>>> '
ps2 = '... '
ps3 = '>-> '
p2c = 'Type "copyright", "credits" or "license" for more information.'

wxID_SHELL_HISTORYUP, wxID_SHELL_HISTORYDOWN = wxNewId(), wxNewId()

class ShellEditor(wxStyledTextCtrl, PythonStyledTextCtrlMix):
    def __init__(self, parent, wId):
        wxStyledTextCtrl.__init__(self, parent, wId, style = wxCLIP_CHILDREN)
        PythonStyledTextCtrlMix.__init__(self, wId, -1)
        #self.SetCaretPeriod(0)
        self.lines = STCLinesList(self)
        self.interp = PythonInterpreter()

        try:
            license
        except NameError:
            pass
        else:
            # XXX This causes problems with globals(), locals() !!
            class MyLicensePrinter(license.__class__):
                def __init__(self):
                    self.__lines = []
                def __call__(self):
                    license.__setup()
#                    print "'''\n%s\n'''"%string.join(license._Printer__lines, '\n')

            self.interp.locals['license'] = MyLicensePrinter()

        self.SetLexer(wxSTC_LEX_NULL)
        if sys.hexversion < 0x01060000:
            copyright = sys.copyright
        else:
            copyright = p2c
        self.SetText('# Python %s (Boa)\n# %s\n%s'%(sys.version, copyright, ps1))
        self.SetLexer(wxSTC_LEX_PYTHON)
        self.SetCurrentPosition(self.GetTextLength())
        self.SetSelectionStart(self.GetCurrentPosition())
##        self.EnsureCaretVisible()
##        self.ScrollToColumn(0)
        EVT_CHAR(self, self.OnShellKey)
        EVT_MENU(self, wxID_SHELL_HISTORYUP, self.OnHistoryUp)
        EVT_MENU(self, wxID_SHELL_HISTORYDOWN, self.OnHistoryDown)

        self.history = []
        self.historyIndex = 1

        self.SetAcceleratorTable(wxAcceleratorTable( [
         (keyDefs['HistoryUp'][0], keyDefs['HistoryUp'][1], wxID_SHELL_HISTORYUP),
         (keyDefs['HistoryDown'][0], keyDefs['HistoryDown'][1], wxID_SHELL_HISTORYDOWN)
        ] ))

        self.stdout = PseudoFileOut(self)
        self.stderr = PseudoFileErr(self)

    def setDebugNamespace(self, ns):
        pass

    def destroy(self):
        del self.lines
        del self.stdout
        del self.stderr

    def OnShellKey(self, event):
        keyCode = event.KeyCode()
        if keyCode == 13:
            try:
                tmpstdout = sys.stdout
                tmpstderr = sys.stderr
                line = string.rstrip(self.GetLine(self.GetLineCount() -2)[4:-1])
                sys.stdout = self.stdout
                sys.stderr = self.stderr

                if self.interp.push(line):
                    self.AddText(ps2)
                else:
                    self.AddText(ps1)

                if string.strip(line):
                    self.history.append(line)
                    self.historyIndex = len(self.history)
            finally:
                sys.stdout = tmpstdout
                sys.stderr = tmpstderr
                self.EnsureCaretVisible()
        else:
            event.Skip()

    def OnUpdateUI(self, event):
        if Preferences.braceHighLight:
            PythonStyledTextCtrlMix.OnUpdateUI(self, event)

    def getHistoryInfo(self):
        lineNo = self.GetCurrentLine()
        if self.history and self.GetLineCount()-1 == lineNo:
            pos = self.PositionFromLine(lineNo) + 4
            endpos = self.GetLineEndPosition(lineNo)
            return lineNo, pos, endpos
        else:
            return None, None, None

    def OnHistoryUp(self, event):
        lineNo, pos, endpos = self.getHistoryInfo()
        if lineNo is not None:
            if self.historyIndex > 0:
                self.historyIndex = self.historyIndex -1

            self.SetSelection(pos, endpos)
            self.ReplaceSelection((self.history+[''])[self.historyIndex])

    def OnHistoryDown(self, event):
        lineNo, pos, endpos = self.getHistoryInfo()
        if lineNo is not None:
            if self.historyIndex < len(self.history):
                self.historyIndex = self.historyIndex +1

            self.SetSelection(pos, endpos)
            self.ReplaceSelection((self.history+[''])[self.historyIndex])

#-----Output redirectors--------------------------------------------------------

class PseudoFileOut(PseudoFile):
    tags = 'stdout'
    def write(self, s):
        self.output.SetLexer(wxSTC_LEX_NULL)
        self.output.AddText(s)
        self.output.SetLexer(wxSTC_LEX_PYTHON)
        self.output.Refresh(false)

class PseudoFileErr(PseudoFile):
    tags = 'stderr'
    def write(self, s):
        self.output.SetLexer(wxSTC_LEX_NULL)
        self.output.AddText(s)
        self.output.SetLexer(wxSTC_LEX_PYTHON)
        self.output.Refresh(false)

class PseudoFileOutStore(PseudoFile):
    tags = 'stdout'
    def write(self, s):
        self.output.append(s)

    def read(self):
        return string.join(self.output, '')

class PseudoFileOutTC(PseudoFile):
    tags = 'stderr'
    def write(self, s):
        self.output.AppendText(s)
        if echo: sys.__stdout__.write(s)

class PseudoFileErrTC(PseudoFile):
    tags = 'stdout'
    def write(self, s):
        self.output.AppendText(s)
        if echo: sys.__stderr__.write(s)
