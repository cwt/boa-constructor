#----------------------------------------------------------------------
# Name:        DialogCompanions.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2000/27/02
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2002 Riaan Booysen
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
        return '''data = wxColourData()
data.SetChooseFull(true)
dlg = wxColourDialog(self, data)
try:
    if dlg.ShowModal() == wxID_OK:
        data = dlg.GetColourData()
        # Your code
finally:
    dlg.Destroy()

'''

class FontDialogCDC(DataCDC): #(parent, data = None)
    #wxDocs = HelpCompanions.wxFontDialogDocs
    def body(self):
        return '''data = wxFontData()
dlg = wxFontDialog(self, data)
try:
    if dlg.ShowModal() == wxID_OK:
        data = dlg.GetFontData()
        font = data.GetChosenFont()
        # Your code
finally:
    dlg.Destroy()

'''

class PrintDialogCDC(DataCDC): #(parent, data = None)
    #wxDocs = HelpCompanions.wxPrintDialogDocs
    def body(self):
        return '''data = wxPrintDialogData()
data.EnablePrintToFile(true)
data.EnablePageNumbers(true)
data.EnableSelection(true)
dlg = wxPrintDialog(self, data)
try:
    if dlg.ShowModal() == wxID_OK:
        # Your code
finally:
    dlg.Destroy()

'''

class PageSetupDialogCDC(DataCDC): #(parent, data = None)
    #wxDocs = HelpCompanions.wxPageSetupDialogDocs
    def body(self):
        return '''data = wxPageSetupDialogData()
data.SetMarginTopLeft(wxPoint(50,50))
data.SetMarginBottomRight(wxPoint(50,50))
dlg = wxPageSetupDialog(self, data)
try:
    if dlg.ShowModal() == wxID_OK:
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
        return '''dlg = wxDirDialog(self)
try:
    if dlg.ShowModal() == wxID_OK:
        dir = dlg.GetPath()
        # Your code
finally:
    dlg.Destroy()
'''

class FileDialogCDC(MessagedCDC): #(parent, message = 'Choose a file', defaultDir = '', defaultFile = '', wildcard ='*.*', style = 0, pos = wxDefaultPosition)
    #wxDocs = HelpCompanions.wxFileDialogDocs
    def body(self):
        return '''dlg = wxFileDialog(self, "Choose a file", ".", "", "*.*", wxOPEN)
try:
    if dlg.ShowModal() == wxID_OK:
        filename = dlg.GetPath()
        # Your code
finally:
    dlg.Destroy()
'''

class SingleChoiceDialogCDC(MessagedCDC): #(parent, message, caption, choices, clientData = None, style = wxOK | wxCANCEL | wxCENTER, pos = wxDefaultPosition)
    #wxDocs = HelpCompanions.wxSingleChoiceDialogDocs
    def body(self):
        return '''dlg = wxSingleChoiceDialog(self, 'Question', 'Caption', [])
try:
    if dlg.ShowModal() == wxID_OK:
        selected = dlg.GetStringSelection()
        # Your code
finally:
    dlg.Destroy()

'''

class TextEntryDialogCDC(MessagedCDC): #(parent, message, caption = 'Please enter text', defaultValue = '', style = wxOK | wxCANCEL | wxCENTER, pos = wxDefaultPosition)
    #wxDocs = HelpCompanions.wxTextEntryDialogDocs
    def body(self):
        return '''dlg = wxTextEntryDialog(self, 'Question', 'Caption', 'Default answer')
try:
    if dlg.ShowModal() == wxID_OK:
        answer = dlg.GetValue()
        # Your code
finally:
    dlg.Destroy()

'''

class MessageDialogCDC(MessagedCDC): #(parent, message, caption = 'Message box', style = wxOK | wxCANCEL | wxCENTER, pos = wxDefaultPosition)
    #wxDocs = HelpCompanions.wxMessageDialogDocs
    def body(self):
        return '''dlg = wxMessageDialog(self, 'Message',
  'Caption', wxOK | wxICON_INFORMATION)
try:
    dlg.ShowModal()
finally:
    dlg.Destroy()

'''

PaletteStore.paletteLists['Dialogs'].extend([wxColourDialog, wxFontDialog,
      wxFileDialog, wxDirDialog, wxPrintDialog, wxPageSetupDialog,
      wxSingleChoiceDialog, wxTextEntryDialog, wxMessageDialog])

PaletteStore.compInfo.update({wxColourDialog: ['wxColorDialog', ColourDialogCDC],
    wxFontDialog: ['wxFontDialog', FontDialogCDC],
    wxFileDialog: ['wxFileDialog', FileDialogCDC],
    wxPrintDialog: ['wxPrintDialog', PrintDialogCDC],
    wxPageSetupDialog: ['wxPageSetupDialog', PageSetupDialogCDC],
    wxDirDialog: ['wxDirDialog', DirDialogCDC],
    wxSingleChoiceDialog: ['wxSingleChoiceDialog', SingleChoiceDialogCDC],
    wxTextEntryDialog: ['wxTextEntryDialog', TextEntryDialogCDC],
    wxMessageDialog: ['wxMessageDialog', MessageDialogCDC],
})
