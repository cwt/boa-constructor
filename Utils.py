#----------------------------------------------------------------------
# Name:        Utils.py
# Purpose:     General purpose functions and classes
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2001 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
import string, os
from types import InstanceType

from wxPython.wx import *

import Preferences
from Preferences import IS
from ExternalLib.ConfigParser import ConfigParser
# Why did I capitalise these ????

def ShowErrorMessage(parent, caption, mess):
    dlg = wxMessageDialog(parent, mess.__class__.__name__ +': '+`mess`,
                          caption, wxOK | wxICON_EXCLAMATION)
    try: dlg.ShowModal()
    finally: dlg.Destroy()

def ShowMessage(parent, caption, message, msgTpe = wxICON_INFORMATION):
    dlg = wxMessageDialog(parent, message, caption, wxOK | msgTpe)
    try: dlg.ShowModal()
    finally: dlg.Destroy()

def yesNoDialog(parent, title, question):
    dlg = wxMessageDialog(parent, question, title , wxYES_NO | wxICON_QUESTION)
    try: return (dlg.ShowModal() == wxID_YES)
    finally: dlg.Destroy()

def AddToolButtonBmpObject(frame, toolbar, thebitmap, hint, triggermeth, theToggleBitmap = wxNullBitmap):
    nId = wxNewId()
    doToggle = theToggleBitmap != wxNullBitmap
#    t = toolbar.AddTool(nId, thebitmap, toggleBitmap, shortHelpString = hint, toggle = toggleBitmap != wxNullBitmap)
    toolbar.AddTool(nId, thebitmap, theToggleBitmap, shortHelpString = hint)#, toggle = doToggle)
    EVT_TOOL(frame, nId, triggermeth)
    return nId

##def AddColMaskToolButtonBmpObject(frame, toolbar, thebitmap, hint, triggermeth,
##      theToggleBitmap=wxNullBitmap, theMaskColour=None):
##    nId = wxNewId()
##    doToggle = theToggleBitmap != wxNullBitmap
##    if theMaskColour:
##        thebitmap.SetMask(wxMaskColour(thebitmap, theMaskColour))
##    toolbar.AddTool(nId, thebitmap, theToggleBitmap, shortHelpString = hint)
##    EVT_TOOL(frame, nId, triggermeth)
##    return nId

def AddToolButtonBmpFile(frame, toolbar, filename, hint, triggermeth):
    return AddToolButtonBmpObject(frame, toolbar, IS.load(filename),
      hint, triggermeth)

def AddToolButtonBmpIS(frame, toolbar, name, hint, triggermeth, toggleBmp = ''):
    if toggleBmp:
        return AddToggleToolButtonBmpObject(frame, toolbar, IS.load(name), hint[:85], triggermeth)
    else:
        return AddToolButtonBmpObject(frame, toolbar, IS.load(name), hint[:85], triggermeth)

def AddToggleToolButtonBmpObject(frame, toolbar, thebitmap, hint, triggermeth):
    nId = wxNewId()
    toolbar.AddTool(nId, thebitmap, thebitmap, shortHelpString = hint, isToggle = true)
    EVT_TOOL(frame, nId, triggermeth)
    return nId

#This format follows wxWindows conventions
def windowIdentifier(frameName, ctrlName):
    return 'wxID_' + string.upper(frameName) + string.upper(ctrlName)


class BoaFileDropTarget(wxFileDropTarget):
    def __init__(self, editor):
        wxFileDropTarget.__init__(self)
        self.editor = editor

    def OnDropFiles(self, x, y, filenames):
        wxBeginBusyCursor()
        try:
            for filename in filenames:
                self.editor.openOrGotoModule(filename)
        finally:
            wxEndBusyCursor()

def split_seq(seq, pivot, transformFunc = None):
    result = []
    cur_sect = []
    for itm in seq:
        if transformFunc and transformFunc(itm) == pivot or itm == pivot:
            result.append(cur_sect)
            cur_sect = []
        else:
            cur_sect.append(itm)
    result.append(cur_sect)

    return result

allowed_width = 78
def human_split(line):
    indent = string.find(line, string.strip(line))

    # XXX use safe split, commas in quotes will break
    segments = string.split(line, ',')
    for idx in range(len(segments)-1):
        segments[idx] = segments[idx]+','

    result = []
    cur_line = ''
    for segment in segments:
        if indent + len(segment) > allowed_width:
            pass
        elif len(cur_line + segment) > allowed_width:
            result.append(cur_line)
            cur_line = ' ' * (indent + 2) + segment
#            print cur_line, indent + 2
        else:
            cur_line = cur_line + segment

    result.append(cur_line)

    return result

def duplicateMenu(source):
    """ Create an duplicate of a menu (does not do sub menus)"""
    dest = wxMenu()
    for menu in source.GetMenuItems():
        if menu.IsSeparator():
            dest.AppendSeparator()
        else:
            dest.Append(menu.GetId(), menu.GetText(), menu.GetHelp(), menu.IsCheckable())
            mi = dest.FindItemById(menu.GetId())
            if menu.IsCheckable() and menu.IsChecked():
                mi.Check(true)
    return dest

def getValidName(usedNames, baseName, ext = '', n = 1, itemCB = lambda x:x):
    def tryName(baseName, ext, n):
        return '%s%d%s' %(baseName, n, ext and '.'+ext)
    while filter(lambda key, name = tryName(baseName, ext, n), itemCB = itemCB: \
                 itemCB(key) == name, usedNames): n = n + 1
    return tryName(baseName, ext, n)

def srcRefFromCtrlName(ctrlName):
    return ctrlName and 'self.'+ctrlName or 'self'

def ctrlNameFromSrcRef(srcRef):
    return srcRef == 'self' and '' or srcRef[5:]

def winIdRange(count):
    return map(lambda x: wxNewId(), range(count))
wxNewIds = winIdRange

def methodLooksLikeEvent(method):
    return len(method) >= 3 and method[:2] == 'On' and method[2] in string.uppercase

def startswith(str, substr):
    return len(str) >= len(substr) and str[:len(substr)] == substr

ws2s = string.maketrans(string.whitespace, ' '*len(string.whitespace))
def whitespacetospace(str):
    return string.translate(str, ws2s)

##tst_str = ' 1\t\n 3'
##print `whitespacetospace(tst_str)`

class PaintEventHandler(wxEvtHandler):
    """ This class is used to merge paint requests.

        Each paint is captured and saved. Later on the idle event,
        the non-duplicated paints are executed. The code attempts to be
        efficient by determining the enclosing rectangle where multiple
        rectangles intersect.
        This is required only on GTK systems.

        Note: there is an assumption here that event handling is synchronous
        i.e. the paints called from the idle event handler are processed
        before the Refresh() call returns.
    """

    def __init__(self, window):
        wxEvtHandler.__init__(self)
        self.painting=0
        self.updates=[]
        self.window = window
        window.PushEventHandler(self)
        EVT_PAINT(self, self.OnPaint)
        EVT_IDLE(self, self.OnIdle)
    def OnPaint(self, event):
        if self.painting == 1:
            event.Skip()
            return
        newRect = self.window.GetUpdateRegion().GetBox()
        newList=[]
        for rect in self.updates:
            if self.RectanglesOverlap(rect, newRect):
                newRect = self.MergeRectangles(rect,newRect)
            else:
                newList.append(rect)
        self.updates = newList
        self.updates.append(newRect)
        event.Skip()
    def OnIdle(self, event):
        if len(self.updates) == 0:
            event.Skip()
            if len(self.updates) > 0:
                self.RequestMore()
            return
        self.painting=1
        for rect in self.updates:
            self.window.Refresh(0, rect)
        self.updates=[]
        self.painting=0
        event.Skip()
    def RectanglesOverlap(self, rect1, rect2):
        " Returns 1 if Rectangles overlap, 0 otherwise "
        if rect1.x > rect2.x + rect2.width : return 0
        if rect1.y > rect2.y + rect2.height : return 0
        if rect1.x + rect1.width < rect2.x : return 0
        if rect1.y + rect1.height < rect2.y : return 0
        return 1
    def MergeRectangles(self, rect1, rect2):
        " Returns a rectangle containing both rect1 and rect2"
        if rect1.x < rect2.x:
            x=rect1.x
            if x+rect1.width > rect2.x + rect2.width:
                width = rect1.width
            else:
                width = rect2.x + rect2.width - rect1.x
        else:
            x=rect2.x
            if x+rect2.width > rect1.x + rect1.width:
                width = rect2.width
            else:
                width = rect1.x + rect1.width - rect2.x
        if rect1.y < rect2.y:
            y=rect1.y
            if y+rect1.height > rect2.y + rect2.height:
                height = rect1.height
            else:
                height = rect2.y + rect2.height - rect1.y
        else:
            y=rect2.y
            if y+rect2.height > rect1.y + rect1.height:
                height = rect2.height
            else:
                height = rect1.y + rect1.height - rect2.y
        rv = wxRect(x, y, width, height)
        return rv

def showTip(frame, forceShow = 0):
    """ Displays tip of the day.

    Driven from and updates config file
    """
    try:
        conf = createAndReadConfig('Explorer')
    except IOError:
        conf = None
        showTip, index = (1, 0)
    else:
        showTip = conf.getint('tips', 'showonstartup')
        index = conf.getint('tips', 'tipindex')

    if showTip or forceShow:
        tp = wxCreateFileTipProvider(Preferences.toPyPath('Docs/tips.txt'), index)
        showTip = wxShowTip(frame, tp, showTip)
        index = tp.GetCurrentTip()
        if conf:
            conf.set('tips', 'showonstartup', showTip)
            conf.set('tips', 'tipindex', index)
            try:
                writeConfig(conf)
            except IOError:
                wxLogError('Could not edit tips settings, please make '
                      'sure that the Explorer.*.cfg file is not read only and you '
                      'have sufficient priviledges to write to this file.')

def readTextFromClipboard():
    clip = wxTheClipboard
    clip.Open()
    try:
        data = wxTextDataObject()
        clip.GetData(data)
        return data.GetText()
    finally:
        clip.Close()

def writeTextToClipboard(text):
    clip = wxTheClipboard
    clip.Open()
    try:
        clip.SetData(wxTextDataObject(text))
    finally:
        clip.Close()

_sharedConfs = {}
def createAndReadConfig(name, forPlatform = 1):
    """ Return an initialised ConfigFile object """
    confFile = '%s/%s%s.cfg' % (Preferences.rcPath, name,
        forPlatform and wx.wxPlatform == '__WXMSW__' and '.msw' \
        or forPlatform and '.gtk' or '')
    
    if not _sharedConfs.has_key(confFile):
        conf = ConfigParser()
        conf.read(confFile)
        conf.confFile = confFile
        _sharedConfs[confFile] = conf
    
    return _sharedConfs[confFile]

def writeConfig(conf):
    #f = get_current_frame()
    #print 'writeConfig', f.f_back.f_back.f_code.co_filename
    conf.write(open(conf.confFile, 'w'))

from wxPython import html

wxEVT_HTML_URL_CLICK = wxNewId()

def EVT_HTML_URL_CLICK(win, func):
    win.Connect(-1, -1, wxEVT_HTML_URL_CLICK, func)

class wxHtmlWindowUrlClick(wxPyEvent):
    def __init__(self, linkinfo):
        wxPyEvent.__init__(self)
        self.SetEventType(wxEVT_HTML_URL_CLICK)
        self.linkinfo = (linkinfo.GetHref(), linkinfo.GetTarget())

class wxUrlClickHtmlWindow(html.wxHtmlWindow):
    """ HTML window that generates and OnLinkClicked event.

    Use this to avoid having to override HTMLWindow
    """
    def OnLinkClicked(self, linkinfo):
        wxPostEvent(self, wxHtmlWindowUrlClick(linkinfo))

def wxProxyPanel(parent, Win, *args, **kwargs):
    """ Function which put's a panel in between two controls.

        Mainly for better repainting under GTK.
        Based on a pattern by Kevin Gill.
    """
    panel = wxPanel(parent, -1, style=wxTAB_TRAVERSAL | wxCLIP_CHILDREN)

    if type(Win) is types.ClassType:
        win = apply(Win, (panel,) + args, kwargs)
    elif type(Win) is types.InstanceType:
        win = Win
        win.Reparent(panel)
    else:
        raise 'Unhandled type for Win'

    def OnWinSize(evt, win=win):
        win.SetSize(evt.GetSize())
    EVT_SIZE(panel, OnWinSize)
    return panel, win

def IsComEnabled():
    if Preferences.blockCOM: return false
    try:
        import win32com
    except ImportError:
        return false
    else:
        return true

import stat, shutil
skipdirs = ('CVS',)
dofiles = ('.py',)

def updateFile(src, dst):
    if not os.path.isdir(src):
        if os.path.splitext(src)[-1] in dofiles and \
              ( not os.path.exists(dst) or \
              os.stat(dst)[stat.ST_MTIME] < os.stat(src)[stat.ST_MTIME]):
            print 'copying', src, dst
            shutil.copy2(src, dst)
    

def updateDir(src, dst):
    """ Traverse src and assures that dst is up to date """
    os.path.walk(src, visit_update, (src, dst) )

def visit_update(paths, dirname, names):
    src, dst = paths
    reldir = dirname[len(src)+1:]
    if reldir:
        dstdirname = os.path.join(dst, reldir)
    else:
        dstdirname = dst
    if os.path.basename(dirname) in skipdirs:
        return
    if not os.path.exists(dstdirname):
        print 'creating', dstdirname
        os.makedirs(dstdirname)
    for name in names:
        srcname = os.path.join(dirname, name)
        dstname = os.path.join(dstdirname, name)
        updateFile(srcname, dstname)
        
def get_current_frame():
    try:
        raise 'get_exc_info'
    except:
        return sys.exc_info()[2].tb_frame.f_back

def descr_frame(frame):
    if frame: return ('<frame:%s(%s)%s [%s]>'%(
          os.path.basename(frame.f_code.co_filename), frame.f_lineno, 
          frame.f_code.co_name, id(frame)) )
    else: return 'None'

padWidth = 80
pad = padWidth*' '

class PseudoFile:
    """ Base class for file like objects to facilitate StdOut for the Shell."""
    def __init__(self, output = None):
        if output is None: output = []
        self.output = output

    def writelines(self, l):
        map(self.write, l)

    def write(self, s):
        pass

    def flush(self):
        pass

class PseudoFileOutStore(PseudoFile):
    """ File like obj with list storage """
    def write(self, s):
        self.output.append(s)

    def read(self):
        return string.join(self.output, '')


class LoggerPF(PseudoFile):
    """ Base class for logging file like objects """
    def pad(self, s):
        padded = s + pad
        return padded[:padWidth] + string.strip(padded[padWidth:])

class OutputLoggerPF(LoggerPF):
    """ Logs stdout to wxLog functions"""
    def write(self, s):
        if string.strip(s):
            if Preferences.recordModuleCallPoint:
                frame = get_current_frame()
                ss = string.strip(s)+ ' : <<%s, %d>>' % (
                     frame.f_back.f_code.co_filename,
                     frame.f_back.f_lineno,)
            else:
                ss = s
            wxLogMessage(self.pad(ss))

        sys.__stdout__.write(s)

class ErrorLoggerPF(LoggerPF):
    """ Logs stderr to wxLog functions"""
    def write(self, s):
        if not hasattr(self, 'buffer'):
            self.buffer = ''

        if s == '    ':
            self.buffer = s
        elif s[-1] != '\n':
            self.buffer = self.buffer + s
        else:
            wxLogError(self.pad(self.buffer+s[:-1]))

        sys.__stderr__.write(s)

def getCtrlsFromDialog(dlg, className):
    """ Returns children of given class from dialog.

    This is useful for standard dialogs that does not expose their children """
    return filter(lambda d, cn=className: d.__class__.__name__ == cn,
                  dlg.GetChildren())

def html2txt(htmlblock):
    import htmllib, formatter, StringIO
    s = StringIO.StringIO('')
    w = formatter.DumbWriter(s)
    f = formatter.AbstractFormatter(w)
    p = htmllib.HTMLParser(f)
    p.feed(htmlblock)
    return string.strip(s.getvalue())

def getEntireWxNamespace():
    """ Return a dictionary containing the entire (non filtered) wxPython 
        namespace """
    from wxPython import wx, html, htmlhelp, grid, calendar, utils, stc, ogl, gizmos, help
    namespace = {}
    map(namespace.update, [wx.__dict__, html.__dict__, htmlhelp.__dict__,
                           grid.__dict__, calendar.__dict__, utils.__dict__,
                           stc.__dict__, ogl.__dict__, gizmos.__dict__,
                           help.__dict__])
    return namespace

class FrameRestorerMixin:
    """ Used by top level windows to restore from gidden or iconised state
    and to load and persist window dimensions 
    
    Classes using the mixin mus define self.setDefaultDimensions()
    """
    confFile = 'Explorer'
    confSection = 'windowdims'

    def restore(self):
        self.Show()
        if self.IsIconized():
            self.Iconize(false)
        self.Raise()

    def setDimensions(self, dims):
        apply(self.SetDimensions, dims)        

    def getDimensions(self):
        return self.GetPosition().asTuple() + self.GetSize().asTuple()        

    def loadDims(self):
        conf = createAndReadConfig(self.confFile)
        if not conf.has_option(self.confSection, self.winConfOption):
            dims = None
        else:
            dims = eval(conf.get(self.confSection , self.winConfOption))

        if dims:
            self.setDimensions(dims)
        else:
            self.setDefaultDimensions()

    def saveDims(self, dims=()):
        if dims == ():
            dims = self.getDimensions()
        conf = createAndReadConfig(self.confFile)
        conf.set(self.confSection, self.winConfOption, `dims`)
        writeConfig(conf)
        
    def restoreDefDims(self):
        self.saveDims(None)
        self.loadDims()


def setupCloseWindowOnEscape(win):
    def OnCloseWin(event, win=win): win.Close()

    wxID_CLOSEWIN = wxNewId()
    EVT_MENU(win, wxID_CLOSEWIN, OnCloseWin)
    return (wxACCEL_NORMAL, WXK_ESCAPE, wxID_CLOSEWIN)

def getModelBaseDir(model):
    if hasattr(model, 'app') and model.app and model.app.savedAs:
        return os.path.dirname(model.app.filename)
    elif model.savedAs:
        return os.path.dirname(model.filename)
    else:
        return ''

def pathRelativeToModel(path, model):
    from relpath import relpath
    mbd = getModelBaseDir(model)
    if mbd:
        return relpath(mbd, path)
    else:
        return path

class BottomAligningSplitterMix:
    """ Mixin class that keeps the bottom window in a splitter at a constant height """
    def __init__(self):
        EVT_SIZE(self, self._OnSplitterwindowSize)
        EVT_SPLITTER_SASH_POS_CHANGED(self, self.GetId(),
            self._OnSplitterwindowSplitterSashPosChanged)
        EVT_SPLITTER_DOUBLECLICKED(self, self.GetId(),
            self._OnSplitterwindowSplitterDoubleclicked)
        sashsize = self.GetSashSize()
        self.SetMinimumPaneSize(sashsize)
        sashpos = self.GetClientSize().y - sashsize
        self.SetSashPosition(sashpos)
        self._win2sze = self._getWin2Sze()

    def bottomWindowIsOpen(self):
        return self.GetSashPosition() != self.GetClientSize().y - self.GetSashSize()

    def openBottomWindow(self):
        self.SetSashPosition(\
                  self.GetClientSize().y *(1.0-Preferences.eoErrOutWindowHeightPerc))
        self._win2sze = self._getWin2Sze()

    def closeBottomWindow(self):
        self.SetSashPosition(self.GetClientSize().y - self.GetSashSize())
        self._win2sze = self._getWin2Sze()

    def _getWin2Sze(self):
        win2 = self.GetWindow2()
        if win2 : return win2.GetSize().y
        else:     return 0

    def _OnSplitterwindowSize(self, event):
        sashpos = self.GetClientSize().y - self._win2sze - self.GetSashSize()
        self.SetSashPosition(sashpos)

    def _OnSplitterwindowSplitterSashPosChanged(self, event):
        self._win2sze = self._getWin2Sze()
        event.Skip()

    def _OnSplitterwindowSplitterDoubleclicked(self, event):
        if self.bottomWindowIsOpen():
            self.closeBottomWindow()
        else:
            self.openBottomWindow()

class BottomAligningSplitterWindow(wxSplitterWindow, BottomAligningSplitterMix):
    def __init__(self, *_args, **_kwargs):
        apply(wxSplitterWindow.__init__, (self,)+_args, _kwargs)
        BottomAligningSplitterMix.__init__(self)

def traverseTreeCtrl(tree, treeItem, func):
    func(tree, treeItem)
    item, cookie = tree.GetFirstChild(treeItem, 0)
    while item.IsOk():
        traverseTreeCtrl(tree, item, func)
        item, cookie = tree.GetNextChild(item, cookie)


class ListCtrlLabelEditFixEH(wxEvtHandler):
    """Fixes broken LabelEdit/Cursor behaviour on MSW

       Add in constructor:
       ListCtrlLabelEditFixEH(<control>)

       Add in destructor:
       <control>.PopEventHandler(true)
    """

    wxEVT_CTRLEDIT = wxNewId()

    def __init__(self, listCtrl):
        wxEvtHandler.__init__(self)
        self._blockMouseEdit = false

        self.listCtrl = listCtrl
        EVT_LIST_BEGIN_LABEL_EDIT(listCtrl, listCtrl.GetId(), self.OnBeginLabelEdit)
        self.Connect(-1, -1, self.wxEVT_CTRLEDIT, self.OnCtrlLabelEdit)
        listCtrl.PushEventHandler(self)
    
    def OnBeginLabelEdit(self, event):
        if not self._blockMouseEdit and wxPlatform == '__WXMSW__':
            event.Veto()

            ctrlEditEvt = wxPyEvent()
            ctrlEditEvt.SetEventType(self.wxEVT_CTRLEDIT)
            ctrlEditEvt.idx = event.GetIndex()

            wxPostEvent(self, ctrlEditEvt)
        else:
            self._blockMouseEdit = false
        event.Skip()

    def OnCtrlLabelEdit(self, event):
        self._blockMouseEdit = true
        self.listCtrl.EditLabel(event.idx)
        event.Skip()

def importFromPlugins(name):
    # find module
    paths = [Preferences.pyPath + '/Plug-ins']
    if Preferences.extraPluginsPath:
        paths.append(Preferences.extraPluginsPath)
    if Preferences.rcPath != Preferences.pyPath and \
          os.path.isdir(Preferences.rcPath+ '/Plug-ins'):
        paths.append(Preferences.rcPath + '/Plug-ins')

    modname = string.replace(name, '.', '/') + '.py'
    for pth in paths:
        modpath = os.path.join(pth, modname)
        if os.path.isfile(modpath):
            break
    else:
        raise ImportError, 'Module %s could not be found in Plug-ins'
    
    import new
    mod = new.module(name)
    
    execfile(modpath, mod.__dict__)
    
    return mod

    
