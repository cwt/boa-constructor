from wxPython.wx import *

print 'Setting user preferences'

#-Miscellaneous-----------------------------------------------------------------

# Should toolbars have flat buttons
flatTools = wxTB_FLAT
# Frame style for child windows of the main frame
# E.g. to prevent child windows from appearing on the taskbar set
# childFrameStyle = wx.wxCLIP_CHILDREN | wxFRAME_TOOL_WINDOW
childFrameStyle = wxCLIP_CHILDREN
# Should the palette be a menubar ('menu') or a notebook ('tabs')
paletteStyle = 'tabs'

# Alternating background colours used in ListCtrls (pastel blue and yellow)
pastels = 1
pastelMedium = wxColour(235, 246, 255)
pastelLight = wxColour(255, 255, 240)
## White and lightgray
##pastelMedium = wx.wxColour(234, 234, 234)
##pastelLight = wx.wxColour(255, 255, 255)

# Replace the standard file dialog with Boa's own dialog
useBoaFileDlg = 1

# Colour used to display uninitialised window space.
# A control must be placed in this space before valid code can be generated
undefinedWindowCol = wxColour(128, 0, 0)

# Info that will be filled into the comment block. (Edit->Add module info)
# Also used by setup.py
staticInfoPrefs = { 'Purpose':   '',
                    'Author':    '<Your name>',
                    'Copyright': '(c) <Your copyright>',
                    'Licence':   '<Your licence>',
                    'Email':     '<Your email>',
                  }

# Should modules be added to the application if it is the active Model when
# a module is created from the palette
autoAddToApplication = 1

# Load images from a singe file Image.archive (zip of Image directory)
useImageArchive = 0
# Only load image 1st time it is requested then cache it
# Turn this off to conserve resources on win9x
useImageCache = 1

# Flag for turning on special checking for european keyboard characters by
# checking for certain codes while ctrl alt is held.
handleSpecialEuropeanKeys = 0
# Country code for keyboards, options: 'euro', 'france', 'swiss-german' 
euroKeysCountry = 'euro'

# Auto correct indentation and EOL characters on load, save and refresh
# This only works for Python 2.0 and up
autoReindent = 0

# Redirect stderrout to logmessages
logStdStreams = 1
recordModuleCallPoint = 1

# Safety net so COM support has to be explicitly turned on
# Will stay here until the win9x crashes has been sorted out
blockCOM = 1

# Debugger to use, options: 'old', 'new'
useDebugger = 'old'

# Syntax checking
# Underlines possible syntax errors with a red squigly line
# Syntax is checked whwn the cursor moves off a line that was modified
checkSyntax = 1
# Only do syntax checking if cursor moves off line that was modified
onlyCheckIfLineModified = 1

# Path to an alternative Python Interpreter. By default (blank string) Boa
# will use the same interpreter it is running on
pythonInterpreterPath = ''
#pythonInterpreterPath = 'd:/progra~1/zope/2-3-1/bin/python.exe'

# Should the files open when closing Boa be reloaded at next startup?
rememberOpenFiles = 1
rememberOpenApps = 0

#-Inspector---------------------------------------------------------------------

# Display properties for which source will be generated in Bold
showModifiedProps = 1
# Colour of property value static text ctrls
propValueColour = wxColour(0, 0, 100)
# Inspector row height
oiLineHeight = 18
# Default Inspector Names (1st coloumn) width
oiNamesWidth = 100
# Inspector notebook style flags
# 16 (FxdWdth), 32 (lft), 64 (rght), 128 (btm)
inspNotebookFlags = 0 
# Should the stderr and stdout notebook be hosted in the inspector?
showErrOutInInspector = 1
##inspPageNames = {'Constr': 'Constructor',
##                 'Props': 'Properties',
##                 'Evts': 'Events',
##                 'Objs': 'Objects'}
#Smaller version if you don't have have high enough res
inspPageNames = {'Constr': 'Constr',
                 'Props': 'Props',
                 'Evts': 'Evts',
                 'Objs': 'Objs'}

# Shell prompt (must be 3 chars with trailing space)'
ps1 = '>>> '
# Shell prompt, continued line (must be 3 chars with trailing space)'
ps2 = '... '
# Shell debug prompt (must be 3 chars with trailing space)'
#ps3 = '>-> '
# Shell prompt, standard input request (must be 3 chars with trailing space)
ps4 = '<<< '

# Try to update the wxPython.libs directory with the newest run time libs (Component files)
installBCRTL = 1

#----Editable preferences-------------------------------------------------------
exportedProperties = ['flatTools', 'childFrameStyle', 'paletteStyle',
  'pastels', 'pastelMedium', 'pastelLight', 
  'useBoaFileDlg', 'undefinedWindowCol', 'autoAddToApplication',
  'useImageArchive',  'handleSpecialEuropeanKeys', 'euroKeysCountry', 
  'autoReindent', 'logStdStreams', 'recordModuleCallPoint', 'blockCOM', 
  'useDebugger',
  'checkSyntax', 'onlyCheckIfLineModified', 'pythonInterpreterPath', 
  'rememberOpenFiles', 'showModifiedProps', 'propValueColour', 
  'oiLineHeight', 'oiNamesWidth', 'inspNotebookFlags', 'showErrOutInInspector', 
  'ps1', 'ps2', 'ps4']
