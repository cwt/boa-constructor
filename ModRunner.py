#-----------------------------------------------------------------------------
# Name:        ModRunner.py
# Purpose:     Different process executers.
#
# Author:      Riaan Booysen
#
# Created:     2001/12/02
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
from wxPython.wx import *
from os import path

import ErrorStack

class ModuleRunner:
    def __init__(self, esf, app, runningDir = ''):
        self.init(esf, app)
        self.runningDir = runningDir
        self.results = {}

    def run(self, cmd):
        pass

    def init(self, esf, app):
        self.esf = esf
        if esf:
            self.esf.app = app
        else:
            self.app = app

    def recheck(self):
        if self.results:
            return apply(self.checkError, (), self.results)

    def checkError(self, err, caption, out = None, root = 'Error'):
        if self.esf:
            if err or out:
                self.esf.updateCtrls(err, out, root, self.runningDir)
                self.esf.display(len(err))
                return len(err)
            else:
                return None
        else:
            self.results = {'err': err, 'caption': caption, 'out': out, 'root': root}


class CompileModuleRunner(ModuleRunner):
    """ Uses compiles a module to show errors in frame"""
    def run(self, filename):
        import py_compile
        py_compile.compile(filename)

class ExecuteModuleRunner(ModuleRunner):
    """ Uses wxPython's wxExecute, no redirection """
    def run(self, cmd):
        wxExecute(cmd, true)

class ProcessModuleRunner(ModuleRunner):
    """ Uses wxPython's wxProcess, output and errors are redirected and displayed
        in a frame. A cancelable dialog displays while the process executes
        This currently only works for non GUI processes """
    def run(self, cmd, Parser=ErrorStack.StdErrErrorParser,
            caption='Execute module', root='Error', autoClose=false):
        import ProcessProgressDlg
        dlg = ProcessProgressDlg.ProcessProgressDlg(None, cmd, caption, 
              autoClose=autoClose)
        try:
            dlg.ShowModal()
            serr = ErrorStack.buildErrorList(dlg.errors, Parser)
            if len(serr):
                return self.checkError(serr, 'Ran', dlg.output, root)
            else:
                return None

        finally:
            dlg.Destroy()

class PopenModuleRunner(ModuleRunner):
    """ Uses Python's popen2, output and errors are redirected and displayed
        in a frame. """
    def run(self, cmd):
        from popen2import import popen3
        inp, outp, errp = popen3(cmd)

        out = []
        while 1:
            l = outp.readline()
            if not l: break
            out.append(l)

        serr = ErrorStack.errorList(errp)

        if serr or out:
            return self.checkError(serr, 'Ran', out)
        else:
            return None

PreferredRunner = PopenModuleRunner

wxEVT_EXEC_FINISH = wxNewId()

def EVT_EXEC_FINISH(win, func):
    win.Connect(-1, -1, wxEVT_EXEC_FINISH, func)

class ExecFinishEvent(wxPyEvent):
    def __init__(self, runner):
        wxPyEvent.__init__(self)
        self.SetEventType(wxEVT_EXEC_FINISH)
        self.runner = runner
 