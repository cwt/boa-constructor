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
  'ContextHelp' : (wxACCEL_NORMAL, WXK_F1),
  'ToggleBrk'   : (wxACCEL_NORMAL, WXK_F5),
  'Compile'     : (wxACCEL_NORMAL, WXK_F7),
  'Debug'       : (wxACCEL_NORMAL, WXK_F8),
  'RunApp'      : (wxACCEL_NORMAL, WXK_F9),
  'RunMod'      : (wxACCEL_NORMAL, WXK_F10),
  'Inspector'   : (wxACCEL_NORMAL, WXK_F11),
  'Designer'    : (wxACCEL_NORMAL, WXK_F12),
  'Editor'      : (wxACCEL_NORMAL, WXK_F12),
  'Find'        : (wxACCEL_CTRL, ord('F')),
  'FindAgain'   : (wxACCEL_NORMAL, WXK_F3),
  'Open'        : (wxACCEL_CTRL, ord('O')),
  'Close'       : (wxACCEL_CTRL, ord('Q')),
  'Save'        : (wxACCEL_CTRL, ord('S')),
  'Indent'      : (wxACCEL_CTRL, ord('I')), # ctrl ] doesn't work
  'Dedent'      : (wxACCEL_CTRL, ord('U')), # ctrl [ doesn't work
  'DashLine'    : (wxACCEL_CTRL, ord('B')),
  'Refresh'     : (wxACCEL_CTRL, ord('R')),
  'Insert'      : (wxACCEL_NORMAL, WXK_INSERT),
  'Delete'      : (wxACCEL_NORMAL, WXK_DELETE),
}

if wxPlatform == '__WXMSW__':
    keyDefs.update({'SaveAs'      : (wxACCEL_ALT, ord('S')),
                    'Comment'     : (wxACCEL_ALT, ord('3')),
                    'Uncomment'   : (wxACCEL_ALT, ord('4')),
                    'SwitchToApp' : (wxACCEL_ALT, ord('A'))})
elif wxPlatform == '__WXGTK__':
    keyDefs.update({'SaveAs'      : (wxACCEL_CTRL, ord('1')),
                    'Comment'     : (wxACCEL_CTRL, ord('3')),
                    'Uncomment'   : (wxACCEL_CTRL, ord('4')),
                    'SwitchToApp' : (wxACCEL_CTRL, ord('5'))})






