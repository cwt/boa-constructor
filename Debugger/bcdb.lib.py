import thread, threading, time, random

class BoaDebuggerError(Exception): pass

waiting_debug_server = None

trace_lock = threading.Lock()
def set_trace(block=0, except_on_fail=0):
    """Call this to set a 'hard' breakpoint.

    Usage:
    import bcdb; bcdb.set_trace()
    
    Defaults to a non blocking mode. If the debugger is not available
    it simply returns.

    Note that this starts debugging only if the code was run with the 
    Debug/Continue full speed option."""
    
    got_lock = trace_lock.acquire(block)
    if not block and not got_lock: 
        if except_on_fail: 
            raise BoaDebuggerError, 'Failed to aquire trace lock'
        return
    try:
        global waiting_debug_server
        ds = waiting_debug_server
        if ds:
            waiting_debug_server = None
            return ds.set_trace(2)
        elif block:
            while not waiting_debug_server:
                time.sleep(0.015)
        else:
            if except_on_fail: 
                raise BoaDebuggerError, 'No debug server available'
            return
    finally:
        trace_lock.release()

class BoaDebugger:
    def hard_break(self, block=0, except_on_fail=0):
        """ Breaks into a running module started in the debugger, but 
        continued at full speed (i.e. not being traced)"""
        set_trace(block, except_on_fail)
    
    def do_continue(self):
        """ Resumes execution in the debugger from this point on """
        pass
    
    def wait_for_debugger(self):
        """ Block until the debugger has finished debugging
        
        This is meant for debugging threads where the debugger could still be
        stepping thru a thread but the main thead would have finished """
        pass

__fin = 0
def _test_trace():
    try:
        set_trace()
        print 'The debugger should stop at this line'
    finally:
        __fin = 1
    
def _test():
    if 1:
        _test_trace()
    else:
        global __fin; __fin = 0
        thread.start_new_thread(_test_trace, ())
        
        # hack to keep the main thread alive while debugging the thread
        while not __fin:
            time.sleep(0.1)
            
if __name__ == '__main__':
    _test()
