import sys

if __name__ == '__main__':
    sys.path.append('.')  # Fix later

from ExternalLib.xmlrpcserver import RequestHandler
from SocketServer import StreamRequestHandler
from IsolatedDebugger import DebuggerController, DebuggerConnection

verify_auth = 1

class DebugRequestHandler (RequestHandler):

    _authstr = None
    __dc = DebuggerController()
    __conn_id = __dc.createServer()
    __conn = DebuggerConnection(__dc, __conn_id)

    def call(self, method, params):
	# override this method to implement RPC methods
        print 'DebugSP step 1'
        h = self.headers
        if verify_auth and (not h.has_key('x-auth') or h['x-auth']
            != self._authstr):
            raise 'Unauthorized', 'x-auth missing or incorrect'
        m = getattr(self.__conn, method)
        print 'DebugSP step 2'
        result = apply(m, params)
        print 'DebugSP step 3'
        if result is None:
            result = 0
        return result

    #def log_message(self, format, *args):
    #    pass


if __name__ == '__main__':

    import whrandom, sha, threading
    from Tasks import ThreadedTaskHandler
    from SocketServer import TCPServer

    class TaskingMixIn:
        """Mix-in class to handle each request in a task thread."""
        __tasker = ThreadedTaskHandler()

        def process_request(self, request, client_address):
            """Start a task to process the request."""
            self.__tasker.addTask(self.finish_request,
                                  args=(request, client_address))

    class TaskingTCPServer(TaskingMixIn, TCPServer): pass

    auth = sha.new(str(whrandom.random())).hexdigest()  # Always 40 chars.
    # Setting a class attribute this way is unsightly...
    DebugRequestHandler._authstr = auth

    # port is 0 to allocate any port.
    server = TaskingTCPServer(('', 0), DebugRequestHandler)
    port = int(server.socket.getsockname()[1])
    sys.stdout.write('%010d %s\n' % (port, auth))
    sys.stdout.flush()

    def serve_forever(server):
        while 1:
            server.handle_request()

    t = threading.Thread(target=serve_forever, args=(server,))
    t.setDaemon(1)
    t.start()

    # Serve until the stdin pipe closes.
    sys.stdin.read()
    sys.exit(0)
