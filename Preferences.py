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
import os, sys, shutil, string

from wxPython import wx

from ImageStore import ImageStore, ZippedImageStore

#---Paths-----------------------------------------------------------------------

pyPath = os.path.abspath(os.path.join(os.getcwd(), sys.path[0]))

def toPyPath(filename):
    return os.path.join(pyPath, filename)

#---Import preference namespace from resource .rc. files------------------------

rcPath = os.path.join(os.environ.get('HOME', pyPath), '.boa')
# fall back to defaults in Boa src if .boa does not exist
if not os.path.isdir(rcPath):
    rcPath = pyPath

plat = wx.wxPlatform == '__WXMSW__' and 'msw' or 'gtk'
for prefsFile in ('prefs.rc.py', 'prefs.%s.rc.py' % plat, 'prefskeys.rc.py'):
    file = os.path.join(rcPath, prefsFile)
    if not os.path.exists(file):
        shutil.copy2(os.path.join(pyPath, prefsFile), file)

    exec string.strip(open(file).read())

file = os.path.join(rcPath, 'Explorer.%s.cfg' % plat)
if not os.path.exists(file):
    shutil.copy2(os.path.join(pyPath, 'Explorer.%s.cfg' % plat), file)

#---Prefs dependent on user prefs-----------------------------------------------

if useImageArchive:
    IS = ZippedImageStore(pyPath, 'Images.archive', useImageCache)
else:
    IS = ImageStore(pyPath, cache=useImageCache)

if useBoaFileDlg:
    import FileDlg
    wxFileDialog = FileDlg.wxBoaFileDialog
    del FileDlg
else:
    wxFileDialog = wx.wxFileDialog

# Ugly but temporary
if useDebugger == 'old':
    from Debugger import OldDebugger
    Debugger = OldDebugger
    del OldDebugger
elif useDebugger == 'new':
    from Debugger import Debugger

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
    wxDefaultFramePos = wx.wxDefaultPosition
    wxDefaultFrameSize = wx.wxDefaultSize
elif wx.wxPlatform == '__WXGTK__':
    wxDefaultFramePos = (screenWidth / 4, screenHeight / 4)
    wxDefaultFrameSize = (round(screenWidth / 1.5), round(screenHeight / 1.5))

inspWidth = screenWidth * (1/3.75) - windowManagerSide * 2
edWidth = screenWidth - inspWidth + 1 - windowManagerSide * 4
paletteHeight = paletteHeights[paletteStyle]
bottomHeight = screenHeight - paletteHeight
 