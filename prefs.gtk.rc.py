## rc-version: 1 ##
# RCS-ID:      $Id$

#-Window settings---------------------------------------------------------------

# Height of the Palette window. Adjust if you use big fonts
paletteHeights = {'tabs': 100, 'menu': 56}

# Window manager dependent values useful for mostly for GTK
windowManagerTop = 16
windowManagerBottom = 7
windowManagerSide = 5

# Try to use transparent bitmaps for palette
transparentPaletteBitmaps = 0

# Match braces in code
braceHighLight = 0

# Minimize the IDE while running applications
minimizeOnRun = 0

# Font size of the text in the Inspector's statusbar
inspStatBarFontSize = 13

explorerFileSysRootDefault = ('/', '/')

#-Designer----------------------------------------------------------------------

# Draw grid in designer
drawDesignerGrid = 0
# Also draw grid for child container controls in the frame
drawDesignerGridForSubWindows = 1
# Grid draw method: 'lines', 'dots', 'grid', NYI: 'bitmap'
## options: 'lines', 'dots', 'grid'
drawGridMethod = 'grid'

# Grayout (blueout actually) source while designer is open
grayoutSource = 0

# Scintilla/wxStyledTextCtrl font definitions
faces = { 'times'  : 'Times', 'mono'   : 'Courier', 'helv'   : 'Helvetica', 'other'  : 'new century schoolbook', 'size'   : 9, 'lnsize' : 8, 'backcol': '#FFFFFF',}

# Editable preferences
exportedProperties2 = ['windowManagerTop', 'windowManagerBottom', 'windowManagerSide',
 'braceHighLight', 'minimizeOnRun', 'inspStatBarFontSize',
 'drawDesignerGrid', 'drawDesignerGridForSubWindows', 'drawGridMethod',
 'grayoutSource']
