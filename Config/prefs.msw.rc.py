## rc-version: 8 ##
# RCS-ID:      $Id$

#-Miscellaneous-----------------------------------------------------------------

# Style of the Error/Output window's notebook.
## options: 'text', 'full', 'side'
eoErrOutNotebookStyle = 'full'

#-Explorer----------------------------------------------------------------------

# Should sorting in the explorer be case insensitive
exCaseInsensitiveSorting = true

#-Editor------------------------------------------------------------------------
# Should there be submenu with all the items from the New palete under the
# Editor's File menu.
edShowFileNewMenu = true

# Should a custom wxSTC paint handler he installed which minimizes refresing?
edUseCustomSTCPaintEvtHandler = false
# There is a problem with folding on GTK
edSTCFolding = true

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
braceHighLight = true

# Minimize the IDE while running applications
minimizeOnRun = false

# Minimize the IDE when using Debug/Continue while debugging 
minimizeOnDebug = false

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

#-Code completion---------------------------------------------------------------

# With these flags you can set which wxPython libraries are available to code completion.

# Import wxPython.utils for Code Completion
ccImportWxPyUtils = true
# Import wxPython.html for Code Completion
ccImportWxPyHtml = true
# Import wxPython.htmlhelp for Code Completion
ccImportWxPyHtmlHelp = true
# Import wxPython.help for Code Completion
ccImportWxPyHelp = true
# Import wxPython.calendar for Code Completion
ccImportWxPyCalendar = true
# Import wxPython.grid for Code Completion
ccImportWxPyGrid = true
# Import wxPython.ogl for Code Completion
ccImportWxPyOgl = true
# Import wxPython.stc for Code Completion
ccImportWxPyStc = true
# Import wxPython.gizmos for Code Completion
ccImportWxPyGizmos = true
# Import wxPython.wizard for Code Completion
ccImportWxPyWizard = true

# With these filters the names available to code completion can be narrowed down further.

# Filter out all wxPython names
ccFilterWxAll = false
# Filter out all classes ending in Ptr
ccFilterWxPtrNames = true
# Filters out integer constant values
ccFilterWxConstants = false
# Filter out functions
ccFilterWxFunctions = false
# Filter out classes
ccFilterWxClasses = false
# Filter out instances
ccFilterWxInstances = false

# Editable preferences
exportedProperties2 = ['exCaseInsensitiveSorting', 'eoErrOutNotebookStyle',
 'edShowFileNewMenu', 'edSTCFolding', 'verticalTaskbarWidth',
 'horizontalTaskbarHeight', 'editorScreenWidthPerc',
 'windowManagerTop', 'windowManagerBottom', 'windowManagerSide',
 'braceHighLight', 'minimizeOnRun', 'minimizeOnDebug', 'inspStatBarFontSize', 
 'drawDesignerGrid', 'drawDesignerGridForSubWindows',  'drawGridMethod', 
 'grayoutSource',
 'ccImportWxPyUtils', 'ccImportWxPyHtml', 'ccImportWxPyHtmlHelp',
 'ccImportWxPyHelp', 'ccImportWxPyCalendar', 'ccImportWxPyGrid',
 'ccImportWxPyOgl', 'ccImportWxPyStc', 'ccImportWxPyGizmos',
 'ccFilterWxAll', 'ccFilterWxPtrNames', 'ccFilterWxConstants',
 'ccFilterWxFunctions', 'ccFilterWxClasses', 'ccFilterWxInstances',
]
