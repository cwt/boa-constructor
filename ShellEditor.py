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
from Views.StyledTextCtrls import PythonStyledTextCtrlMix
from wxPython.stc import *
from ExternalLib.PythonInterpreter import PythonInterpreter
import string
import Preferences

ps1 = '>>> '
ps2 = '... '

class ShellEditor(wxStyledTextCtrl, PythonStyledTextCtrlMix):
    def __init__(self, parent, wId):
        wxStyledTextCtrl.__init__(self, parent, wId, style = wxCLIP_CHILDREN)
        PythonStyledTextCtrlMix.__init__(self, wId, -1)

        self.interp = PythonInterpreter()
        self.SetLexer(wxSTC_LEX_NULL)
        self.SetText('# Python %s (Boa)\n# %s\n%s'%(sys.version, sys.copyright, ps1))
        self.SetLexer(wxSTC_LEX_PYTHON)
        self.SetCurrentPosition(self.GetTextLength())
##        self.EnsureCaretVisible()
        self.ScrollToColumn(0)
        EVT_CHAR(self, self.OnShellKey)

    def OnShellKey(self, event):
        if event.KeyCode() == 13:
            try:
                tmpstdout = sys.stdout
                tmpstderr = sys.stderr
                line = string.rstrip(self.GetLine(self.GetLineCount() -2)[4:])
                print 'shell line', `line`
                sys.stdout = PseudoFileOut(self)
                sys.stderr = PseudoFileErr(self)

                if self.interp.push(line):
                    self.AddText(ps2)
                else:
                    self.AddText(ps1)
            finally:                
                sys.stdout = tmpstdout
                sys.stderr = tmpstderr
	else: event.Skip()

    def OnUpdateUI(self, event):
	if Preferences.braceHighLight:
            PythonStyledTextCtrlMix.OnUpdateUI(self, event)
        
        
#-----Output redirectors--------------------------------------------------------

class PseudoFile:
    """ Base class for file like objects to facilitate StdOut for the Shell."""
    def __init__(self, output):
        self.output = output

    def writelines(self, l):
        map(self.write, l)
    
    def write(s):
        pass

    def flush(self):
        pass

class PseudoFileOut(PseudoFile):
    tags = 'stderr'
    def write(self, s):
        self.output.SetLexer(wxSTC_LEX_NULL)
        self.output.AddText(s)
        self.output.SetLexer(wxSTC_LEX_PYTHON)
        self.output.Refresh(false)

class PseudoFileErr(PseudoFile):
    tags = 'stdout'
    def write(self, s):
        self.output.SetLexer(wxSTC_LEX_NULL)
        self.output.AddText(s)
        self.output.SetLexer(wxSTC_LEX_PYTHON)
        self.output.Refresh(false)

class PseudoFileOutTC(PseudoFile):
    tags = 'stderr'
    def write(self, s):
        self.output.AppendText(s)

class PseudoFileErrTC(PseudoFile):
    tags = 'stdout'
    def write(self, s):
        self.output.AppendText(s)
