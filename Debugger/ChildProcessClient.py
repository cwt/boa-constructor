
import os, string, sys, threading
from DebugClient import DebugClient, MultiThreadedDebugClient, \
     DebuggerTask, wxEVT_DEBUGGER_EXC, wxEVT_DEBUGGER_STDIO, \
     wxEVT_DEBUGGER_START, EVT_DEBUGGER_START
from ExternalLib import xmlrpclib
from wxPython.wx import wxProcess, wxExecute, EVT_IDLE, EVT_END_PROCESS


class TransportWithAuth (xmlrpclib.Transport):
    """Adds an authentication header to the RPC mechanism"""

    def __init__(self, auth):
        self._auth = auth

    def request(self, host, handler, request_body):
	# issue XML-RPC request

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


class ChildProcessClient (wxProcess, MultiThreadedDebugClient):

    server = None
    process = None

    def __init__(self, win):
        DebugClient.__init__(self, win)
        self.win = win
        EVT_IDLE(win, self.OnIdle)
        EVT_END_PROCESS(win, win.GetId(), self.OnProcessEnded)
        EVT_DEBUGGER_START(win, win.GetId(), self.OnDebuggerStart)

    def invokeOnServer(self, m_name, m_args=(), r_name=None, r_args=()):
        task = DebuggerTask(self, m_name, m_args, r_name, r_args)
        if self.server is None:
            evt = self.createEvent(wxEVT_DEBUGGER_START)
            evt.SetTask(task)
            self.postEvent(evt)
        else:
            self.taskHandler.addTask(task)

    def invoke(self, m_name, m_args):
        m = getattr(self.server, m_name)
        result = apply(m, m_args)
        return result

    def spawnServer(self):
        dsp = find_script(('Debugger', 'ChildProcessServerStart.py'))
        os.environ['PYTHONPATH'] = string.join(sys.path, os.pathsep)
        cmd = '%s "%s"' % (sys.executable, dsp)
        self.process = wxProcess(self.win, self.win_id)
        self.process.Redirect()
        try:
            pid = wxExecute(cmd, 0, self.process)
            if self.process:
                istream = self.process.GetInputStream()
                line = istream.read(51)
            while self.process and string.find(line, '\n') < 0:
                line = line + istream.read(1)
            if self.process:
                port, auth = string.split(string.strip(line))
                trans = TransportWithAuth(auth)
                self.server = xmlrpclib.Server(
                    'http://localhost:%s' % port, trans)
            else:
                raise Exception('Debug server failed to start')
        except:
            self.process = None
            raise

    def __del__(self):
        if self.process is not None:
            self.process.Detach()
            self.process.CloseOutput()
            self.process = None

    def _receiveStreamData(self):
        if self.process is not None:
            text = ''
            stream = self.process.GetInputStream()
            if not stream.eof():
                text = stream.read()
            stream = self.process.GetErrorStream()
            if not stream.eof():
                text = text + stream.read()
            if text:
                evt = self.createEvent(wxEVT_DEBUGGER_STDIO)
                evt.SetResult(text)
                self.postEvent(evt)

    def OnDebuggerStart(self, evt):
        try:
            if self.server is None:
                self.spawnServer()
            self.taskHandler.addTask(evt.GetTask())
        except:
            t, v = sys.exc_info()[:2]
            evt = self.createEvent(wxEVT_DEBUGGER_EXC)
            evt.SetExc(t, v)
            self.postEvent(evt)

    def OnIdle(self, evt):
        self._receiveStreamData()

    def OnProcessEnded(self, evt):
        self._receiveStreamData()
        self.process.CloseOutput()
        self.process.Detach()
        self.process = None
        self.server = None
        # TODO: Post a wxEVT_DEBUGGER_STOPPED event.
