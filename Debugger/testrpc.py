
import os, sys
sys.path[0:0] = [os.pardir]

from ChildProcessClient import spawnChild
from wxPython.wx import wxProcess
from time import sleep
import threading

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

def streamPollThread():
    while 1:
        pollStreams()
        sleep(0.15)

t = threading.Thread(target=streamPollThread)
t.setDaemon(1)

print 'spawning...'
s = spawnChild(Monitor(), process)

t.start()

print 'starting... (via %s)' % s
status = s.runFileAndRequestStatus('test.py', (), 0, (),
                                   ({'filename':'test.py',
                                     'lineno':15,
                                     'cond':'',
                                     'enabled':1,
                                     'temporary':0},
                                    ))
print status
print 'running...'
status = s.proceedAndRequestStatus('set_continue')
sleep(0.5)
print status

# Should stop in the middle of the process.
