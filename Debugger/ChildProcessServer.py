
import sys, os, time
import whrandom, sha, threading
from time import sleep
from SocketServer import TCPServer

from IsolatedDebugger import DebugServer, DebuggerConnection
from Tasks import ThreadedTaskHandler


try:
    from ExternalLib.xmlrpcserver import RequestHandler
except:
    # Add parent directory to the path search.
    sys.path[0:0] = [os.pardir]
    from ExternalLib.xmlrpcserver import RequestHandler

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


serving = 0

debug_server = DebugServer()
connection = DebuggerConnection(debug_server)
connection.allowEnvChanges()  # Allow changing of sys.path, etc.
task_handler = ThreadedTaskHandler()
auth_str = ''


class DebugRequestHandler (RequestHandler):

    def _authenticate(self):
        h = self.headers
        if auth_str and (not h.has_key('x-auth')
                         or h['x-auth'] != auth_str):
            raise 'Unauthorized', 'X-Auth header missing or incorrect'

    def call(self, method, params):
        # Override of xmlrpcserver.RequestHandler.call()
        self._authenticate()
        if method == 'exit_debugger':
            global serving
            serving = 0
            return 1
        else:
            m = getattr(connection, method)
            result = apply(m, params)
            if result is None:
                result = 0
            return result

    def log_message(self, format, *args):
        pass


class TaskingMixIn:
    """Mix-in class to handle each request in a task thread."""

    def process_request(self, request, client_address):
        """Start a task to process the request."""
        task_handler.addTask(self.finish_request,
                             args=(request, client_address))

class TaskingTCPServer(TaskingMixIn, TCPServer): pass


def streamFlushThread():
    while 1:
        sys.stdout.flush()
        sys.stderr.flush()
        sleep(0.15)  # 150 ms


def main():
    # Create an authentication string, always 40 characters.
    global auth_str
    auth_str = sha.new(str(whrandom.random())).hexdigest()

    # port is 0 to allocate any port.
    server = TaskingTCPServer(('', 0), DebugRequestHandler)
    port = int(server.socket.getsockname()[1])
    # Tell the client what port to connect to and the auth string to send.
    sys.stdout.write('%010d %s%s' % (port, auth_str, os.linesep))
    sys.stdout.flush()

    # Provide a hard breakpoint hook.  Use it like this:
    # if hasattr(sys, 'breakpoint'): sys.breakpoint()
    sys.breakpoint = debug_server.set_trace

    def serve_forever(server):
        while 1:
            server.handle_request()

    def startDaemon(target, args=()):
        t = threading.Thread(target=target, args=args)
        t.setDaemon(1)
        t.start()

    startDaemon(serve_forever, (server,))
    startDaemon(streamFlushThread)
    startDaemon(debug_server.servicerThread)


    # Serve until the stdin pipe closes.
    #print 'serving until stdin returns EOF'
    #sys.stdin.read()

    global serving; serving = 1
    while serving: 
        time.sleep(0.1)

    sys.exit(0)


if __name__ == '__main__':
    main()
