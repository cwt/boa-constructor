#-----------------------------------------------------------------------------
# Name:        wxNamespace.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2001
# RCS-ID:      $Id$
# Copyright:   (c) 2002
# Licence:     GPL
#-----------------------------------------------------------------------------
import Preferences; _Prefs = Preferences; del Preferences

from wxPython.wx import *

if _Prefs.ccImportWxPyUtils:
    from wxPython.utils import *
if _Prefs.ccImportWxPyHtml:
    from wxPython.html import *
if _Prefs.ccImportWxPyHtmlHelp:
    from wxPython.htmlhelp import *
if _Prefs.ccImportWxPyHelp:
    from wxPython.help import *
if _Prefs.ccImportWxPyCalendar:
    from wxPython.calendar import *
if _Prefs.ccImportWxPyGrid:
    from wxPython.grid import *
if _Prefs.ccImportWxPyOgl:
    from wxPython.ogl import *
if _Prefs.ccImportWxPyStc:
    from wxPython.stc import *
if _Prefs.ccImportWxPyGizmos:
    from wxPython.gizmos import *
if _Prefs.ccImportWxPyWizard:
    from wxPython.wizard import *

import types; _types = types; del types

# remove wxPython *c modules from namespace
_g = globals()
for _k, _v in _g.items():
    if type(_v) is _types.ModuleType and _k[-1] == 'c':
        del _g[_k]
del _g, _k, _v


filterTypes = []
if _Prefs.ccFilterWxConstants:
    filterTypes.append(_types.IntType)
if _Prefs.ccFilterWxFunctions:
    filterTypes.extend( [_types.FunctionType, _types.BuiltinFunctionType])
if _Prefs.ccFilterWxClasses:
    filterTypes.append(_types.ClassType)
if _Prefs.ccFilterWxInstances:
    filterTypes.append(_types.InstanceType)

def _getWxNameSpace():
    if _Prefs.ccFilterWxAll:
        return []
    g = globals()
    ns = filterOnPrefs(g, g)

    for name in ('filterTypes', 'getWxNameSpace', 'getWxClass',
                 'getNamesOfType', '_getWxNameSpace', '_nameSpace'):
        try: ns.remove(name)
        except ValueError: pass
    return ns

def filterOnPrefs(g, w):
    ns = g.keys()
    if _Prefs.ccFilterWxPtrNames:
        return filter(lambda n, g=g, w=w: n[-3:] != 'Ptr' and \
              (type(g[n]) not in filterTypes or not w.has_key(n)), ns)
    else:
        return filter(lambda n, g=g, w=w: \
              type(g[n]) not in filterTypes or not w.has_key(n), ns)

def getWxClass(name):
    g = globals()
    if g.has_key(name) and type(g[name]) == _types.ClassType:
        return g[name]

def getNamesOfType(aType):
    res = []
    for k, v in globals().items():
        if type(v) == aType:
            if _Prefs.ccFilterWxPtrNames and k[-3:] == 'Ptr':
                continue
            res.append(k)
    return res

def getWxNameSpace():
    return _nameSpace

_nameSpace = _getWxNameSpace()
