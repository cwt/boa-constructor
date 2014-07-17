## rc-version: 9 ##
# RCS-ID:      $Id$

#-Miscellaneous-----------------------------------------------------------------

# Style of the Error/Output window's notebook.
## options: 'text', 'full', 'side'
eoErrOutNotebookStyle = 'full'

#-Explorer----------------------------------------------------------------------

# Should sorting in the explorer be case insensitive
exCaseInsensitiveSorting = True

#-Editor------------------------------------------------------------------------
# Should there be submenu with all the items from the New palete under the
# Editor's File menu.
edShowFileNewMenu = True

# Should a custom wxSTC paint handler he installed which minimizes refresing?
edUseCustomSTCPaintEvtHandler = True
# There is a problem with folding on GTK
edSTCFolding = True

#-Window settings---------------------------------------------------------------

# Height of the Palette window. Adjust if you use big fonts
paletteHeights = {'tabs': 120, 'menu': 74}
# Used my Mac toplevel main menu
topMenuHeight = 0

# The amount of space Boa should leave on the right for a vertical OS Taskbar.
verticalTaskbarWidth = 0
# The amount of space Boa should leave from the bottom for a horizontal OS Taskbar.
horizontalTaskbarHeight = 50
# Percentage of the with that the Editor window should occupy
editorScreenWidthPerc = 0.73

# Window manager dependent values useful for mostly for GTK
windowManagerTop = 0
windowManagerBottom = 0
windowManagerSide = 0

# Font size of the text in the Inspector's statusbar
inspStatBarFontSize = 9

# Match braces in code
braceHighLight = True

# Minimize the IDE while running applications
minimizeOnRun = True

# Minimize the IDE when using Debug/Continue while debugging 
minimizeOnDebug = True

explorerFileSysRootDefault = ('DRIVE:\\', 'C:\\')

#-Designer----------------------------------------------------------------------

# Draw grid in designer
drawDesignerGrid = True
# Also draw grid for child container controls in the frame
drawDesignerGridForSubWindows = True
# Grid drawing method
## options: 'lines', 'dots', 'grid'
drawGridMethod = 'grid'

# Grayout (blueout actually) source while designer is open
grayoutSource = True

# Editable preferences
exportedProperties2 = ['exCaseInsensitiveSorting', 'eoErrOutNotebookStyle',
 'edShowFileNewMenu', 'edSTCFolding', 'verticalTaskbarWidth',
 'horizontalTaskbarHeight', 'editorScreenWidthPerc',
 'windowManagerTop', 'windowManagerBottom', 'windowManagerSide',
 'braceHighLight', 'minimizeOnRun', 'minimizeOnDebug', 'inspStatBarFontSize', 
 'drawDesignerGrid', 'drawDesignerGridForSubWindows',  'drawGridMethod', 
 'grayoutSource',
]
