#-----------------------------------------------------------------------------
# Name:        wxNamespace.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2001
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2004
# Licence:     GPL
#-----------------------------------------------------------------------------
import Preferences as _Prefs

import wx

if _Prefs.ccImportWxPyHtml:
    import wx.html
if _Prefs.ccImportWxPyCalendar:
    import wx.calendar
if _Prefs.ccImportWxPyGrid:
    import wx.grid
if _Prefs.ccImportWxPyStc:
    import wx.stc
if _Prefs.ccImportWxPyGizmos:
    import wx.gizmos
if _Prefs.ccImportWxPyWizard:
    import wx.wizard

import types as _types


def getWxClass(name):
    return getWxObjPath(name)

def getNamesOfType(aType):
    res = []
    for k, v in globals().items():
        if type(v) == aType:
            if _Prefs.ccFilterWxPtrNames and k[-3:] == 'Ptr':
                continue
            res.append(k)
    return res

def getWxObjPath(objPath):
    pathSegs = objPath.split('.')
    if pathSegs[0] != 'wx':
        return None
    obj = wx
    for name in pathSegs[1:]:
        if hasattr(obj, name):
            obj = getattr(obj, name)
        else:
            return None
    return obj

def getWxNamespaceForObjPath(objPath):
    obj = getWxObjPath(objPath)
    if obj:
        return dir(obj)
    else:
        return []

