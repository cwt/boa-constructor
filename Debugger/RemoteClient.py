
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
        if self._auth:
            h.putheader('Authorization', 'Basic %s' % self._auth)

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


from DebugClient import DebugClient, MultiThreadedDebugClient

class RemoteClient (MultiThreadedDebugClient):

    def __init__(self, win, host, port, user, pw):
        DebugClient.__init__(self, win)
        trans = TransportWithAuth(user, pw)
        self.server = xmlrpclib.Server(
            'http://%s:%s' % (host, port), trans)

    def invoke(self, m_name, m_args):
        m = getattr(self.server, m_name)
        result = apply(m, m_args)
        return result

    def kill(self):
        pass

    def pollStreams(self):
        pass
