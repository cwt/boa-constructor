## rc-version: 1 ##
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
                    'Author':    '<Name>',
                    'Copyright': '(c)',
                    'Licence':   '<License>',
                    'Email':     '<Email>',
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
blockCOM = false

# Debugger to use
# Before changing this variable, save all modified files.
# After changing this variable, Boa has to be restarted immediately
# or it will behave abnormally
## options: 'old', 'new'
useDebugger = 'old'

# Path to an alternative Python Interpreter. By default (blank string) Boa
# will use the same interpreter it is running on
## type: filepath
pythonInterpreterPath = ''
#pythonInterpreterPath = 'd:/progra~1/zope/2-3-1/bin/python.exe'

# Should the initialisation of the help be delayed until first usage?
delayInitHelp = true

# Try to update the wxPython.libs directory with the newest run time libs 
# (Component files and example components)
# Turn this off if you don't have permissions to write to the wxPython/lib directory
installBCRTL = true

#-Editor------------------------------------------------------------------------

# Syntax checking
# Underlines possible syntax errors with a red squigly line
# Syntax is checked whwn the cursor moves off a line that was modified
checkSyntax = true
# Only do syntax checking if cursor moves off line that was modified
onlyCheckIfLineModified = true
# Also run pylint (very spurious!) on 'Check source'
runPyLintOnCheckSource = false

# Flag for turning on special checking for european keyboard characters by
# checking for certain codes while ctrl alt is held.
handleSpecialEuropeanKeys = false
# Country code for keyboards, 
## options: 'euro', 'france', 'swiss-german' 
euroKeysCountry = 'euro'

# The undo buffer can be cleared after saving, turning this on will
# never clear it and preserve the editing history but take extra memory
neverEmptyUndoBuffer = true

# Auto correct indentation and EOL characters on load, save and refresh
# This only works for Python 2.0 and up
autoReindent = false

# Should the files open when closing Boa be reloaded at next startup?
rememberOpenFiles = true

#-Explorer----------------------------------------------------------------------

# Should sorting in the explorer be case insensitive
caseInsensitiveSorting = true

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
# Inspector notebook style flags
## options: 0, wxNB_FIXEDWIDTH, wxNB_LEFT, wxNB_RIGHT, wxNB_BOTTOM
inspNotebookFlags = 0 
# Should the stderr and stdout notebook be hosted in the inspector?
showErrOutInInspector = true
# Page names for the inspector notebook
inspPageNames = {'Constr': 'Constr', ##'Constructor',
                 'Props': 'Props', ##'Properties',
                 'Evts': 'Evts', ##'Events',
                 'Objs': 'Objs'} ##'Objects'}

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
STCSymbolMarginWidth = 13
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
STCSyntaxErrorColour = wxColour(255, 128, 0)
STCCodeBrowseColour = wxColour(0, 255, 255)
STCDebugBrowseColour = wxColour(255, 128, 0)#wxRED

# Markers
from wxPython.stc import wxSTC_MARK_CIRCLE, wxSTC_MARK_ROUNDRECT, \
      wxSTC_MARK_ARROW, wxSTC_MARK_SMALLRECT, wxSTC_MARK_SHORTARROW, \
      wxSTC_MARK_EMPTY, wxSTC_MARK_ARROWDOWN, wxSTC_MARK_MINUS, wxSTC_MARK_PLUS 

STCBreakpointMarker = wxSTC_MARK_CIRCLE, '#FF8080', 'RED' #'BLACK', 'RED'
STCLinePointer = wxSTC_MARK_SHORTARROW, '#00FFFF', 'BLUE' #'NAVY', 'BLUE'
STCTmpBreakpointMarker = wxSTC_MARK_CIRCLE, '#00FFFF', 'BLUE' #'BLACK', 'BLUE'
STCMarkPlaceMarker = wxSTC_MARK_SHORTARROW, 'WHITE', 'YELLOW' #'NAVY', 'YELLOW'

STCDiffAddedMarker = wxSTC_MARK_PLUS, 'BLACK', 'WHITE'
STCDiffRemovedMarker = wxSTC_MARK_MINUS, 'BLACK', 'WHITE'
STCDiffChangesMarker = wxSTC_MARK_SMALLRECT, 'BLACK', 'WHITE'

STCFoldingOpen = wxSTC_MARK_PLUS, 'BLACK', 'WHITE'
STCFoldingClose = wxSTC_MARK_MINUS, 'BLACK', 'WHITE'

#-------------------------------------------------------------------------------

# Editable preferences
exportedProperties = ['flatTools', 'childFrameStyle', 'paletteStyle',
  'pastels', 'pastelMedium', 'pastelLight', 'undefinedWindowCol', 
  'useImageArchive', 'pythonInterpreterPath', 'delayInitHelp',
  'logStdStreams', 'recordModuleCallPoint', 'autoAddToApplication',
  'installBCRTL', 'blockCOM', 
  'checkSyntax', 'onlyCheckIfLineModified', 'autoReindent', 'caseInsensitiveSorting',
  'handleSpecialEuropeanKeys', 'euroKeysCountry', 'rememberOpenFiles',
  'ps1', 'ps2', 'ps3', 'ps4',
  'showModifiedProps', 'propValueColour', 
  'oiLineHeight', 'oiNamesWidth', 'inspNotebookFlags', 'showErrOutInInspector']

exportedSTCProps = ['STCViewEOL', 'STCUseTabs', 'STCTabWidth', 'STCIndent', 
  'STCLineNumMarginWidth', 
  'STCSymbolMarginWidth', 'STCFoldingMarginWidth', 'STCBufferedDraw', 
  'STCIndentationGuides', 'STCViewWhiteSpace', 'STCCaretPolicy', 'STCCaretPeriod',
  'STCEdgeMode', 'STCEdgeColumnWidth', 
  'STCCallTipBackColour', 'STCSyntaxErrorColour', 'STCCodeBrowseColour', 
  'STCDebugBrowseColour']

