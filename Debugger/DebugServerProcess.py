
import sys
from xmlrpc.xmlrpcserver import RequestHandler
from SocketServer import StreamRequestHandler
from IsolatedDebugger import DebuggerController, DebuggerConnection

stop_server = 0
verify_auth = 0   # Turn on before release!!!

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
        if method == 'quit':
            global stop_server
            stop_server = 1
            return 1
        else:
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

    import whrandom, sha
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

    auth = sha.new(str(whrandom.random())).hexdigest()
    # Setting a class attribute this way is unsightly.
    DebugRequestHandler._authstr = auth

    # port is 0 to allocate any port.
    server = TaskingTCPServer(('', 0), DebugRequestHandler)
    port = server.socket.getsockname()[1]
    sys.stdout.write('%d %s\n' % (port, auth))
    sys.stdout.flush()
    while not stop_server:
        server.handle_request()
