#----------------------------------------------------------------------
# Name:        PrefsGTK.py
# Purpose:     wxGTK specific preferences
#
# Author:      Riaan Booysen
#
# Created:     2000/01/07
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------



logFontSize = 10
srchCtrlOffset = 0
paletteHeight = 100

windowManagerTop = 16
windowManagerBottom = 7
windowManagerSide = 5

editorProgressFudgePosX = -8
editorProgressFudgeSizeY = 2

# Try to use transparent bitmaps for palette
transparentPaletteBitmaps = 0

# Match braces in code
braceHighLight = 0

# Minimize the IDE while running applications
minimizeOnRun = 0

# Draw grid in designer
drawDesignerGrid = 0

# Grayout (blueout actually) source while designer is open
grayoutSource = 0

# These settings may be specific to Red Hat, change them if the help
# complains about missing files.
# Note: If you want to use different versions of the help, see Scripts/HelpScrpt.py
pythonDocsPath = '/usr/doc/python-docs-1.5.2/Doc'

wxWinDocsPath = '/usr/doc/wxPython-2.2.5'

inspStatBarFontSize = 13

explorerFileSysRootDefault = ('/', '/')

# Scintilla/wxStyledTextCtrl font definitions
faces = { 'times'  : 'Times',
          'mono'   : 'Courier',
          'helv'   : 'Helvetica',
          'other'  : 'new century schoolbook',
          'size'   : 9,
          'lnsize' : 8,
          'backcol': '#FFFFFF',}
