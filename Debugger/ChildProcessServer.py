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

try: from cStringIO import StringIO
except ImportError: from StringIO import StringIO

serving = 0

class DebugRequestHandler (RequestHandler):

    _authstr = None
    _ds = DebugServer()
    _conn = DebuggerConnection(_ds)
    _conn._enableProcessModification()

    def _authenticate(self):
        h = self.headers
        if self._authstr and (not h.has_key('x-auth') or h['x-auth'] != self._authstr):
            raise 'Unauthorized', 'x-auth missing or incorrect'
        
    def call(self, method, params):
        #print 'DebugRequestHandler.call(%s, %s)' % (method, params)
        #raise 'Fuckup', 'Big'
        self._authenticate()
        if method == 'exit_debugger':
            global serving
            serving = 0
            #print 'DebugRequestHandler exit triggered'
            return 1
        else:
            m = getattr(self._conn, method)
            result = apply(m, params)
            if result is None:
                result = 0
            #print 'DebugRequestHandler.call() result =', result
            return result

    def log_message(self, format, *args):
        pass # don't print http requests
    
##    def exit(self):
##        #print 'DebugRequestHandler.exit()'
##        self._authenticate()
##        global serving
##        serving = 0
##        return 1
        

    #def log_message(self, format, *args):
    #    pass


class TaskingMixIn:
    """Mix-in class to handle each request in a task thread."""
    __tasker = ThreadedTaskHandler()

    def process_request(self, request, client_address):
        """Start a task to process the request."""
        self.__tasker.addTask(self.finish_request,
                              args=(request, client_address))

class TaskingTCPServer(TaskingMixIn, TCPServer): pass


def streamFlushThread():
    while 1:
        sys.stdout.flush()
        sys.stderr.flush()
        sleep(0.15)  # 150 ms


def main():
    auth = sha.new(str(whrandom.random())).hexdigest()  # Always 40 chars.
    DebugRequestHandler._authstr = auth

    # port is 0 to allocate any port.
    server = TaskingTCPServer(('', 0), DebugRequestHandler)
    port = int(server.socket.getsockname()[1])
    sys.stdout.write('%010d %s%s' % (port, auth, os.linesep))
    sys.stdout.flush()

    def serve_forever(server):
        while 1:
            #print 'serve_forever waiting for request...'
            server.handle_request()

    def startDaemon(target, args=()):
        #print 'starting daemon', target
        t = threading.Thread(target=target, args=args)
        t.setDaemon(1)
        t.start()

    startDaemon(serve_forever, (server,))
    startDaemon(streamFlushThread)
    startDaemon(DebugRequestHandler._ds.servicerThread)

    # Serve until the stdin pipe closes.
    #print 'serving until stdin returns EOF'
    #sys.stdin.read()

    global serving; serving = 1
    while serving: 
        time.sleep(0.01)

    #print 'exiting ChildProcessServer'
    sys.exit(0)


if __name__ == '__main__':
    main()
