#----------------------------------------------------------------------
# Name:        Palette.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

import PaletteMapping
print 'imported PaletteMapping' 
import Editor
print 'imported Editor' 
import Inspector
print 'imported Inspector' 
import string
import sender
import ClassBrowser, Help, Preferences
from wxPython.wx import *
from Preferences import logFontSize
from wxPython.lib.buttons import wxGenButton, wxGenBitmapButton, \
                                 wxGenToggleButton, wxGenBitmapToggleButton
currentMouseOverTip = ''

class BoaFrame(wxFrame):
    def __init__(self, parent, id, title, app):
        wxFrame.__init__(self, parent, -1, title, wxPoint(0, 0), 
          wxSize(Preferences.screenWidth, Preferences.paletteHeight))
        self.app = app
        
        self.splitter = wxSplitterWindow(self, -1, style = wxSP_NOBORDER)
                
        wxToolTip_Enable(TRUE) 
        self.widgetSet = {}
        if wxPlatform == '__WXMSW__':
            self.icon = wxIcon('Images/Icons/Boa.ico', wxBITMAP_TYPE_ICO)
            self.SetIcon(self.icon)

        self.palette = wxNotebook(self.splitter, -1)

        palettePages = []
        self.senders = sender.SenderMapper()
        if Preferences.transparentPaletteBitmaps:
            transpSF = ''
        else:
            transpSF = 'Gray/'


        self.componentSB = ComponentStatusBar(self)
        self.SetStatusBar(self.componentSB)
	
	# XXX Set these from class
        palettePage = PanelPalettePage(self.palette, 'New', 'Images/Palette/'+transpSF, self, self.widgetSet, self.senders, self.componentSB)       
        palettePage.addButton('wxApp', None, None, self.OnNewApp, self.OnHint, self.OnHintLeave, wxGenBitmapButton)
        palettePage.addButton('wxFrame', None, None, self.OnNewFrame, self.OnHint, self.OnHintLeave, wxGenBitmapButton)
        palettePage.addButton('wxDialog', None, None, self.OnNewDialog, self.OnHint, self.OnHintLeave, wxGenBitmapButton)
        palettePage.addButton('wxMiniFrame', None, None, self.OnNewMiniFrame, self.OnHint, self.OnHintLeave, wxGenBitmapButton)
        palettePage.addButton('wxMDIParentFrame', None, None, self.OnNewMDIMainFrame, self.OnHint, self.OnHintLeave, wxGenBitmapButton)
        palettePage.addButton('wxMDIChildFrame', None, None, self.OnNewMDIChildFrame, self.OnHint, self.OnHintLeave, wxGenBitmapButton)
        palettePage.addButton('Module', None, None, self.OnNewModule, self.OnHint, self.OnHintLeave, wxGenBitmapButton)
        palettePage.addButton('Package', None, None, self.OnNewPackage, self.OnHint, self.OnHintLeave, wxGenBitmapButton)
        palettePage.addButton('Text', None, None, self.OnNewText, self.OnHint, self.OnHintLeave, wxGenBitmapButton)
        palettePages.append(palettePage)
        for palette in PaletteMapping.palette:
            palettePage = PalettePage(self.palette, palette[0], 'Images/Palette/'+transpSF, self, self.widgetSet, self.senders, self.componentSB)
            palettePage.addToggleBitmaps(palette[2], self.OnPaletteClick, self.OnHint, self.OnHintLeave)
            palettePages.append(palettePage)
        
        self.dialogPalettePage = PanelPalettePage(self.palette, PaletteMapping.dialogPalette[0], 'Images/Palette/'+transpSF, self, self.widgetSet, self.senders, self.componentSB)       
        for dialog in PaletteMapping.dialogPalette[2]:
            self.dialogPalettePage.addButton(PaletteMapping.compInfo[dialog][0], 
              dialog, PaletteMapping.compInfo[dialog][1],  
              self.OnDialogPaletteClick, self.OnHint, self.OnHintLeave, wxGenBitmapButton)
        palettePages.append(self.dialogPalettePage)

        # Prototype for composites
        # Composites are very much not thought out right now, but basically
        # reflects Frames in Delphi 5. A D5 frame is a composite component
        # for reuse of common control combinations. In implementation it's
        # very much like Delphi's form inheritance, i.e. by changing the parent
        # all children will be updated.
        # Current thoughts on implementation in Boa:
        #    To centralise, I like the idea of storing initialisations in a 
        #    sepatate file and using 'import' to load controls into a frame.
        
        self.composites = CompositeListCtrlPalPage(self.palette, -1, style = wxLC_SMALL_ICON)
        self.palette.AddPage(self.composites, 'Composites')
        self.composites.InsertStringItem(0, 'OK / Cancel buttons')
        self.composites.InsertStringItem(0, 'Tabbed dialog')
        self.composites.InsertStringItem(0, 'Name/Value')
        self.composites.Enable(false)

        # Prototype for templates
        # Templates is a real simple idea, instead of starting from a blank
        # frame, start from a previously saved frame in the templates directory
        
        self.templates = TemplateListCtrlPalPage(self.palette, -1, style = wxLC_SMALL_ICON)
        self.palette.AddPage(self.templates, 'Templates')
        self.templates.InsertStringItem(0, 'Menu/Toolbar/StatusBar')
        self.templates.InsertStringItem(0, 'Wizard')
        self.templates.Enable(false)

        self.browser = None
        self.toolBar = wxToolBar(self, -1)
        self.SetToolBar(self.toolBar)

        self.addTool('Images/Shared/Inspector', 'Inspector', 'Brings the Inspector to the front', self.OnInspectorToolClick)
        self.addTool('Images/Shared/Editor', 'Editor', 'Brings the Editor to the front', self.OnEditorToolClick)
        self.addTool('Images/Shared/ClassBrowser', 'Classexplorer', 'Opens the Class explorer for wxPython', self.OnExplorerToolClick)
        self.toolBar.AddSeparator()
        self.addTool('Images/Shared/Preferences', 'Preferences', 'Set preferences (not implemented)', self.OnPrefsToolClick)
        self.toolBar.AddSeparator()
        self.addTool('Images/Shared/Help', 'Help', 'Show help', self.OnHelpToolClick)
        self.addTool('Images/Shared/wxWinHelp', 'wxWindows help', 'Show help', self.OnWxWinHelpToolClick)
        self.addTool('Images/Shared/PythonHelp', 'Python help', 'Show help', self.OnPythonHelpToolClick)
        if wxPlatform == '__WXGTK__':
            self.toolBar.AddSeparator()
            self.addTool('Images/Shared/CloseWindow', 'Exit', '', self.OnCloseClick)
        self.toolBar.Realize()

        self.log = wxTextCtrl(self.splitter, -1, '', style = wxTE_MULTILINE | \
          wxTE_RICH | wxVSCROLL)
        self.log.SetFont(wxFont(logFontSize, wxSWISS, wxNORMAL, wxNORMAL, false))

        self.splitter.SetMinimumPaneSize(0)
        self.splitter.SplitVertically(self.palette, self.log)
        self.splitter.SetSashPosition(Preferences.screenWidth)

        self.inspector = Inspector.InspectorFrame(self, -1, 'Inspector')
        self.editor = Editor.EditorFrame(self, -1, 'Editor', self.inspector, self.componentSB, app)

    def addTool(self, filename, text, help, func):
        mID = NewId()
        self.toolBar.AddTool(mID, wxBitmap(filename+'.bmp', wxBITMAP_TYPE_BMP),
          shortHelpString = text)
        EVT_TOOL(self, mID, func)
    
    def OnClick(self, event):
    	self.componentSB.SetStatusText('Palette Click'+`event.GetId()`)

    def OnOpenToolClick(self, event):
        dlg = wxFileDialog(self, "Choose a file", ".", "", "*.*", wxOPEN)
        if dlg.ShowModal() == wxID_OK:
            self.editor.addFile(dlg.GetFilename())
        dlg.Destroy()

    def OnInspectorToolClick(self, event):
        self.inspector.Show(true)
	
    def OnDesignerToolClick(self, event):
        self.editor.showDesigner()

    def OnHelpToolClick(self, event):
        if self.componentSB.selection:
            Help.showHelp(self, Help.wxWinHelpFrame, self.componentSB.selection[2].wxDocs)
        else:
            Help.showHelp(self, Help.BoaHelpFrame, '')

    def OnWxWinHelpToolClick(self, event):
        Help.showHelp(self, Help.wxWinHelpFrame, '')

    def OnPythonHelpToolClick(self, event):
        Help.showHelp(self, Help.PythonHelpFrame, '')
	
    def OnPrefsToolClick(self, event):
        pass
		    
    def OnLeave(self, event):
        self.componentSB.setHint('')

    def OnNewFrame(self, event):
        self.editor.addNewFramePage('Frame')

    def OnNewDialog(self, event):
        self.editor.addNewFramePage('Dialog')

    def OnNewMiniFrame(self, event):
        self.editor.addNewFramePage('MiniFrame')

    def OnNewMDIMainFrame(self, event):
        self.editor.addNewFramePage('MDIParent')

    def OnNewMDIChildFrame(self, event):
        self.editor.addNewFramePage('MDIChild')

    def OnFileExit(self, event):
        self.Close()

    def OnNewApp(self, event):
        print "print here"
        self.editor.addNewAppPage()
        
    def OnNewModule(self, event):
        print 'On new module', event, dir(event), event.GetIsDown()
        
        self.editor.addNewModulePage()

    def OnNewText(self, event):
        self.editor.addNewTextPage()

    def OnNewWidget(self, event):
        pass
    def OnNewPackage(self, event):
        self.editor.addNewPackage()
        pass
    
    def OnPaletteClick(self, event):
        pass

    def OnDialogPaletteClick(self, event):
        cls, cmp = self.dialogPalettePage.widgets[`event.GetId()`][1:]
        self.editor.addNewDialog(cls, cmp)

    def OnHint(self, event):
        pass

        #linux mod self.componentSB.setHint(self.senders.getObject(event).GetLabel())

    def OnHintLeave(self, event):
        self.componentSB.setHint('')

    def OnEditorToolClick(self, event):
        self.editor.Show(true)

    def OnExplorerToolClick(self, event):
        if not self.browser:
	    self.browser = ClassBrowser.ClassBrowserFrame(self, -1, "Class explorer")
        self.browser.Show(true)
    
    def OnCloseClick(self, event):
        self.Close()
    
    def OnCloseWindow(self, event):
        if self.editor:
##            if self.editor.modules:
##                for mod in self.editor.modules.values():
##                    if mod.model.views.has_key('Designer'):
##                        wxMessageBox("Can't close while there are open designers")
##                        return            
            self.editor.Close()

##        self.inspector.Close()
        self.app.quit = true
#        print 'Close window'
        self.app = None
        self.Destroy()
        event.Skip()

class ComponentStatusBar(wxStatusBar):
    """ Controls the selection of the palette and access to associated
        palette mapping structures. Accessed by the Designer """
    def __init__(self, parent):
        wxStatusBar.__init__(self, parent, -1, style = wxST_SIZEGRIP)
	self.SetFieldsCount(4)
	self.SetStatusWidths([150, 150, 170, -1])
	wID = NewId()
	self.hint = wxStaticText(self, -1, '', wxPoint(7, 4))
	self.selComp = wxCheckBox(self, wID, '', wxPoint(157, 4), wxSize(140, 15))
	self.selComp.Enable(false)
	EVT_CHECKBOX(self.selComp, wID, self.OnUncheck)
	self.selCompose = wxRadioButton(self, -1, 'Compose', wxPoint(310, 4), wxSize(65, 15))
	self.selCompose.SetValue(true)
	self.selInherit = wxRadioButton(self, -1, 'Inherit', wxPoint(400, 4), wxSize(55, 15))
	self.selInherit.Enable(false)

        self.selection = None
        self.prevPage = None

        dc = wxClientDC(self)
        dc.SetFont(self.GetFont())
        (w,h) = dc.GetTextExtent('X')
        h = int(h * 1.8)
        self.SetSize(wxSize(100, h-1))

    def selectComponent(self, page, detail):
        if self.prevPage: self.prevPage.selectNone()
        self.selection = detail
        self.prevPage = page
        self.selComp.Enable(true)
        self.selComp.SetLabel(detail[0])
        self.selComp.SetValue(true)

    def selectNone(self):
        if self.prevPage: self.prevPage.selectNone()
        self.selection = None
        self.selComp.Enable(false)
        self.selComp.SetLabel('')
        self.selComp.SetValue(false)

    def setHint(self, text):
        self.hint.SetLabel(text)        
                
    def OnUncheck(self, event):
        self.selectNone()
        
class BasePalettePage:
    pass
class ListCtrlPalettePage(wxListCtrl, BasePalettePage):
    pass
class CompositeListCtrlPalPage(ListCtrlPalettePage):
    pass
class TemplateListCtrlPalPage(ListCtrlPalettePage):
    pass
    
class PanelPalettePage(wxPanel, BasePalettePage):
    def __init__(self, parent, name, bitmapPath, eventOwner, widgets, senders, statusbar):
        wxPanel.__init__(self, parent, -1)
	
        self.statusbar = statusbar
        self.senders = senders
        self.name = name
        self.bitmapPath = bitmapPath
        self.pos = 5
        self.widgets = widgets
        parent.AddPage(self, name)
        self.eventOwner = eventOwner
        EVT_MOTION(self, self.OnHintDesc)
        EVT_LEAVE_WINDOW(self, self.OnHintLeave)

    def addButton(self, widgetName, wxClass, constrClass, clickEvt, hintFunc, hintLeaveFunc, btnType):
        bmp = self.getButtonBmp(widgetName, wxClass)
        mID = NewId()
        newButton = btnType(self, mID, None, wxPoint(self.pos, 3),
                           wxSize(bmp.GetWidth()+ 7, bmp.GetHeight()+7))
        newButton.SetBezelWidth(1)
        newButton.SetToolTipString(widgetName)
        mask = wxMaskColour(bmp, wxColour(255, 0, 255))
        bmp.SetMask(mask)
        newButton.SetBitmapLabel(bmp)

        EVT_BUTTON(self,mID,clickEvt)

        self.senders.addObject(newButton)
       	
        self.widgets[`mID`] = (widgetName, wxClass, constrClass)
       	
        self.pos = self.pos + bmp.GetWidth() + 11
    
    def getButtonBmp(self, name, wxClass):
        return wxBitmap('%s%s.bmp' %(self.bitmapPath, name), wxBITMAP_TYPE_BMP)
                
    def OnHintDesc(self, event):
        pass

    def OnHintLeave(self, event):
        pass
    
class PalettePage(PanelPalettePage):
    def __init__(self, parent, name, bitmapPath, eventOwner, widgets, senders, statusbar):
        PanelPalettePage.__init__(self, parent, name, bitmapPath, eventOwner, widgets, senders, statusbar)
        self.clickEvt = None
        self.selection = None

    def addToggleBitmaps(self, classes, clickEvt, hintFunc, hintLeaveFunc):
        self.clickEvt = clickEvt
	for wxClass in classes:
	    ci = PaletteMapping.compInfo[wxClass]
	    self.addButton(ci[0], wxClass, ci[1], self.OnClickTrap, hintFunc, hintLeaveFunc, wxGenBitmapToggleButton)

    def getButtonBmp(self, name, wxClass):
	return PaletteMapping.bitmapForComponent(wxClass, gray = not Preferences.transparentPaletteBitmaps)

    def OnClickTrap(self, event):
        print 'on click trap', event
        obj = self.senders.getBtnObject(event)
        if obj.up:
            self.selectNone()
            self.statusbar.selectNone()
        else:
            self.statusbar.selectComponent(self, self.widgets[`event.GetId()`])
            self.selection = obj

    def selectNone(self):
        print 'select none'
        if self.selection:
            print 'select none 2'
            self.selection.SetToggle(false)
            self.selection.Refresh()
            self.selection = None



