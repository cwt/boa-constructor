#-----------------------------------------------------------------------------
# Name:        PrefsKeys.py                                                   
# Purpose:     Keyboard definitions                                           
#                                                                             
# Author:      Riaan Booysen                                                  
#                                                                             
# Created:     2000/05/12                                                     
# RCS-ID:      $Id$                                             
# Copyright:   (c) 1999, 2000 Riaan Booysen                                   
# Licence:     GPL                                                            
#-----------------------------------------------------------------------------

from wxPython.wx import *

wxACCEL_NORMAL = 0

keyDefs = {
  'ContextHelp' : (wxACCEL_NORMAL, WXK_F1, 'F1'),
  'CheckSource' : (wxACCEL_NORMAL, WXK_F2, 'F2'),
  'FindAgain'   : (wxACCEL_NORMAL, WXK_F3, 'F3'),
  'Debug'       : (wxACCEL_NORMAL, WXK_F4, 'F4'),
  'ToggleBrk'   : (wxACCEL_NORMAL, WXK_F5, 'F5'),
  'DebugOut'    : (wxACCEL_NORMAL, WXK_F6, 'F6'),
  'DebugStep'   : (wxACCEL_NORMAL, WXK_F7, 'F7'),
  'DebugOver'   : (wxACCEL_NORMAL, WXK_F8, 'F8'),
  'RunApp'      : (wxACCEL_NORMAL, WXK_F9, 'F9'),
  'RunMod'      : (wxACCEL_NORMAL, WXK_F10, 'F10'),
  'Inspector'   : (wxACCEL_NORMAL, WXK_F11, 'F11'),
  'Designer'    : (wxACCEL_NORMAL, WXK_F12, 'F12'),
  'Editor'      : (wxACCEL_NORMAL, WXK_F12, 'F12'),
  'Find'        : (wxACCEL_CTRL, ord('F'), 'Ctrl-F'),
  'Open'        : (wxACCEL_CTRL, ord('O'), 'Ctrl-O'),
  'Close'       : (wxACCEL_CTRL, ord('Q'), 'Ctrl-Q'),
  'Save'        : (wxACCEL_CTRL, ord('S'), 'Ctrl-S'),
  'Indent'      : (wxACCEL_CTRL, ord('I'), 'Ctrl-I'), # ctrl ] doesn't work
  'Dedent'      : (wxACCEL_CTRL, ord('U'), 'Ctrl-U'), # ctrl [ doesn't work
  'DashLine'    : (wxACCEL_CTRL, ord('B'), 'Ctrl-B'),
  'Refresh'     : (wxACCEL_CTRL, ord('R'), 'Ctrl-R'),
  'Insert'      : (wxACCEL_NORMAL, WXK_INSERT, 'Ins'),
  'Delete'      : (wxACCEL_NORMAL, WXK_DELETE, 'Del'),
  'Escape'      : (wxACCEL_NORMAL, WXK_ESCAPE, 'Esc'),
  'NextPage'    : (wxACCEL_CTRL, ord('K'), 'Ctrl-K'),
  'PrevPage'    : (wxACCEL_CTRL, ord('J'), 'Ctrl-J'),
  'Cut'         : (wxACCEL_SHIFT, WXK_DELETE, 'Shft-Del'),
  'Copy'        : (wxACCEL_CTRL, WXK_INSERT, 'Ctrl-Ins'),
  'Paste'       : (wxACCEL_SHIFT, WXK_INSERT, 'Shft-Ins'), 
  'MoveLeft'    : (wxACCEL_CTRL, WXK_LEFT, 'Ctrl-Left'),
  'MoveRight'   : (wxACCEL_CTRL, WXK_RIGHT, 'Ctrl-Right'),
  'MoveUp'      : (wxACCEL_CTRL, WXK_UP, 'Ctrl-Up'),
  'MoveDown'    : (wxACCEL_CTRL, WXK_DOWN, 'Ctrl-Down'),
  'WidthDec'    : (wxACCEL_SHIFT, WXK_LEFT, 'Shft-Left'),
  'WidthInc'    : (wxACCEL_SHIFT, WXK_RIGHT, 'Shft-Right'),
  'HeightInc'   : (wxACCEL_SHIFT, WXK_DOWN, 'Shft-Down'),
  'HeightDec'   : (wxACCEL_SHIFT, WXK_UP, 'Shft-Up'),
  'MarkPlace'   : (wxACCEL_CTRL, ord('M'), 'Ctrl-M'), 
}

if wxPlatform == '__WXMSW__':
    keyDefs.update({'SaveAs'      : (wxACCEL_ALT, ord('S'), 'Alt-S'),
                    'Comment'     : (wxACCEL_ALT, ord('3'), 'Alt-3'),
                    'Uncomment'   : (wxACCEL_ALT, ord('4'), 'Alt-4'),
                    'SwitchToApp' : (wxACCEL_ALT, ord('A'), 'Alt-A'),
                    'CodeComplete': (wxACCEL_ALT, ord('C'), 'Alt-C'),
                  })
elif wxPlatform == '__WXGTK__':
    keyDefs.update({'SaveAs'      : (wxACCEL_CTRL, ord('1'), 'Ctrl-1'),
                    'Comment'     : (wxACCEL_CTRL, ord('3'), 'Ctrl-3'),
                    'Uncomment'   : (wxACCEL_CTRL, ord('4'), 'Ctrl-4'),
                    'SwitchToApp' : (wxACCEL_CTRL, ord('5'), 'Ctrl-5'),
                    'CodeComplete': (wxACCEL_CTRL, ord('E'), 'Ctrl-E'),
                  })

# Not used yet, defined for compleness
stcDefs = {'Cut'        : 'Shft-Del',
           'Copy'       : 'Ctrl-Ins',
           'Paste'      : 'Shft-Ins',
           'SelectAll'  : 'Ctrl-A',
           'Undo'       : 'Ctrl-Z',
           'Redo'       : 'Ctrl-Y',
           'DeleteLine' : 'Ctrl-L'} 
