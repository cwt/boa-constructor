from wxPython.wx import *
from wxPython.stc import *
from wxPython.html import *
import types

def getWxNameSpace():
    return globals().keys()

def getWxClass(name):
    g = globals()
    if g.has_key(name) and type(g[name]) == types.ClassType:
        return g[name]
