#----------------------------------------------------------------------
# Name:        PaletteMapping.py
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
from Companions import *
from UtilCompanions import *
from DialogCompanions import *
import Preferences
from os import path
from wxPython.html import wxHtmlWindow

utilities = [wxMenu, wxImageList, wxAcceleratorTable]

palette = [
  ['Frame bars', 'Editor/Tabs/Singletons', 
    [wxMenuBar, wxToolBar, wxStatusBar]],
  ['Containers/Layout', 'Editor/Tabs/Containers', 
    [wxPanel, wxScrolledWindow, wxNotebook, wxSplitterWindow]], 
  ['Basic Controls', 'Editor/Tabs/Basic', 
    [wxStaticText, wxTextCtrl, wxComboBox, wxChoice, wxButton, wxBitmapButton,
     wxCheckBox, wxRadioButton, wxSpinButton, wxSlider, wxGauge, wxStaticBox, 
     wxScrollBar, wxStaticBitmap, wxStaticLine, wxHtmlWindow]],
  ['List Controls', 'Editor/Tabs/Lists', 
    [wxRadioBox, wxListBox, wxCheckListBox, wxGrid, wxListCtrl, wxTreeCtrl]],
  ['Utilities', 'Editor/Tabs/Utilities', 
    utilities]]

helperClasses = {
    'wxFontPtr': FontDTC,
    'wxColourPtr': ColourDTC
}    

dialogPalette =  ['Dialogs', 'Editor/Tabs/Dialogs', 
    [wxColourDialog, wxFontDialog, wxFileDialog, wxDirDialog, 
    wxPrintDialog, wxPageSetupDialog, 
    wxSingleChoiceDialog, wxTextEntryDialog, wxMessageDialog]]

compInfo = {
    wxApp: ['wxApp', None],
    wxFrame: ['wxFrame', FrameDTC],
    wxDialog: ['wxDialog', DialogDTC],
    wxMiniFrame: ['wxMiniFrame', MiniFrameDTC],
    wxMDIParentFrame: ['wxMDIParentFrame', MDIParentFrameDTC],
    wxMDIChildFrame: ['wxMDIChildFrame', MDIChildFrameDTC],
    wxMenuBar: ['wxMenuBar', DesignTimeCompanion],
    wxToolBar: ['wxToolBar', DesignTimeCompanion],
    wxStatusBar: ['wxStatusBar', DesignTimeCompanion],
    wxPanel: ['wxPanel', PanelDTC], 
    wxScrolledWindow: ['wxScrolledWindow', ScrolledWindowDTC], 
    wxNotebook: ['wxNotebook', NotebookDTC],
    wxSplitterWindow: ['wxSplitterWindow', DesignTimeCompanion],
    wxStaticText: ['wxStaticText', StaticTextDTC], 
    wxTextCtrl: ['wxTextCtrl', TextCtrlDTC], 
    wxChoice: ['wxChoice', ChoiceDTC],
    wxComboBox: ['wxComboBox', ComboBoxDTC],
    wxCheckBox: ['wxCheckBox', CheckBoxDTC],
    wxButton: ['wxButton', ButtonDTC], 
    wxBitmapButton: ['wxBitmapButton', BitmapButtonDTC], 
    wxRadioButton: ['wxRadioButton', RadioButtonDTC],
    wxSpinButton: ['wxSpinButton', SpinButtonDTC],
    wxSlider: ['wxSlider', SliderDTC],
    wxGauge: ['wxGauge', GaugeDTC],
    wxStaticBitmap: ['wxStaticBitmap', StaticBitmapDTC],
    wxListBox: ['wxListBox', ListBoxDTC],
    wxCheckListBox: ['wxCheckListBox', CheckListBoxDTC],
    wxGrid: ['wxGrid', GridDTC], 
    wxListCtrl: ['wxListCtrl', ListCtrlDTC],
    wxTreeCtrl: ['wxTreeCtrl', TreeCtrlDTC],
    wxScrollBar: ['wxScrollBar', ScrollBarDTC],
    wxStaticBox: ['wxStaticBox', StaticBoxDTC],
    wxStaticLine: ['wxStaticLine', StaticLineDTC],
    wxRadioBox: ['wxRadioBox', RadioBoxDTC],
    wxHtmlWindow: ['wxHtmlWindow', HtmlWindowDTC],
    wxColourDialog: ['wxColorDialog', ColourDialogCDC],
    wxFontDialog: ['wxFontDialog', FontDialogCDC],
    wxFileDialog: ['wxFileDialog', FileDialogCDC],
    wxPrintDialog: ['wxPrintDialog', PrintDialogCDC],
    wxPageSetupDialog: ['wxPageSetupDialog', PageSetupDialogCDC],
    wxDirDialog: ['wxDirDialog', DirDialogCDC],
    wxSingleChoiceDialog: ['wxSingleChoiceDialog', SingleChoiceDialogCDC],
    wxTextEntryDialog: ['wxTextEntryDialog', TextEntryDialogCDC],
    wxMessageDialog: ['wxMessageDialog', MessageDialogCDC],
    wxImageList: ['wxImageList', ImageListDTC],
    wxAcceleratorTable: ['wxAcceleratorTable', AcceleratorTableDTC],
    wxMenu: ['wxMenu', MenuDTC],
    wxTimer: ['wxTimer', TimerDTC]
}

def compInfoByName(name):
    for comp in compInfo.keys():
        if comp.__name__ == name: return comp
    raise name+' not found'
    
def loadBitmap(name, subfold = ''):
    try:
        filename = Preferences.toPyPath('Images/Palette/' + subfold + name+'.bmp')
        f = open(filename)
        f.close()
#        if path.exists(filename):
        return wxBitmap(filename, wxBITMAP_TYPE_BMP)
    except:
        return wxBitmap(Preferences.toPyPath('Images/Palette/Component.bmp'), 
          wxBITMAP_TYPE_BMP)
        
    
def bitmapForComponent(wxClass, wxBase = 'None', gray = false):
    # "Aquire" bitmap thru inheritance if necessary
    if gray: sf = 'Gray/'
    else: sf = ''
    if wxBase != 'None': return loadBitmap(wxBase, sf)
    else:
        cls = wxClass
        try: bse = wxClass.__bases__[0]
        except:
            if compInfo.has_key(wxClass):
                return loadBitmap(compInfo[wxClass][0], sf)
            else: 
                return loadBitmap('Component')
        try:
            while not compInfo.has_key(cls):
                cls = bse
                bse = cls.__bases__[0]
                
            return loadBitmap(compInfo[cls][0], sf)
        except:
            print 'not found!'
            return loadBitmap('Component')

#print 'PaletteMapping:', len(locals())
