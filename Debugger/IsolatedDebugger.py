#----------------------------------------------------------------------------
# Name:         IsolatedDebugger.py
# Purpose:      A Bdb-based debugger (tracer) that can be operated by
#               another process
#
# Authors:      Shane Hathaway, Riaan Booysen
#
# Created:      November 2000
# RCS-ID:       $Id$
# Copyright:    (c) Shane Hathaway, Riaan Booysen
# Licence:      GPL
#----------------------------------------------------------------------------

import sys, thread, threading, Queue
import pprint
from os import chdir
from os import path
import bdb
from bdb import Bdb, BdbQuit, Breakpoint
from repr import Repr



class DebugError(Exception):
    """Incorrect operation of the debugger"""



class DebuggerConnection:
    """A debugging connection that can be operated via RPC.
    """

    def __init__(self, ds):
        """Creates a DebuggerConnection that wraps around a DebugServer."""
        self._ds = ds

    def _callNoWait(self, func_name, do_return, *args, **kw):
        sm = MethodCall(func_name, args, kw, do_return)
        sm.setWait(0)
        self._ds.queueServerMessage(sm)

    def _callMethod(self, func_name, do_return, *args, **kw):
        sm = MethodCall(func_name, args, kw, do_return)
        sm.setupEvent()
        self._ds.queueServerMessage(sm)
        # Block.
        res = sm.getResult()
        return res

    ### Non-blocking calls.

    def allowEnvChanges(self, allow=1):
        """Allows the debugger to set sys.path, sys.argv, and
        use os.chdir().
        """
        self._ds._allow_env_changes = allow

    def run(self, cmd, globals=None, locals=None):
        """Starts debugging.  Stops the process at the
        first source line.  Non-blocking.
        """
        self._callNoWait('run', 1, cmd, globals, locals)

    def runFile(self, filename, params=(), autocont=0, add_paths=()):
        """Starts debugging.  Stops the process at the
        first source line.  Use the autocont parameter to proceed immediately
        rather than stop.  Non-blocking.
        """
        self._callNoWait('runFile', 1, filename, params, autocont, add_paths)

    def set_continue(self, full_speed=0):
        """Proceeds until a breakpoint or program stop.
        Non-blocking.
        """
        self._callNoWait('set_continue', 1, full_speed)

    def set_step(self):
        """Steps to the next instruction.  Non-blocking.
        """
        self._callNoWait('set_step', 1)

    def set_step_out(self):
        """Proceeds until the process returns from the current
        stack frame.  Non-blocking."""
        self._callNoWait('set_step_out', 1)

    def set_step_over(self):
        """Proceeds to the next source line in the current frame
        or above.  Non-blocking."""
        self._callNoWait('set_step_over', 1)

    def set_pause(self):
        """Stops as soon as possible.  Non-blocking and immediate.
        """
        self._ds.stopAnywhere()

    def set_quit(self):
        """Quits debugging, executing only the try/finally handlers.
        Non-blocking and immediate.
        """
        self._ds.stopAnywhere()
        if self._ds.isRunning():
            self._callNoWait('set_quit', 1)

    def setAllBreakpoints(self, brks):
        """brks is a list of mappings containing the keys:
        filename, lineno, temporary, enabled, and cond.
        Non-blocking and immediate."""
        self._ds.setAllBreakpoints(brks)

    def addBreakpoint(self, filename, lineno, temporary=0,
                      cond=None, enabled=1):
        """Sets a breakpoint.  Non-blocking and immediate.
        """
        self._ds.addBreakpoint(filename, lineno, temporary, cond,
                               enabled)

    def enableBreakpoints(self, filename, lineno, enabled=1):
        """Sets the enabled flag for all breakpoints on a given line.
        Non-blocking and immediate.
        """
        self._ds.enableBreakpoints(filename, lineno, enabled)

    def clearBreakpoints(self, filename, lineno):
        """Clears all breakpoints on a line.  Non-blocking and immediate.
        """
        self._ds.clearBreakpoints(filename, lineno)

    ### Blocking methods.

    def pprintVarValue(self, name, frameno):
        """Pretty-prints the value of name.  Blocking."""
        return self._callMethod('pprintVarValue', 0, name, frameno)

    def getStatusSummary(self):
        """Returns a mapping containing the keys:
          exc_type, exc_value, stack, frame_stack_len, running.
        Also returns and empties the stdout and stderr buffers.
        stack is a list of mappings containing the keys:
          filename, lineno, funcname, modname.
        breaks contains the breakpoint statistics information
          for all current breakpoints.
        The most recent stack entry will be at the last
        of the list.  Blocking.
        """
        return self._callMethod('getStatusSummary', 0)

    def proceedAndRequestStatus(self, command, temp_breakpoint=0, args=()):
        """Executes one non-blocking command then returns
        getStatusSummary().  Blocking."""
        if temp_breakpoint:
            self.addBreakpoint(temp_breakpoint[0], temp_breakpoint[1], 1)
        if command:
            allowed = ('set_continue', 'set_step', 'set_step_over',
                       'set_step_out', 'set_pause', 'set_quit')
            if command not in allowed:
                raise DebugError('Illegal command: %s' % command)
            apply(getattr(self, command), args)
        ss = self.getStatusSummary()
        return ss

    def runFileAndRequestStatus(self, filename, params=(), autocont=0,
                                add_paths=(), breaks=()):
        """Calls setAllBreakpoints(), runFile(), and
        getStatusSummary().  Blocking."""
        self.setAllBreakpoints(breaks)
        self._callNoWait('runFile', 1, filename, params, autocont, add_paths)
        return self.getStatusSummary()

    def setupAndRequestStatus(self, autocont=0, breaks=()):
        """Calls setAllBreakpoints() and
        getStatusSummary().  Blocking."""
        self.setAllBreakpoints(breaks)
        if autocont:
            self.set_continue()
        return self.getStatusSummary()

    def getSafeDict(self, locals, frameno):
        """Returns the repr-fied mappings of locals and globals in a
        tuple.  Blocking."""
        return self._callMethod('getSafeDict', 0, locals, frameno)

    def evaluateWatches(self, exprs, frameno):
        """Evalutes the watches listed in exprs and returns the
        results. Input is a tuple of mappings with keys name and
        local; output is a mapping of name -> svalue.  Blocking.
        """
        return self._callMethod('evaluateWatches', 0, exprs, frameno)

    def getWatchSubobjects(self, expr, frameno):
        """Returns a tuple containing the names of subobjects
        available through the given watch expression.  Blocking."""
        return self._callMethod('getWatchSubobjects', 0, expr, frameno)


class NonBlockingDebuggerConnection (DebuggerConnection):
    """Modifies call semantics in such a way that even blocking
    calls don't block but instead return None.
    Note that for each call, a new NonBlockingDebuggerConnection object
    has to be created.  Use setCallback() to receive notification when
    blocking calls are finished.
    """

    callback = None

    def setCallback(self, callback):
        self.callback = callback

    def _callMethod(self, func_name, do_return, *args, **kw):
        sm = MethodCall(func_name, args, kw, do_return)
        if self.callback:
            sm.setCallback(self.callback)
        self._ds.queueServerMessage(sm)
        return None


# Set exclusive mode to kill all existing debug servers whenever
# a new connection is created.  This helps avoid resource drains.
exclusive_mode = 1


class DebuggerController:
    """Interfaces between DebuggerConnections and DebugServers."""

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
        """Returns a string which identifies a new DebugServer.
        """
        global exclusive_mode
        if exclusive_mode:
            # Kill existing servers.
            for id in self._debug_servers.keys():
                self.deleteServer(id)
        ds = DebugServer()
        id = self._newServerId()
        self._debug_servers[id] = ds
        return id

    def deleteServer(self, id):
        """Terminates the connection to the DebugServer."""
        try:
            ds = self._debug_servers[id]
            ds.set_quit()
            self._deleteServer(id)
        except: pass

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
            self.event.wait()

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
        self.waiting = 1

    def setWait(self, val):
        self.waiting = val

    def doExecute(self):
        return 1

    def execute(self, ob):
        try:
            result = apply(getattr(ob, self.func_name), self.args, self.kw)
        except (SystemExit, BdbQuit):
            raise
        except:
            if hasattr(self, 'callback'):
                self.callback.notifyException()
            else:
                if self.waiting:
                    self.exc = sys.exc_info()
                else:
                    # No one will see this message otherwise.
                    import traceback
                    traceback.print_exc()
        else:
            if hasattr(self, 'callback'):
                self.callback.notifyReturn(result)
            else:
                self.result = result

        if hasattr(self, 'event'):
            self.event.set()

    def doReturn(self):
        return self.do_return

    def setCallback(self, callback):
        self.callback = callback

    def getResult(self, timeout=None):
        self.wait()
        if hasattr(self, 'exc'):
            try:
                raise self.exc[0], self.exc[1], self.exc[2]
            finally:
                # Circ ref
                del self.exc
        if not hasattr(self, 'result'):
            raise DebugError, 'Timed out while waiting for debug server.'
        return self.result

_orig_syspath = sys.path[:]


class DebugServer (Bdb):

    # frame is set only while paused.
    frame = None

    # exc_info is set only while paused and an exception occurred.
    exc_info = None

    # ignore_stopline is the line number we should *not* stop on.
    ignore_stopline = -1

    # autocont is set by runFile() if the debugger should enter set_continue
    # mode right after starting.
    autocont = 0

    # _allow_env_changes governs whether sys.path, etc. can be modified.
    _allow_env_changes = 0

    # quitting is set to true when the user clicks the stop button.
    quitting = 0

    # stopframe can hold several values:
    #   None: Stop anywhere
    #   frame object: Stop in that frame
    #   (): Stop nowhere

    def __init__(self):
        Bdb.__init__(self)
        self.fncache = {}

        self.__queue = Queue.Queue(0)

        # self._lock is a reentrant lock that governs which thread
        # the debugger will stop in.
        self._lock = threading.RLock()

        self.repr = repr = Repr()
        repr.maxstring = 100
        repr.maxother = 100
        self.maxdict2 = 1000

        self._running = 0

        sys.boa_debugger = self

    def queueServerMessage(self, sm):
        self.__queue.put(sm)

    def cleanupServer(self):
        self.reset()
        self.frame = None
        self.ignore_stopline = -1
        self.autocont = 0
        self.exc_info = None
        self.fncache.clear()

    def servicerThread(self):
        """Bootstraps the debugger server loop."""
        while 1:
            try:
                self.eventLoop()
            except:
                # ??
                import traceback
                traceback.print_exc()
            self.quitting = 0

    def eventLoop(self):
        while not self.quitting:
            if not self.executeOneEvent():
                break  # event requested a return

    def executeOneEvent(self):
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

    # Bdb overrides.
    def canonic(self, filename):
        canonic = self.fncache.get(filename, None)
        if not canonic:
            if filename[:1] == '<' and filename[-1:] == '>':
                canonic = filename
            else:
                # Should we deal with URL's here?
                canonic = path.abspath(filename)
            self.fncache[filename] = canonic
        return canonic

    def stop_here(self, frame):
        # Redefine stopping.
        if frame is self.botframe:
            # Don't stop in the bottom frame.
            return 0
        sf = self.stopframe
        if sf is None:
            # Stop anywhere.
            return 1
        elif sf is ():
            # Stop nowhere.
            return 0
        # else stop in a specific frame.
        if (frame is sf and frame.f_lineno != self.ignore_stopline):
            # Stop in the current frame unless we're on
            # ignore_stopline.
            return 1
        # Stop at any frame that called stopframe.
        f = sf
        while f:
            if frame is f:
                return 1
            f = f.f_back
        return 0

    def break_anywhere(self, frame):
        # Allow a stop anywhere, anytime.
        # todo: Optimize by stopping only when in one of the
        # files being debugged?  Problem: callbacks don't get debugged.
        return 1

    def set_continue(self, full_speed=0):
        # Only stop at breakpoints, exceptions or when finished
        self.stopframe = ()
        self.returnframe = None
        self.quitting = 0

        if full_speed:
            # run without debugger overhead
            sys.settrace(None)

            import bcdb
            bcdb.waiting_debug_server = self

            try:
                raise 'gen_exc_info'
            except:
                frame = sys.exc_info()[2].tb_frame.f_back
                while frame and frame is not self.botframe:
                    # Clear all the f_trace attributes
                    # that were created while processing with a
                    # settrace callback enabled.
                    frame.f_trace = None
                    frame = frame.f_back

        if self._lock.acquire(0):
            # Allow a stop in any thread.
            self._lock.release()

    def runcall(self, func, *args, **kw):
        self.reset()
        sys.settrace(self.trace_dispatch)
        res = None
        try:
            try:
                res = apply(func, args, kw)
            except BdbQuit:
                pass
        finally:
            self.quitting = 1
            sys.settrace(None)
        return res

    def set_trace(self, call_depth=1):
        """Start debugging from the caller frame.

        Called by hard breakpoints.
        """
        self._running = 1
        # Note: we can't use Bdb.set_trace() because the
        # exception trickery below would have to change [2] to [3].
        try:
            raise 'gen_exc_info'
        except:
            frame = sys.exc_info()[2].tb_frame
            while call_depth:
                frame = frame.f_back
                call_depth = call_depth - 1
        break_frame = frame
        #self.reset()
        while frame:
            frame.f_trace = self.trace_dispatch
            #self.botframe = frame # XXX shouldn't botframe stay frame (bdb.run...)
            frame = frame.f_back
        #self.set_step()
        # Semantics have been redefined for this debugger's version of set_trace
        # The current bottom frame is kept (for a proper stack), 
        # and the debugger to the next line of the calling frame instead of the 
        # next instruction
        self.set_next(break_frame)
        
        sys.settrace(self.trace_dispatch)
        return self.trace_dispatch

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
        #orig_filename = filename
        filename = self.canonic(filename)
        import linecache # Import as late as possible
        line = linecache.getline(filename, lineno)
        if not line:
            # XXX maybe should call linecache.checkcache() here?
            return 'Invalid line: %s(%s)' % (filename, lineno)
        self.set_internal_breakpoint(filename, lineno, temporary, cond)
        bp = bdb.Breakpoint(filename, lineno, temporary, cond)
        # Save the original filename for passing back the stats.
        #bp.orig_filename = orig_filename
        return bp

    # An oversight in bdb?
    def do_clear(self, bpno):
        self.clear_bpbynumber(bpno)

    def clearTemporaryBreakpoints(self, filename, lineno):
        filename = self.canonic(filename)
        if not self.breaks.has_key(filename):
            return
        if lineno not in self.breaks[filename]:
            return
        # If all bp's are removed for that file,line
        # pair, then remove the breaks entry
        for bp in Breakpoint.bplist[filename, lineno][:]:
            if bp.temporary:
                bp.deleteMe()
        if not Breakpoint.bplist.has_key((filename, lineno)):
            self.breaks[filename].remove(lineno)
        if not self.breaks[filename]:
            del self.breaks[filename]

    # Bdb callbacks.

    def user_line(self, frame):
        # This method is called when we stop or break at a line
        if not self._lock.acquire(0):
            # Already working in another thread.
            return
        if self.autocont:
            self.autocont = 0
            self.set_continue()
            return
        self.stopframe = ()  # Don't stop.
        self.ignore_stopline = -1
        self.frame = frame
        self.exc_info = None
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
        self.clearTemporaryBreakpoints(filename, lineno)
        self.eventLoop()

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
        #self.exc_info = exc_info
        #self.eventLoop()
        pass

    ### Utility methods.
    def stopAnywhere(self):
        self.stopframe = None
        self.returnframe = None

    def runFile(self, filename, params, autocont, add_paths):
        d = {'__name__': '__main__',
             '__doc__': 'Debugging',
             '__builtins__': __builtins__,}

        fn = self.canonic(filename)
        if self._allow_env_changes:
            bn = path.basename(fn)
            dn = path.dirname(fn)
            sys.argv = [bn] + list(params)
            if not add_paths:
                add_paths = []
            sys.path = [dn] + list(add_paths) + list(_orig_syspath)
            chdir(dn)

        self.autocont = autocont

        self.run("execfile(fn, d)", {'fn':fn, 'd':d})

    def run(self, cmd, globals=None, locals=None):
        try:
            self._running = 1
            try:
                Bdb.run(self, cmd, globals, locals)
            except (BdbQuit, SystemExit):
                pass
            except:
                # Provide post-mortem analysis.
                import traceback
                traceback.print_exc()
                self.exc_info = sys.exc_info()
                self.frame = self.exc_info[2].tb_frame
                self.quitting = 0
                self.eventLoop()
        finally:
            self.quitting = 1
            self._running = 0
            self.cleanupServer()

    def runFunc(self, func, *args, **kw):
        try:
            self._running = 1
            try:
                return apply(self.runcall, (func,) + args, kw)
            except BdbQuit:
                pass
            except:
                # Provide post-mortem analysis.
                self.exc_info = sys.exc_info()
                self.frame = self.exc_info[2].tb_frame
                self.quitting = 0
                self.eventLoop()
        finally:
            self.quitting = 1
            self._running = 0
            self.cleanupServer()

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

    ### Breakpoint control.
    def setAllBreakpoints(self, brks):
        """brks is a list of mappings containing the keys:
        filename, lineno, temporary, enabled, and cond.
        Non-blocking."""
        self.clear_all_breaks()
        #print 'setting breakpoints:', brks
        if brks:
            for brk in brks:
                apply(self.addBreakpoint, (), brk)

    def addBreakpoint(self, filename, lineno, temporary=0,
                      cond=None, enabled=1):
        """Sets a breakpoint.  Non-blocking.
        """
        bp = self.set_break(filename, lineno, temporary, cond)
        if type(bp) == type(''):
            # Note that checking for string type is strange. Argh.
            raise DebugError(bp)
        elif bp is not None and not enabled:
            bp.disable()

    def enableBreakpoints(self, filename, lineno, enabled=1):
        """Sets the enabled flag for all breakpoints on a given line.
        Non-blocking.
        """
        bps = self.get_breaks(filename, lineno)
        if bps:
            for bp in bps:
                if enabled: bp.enable()
                else: bp.disable()

    def clearBreakpoints(self, filename, lineno):
        """Clears all breakpoints on a line.  Non-blocking.
        """
        msg = self.clear_break(filename, lineno)
        if msg is not None:
            raise DebugError(msg)

    def getStackInfo(self):
        try:
            if self.exc_info is not None:
                exc_type, exc_value, exc_tb = self.exc_info
                try:
                    exc_type = exc_type.__name__
                except AttributeError:
                    # Python 2.x -> ustr()?
                    exc_type = "%s" % str(exc_type)
                if exc_value is not None:
                    exc_value = str(exc_value)
                    
                stack, frame_stack_len = self.get_stack(
                    exc_tb.tb_frame, exc_tb)

                # Remove debugger's own stack
                stack = stack[frame_stack_len + 2:]
                frame_stack_len = len(stack)
            else:
                exc_type = None
                exc_value = None
                stack, frame_stack_len = self.get_stack(
                    self.frame, None)
            return exc_type, exc_value, stack, frame_stack_len
        finally:
            exc_tb = None
            stack = None

    def getQueryFrame(self, frameno):
        try:
            stack = self.getStackInfo()[2]
            if stack:
                if frameno > len(stack):
                    return stack[-1][0]
                else:
                    return stack[frameno][0]
            else:
                return None
        finally:
            stack = None

    def getExtendedFrameInfo(self):
        try:
            (exc_type, exc_value, stack,
             frame_stack_len) = self.getStackInfo()
            stack_summary = []
            for frame, lineno in stack:
                try:
                    modname = frame.f_globals['__name__']
                except:
                    modname = ''
                code = frame.f_code
                filename = self.canonic(code.co_filename)
                co_name = code.co_name
                stack_summary.append(
                    {'filename':filename, 'lineno':lineno,
                     'funcname':co_name, 'modname':modname})
            result = {'stack':stack_summary,
                      'frame_stack_len':frame_stack_len,
                      'running':self._running and 1 or 0}
            if exc_type:
                result['exc_type'] = exc_type
            if exc_value:
                result['exc_value'] = exc_value
            return result
        finally:
            frame = None
            stack = None

    def getBreakpointStats(self):
        rval = []
        for bps in bdb.Breakpoint.bplist.values():
            for bp in bps:
                #filename = getattr(bp, 'orig_filename', bp.file)
                filename = bp.file  # Already canonic
                rval.append({'filename':filename,
                             'lineno':bp.line,
                             'cond':bp.cond or '',
                             'temporary':bp.temporary and 1 or 0,
                             'enabled':bp.enabled and 1 or 0,
                             'hits':bp.hits or 0,
                             'ignore':bp.ignore and 1 or 0,
                             })
        return rval

    def getStatusSummary(self):
        rval = self.getExtendedFrameInfo()
        rval['breaks'] = self.getBreakpointStats()
        return rval

    def getSafeDict(self, locals, frameno):
        if locals:
            rname = 'locals'
        else:
            rname = 'globals'
        query_frame = self.getQueryFrame(frameno)
        if query_frame is None:
            return {'frameno':frameno, rname:{}}
        if locals:
            d = self.safeReprDict(query_frame.f_locals)
        else:
            d = self.safeReprDict(query_frame.f_globals)
        return {'frameno':frameno, rname:d}

    def evaluateWatches(self, exprs, frameno):
        query_frame = self.getQueryFrame(frameno)
        if query_frame is None:
            return {'frameno':frameno, 'watches':{}}
        localsDict = query_frame.f_locals
        globalsDict = query_frame.f_globals
        rval = {}
        for info in exprs:
            name = info['name']
            local = info['local']
            if local:
                primaryDict = localsDict
            else:
                primaryDict = globalsDict
            if primaryDict.has_key(name):
                value = primaryDict[name]
            else:
                try:
                    value = eval(name, globalsDict, localsDict)
                except Exception, message:
                    value = '??? (%s)' % message
            svalue = self.safeRepr(value)
            rval[name] = svalue
        return {'frameno':frameno, 'watches':rval}

    def getWatchSubobjects(self, expr, frameno):
        """Returns a tuple containing the names of subobjects
        available through the given watch expression."""
        query_frame = self.getQueryFrame(frameno)
        if query_frame is None:
            return []
        localsDict = query_frame.f_locals
        globalsDict = query_frame.f_globals
        try: inst_items = dir(eval(expr, globalsDict, localsDict))
        except: inst_items = []
        try: clss_items = dir(eval(expr, globalsDict, localsDict)
                              .__class__)
        except: clss_items = []
        return inst_items + clss_items

    def pprintVarValue(self, expr, frameno):
        query_frame = self.getQueryFrame(frameno)
        if query_frame is None:
            return ''
        else:
            try:
                v = eval(expr, query_frame.f_globals, query_frame.f_locals)
                return pprint.pformat(v)
            except:
                t, v = sys.exc_info()[:2]
                return str(v)

    def safeRepr(self, s):
        return self.repr.repr(s)

    def safeReprDict(self, dict):
        rval = {}
        l = dict.items()
        if len(l) >= self.maxdict2:
            l = l[:self.maxdict2]
        for key, value in l:
            rval[str(key)] = self.safeRepr(value)
        return rval

    def reset(self):
        Bdb.reset(self)
        #self.frame = None
    
    def dispatch_return(self, frame, arg):
        Bdb.dispatch_return(self, frame, arg)
        # XXX this can be used as a hook to detect when a debugging session is
        # XXX about to stop. frame.f_back will be None
        # XXX For the main thread this means the end of the program, but
        # XXX for threads I want to transfer control (tracing) back to the 
        # XXX main thread

##waiting_debug_server = None
##
##def set_trace():
##    global waiting_debug_server
##    ds = waiting_debug_server
##    if ds:
##        waiting_debug_server = None
##        if hasattr(sys, 'boa_debugger'): 
##            del sys.boa_debugger
##
##        ds.set_trace(call_depth=2)

def descrframe(frame):
    if frame: return ('<frame:%s(%s)%s [%s]>'%(path.basename(frame.f_code.co_filename), 
          frame.f_lineno, frame.f_code.co_name, id(frame)) )
    else: return 'None'

# for debugging debugging
# to track who sets the sys trace function
_settrace = sys.settrace
def settrace_prx(func):
    print 'TRACE: %s set by %s'%(func, threading.currentThread())
    _settrace(func)
#sys.settrace = settrace_prx
