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
from Preferences import IS
import string

# Why did I capitalise these ????

def ShowErrorMessage(parent, caption, mess):
    print mess, mess.__class__, mess.args[0]
    dlg = wxMessageDialog(parent, mess.__class__.__name__ +': '+mess.args[0],
                          caption, wxOK | wxICON_EXCLAMATION)
    try: dlg.ShowModal()
    finally: dlg.Destroy()

def yesNoDialog(parent, title, question):
    dlg = wxMessageDialog(parent, question, title , wxYES_NO | wxICON_QUESTION)
    try: return (dlg.ShowModal() == wxID_YES)
    finally: dlg.Destroy()

def AddToolButtonBmpObject(frame, toolbar, thebitmap, hint, triggermeth, toggleBitmap = wxNullBitmap):
    nId = NewId()
#    t = toolbar.AddTool(nId, thebitmap, toggleBitmap, shortHelpString = hint, toggle = toggleBitmap != wxNullBitmap)
    toolbar.AddTool(nId, thebitmap, toggleBitmap, shortHelpString = hint)#, toggle = toggleBitmap != wxNullBitmap)
    EVT_TOOL(frame, nId, triggermeth)
#    return t

def AddToolButtonBmpFile(frame, toolbar, filename, hint, triggermeth):
    AddToolButtonBmpObject(frame, toolbar, wxBitmap(filename, wxBITMAP_TYPE_BMP),
      hint, triggermeth)

def AddToolButtonBmpIS(frame, toolbar, name, hint, triggermeth, toggleBmp = ''):
    if toggleBmp:
        AddToolButtonBmpObject(frame, toolbar, IS.load(name), hint, triggermeth, IS.load(toggleBmp))
    else:
        AddToolButtonBmpObject(frame, toolbar, IS.load(name), hint, triggermeth)


#This format follows wxWindows conventions
def windowIdentifier(frameName, ctrlName):
    return 'wxID_' + string.upper(frameName) + string.upper(ctrlName)
    

class BoaFileDropTarget(wxFileDropTarget):
    def __init__(self, editor):
        wxFileDropTarget.__init__(self)
        self.editor = editor

    def OnDropFiles(self, x, y, filenames):
        print 'DROP'
        wxBeginBusyCursor()
        try:
            for filename in filenames:
                self.editor.openOrGotoModule(filename)
        finally:
            wxEndBusyCursor()
            
def split_seq(seq, pivot):
    result = []
    cur_sect = []
    for itm in seq:
        if itm == pivot:
            result.append(cur_sect)
            cur_sect = []
        else:
            cur_sect.append(itm)
    result.append(cur_sect)
            
    return result        

allowed_width = 78
def human_split(line):
    indent = string.find(line, string.strip(line))

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
        
            
                    
            
            
          