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

import string, os, sys
import keyword, types

from wxPython.wx import *
from wxPython.stc import *

from Views import StyledTextCtrls
from ExternalLib.PythonInterpreter import PythonInterpreter
import Preferences
from PrefsKeys import keyDefs
from Utils import PseudoFile
from methodparse import safesplitfields, matchbracket
echo = true

p2c = 'Type "copyright", "credits" or "license" for more information.'

[wxID_SHELL_HISTORYUP, wxID_SHELL_HISTORYDOWN, wxID_SHELL_ENTER, wxID_SHELL_HOME,
 wxID_SHELL_CODECOMP, wxID_SHELL_CALLTIPS,
] = map(lambda _init_ctrls: wxNewId(), range(6))

only_first_block = 1

class ShellEditor(StyledTextCtrls.wxStyledTextCtrl, 
                  StyledTextCtrls.PythonStyledTextCtrlMix, 
                  StyledTextCtrls.AutoCompleteCodeHelpSTCMix,
                  StyledTextCtrls.CallTipCodeHelpSTCMix):
    def __init__(self, parent, wId):
        StyledTextCtrls.wxStyledTextCtrl.__init__(self, parent, wId, 
              style = wxCLIP_CHILDREN)
        StyledTextCtrls.CallTipCodeHelpSTCMix.__init__(self)
        StyledTextCtrls.PythonStyledTextCtrlMix.__init__(self, wId, -1)
        #self.SetCaretPeriod(0)
        self.lines = StyledTextCtrls.STCLinesList(self)
        self.interp = PythonInterpreter()
        self.lastResult = ''

        try:
            license
            #_license = license
        except NameError:
            pass
        else:
            def my_raw_input(prompt = ''):
                """ This function replaces the builtin raw_input which reads
                from the console """
                dlg = wxTextEntryDialog(None, prompt, 'raw_input', '')
                try:
                    if dlg.ShowModal() == wxID_OK:
                        return dlg.GetValue()
                finally:
                    dlg.Destroy()

                return ''

            class MyLicensePrinter:
                """ This class replaces the standard license printer obj
                that causes a freeze because it blocks reading from
                the keyboard """
                def __init__(self, _license):
                    self._license = _license

                def __call__(self):
                    self._license._Printer__setup()
                    print "'''\n%s\n'''"%string.join(self._license._Printer__lines, '\n')
                
                def __repr__(self):
                    return repr(self._license)

            self.interp.locals['license'] = MyLicensePrinter(license)
        self.interp.locals['raw_input'] = my_raw_input
    
        if sys.hexversion < 0x01060000:
            copyright = sys.copyright
        else:
            copyright = p2c
        self.CallTipSetBackground(wxColour(255, 255, 232))
        self.SetText('# Python %s (Boa)\n# %s\n%s'%(sys.version, copyright, 
              Preferences.ps1))
        self.SetCurrentPosition(self.GetTextLength())
        self.SetSelectionStart(self.GetCurrentPosition())
        self.SetSavePoint()

        EVT_KEY_UP(self, self.OnKeyUp)

        EVT_MENU(self, wxID_SHELL_HISTORYUP, self.OnHistoryUp)
        EVT_MENU(self, wxID_SHELL_HISTORYDOWN, self.OnHistoryDown)
        EVT_MENU(self, wxID_SHELL_ENTER, self.OnShellEnter)
        EVT_MENU(self, wxID_SHELL_HOME, self.OnShellHome)
        EVT_MENU(self, wxID_SHELL_CODECOMP, self.OnShellCodeComplete)
        EVT_MENU(self, wxID_SHELL_CALLTIPS, self.OnShellCallTips)

        self.SetAcceleratorTable(wxAcceleratorTable( [
         (keyDefs['HistoryUp'][0], keyDefs['HistoryUp'][1], wxID_SHELL_HISTORYUP),
         (keyDefs['HistoryDown'][0], keyDefs['HistoryDown'][1], wxID_SHELL_HISTORYDOWN),
         (keyDefs['CodeComplete'][0], keyDefs['CodeComplete'][1], wxID_SHELL_CODECOMP),
         (keyDefs['CallTips'][0], keyDefs['CallTips'][1], wxID_SHELL_CALLTIPS),
         (0, WXK_RETURN, wxID_SHELL_ENTER),
         (0, WXK_HOME, wxID_SHELL_HOME),
        ] ))

        self.history = []
        self.historyIndex = 1

        self.stdout = PseudoFileOut(self)
        self.stderr = PseudoFileErr(self)
        
    def setDebugNamespace(self, ns):
        pass

    def destroy(self):
        del self.lines
        del self.stdout
        del self.stderr

    def OnUpdateUI(self, event):
        if Preferences.braceHighLight:
            StyledTextCtrls.PythonStyledTextCtrlMix.OnUpdateUI(self, event)

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

    def pushLine(self, line):
        self.AddText('\n')
        try:
            tmpstdout = sys.stdout
            tmpstderr = sys.stderr
            sys.stdout = self.stdout
            sys.stderr = self.stderr

            self.lastResult = ''
            if self.interp.push(line):
                self.AddText(Preferences.ps2)
                return true
            else:
                self.AddText(Preferences.ps1)
                return false
        finally:
            sys.stdout = tmpstdout
            sys.stderr = tmpstderr
            self.EnsureCaretVisible()

    def OnShellEnter(self, event):
        self.BeginUndoAction()
        try:
            if self.AutoCompActive():
                self.AutoCompComplete()
                return
            if self.CallTipActive():
                self.CallTipCancel()
                
            lc = self.GetLineCount()
            cl = self.GetCurrentLine()
            ct = self.GetCurrentLineText()[0]
            line = string.rstrip(ct[4:])
            self.SetCurrentPosition(self.GetTextLength())
            ll = self.GetCurrentLine()

            # bottom line, process the line
            if cl == lc -1:
                # Auto indent
                if self.pushLine(line):
                    self.doAutoIndent(line, self.GetCurrentPos())

                # Manage history
                if string.strip(line) and (self.history and self.history[-1] != line or not self.history):
                    self.history.append(line)
                    self.historyIndex = len(self.history)
            # Other lines, copy the line to the bottom line
            else:
                self.SetSelection(self.GetLineStartPos(self.GetCurrentLine()), self.GetTextLength())
                self.ReplaceSelection(string.rstrip(ct))
        finally:
            self.EndUndoAction()

    def getCodeCompOptions(self, word, rootWord, matchWord, lnNo):
        if not rootWord:
            return eval('dir()+__builtins__.keys()', self.interp.locals) +\
                  keyword.kwlist
        else:
            try:
                obj = eval(rootWord, self.interp.locals)
            except Exception, error:
                return []
            else:
                try:
                    return recdir(obj)
                except Exception, err:
                    return [] 
        
    def OnShellCodeComplete(self, event):
        self.codeCompCheck()

    def getTipValue(self, word, lnNo):
        try:
            obj = eval(word, self.interp.locals)
        except:
            docs = ''
        else:
            # we want to reroute wxPython objects to their doc strings
            # if they are defined
            docs = ''
            if hasattr(obj, '__doc__') and obj.__doc__:
                if type(obj) is types.ClassType:
                    if wx.__dict__.has_key(obj.__name__):
                        docs = obj.__init__.__doc__
                elif type(obj) is types.InstanceType:
                    if wx.__dict__.has_key(obj.__class__.__name__):
                        docs = obj.__doc__
                elif type(obj) is types.MethodType:
                    if wx.__dict__.has_key(obj.im_class.__name__):
                        docs = obj.__doc__
            # Get docs from builtin's docstrings or from Signature module
            if not docs:
                if type(obj) is types.BuiltinFunctionType:
                    try: docs = obj.__doc__
                    except AttributeError: docs = ''
                else:
                    from ExternalLib import Signature
                    try:
                        sig = str(Signature.Signature(obj))
                        docs = string.replace(sig, '(self, ', '(')
                        docs = string.replace(docs, '(self)', '()')
                    except ValueError:
                        try: docs = obj.__doc__
                        except AttributeError: docs = ''

            if docs:
                # Take only the first continuous block from big docstrings
                if only_first_block:
                    tip = self.getFirstContinousBlock(docs)
                else:
                    tip = docs
                
                return tip
        return ''

    def OnShellCallTips(self, event):
        self.callTipCheck()

    def OnShellHome(self, event):
        pos = self.GetCurrentPos()
        lnNo = self.GetCurrentLine()
        lnStPs = self.GetLineStartPos(lnNo)
        line = self.GetCurrentLineText()[0]
        
        if len(line) >=4 and line[:4] in (Preferences.ps1, Preferences.ps2):
            self.SetCurrentPos(lnStPs+4)
            self.SetAnchor(lnStPs+4)
        else:
            self.SetCurrentPos(lnStPs)
            self.SetAnchor(lnStPs)

    def OnKeyUp(self, event):
        if self.CallTipActive():
            self.callTipCheck()
        event.Skip()

def recdir(obj):
    res = dir(obj)
    if hasattr(obj, '__class__'):
        res.extend(recdir(obj.__class__))
    if hasattr(obj, '__bases__'):
        for base in obj.__bases__:
            res.extend(recdir(base))
    
    unq = {}
    for name in res: unq[name] = None
    return unq.keys()

#-----Output redirectors--------------------------------------------------------

class PseudoFileOut(PseudoFile):
    tags = 'stdout'
    def write(self, s):
        #self.output.SetLexer(wxSTC_LEX_NULL)
        self.output.AddText(s)
        self.output.EnsureCaretVisible()
        self.output.lastResult = self.tags
        #self.output.SetLexer(wxSTC_LEX_PYTHON)
        #self.output.Refresh(false)

class PseudoFileErr(PseudoFile):
    tags = 'stderr'
    def write(self, s):
        #self.output.SetLexer(wxSTC_LEX_NULL)
        self.output.AddText(s)
        self.output.EnsureCaretVisible()
        self.output.lastResult = self.tags
        #self.output.SetLexer(wxSTC_LEX_PYTHON)
        #self.output.Refresh(false)

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
