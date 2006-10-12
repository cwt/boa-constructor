import os, sys, time, socket
import wx

import Preferences, Utils
from Utils import _

try:
    from ExternalLib import xmlrpclib
except ImportError:
    import xmlrpclib

from DebugClient import DebugClient, MultiThreadedDebugClient, \
     EmptyResponseError, DebuggerTask, EVT_DEBUGGER_START, \
     wxEVT_DEBUGGER_START, wxEVT_DEBUGGER_EXC, wxEVT_DEBUGGER_STOPPED


KEEP_STREAMS_OPEN = 1
USE_TCPWATCH = 0
LOG_TRACEBACKS = 0


class TransportWithAuth (xmlrpclib.Transport):
    """Adds a proprietary but simple authentication header to the
    RPC mechanism.  NOTE: this requires xmlrpclib version 1.0.0."""

    def __init__(self, auth):
        self._auth = auth

    def send_user_agent(self, connection):
        xmlrpclib.Transport.send_user_agent(self, connection)
        connection.putheader("X-Auth", self._auth)

    def parse_response(self, f, sock=None):
        # read response from input file, and parse it
        # If there was no response, raise a special exception.
        got_data = 0

        p, u = self.getparser()

        while 1:
            if sock:
                response = sock.recv(1024)
            else:
                response = f.read(1024)
            if not response:
                break
            else:
                got_data = 1
            if self.verbose:
                print "body:", repr(response)
            p.feed(response)

        f.close()
        if not got_data:
            raise EmptyResponseError, _('Empty response from debugger process')

        p.close()
        return u.close()

class UnknownError(Exception):
    pass

def spawnChild(monitor, process, args=''):
    """Returns an xmlrpclib.Server, a connection to an xml-rpc server,
    and the input and error streams.
    """
    # Start ChildProcessServerStart.py in a new process.
    if hasattr(sys, 'frozen'):
        script_fn = os.path.join(os.path.dirname(sys.executable), 'Debugger', 
              'ChildProcessServerStart.py')
    else:
        script_fn = os.path.join(os.path.dirname(__file__),
                             'ChildProcessServerStart.py')
    pyIntpPath = Preferences.getPythonInterpreterPath()
    cmd = '%s "%s" %s' % (pyIntpPath, script_fn, args)
    try:
        pid = wx.Execute(cmd, wx.EXEC_NOHIDE, process)

        line = ''
        if monitor.isAlive():
            istream = process.GetInputStream()
            estream = process.GetErrorStream()

            err = ''
            # read in the port and auth hash
            while monitor.isAlive() and line.find('\n') < 0:
                # don't take more time than the process we wait for ;)
                time.sleep(0.00001)
                if istream.CanRead():
                    line = line + istream.read(1)
                # test for tracebacks on stderr
                if estream.CanRead():
                    err = estream.read()
                    if LOG_TRACEBACKS:
                        if hasattr(sys, 'frozen'):
                            fn = os.path.join(os.path.dirname(sys.executable), 'DebugTracebacks.txt')
                        else:
                            fn = os.path.join(os.path.dirname(__file__), 'DebugTracebacks.txt')
                        open(fn, 'a').write(err)
                    errlines = err.split('\n')
                    while not errlines[-1].strip(): del errlines[-1]
                    try:
                        exctype, excvalue = errlines[-1].split(':')
                    except ValueError:
                        # XXX non standard output on stderr
                        # XXX possibly warnings
                        # XXX for now ignore it (it's non fatal)
                        
                        #raise UnknownError, errlines[-1]
                        continue
                        
                    while errlines and errlines[-1][:7] != '  File ':
                        del errlines[-1]
                    if errlines:
                        errfile = ' (%s)' % errlines[-1].strip()
                    else:
                        errfile = ''
                    try:
                        Error, val = __builtins__[exctype.strip()], (excvalue.strip()+errfile)
                    except KeyError:
                        Error, val = UnknownError, (exctype.strip()+':'+excvalue.strip()+errfile)
                    raise Error, val

        if not KEEP_STREAMS_OPEN:
            process.CloseOutput()

        if monitor.isAlive():
            line = line.strip()
            if not line:
                raise RuntimeError, (
                    _('The debug server address could not be read'))
            port, auth = line.strip().split()

            if USE_TCPWATCH:
                # Start TCPWatch as a connection forwarder.
                from thread import start_new_thread
                new_port = 20202  # Hopefully free
                def run_tcpwatch(port1, port2):
                    os.system("tcpwatch -L %d:127.0.0.1:%d" % (
                        int(port1), int(port2)))
                start_new_thread(run_tcpwatch, (new_port, port))
                time.sleep(3)
                port = new_port

            trans = TransportWithAuth(auth)
            server = xmlrpclib.Server(
                'http://127.0.0.1:%d' % int(port), trans)
            return server, istream, estream, pid, pyIntpPath
        else:
            raise RuntimeError, _('The debug server failed to start')
    except:
        if monitor.isAlive():
            process.CloseOutput()
        monitor.kill()
        raise


###################################################################


class ChildProcessClient(MultiThreadedDebugClient):

    server = None       # An xmlrpclib.Server instance
    processId = 0
    process = None      # A wx.Process
    input_stream = None
    error_stream = None
    pyIntpPath = None
    
    def __init__(self, win, process_args=''):
        self.process_args = process_args
        DebugClient.__init__(self, win)
        win.Bind(EVT_DEBUGGER_START, self.OnDebuggerStart, id=self.win_id)

    def invokeOnServer(self, m_name, m_args=(), r_name=None, r_args=()):
        task = DebuggerTask(self, m_name, m_args, r_name, r_args)
        if self.server is None:
            # Start the process, making sure the spawn occurs
            # in the main thread *only*.
            evt = self.createEvent(wxEVT_DEBUGGER_START)
            evt.SetTask(task)
            self.postEvent(evt)
        else:
            self.taskHandler.addTask(task)

    def invoke(self, m_name, m_args):
        m = getattr(self.server, m_name)
        result = m(*m_args)
        return result

    def isAlive(self):
        return (self.process is not None)

    def kill(self):
        server = self.server
        if server is not None:
            def call_exit(server=server):
                try:
                    server.exit_debugger()
                except (EmptyResponseError, socket.error):
                    # Already stopped.
                    pass
            self.taskHandler.addTask(call_exit)
            self.server = None
        self.input_stream = None
        self.error_stream = None
        process = self.process
        self.process = None
        if process is not None:
            # process.Detach()
            if KEEP_STREAMS_OPEN:
                process.CloseOutput()

##    def __del__(self):
##        pass#self.kill()

    def pollStreams(self):
        stderr_text = ''
        stream = self.error_stream
        if stream is not None and stream.CanRead():
            stderr_text = stream.read()
        stdin_text = ''
        stream = self.input_stream
        if stream is not None and stream.CanRead():
            stdin_text = stream.read()
        
        return (stdin_text, stderr_text)

    def getProcessId(self):
        """Returns the process ID if this client is connected to another
        process."""
        return self.processId

    def OnDebuggerStart(self, evt):
        try:
            wx.BeginBusyCursor()
            try:
                if self.server is None:
                    # Start the subprocess.
                    process = wx.Process(self.event_handler, self.win_id)
                    process.Redirect()
                    self.process = process
                    wx.EVT_END_PROCESS(self.event_handler, self.win_id,
                                       self.OnProcessEnded)
                    (self.server, self.input_stream, self.error_stream,
                     self.processId, self.pyIntpPath) = spawnChild(
                        self, process, self.process_args)
                self.taskHandler.addTask(evt.GetTask())
            except:
                t, v, tb = sys.exc_info()
                evt = self.createEvent(wxEVT_DEBUGGER_EXC)
                evt.SetExc(t, v)
                self.postEvent(evt)
                if LOG_TRACEBACKS:
                    import traceback
                    fn = os.path.join(os.path.dirname(__file__), 'DebugTracebacks.txt')
                    open(fn, 'a').write(''.join(traceback.format_exception(t, v, tb)))
                del tb
        finally:
            wx.EndBusyCursor()

    def OnProcessEnded(self, evt):
        self.pollStreams()
        self.server = None
        self.kill()
        evt = self.createEvent(wxEVT_DEBUGGER_STOPPED)
        self.postEvent(evt)


if __name__ == '__main__':
    a = wx.PySimpleApp()
    f = wx.Frame(None, -1, '')
    f.Show()
    cpc = ChildProcessClient(f)
    cpc.OnDebuggerStart(None)
    a.MainLoop()
