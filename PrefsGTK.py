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



# Height of the Palette window. Adjust if you use big fonts
paletteHeights = {'tabs': 100, 'menu': 56}

# Window manager dependent values useful for mostly for GTK
windowManagerTop = 16
windowManagerBottom = 7
windowManagerSide = 5

# Fudge values for placing the progressbar in the editor
editorProgressFudgePosX = -8
# Fudge values for placing the progressbar in the editor
editorProgressFudgeSizeY = 2

# Try to use transparent bitmaps for palette
transparentPaletteBitmaps = 0

# Match braces in code
braceHighLight = 0

# Minimize the IDE while running applications
minimizeOnRun = 0

# Draw grid in designer
drawDesignerGrid = 0
# Also draw grid for child container controls in the frame
drawDesignerGridForSubWindows = 1
# Grid draw method: 'lines', 'dots', 'grid', NYI: 'bitmap'
drawGridMethod = 'grid'

# Grayout (blueout actually) source while designer is open
grayoutSource = 0

# These settings may be specific to Red Hat, change them if the help
# complains about missing files.
# Note: If you want to use different versions of the help, see Scripts/HelpScrpt.py
# Python documentation path
pythonDocsPath = '/usr/doc/python-docs-1.5.2/Doc'
# wxWindows documentation path
wxWinDocsPath = '/usr/doc/wxPython-2.2.5'

# Font size of the text in the Inspector's statusbar
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

exportedProperties2 = ['logFontSize', 'srchCtrlOffset', 'paletteHeights',
 'windowManagerTop', 'windowManagerBottom', 'windowManagerSide',
 'editorProgressFudgePosX', 'editorProgressFudgeSizeY',
 'transparentPaletteBitmaps', 'braceHighLight', 'minimizeOnRun',
 'drawDesignerGrid', 'grayoutSource', 'inspStatBarFontSize',
 'pythonDocsPath', 'wxWinDocsPath']
