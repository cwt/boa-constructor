#----------------------------------------------------------------------
# Name:        Preferences.py
# Purpose:     Global settings. Populated by resource files *.rc.py
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2002 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
import os, sys, shutil, string

from wxPython import wx

#---Paths-----------------------------------------------------------------------

pyPath = sys.path[0]
if not pyPath: pyPath = os.path.abspath('')

def toPyPath(filename):
    return os.path.join(pyPath, filename)

#---Import preference namespace from resource .rc. files------------------------

print 'setting user preferences'

# This cannot be stored as a Preference option for obvious reasons :)
prefsDirName = '.boa'
if '--OverridePrefsDirName' in sys.argv or '-O' in sys.argv:
    try: idx = sys.argv.index('--OverridePrefsDirName')
    except ValueError:
        try: idx = sys.argv.index('-O')
        except ValueError: idx = -1
            
    if idx != -1:
        try: prefsDirName = sys.argv[idx + 1]
        except IndexError: raise 'OverridePrefsDirName must specify a directory'
        print 'using preference directory name', prefsDirName

# To prevent using the HOME env variable run different versions of Boa this flag forces Boa to user Preference
# settings either in the Boa root or in a .boa dir in the Boa root
if '--BlockHomePrefs' in sys.argv or '-B' in sys.argv:
    ##del os.environ['HOME']
    print 'ignoring $HOME (if set)'
    rcPath = os.path.join(pyPath, prefsDirName)
else:
    rcPath = os.path.join(os.environ.get('HOME', pyPath), prefsDirName)

# fall back to defaults in Boa src root if .boa does not exist
if not os.path.isdir(rcPath):
    rcPath = pyPath

# upgrade if needed and exec in our namespace
plat = wx.wxPlatform == '__WXMSW__' and 'msw' or 'gtk'
for prefsFile, version in (('prefs.rc.py', 3),
                           ('prefs.%s.rc.py'%plat, 3),
                           ('prefskeys.rc.py', 3)):
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

    execfile(file)

for file in ('Explorer.%s.cfg' % plat, 'stc-styles.rc.cfg'):
    rcFile = os.path.join(rcPath, file)
    if not os.path.exists(rcFile):
        shutil.copy2(os.path.join(pyPath, file), rcFile)

pluginPaths = []
if pluginsEnabled:
    pluginPaths.append(pyPath+'/Plug-ins')
    # Library plugin path
    if extraPluginsPath:
        pluginPaths.append(extraPluginsPath)
    # User plugin path
    if rcPath != pyPath and os.path.isdir(rcPath+'/Plug-ins'):
        pluginPaths.append(rcPath +'/Plug-ins')


#---Prefs dependent on user prefs-----------------------------------------------

imageStorePaths = [pyPath]
for ppth in pluginPaths:
    imageStorePaths.append(ppth)
##    if useImageArchive and os.path.exists(pyPath+'/Images/Images.archive'):
##        imageStorePaths.append(ppth+'/Images')
##    else:
##    imageStorePaths.append(ppth)

import ImageStore 
if useImageArchive and os.path.exists(pyPath+'/Images/Images.archive'):
    IS = ImageStore.ZippedImageStore(pyPath+'/Images', 'Images.archive', useImageCache)
else:
    IS = ImageStore.ImageStore(imageStorePaths, cache=useImageCache)

import FileDlg
wxFileDialog = FileDlg.wxBoaFileDialog
del FileDlg

# If user does not override interpreter, use own interpreter path
if not pythonInterpreterPath:
    pythonInterpreterPath = sys.executable

#-Window size calculations------------------------------------------------------

try:
    import win32api, win32con
except ImportError:
    # thnx Mike Fletcher
    screenWidth =  wx.wxSystemSettings_GetSystemMetric(wx.wxSYS_SCREEN_X)
    screenHeight = wx.wxSystemSettings_GetSystemMetric(wx.wxSYS_SCREEN_Y)
    # handle dual monitors on Linux
    if wx.wxPlatform == '__WXGTK__' and screenWidth / screenHeight >= 2:
        screenWidth = screenWidth / 2
    screenWidth = int(screenWidth - verticalTaskbarWidth)
    screenHeight = int(screenHeight - horizontalTaskbarHeight)
else:
    screenWidth = win32api.GetSystemMetrics(win32con.SM_CXFULLSCREEN)
    screenHeight = win32api.GetSystemMetrics(win32con.SM_CYFULLSCREEN) + 20

if wx.wxPlatform == '__WXMSW__':
    wxDefaultFramePos = wx.wxDefaultPosition
    wxDefaultFrameSize = wx.wxDefaultSize
elif wx.wxPlatform == '__WXGTK__':
    wxDefaultFramePos = (screenWidth / 4, screenHeight / 4)
    wxDefaultFrameSize = (int(round(screenWidth / 1.5)), int(round(screenHeight / 1.5)))

edWidth = screenWidth * editorScreenWidthPerc - windowManagerSide * 2
inspWidth = screenWidth - edWidth + 1 - windowManagerSide * 4
paletteHeight = paletteHeights[paletteStyle]
bottomHeight = screenHeight - paletteHeight

if wxPlatform == '__WXGTK__':
    oglBoldFont = wxFont(12, wxDEFAULT, wxNORMAL, wxBOLD, false)
    oglStdFont = wxFont(10, wxDEFAULT, wxNORMAL, wxNORMAL, false)
else:
    oglBoldFont = wxFont(7, wxDEFAULT, wxNORMAL, wxBOLD, false)
    oglStdFont = wxFont(7, wxDEFAULT, wxNORMAL, wxNORMAL, false)

#-------------------------------------------------------------------------------
# Delays wxApp_Cleanup
sys._wxApp_Cleanup = wx.__cleanMeUp

def cleanup():
    IS.cleanup()
    g = globals()
    cleanWxClasses = (wxColourPtr, wxSizePtr, wxFontPtr)
    for k, v in g.items():
        if hasattr(wx, k):
            continue
        for Class in cleanWxClasses:
            if isinstance(v, Class):
                #print 'deleting %s'%k
                del g[k]
                break;

#-------------------------------------------------------------------------------
