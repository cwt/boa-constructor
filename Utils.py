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

def AddToolButtonBmpObject(frame, toolbar, bitmap, hint, triggermeth):
    nId = NewId()
    t = toolbar.AddTool(nId, bitmap, shortHelpString = hint)
    EVT_TOOL(frame, nId, triggermeth)
    return t

def AddToolButtonBmpFile(frame, toolbar, filename, hint, triggermeth):
    AddToolButtonBmpObject(frame, toolbar, wxBitmap(filename, wxBITMAP_TYPE_BMP),
      hint, triggermeth)

def AddToggleToolButtonBmpFile(frame, toolbar, filename1, filename2, hint, triggermeth):
    nId = NewId()
    toolbar.AddTool(nId, wxBitmap(filename1, wxBITMAP_TYPE_BMP), 
      wxBitmap(filename2, wxBITMAP_TYPE_BMP), toggle = true, shortHelpString = hint)
    EVT_TOOL(frame, nId, triggermeth)

#This format follows wxWindows conventions
def windowIdentifier(frameName, ctrlName):
    return 'wxID_' + string.upper(frameName) + string.upper(ctrlName)
    

