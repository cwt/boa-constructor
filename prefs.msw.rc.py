## rc-version: 1 ##
# RCS-ID:      $Id$

#-Window settings---------------------------------------------------------------

# Height of the Palette window. Adjust if you use big fonts
paletteHeights = {'tabs': 118, 'menu': 72}

# Window manager dependent values useful for mostly for GTK
windowManagerTop = 0
windowManagerBottom = 0
windowManagerSide = 0

# Font size of the text in the Inspector's statusbar
inspStatBarFontSize = 9

# Try to use transparent bitmaps for palette
#transparentPaletteBitmaps = 1

# Match braces in code
braceHighLight = true

# Minimize the IDE while running applications
minimizeOnRun = false

explorerFileSysRootDefault = ('DRIVE:\\', 'C:\\')

#-Designer----------------------------------------------------------------------

# Draw grid in designer
drawDesignerGrid = true
# Also draw grid for child container controls in the frame
drawDesignerGridForSubWindows = true
# Grid drawing method
## options: 'lines', 'dots', 'grid'
drawGridMethod = 'grid'

# Grayout (blueout actually) source while designer is open
grayoutSource = true

# Editable preferences
exportedProperties2 = ['windowManagerTop', 'windowManagerBottom', 'windowManagerSide',
 'braceHighLight', 'minimizeOnRun', 'inspStatBarFontSize',
 'drawDesignerGrid', 'drawDesignerGridForSubWindows', 'drawGridMethod',
 'grayoutSource']
