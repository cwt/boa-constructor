#----------------------------------------------------------------------
# Name:        Utils.py
# Purpose:     General purpose functions and classes
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2004 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
import string, os, glob, pprint
from types import InstanceType

from wxPython.wx import *

import Preferences
from Preferences import IS
from ExternalLib.ConfigParser import ConfigParser

def toPyPath(filename):
    return os.path.join(Preferences.pyPath, filename)

def ShowErrorMessage(parent, caption, mess):
    dlg = wxMessageDialog(parent, mess.__class__.__name__ +': '+`mess`,
                          caption, wxOK | wxICON_EXCLAMATION)
    try: dlg.ShowModal()
    finally: dlg.Destroy()

def ShowMessage(parent, caption, message, msgTpe=wxICON_INFORMATION):
    dlg = wxMessageDialog(parent, message, caption, wxOK | msgTpe)
    try: dlg.ShowModal()
    finally: dlg.Destroy()

def yesNoDialog(parent, title, question):
    dlg = wxMessageDialog(parent, question, title, wxYES_NO | wxICON_QUESTION)
    try: return (dlg.ShowModal() == wxID_YES)
    finally: dlg.Destroy()

def AddToolButtonBmpObject(frame, toolbar, thebitmap, hint, triggermeth,
      theToggleBitmap=wxNullBitmap):
    nId = wxNewId()
    toolbar.AddTool(nId, thebitmap, theToggleBitmap, shortHelpString = hint)
    EVT_TOOL(frame, nId, triggermeth)
    return nId

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

#This format follows wxWidgets conventions
def windowIdentifier(frameName, ctrlName):
    return 'wxID_' + frameName.upper() + ctrlName.upper()


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
    indent = line.find(line.strip())

    # XXX use safe split, commas in quotes will break
    segments = line.split(',')
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
    return str.translate(ws2s)

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

def showTip(frame, forceShow=0):
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
        tp = wxCreateFileTipProvider(toPyPath('Docs/tips.txt'), index)
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
def createAndReadConfig(name, forPlatform=1):
    """ Return an initialised ConfigFile object """
    confFile = os.path.join(Preferences.rcPath, '%s%s.cfg' % (name,
        forPlatform and '.'+Preferences.thisPlatform or ''))

    # paths are within quotes in config, simpler to use fwd slash
    _confDefaults = {'BOAROOT': Preferences.pyPath.replace('\\', '/'),
                     'RESOURCECONFIG': Preferences.rcPath.replace('\\', '/')}

    if not _sharedConfs.has_key(confFile):
        conf = ConfigParser(_confDefaults)
        conf.read(confFile)
        conf.confFile = confFile
        _sharedConfs[confFile] = conf

    return _sharedConfs[confFile]

def writeConfig(conf):
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
    
    def isatty(self):
        return false

class PseudoFileOutStore(PseudoFile):
    """ File like obj with list storage """
    def write(self, s):
        self.output.append(s)

    def read(self):
        return ''.join(self.output)


class LoggerPF(PseudoFile):
    """ Base class for logging file like objects """
    def pad(self, s):
        padded = s + pad
        return padded[:padWidth] + padded[padWidth:].strip()

class OutputLoggerPF(LoggerPF):
    """ Logs stdout to wxLog functions"""
    def write(self, s):
        if s.strip():
            if Preferences.recordModuleCallPoint:
                frame = get_current_frame()
                ss = s.strip()+ ' : <<%s, %d>>' % (
                     frame.f_back.f_code.co_filename,
                     frame.f_back.f_lineno,)
            else:
                ss = s
            wxLogMessage(self.pad(ss).replace('%', '%%'))

        sys.__stdout__.write(s)

# XXX Should try to recognise warnings
# Match start against [v for k, v in __builtins__.items() if type(v) is types.ClassType and issubclass(v, Warning)]

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
            wxLogError(self.pad(self.buffer+s[:-1]).replace('%', '%%'))

        sys.__stderr__.write(s)

def installErrOutLoggers():
    sys.stdout = OutputLoggerPF()
    sys.stderr = ErrorLoggerPF()

def uninstallErrOutLoggers():
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

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
    return s.getvalue().strip()

def getEntireWxNamespace():
    """ Return a dictionary containing the entire (non filtered) wxPython
        namespace """
    from wxPython import wx, html, htmlhelp, grid, calendar, stc, ogl
    from wxPython import help, gizmos, wizard
    namespace = {}
    map(namespace.update, [wx.__dict__, html.__dict__, htmlhelp.__dict__,
                           grid.__dict__, calendar.__dict__, 
                           stc.__dict__, ogl.__dict__, gizmos.__dict__,
                           help.__dict__, wizard.__dict__])
    return namespace

class FrameRestorerMixin:
    """ Used by top level windows to restore from gidden or iconised state
    and to load and persist window dimensions

    Classes using the mixin must define self.setDefaultDimensions()
    To be able to save, a winConfOption attr must be defined.
    """
    confFile = 'Explorer'
    confSection = 'windowdims'
    frameRestorerWindows = {}

    def restore(self):
        self.Show()
        if self.IsIconized():
            self.Iconize(false)
        self.Raise()

    def setDimensions(self, dims):
        if None in dims:
            if dims[0] is None:
                if dims[1] is not None:
                    self.SetClientSize(tuple(dims[1:]))
            else:
                self.SetPosition(tuple(dims[:-1]))
        else:
            self.SetDimensions(*dims)

    def getDimensions(self):
        pos = self.GetPosition().asTuple()
        size = self.GetSize().asTuple()
        return pos + size

    def loadDims(self):
        conf = createAndReadConfig(self.confFile)
        if not conf.has_option(self.confSection, self.winConfOption):
            dims = None
        else:
            dims = eval(conf.get(self.confSection , self.winConfOption), 
                        {'wxSize': wxSize, 'wxPoint': wxPoint,
                         'wxDefaultSize': wxDefaultSize, 
                         'wxDefaultPosition': wxDefaultPosition})

        if dims:
            self.setDimensions(dims)
        else:
            self.setDefaultDimensions()

        self.frameRestorerWindows[self.winConfOption] = self

    def saveDims(self, dims=()):
        if dims == ():
            dims = self.getDimensions()
        conf = createAndReadConfig(self.confFile)
        conf.set(self.confSection, self.winConfOption, `dims`)
        writeConfig(conf)

    def restoreDefDims(self):
        self.saveDims(None)
        self.loadDims()

def callOnFrameRestorers(method):
    for name, window in FrameRestorerMixin.frameRestorerWindows.items():
        if not window:
            del FrameRestorerMixin.frameRestorerWindows[name]
        else:
            method(window)


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
        self.SetSashPosition(
         int(self.GetClientSize().y *(1.0-Preferences.eoErrOutWindowHeightPerc)))
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
        listCtrl.PushEventHandler(self)

    def OnBeginLabelEdit(self, event):
        if not self._blockMouseEdit and wxPlatform == '__WXMSW__':
            event.Veto()
            wxCallAfter(self.ctrlLabelEdit, event.GetIndex())
        else:
            self._blockMouseEdit = false
        event.Skip()

    def ctrlLabelEdit(self, idx):
        self._blockMouseEdit = true
        self.listCtrl.EditLabel(idx)

SEL_FOC = wxLIST_STATE_SELECTED | wxLIST_STATE_FOCUSED
def selectBeforePopup(event):
    """Ensures the item the mouse is pointing at is selected before a popup.

    Works with both single-select and multi-select lists."""
    ctrl = event.GetEventObject()
    if isinstance(ctrl, wxListCtrl):
        n, flags = ctrl.HitTest(event.GetPosition())
        if n >= 0:
            if not ctrl.GetItemState(n, wxLIST_STATE_SELECTED):
                if not (ctrl.GetWindowStyleFlag() & wxLC_SINGLE_SEL):
                    # Clear selection if multi-select.
                    for i in range(ctrl.GetItemCount()):
                        ctrl.SetItemState(i, 0, SEL_FOC)
                ctrl.SetItemState(n, SEL_FOC, SEL_FOC)

def getListCtrlSelection(listctrl, state=wxLIST_STATE_SELECTED):
    """ Returns list of item indexes of given state """
    res = []
    idx = -1
    while 1:
        idx = listctrl.GetNextItem(idx, wxLIST_NEXT_ALL, state)
        if idx == -1:
            break
        res.append(idx)
    return res

class ListCtrlSelectionManagerMix:
    """Mixin that defines a platform independent selection policy

    As selection single and multi-select list return the item index or a
    list of item indexes respectively.
    """
    wxEVT_DOPOPUPMENU = wxNewId()
    _menu = None

    def __init__(self):
        EVT_RIGHT_DOWN(self, self.OnLCSMRightDown)
        self.Connect(-1, -1, self.wxEVT_DOPOPUPMENU, self.OnLCSMDoPopup)

    def getPopupMenu(self):
        """ Override to implement dynamic menus (create) """
        return self._menu

    def setPopupMenu(self, menu):
        """ Must be set for default behaviour """
        self._menu = menu

    def afterPopupMenu(self, menu):
        """ Override to implement dynamic menus (destroy) """
        pass

    def getSelection(self):
        res = getListCtrlSelection(self)
        if self.GetWindowStyleFlag() & wxLC_SINGLE_SEL:
            if res:
                return res[0]
            else:
                return -1
        else:
            return res

    def OnLCSMRightDown(self, event):
        selectBeforePopup(event)
        menu = self.getPopupMenu()
        #event.Skip()
        if menu:
            # XXX
            self.PopupMenu(menu, event.GetPosition())
            self.afterPopupMenu(menu)
            return

            evt = wxPyEvent()
            evt.SetEventType(self.wxEVT_DOPOPUPMENU)
            evt.menu = menu
            evt.pos = event.GetPosition()
            wxPostEvent(self, evt)

    def OnLCSMDoPopup(self, event):
        self.PopupMenu(event.menu, event.pos)
        self.afterPopupMenu(event.menu)


# Does this version leak event handlers?
def wxCallAfter(callable, *args, **kw):
    handler, evtType = wxEvtHandler(), wxNewId()
    handler.Connect(-1, -1, evtType, lambda event, handler=handler,
          callable=callable, args=args, kw=kw: apply(callable, args, kw) )
    evt = wxPyEvent()
    evt.SetEventType(evtType)
    wxPostEvent(handler, evt)

_wxCallAfterId = None
def wxCallAfter(callable, *args, **kw):
    app = wxGetApp()
    assert app, 'No wxApp created yet'

    global _wxCallAfterId
    if _wxCallAfterId is None:
        _wxCallAfterId = wxNewId()
        app.Connect(-1, -1, _wxCallAfterId,
              lambda event: apply(event.callable, event.args, event.kw) )
    evt = wxPyEvent()
    evt.SetEventType(_wxCallAfterId)
    evt.callable = callable
    evt.args = args
    evt.kw = kw
    wxPostEvent(app, evt)

def getIndentBlock():
    if Preferences.STCUseTabs:
        return '\t'
    else:
        return Preferences.STCIndent*' '

#-------------------------------------------------------------------------------

def canReadStream(stream):
    try:
        return stream.CanRead()
    except AttributeError:
        return not stream.eof()

def find_dotted_module(name, path=None):
    import imp
    segs = name.split('.')
    file = None
    while segs:
        if file: file.close()
        file, filename, desc = imp.find_module(segs[0], path)
        del segs[0]
        path = [filename]
    return file, filename, desc

def appendMenuItem(menu, wId, label, code=(), bmp='', help=''):
    # XXX Add kind=wxITEM_NORMAL when 2.3.3 is minimum.
    text = label + (code and ' \t'+code[2] or '')
    menuItem = wxMenuItem(menu, wId, text, help)
    if Preferences.editorMenuImages and bmp and bmp != '-':
        if wxPlatform == '__WXGTK__' and wxVERSION >= (2,3,3) or \
              wxPlatform == '__WXMSW__':
            menuItem.SetBitmap(Preferences.IS.load(bmp))
    menu.AppendItem(menuItem)

def stringFromControl(u):
    try: wxUSE_UNICODE, UnicodeError
    except NameError: return u

    if wxUSE_UNICODE:
        try: 
            return str(u)
        except UnicodeError, err:
            raise Exception, 'Unable to encode unicode string, please change '\
                  'the defaultencoding in sitecustomize.py to handle this '\
                  'encoding.\nError message %s'%str(err)
    else:
        return u
        
def stringToControl(s):
    try: wxUSE_UNICODE, UnicodeError
    except NameError: return s

    if wxUSE_UNICODE:
        try: 
            return unicode(s)
        except UnicodeError, err:
            raise Exception, 'Unable to decode unicode string, please change '\
                  'the defaultencoding in sitecustomize.py to handle this '\
                  'encoding.\n Error message %s'%str(err)
    else:
        return s


def getEOLMode(text, default=os.linesep):
    if text.find('\r\n') != -1: return '\r\n'
    elif text.find('\r') != -1: return '\r'
    elif text.find('\n') != -1: return '\n'
    else: return default

def toUnixEOLMode(text):
    return text.replace('\r\n', '\n').replace('\r', '\n')

def checkMixedEOLs(text):
    """ Returns false for mixed EOLs """

    crlf = text.count('\r\n')
    lf = text.count('\n')
    cr = text.count('\r')

    if crlf and (lf > crlf or cr > crlf):
        return true
    elif not crlf and cr and lf:
        return true
    else:
        return false
