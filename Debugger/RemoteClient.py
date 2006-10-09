import os, sys, base64
try:
    from ExternalLib import xmlrpclib
except ImportError:
    import xmlrpclib

class TransportWithAuthentication (xmlrpclib.Transport):
    """Adds a proprietary but simple authentication header to the
    RPC mechanism.  NOTE: this requires xmlrpclib version 1.0.0."""

    def __init__(self, user, pw):
        self._auth = 'basic %s' % base64.encodestring(
            '%s:%s' % (user, pw)).strip()

    def send_user_agent(self, connection):
        xmlrpclib.Transport.send_user_agent(self, connection)
        connection.putheader("Authentication", self._auth)


from DebugClient import DebugClient, MultiThreadedDebugClient, \
     DebuggerTask

class RemoteClient (MultiThreadedDebugClient):

    server = None
    pyIntpPath = ''

    def __init__(self, win, host, port, user, pw):
        DebugClient.__init__(self, win)
        self.host = host
        self.port = port
        self.user = user
        self.pw = pw

    def invoke(self, m_name, m_args):
        if self.server is None:
            trans = TransportWithAuthentication(self.user, self.pw)
            url = 'http://%s:%d/RemoteDebug' % (
                self.host, int(self.port))
            self.server = xmlrpclib.Server(url, trans)
        m = getattr(self.server, m_name)
        result = m(*m_args)
        return result

    def kill(self):
        if self.server is not None:
            # Let the debugged process know about the disconnect.
            self.taskHandler.addTask(
                self.server.set_disconnect, ())
        self.server = None

    def pollStreams(self):
        pass

    def isAlive(self):
        return self.server is not None
