#----------------------------------------------------------------------
# Name:        Palette.py
# Purpose:     Main frame containing palette for visual frame design
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
#Boa:Frame:BoaFrame

import PaletteMapping
print 'imported PaletteMapping'
import Editor
print 'imported Editor'
import Inspector
print 'imported Inspector'
import sender
import ClassBrowser, Help, Preferences
from wxPython.wx import *
from Preferences import logFontSize, IS, toPyPath, flatTools
from ExternalLib.buttons import wxGenButton, wxGenBitmapButton, wxGenToggleButton, wxGenBitmapToggleButton
import Utils
import os

currentMouseOverTip = ''
cyclopsing = 0

wxEVT_NEW_PACKAGE = wxNewId()

def EVT_NEW_PACKAGE(win, func):
    win.Connect(-1, -1, wxEVT_NEW_PACKAGE, func)

class NewPackageEvent(wxPyEvent):
    def __init__(self):
        wxPyEvent.__init__(self)
        self.SetEventType(wxEVT_NEW_PACKAGE)

[wxID_CONTEXTSEARCH] = map(lambda _init_ctrls: wxNewId(), range(1))

[wxID_BOAFRAME] = map(lambda _init_ctrls: wxNewId(), range(1))

class BoaFrame(wxFrame):
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxFrame.__init__(self, size = (-1, -1), id = wxID_BOAFRAME, title = 'Boa Constructor - wxPython GUI Builder', parent = prnt, name = '', style = wxDEFAULT_FRAME_STYLE, pos = (-1, -1))

    def __init__(self, parent, id, app):

        self._init_ctrls(parent)
        self._init_utils()

        self.SetDimensions(0, 0, Preferences.screenWidth - Preferences.windowManagerSide * 2, Preferences.paletteHeight)

        self.app = app
        self.destroying = false

#        self.splitter = wxSplitterWindow(self, -1, style = wxSP_NOBORDER)

        self.widgetSet = {}
        if wxPlatform == '__WXMSW__':
            self.SetIcon(IS.load('Images/Icons/Boa.ico'))

        # Setup toolbar
        self.browser = None
        self.toolBar = wxToolBar(self, -1, style = wxTB_HORIZONTAL|wxNO_BORDER|flatTools)
        self.SetToolBar(self.toolBar)

        self.addTool('Images/Shared/Inspector', 'Inspector', 'Brings the Inspector to the front', self.OnInspectorToolClick)
        self.addTool('Images/Shared/Editor', 'Editor', 'Brings the Editor to the front', self.OnEditorToolClick)
        self.addTool('Images/Shared/ClassBrowser', 'ClassExplorer', 'Opens the Class explorer for wxPython', self.OnExplorerToolClick)
        self.toolBar.AddSeparator()
        self.addTool('Images/Shared/Preferences', 'Preferences', 'Set preferences (not implemented)', self.OnPrefsToolClick)
        self.toolBar.AddSeparator()

        self.componentSB = ComponentSelection(self)

        self.toolBar.AddSeparator()
        self.addTool('Images/Shared/Help', 'Help', 'Show help', self.OnHelpToolClick)
        self.addTool('Images/Shared/wxWinHelp', 'wxWindows help', 'Show help', self.OnWxWinHelpToolClick)
        self.addTool('Images/Shared/PythonHelp', 'Python help', 'Show help', self.OnPythonHelpToolClick)

        # Add additional helpbuttons if defined in the config file
        conf = Utils.createAndReadConfig('Explorer')

        customHelpItems = eval(conf.get('preferences', 'customhelp'))
        self.customHelpItems = {}
        for caption, helpFile in customHelpItems.items():
            mID = wxNewId()
            self.toolBar.AddTool(mID, IS.load('Images/Shared/CustomHelp.bmp'),
              shortHelpString = caption)
            EVT_TOOL(self, mID, self.OnCustomHelpToolClick)
            self.customHelpItems[mID] = (caption, helpFile)

        self.contextHelpSearch = wxTextCtrl(self.toolBar, wxID_CONTEXTSEARCH)
        EVT_TEXT_ENTER(self, wxID_CONTEXTSEARCH, self.OnSearchEnter)
        self.toolBar.AddControl(self.contextHelpSearch)

        if wxPlatform == '__WXGTK__':
            self.toolBar.AddSeparator()
            self.addTool('Images/Shared/CloseWindow', 'Exit', '', self.OnCloseClick)
        self.toolBar.AddSeparator()
        self.toolBar.Realize()

        # Setup palette
        self.palette = wxNotebook(self, -1)

        self.palettePages = []
        self.senders = sender.SenderMapper()
        if Preferences.transparentPaletteBitmaps:
            transpSF = ''
        else:
            transpSF = 'Gray/'


        # XXX Set these from class
        if not cyclopsing:
            # 'New' page
            palettePage = NewPalettePage(self.palette, 'New', 'Images/Palette/'+transpSF, self, self.widgetSet, self.senders, self.componentSB)
            palettePage.addButton('wxApp', None, None, self.OnNewApp, self.OnHint, self.OnHintLeave, wxGenBitmapButton)
            palettePage.addButton('wxFrame', None, None, self.OnNewFrame, self.OnHint, self.OnHintLeave, wxGenBitmapButton)
            palettePage.addButton('wxDialog', None, None, self.OnNewDialog, self.OnHint, self.OnHintLeave, wxGenBitmapButton)
            palettePage.addButton('wxMiniFrame', None, None, self.OnNewMiniFrame, self.OnHint, self.OnHintLeave, wxGenBitmapButton)
            palettePage.addButton('wxMDIParentFrame', None, None, self.OnNewMDIMainFrame, self.OnHint, self.OnHintLeave, wxGenBitmapButton)
            palettePage.addButton('wxMDIChildFrame', None, None, self.OnNewMDIChildFrame, self.OnHint, self.OnHintLeave, wxGenBitmapButton)
            palettePage.addButton('Module', None, None, self.OnNewModule, self.OnHint, self.OnHintLeave, wxGenBitmapButton)
            palettePage.addButton('Package', None, None, self.OnNewPackagePost, self.OnHint, self.OnHintLeave, wxGenBitmapButton)
            palettePage.addButton('Setup', None, None, self.OnNewSetup, self.OnHint, self.OnHintLeave, wxGenBitmapButton)
            palettePage.addButton('Text', None, None, self.OnNewText, self.OnHint, self.OnHintLeave, wxGenBitmapButton)
            self.palettePages.append(palettePage)
            # Normal control pages
            for palette in PaletteMapping.palette:
                palettePage = PalettePage(self.palette, palette[0], 'Images/Palette/'+transpSF, self, self.widgetSet, self.senders, self.componentSB)
                palettePage.addToggleBitmaps(palette[2], self.OnHint, self.OnHintLeave)
                self.palettePages.append(palettePage)
            # Dialog page
            self.dialogPalettePage = PanelPalettePage(self.palette, PaletteMapping.dialogPalette[0], 'Images/Palette/'+transpSF, self, self.widgetSet, self.senders, self.componentSB)
            for dialog in PaletteMapping.dialogPalette[2]:
                self.dialogPalettePage.addButton(PaletteMapping.compInfo[dialog][0],
                  dialog, PaletteMapping.compInfo[dialog][1],
                  self.OnDialogPaletteClick, self.OnHint, self.OnHintLeave, wxGenBitmapButton)
            self.palettePages.append(self.dialogPalettePage)
            # Zope page
            if conf.has_option('explorer', 'zope'):
                self.zopePalettePage = ZopePalettePage(self.palette, PaletteMapping.zopePalette[0], 'Images/Palette/'+transpSF, self, self.widgetSet, self.senders, self.componentSB)
                self.zopePalettePage.addToggleBitmaps(PaletteMapping.zopePalette[2], None, None)
                self.palettePages.append(self.zopePalettePage)
        else:
            palettePage = None

        # Prototype for composites
        # Composites are very much not thought out right now, but basically
        # reflects Frames in Delphi 5. A D5 frame is a composite component
        # for reuse of common control combinations. In implementation it's
        # very much like Delphi's form inheritance, i.e. by changing the parent
        # all children will be updated.
        # Current thoughts on implementation in Boa:
        #    To centralise, I like the idea of storing initialisations in a
        #    sepatate file and using 'import' to load controls into a frame.

##        self.composites = CompositeListCtrlPalPage(self.palette, -1, style = wxLC_SMALL_ICON)
##        self.palette.AddPage(self.composites, 'Composites')
##        self.composites.InsertStringItem(0, 'OK / Cancel buttons')
##        self.composites.InsertStringItem(0, 'Tabbed dialog')
##        self.composites.InsertStringItem(0, 'Name/Value')
##        self.composites.Enable(false)

        # Prototype for templates
        # Templates is a real simple idea, instead of starting from a blank
        # frame, start from a previously saved frame in the templates directory

##        self.templates = TemplateListCtrlPalPage(self.palette, -1, style = wxLC_SMALL_ICON)
##        self.palette.AddPage(self.templates, 'Templates')
##        self.templates.InsertStringItem(0, 'Menu/Toolbar/StatusBar')
##        self.templates.InsertStringItem(0, 'Wizard')
##        self.templates.Enable(false)


##        self.log = wxTextCtrl(self.splitter, -1, '', style = wxTE_MULTILINE | \
##          wxTE_RICH | wxVSCROLL)
##        self.log.SetFont(wxFont(logFontSize, wxSWISS, wxNORMAL, wxNORMAL, false))
##
##        self.splitter.SetMinimumPaneSize(0)
##        self.splitter.SplitVertically(self.palette, self.log)
##        self.splitter.SetSashPosition(Preferences.screenWidth)
##

        self.inspector = Inspector.InspectorFrame(self)

        if cyclopsing:
            self.editor = Editor.EditorFrame(self, -1, self.inspector,
              wxMenu(), self.componentSB, app)
        else:
            self.editor = Editor.EditorFrame(self, -1, self.inspector,
              wxMenu(), self.componentSB, app)#palettePage.menu

        EVT_NEW_PACKAGE(self, self.OnNewPackage)
        EVT_CLOSE(self, self.OnCloseWindow)

    def addTool(self, filename, text, help, func, toggle = false):
        mID = wxNewId()
        self.toolBar.AddTool(mID, IS.load(filename+'.bmp'), #wxBitmap(filename+'.bmp', wxBITMAP_TYPE_BMP),
          shortHelpString = text, isToggle = toggle)
        EVT_TOOL(self, mID, func)
        return mID

##    def OnClick(self, event):
##        self.componentSB.SetStatusText('Palette Click'+`event.GetId()`)

    def OnOpenToolClick(self, event):
        dlg = wxFileDialog(self, "Choose a file", ".", "", "*.*", wxOPEN)
        if dlg.ShowModal() == wxID_OK:
            self.editor.addFile(dlg.GetFilename())
        dlg.Destroy()

    def OnInspectorToolClick(self, event):
        self.inspector.Show(true)
        if self.inspector.IsIconized():
            self.inspector.Iconize(false)
        self.inspector.Raise()

    def OnHelpToolClick(self, event):
        if self.componentSB.selection:
            Help.showHelp(self, Help.wxWinHelpFrame,
              self.componentSB.selection[2].wxDocs, self.toolBar)
        else:
            Help.showHelp(self, Help.BoaHelpFrame, '', self.toolBar)

    def OnWxWinHelpToolClick(self, event):
        Help.showHelp(self, Help.wxWinHelpFrame, '', self.toolBar)

    def OnPythonHelpToolClick(self, event):
        Help.showHelp(self, Help.PythonHelpFrame, '', self.toolBar)

    def OnCustomHelpToolClick(self, event):
        caption, helpFile = self.customHelpItems[event.GetId()]
        help = Help.CustomHelpFrame(self, os.path.dirname(helpFile),
            os.path.basename(helpFile), self.toolBar)
        help.loadPage(helpFile)
        help.Show(true)

    def OnPrefsToolClick(self, event):
##        print 'inspector', sys.getrefcount(self.inspector)
##        print 'editor', sys.getrefcount(self.editor)
        self.editor.openOrGotoModule(toPyPath('Preferences.py'))

    def OnLeave(self, event):
        self.componentSB.setHint('')

    def OnNewClick(self, event):
        pass

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
        self.editor.addNewAppPage()

    def OnNewModule(self, event):
        self.editor.addNewModulePage()

    def OnNewText(self, event):
        self.editor.addNewTextPage()

    def OnNewSetup(self, event):
        self.editor.addNewSetupPage()

##    def OnNewWidget(self, event):
##        pass

    def OnNewPackagePost(self, event):
        wxPostEvent(self, NewPackageEvent())

    def OnNewPackage(self, event):
        self.editor.addNewPackage()

    def OnDialogPaletteClick(self, event):
        cls, cmp = self.dialogPalettePage.widgets[`event.GetId()`][1:]
        self.editor.addNewDialog(cls, cmp)

    def OnZopePaletteClick(self, event):
        cls, cmp = self.zopePalettePage.widgets[`event.GetId()`][1:]

    def OnHint(self, event):
        pass

    def OnHintLeave(self, event):
        self.componentSB.setHint('')

    def OnEditorToolClick(self, event):
        self.editor.Show(true)
        if self.editor.IsIconized():
            self.editor.Iconize(false)
        self.editor.Raise()

    def OnExplorerToolClick(self, event):
        if not self.browser:
            self.browser = ClassBrowser.ClassBrowserFrame(self, -1, "Class explorer")
        self.browser.Show(true)
        self.browser.Raise()

    def OnComposeClick(self, event):
        pass
    def OnInheritClick(self, event):
        pass

    def OnCloseClick(self, event):
        self.Close()

    def OnCloseWindow(self, event):
        self.Show(false)
        self.destroying = true
        try:
            if hasattr(self, 'editor') and self.editor:
                self.editor.destroying = true
                self.editor.Close()

            if hasattr(self, 'inspector'):
                self.inspector.destroying = true
                self.inspector.Close()

                if hasattr(self, 'app'):
                    self.app.quit = true
                    self.app = None

            for page in self.palettePages:
                page.destroy()

        finally:
            self.Destroy()
            event.Skip()

    def OnUncheckComponent(self, event):
        self.componentSB.selectNone()

    def OnSearchEnter(self, event):
        Help.showContextHelp(self, self.toolBar, self.contextHelpSearch.GetValue())
        event.Skip()

class ComponentSelection:
    """ Controls the selection of the palette and access to associated
        palette mapping structures. Accessed by the Designer """
    def __init__(self, palette):
        wID = wxNewId()
        self.selComp = wxCheckBox(palette.toolBar, wID, '  (Nothing selected)', size = wxSize(120, 20))
        self.selComp.Enable(false)
        EVT_CHECKBOX(self.selComp, wID, palette.OnUncheckComponent)
        palette.toolBar.AddControl(self.selComp)

        cId = palette.addTool('Images/Shared/Compose', 'Compose', ' ', palette.OnComposeClick, toggle = true)
        iId = palette.addTool('Images/Shared/Inherit', 'Inherit', ' ', palette.OnInheritClick, toggle = true)
        palette.toolBar.ToggleTool(cId, true)
        palette.toolBar.EnableTool(iId, false)

        self.selection = None
        self.prevPage = None

    def selectComponent(self, page, detail):
        if self.prevPage: self.prevPage.selectNone()
        self.selection = detail
        self.prevPage = page
        self.selComp.Enable(true)
        self.selComp.SetLabel('  '+detail[0])
        self.selComp.SetValue(true)

    def selectNone(self):
        if self.prevPage: self.prevPage.selectNone()
        self.selection = None
        self.selComp.Enable(false)
        self.selComp.SetLabel('  (Nothing selected)')
        self.selComp.SetValue(false)

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
        self.selCompose = wxRadioButton(self, -1, 'Compose', wxPoint(320, 3), wxSize(70, 15))
        self.selCompose.SetValue(true)
        self.selInherit = wxRadioButton(self, -1, 'Inherit', wxPoint(400, 3), wxSize(55, 15))
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
    defX = 5
    defY = 3
    def __init__(self, parent, name, bitmapPath, eventOwner, widgets, senders, statusbar):
        wxPanel.__init__(self, parent, -1)

        self.statusbar = statusbar
        self.senders = senders
        self.name = name
        self.bitmapPath = bitmapPath
        self.posX = self.defX
        self.posY = self.defY
        self.widgets = widgets
        parent.AddPage(self, name)
        self.eventOwner = eventOwner

##    def __del__(self):
##        print '__del__', self.__class__.__name__

    def destroy(self):
        del self.senders
        del self.widgets
#        pass

    def addButton(self, widgetName, wxClass, constrClass, clickEvt, hintFunc, hintLeaveFunc, btnType):
        bmp = self.getButtonBmp(widgetName, wxClass)
        width = bmp.GetWidth() + 7
        height = bmp.GetHeight() + 7

        mID = wxNewId()

        newButton = btnType(self, mID, None, wxPoint(self.posX, self.posY),
                           wxSize(width, height))

        newButton.SetBezelWidth(1)
        newButton.SetUseFocusIndicator(0)
        newButton.SetToolTipString(widgetName)
        mask = wxMaskColour(bmp, wxColour(255, 0, 255))
        bmp.SetMask(mask)
        newButton.SetBitmapLabel(bmp)

        EVT_BUTTON(self, mID, clickEvt)

        self.senders.addObject(newButton)
        self.widgets[`mID`] = (widgetName, wxClass, constrClass)
        self.posX = self.posX + bmp.GetWidth() + 11

        return mID

    def getButtonBmp(self, name, wxClass):
        return IS.load('%s%s.bmp' %(self.bitmapPath, name))
#        return wxBitmap('%s%s.bmp' %(self.bitmapPath, name), wxBITMAP_TYPE_BMP)

class NewPalettePage(PanelPalettePage):
    def __init__(self, parent, name, bitmapPath, eventOwner, widgets, senders, statusbar):
        PanelPalettePage.__init__(self, parent, name, bitmapPath, eventOwner, widgets, senders, statusbar)
        self.menu = wxMenu()
        self.selection = None

    def destroy(self):
        self.menu.Destroy()
        PanelPalettePage.destroy(self)

    def addButton(self, widgetName, wxClass, constrClass, clickEvt, hintFunc, hintLeaveFunc, btnType):
        mID = PanelPalettePage.addButton(self, widgetName, wxClass, constrClass, clickEvt, hintFunc, hintLeaveFunc, btnType)
        self.menu.Append(mID, widgetName)
        EVT_MENU(self, mID, clickEvt)
        return mID

class PalettePage(PanelPalettePage):
    def __init__(self, parent, name, bitmapPath, eventOwner, widgets, senders, statusbar):
        PanelPalettePage.__init__(self, parent, name, bitmapPath, eventOwner, widgets, senders, statusbar)
        self.clickEvt = None
        self.selection = None

    def addToggleBitmaps(self, classes, hintFunc, hintLeaveFunc):
#        self.clickEvt = clickEvt
        for wxClass in classes:
            ci = PaletteMapping.compInfo[wxClass]
            self.addButton(ci[0], wxClass, ci[1], self.OnClickTrap, hintFunc, hintLeaveFunc, wxGenBitmapToggleButton)

    def OnClickTrap(self, event):
        obj = self.senders.getBtnObject(event)
        if obj.up:
            self.selectNone()
            self.statusbar.selectNone()
        else:
            self.statusbar.selectComponent(self, self.widgets[`event.GetId()`])
            self.selection = obj

    def selectNone(self):
        if self.selection:
            self.selection.SetToggle(false)
            self.selection.Refresh()
            self.selection = None

class ZopePalettePage(PalettePage):
    def __init__(self, parent, name, bitmapPath, eventOwner, widgets, senders, statusbar):
        PalettePage.__init__(self, parent, name, bitmapPath, eventOwner, widgets, senders, statusbar)

    def getButtonBmp(self, name, wxClass):
        return IS.load('%s%s.bmp' %(self.bitmapPath, name))
