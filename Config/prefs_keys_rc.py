## rc-version: 10 ##
# RCS-ID:      $Id$

import wx

# Keycodes <- press F1 ;)

keyDefs = {
#--Source View------------------------------------------------------------------
  'Refresh'     : (wx.ACCEL_CTRL, ord('R'), 'Ctrl-R'),
  'Find'        : (wx.ACCEL_CTRL, ord('F'), 'Ctrl-F'),
  'FindAgain'   : (wx.ACCEL_NORMAL, wx.WXK_F3, 'F3'),
  'FindAgainPrev' : (wx.ACCEL_SHIFT, wx.WXK_F3, 'Shift-F3'),
  'ToggleBrk'   : (wx.ACCEL_NORMAL, wx.WXK_F5, 'F5'),
  'Indent'      : (wx.ACCEL_CTRL, ord('I'), 'Ctrl-I'),
  'Dedent'      : (wx.ACCEL_CTRL, ord('U'), 'Ctrl-U'),
  'Comment'     : (wx.ACCEL_ALT, ord('3'), 'Alt-3'),
  'Uncomment'   : (wx.ACCEL_ALT, ord('4'), 'Alt-4'),
  'DashLine'    : (wx.ACCEL_CTRL, ord('B'), 'Ctrl-B'),
  'MarkPlace'   : (wx.ACCEL_CTRL, ord('M'), 'Ctrl-M'),
  'CodeComplete': (wx.ACCEL_CTRL, wx.WXK_SPACE, 'Ctrl-Space'),
  'CallTips'    : (wx.ACCEL_SHIFT|wx.ACCEL_CTRL, wx.WXK_SPACE, 'Ctrl-Shift-Space'),
  'CodeXform'   : (wx.ACCEL_ALT, ord('C'), 'Alt-C'),
  'BrowseTo'    : (wx.ACCEL_CTRL, wx.WXK_RETURN, 'Ctrl-Return'),
  'BrowseFwd'   : (wx.ACCEL_SHIFT|wx.ACCEL_CTRL, ord('K'), 'Ctrl-K'),
  'BrowseBack'  : (wx.ACCEL_SHIFT|wx.ACCEL_CTRL, ord('J'), 'Ctrl-J'),
#-Modules-----------------------------------------------------------------------
  'RunApp'      : (wx.ACCEL_NORMAL, wx.WXK_F9, 'F9'),
  'RunMod'      : (wx.ACCEL_NORMAL, wx.WXK_F10, 'F10'),
  'Close'       : (wx.ACCEL_CTRL, ord('W'), 'Ctrl-W'),
  'Save'        : (wx.ACCEL_CTRL, ord('S'), 'Ctrl-S'),
  'SaveAs'      : (wx.ACCEL_ALT, ord('S'), 'Alt-S'),
  'CheckSource' : (wx.ACCEL_NORMAL, wx.WXK_F2, 'F2'),
  'Debug'       : (wx.ACCEL_NORMAL, wx.WXK_F4, 'F4'),
  'DebugOut'    : (wx.ACCEL_NORMAL, wx.WXK_F6, 'F6'),
  'DebugStep'   : (wx.ACCEL_NORMAL, wx.WXK_F7, 'F7'),
  'DebugOver'   : (wx.ACCEL_NORMAL, wx.WXK_F8, 'F8'),
  'DebugPause'  : (wx.ACCEL_SHIFT, wx.WXK_F4, 'Shift-F4'),
  'DebugStop'   : (wx.ACCEL_CTRL|wx.ACCEL_SHIFT, wx.WXK_F4, 'Ctrl-Shift-F4'),
  'SwitchToApp' : (wx.ACCEL_ALT, ord('A'), 'Alt-A'),
#--General----------------------------------------------------------------------
  'ContextHelp' : (wx.ACCEL_NORMAL, wx.WXK_F1, 'F1'),
  'Open'        : (wx.ACCEL_CTRL, ord('O'), 'Ctrl-O'),
  'Insert'      : (wx.ACCEL_NORMAL, wx.WXK_INSERT, 'Ins'),
  'Delete'      : (wx.ACCEL_NORMAL, wx.WXK_DELETE, 'Del'),
  'Escape'      : (wx.ACCEL_NORMAL, wx.WXK_ESCAPE, 'Esc'),
  'NextPage'    : (wx.ACCEL_CTRL, ord('K'), 'Ctrl-K'),
  'PrevPage'    : (wx.ACCEL_CTRL, ord('J'), 'Ctrl-J'),
  'Inspector'   : (wx.ACCEL_NORMAL, wx.WXK_F11, 'F11'),
  'Designer'    : (wx.ACCEL_NORMAL, wx.WXK_F12, 'F12'),
  'Editor'      : (wx.ACCEL_NORMAL, wx.WXK_F12, 'F12'),
  'GotoLine'    : (wx.ACCEL_CTRL, ord('G'), 'Ctrl-G'),
  'HelpFind'    : (wx.ACCEL_CTRL, ord('H'), 'Ctrl-H'),
  'GotoExplorer': (wx.ACCEL_CTRL, ord('E'), 'Ctrl-E'),
  'GotoShell'   : (wx.ACCEL_CTRL, ord('P'), 'Ctrl-P'),
  'CloseView'   : (wx.ACCEL_CTRL, ord('Q'), 'Ctrl-Q'),
#--Clipboard--------------------------------------------------------------------
  'Cut'         : (wx.ACCEL_SHIFT, wx.WXK_DELETE, 'Shift-Del'),
  'Copy'        : (wx.ACCEL_CTRL, wx.WXK_INSERT, 'Ctrl-Ins'),
  'Paste'       : (wx.ACCEL_SHIFT, wx.WXK_INSERT, 'Shift-Ins'),
#--Designer---------------------------------------------------------------------
  'MoveLeft'    : (wx.ACCEL_CTRL, wx.WXK_LEFT, 'Ctrl-Left'),
  'MoveRight'   : (wx.ACCEL_CTRL, wx.WXK_RIGHT, 'Ctrl-Right'),
  'MoveUp'      : (wx.ACCEL_CTRL, wx.WXK_UP, 'Ctrl-Up'),
  'MoveDown'    : (wx.ACCEL_CTRL, wx.WXK_DOWN, 'Ctrl-Down'),
  'WidthDec'    : (wx.ACCEL_SHIFT, wx.WXK_LEFT, 'Shift-Left'),
  'WidthInc'    : (wx.ACCEL_SHIFT, wx.WXK_RIGHT, 'Shift-Right'),
  'HeightInc'   : (wx.ACCEL_SHIFT, wx.WXK_DOWN, 'Shift-Down'),
  'HeightDec'   : (wx.ACCEL_SHIFT, wx.WXK_UP, 'Shift-Up'),
  'SelectLeft'  : (wx.ACCEL_NORMAL, wx.WXK_LEFT, 'Left'),
  'SelectRight' : (wx.ACCEL_NORMAL, wx.WXK_RIGHT, 'Right'),
  'SelectDown'  : (wx.ACCEL_NORMAL, wx.WXK_DOWN, 'Down'),
  'SelectUp'    : (wx.ACCEL_NORMAL, wx.WXK_UP, 'Up'),
#--Shell------------------------------------------------------------------------
  'HistoryUp'   : (wx.ACCEL_CTRL, wx.WXK_UP, 'Ctrl-Up'),
  'HistoryDown' : (wx.ACCEL_CTRL, wx.WXK_DOWN, 'Ctrl-Down'),
}

##  'NextView'    : (wx.ACCEL_SHIFT|wx.ACCEL_CTRL, ord('T'), 'Ctrl-Shift-T'),
##  'PrevView'    : (wx.ACCEL_SHIFT|wx.ACCEL_CTRL, ord('R'), 'Ctrl-Shift-R'),

##if wx.Platform == '__WXGTK__':
##    keyDefs.update({'SaveAs'      : (wx.ACCEL_CTRL, ord('1'), 'Ctrl-1'),
##                    'Comment'     : (wx.ACCEL_CTRL, ord('3'), 'Ctrl-3'),
##                    'Uncomment'   : (wx.ACCEL_CTRL, ord('4'), 'Ctrl-4'),
##                    'SwitchToApp' : (wx.ACCEL_CTRL, ord('5'), 'Ctrl-5'),
##                    'CodeXform'   : (wx.ACCEL_CTRL, ord('E'), 'Ctrl-E'),
##                  })
##else:
##    keyDefs.update({'SaveAs'      : (wx.ACCEL_ALT, ord('S'), 'Alt-S'),
##                    'Comment'     : (wx.ACCEL_ALT, ord('3'), 'Alt-3'),
##                    'Uncomment'   : (wx.ACCEL_ALT, ord('4'), 'Alt-4'),
##                    'SwitchToApp' : (wx.ACCEL_ALT, ord('A'), 'Alt-A'),
##                    'CodeXform'   : (wx.ACCEL_ALT, ord('C'), 'Alt-C'),
##                  })
    
# Not used yet, defined for completeness
_stcDefs = {'Cut'        : 'Shift-Del',
           'Copy'       : 'Ctrl-Ins',
           'Paste'      : 'Shift-Ins',
           'SelectAll'  : 'Ctrl-A',
           'Undo'       : 'Ctrl-Z',
           'Redo'       : 'Ctrl-Y',
           'DeleteLine' : 'Ctrl-L'}
