from wxPython.wx import *
from wxPython.lib.activexwrapper import MakeActiveXClass
import win32com.client.gencache

IEModule = win32com.client.gencache.EnsureModule('{EAB22AC0-30C1-11CF-A7EB-0000C05BAE0B}', 0x0, 1, 1)
defaultNamedNotOptArg = IEModule.defaultNamedNotOptArg

[wxEVT_CWB_BEFORENAVIGATE, wxEVT_CWB_TITLECHANGE, wxEVT_CWB_DOWNLOADBEGIN,
 wxEVT_CWB_PROPERTYCHANGE, wxEVT_CWB_COMMANDSTATECHANGE, 
 wxEVT_CWB_FRAMEBEFORENAVIGATE, wxEVT_CWB_WINDOWACTIVATE, wxEVT_CWB_NEWWINDOW,
 wxEVT_CWB_DOWNLOADCOMPLETE, wxEVT_CWB_WINDOWRESIZE, wxEVT_CWB_WINDOWMOVE,
 wxEVT_CWB_PROGRESSCHANGE, wxEVT_CWB_FRAMENEWWINDOW, wxEVT_CWB_STATUSTEXTCHANGE,
 wxEVT_CWB_FRAMENAVIGATECOMPLETE, wxEVT_CWB_QUIT, wxEVT_CWB_NAVIGATECOMPLETE,
] = map(lambda _init_events: wxNewId(), range(17))

def EVT_CWB_BEFORENAVIGATE(win, func):
    win.Connect(-1, -1, wxEVT_CWB_BEFORENAVIGATE, func)
def EVT_CWB_TITLECHANGE(win, func):
    win.Connect(-1, -1, wxEVT_CWB_TITLECHANGE, func)
def EVT_CWB_DOWNLOADBEGIN(win, func):
    win.Connect(-1, -1, wxEVT_CWB_DOWNLOADBEGIN, func)
def EVT_CWB_PROPERTYCHANGE(win, func):
    win.Connect(-1, -1, wxEVT_CWB_PROPERTYCHANGE, func)
def EVT_CWB_COMMANDSTATECHANGE(win, func):
    win.Connect(-1, -1, wxEVT_CWB_COMMANDSTATECHANGE, func)
def EVT_CWB_FRAMEBEFORENAVIGATE(win, func):
    win.Connect(-1, -1, wxEVT_CWB_FRAMEBEFORENAVIGATE, func)
def EVT_CWB_WINDOWACTIVATE(win, func):
    win.Connect(-1, -1, wxEVT_CWB_WINDOWACTIVATE, func)
def EVT_CWB_NEWWINDOW(win, func):
    win.Connect(-1, -1, wxEVT_CWB_NEWWINDOW, func)
def EVT_CWB_DOWNLOADCOMPLETE(win, func):
    win.Connect(-1, -1, wxEVT_CWB_DOWNLOADCOMPLETE, func)
def EVT_CWB_WINDOWRESIZE(win, func):
    win.Connect(-1, -1, wxEVT_CWB_WINDOWRESIZE, func)
def EVT_CWB_WINDOWMOVE(win, func):
    win.Connect(-1, -1, wxEVT_CWB_WINDOWMOVE, func)
def EVT_CWB_PROGRESSCHANGE(win, func):
    win.Connect(-1, -1, wxEVT_CWB_PROGRESSCHANGE, func)
def EVT_CWB_FRAMENEWWINDOW(win, func):
    win.Connect(-1, -1, wxEVT_CWB_FRAMENEWWINDOW, func)
def EVT_CWB_STATUSTEXTCHANGE(win, func):
    win.Connect(-1, -1, wxEVT_CWB_STATUSTEXTCHANGE, func)
def EVT_CWB_FRAMENAVIGATECOMPLETE(win, func):
    win.Connect(-1, -1, wxEVT_CWB_FRAMENAVIGATECOMPLETE, func)
def EVT_CWB_QUIT(win, func):
    win.Connect(-1, -1, wxEVT_CWB_QUIT, func)
def EVT_CWB_NAVIGATECOMPLETE(win, func):
    win.Connect(-1, -1, wxEVT_CWB_NAVIGATECOMPLETE, func)

class wxComWebBrowserEvent(wxPyEvent):
    def __init__(self, eventType, evtArgs):
        wxPyEvent.__init__(self)
        self.SetEventType(eventType)
        self.__dict__.update(evtArgs)

def varnames2dict(varnames, locals):
    res = {}
    for name in varnames:
        res['m_'+name] = locals[name]
    return res

class wxComWebBrowserEvents:
    def __init__(self, eventhandler):
        self.eventhandler = eventhandler
    def OnBeforeNavigate(self, URL=defaultNamedNotOptArg, Flags=defaultNamedNotOptArg, TargetFrameName=defaultNamedNotOptArg, PostData=defaultNamedNotOptArg, Headers=defaultNamedNotOptArg, Cancel=defaultNamedNotOptArg):
        "Fired when a new hyperlink is being navigated to."
        wxPostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_BEFORENAVIGATE, varnames2dict(self.OnBeforeNavigate.im_func.func_code.co_varnames[1:], locals())))
    def OnTitleChange(self, Text=defaultNamedNotOptArg):
        "Document title changed."
        wxPostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_TITLECHANGE, varnames2dict(self.OnTitleChange.im_func.func_code.co_varnames[1:], locals())))
    def OnDownloadBegin(self):
        "Download of a page started."
        wxPostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_DOWNLOADBEGIN, varnames2dict(self.OnDownloadBegin.im_func.func_code.co_varnames[1:], locals())))
    def OnPropertyChange(self, Property=defaultNamedNotOptArg):
        "Fired when the PutProperty method has been called."
        wxPostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_PROPERTYCHANGE, varnames2dict(self.OnPropertyChange.im_func.func_code.co_varnames[1:], locals())))
    def OnCommandStateChange(self, Command=defaultNamedNotOptArg, Enable=defaultNamedNotOptArg):
        "The enabled state of a command changed"
        wxPostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_COMMANDSTATECHANGE, varnames2dict(self.OnCommandStateChange.im_func.func_code.co_varnames[1:], locals())))
    def OnFrameBeforeNavigate(self, URL=defaultNamedNotOptArg, Flags=defaultNamedNotOptArg, TargetFrameName=defaultNamedNotOptArg, PostData=defaultNamedNotOptArg, Headers=defaultNamedNotOptArg, Cancel=defaultNamedNotOptArg):
        "Fired when a new hyperlink is being navigated to in a frame."
        wxPostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_FRAMEBEFORENAVIGATE, varnames2dict(self.OnFrameBeforeNavigate.im_func.func_code.co_varnames[1:], locals())))
    def OnWindowActivate(self):
        "Fired when window has been activated."
        wxPostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_WINDOWACTIVATE, varnames2dict(self.OnWindowActivate.im_func.func_code.co_varnames[1:], locals())))
    def OnNewWindow(self, URL=defaultNamedNotOptArg, Flags=defaultNamedNotOptArg, TargetFrameName=defaultNamedNotOptArg, PostData=defaultNamedNotOptArg, Headers=defaultNamedNotOptArg, Processed=defaultNamedNotOptArg):
        "Fired when a new window should be created."
        wxPostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_NEWWINDOW, varnames2dict(self.OnNewWindow.im_func.func_code.co_varnames[1:], locals())))
    def OnDownloadComplete(self):
        "Download of page complete."
        wxPostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_DOWNLOADCOMPLETE, varnames2dict(self.OnDownloadComplete.im_func.func_code.co_varnames[1:], locals())))
    def OnWindowResize(self):
        "Fired when window has been sized."
        wxPostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_WINDOWRESIZE, varnames2dict(self.OnWindowResize.im_func.func_code.co_varnames[1:], locals())))
    def OnWindowMove(self):
        "Fired when window has been moved."
        wxPostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_WINDOWMOVE, varnames2dict(self.OnWindowMove.im_func.func_code.co_varnames[1:], locals())))
    def OnProgressChange(self, Progress=defaultNamedNotOptArg, ProgressMax=defaultNamedNotOptArg):
        "Fired when download progress is updated."
        wxPostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_PROGRESSCHANGE, varnames2dict(self.OnProgressChange.im_func.func_code.co_varnames[1:], locals())))
    def OnFrameNewWindow(self, URL=defaultNamedNotOptArg, Flags=defaultNamedNotOptArg, TargetFrameName=defaultNamedNotOptArg, PostData=defaultNamedNotOptArg, Headers=defaultNamedNotOptArg, Processed=defaultNamedNotOptArg):
        "Fired when a new window should be created."
        wxPostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_FRAMENEWWINDOW, varnames2dict(self.OnFrameNewWindow.im_func.func_code.co_varnames[1:], locals())))
    def OnStatusTextChange(self, Text=defaultNamedNotOptArg):
        "Statusbar text changed."
        wxPostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_STATUSTEXTCHANGE, varnames2dict(self.OnStatusTextChange.im_func.func_code.co_varnames[1:], locals())))
    def OnFrameNavigateComplete(self, URL=defaultNamedNotOptArg):
        "Fired when a new hyperlink is being navigated to in a frame."
        wxPostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_FRAMENAVIGATECOMPLETE, varnames2dict(self.OnFrameNavigateComplete.im_func.func_code.co_varnames[1:], locals())))
    def OnQuit(self, Cancel=defaultNamedNotOptArg):
        "Fired when application is quiting."
        wxPostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_CWB_QUIT, varnames2dict(self.OnQuit.im_func.func_code.co_varnames[1:], locals())))
    def OnNavigateComplete(self, URL=defaultNamedNotOptArg):
        "Fired when the document being navigated to becomes visible and enters the navigation stack."
        wxPostEvent(self.eventhandler, wxComWebBrowserEvent(wxEVT_NAVIGATECOMPLETE, varnames2dict(self.OnNavigateComplete.im_func.func_code.co_varnames[1:], locals())))

wxComWebBrowserPtr = MakeActiveXClass(IEModule.WebBrowser)
class wxComWebBrowser(wxComWebBrowserPtr):
    def __init__(self, parent = None, id = -1, pos=wxDefaultPosition, size=wxDefaultSize, style=0, name=''):
        wxComWebBrowserPtr.__init__(self, parent, id, pos, size, style)
        self._eventObj = wxComWebBrowserEvents(self)
        self.SetName(name)
