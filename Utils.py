#----------------------------------------------------------------------
# Name:        Utils.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
from wxPython.wx import *
import Preferences
from Preferences import IS
import string
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

def AddToolButtonBmpFile(frame, toolbar, filename, hint, triggermeth):
    return AddToolButtonBmpObject(frame, toolbar, wxBitmap(filename, wxBITMAP_TYPE_BMP),
      hint, triggermeth)

def AddToolButtonBmpIS(frame, toolbar, name, hint, triggermeth, toggleBmp = ''):
    if toggleBmp:
        return AddToggleToolButtonBmpObject(frame, toolbar, IS.load(name), hint, triggermeth)
    else:
        return AddToolButtonBmpObject(frame, toolbar, IS.load(name), hint, triggermeth)

def AddToggleToolButtonBmpObject(frame, toolbar, thebitmap, hint, triggermeth):
    nId = wxNewId()
    from Views.StyledTextCtrls import new_stc
    if new_stc:
        toolbar.AddTool(nId, thebitmap, thebitmap, shortHelpString = hint, isToggle = true)
    else:
        toolbar.AddTool(nId, thebitmap, thebitmap, shortHelpString = hint, toggle = true)
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
            print cur_line, indent + 2
        else:
            cur_line = cur_line + segment

    result.append(cur_line)
    
    return result
        
def duplicateMenu(source):
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

def startswith(str, substr):
    return len(str) >= len(substr) and str[:len(substr)] == substr

class PaintEventHandler(wxEvtHandler):
    """ This class is used to merge paint reqeusts. Each paint is 
    captured and saved. Later on the idle event, the non-duplicated
    paints are executed. The code attempts to be efficient by determining
    the enclosing rectangle where multiple rectangles intersect.
    This is required only on GTK systems.
   
    Note: there is an assumption here that event handling is synchronous
    i.e. the paints called from the idle event handler are processed
    before the Refresh() call returns."""

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
                conf.write(open(conf.confFile, 'w'))
            except IOError:
                print 'Could not update tips file', showTipsFile, '(check permissions)'

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

def createAndReadConfig(name, forPlatform = 1):
    conf = ConfigParser()
    confFile = '%s/%s%s.cfg' % (Preferences.pyPath, name,
        forPlatform and wx.wxPlatform == '__WXMSW__' and '.msw' \
        or forPlatform and '.gtk' or '')
    conf.read(confFile)
    conf.confFile = confFile
    return conf 
    