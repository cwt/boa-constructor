
import string, sys
from string import rfind
from Tasks import ThreadedTaskHandler
from wxPython.wx import NewId, wxPyCommandEvent, wxYield

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



from wxPython.wx import wxExecute, wxProcess, wxYield
from xmlrpc import xmlrpclib
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


class SpawningDebugClient (MultiThreadedDebugClient):

    server = None

    def invokeOnServer(self, m_name, m_args=(), r_name=None, r_args=()):
        if self.server is None:
            self.spawnServer()
        print 'comm started'
        MultiThreadedDebugClient.invokeOnServer(
            self, m_name, m_args, r_name, r_args)

    def invoke(self, m_name, m_args):
        m = getattr(self.server, m_name)
        result = apply(m, m_args)
        print 'comm ended'
        return result

    def spawnServer(self):
        dsp = os.path.join(package_home(globals()), 'DebugServerProcess.py')
        process = wxProcess()
        process.Redirect()
        wxExecute('%s "%s"' % (sys.executable, dsp), 0, process)

        line = ''
        while string.find(line, '\n') < 0:
            stream = process.GetInputStream()
            if not stream.eof():
                text = stream.read()
                line = line + text
            else:
                wxYield()
 
        port, auth = string.split(string.strip(line))
        self.server = xmlrpclib.Server('http://localhost:%s' % port)
