
import string, sys
from string import rfind
from Tasks import ThreadedTaskHandler
from wxPython.wx import NewId, wxPyCommandEvent, wxYield
import thread

'''
    The client starts and connects to the debug server.  The process
    being debugged runs on the debug server.
'''

wxEVT_DEBUGGER_OK = NewId()
wxEVT_DEBUGGER_EXC = NewId()

def EVT_DEBUGGER_OK(win, id, func):
    win.Connect(id, -1, wxEVT_DEBUGGER_OK, func)

def EVT_DEBUGGER_EXC(win, id, func):
    win.Connect(id, -1, wxEVT_DEBUGGER_EXC, func)

class DebuggerCommEvent(wxPyCommandEvent):
    receiver_name = None
    receiver_args = ()
    result = None
    t = None
    v = None

    def __init__(self, evtType, id):
        wxPyCommandEvent.__init__(self, evtType, id)

    def SetResult(self, result):
        self.result = result

    def GetResult(self):
        return self.result

    def SetReceiverName(self, name):
        self.receiver_name = name

    def GetReceiverName(self):
        return self.receiver_name

    def SetReceiverArgs(self, args):
        self.receiver_args = args

    def GetReceiverArgs(self):
        return self.receiver_args

    def SetExc(self, t, v):
        self.t, self.v = t, v

    def GetExc(self):
        return self.t, self.v
    

class DebugClient:
    def __init__(self, win):
        self.win_id = win.GetId()
        self.event_handler = win.GetEventHandler()

    def invokeOnServer(self, m_name, m_args=(), r_name=None, r_args=()):
        pass

    def stop(self):
        pass


from IsolatedDebugger import NonBlockingDebuggerConnection, \
     DebuggerController
class InProcessDebugClient (DebugClient):

    dc = DebuggerController()

    def __init__(self, win):
        DebugClient.__init__(self, win)
        self.conn_id = self.dc.createServer()

    def invokeOnServer(self, m_name, m_args=(), r_name=None, r_args=()):
        conn = NonBlockingDebuggerConnection(self.dc, self.conn_id)
        cb = InProcessCallback(
            self.event_handler, self.win_id, r_name, r_args)
        conn.setCallback(cb)
        try:
            apply(getattr(conn, m_name), m_args)
        except:
            cb.notifyException()

    def __del__(self):
        conn_id = self.conn_id
        self.conn_id = None
        self.dc.deleteServer(conn_id)


class InProcessCallback:
    def __init__(self, event_handler, win_id, r_name, r_args):
        self.event_handler = event_handler
        self.win_id = win_id
        self.r_name = r_name
        self.r_args = r_args
    
    def notifyReturn(self, result):
        if self.r_name:
            evt = DebuggerCommEvent(wxEVT_DEBUGGER_OK, self.win_id)
            evt.SetReceiverName(self.r_name)
            evt.SetReceiverArgs(self.r_args)
            evt.SetResult(result)
            self.event_handler.AddPendingEvent(evt)

    def notifyException(self):
        t, v = sys.exc_info()[:2]
        evt = DebuggerCommEvent(wxEVT_DEBUGGER_EXC, self.win_id)
        evt.SetExc(t, v)
        self.event_handler.AddPendingEvent(evt)


class DebuggerTask:
    def __init__(self, client, m_name, m_args, r_name, r_args):
        self.client = client
        self.m_name = m_name
        self.m_args = m_args
        self.r_name = r_name
        self.r_args = r_args

    def __call__(self):
        evt = None
        try:
            result = self.client.invoke(self.m_name, self.m_args)
        except:
            t, v = sys.exc_info()[:2]
            evt = DebuggerCommEvent(wxEVT_DEBUGGER_EXC,
                                    self.client.win_id)
            evt.SetExc(t, v)
        else:
            if self.r_name:
                evt = DebuggerCommEvent(wxEVT_DEBUGGER_OK,
                                        self.client.win_id)
                evt.SetReceiverName(self.r_name)
                evt.SetReceiverArgs(self.r_args)
                evt.SetResult(result)
        if evt:
            self.client.event_handler.AddPendingEvent(evt)
        

class MultiThreadedDebugClient (DebugClient):

    taskHandler = ThreadedTaskHandler()

    def invoke(self, m_name, m_args):
        pass

    def invokeOnServer(self, m_name, m_args=(), r_name=None, r_args=()):
        task = DebuggerTask(self, m_name, m_args, r_name, r_args)
        self.taskHandler.addTask(task)



from ExternalLib import xmlrpclib
import os

def package_home(globals_dict):
    __name__=globals_dict['__name__']
    m=sys.modules[__name__]
    if hasattr(m,'__path__'):
        r=m.__path__[0]
    elif "." in __name__:
        r=sys.modules[__name__[:rfind(__name__,'.')]].__path__[0]
    else:
        r=__name__
    if __name__ == '__main__':
        return os.getcwd()
    else:
        return os.path.join(os.getcwd(), r)


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



class SpawningDebugClient (MultiThreadedDebugClient):

    spawn_lock = None
    server = None

    def __init__(self, win):
        DebugClient.__init__(self, win)
        self.spawn_lock = thread.allocate_lock()

    def invokeOnServer(self, m_name, m_args=(), r_name=None, r_args=()):
        MultiThreadedDebugClient.invokeOnServer(
            self, m_name, m_args, r_name, r_args)

    def invoke(self, m_name, m_args):
        if self.server is None:
            self.spawn_lock.acquire()
            try:
                if self.server is None:
                    self.spawnServer()
            finally:
                self.spawn_lock.release()
        if self.server is None:
            raise Exception('Debug server closed')  # Probably never happen
        m = getattr(self.server, m_name)
        result = apply(m, m_args)
        return result

    def spawnServer(self):
        dsp = os.path.join(
            package_home(globals()), 'DebugServerProcess.py')
        homepath = os.getcwd()  # XXX This won't always work.
        cmd = '%s "%s" -p "%s"' % (sys.executable, dsp, homepath)
        if hasattr(os, 'popen3'):
            ostream, istream, eistream = os.popen3(cmd)
        else:
            # Note: something will likely fail if this is ever reached
            # by Windows 9x because Python 1.52 does not have
            # os.popen3 and popen() on Python 1.52 reveals a Windows
            # bug, later covered up by Python 2.0.
            import popen2
            istream, ostream, eistream = popen2.popen3(cmd)

        line = istream.read(51)
        while string.find(line, '\n') < 0:
            line = line + istream.read(1)
        port, auth = string.split(string.strip(line))

        trans = TransportWithAuth(auth)
        self.server = xmlrpclib.Server(
            'http://localhost:%s' % port, trans)
        # Note that if any exception occurs, none of the
        # streams will be kept and therefore will be closed.
        # DebugServerProcess will shut itself down.  self.server
        # will also continue to be "None".
        self.ostream = ostream
        self.istream = istream
        self.eistream = eistream

    def close(self):
        self.spawn_lock.acquire()
        try:
            # Implicitly close the streams.
            self.server = None
            self.ostream = None
            self.istream = None
            self.eistream = None
        finally:
            self.spawn_lock.release()
