## rc-version: 6 ##
# RCS-ID:      $Id$




# Style of the Error/Output window's notebook. GTK is text only
eoErrOutNotebookStyle = 'text'

#-Explorer----------------------------------------------------------------------

# Should sorting in the explorer be case insensitive
exCaseInsensitiveSorting = false

#-Editor------------------------------------------------------------------------
# Should there be submenu with all the items from the New palete under the
# Editor's File menu. Causes warnings under wxGTK.
edShowFileNewMenu = false

# Should a custom wxSTC paint handler he installed which minimizes refresing?
edUseCustomSTCPaintEvtHandler = false
# There is a problem with folding on GTK
edSTCFolding = false

#-Window settings---------------------------------------------------------------

# Height of the Palette window. Adjust if you use big fonts
paletteHeights = {'tabs': 100, 'menu': 56}

# The amount of space Boa should leave on the right for a vertical OS Taskbar.
verticalTaskbarWidth = 0
# The amount of space Boa should leave from the bottom for a horizontal OS Taskbar.
horizontalTaskbarHeight = 100
# Percentage of the with that the Editor window should occupy
editorScreenWidthPerc = 3.0/4.0

# Window manager dependent values useful for mostly for GTK
windowManagerTop = 16
windowManagerBottom = 7
windowManagerSide = 5

# Font size of the text in the Inspector's statusbar
inspStatBarFontSize = 13

# Match braces in code
braceHighLight = false

# Minimize the IDE while running applications
minimizeOnRun = false

explorerFileSysRootDefault = ('/', '/')

#-Designer----------------------------------------------------------------------

# Draw grid in designer
drawDesignerGrid = false
# Also draw grid for child container controls in the frame
drawDesignerGridForSubWindows = false
# Grid draw method: 'lines', 'dots', 'grid', NYI: 'bitmap'
## options: 'lines', 'dots', 'grid'
drawGridMethod = 'grid'

# Grayout (blueout actually) source while designer is open
grayoutSource = false

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

# With these filters the names available to code completion can be narrowed down further.

# Filter out all wxPython names
ccFilterWxAll = false
# Filter out all classes ending in Ptr
ccFilterWxPtrNames = true
# Filters out integer constant values
ccFilterWxConstants = true
# Filter out functions
ccFilterWxFunctions = false
# Filter out classes
ccFilterWxClasses = false
# Filter out instances
ccFilterWxInstances = false

# Editable preferences
exportedProperties2 = ['exCaseInsensitiveSorting', 'edShowFileNewMenu',
 'edUseCustomSTCPaintEvtHandler', 'edSTCFolding', 'verticalTaskbarWidth',
 'horizontalTaskbarHeight', 'editorScreenWidthPerc',
 'windowManagerTop', 'windowManagerBottom', 'windowManagerSide',
 'braceHighLight', 'minimizeOnRun', 'inspStatBarFontSize',
 'drawDesignerGrid', 'drawDesignerGridForSubWindows', 'drawGridMethod',
 'grayoutSource',
 'ccImportWxPyUtils', 'ccImportWxPyHtml', 'ccImportWxPyHtmlHelp',
 'ccImportWxPyHelp', 'ccImportWxPyCalendar', 'ccImportWxPyGrid',
 'ccImportWxPyOgl', 'ccImportWxPyStc', 'ccImportWxPyGizmos',
 'ccFilterWxAll', 'ccFilterWxPtrNames', 'ccFilterWxConstants',
 'ccFilterWxFunctions', 'ccFilterWxClasses', 'ccFilterWxInstances',
]
