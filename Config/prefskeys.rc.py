## rc-version: 7 ##
# RCS-ID:      $Id$

from wxPython.wx import *

# Keycodes <- press F1 ;)

keyDefs = {
#--Source View------------------------------------------------------------------
  'Refresh'     : (wxACCEL_CTRL, ord('R'), 'Ctrl-R'),
  'Find'        : (wxACCEL_CTRL, ord('F'), 'Ctrl-F'),
  'FindAgain'   : (wxACCEL_NORMAL, WXK_F3, 'F3'),
  'ToggleBrk'   : (wxACCEL_NORMAL, WXK_F5, 'F5'),
  'Indent'      : (wxACCEL_CTRL, ord('I'), 'Ctrl-I'),
  'Dedent'      : (wxACCEL_CTRL, ord('U'), 'Ctrl-U'),
  'DashLine'    : (wxACCEL_CTRL, ord('B'), 'Ctrl-B'),
  'MarkPlace'   : (wxACCEL_CTRL, ord('M'), 'Ctrl-M'),
  'CodeComplete': (wxACCEL_CTRL, WXK_SPACE, 'Ctrl-Space'),
  'CallTips'    : (wxACCEL_SHIFT|wxACCEL_CTRL, WXK_SPACE, 'Ctrl-Shift-Space'),
  'BrowseTo'    : (wxACCEL_CTRL, WXK_RETURN, 'Ctrl-Return'),
  'BrowseFwd'   : (wxACCEL_SHIFT|wxACCEL_CTRL, ord('K'), 'Ctrl-K'),
  'BrowseBack'  : (wxACCEL_SHIFT|wxACCEL_CTRL, ord('J'), 'Ctrl-J'),
#-Modules-----------------------------------------------------------------------
  'RunApp'      : (wxACCEL_NORMAL, WXK_F9, 'F9'),
  'RunMod'      : (wxACCEL_NORMAL, WXK_F10, 'F10'),
  'Close'       : (wxACCEL_CTRL, ord('Q'), 'Ctrl-Q'),
  'Save'        : (wxACCEL_CTRL, ord('S'), 'Ctrl-S'),
  'CheckSource' : (wxACCEL_NORMAL, WXK_F2, 'F2'),
  'Debug'       : (wxACCEL_NORMAL, WXK_F4, 'F4'),
  'DebugOut'    : (wxACCEL_NORMAL, WXK_F6, 'F6'),
  'DebugStep'   : (wxACCEL_NORMAL, WXK_F7, 'F7'),
  'DebugOver'   : (wxACCEL_NORMAL, WXK_F8, 'F8'),
#--General----------------------------------------------------------------------
  'ContextHelp' : (wxACCEL_NORMAL, WXK_F1, 'F1'),
  'Open'        : (wxACCEL_CTRL, ord('O'), 'Ctrl-O'),
  'Insert'      : (wxACCEL_NORMAL, WXK_INSERT, 'Ins'),
  'Delete'      : (wxACCEL_NORMAL, WXK_DELETE, 'Del'),
  'Escape'      : (wxACCEL_NORMAL, WXK_ESCAPE, 'Esc'),
  'NextPage'    : (wxACCEL_CTRL, ord('K'), 'Ctrl-K'),
  'PrevPage'    : (wxACCEL_CTRL, ord('J'), 'Ctrl-J'),
  'Inspector'   : (wxACCEL_NORMAL, WXK_F11, 'F11'),
  'Designer'    : (wxACCEL_NORMAL, WXK_F12, 'F12'),
  'Editor'      : (wxACCEL_NORMAL, WXK_F12, 'F12'),
  'GotoLine'    : (wxACCEL_CTRL, ord('G'), 'Ctrl-G'),
  'HelpFind'    : (wxACCEL_CTRL, ord('H'), 'Ctrl-H'),
  'GotoExplorer': (wxACCEL_CTRL, ord('E'), 'Ctrl-E'),
  'GotoShell'   : (wxACCEL_CTRL, ord('P'), 'Ctrl-P'),
  'CloseView'   : (wxACCEL_CTRL, ord('W'), 'Ctrl-W'),
#--Clipboard--------------------------------------------------------------------
  'Cut'         : (wxACCEL_SHIFT, WXK_DELETE, 'Shift-Del'),
  'Copy'        : (wxACCEL_CTRL, WXK_INSERT, 'Ctrl-Ins'),
  'Paste'       : (wxACCEL_SHIFT, WXK_INSERT, 'Shift-Ins'),
  'CopyPlus'    : (wxACCEL_CTRL|wxACCEL_SHIFT, ord('C') , 'Ctrl-Shift-C'),
  'PastePlus'   : (wxACCEL_CTRL|wxACCEL_SHIFT, ord('V'), 'Ctrl-Shift-V'),
#--Designer---------------------------------------------------------------------
  'MoveLeft'    : (wxACCEL_CTRL, WXK_LEFT, 'Ctrl-Left'),
  'MoveRight'   : (wxACCEL_CTRL, WXK_RIGHT, 'Ctrl-Right'),
  'MoveUp'      : (wxACCEL_CTRL, WXK_UP, 'Ctrl-Up'),
  'MoveDown'    : (wxACCEL_CTRL, WXK_DOWN, 'Ctrl-Down'),
  'WidthDec'    : (wxACCEL_SHIFT, WXK_LEFT, 'Shift-Left'),
  'WidthInc'    : (wxACCEL_SHIFT, WXK_RIGHT, 'Shift-Right'),
  'HeightInc'   : (wxACCEL_SHIFT, WXK_DOWN, 'Shift-Down'),
  'HeightDec'   : (wxACCEL_SHIFT, WXK_UP, 'Shift-Up'),
  'SelectLeft'  : (wxACCEL_NORMAL, WXK_LEFT, 'Left'),
  'SelectRight' : (wxACCEL_NORMAL, WXK_RIGHT, 'Right'),
  'SelectDown'  : (wxACCEL_NORMAL, WXK_DOWN, 'Down'),
  'SelectUp'    : (wxACCEL_NORMAL, WXK_UP, 'Up'),
#--Shell------------------------------------------------------------------------
  'HistoryUp'   : (wxACCEL_CTRL, WXK_UP, 'Ctrl-Up'),
  'HistoryDown' : (wxACCEL_CTRL, WXK_DOWN, 'Ctrl-Down'),
}

##  'NextView'    : (wxACCEL_SHIFT|wxACCEL_CTRL, ord('T'), 'Ctrl-Shift-T'),
##  'PrevView'    : (wxACCEL_SHIFT|wxACCEL_CTRL, ord('R'), 'Ctrl-Shift-R'),

if wxPlatform == '__WXGTK__':
    keyDefs.update({'SaveAs'      : (wxACCEL_CTRL, ord('1'), 'Ctrl-1'),
                    'Comment'     : (wxACCEL_CTRL, ord('3'), 'Ctrl-3'),
                    'Uncomment'   : (wxACCEL_CTRL, ord('4'), 'Ctrl-4'),
                    'SwitchToApp' : (wxACCEL_CTRL, ord('5'), 'Ctrl-5'),
                    'CodeXform'   : (wxACCEL_CTRL, ord('E'), 'Ctrl-E'),
                  })
else:
    keyDefs.update({'SaveAs'      : (wxACCEL_ALT, ord('S'), 'Alt-S'),
                    'Comment'     : (wxACCEL_ALT, ord('3'), 'Alt-3'),
                    'Uncomment'   : (wxACCEL_ALT, ord('4'), 'Alt-4'),
                    'SwitchToApp' : (wxACCEL_ALT, ord('A'), 'Alt-A'),
                    'CodeXform'   : (wxACCEL_ALT, ord('C'), 'Alt-C'),
                  })
    
# Not used yet, defined for completeness
stcDefs = {'Cut'        : 'Shift-Del',
           'Copy'       : 'Ctrl-Ins',
           'Paste'      : 'Shift-Ins',
           'SelectAll'  : 'Ctrl-A',
           'Undo'       : 'Ctrl-Z',
           'Redo'       : 'Ctrl-Y',
           'DeleteLine' : 'Ctrl-L'}
