import sys

# don't trace this module
__traceable__ = 0

def StartDebugServer():
    sys.path.append('c:/Path/To/Boa')

    from Debugger.RemoteServer import start
    start('', '') # username, password

    return 'Debug Server started, attach to it from the IDE.'

def HookDebugServer():
    if hasattr(sys, 'debugger_control'):
        sys.debugger_control.set_traceable()
        sys.debugger_control.set_continue()
    else:
        raise Exception('Not running in the debugger.')

    return 'Debug Server hooked, breakpoints now active.'
