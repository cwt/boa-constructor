""" Plugin to toggle the Error/Output window with a keybinding """

import wx

import Preferences, Utils, Plugins

# only install if ErrOut is docked in the Editor
if Preferences.eoErrOutDockWindow != 'editor':
    raise Plugins.SkipPluginSilently

Preferences.keyDefs['ToggleErrOut'] = (wx.ACCEL_ALT, ord('O'), 'Alt-O')

def toggleErrOutWindow(editor): 
    editor.tabsSplitter._OnSplitterwindowSplitterDoubleclicked(None)

Plugins.registerTool(
      'Toggle Error/Output window', toggleErrOutWindow, key='ToggleErrOut')
