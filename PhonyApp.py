#----------------------------------------------------------------------
# Name:        PhonyApp.py
# Purpose:     To impersonate a second wxApp for the debugger or
#              profiler because there may only be one per process
#
# Author:      Riaan Booysen
#
# Created:     2000/01/15
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
true = 1
false = 0
import time

class wxBasePhonyApp:
    inMainLoop = false
    def __init__(self, flag = 0):
        self.inMainLoop = true
        self.OnInit()
    def GetAppName(self, *_args, **_kwargs):
        pass
    def GetAuto3D(self, *_args, **_kwargs):
        pass
    def GetClassName(self, *_args, **_kwargs):
        pass
    def GetExitOnFrameDelete(self, *_args, **_kwargs):
        pass
    def GetPrintMode(self, *_args, **_kwargs):
        pass
    def GetTopWindow(self, *_args, **_kwargs):
        pass
    def GetVendorName(self, *_args, **_kwargs):
        pass
    def Dispatch(self, *_args, **_kwargs):
        pass
    def ExitMainLoop(self, *_args, **_kwargs):
        pass
    def Initialized(self, *_args, **_kwargs):
        pass
    def MainLoop(self, *_args, **_kwargs):
##      print 'PhonyApp enter mainloop'
        pass
    def Pending(self, *_args, **_kwargs):
        pass
    def ProcessIdle(self, *_args, **_kwargs):
        pass
    def SetAppName(self, *_args, **_kwargs):
        pass
    def SetAuto3D(self, *_args, **_kwargs):
        pass
    def SetClassName(self, *_args, **_kwargs):
        pass
    def SetExitOnFrameDelete(self, *_args, **_kwargs):
        pass
    def SetPrintMode(self, *_args, **_kwargs):
        pass
    def SetTopWindow(self, *_args, **_kwargs):
        pass
    def SetVendorName(self, *_args, **_kwargs):
        pass
    def GetStdIcon(self, *_args, **_kwargs):
        pass
    def __repr__(self):
        return "<wxPhonyApp instance at %d>" % (self.id,)

class wxPhonyApp(wxBasePhonyApp):
    def MainLoop(self, *_args, **_kwargs):
        while self.inMainLoop:
            self.Dispatch()
            self.debugger.startMainLoop()
            self.debugger.stopMainLoop()

        print 'quiting from Phony app'
        self.quit = true

    def OnInit(self):
        pass

class wxProfilerPhonyApp(wxBasePhonyApp):
    def MainLoop(self, *_args, **_kwargs):
#        while self.inMainLoop:
        self.realApp.Dispatch()
