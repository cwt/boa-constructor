#----------------------------------------------------------------------
# Name:        Preferences.py
# Purpose:     
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
from wxPython.wx import wxSystemSettings_GetSystemMetric, wxSYS_SCREEN_X, wxSYS_SCREEN_Y
from wxPython.wx import wxPlatform, wxDefaultSize, wxDefaultPosition

#thnx Mike Fletcher        
screenWidth = wxSystemSettings_GetSystemMetric(wxSYS_SCREEN_X)
screenHeight = wxSystemSettings_GetSystemMetric(wxSYS_SCREEN_Y)

bottomSpace = screenHeight * (1/22.0)
inspWidth = screenWidth * (1/3.75)
edWidth = screenWidth - inspWidth

if wxPlatform == '__WXMSW__':
    from PrefsMSW import *
    wxDefaultFramePos = wxDefaultPosition
    wxDefaultFrameSize = wxDefaultSize
elif wxPlatform == '__WXGTK__':
    from PrefsGTK import *
    wxDefaultFramePos = (screenWidth / 4, screenHeight / 4)
    wxDefaultFrameSize = (screenWidth / 2, screenHeight / 2)

bottomHeight = screenHeight - paletteHeight - bottomSpace

pyPath = os.getcwd()

def toPyPath(filename):
    return path.join(pyPath, filename)

def toWxDocsPath(filename):
    return path.join(wxWinDocsPath, filename)


