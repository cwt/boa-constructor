
def test1():
    print 'I'
    print 'am'
    print 'here.'

def test():
    print 'Hello'
    print 'World!'
    print 'Message:'
    test1()
    print 'Bye.'
    print 'yeah.'
    
if __name__ == '__main__':
  test1()
  if 0:    
    import IsolatedDebugger
    dc = IsolatedDebugger.DebuggerController()
    id = dc.createServer()
    conn = IsolatedDebugger.DebuggerConnection(dc, id)
    conn.run('test()', globals(), locals())
    for n in range(3):
        print conn.getExtendedFrameInfo()
        conn.set_step_over()
    for n in range(6):
        print conn.getExtendedFrameInfo()
        conn.set_step()
    print conn.getExtendedFrameInfo()
    conn.set_continue()
    print conn.getExtendedFrameInfo()

