from wxPython.wx import *
from os import path

class ModuleRunner:
    def __init__(self, editor, app):
        self.editor = editor
        self.app = app
        self.esf = None
    
    def run(self, cmd):
        pass
        
    def checkError(self, err, caption, out = None):    
        if err or out:
            import ErrorStackFrm
            self.esf = ErrorStackFrm.ErrorStackMF(self.editor, self.app, self.editor)
            self.esf.updateCtrls(err, out)
            self.esf.Show(true)
            return self.esf
        else:
            return None
##        else:
##            self.editor.statusBar.setHint('%s %s successfully.' %\
##              (caption, path.basename(self.filename)))

class CompileModuleRunner(ModuleRunner):
    """ Uses compiles a module to show errors in frame"""
    def run(self, filename):
        py_compile.compile(self.filename)
        
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