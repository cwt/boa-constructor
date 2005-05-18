from DebugClient import DebugClient, DebuggerCommEvent, \
     wxEVT_DEBUGGER_OK, wxEVT_DEBUGGER_EXC
from IsolatedDebugger import NonBlockingDebuggerConnection, DebuggerController


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


class InProcessClient (DebugClient):

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
            getattr(conn, m_name)(*m_args)
        except:
            cb.notifyException()

    def __del__(self):
        conn_id = self.conn_id
        self.conn_id = None
        self.dc.deleteServer(conn_id)
