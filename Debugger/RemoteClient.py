import os, string, sys, base64
from ExternalLib import xmlrpclib


class TransportWithAuth (xmlrpclib.Transport):
    """Adds an authentication header to the RPC mechanism"""
    _auth = None

    def __init__(self, user='', pw=''):
        if user:
            self._auth = string.strip(
                base64.encodestring('%s:%s' % (user, pw)))

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
        if self._auth:
            h.putheader('Authorization', 'Basic %s' % self._auth)

        h.endheaders()

        if request_body:
            h.send(request_body)

        errcode, errmsg, headers = h.getreply()

        if errcode != 200:
            raise xmlrpclib.ProtocolError(
                host + handler,
                errcode, errmsg,
                headers
                )

        return self.parse_response(h.getfile())


from DebugClient import DebugClient, MultiThreadedDebugClient, \
     DebuggerTask

class RemoteClient (MultiThreadedDebugClient):

    controller = None
    server = None
    server_id = None

    def __init__(self, win, host, port, user, pw):
        DebugClient.__init__(self, win)
        self.host = host
        self.port = port
        self.user = user
        self.pw = pw

    def invoke(self, m_name, m_args):
        if self.server is None:
            trans = TransportWithAuth(self.user, self.pw)
            url = 'http://%s:%d/RemoteDebugControl' % (
                self.host, int(self.port))
            self.controller = xmlrpclib.Server(url, trans)
            # Create a debugging session on the server.
            self.server_id = self.controller.createServer()
            url = '%s/%s' % (url, self.server_id)
            # url now looks like 'http://host:port/RemoteDebugControl/id'
            self.server = xmlrpclib.Server(url, trans)
        m = getattr(self.server, m_name)
        result = apply(m, m_args)
        return result

    def kill(self):
        if self.controller is not None and self.server_id is not None:
            # Try to free the debug connection on the server.
            self.taskHandler.addTask(
                self.controller.deleteServer, (self.server_id,))
        self.controller = None
        self.server_id = None
        self.server = None

    def pollStreams(self):
        pass
