import time
from StringIO import StringIO

from wxPython.wx import *

class ProcessRunnerMix:
    def __init__(self, input, handler=None):
        if handler is None:
            handler = self
        self.handler = handler    
        EVT_IDLE(handler, self.OnIdle)
        EVT_END_PROCESS(handler, -1, self.OnProcessEnded)

        input.reverse() # so we can pop
        self.input = input
        
        self.reset()

    def reset(self):
        self.process = None
        self.pid = -1
        self.output = []
        self.errors = []
        self.inputStream = None
        self.errorStream = None
        self.outputStream = None
        self.outputFunc = None
        self.errorsFunc = None
        self.finishedFunc = None
        self.finished = false
        self.responded = false

    def execute(self, cmd):
        self.process = wxProcess(self.handler)
        self.process.Redirect()

        self.pid = wxExecute(cmd, wxEXEC_NOHIDE, self.process)

        self.inputStream = self.process.GetOutputStream()
        self.errorStream = self.process.GetErrorStream()
        self.outputStream = self.process.GetInputStream()

        #self.OnIdle()
        wxWakeUpIdle()
    
    def setCallbacks(self, output, errors, finished):
        self.outputFunc = output
        self.errorsFunc = errors
        self.finishedFunc = finished

    def detach(self):
        if self.process is not None:
            self.process.CloseOutput()
            self.process.Detach()
            self.process = None

    def kill(self):
        if self.process is not None:
            self.process.CloseOutput()
            if wxProcess_Kill(self.pid, wxSIGTERM) != wxKILL_OK:
                wxProcess_Kill(self.pid, wxSIGKILL)
            self.process = None

    def updateStream(self, stream, data):
        if stream and stream.CanRead():
            if not self.responded:
                self.responded = true
            text = stream.read()
            data.append(text)
            return text
        else:
            return None

    def updateInpStream(self, stream, input):
        if stream and input:
            line = input.pop()
            stream.write(line)

    def updateErrStream(self, stream, data):
        return self.updateStream(stream, data)

    def updateOutStream(self, stream, data):
        return self.updateStream(stream, data)

    def OnIdle(self, event=None):
        if self.process is not None:
            self.updateInpStream(self.inputStream, self.input)
            e = self.updateErrStream(self.errorStream, self.errors)
            if e is not None and self.errorsFunc is not None:
                wxCallAfter(self.errorsFunc, e)
            o = self.updateOutStream(self.outputStream, self.output)
            if o is not None and self.outputFunc is not None:
                wxCallAfter(self.outputFunc, o)

            #wxWakeUpIdle()
            #time.sleep(0.001)

    def OnProcessEnded(self, event):
        self.OnIdle()

        if self.process:
            self.process.Destroy()
            self.process = None

        self.finished = true
        
        # XXX doesn't work ???
        #self.handler.Disconnect(-1, wxEVT_IDLE)
        
        if self.finishedFunc:
            wxCallAfter(self.finishedFunc)

class ProcessRunner(wxEvtHandler, ProcessRunnerMix):
    def __init__(self, input):
        wxEvtHandler.__init__(self)
        ProcessRunnerMix.__init__(self, input)

def wxPopen3(cmd, input, output, errors, finish, handler=None):
    p = ProcessRunnerMix(input, handler)
    p.setCallbacks(output, errors, finish)
    p.execute(cmd)
    return p

def _test():
    app = wxPySimpleApp()
    f = wxFrame(None, -1, 'asd')#, style=0)
    f.Show()

    def output(v):
        print 'OUTPUT:', v
    def errors(v):
        print 'ERRORS:', v
    def fin():
        p.Close()
        f.Close()
        print 'FINISHED'
        

    def spin(p):
        while not p.finished:
            wxYield()
            time.sleep(0.01)
    
    def evt(self, event):
        input = []
        p = wxPopen3('''c:\\python23\\python.exe -c "print '*'*5000"''', 
                 input, output, errors, fin, f)
        print p.pid
    
    app.MainLoop()

if __name__ == '__main__':
    _test()
    
    