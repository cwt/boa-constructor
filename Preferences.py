#----------------------------------------------------------------------
# Name:        Preferences.py
# Purpose:     Global settings. Populated by resource files *.rc.py
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2006 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

""" The global preferences module shared by most Boa modules.

This namespace is populated by *.rc.py files from the selected
resource configuration.

The resource config files are version checked and updated from the
resource config files in Config (so that a CVS updated schema will
override old settings in external resource config directories.

Application, Plug-ins and Image paths are initialised and the global ImageStore
is configured.

"""

import os, sys, shutil

import wx

#---Paths-----------------------------------------------------------------------

#pyPath = sys.path[0] = os.path.abspath(sys.path[0])
#sys.path.insert(1, '')
if getattr(sys, "frozen", None):
    pyPath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
else:
    pyPath = os.path.abspath(os.path.dirname(__file__))

#---Import preference namespace from resource .rc. files------------------------

print 'reading user preferences'

# This cannot be stored as a Preference option for obvious reasons :)
prefsDirName = '.boa-constructor'
if '--OverridePrefsDirName' in sys.argv or '-O' in sys.argv:
    try: idx = sys.argv.index('--OverridePrefsDirName')
    except ValueError:
        try: idx = sys.argv.index('-O')
        except ValueError: idx = -1

    if idx != -1:
        try: prefsDirName = sys.argv[idx + 1]
        except IndexError: raise Exception, 'OverridePrefsDirName must specify a directory'
        print 'using preference directory name', prefsDirName

# To prevent using the HOME env variable run different versions of Boa this flag
# forces Boa to use Preference settings either in the Config dir or in a 
# specified rc path
if os.path.isabs(prefsDirName):
    rcPath = prefsDirName
elif '--BlockHomePrefs' in sys.argv or '-B' in sys.argv:
    print 'ignoring $HOME (if set)'
    rcPath = os.path.join(pyPath, prefsDirName)
else:
    homeDir = os.environ.get('HOMEPATH', None)
    if homeDir is not None:
        homeDir = os.environ['HOMEDRIVE']+homeDir
    else:
        homeDir = os.environ.get('HOME', None)
        
    if homeDir is not None and os.path.isdir(homeDir):
        rcPath = os.path.join(homeDir, prefsDirName)
        for fn in ('', 'docs-cache', 'Plug-ins'):
            if fn:
                pth = os.path.join(rcPath, fn)
            else:
                pth = rcPath

            if not os.path.isdir(pth):
                try:
                    os.mkdir(pth)
                    print 'Created directory: %s' % pth
                except OSError:
                    # Protected
                    pass
    else:
        rcPath = os.path.join(pyPath, prefsDirName)

# fall back to defaults in Config root if .boa-constructor is not available.
if not os.path.isdir(rcPath):
    rcPath = os.path.join(pyPath, 'Config')

# no editors for these settings yet, can be redefined in prefs.rc.py if needed
# e.g. wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, 'Courier New')
eoErrOutFont = wx.NORMAL_FONT


wxPlatforms = {'__WXMSW__': 'msw',
               '__WXGTK__': 'gtk',
               '__WXMAC__': 'mac'}
thisPlatform = wxPlatforms[wx.Platform]

# upgrade if needed and exec in our namespace
for prefsFile, version in (('prefs.rc.py', 18),
                           ('prefs.%s.rc.py'%thisPlatform, 9),
                           ('prefs.keys.rc.py', 10),
                           ('prefs.plug-ins.rc.py', None)):
    file = os.path.join(rcPath, prefsFile)

    # first time, install to env dir
    if not os.path.exists(file):
        shutil.copy2(os.path.join(pyPath, 'Config', prefsFile), file)
    # check version
    else:
        if version is not None:
            verline = open(file).readline().strip()
    
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
                shutil.copy2(os.path.join(pyPath, 'Config', prefsFile), file)
                print 'Preference file %s replaced, previous version backed up to %s'%(
                      file, bkfile)

    execfile(file)

for file in ('Explorer.%s.cfg' % thisPlatform, 'stc-styles.rc.cfg'):
    rcFile = os.path.join(rcPath, file)
    if not os.path.exists(rcFile):
        shutil.copy2(os.path.join(pyPath, 'Config', file), rcFile)

pluginPaths = []
pluginSections = []

installedPlugins = []
failedPlugins = {}
if pluginsEnabled:
    pluginPaths.append(os.path.join(pyPath, 'Plug-ins'))
    pluginSections.append('plug-ins.root')
    # Library plugin path
    if extraPluginsPath:
        pluginPaths.append(extraPluginsPath)
        pluginSections.append('plug-ins.extra')
    # User plugin path
    if rcPath != pyPath and os.path.isdir(os.path.join(rcPath, 'Plug-ins')):
        pluginPaths.append(os.path.join(rcPath, 'Plug-ins'))
        pluginSections.append('plug-ins.home')

#---Prefs dependent on user prefs-----------------------------------------------

imageStorePaths = [pyPath]
if hasattr(sys, 'frozen'):
    imageStorePaths.append(sys.executable)
for ppth in pluginPaths:
    imageStorePaths.append(ppth)

import ImageStore

IS = ImageStore.ImageStoreClasses[imageStoreType](imageStorePaths, cache=useImageCache)

def getPythonInterpreterPath():
    if not pythonInterpreterPath:
        if hasattr(sys, 'frozen'):
            from Utils import _
            raise Exception, _('No python interpreter defined')
        else:
            return sys.executable
    else:
        return pythonInterpreterPath

#-Window size calculations------------------------------------------------------

# thnx Mike Fletcher
screenWidth = screenHeight = wxDefaultFramePos = wxDefaultFrameSize = \
    edWidth = inspWidth = paletteHeight = bottomHeight = underPalette = \
    oglBoldFont = oglStdFont = None

def initScreenVars():
    global screenWidth, screenHeight, wxDefaultFramePos, wxDefaultFrameSize
    global edWidth, inspWidth, paletteHeight, bottomHeight, underPalette
    global oglBoldFont, oglStdFont 
    
    screenWidth = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
    screenHeight = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)
    if wx.Platform == '__WXMSW__':
        _x, _y, screenWidth, screenHeight = wx.GetClientDisplayRect()
        screenHeight -= topMenuHeight
    else:
        # handle dual monitors on Linux
        if screenWidth / screenHeight >= 2:
            screenWidth = screenWidth / 2
    
        screenWidth = int(screenWidth - verticalTaskbarWidth)
        screenHeight = int(screenHeight - horizontalTaskbarHeight - topMenuHeight)
    
    if wx.Platform == '__WXMSW__':
        wxDefaultFramePos = wx.DefaultPosition
        wxDefaultFrameSize = wx.DefaultSize
    else:
        wxDefaultFramePos = (screenWidth / 4, screenHeight / 4)
        wxDefaultFrameSize = (int(round(screenWidth / 1.5)), int(round(screenHeight / 1.5)))
    
    edWidth = int(screenWidth * editorScreenWidthPerc - windowManagerSide * 2)
    inspWidth = screenWidth - edWidth + 1 - windowManagerSide * 4
    paletteHeight = paletteHeights[paletteStyle]
    bottomHeight = screenHeight - paletteHeight
    underPalette = paletteHeight + windowManagerTop + windowManagerBottom + topMenuHeight

    if wx.Platform == '__WXMSW__':
        oglBoldFont = wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.BOLD, False)
        oglStdFont = wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)
    else:
        oglBoldFont = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, False)
        oglStdFont = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)


paletteTitle = 'Boa Constructor'


#-------------------------------------------------------------------------------
# Delays wxApp_Cleanup
#try: sys._wxApp_Cleanup = wx.__cleanMeUp
#except: pass

def cleanup():
    IS.cleanup()
##    g = globals()
##    cleanWxClasses = (wxColourPtr, wxPointPtr, wxSizePtr, wxFontPtr,
##                      wxPenPtr, wxBrushPtr, wxPen, wxBrush)
##    for k, v in g.items():
##        if hasattr(wx, k):
##            continue
##        for Class in cleanWxClasses:
##            if isinstance(v, Class):
##                g[k] = None
##                break

    import PaletteMapping
    PaletteMapping._NB = None
    PM = PaletteMapping.PaletteStore
    PM.helperClasses = {}
    PM.compInfo = {}
    PM.newControllers = {}

#-------------------------------------------------------------------------------
