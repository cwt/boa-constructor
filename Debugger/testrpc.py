
import os, sys
sys.path[0:0] = [os.pardir]

from ChildProcessClient import spawnChild
from wxPython.wx import wxProcess

class Monitor: pass


process = wxProcess()
process.Redirect()

def pollStreams():
    stream = process.GetInputStream()
    if not stream.eof():
        print stream.read()
    stream = process.GetErrorStream()
    if not stream.eof():
        print stream.read()

print 'spawning...'
s = spawnChild(Monitor(), process)

print 'starting...'
v = s.runFileAndRequestStatus('test.py', (), 0, (),
                                ({'filename':'test.py',
                                  'lineno':15,
                                  'cond':'',
                                  'enabled':1,
                                  'temporary':0},
                                 ))
pollStreams()
print v
print 'running...'
v = s.proceedAndRequestStatus('set_continue')
pollStreams()
print v

# Should stop in the middle of the process.
