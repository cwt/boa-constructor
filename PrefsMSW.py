#----------------------------------------------------------------------
# Name:        PrefsMSW.py
# Purpose:     wxMSW specific preferences
#
# Author:      Riaan Booysen
#
# Created:     2000/01/07
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
from os import path
import sys

logFontSize = 7
srchCtrlOffset = 0
paletteHeight = 118

windowManagerTop = 0
windowManagerBottom = 0

editorProgressFudgePosX = 0
editorProgressFudgeSizeY = 0

transparentPaletteBitmaps = 1 

braceHighLight = 1




pythonDocsPath = path.join(path.dirname(sys.executable), 'Doc')
import wxPython
wxWinDocsPath = path.join(path.dirname(wxPython.__file__), 'docs', 'wx')

inspStatBarFontSize = 9

explorerFileSysRootDefault = ('DRIVE:\\', 'C:\\')

# Scintilla/wxStyledTextCtrl font definitions 
faces = { 'times'  : 'Times New Roman',
          'mono'   : 'Courier New',
          'helv'   : 'Lucida Console',
          'lucd'   : 'Lucida Console',
          'other'  : 'Comic Sans MS',
          'size'   : 8,
          'lnsize' : 6,
          'backcol': '#FFFFFF',}
