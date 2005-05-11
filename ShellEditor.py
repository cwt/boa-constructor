#-----------------------------------------------------------------------------
# Name:        ShellEditor.py
# Purpose:     Interactive interpreter
#
# Author:      Riaan Booysen
#
# Created:     2000/06/19
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2005 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------

# XXX Try to handle multi line paste

import sys, keyword, types, time

from wxPython.wx import *
from wxPython.stc import *

import Preferences, Utils
from Preferences import keyDefs
from Views import StyledTextCtrls
from ExternalLib.PythonInterpreter import PythonInterpreter
from ExternalLib import Signature
from Models import EditorHelper

import wxNamespace

echo = true

p2c = 'Type "copyright", "credits" or "license" for more information.'

[wxID_SHELL_HISTORYUP, wxID_SHELL_HISTORYDOWN, wxID_SHELL_ENTER, wxID_SHELL_HOME,
 wxID_SHELL_CODECOMP, wxID_SHELL_CALLTIPS,
] = map(lambda _init_ctrls: wxNewId(), range(6))

only_first_block = 1


class IShellEditor:
    def destroy(self):
        pass
    
    def execStartupScript(self, startupfile):
        pass
    
    def debugShell(self, doDebug, debugger):
        pass
    
    def pushLine(self, line, addText=''):
        pass

    def getShellLocals(self):
        return {}


class ShellEditor(StyledTextCtrls.wxStyledTextCtrl,
                  StyledTextCtrls.PythonStyledTextCtrlMix,
                  StyledTextCtrls.AutoCompleteCodeHelpSTCMix,
                  StyledTextCtrls.CallTipCodeHelpSTCMix):
    def __init__(self, parent, wId):
        StyledTextCtrls.wxStyledTextCtrl.__init__(self, parent, wId,
              style = wxCLIP_CHILDREN | wxSUNKEN_BORDER)
        StyledTextCtrls.CallTipCodeHelpSTCMix.__init__(self)
        StyledTextCtrls.AutoCompleteCodeHelpSTCMix.__init__(self)
        StyledTextCtrls.PythonStyledTextCtrlMix.__init__(self, wId, ())

        self.lines = StyledTextCtrls.STCLinesList(self)
        self.interp = PythonInterpreter()
        self.lastResult = ''

        self.CallTipSetBackground(wxColour(255, 255, 232))
        # 2, 4, 1, 2 crashes in wrap mode.
        # XXX remove when min version > 2.4.1.2
        if wxVERSION[:4] != (2, 4, 1, 2):
            try: self.SetWrapMode(1)
            except AttributeError: pass

        self.bindShortcuts()

        EVT_KEY_DOWN(self, self.OnKeyDown)
        EVT_STC_CHARADDED(self, wId, self.OnAddChar)

        EVT_MENU(self, wxID_SHELL_HISTORYUP, self.OnHistoryUp)
        EVT_MENU(self, wxID_SHELL_HISTORYDOWN, self.OnHistoryDown)
        #EVT_MENU(self, wxID_SHELL_ENTER, self.OnShellEnter)
        EVT_MENU(self, wxID_SHELL_HOME, self.OnShellHome)
        EVT_MENU(self, wxID_SHELL_CODECOMP, self.OnShellCodeComplete)
        EVT_MENU(self, wxID_SHELL_CALLTIPS, self.OnShellCallTips)


        self.history = []
        self.historyIndex = 1

        self.buffer = []

        self.stdout = PseudoFileOut(self)
        self.stderr = PseudoFileErr(self)
        self.stdin = PseudoFileIn(self, self.buffer)

        self._debugger = None

        if sys.hexversion < 0x01060000:
            copyright = sys.copyright
        else:
            copyright = p2c
        import wxPython
        import __version__
        self.AddText('# Python %s\n# wxPython %s, Boa Constructor %s\n# %s'%(
              sys.version, wxPython.__version__, __version__.version, copyright))
        self.LineScroll(-10, 0)
        self.SetSavePoint()


    def destroy(self):
        if self.stdin.isreading():
            self.stdin.kill()

        del self.lines
        del self.stdout
        del self.stderr
        del self.stdin
        del self.interp

    def bindShortcuts(self):
        # dictionnary of shortcuts: (MOD, KEY) -> function
        self.sc = {}
        self.sc[(keyDefs['HistoryUp'][0], keyDefs['HistoryUp'][1])] = self.OnHistoryUp
        self.sc[(keyDefs['HistoryDown'][0], keyDefs['HistoryDown'][1])] = self.OnHistoryDown
        self.sc[(keyDefs['CodeComplete'][0], keyDefs['CodeComplete'][1])] = self.OnShellCodeComplete
        self.sc[(keyDefs['CallTips'][0], keyDefs['CallTips'][1])] = self.OnShellCallTips

    def execStartupScript(self, startupfile):
        if startupfile:
            startuptext = '## Startup script: ' + startupfile
            self.pushLine('print %s;execfile(%s)'%(`startuptext`, `startupfile`))
        else:
            self.pushLine('')

    def debugShell(self, doDebug, debugger):
        if doDebug:
            self._debugger = debugger
            self.stdout.write('\n## Debug mode turned on.')
            self.pushLine('print "?"')
        else:
            self._debugger = None
            self.pushLine('print "## Debug mode turned %s."'% (doDebug and 'on' or 'off'))

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

    def pushLine(self, line, addText=''):
        """ Interprets a line """
        self.AddText(addText+'\n')
        prompt = ''
        try:
            self.stdin.clear()
            tmpstdout,tmpstderr,tmpstdin = sys.stdout,sys.stderr,sys.stdin
            sys.stdout,sys.stderr,sys.stdin = self.stdout,self.stderr,self.stdin
            self.lastResult = ''
            if self._debugger:
                prompt = Preferences.ps3
                val = self._debugger.getVarValue(line)
                if val is not None:
                    print val
                return false
            elif self.interp.push(line):
                prompt = Preferences.ps2
                self.stdout.fin(); self.stderr.fin()
                return true
            else:
                # check if already destroyed
                if not hasattr(self, 'stdin'):
                    return false

                prompt = Preferences.ps1
                self.stdout.fin(); self.stderr.fin()
                return false
        finally:
            sys.stdout,sys.stderr,sys.stdin = tmpstdout,tmpstderr,tmpstdin
            if prompt:
                self.AddText(prompt)
            self.EnsureCaretVisible()
    
    def getShellLocals(self):
        return self.interp.locals

    def OnShellEnter(self, event):
        self.BeginUndoAction()
        try:
            if self.CallTipActive():
                self.CallTipCancel()

            lc = self.GetLineCount()
            cl = self.GetCurrentLine()
            ct = self.GetCurLine()[0]
            line = ct[4:].rstrip()
            self.SetCurrentPos(self.GetTextLength())
            #ll = self.GetCurrentLine()

            # bottom line, process the line
            if cl == lc -1:
                if self.stdin.isreading():
                    self.AddText('\n')
                    self.buffer.append(line)
                    return
                # Auto indent
                if self.pushLine(line):
                    self.doAutoIndent(line, self.GetCurrentPos())

                # Manage history
                if line.strip() and (self.history and self.history[-1] != line or not self.history):
                    self.history.append(line)
                    self.historyIndex = len(self.history)
            # Other lines, copy the line to the bottom line
            else:
                self.SetSelection(self.PositionFromLine(self.GetCurrentLine()), self.GetTextLength())
                #self.lines.select(self.lines.current)
                self.ReplaceSelection(ct.rstrip())
        finally:
            self.EndUndoAction()
            #event.Skip()

    def getCodeCompOptions(self, word, rootWord, matchWord, lnNo):
        if not rootWord:
            return wxNamespace.filterOnPrefs(self.interp.locals,
                   wxNamespace.__dict__) + __builtins__.keys() + keyword.kwlist
        else:
            try: obj = eval(rootWord, self.interp.locals)
            except Exception, error: return []
            else:
                try: return recdir(obj)
                except Exception, err: return []

    def OnShellCodeComplete(self, event):
        self.codeCompCheck()

    def getTipValue(self, word, lnNo):
        try:
            obj = eval(word, self.interp.locals)
        except:
            return ''
        else:
            return tipforobj(obj, self)

    def OnShellCallTips(self, event):
        self.callTipCheck()

    def OnShellHome(self, event):
        lnNo = self.GetCurrentLine()
        lnStPs = self.PositionFromLine(lnNo)
        line = self.GetCurLine()[0]

        if len(line) >=4 and line[:4] in (Preferences.ps1, Preferences.ps2):
            self.SetCurrentPos(lnStPs+4)
            self.SetAnchor(lnStPs+4)
        else:
            self.SetCurrentPos(lnStPs)
            self.SetAnchor(lnStPs)

    def OnKeyDown(self, event):
        if Preferences.handleSpecialEuropeanKeys:
            self.handleSpecialEuropeanKeys(event, Preferences.euroKeysCountry)

        kk = event.KeyCode()
        controlDown = event.ControlDown()
        shiftDown = event.ShiftDown()
        if kk == WXK_RETURN and not (shiftDown or event.HasModifiers()):
            if self.AutoCompActive():
                self.AutoCompComplete()
                return
            self.OnShellEnter(event)
            return
        elif kk == WXK_BACK:
                # don't delete the prompt
            if self.lines.current == self.lines.count -1 and \
              self.lines.pos - self.PositionFromLine(self.lines.current) < 5:
                return
        elif kk == WXK_HOME and not (controlDown or shiftDown):
            self.OnShellHome(event)
            return
        elif controlDown:
            if shiftDown and self.sc.has_key((wxACCEL_CTRL|wxACCEL_SHIFT, kk)):
                self.sc[(wxACCEL_CTRL|wxACCEL_SHIFT, kk)](self)
                return
            elif self.sc.has_key((wxACCEL_CTRL, kk)):
                self.sc[(wxACCEL_CTRL, kk)](self)
                return
        
        if self.CallTipActive():
            self.callTipCheck()
        event.Skip()

    def OnAddChar(self, event):
        if event.GetKey() == 40 and Preferences.callTipsOnOpenParen:
            self.callTipCheck()
        

def recdir(obj):
    res = dir(obj)
    if hasattr(obj, '__class__') and obj != obj.__class__:
        if hasattr(obj, '__class__') and type(obj) != types.ModuleType:
            res.extend(recdir(obj.__class__))
        if hasattr(obj, '__bases__'):
            for base in obj.__bases__:
                res.extend(recdir(base))

    unq = {}
    for name in res: unq[name] = None
    return unq.keys()

def tipforobj(obj, ccstc):
    # we want to reroute wxPython objects to their doc strings
    # if they are defined
    docs = ''
    if hasattr(obj, '__doc__') and obj.__doc__:
        wxNS = Utils.getEntireWxNamespace()
        if type(obj) is types.ClassType:
            if wxNS.has_key(obj.__name__):
                docs = obj.__init__.__doc__
        elif type(obj) is types.InstanceType:
            if wxNS.has_key(obj.__class__.__name__):
                docs = obj.__doc__
        elif type(obj) is types.MethodType:
            if wxNS.has_key(obj.im_class.__name__):
                docs = obj.__doc__
    # Get docs from builtin's docstrings or from Signature module
    if not docs:
        if type(obj) is types.BuiltinFunctionType:
            try: docs = obj.__doc__
            except AttributeError: docs = ''
        else:
            try:
                sig = str(Signature.Signature(obj))
                docs = sig.replace('(self, ', '(')
                docs = docs.replace('(self)', '()')
            except (ValueError, TypeError):
                try: docs = obj.__doc__
                except AttributeError: docs = ''

    if docs:
        # Take only the first continuous block from big docstrings
        if only_first_block:
            tip = ccstc.getFirstContinousBlock(docs)
        else:
            tip = docs

        return tip
    return ''


#-----Pipe redirectors--------------------------------------------------------

class PseudoFileIn:
    def __init__(self, output, buffer):
        self._buffer = buffer
        self._output = output
        self._reading = false

    def clear(self):
        self._buffer[:] = []
        self._reading = false

    def isreading(self):
        return self._reading

    def kill(self):
        self._buffer.append(None)

    def readline(self):
        self._reading = true
        self._output.AddText('\n'+Preferences.ps4)
        self._output.EnsureCaretVisible()
        try:
            while not self._buffer:
                # XXX with safe yield once the STC loses focus there is no way
                # XXX to give it back the focus
                # wxSafeYield()
                time.sleep(0.001)
                wxYield()
            line = self._buffer.pop()
            if line is None: raise 'Terminate'
            if not(line.strip()): return '\n'
            else: return line
        finally:
            self._reading = false

class QuoterPseudoFile(Utils.PseudoFile):
    quotes = '```'
    def __init__(self, output = None, quote=false):
        Utils.PseudoFile.__init__(self, output)
        self._dirty = false
        self._quote = quote

    def _addquotes(self):
        if self._quote:
            self.output.AddText(self.quotes+'\n')

    def write(self, s):
        if not self._dirty:
            self._addquotes()
            self._dirty = true

    def fin(self):
        if self._dirty:
            self._addquotes()
            self._dirty = false

class PseudoFileOut(QuoterPseudoFile):
    tags = 'stdout'
    quotes = '"""'
    def write(self, s):
        QuoterPseudoFile.write(self, s)
        self.output.AddText(s)
        self.output.lastResult = self.tags

class PseudoFileErr(QuoterPseudoFile):
    tags = 'stderr'
    quotes = "'''"
    def write(self, s):
        QuoterPseudoFile.write(self, s)
        self.output.AddText(s)
        self.output.EnsureCaretVisible()
        self.output.lastResult = self.tags

class PseudoFileOutTC(Utils.PseudoFile):
    tags = 'stderr'
    def write(self, s):
        self.output.AppendText(s)
        if echo: sys.__stdout__.write(s)

class PseudoFileErrTC(Utils.PseudoFile):
    tags = 'stdout'
    def write(self, s):
        self.output.AppendText(s)
        if echo: sys.__stderr__.write(s)


#-------------------------------------------------------------------------------

EditorHelper.imgPyCrust = EditorHelper.addPluginImgs('Images\Editor\PyCrust.png')

class PyCrustShellEditor(wxSplitterWindow):
    def __init__(self, parent, wId):
        wxSplitterWindow.__init__(self, parent, wId)

        from wx.py.crust import Shell, Filling

        # XXX argh! PyCrust records the About box pseudo file objs from 
        # XXX sys.in/err/out
        o, i, e = sys.stdout, sys.stdin, sys.stderr
        sys.stdout, sys.stdin, sys.stderr = \
              sys.__stdout__, sys.__stdin__, sys.__stderr__
        try:
            self.shellWin = Shell(self, -1)
        finally:
            sys.stdout, sys.stdin, sys.stderr = o, i, e
            
        self.fillingWin = Filling(self, -1, style=wxSP_3DSASH,
              rootObject=self.shellWin.interp.locals, rootIsNamespace=True)
        
        height = Preferences.screenHeight / 2
        #int(self.GetSize().y * 0.75)
        self.SplitHorizontally(self.shellWin, self.fillingWin, height)
        self.SetMinimumPaneSize(5)

        self.lastResult = 'stdout'
        self._debugger = None

    def destroy(self):
        pass
    
    def execStartupScript(self, startupfile):
        pass
    
    def debugShell(self, doDebug, debugger):
        if doDebug:
            self._debugger = debugger
            self.shellWin.stdout.write('\n## Debug mode turned on.')
            self.pushLine('print "?"')
        else:
            self._debugger = None
            self.pushLine('print "## Debug mode turned %s."'% (doDebug and 'on' or 'off'))
    
    def pushLine(self, line, addText=''):
        if addText:
            self.shellWin.write(addText)

        self.shellWin.push(line)

    def getShellLocals(self):
        return self.shellWin.interp.locals


#-------------------------------------------------------------------------------


shellReg = {'Shell':   (ShellEditor, EditorHelper.imgShell),
            'PyCrust': (PyCrustShellEditor, EditorHelper.imgPyCrust)}
