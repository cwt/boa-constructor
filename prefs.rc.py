## rc-version: 3 ##
# RCS-ID:      $Id$

# The main preference file.

from wxPython.wx import *

#-Miscellaneous-----------------------------------------------------------------

# Should toolbars have flat buttons, 0 for beveled buttons
flatTools = wxTB_FLAT
# Frame style for child windows of the main frame
# E.g. to prevent child windows from appearing on the taskbar set
# childFrameStyle = wx.wxCLIP_CHILDREN | wxFRAME_TOOL_WINDOW
childFrameStyle = wxCLIP_CHILDREN
# Style that the DataView ListCtrl is created in
## options: wxLC_SMALL_ICON, wxLC_LIST
dataViewListStyle = wxLC_LIST
# Should the palette be a menubar or a notebook
## options: 'tabs', 'menu'
paletteStyle = 'tabs'

# Alternating background colours used in ListCtrls (pastel blue and yellow)
pastels = true
pastelMedium = wxColour(235, 246, 255)
pastelLight = wxColour(255, 255, 240)

# Colour (indicating danger) used to display uninitialised window space.
# A control must be placed in this space before valid code can be generated
undefinedWindowCol = wxColour(128, 0, 0)

# Info that will be filled into the comment block. (Edit->Add module info)
# Also used by setup.py
staticInfoPrefs = { 'Purpose':   '',
                    'Author':    '<your name>',
                    'Copyright': '(c) 2002',
                    'Licence':   '<your licence>',
                    'Email':     '<your email>',
                  }

# Should modules be added to the application if it is the active Model when
# a module is created from the palette
autoAddToApplication = true

# Load images from a singe file Image.archive (zip of Image directory)
useImageArchive = false
# Only load image 1st time it is requested then cache it
# Turn this off to conserve resources on win9x
useImageCache = false

# Redirect stderrout to logmessages
logStdStreams = true
# Add module and line number where 'print' was called from
recordModuleCallPoint = false

# Safety net so COM support has to be explicitly turned on
# Will stay here until the win9x crashes has been sorted out
blockCOM = true

# Path to an alternative Python Interpreter. By default (blank string) Boa
# will use the same interpreter it is running on
## type: filepath
pythonInterpreterPath = ''

# Should the initialisation of the help be delayed until first usage?
delayInitHelp = true

# Try to update the wxPython.libs directory with the newest run time libs
# (Component files and example components)
# Turn this off if you don't have permissions to write to the wxPython/lib directory
installBCRTL = false

# Any module in the Plug-ins directory is automatically executed at startup
# While developing or debugging new plugins it is sometimes useful to
# turn off plugins if some plugin problem prevents Boa from starting up.
# Note: you may also create the Plug-ins directory : $HOME/.boa/Plug-ins
pluginsEnabled = false
# Path to an additional Plug-ins directory
## type: dirpath
extraPluginsPath = ''

# If the environment variable PYTHONSTARTUP is set to a python file
# this file can be executed at startup in the Shell's namespace
# The command-line flag -S can override this setting.
suExecPythonStartup = true

# In constricted mode Boa starts up showing only the Editor window.
# In the future this mode will be extended to not load support for the Designer.
# This will be the Python Editor mode.
# The command-line flag -C can override this setting.
suBoaConstricted = false

# Should wxPython Companions, Models and Views be loaded at startup
suWxPythonSupport = true

# This flag determines if Boa should create and listen on the socket for
# filenames sent by other instances of Boa. This way when you start another
# instance of Boa with a filename as command-line switch, that instance
# will send the filename to this one running the socket and the file will
# open here
suSocketFileOpenServer = true

# Where should the stderr and stdout notebook be docked?
## options: 'editor', 'inspector', 'undocked'
eoErrOutDockWindow = 'editor'
# When docked in the Editor, percentage wise, how high should the default
# Error/Output window be?
eoErrOutWindowHeightPerc = 0.2

#-Editor------------------------------------------------------------------------

# Syntax checking
# Underlines possible syntax errors with a red squigly line
checkSyntax = true
# Only do syntax checking if cursor moves off line that was modified
onlyCheckIfLineModified = true

# Also run pylint (very spurious!) on 'Check source'
runPyLintOnCheckSource = false
# Check Source (e.g. compile) when saving
checkSourceOnSave = false

# Should the model be refresh before invoking code completion or call tips.
# This causes a delay but is more accurate.
autoRefreshOnCodeComplete = false

# Flag for turning on special checking for european keyboard characters by
# checking for certain codes while ctrl alt is held.
handleSpecialEuropeanKeys = false
# Country code for keyboards,
## options: 'euro', 'france', 'swiss-german', 'italian'
euroKeysCountry = 'euro'

# The undo buffer can be cleared after saving, turning this on will
# never clear it and preserve the editing history but take extra memory
neverEmptyUndoBuffer = true

# Auto correct indentation and EOL characters on load, save and refresh
# This only works for Python 2.0 and up
autoReindent = false

# Should the files open when closing Boa be reloaded at next startup?
rememberOpenFiles = true

# Show filename extensions on the page tabs
showFilenameExtensions = false


#-Explorer----------------------------------------------------------------------

# Should sorting in the explorer be case insensitive
exCaseInsensitiveSorting = true

# Default filter for the Explorer and the File Dialog.
# BoaFiles - The most detailed and slowest, showing Packages and the different
# types of Python modules.
# StdFiles - The fastest, displaying only file association information.
## options: 'BoaFiles', 'StdFiles'
exDefaultFilter = 'BoaFiles'

# Normally Boa will startup and run in the Current Working Directory of it's
# process. With this setting you may overwrite it.
## type: dirpath
exWorkingDirectory = ''

# Default width of the tree in the Explorer
exDefaultTreeWidth = 230

# Should filetypes which are known to optionally contain a header be opened
# and read when listing items
exInspectInspectableFiles = true

# Start the open file dialog relative to the file in the active module page
exOpenFromHere = true

#-Shell prompts-----------------------------------------------------------------

# Shell prompt (must be 3 chars with trailing space)'
ps1 = '>>> '
# Shell prompt, continued line (must be 3 chars with trailing space)'
ps2 = '... '
# Shell debug prompt (must be 3 chars with trailing space)'
ps3 = 'Db> '
# Shell prompt, standard input request (must be 3 chars with trailing space)
ps4 = '<<< '

#-Inspector---------------------------------------------------------------------

# Display properties for which source will be generated in Bold
showModifiedProps = true
# Colour of property value static text ctrls
propValueColour = wxColour(0, 0, 120)
# Inspector row height
oiLineHeight = 18
# Default height of event selection window in Inspector
oiEventSelectionHeight = 140
# Inspector notebook style flags
## options: 0, wxNB_FIXEDWIDTH, wxNB_LEFT, wxNB_RIGHT, wxNB_BOTTOM
inspNotebookFlags = 0
# Page names for the inspector notebook
inspPageNames = {'Constr': 'Constr', ##'Constructor',
                 'Props': 'Props', ##'Properties',
                 'Evts': 'Evts', ##'Events',
                 'Objs': 'Objs'} ##'Objects'}

#-Designer----------------------------------------------------------------------

# Granularity of the Designer's grid.
dsGridSize = 8

# Size of the selection tags (small black squares) used in the Designer for
# sizing and to show selection.
dsSelectionTagSize = 8

# Width of the lines of frame around the selection.
dsSelectionFrameWidth = 2

# Colours for the selection tags when they represent Anchors
dsAnchorEnabledCol = wxColour(0, 0, 255)
dsAnchorDisabledCol = wxColour(40, 100, 110)

# Default control size if control itself has no sensible default
dsDefaultControlSize = wxSize(200, 100)

#-Code generation---------------------------------------------------------------

# Should the paths to image file be created as absolute paths or relative to
# either the directory of the application file or the directory of the module?
# When a path is created for a module that has never been saved it will always
# be absolute.
# Remember, when a path is stored relatively, the current directory of the
# process must be correct (relatively ;) when your code executes.
cgAbsoluteImagePaths = true

# Should there be an empty line between objects in _init_* methods?
# Note that in _init_coll_* methods, blank lines between are NOT optional
cgEmptyLineBetweenObjects = true

# Format string used to generate keyword argument parameter
cgKeywordArgFormat = '%(keyword)s = %(value)s'

#-Views-------------------------------------------------------------------------

# Background colour of the canvas used by OGL views.
vpOGLCanvasBackgroundColour = wxWHITE
# Colours of the connection lines between shapes in diagrams
vpOGLLinePen = wxBLACK_PEN
vpOGLLineBrush = wxBLACK_BRUSH
# Pen used to draw Class shapes
vpOGLClassShapePen = wxBLACK_PEN
# Brush used to draw Class shapes
vpOGLClassShapeBrush = wxLIGHT_GREY_BRUSH
# Pen used to draw Class shapes defined in other modules
vpOGLExternalClassShapePen = wxBLACK_PEN
# Brush used to draw Class shapes defined in other modules
vpOGLExternalClassShapeBrush = wxGREY_BRUSH
# Pen used to draw Modules
vpOGLModuleShapePen = wxBLACK_PEN
# Brush used to draw Modules
vpOGLModuleShapeBrush = wxLIGHT_GREY_BRUSH

#-------------------------------------------------------------------------------
# wxStyledTextCtrl default settings, edited on a seperate config node.
# Docs from the Scintilla web page

# Makes end-of-line characters visible or not.
STCViewEOL = false
# Determines whether indentation should be created out of a mixture of tabs and
# space or be based purely on spaces.
STCUseTabs = false
# Sets the size of a tab as a multiple of the size of a space character in the
# style of the language's default style definition.
STCTabWidth = 4
# Sets the size of indentation in terms of characters.
STCIndent = 4
# Margin width used for line numbering
STCLineNumMarginWidth = 28
# Margin width used by symbols such as breakpoints and line pointers
STCSymbolMarginWidth = 15
# Margin width used for line folding, set to 0 to 'disable' folding
STCFoldingMarginWidth = 13
# Turns buffered drawing on or off. Buffered drawing draws each line into a bitmap
# rather than directly to the screen and then copies the bitmap to the screen.
# This avoids flickering although it does take slightly longer.
STCBufferedDraw = true
# Indentation guides are dotted vertical lines that appear within indentation
# whitespace every indent size columns. They make it easy to see which constructs
# line up especially when they extend over multiple pages.
STCIndentationGuides = false

from wxPython.stc import wxSTC_WS_INVISIBLE, wxSTC_WS_VISIBLEALWAYS, wxSTC_WS_VISIBLEAFTERINDENT
# White space can be made visible. Space characters appear as small centred dots
# and tab characters as light arrows pointing to the right.
# With the SCWS_VISIBLEAFTERINDENT option, white space used for indentation is
# invisible but after the first visible character, it is visible.
## options: wxSTC_WS_INVISIBLE, wxSTC_WS_VISIBLEALWAYS, wxSTC_WS_VISIBLEAFTERINDENT
STCViewWhiteSpace = wxSTC_WS_INVISIBLE

from wxPython.stc import wxSTC_CARET_SLOP, wxSTC_CARET_CENTER, wxSTC_CARET_STRICT
wxSTC_CARET_SLOP_CENTER = wxSTC_CARET_SLOP | wxSTC_CARET_CENTER
wxSTC_CARET_SLOP_STRICT = wxSTC_CARET_SLOP | wxSTC_CARET_STRICT
wxSTC_CARET_SLOP_CENTER_STRICT = wxSTC_CARET_SLOP | wxSTC_CARET_CENTER | wxSTC_CARET_STRICT
wxSTC_CARET_CENTER_STRICT = wxSTC_CARET_CENTER | wxSTC_CARET_STRICT
# Can be set to a combination of the flags CARET_SLOP and CARET_STRICT to change
# the automatic vertical positioning of the view when ensuring a position is visible.
# If CARET_SLOP is off then the caret is centred within the view.
# When CARET_STRICT is set then caret policy is rechecked even if the caret is completely visible.
# Setting this value to 0 will leave the policy at startup default
## options: 0, wxSTC_CARET_SLOP, wxSTC_CARET_CENTER, wxSTC_CARET_STRICT, wxSTC_CARET_SLOP_CENTER, wxSTC_CARET_SLOP_STRICT, wxSTC_CARET_SLOP_CENTER_STRICT, wxSTC_CARET_CENTER_STRICT
STCCaretPolicy = 0
# If CARET_SLOP is on then the slop value determines the number of lines at top
# and bottom of the view where the caret should not go.
STCCaretPolicySlop = 0
# Sets rate at which the caret blinks, this determines the time in milliseconds
# that the caret is visible or invisible before changing state.
# Setting the period to 0 stops the caret blinking.
STCCaretPeriod = 500

from wxPython.stc import wxSTC_EDGE_NONE, wxSTC_EDGE_LINE, wxSTC_EDGE_BACKGROUND
# This mechanism marks lines that are longer than a specified length in one of two ways.
# A vertical line can be displayed at the specified column number (EDGE_LINE) or
# characters after that column can be displayed with a specified background colour
# (EDGE_BACKGROUND). The vertical line works well for monospaced fonts but not for
# proportional fonts which should use EDGE_BACKGROUND.
## options: wxSTC_EDGE_NONE, wxSTC_EDGE_LINE, wxSTC_EDGE_BACKGROUND
STCEdgeMode = wxSTC_EDGE_LINE
STCEdgeColumnWidth = 80

# Colours
STCCallTipBackColour = wxColour(255, 255, 240)
STCSyntaxErrorColour = wxColour(255, 0, 0)
STCCodeBrowseColour = wxColour(0, 0, 255)
STCDebugBrowseColour = wxColour(255, 0, 0)

# Markers
from wxPython.stc import wxSTC_MARK_CIRCLE, wxSTC_MARK_ROUNDRECT, \
      wxSTC_MARK_ARROW, wxSTC_MARK_SMALLRECT, wxSTC_MARK_SHORTARROW, \
      wxSTC_MARK_EMPTY, wxSTC_MARK_ARROWDOWN, wxSTC_MARK_MINUS, wxSTC_MARK_PLUS

STCLinePointer = wxSTC_MARK_SHORTARROW, 'BLACK', 'BLUE'
STCBreakpointMarker = wxSTC_MARK_CIRCLE, 'BLACK', 'RED'
STCTmpBreakpointMarker = wxSTC_MARK_CIRCLE, 'BLACK', 'BLUE'
STCDisabledBreakpointMarker = wxSTC_MARK_CIRCLE, 'BLACK', wxColour(0xCC, 0xCC, 0xCC)
STCMarkPlaceMarker = wxSTC_MARK_SHORTARROW, 'BLACK', 'YELLOW'

STCDiffAddedMarker = wxSTC_MARK_PLUS, 'BLACK', 'WHITE'
STCDiffRemovedMarker = wxSTC_MARK_MINUS, 'BLACK', 'WHITE'
STCDiffChangesMarker = wxSTC_MARK_SMALLRECT, 'BLACK', 'WHITE'

STCFoldingOpen = wxSTC_MARK_MINUS, 'BLACK', 'WHITE'
STCFoldingClose = wxSTC_MARK_PLUS, 'BLACK', 'WHITE'

#-------------------------------------------------------------------------------

# Editable preferences
exportedProperties = ['flatTools', 'childFrameStyle', 'dataViewListStyle',
  'paletteStyle',
  'pastels', 'pastelMedium', 'pastelLight', 'undefinedWindowCol',
  'useImageArchive', 'pythonInterpreterPath', 'delayInitHelp',
  'logStdStreams', 'recordModuleCallPoint', 'autoAddToApplication',
  'installBCRTL', 'blockCOM', 'pluginsEnabled', 'extraPluginsPath',
  'suExecPythonStartup', 'suBoaConstricted', 'suWxPythonSupport', 
  'suSocketFileOpenServer',
  'eoErrOutDockWindow', 'eoErrOutWindowHeightPerc',
  'checkSyntax', 'onlyCheckIfLineModified', 'checkSourceOnSave',
  'autoRefreshOnCodeComplete', 'autoReindent',
  'exCaseInsensitiveSorting', 'exDefaultFilter', 'exWorkingDirectory',
  'exDefaultTreeWidth', 'exInspectInspectableFiles', 'exOpenFromHere',
  'handleSpecialEuropeanKeys', 'euroKeysCountry', 'rememberOpenFiles',
  'showFilenameExtensions',
  'ps1', 'ps2', 'ps3', 'ps4',
  'showModifiedProps', 'propValueColour',
  'oiLineHeight', 'oiEventSelectionHeight', 'inspNotebookFlags',
  'cgAbsoluteImagePaths', 'cgEmptyLineBetweenObjects', 'cgKeywordArgFormat',
  'dsGridSize', 'dsSelectionTagSize', 'dsSelectionFrameWidth',
  'dsAnchorEnabledCol', 'dsAnchorDisabledCol', 'dsDefaultControlSize',
  'vpOGLCanvasBackgroundColour', 'vpOGLLinePen', 'vpOGLLineBrush',
  'vpOGLClassShapePen', 'vpOGLClassShapeBrush', 'vpOGLExternalClassShapePen',
  'vpOGLClassShapeBrush', 'vpOGLExternalModuleShapePen',
  'vpOGLModuleShapeBrush',
]

exportedSTCProps = ['STCViewEOL', 'STCUseTabs', 'STCTabWidth', 'STCIndent',
  'STCLineNumMarginWidth',
  'STCSymbolMarginWidth', 'STCFoldingMarginWidth', 'STCBufferedDraw',
  'STCIndentationGuides', 'STCViewWhiteSpace', 'STCCaretPolicy', 'STCCaretPeriod',
  'STCEdgeMode', 'STCEdgeColumnWidth',
  'STCCallTipBackColour', 'STCSyntaxErrorColour', 'STCCodeBrowseColour',
  'STCDebugBrowseColour']
