
import sys
from Tasks import ThreadedTaskHandler
from wxPython.wx import NewId, wxPyCommandEvent

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
