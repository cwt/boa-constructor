
import os, string, sys
from ExternalLib import xmlrpclib
from wxPython.wx import wxProcess, wxExecute


class TransportWithAuth (xmlrpclib.Transport):
    """Adds an authentication header to the RPC mechanism"""

    def __init__(self, auth):
        self._auth = auth

    def request(self, host, handler, request_body):
	# issue XML-RPC request
        if host == 'localhost':
            host = ''  # Trigger "special" name

	import httplib
	h = httplib.HTTP(host)
	h.putrequest("POST", handler)

	# required by HTTP/1.1
	h.putheader("Host", host)

	# required by XML-RPC
	h.putheader("User-Agent", self.user_agent)
	h.putheader("Content-Type", "text/xml")
	h.putheader("Content-Length", str(len(request_body)))
	h.putheader("X-Auth", self._auth)

	h.endheaders()

	if request_body:
	    h.send(request_body)

	errcode, errmsg, headers = h.getreply()

	if errcode != 200:
	    raise ProtocolError(
		host + handler,
		errcode, errmsg,
		headers
		)

	return self.parse_response(h.getfile())


def find_script(path):
    join = os.path.join
    exists = os.path.exists
    for dir in sys.path:
        p = apply(join, (dir,) + path)
        if exists(p):
            # Found it.
            if dir == '':
                # Expand to the full path name.
                p = os.path.abspath(p)
            return p
    raise IOError('Script not found: ' + apply(join, path))

def spawnChild(monitor, process):
    dsp = find_script(('Debugger', 'ChildProcessServerStart.py'))
    os.environ['PYTHONPATH'] = string.join(sys.path, os.pathsep)
    cmd = '%s "%s"' % (sys.executable, dsp)
    try:
        monitor.alive = 1
        pid = wxExecute(cmd, 0, process)
        if monitor.alive:
            istream = process.GetInputStream()
            line = istream.read(51)
        while monitor.alive and string.find(line, '\n') < 0:
            line = line + istream.read(1)
        if monitor.alive:
            port, auth = string.split(string.strip(line))
            trans = TransportWithAuth(auth)
            server = xmlrpclib.Server(
                'http://localhost:%s' % port, trans)
            return server
        else:
            raise 'DebugError', 'The debug server failed to start'
    except:
        if monitor.alive:
            process.CloseOutput()
        monitor.alive = 0
        raise


###################################################################


from DebugClient import DebugClient, MultiThreadedDebugClient, \
     DebuggerTask, wxEVT_DEBUGGER_EXC, \
     wxEVT_DEBUGGER_START, EVT_DEBUGGER_START
from wxPython.wx import EVT_END_PROCESS


class ChildProcessClient (MultiThreadedDebugClient):

    server = None
    alive = 0

    def __init__(self, win):
        DebugClient.__init__(self, win)
        self.process = wxProcess(win, self.win_id)
        self.process.Redirect()
        EVT_END_PROCESS(win, self.win_id, self.OnProcessEnded)
        EVT_DEBUGGER_START(win, self.win_id, self.OnDebuggerStart)

    def invokeOnServer(self, m_name, m_args=(), r_name=None, r_args=()):
        task = DebuggerTask(self, m_name, m_args, r_name, r_args)
        if self.server is None:
            # Make sure the spawn occurs in the main thread *only*.
            evt = self.createEvent(wxEVT_DEBUGGER_START)
            evt.SetTask(task)
            self.postEvent(evt)
        else:
            self.taskHandler.addTask(task)

    def invoke(self, m_name, m_args):
        m = getattr(self.server, m_name)
        result = apply(m, m_args)
        return result

    def kill(self):
        if self.alive:
            self.alive = 0
            self.process.Detach()
            self.process.CloseOutput()

    def __del__(self):
        self.kill()

    def pollStreams(self):
        stdin_text = ''
        if self.alive:
            stream = self.process.GetInputStream()
            if not stream.eof():
                stdin_text = stream.read()
        stderr_text = ''
        if self.alive:
            stream = self.process.GetErrorStream()
            if not stream.eof():
                stderr_text = stream.read()
        return (stdin_text, stderr_text)

    def OnDebuggerStart(self, evt):
        try:
            if self.server is None:
                self.server = spawnChild(self, self.process)
            self.taskHandler.addTask(evt.GetTask())
        except:
            t, v = sys.exc_info()[:2]
            evt = self.createEvent(wxEVT_DEBUGGER_EXC)
            evt.SetExc(t, v)
            self.postEvent(evt)

    def OnProcessEnded(self, evt):
        self._receiveStreamData()
        self.alive = 0
        self.process.CloseOutput()
        self.process.Detach()
        self.server = None
        # TODO: Post a wxEVT_DEBUGGER_STOPPED event?
