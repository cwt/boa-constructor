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
paletteHeight = 140

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
