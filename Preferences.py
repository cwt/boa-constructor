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
#import wxSystemSettings_GetSystemMetric, wxSYS_SCREEN_X, wxSYS_SCREEN_Y, wxTB_FLAT
#from wxPython.wx import wxPlatform, wxDefaultSize, wxDefaultPosition, wxSize, wxColour
from ImageStore import ImageStore

try:
    import win32api, win32con
except ImportError:
    # thnx Mike Fletcher
    screenWidth = int(wx.wxSystemSettings_GetSystemMetric(wx.wxSYS_SCREEN_X) * 1.0)
    screenHeight = int(wx.wxSystemSettings_GetSystemMetric(wx.wxSYS_SCREEN_Y) * 0.89)
else:
    screenWidth = win32api.GetSystemMetrics(win32con.SM_CXFULLSCREEN)
    screenHeight = win32api.GetSystemMetrics(win32con.SM_CYFULLSCREEN) + 20
    
inspWidth = screenWidth * (1/3.75)
edWidth = screenWidth - inspWidth + 1

if wx.wxPlatform == '__WXMSW__':
    from PrefsMSW import *
    wxDefaultFramePos = wx.wxDefaultPosition
    wxDefaultFrameSize = wx.wxDefaultSize
elif wx.wxPlatform == '__WXGTK__':
    from PrefsGTK import *
    wxDefaultFramePos = wx.wxSize(screenWidth / 4, screenHeight / 4)
    wxDefaultFrameSize = wx.wxSize(screenWidth / 2, screenHeight / 2)

bottomHeight = screenHeight - paletteHeight

flatTools = wx.wxTB_FLAT # 0

pastels = 1
pastelMedium = wx.wxColour(235, 246, 255)
pastelLight = wx.wxColour(255, 255, 240)

useBoaFileDlg = 1

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


def reassignFileDlg():
    import FileDlg
    wx.wxFileDialog = FileDlg.wxBoaFileDialog
    
if useBoaFileDlg:
    import FileDlg
    wxFileDialog = FileDlg.wxBoaFileDialog
    del FileDlg
else:
    wxFileDialog = wx.wxFileDialog
