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

# XXX Think about the following
# XXX Letting users edit this file directly and reload it

import Preferences
from Preferences import IS
from os import path

from wxPython.wx import *
from wxPython.grid import wxGrid
from wxPython.html import wxHtmlWindow
from wxPython.lib.buttons import wxGenButton, wxGenBitmapButton, wxGenToggleButton, wxGenBitmapToggleButton
from wxPython.calendar import wxCalendarCtrl
from wxPython.stc import wxStyledTextCtrl

from Companions.Companions import *
from Companions.UtilCompanions import *
from Companions.DialogCompanions import *
from Companions.Companions import *
from Companions.UtilCompanions import *
from Companions.DialogCompanions import *
from Companions.ZopeCompanions import *

utilities = [wxMenu, wxImageList, wxAcceleratorTable, wxTextDropTarget, wxFileDropTarget]

palette = [
  ['Frame bars', 'Editor/Tabs/Singletons', 
    [wxMenuBar, wxToolBar, wxStatusBar] ],
  ['Containers/Layout', 'Editor/Tabs/Containers', 
    [wxPanel, wxScrolledWindow, wxNotebook, wxSplitterWindow, wxSashWindow,
     wxSashLayoutWindow] ], 
  ['Basic Controls', 'Editor/Tabs/Basic', 
    [wxStaticText, wxTextCtrl, wxComboBox, wxChoice, wxCheckBox, wxRadioButton, 
     wxSlider, wxGauge, wxStaticBox, wxScrollBar, wxStaticBitmap, wxStaticLine, 
     wxHtmlWindow, wxSpinCtrl, wxCalendarCtrl, wxStyledTextCtrl] ],
  ['Buttons', 'Editor/Tabs/Basic',
    [wxButton, wxBitmapButton, wxSpinButton, wxGenButton, wxGenBitmapButton, 
     wxGenToggleButton, wxGenBitmapToggleButton] ],
  ['List Controls', 'Editor/Tabs/Lists', 
    [wxRadioBox, wxListBox, wxCheckListBox, wxGrid, wxListCtrl, wxTreeCtrl] ],
  ['Utilities', 'Editor/Tabs/Utilities', 
    utilities] ]

helperClasses = {
    'wxFontPtr': FontDTC,
    'wxColourPtr': ColourDTC
}    

dialogPalette =  ['Dialogs', 'Editor/Tabs/Dialogs', 
    [wxColourDialog, wxFontDialog, wxFileDialog, wxDirDialog, 
    wxPrintDialog, wxPageSetupDialog, 
    wxSingleChoiceDialog, wxTextEntryDialog, wxMessageDialog] ]

zopePalette =  ['Zope', 'Editor/Tabs/Zope', 
    ['DTML Document', 'DTML Method', 'Folder', 'File', 'Image', 'External Method',
     'Python Method', 'Mail Host', 'ZCatalog', 'User Folder'] ]#'SQL Method', 

compInfo = {
    wxApp: ['wxApp', None],
    wxFrame: ['wxFrame', FrameDTC],
    wxDialog: ['wxDialog', DialogDTC],
    wxMiniFrame: ['wxMiniFrame', MiniFrameDTC],
    wxMDIParentFrame: ['wxMDIParentFrame', MDIParentFrameDTC],
    wxMDIChildFrame: ['wxMDIChildFrame', MDIChildFrameDTC],
    wxMenuBar: ['wxMenuBar', MenuBarDTC],
    wxToolBar: ['wxToolBar', ToolBarDTC],
    wxStatusBar: ['wxStatusBar', StatusBarDTC],
    wxPanel: ['wxPanel', PanelDTC], 
    wxScrolledWindow: ['wxScrolledWindow', ScrolledWindowDTC], 
    wxNotebook: ['wxNotebook', NotebookDTC],
    wxSplitterWindow: ['wxSplitterWindow', SplitterWindowDTC],
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
    wxGrid: ['wxGrid', NYIDTC], 
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
    wxTimer: ['wxTimer', TimerDTC],
    wxStyledTextCtrl: ['wxStyledTextCtrl', NYIDTC],
    wxCalendarCtrl: ['wxCalendarCtrl', NYIDTC],
    wxSpinCtrl: ['wxSpinCtrl', NYIDTC],
    wxGenButton: ['wxGenButton', GenButtonDTC],
    wxGenBitmapButton: ['wxGenBitmapButton', GenBitmapButtonDTC],
    wxGenToggleButton: ['wxGenToggleButton', GenButtonDTC],
    wxGenBitmapToggleButton: ['wxGenBitmapToggleButton', GenBitmapButtonDTC],
    wxTextDropTarget: ['wxTextDropTarget', NYIDTC],
    wxFileDropTarget: ['wxFileDropTarget', NYIDTC],
    wxSashWindow: ['wxSashWindow', SashWindowDTC],
    wxSashLayoutWindow: ['wxSashLayoutWindow', SashLayoutWindowDTC],
    
    'DTML Document': ['DTMLDocument', DTMLDocumentZC], 
    'DTML Method': ['DTMLMethod', DTMLMethodZC], 
    'Folder': ['Folder', FolderZC],
    'File': ['File', FileZC],
    'Image': ['Image', ImageZC],
    'External Method': ['ExternalMethod', ExternalMethodZC],
    'Python Method': ['PythonMethod', PythonMethodZC], 
    'Mail Host': ['MailHost', MailHostZC], 
    'ZCatalog': ['ZCatalog', ZCatalogZC],
#    'SQL Method': ['SQLMethod', SQLMethodZC],
    'User Folder': ['UserFolder', UserFolderZC],
    
}

def compInfoByName(name):
    for comp in compInfo.keys():
        if comp.__name__ == name: return comp
    raise name+' not found'
    
def loadBitmap(name, subfold = ''):
    try:
        return IS.load('Images/Palette/' + subfold + name+'.bmp')
    except:
        return IS.load('Images/Palette/Component.bmp')
        
    
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

#print 'PaletteMapping:', len(locals()

def evalCtrl(expr):
    return eval(expr)