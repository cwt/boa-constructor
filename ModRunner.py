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

class ModuleRunner:
    def __init__(self, esf, app):
        self.esf = esf
        self.esf.app = app

    def run(self, cmd):
        pass

    def checkError(self, err, caption, out = None):
        if err or out:
            self.esf.updateCtrls(err, out)
            self.esf.Show(true)
            print 'MR shown'
            return self.esf
        else:
            return None

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
    def run(self, cmd):
        import ProcessProgressDlg, ErrorStack
        dlg = ProcessProgressDlg.ProcessProgressDlg(self.editor, cmd, 'Execute module')
        try:
            dlg.ShowModal()
            serr = ErrorStack.buildErrorList(dlg.errors)
            if len(serr):
                return self.checkError(serr, 'Ran', dlg.output)
            else:
                return None

        finally:
            dlg.Destroy()

class PopenModuleRunner(ModuleRunner):
    """ Uses Python's popen2, output and errors are redirected and displayed
        in a frame. """
    def run(self, cmd):
        from popen2import import popen3
        import ErrorStack
        inp, outp, errp = popen3(cmd)

        out = []
        while 1:
            l = outp.readline()
            if not l: break
            out.append(l)
            print l,

        serr = ErrorStack.errorList(errp)

        if serr or out:
            return self.checkError(serr, 'Ran', out)
        else:
            return None

PreferredRunner = PopenModuleRunner
