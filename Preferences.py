#----------------------------------------------------------------------
# Name:        Preferences.py
# Purpose:     Global settings
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
import os, sys
from os import path

from wxPython import wx

from ImageStore import ImageStore, ZippedImageStore

#-Window sizes------------------------------------------------------------------
wx_screenWidthPerc = 1.0
if wx.wxPlatform == '__WXMSW__':
    wx_screenHeightPerc = 0.91
else:
    wx_screenHeightPerc = 0.87

w32_screenHeightOffset = 20
try:
    import win32api, win32con
except ImportError:
    # thnx Mike Fletcher
    screenWidth = int(wx.wxSystemSettings_GetSystemMetric(wx.wxSYS_SCREEN_X) * wx_screenWidthPerc)
    screenHeight = int(wx.wxSystemSettings_GetSystemMetric(wx.wxSYS_SCREEN_Y) * wx_screenHeightPerc)
else:
    screenWidth = win32api.GetSystemMetrics(win32con.SM_CXFULLSCREEN)
    screenHeight = win32api.GetSystemMetrics(win32con.SM_CYFULLSCREEN) + w32_screenHeightOffset

if wx.wxPlatform == '__WXMSW__':
    from PrefsMSW import *
    wxDefaultFramePos = wx.wxDefaultPosition
    wxDefaultFrameSize = wx.wxDefaultSize
elif wx.wxPlatform == '__WXGTK__':
    from PrefsGTK import *
    wxDefaultFramePos = (screenWidth / 4, screenHeight / 4)
    wxDefaultFrameSize = (round(screenWidth / 1.5), round(screenHeight / 1.5))

inspWidth = screenWidth * (1/3.75) - windowManagerSide * 2
edWidth = screenWidth - inspWidth + 1 - windowManagerSide * 4

bottomHeight = screenHeight - paletteHeight

#-Miscellaneous-----------------------------------------------------------------

# Should toolbars have flat buttons
flatTools = wx.wxTB_FLAT # 0
# Frame style for child windows of the main frame
childFrameStyle = wx.wxCLIP_CHILDREN

# Alternating background colours used in ListCtrls
pastels = 1
pastelMedium = wx.wxColour(235, 246, 255)
pastelLight = wx.wxColour(255, 255, 240)

# Replace the standard file dialog with Boa's own dialog
useBoaFileDlg = 1

# Colour used to display uninitialised window space.
# A control must be placed in this space before valid code can be generated
undefinedWindowCol = wx.wxColour(128, 0, 0)

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

# Load images from a singe image archive (zip of image directory)
useImageArchive = 0
# Only load image 1st time it is requested then cache it
# Turn this off to conserve resources on win9x
useImageCache = 1

# Flag for turning on special checking for european keyboard characters by
# checking for certain codes while ctrl alt is held.
handleSpecialEuropeanKeys = 1
# Country code for keyboards, options: 'euro', 'france'
euroKeysCountry = 'france'

# Auto correct indentation and EOL characters on load, save and refresh
# This only works for Python 2.0 and up
autoReindent = 0

# Redirect stderrout to logmessages
logStdStreams = 1
recordModuleCallPoint = 1

# Safety net so COM support has to be explicitly turned on
# Will stay here until the win9x crashes has been sorted out
blockCOM = 1

# Syntax checking
# Underlines possible syntax errors with a red squigly line
# Syntax is checked whwn the cursor moves off a line that was modified
checkSyntax = 1
onlyCheckIfLineModified = 1

# Path to an alternative Python Interpreter. By default (blank string) Boa
# will use the same interpreter it is running on
pythonInterpreterPath = ''
#pythonInterpreterPath = 'd:/progra~1/zope/2-3-1/bin/python.exe'

# Should the files open when closing Boa be reloaded at next startup
rememberOpenFiles = 1
rememberOpenApps = 0

#-Inspector---------------------------------------------------------------------

# Display properties for which source will be generated in Bold
showModifiedProps = 1
# Inspector row height
oiLineHeight = 18
# Default Inspector Names (1st coloumn) width
oiNamesWidth = 100
inspNotebookFlags = 0 #32
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

# Try to update the wxPython.libs directory with the newest run time libs (Component files)
installBCRTL = 1

#---Other-----------------------------------------------------------------------

pyPath = path.abspath(path.join(os.getcwd(), sys.path[0]))
if useImageArchive:
    IS = ZippedImageStore(pyPath, 'Images.archive', useImageCache)
else:
    IS = ImageStore(pyPath, cache=useImageCache)

def toPyPath(filename):
    return path.join(pyPath, filename)

def toWxDocsPath(filename):
    return path.join(wxWinDocsPath, filename)

if useBoaFileDlg:
    import FileDlg
    wxFileDialog = FileDlg.wxBoaFileDialog
    del FileDlg
else:
    wxFileDialog = wx.wxFileDialog

exportedProperties = ['flatTools', 'childFrameStyle', 'pastels', 'pastelMedium', 
  'pastelLight', 'useBoaFileDlg', 'undefinedWindowCol', 'autoAddToApplication',
  'useImageArchive',  'handleSpecialEuropeanKeys', 'euroKeysCountry', 
  'autoReindent', 'logStdStreams', 'recordModuleCallPoint', 'blockCOM', 
  'checkSyntax', 'onlyCheckIfLineModified', 'pythonInterpreterPath', 
  'rememberOpenFiles', 'showModifiedProps', 'oiLineHeight', 'oiNamesWidth', 
  'inspNotebookFlags', 'ps1', 'ps2' ]
