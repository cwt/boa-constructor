#----------------------------------------------------------------------
# Name:        Preferences.py
# Purpose:     Global settings. Populated by resource files *.rc.py
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2001 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
import os, sys, shutil, string

from wxPython import wx

#---Paths-----------------------------------------------------------------------

try:
    pyPath = os.path.dirname(__file__)
    # handle case where not a pyc and in current dir
    if not pyPath: pyPath = os.path.abspath('')
except AttributeError:
    pyPath = os.path.abspath(os.path.join(os.getcwd(), sys.path[0]))

def toPyPath(filename):
    return os.path.join(pyPath, filename)

#---Import preference namespace from resource .rc. files------------------------

print 'Setting user preferences'

rcPath = os.path.join(os.environ.get('HOME', pyPath), '.boa')
# fall back to defaults in Boa src if .boa does not exist
if not os.path.isdir(rcPath):
    rcPath = pyPath

# upgrade if needed and exec in our namespace
plat = wx.wxPlatform == '__WXMSW__' and 'msw' or 'gtk'
for prefsFile, version in (('prefs.rc.py', 1), 
                           ('prefs.%s.rc.py'%plat, 1), 
                           ('prefskeys.rc.py', 1)):
    file = os.path.join(rcPath, prefsFile)
    
    # first time, install to env dir
    if not os.path.exists(file):
        shutil.copy2(os.path.join(pyPath, prefsFile), file)
    # check version
    else:
        verline = string.strip(open(file).readline())
        
        if len(verline) >= 14 and verline[:14] == '## rc-version:':
            rcver = int(verline[14:-2])
        else:
            rcver = 0
        if rcver < version:
            # backup and copy newest
            bkno=0;bkstr=''
            while 1:
                bkfile = os.path.splitext(file)[0]+'.py~'+bkstr
                try:
                    os.rename(file, bkfile)
                except OSError, err:
                    if err.errno != 17: raise
                    bkno=bkno+1;bkstr=str(bkno)
                else:
                    break    
            shutil.copy2(os.path.join(pyPath, prefsFile), file)
            print 'Preference file %s replaced, previous version backed up to %s'%(
                  file, bkfile)

    data = open(file).read()

    exec string.strip(data)

for file in ('Explorer.%s.cfg' % plat, 'stc-styles.rc.cfg'):
    rcFile = os.path.join(rcPath, file)
    if not os.path.exists(rcFile):
        shutil.copy2(os.path.join(pyPath, file), rcFile)


#---Prefs dependent on user prefs-----------------------------------------------

from ImageStore import ImageStore, ZippedImageStore

if useImageArchive:
    IS = ZippedImageStore(pyPath, 'Images.archive', useImageCache)
else:
    IS = ImageStore(pyPath, cache=useImageCache)

import FileDlg
wxFileDialog = FileDlg.wxBoaFileDialog
del FileDlg

# If user does not override interpreter, use own interpreter path    
if not pythonInterpreterPath:
    pythonInterpreterPath = sys.executable

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
