
import sys, os
import whrandom, sha, threading
from SocketServer import TCPServer
from ExternalLib.xmlrpcserver import RequestHandler
from IsolatedDebugger import DebuggerController, DebuggerConnection
from Tasks import ThreadedTaskHandler


class DebugRequestHandler (RequestHandler):

    _authstr = None
    __dc = DebuggerController()
    __conn_id = __dc.createServer()
    _conn = DebuggerConnection(__dc, __conn_id)

    def call(self, method, params):
	# override this method to implement RPC methods
        h = self.headers
        if self._authstr and (not h.has_key('x-auth') or h['x-auth']
            != self._authstr):
            raise 'Unauthorized', 'x-auth missing or incorrect'
        m = getattr(self._conn, method)
        result = apply(m, params)
        if result is None:
            result = 0
        return result

    def log_message(self, format, *args):
        pass


class FlushingStream:

    def __init__(self, s):
        self.s = s

    def __getattr__(self, name):
        return getattr(self.s, name)

    def write(self, data):
        self.s.write(data)
        self.s.flush()

    def writelines(self, data):
        self.s.writelines(data)
        self.s.flush()


def main():

    class TaskingMixIn:
        """Mix-in class to handle each request in a task thread."""
        __tasker = ThreadedTaskHandler()

        def process_request(self, request, client_address):
            """Start a task to process the request."""
            self.__tasker.addTask(self.finish_request,
                                  args=(request, client_address))

    class TaskingTCPServer(TaskingMixIn, TCPServer): pass

    auth = sha.new(str(whrandom.random())).hexdigest()  # Always 40 chars.
    DebugRequestHandler._authstr = auth

    # port is 0 to allocate any port.
    server = TaskingTCPServer(('', 0), DebugRequestHandler)
    port = int(server.socket.getsockname()[1])
    sys.stdout.write('%010d %s%s' % (port, auth, os.linesep))
    sys.stdout.flush()

    sys.stdout = FlushingStream(sys.stdout)
    sys.stderr = FlushingStream(sys.stderr)

    #sys.stdout = DebugRequestHandler._conn._getStdoutBuf()
    #sys.stderr = DebugRequestHandler._conn._getStderrBuf()

    def serve_forever(server):
        while 1:
            server.handle_request()

    t = threading.Thread(target=serve_forever, args=(server,))
    t.setDaemon(1)
    t.start()

    # Serve until the stdin pipe closes.
    sys.stdin.read()
    sys.exit(0)


if __name__ == '__main__':
    main()
