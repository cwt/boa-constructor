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
from wxPython.wx import wxSystemSettings_GetSystemMetric, wxSYS_SCREEN_X, wxSYS_SCREEN_Y, wxTB_FLAT
from wxPython.wx import wxPlatform, wxDefaultSize, wxDefaultPosition
from ImageStore import ImageStore

try:
    import win32api, win32con
except ImportError:
    # thnx Mike Fletcher
    screenWidth = int(wxSystemSettings_GetSystemMetric(wxSYS_SCREEN_X) * 1.0)
    screenHeight = int(wxSystemSettings_GetSystemMetric(wxSYS_SCREEN_Y) * 0.94)
else:
    screenWidth = win32api.GetSystemMetrics(win32con.SM_CXFULLSCREEN)
    screenHeight = win32api.GetSystemMetrics(win32con.SM_CYFULLSCREEN) + 20
    
inspWidth = screenWidth * (1/3.75)
edWidth = screenWidth - inspWidth + 1

if wxPlatform == '__WXMSW__':
    from PrefsMSW import *
    wxDefaultFramePos = wxDefaultPosition
    wxDefaultFrameSize = wxDefaultSize
elif wxPlatform == '__WXGTK__':
    from PrefsGTK import *
    wxDefaultFramePos = (screenWidth / 4, screenHeight / 4)
    wxDefaultFrameSize = (screenWidth / 2, screenHeight / 2)

bottomHeight = screenHeight - paletteHeight

flatTools = wxTB_FLAT # 0

pastels = 1

braceHighLight = 0

oiLineHeight = 18
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

staticInfoPrefs = { 'Purpose':   '',
                    'Author':    'Riaan Booysen',
                    'Copyright': '(c) 1999, 2000 Riaan Booysen',
                    'Licence':   'GPL'}

pyPath = path.abspath(path.join(os.getcwd(), sys.path[0]))

IS = ImageStore(pyPath)

def toPyPath(filename):
    return path.join(pyPath, filename)

def toWxDocsPath(filename):
    return path.join(wxWinDocsPath, filename)
    
    
    
    
    
    
    
    
    
    
    
    