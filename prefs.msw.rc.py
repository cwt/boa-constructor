# Height of the Palette window. Adjust if you use big fonts
paletteHeights = {'tabs': 118, 'menu': 72}

# Window manager dependent values useful for mostly for GTK
windowManagerTop = 0
windowManagerBottom = 0
windowManagerSide = 0

# Fudge values for placing the progressbar in the editor
editorProgressFudgePosX = 0
# Fudge values for placing the progressbar in the editor
editorProgressFudgeSizeY = 0

# Try to use transparent bitmaps for palette
transparentPaletteBitmaps = 1

# Match braces in code
braceHighLight = 1

# Minimize the IDE while running applications
minimizeOnRun = 1

# Draw grid in designer
drawDesignerGrid = 1
# Also draw grid for child container controls in the frame
drawDesignerGridForSubWindows = 1
# Grid draw method: 'lines', 'dots', 'grid', NYI: 'bitmap'
drawGridMethod = 'grid'

# Grayout (blueout actually) source while designer is open
grayoutSource = 1

# Font size of the text in the Inspector's statusbar
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

#----Editable preferences-------------------------------------------------------
exportedProperties2 = ['logFontSize', 'srchCtrlOffset', 'paletteHeights',
 'windowManagerTop', 'windowManagerBottom', 'windowManagerSide',
 'editorProgressFudgePosX', 'editorProgressFudgeSizeY',
 'transparentPaletteBitmaps', 'braceHighLight', 'minimizeOnRun',
 'drawDesignerGrid', 'drawDesignerGridForSubWindows', 'drawGridMethod',
 'grayoutSource', 'inspStatBarFontSize']
