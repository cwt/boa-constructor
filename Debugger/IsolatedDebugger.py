
import sys, threading, Queue
import pprint
from os.path import normcase, abspath
import bdb
from bdb import Bdb, BdbQuit
from repr import Repr

class DebuggerConnection:
    '''A debugging connection that can be operated via RPC.
    It is possible to operate in both stateful and
    stateless mode.'''

    def __init__(self, controller, id):
        self._controller = controller
        self._id = id
        self._ds = controller._getDebugServer(id)

    def _getMessageTimeout(self):
        return self._controller.getMessageTimeout()
    
    def _callNoWait(self, func_name, do_return, *args, **kw):
        ds = self._ds
        sm = MethodCall(func_name, args, kw, do_return)
        ds.queueServerMessage(sm)
        return sm

    def _callMethod(self, func_name, do_return, *args, **kw):
        ds = self._ds
        sm = MethodCall(func_name, args, kw, do_return)
        sm.setupEvent()
        ds.queueServerMessage(sm)
        sm.wait(self._getMessageTimeout())
        if hasattr(sm, 'exc'):
            try:
                raise sm.exc[0], sm.exc[1], sm.exc[2]
            finally:
                # Circ ref
                del sm.exc
        if not hasattr(sm, 'result'):
            raise DebugError, 'Timed out while waiting for debug server.'
        return sm.result

    def _return(self):
        ds = self._ds
        sm = MethodReturn()
        sm.setupEvent()
        ds.queueServerMessage(sm)
        sm.wait(self._getMessageTimeout())

    def _exit(self):
        ds = self._ds
        sm = ThreadExit()
        sm.setupEvent()
        ds.queueServerMessage(sm)
        sm.wait(self._getMessageTimeout())

    def run(self, cmd, globals=None, locals=None):
        '''Starts debugging.  Stops the process at the
        first source line.  Non-blocking.
        '''
        self._callNoWait('run', 1, cmd, globals, locals)

    def runFile(self, filename, params=()):
        '''Starts debugging.  Stops the process at the
        first source line.  Non-blocking.
        '''
        self._callNoWait('runFile', 1, filename, params)

    def set_continue(self, full_speed=0):
        '''Proceeds until a breakpoint or program stop.
        Non-blocking.
        '''
        self._callNoWait('set_continue', 1, full_speed)

    def set_step(self):
        '''Steps to the next instruction.  Non-blocking.
        '''
        self._callNoWait('set_step', 1)

    def set_step_out(self):
        '''Proceeds until the process returns from the current
        stack frame.  Non-blocking.'''
        self._callNoWait('set_step_out', 1)

    def set_step_over(self):
        '''Proceeds to the next source line in the current frame
        or above.  Non-blocking.'''
        self._callNoWait('set_step_over', 1)

    def set_quit(self):
        '''Quits debugging, executing only the try/finally handlers.
        Non-blocking.
        '''
        ds = self._ds
        # Assist bdb in quitting quickly.  See Bdb.set_quit().
        ds.stopframe = ds.botframe
        ds.returnframe = None
        ds.quitting = 1
        if ds.isRunning():
            self._callNoWait('set_quit', 1)

    # Control breakpoints directly--don't wait for the queue.
    # This allows us to set a breakpoint at any moment.
    def setAllBreakpoints(self, brks):
        '''brks is a list of mappings containing the keys:
        filename, lineno, temporary, enabled, and cond.
        Non-blocking.'''
        ds = self._ds
        ds.clear_all_breaks()
        for brk in brks:
            apply(self.set_break, (), brk)
        
    def set_break(self, filename, lineno, temporary=0, cond=None, enabled=1):
        '''Sets a breakpoint.  Non-blocking.
        '''
        ds = self._ds
        bp = ds.set_break(filename, lineno, temporary, cond)
        if type(bp) == type(''):
            # Note that checking for string type is strange. Argh.
            raise DebugError(bp)
        elif bp is not None and not enabled:
            bp.disable()

    def clear_breaks(self, filename, lineno):
        '''Clears all breakpoints on a line.  Non-blocking.
        '''
        ds = self._ds
        msg = ds.clear_break(filename, lineno)
        if msg is not None:
            raise DebugError(msg)
    
##    def clear_all_breaks(self):
##        '''Clears all breakpoints.  Non-blocking.
##        '''
##        ds = self._ds
##        ds.clear_all_breaks()
    
##    def getSafeLocalsAndGlobals(self):
##        '''Returns the repr-fied mappings of locals and globals in a
##        tuple. Blocking.'''
##        return self._callMethod('getSafeLocalsAndGlobals', 0)

##    def getFrameInfo(self):
##        '''Returns a mapping containing the keys:
##          filename, lineno, funcname, is_exception.
##        Blocking.
##        '''
##        return self._callMethod('getFrameInfo', 0)

##    def getExtendedFrameInfo(self):
##        '''Returns a mapping containing the keys:
##          exc_type, exc_value, stack, frame_stack_len, running.
##        stack is a list of mappings containing the keys:
##          filename, lineno, funcname, modname.
##        The most recent stack entry will be at the last
##        of the list.  Blocking.
##        '''
##        return self._callMethod('getExtendedFrameInfo', 0)

##    def evaluateWatches(self, exprs):
##        '''Evalutes the watches listed in exprs and returns the
##        results. Input is a tuple of mappings with keys name and
##        local, output is a mapping of name -> svalue.  Blocking.
##        '''
##        return self._callMethod('evaluateWatches', 0, exprs)

    def getVariablesAndWatches(self, exprs):
        '''Combines the output from getSafeLocalsAndGlobals() and
        evaluateWatches().  Blocking.
        '''
        return self._callMethod('getVariablesAndWatches', 0, exprs)

    def getWatchSubobjects(self, expr):
        '''Returns a tuple containing the names of subobjects
        available through the given watch expression.'''
        return self._callMethod('getWatchSubobjects', 0, expr)

    def setWatchQueryFrame(self, n):
        '''Temporarily causes watch queries to work on a frame other
        than the topmost.
        '''
        self._callNoWait('selectFrameFromStack', 0, n)

    def pprintVarValue(self, name):
        '''Pretty-prints the value of name.'''
        return self._callMethod('pprintVarValue', 0, name)

    def getInteractionUpdate(self):
        '''Returns a mapping containing the keys:
          exc_type, exc_value, stack, frame_stack_len, running.
        Also returns and empties the stdout and stderr buffers.
        stack is a list of mappings containing the keys:
          filename, lineno, funcname, modname.
        The most recent stack entry will be at the last
        of the list.  Blocking.
        '''
        return self._callMethod('getInteractionUpdate', 0)

    def closeConnection(self):
        '''Terminates the connection to the DebugServer.'''
        self.set_quit()
        self._controller._deleteServer(self._id)


class DebuggerController:
    '''Interfaces between DebuggerConnections and DebugServers.'''

    def __init__(self):
        self._debug_servers = {}
        self._next_server_id = 0
        self._server_id_lock = threading.Lock()
        self._message_timeout = None

    def _newServerId(self):
        self._server_id_lock.acquire()
        try:
            id = str(self._next_server_id)
            self._next_server_id = self._next_server_id + 1
        finally:
            self._server_id_lock.release()
        return id        

    def createServer(self):
        '''Returns a string which identifies a new DebugServer.
        '''
        ds = DebugServer()
        id = self._newServerId()
        self._debug_servers[id] = ds
        return id

    def _deleteServer(self, id):
        del self._debug_servers[id]

    def _getDebugServer(self, id):
        return self._debug_servers[id]

    def getMessageTimeout(self):
        return self._message_timeout


class ServerMessage:
    def setupEvent(self):
        self.event = threading.Event()

    def wait(self, timeout=None):
        if hasattr(self, 'event'):
            self.event.wait(timeout)

    def doExecute(self): return 0
    def doReturn(self): return 0
    def doExit(self): return 0
    def execute(self, ds): pass

class MethodCall (ServerMessage):
    def __init__(self, func_name, args, kw, do_return):
        self.func_name = func_name
        self.args = args
        self.kw = kw
        self.do_return = do_return

    def doExecute(self):
        return 1

    def execute(self, ob):
        try:
            self.result = apply(getattr(ob, self.func_name), self.args,
                                self.kw)
        except SystemExit, BdbQuit:
            raise
        except:
            self.exc = sys.exc_info()
        if hasattr(self, 'event'):
            self.event.set()

    def doReturn(self):
        return self.do_return

class MethodReturn (ServerMessage):
    def doReturn(self):
        if hasattr(self, 'event'):
            self.event.set()
        return 1
    
class ThreadExit (ServerMessage):
    def doExit(self):
        if hasattr(self, 'event'):
            self.event.set()
        return 1


serversQueue = Queue.Queue(0)
free_threads = 0
server_threads_lock = threading.Lock()

# Set keep_threads_alive to 1 when thread-bound variables are
# used in a long-running process (such as Zope.)
# It may be better to leave on anyway.
keep_threads_alive = 1

def serverThread():
    global free_threads
    while 1:
        ds = serversQueue.get()  # Blocks.
        try:
            ds.topServerLoop(1)
        except SystemExit, BdbQuit:
            # A request to exit thread.
            # Ignore: Exit only if do_exit is set.
            pass
        except:
            # Expected to never happen.
            import traceback
            traceback.print_exc()
        server_threads_lock.acquire()
        try:
            ds = None
            if keep_threads_alive:
                # loop and wait to service another DebugServer.
                free_threads = free_threads + 1
            else:
                break
        finally:
            server_threads_lock.release()


class DebugServer (Bdb):

    frame = None
    exc_info = None
    max_string_len = 250
    ignore_stopline = -1

    def __init__(self):
        Bdb.__init__(self)
        self.__queue = Queue.Queue(0)
        self._queue_servicer_running = 0

        self.repr = repr = Repr()
        repr.maxstring = 60
        repr.maxother = 60
        self.maxdict2 = 1000

        self._running = 0
        self.stdoutbuf = ''
        self.stderrbuf = ''
        self.stdinbuf = ''

    def queueServerMessage(self, sm):
        global free_threads
        server_threads_lock.acquire()
        try:
            self.__queue.put(sm)
            if not self._queue_servicer_running:
                self._queue_servicer_running = 1
                if free_threads < 1:
                    t = threading.Thread(target=serverThread)
                    t.setDaemon(1)
                    t.start()
                else:
                    free_threads = free_threads - 1
                serversQueue.put(self)
        finally:
            server_threads_lock.release()

    def executeMessageInPlace(self, sm):
        # Lets the debugger work in an existing thread.
        started = 0
        server_threads_lock.acquire()
        try:
            self.__queue.put(sm)
            if not self._queue_servicer_running:
                self._queue_servicer_running = 1
                started = 1
        finally:
            server_threads_lock.release()
        self.topServerLoop(started)

    def cleanupServer(self):
        self.reset()
        self.frame = None
        self.query_frame = None
        self.exc_info = None

    def topServerLoop(self, started=0):
        try:
            self.serverLoop()
        finally:
            if started:
                server_threads_lock.acquire()
                try:
                    # Make sure all queued messages get processed.
                    while not self.__queue.empty():
                        try:
                            self.oneServerLoop()
                        except:
                            # ??
                            pass
                    self._queue_servicer_running = 0
                finally:
                    server_threads_lock.release()
            self.cleanupServer()

    def serverLoop(self):
        while 1:
            if not self.oneServerLoop():
                break

    def oneServerLoop(self):
        # The heart of this whole mess.  Fetches a message and executes
        # it in the current frame.
        # Should not catch exceptions.
        sm = self.__queue.get()
        if sm.doExecute():
            sm.execute(self)
        if sm.doExit():
            thread.exit()
        if sm.doReturn():
            return 0
        return 1

    # Overrides of Bdb methods.
    def canonic(self, filename):
        # Canonicalize filename.
        # XXX This is expensive.
        return normcase(abspath(filename))

    def stop_here(self, frame):
        # Redefine stopping.
        if frame is self.botframe:
            # Don't stop in the bottom frame.
            return 0
        if self.stopframe is None:
            # Stop anywhere.
            return 1
        if (frame is self.stopframe and
            frame.f_lineno != self.ignore_stopline):
            # Stop in the current frame unless we're on
            # ignore_stopline.
            return 1
        f = self.stopframe
        while f is not self.botframe:
            # Stop at any frame that called stopframe except botframe.
            if frame is f:
                return 1
            f = f.f_back
        return 0

    def set_continue(self, full_speed=0):
        # Don't stop except at breakpoints or when finished
        self.stopframe = self.botframe
        self.returnframe = None
        self.quitting = 0
        if full_speed:
            # no breakpoints; run without debugger overhead
            sys.settrace(None)
            try:
                1 + ''	# raise an exception
            except:
                frame = sys.exc_info()[2].tb_frame.f_back
                while frame and frame is not self.botframe:
                    # Remove all the f_trace attributes
                    # that were created while processing with a
                    # settrace callback enabled.
                    del frame.f_trace
                    frame = frame.f_back

    def set_quit(self):
        Bdb.set_quit(self)
        # Try to not execute anything besides finally clauses.
        # Generate an exception which won't be caught by serverLoop.
        raise BdbQuit

    def set_internal_breakpoint(self, filename, lineno, temporary=0,
                                cond=None):
        if not self.breaks.has_key(filename):
            self.breaks[filename] = []
        list = self.breaks[filename]
        if not lineno in list:
            list.append(lineno)

    # A literal copy of Bdb.set_break() without the print statement
    # at the end, returning the Breakpoint object.
    def set_break(self, filename, lineno, temporary=0, cond=None):
        filename = self.canonic(filename)
        import linecache # Import as late as possible
        line = linecache.getline(filename, lineno)
        if not line:
                return 'That line does not exist!'
        self.set_internal_breakpoint(filename, lineno, temporary, cond)
        return bdb.Breakpoint(filename, lineno, temporary, cond)

    # Bdb callbacks.
    # Note that ignore_stopline probably should be set by the
    # dispatch methods, not the user methods...
    def user_line(self, frame):
        # This method is called when we stop or break at a line
        self.ignore_stopline = -1
        self.frame = frame
        self.query_frame = frame
        self.exc_info = None
        self.serverLoop()
	
    def user_return(self, frame, return_value):
        # This method is called when a return trap is set here
        # frame.f_locals['__return__'] = return_value
        # self.interaction(frame, None)
        pass
	
    def user_exception(self, frame, exc_info):
        # This method should be used to automatically stop
        # when specific exception types occur.
        #self.ignore_stopline = -1
        #self.frame = frame
        #self.query_frame = frame
        #self.exc_info = exc_info
        #self.serverLoop()
        pass

    # Utility methods.
    def runFile(self, filename, params):
        d = {'__name__': '__main__',
             '__doc__': 'Debugging',
             '__builtins__': __builtins__,}
        
        # XXX This is imperfect.
        sys.argv = (filename,) + tuple(params)
        
        try:
            self._running = 1
            self.run("execfile('%s', d)" % filename, {'d':d})
        finally:
            self._running = 0

    def isRunning(self):
        return self._running

    def set_step_out(self):
        # Stop when returning from the current frame.
        if self.frame is not None:
            self.set_return(self.frame)
        else:
            raise DebugError('No current frame')

    def set_step_over(self):
        # Stop on the next line in the current frame or above.
        frame = self.frame
        if frame is not None:
            self.ignore_stopline = frame.f_lineno
            self.set_next(frame)
        else:
            raise DebugError('No current frame')

##    def getFrameInfo(self):
##        if self.query_frame is None:
##            return None
##        frame = self.query_frame
##        code = frame.f_code
##        co_name = code.co_name
##        file = code.co_filename
##        lineno = frame.f_lineno
##        return {'filename':file, 'lineno':lineno, 'funcname':co_name,
##                'is_exception':(not not self.exc_info)}

    def getExtendedFrameInfo(self):
        exc_info = self.exc_info
        try:
            if exc_info is not None:
                try:
                    exc_type, exc_value, exc_tb = exc_info
                    try:
                        exc_type = exc_type.__name__
                    except AttributeError:
                        # Python 2.x -> ustr()?
                        exc_type = "%s" % str(exc_type)
                    if exc_value is not None:
                        exc_value = self.safeRepr(exc_value)
                    stack, frame_stack_len = self.get_stack(
                        exc_tb.tb_frame, exc_tb)
                finally:
                    exc_tb = None
            else:
                exc_type = None
                exc_value = None
                stack, frame_stack_len = self.get_stack(
                    self.frame, None)
            stack_summary = []
            # Ignore the first stack entry.
            stack = stack[1:]
            for frame, lineno in stack:
                try:
                    modname = frame.f_globals['__name__']
                except:
                    modname = ''
                code = frame.f_code
                filename = code.co_filename
                co_name = code.co_name
                stack_summary.append(
                    {'filename':filename, 'lineno':lineno,
                     'funcname':co_name, 'modname':modname})
            return {'exc_type':exc_type, 'exc_value':exc_value,
                    'stack':stack_summary,
                    'frame_stack_len':frame_stack_len,
                    'running':self._running}
        finally:
            stack = None

    def getSafeLocalsAndGlobals(self):
        if self.query_frame is None:
            return None
        l = self.safeReprDict(self.query_frame.f_locals)
        g = self.safeReprDict(self.query_frame.f_globals)
        return (l, g)

    def evaluateWatches(self, exprs):
        if self.query_frame is None:
            return None
        localsDict = self.query_frame.f_locals
        globalsDict = self.query_frame.f_globals
        rval = {}
        for info in exprs:
            name = info['name']
            local = info['local']
            if local:
                primaryDict = localsDict
            else:
                primaryDict = globalsDict
            if has_key(primaryDict, name):
                value = primaryDict[name]
            else:
                try:
                    value = eval(name, globalsDict, localsDict)
                except Exception, message:
                    value = '??? (%s)' % message
            svalue = self.safeRepr(value)
            rval[name] = svalue
        return rval

    def getVariablesAndWatches(self, expr):
        # Generate a three-element tuple.
        return (self.getSafeLocalsAndGlobals() +
                (self.evaluateWatches(expr),))

    def getWatchSubobjects(self, expr):
        '''Returns a tuple containing the names of subobjects
        available through the given watch expression.'''
        localsDict = self.query_frame.f_locals
        globalsDict = self.query_frame.f_globals
        try: inst_items = dir(eval(expr, globalsDict, localsDict))
        except: inst_items = ()
        try: clss_items = dir(eval(expr, globalsDict, localsDict)
                              .__class__)
        except: clss_items = ()
        return inst_items + clss_items

    def setQueryFrame(self, n):
        query_frame = self.frame
        while query_frame is not None and n > 0:
            query_frame = query_frame.f_back
        self.query_frame = query_frame

    def pprintVarValue(self, name):
        if self.query_frame:
            frame = self.query_frame
            l, g = frame.f_locals, frame.f_globals
            if l.has_key(name): d = l
            elif g.has_key(name): d = g
            else: return ''
#            return self.repr.repr(d[name])
            return pprint.pformat(d[name])
        else:
            return ''

    def getInteractionUpdate(self):
        rval = {'stdout':self.stdoutbuf,
                'stderr':self.stderrbuf,
                }
        self.stdoutbuf = ''
        self.stderrbuf = ''
        info = self.getExtendedFrameInfo()
        rval.update(info)
        return rval

    def safeRepr(self, s):
        return self.repr.repr(s)

    def safeReprDict(self, dict):
        rval = {}
        l = dict.items()
        if len(l) >= self.maxdict2:
            l = l[:self.maxdict2]
        for key, value in l:
            rval[self.safeRepr(key)] = self.safeRepr(value)
        return rval

