#----------------------------------------------------------------------
# Name:        DialogCompanions.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2000/27/02
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2005 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
print 'importing Companions.DialogCompanions'

from wxPython.wx import *

from BaseCompanions import CodeCompanion
import PaletteStore

class CommonDialogCompanion(CodeCompanion):
    def __init__(self, name, parent):
        CodeCompanion.__init__(self, name)
        self.parent = parent

class DataCDC(CommonDialogCompanion):
    def constructor(self):
        return '    dlg = %(dlgclass)s(%(parent)s, data = None)'

class ColourDialogCDC(DataCDC): #(parent, data = None)
    #wxDocs = HelpCompanions.wxColourDialogDocs
    def body(self):
        return '''data = wx.ColourData()
data.SetChooseFull(true)
dlg = wx.ColourDialog(self, data)
try:
    if dlg.ShowModal() == wx.ID_OK:
        data = dlg.GetColourData()
        # Your code
finally:
    dlg.Destroy()

'''

class FontDialogCDC(DataCDC): #(parent, data = None)
    #wxDocs = HelpCompanions.wxFontDialogDocs
    def body(self):
        return '''data = wx.FontData()
dlg = wx.FontDialog(self, data)
try:
    if dlg.ShowModal() == wx.ID_OK:
        data = dlg.GetFontData()
        font = data.GetChosenFont()
        # Your code
finally:
    dlg.Destroy()

'''

class PrintDialogCDC(DataCDC): #(parent, data = None)
    #wxDocs = HelpCompanions.wxPrintDialogDocs
    def body(self):
        return '''data = wx.PrintDialogData()
data.EnablePrintToFile(true)
data.EnablePageNumbers(true)
data.EnableSelection(true)
dlg = wx.PrintDialog(self, data)
try:
    if dlg.ShowModal() == wx.ID_OK:
        # Your code
finally:
    dlg.Destroy()

'''

class PageSetupDialogCDC(DataCDC): #(parent, data = None)
    #wxDocs = HelpCompanions.wxPageSetupDialogDocs
    def body(self):
        return '''data = wx.PageSetupDialogData()
data.SetMarginTopLeft(wx.Point(50,50))
data.SetMarginBottomRight(wx.Point(50,50))
dlg = wx.PageSetupDialog(self, data)
try:
    if dlg.ShowModal() == wx.ID_OK:
        data = dlg.GetPageSetupData()
        # Your code
finally:
    dlg.Destroy()

'''

class MessagedCDC(CommonDialogCompanion):
    pass

class DirDialogCDC(MessagedCDC): #(parent, message = 'Choose a directory', defaultPath = '', style = 0, pos = wxDefaultPosition)
    #wxDocs = HelpCompanions.wxDirDialogDocs
    def body(self):
        return '''dlg = wx.DirDialog(self)
try:
    if dlg.ShowModal() == wx.ID_OK:
        dir = dlg.GetPath()
        # Your code
finally:
    dlg.Destroy()
'''

class FileDialogCDC(MessagedCDC): #(parent, message = 'Choose a file', defaultDir = '', defaultFile = '', wildcard ='*.*', style = 0, pos = wxDefaultPosition)
    #wxDocs = HelpCompanions.wxFileDialogDocs
    def body(self):
        return '''dlg = wx.FileDialog(self, "Choose a file", ".", "", "*.*", wx.OPEN)
try:
    if dlg.ShowModal() == wx.ID_OK:
        filename = dlg.GetPath()
        # Your code
finally:
    dlg.Destroy()
'''

class SingleChoiceDialogCDC(MessagedCDC): #(parent, message, caption, choices, clientData = None, style = wxOK | wxCANCEL | wxCENTER, pos = wxDefaultPosition)
    #wxDocs = HelpCompanions.wxSingleChoiceDialogDocs
    def body(self):
        return '''dlg = wx.SingleChoiceDialog(self, 'Question', 'Caption', [])
try:
    if dlg.ShowModal() == wx.ID_OK:
        selected = dlg.GetStringSelection()
        # Your code
finally:
    dlg.Destroy()

'''

class TextEntryDialogCDC(MessagedCDC): #(parent, message, caption = 'Please enter text', defaultValue = '', style = wxOK | wxCANCEL | wxCENTER, pos = wxDefaultPosition)
    #wxDocs = HelpCompanions.wxTextEntryDialogDocs
    def body(self):
        return '''dlg = wx.TextEntryDialog(self, 'Question', 'Caption', 'Default answer')
try:
    if dlg.ShowModal() == wx.ID_OK:
        answer = dlg.GetValue()
        # Your code
finally:
    dlg.Destroy()

'''

class MessageDialogCDC(MessagedCDC): #(parent, message, caption = 'Message box', style = wxOK | wxCANCEL | wxCENTER, pos = wxDefaultPosition)
    #wxDocs = HelpCompanions.wxMessageDialogDocs
    def body(self):
        return '''dlg = wx.MessageDialog(self, 'Message',
  'Caption', wx.OK | wx.ICON_INFORMATION)
try:
    dlg.ShowModal()
finally:
    dlg.Destroy()

'''

PaletteStore.paletteLists['Dialogs'].extend([wxColourDialog, wxFontDialog,
      wxFileDialog, wxDirDialog, wxPrintDialog, wxPageSetupDialog,
      wxSingleChoiceDialog, wxTextEntryDialog, wxMessageDialog])

PaletteStore.compInfo.update({wxColourDialog: ['wx.ColorDialog', ColourDialogCDC],
    wxFontDialog: ['wx.FontDialog', FontDialogCDC],
    wxFileDialog: ['wx.FileDialog', FileDialogCDC],
    wxPrintDialog: ['wx.PrintDialog', PrintDialogCDC],
    wxPageSetupDialog: ['wx.PageSetupDialog', PageSetupDialogCDC],
    wxDirDialog: ['wx.DirDialog', DirDialogCDC],
    wxSingleChoiceDialog: ['wx.SingleChoiceDialog', SingleChoiceDialogCDC],
    wxTextEntryDialog: ['wx.TextEntryDialog', TextEntryDialogCDC],
    wxMessageDialog: ['wx.MessageDialog', MessageDialogCDC],
})
