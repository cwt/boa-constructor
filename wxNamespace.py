from wxPython.wx import *
from wxPython.utils import *
from wxPython.stc import *
from wxPython.html import *
from wxPython.htmlhelp import *
from wxPython.calendar import *
from wxPython.grid import *
from wxPython.ogl import *

def getWxNameSpace():
    return globals().keys()

def getWxClass(name):
    g = globals()
    import types
    if g.has_key(name) and type(g[name]) == types.ClassType:
        return g[name]
