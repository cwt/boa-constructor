#----------------------------------------------------------------------
# Name:        EditorViews.py
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
from wxPython.html import *
import PaletteMapping, Debugger, Search
import string
import os
from os import path
from Utils import AddToolButtonBmpObject
from wxPython.lib.editor import wxPyEditor
from moduleparse import CodeBlock

# XXX Add close option to source

wxwHeaderTemplate ='''<html>
<head>
   <title>Boa doc</title>
</head>
<body bgcolor="#FFFFFF">'''

wxwModuleTemplate = """
<h1>[[Module]]</h1>
[[ModuleSynopsis]]
<p><b><font color="#FF0000">Classes</font></b><br>
<p>[[ClassList]]
<hr>
"""

wxwAppModuleTemplate = """
<h1>[[Module]]</h1>
[[ModuleSynopsis]]
<p><b><font color="#FF0000">Modules</font></b><br>
<p>[[ModuleList]]
<br>
<p><b><font color="#FF0000">Classes</font></b><br>
<p>[[ClassList]]
<hr>
"""

wxwClassTemplate = """
<a NAME="[[Class]]"></a>
<h2>[[Class]]</h2>
[[ClassSynopsis]]
<p><b><font color="#FF0000">Derived from</font></b>
<p>[[ClassSuper]]
<p><b><font color="#FF0000">Methods</font></b>
<p>
[[MethodList]]
<p>
[[MethodDetails]]
<hr>
<center>
*</center>
"""
wxwMethodTemplate = '''
<hr><a NAME="[[Class]][[Method]]"></a>
<h3>
[[Class]].[[Method]]</h3>
<b>[[Method]]</b>(<i>[[Params]])
<p>&nbsp;[[MethodSynopsis]]
<p>
'''

wxwFooterTemplate = """</body>
</html>
"""

staticInfoPrefs = { 'Purpose':   '',
                    'Author':    'Riaan Booysen',
                    'Copyright': '(c) 1999, 2000 Riaan Booysen',
                    'Licence':   'GPL'}


class EditorView:
    def __init__(self, actions = [], dclickActionIdx = -1):
        self.modified = false 
        EVT_RIGHT_DOWN(self, self.OnRightDown)
        # for wxMSW
        EVT_COMMAND_RIGHT_CLICK(self, -1, self.OnRightClick)
        # for wxGTK
        EVT_RIGHT_UP(self, self.OnRightClick)
            
        self.menu = wxMenu()
        self.popx = self.popy = 0

        for id, name, meth in actions:
            self.menu.Append(id, name)
            EVT_MENU(self, id, meth)
    
        if dclickActionIdx < len(actions) and dclickActionIdx > -1:
            EVT_LEFT_DCLICK(self, actions[dclickActionIdx][2])

    def addViewTools(self, toolbar):
        pass

    docked = true
    def addToNotebook(self, notebook):
        self.notebook = notebook
        notebook.AddPage(self, self.viewName)
        self.pageIdx = notebook.GetPageCount() -1
        self.modified =  false
        self.readOnly = false

    def activate(self):
        self.active = true
        if self.modified: self.refresh()
        
    def deactivate(self):
        self.active = false
            
    def update(self):
        self.modified = true
        if self.active:
##            try: self.refresh()
##            except Exception, message: print Exception, message
            self.refresh()
	
    def refresh(self):
        self.refreshCtrl()
        self.modified = false

    def refreshModel(self):
        """ Override this to apply changes in your view to the model """
        self.model.update()
        self.model.notify()
    
    def focus(self):
        wxYield()
        self.notebook.SetSelection(self.pageIdx)
        self.notebook.Refresh()
#        self.model.editor.setupToolBar(viewIdx = self.pageIdx)
    
    def setReadOnly(self, val):
        self.readOnly = val
    
    def close(self):
        pass 

    def isModified(self):
        return self.modified 
    
    def OnRightDown(self, event):
        self.popx = event.GetX()
        self.popy = event.GetY()

    def OnRightClick(self, event):
        self.PopupMenu(self.menu, wxPoint(self.popx, self.popy))
            
class TestView(wxTextCtrl, EditorView):
    viewName = 'Test'
    def __init__(self, parent, model):
        wxTextCtrl.__init__(self, parent, -1, '', style = wxTE_MULTILINE | wxTE_RICH | wxHSCROLL)
        EditorView.__init__(self, (), 5)
        self.active = true
        self.model = model
        
    def refreshCtrl(self):
        self.SetValue('')

class TextView(wxTextCtrl, EditorView):
    # XXX Factor base class for Text & Source
    viewName = 'Text'
    def __init__(self, parent, model):
        wxTextCtrl.__init__(self, parent, -1, '', style = wxTE_MULTILINE | \
          wxTE_RICH | wxHSCROLL)
        EditorView.__init__(self, ((NewId(), 'Refresh', self.OnRefresh),), 0)
        self.active = true
        self.model = model
        self.SetFont(wxFont(9, wxDEFAULT, wxNORMAL, wxNORMAL, false))
        EVT_KEY_UP(self, self.OnKeyDown) 

    def setReadOnly(self, val):
        EditorView.readOnly(self, val)
        self.SetEditable(val)
    
    def refreshCtrl(self):
#        self.SetValue('')
        self.SetValue(self.model.data)
        self.SetInsertionPoint(0)
        self.DiscardEdits()
        self.updatePageName()
    
    def refreshModel(self):
        src = self.GetValue()
        lns = string.split(src, os.linesep)
        src = string.join(lns, '\012')
        self.model.data = src
        if self.IsModified():
            self.model.modified = true
            self.DiscardEdits()
        EditorView.refreshModel(self) 
    
    def OnRefresh(self, event):
        self.refreshModel()
        self.model.editor.updateModulePage(self.model)
        self.model.editor.updateTitle()
    
    def updatePageName(self):
        currName = self.notebook.GetPageText(self.pageIdx)
        if self.IsModified(): newName = '~%s~'%self.viewName
        else: newName = self.viewName

        if currName != newName:
            self.notebook.SetPageText(self.pageIdx, newName)
	    self.notebook.Refresh()

    def updateStatusBar(self):
        rc = self.PositionToXY(self.GetInsertionPoint())
        self.model.editor.updateStatusRowCol(rc[0], rc[1])
    
    def gotoLine(self, lineno):
        self.SetInsertionPoint(self.XYToPosition(0, lineno))
    
    def selectLine(self, lineno):
        self.gotoLine(lineno)
        length = self.GetLineLength(lineno)
        startPos = self.XYToPosition(0, lineno)
        endPos = self.XYToPosition(length, lineno)
        self.SetSelection(startPos, endPos)

    def OnKeyDown(self, event):
        event.Skip()
        self.updatePageName()
        self.updateStatusBar()
#            self.tabs.ResizeChildren();

[wxID_SOURCECUT, wxID_SOURCECOPY, wxID_SOURCEPASTE, wxID_SOURCEUNDO, wxID_SOURCEREDO] = map(lambda x: NewId(), range(5))
class SourceView(wxTextCtrl, EditorView):
    viewName = 'Source'
    refreshBmp = wxBitmap('Images/Editor/Refresh.bmp', wxBITMAP_TYPE_BMP)
    undoBmp = wxBitmap('Images/Shared/Undo.bmp', wxBITMAP_TYPE_BMP)
    redoBmp = wxBitmap('Images/Shared/Redo.bmp', wxBITMAP_TYPE_BMP)
    cutBmp = wxBitmap('Images/Shared/Cut.bmp', wxBITMAP_TYPE_BMP)
    copyBmp = wxBitmap('Images/Shared/Copy.bmp', wxBITMAP_TYPE_BMP)
    pasteBmp = wxBitmap('Images/Shared/Paste.bmp', wxBITMAP_TYPE_BMP)
    findBmp = wxBitmap('Images/Shared/Find.bmp', wxBITMAP_TYPE_BMP)
    findAgainBmp = wxBitmap('Images/Shared/FindAgain.bmp', wxBITMAP_TYPE_BMP)
    breakBmp = wxBitmap('Images/Debug/Breakpoints.bmp', wxBITMAP_TYPE_BMP)
    runCrsBmp = wxBitmap('Images/Editor/RunToCursor.bmp', wxBITMAP_TYPE_BMP)
    runBmp = wxBitmap('Images/Debug/Run.bmp', wxBITMAP_TYPE_BMP)
    debugBmp = wxBitmap('Images/Debug/Debug.bmp', wxBITMAP_TYPE_BMP)
    modInfoBmp = wxBitmap('Images/Modules/InfoBlock.bmp', wxBITMAP_TYPE_BMP)
    def __init__(self, parent, model):
        wxTextCtrl.__init__(self, parent, -1, '', style = wxTE_MULTILINE | \
          wxTE_RICH | wxHSCROLL | wxVSCROLL)
        EditorView.__init__(self, ((NewId(), 'Refresh', self.OnRefresh),
                                   (-1, '-', None),
                                   (NewId(), 'Undo', self.OnEditUndo),
                                   (NewId(), 'Redo', self.OnEditRedo),
                                   (-1, '-', None),
                                   (NewId(), 'Cut', self.OnEditCut),
                                   (NewId(), 'Copy', self.OnEditCopy),
                                   (NewId(), 'Paste', self.OnEditPaste),
                                   (-1, '-', None),
                                   (NewId(), 'Find', self.OnFind),
                                   (NewId(), 'Find again', self.OnFindAgain),
                                   (-1, '-', None),
                                   (NewId(), 'Run', self.OnRun),
                                   (NewId(), 'Debug', self.OnDebug),
                                   (-1, '-', None),
                                   (NewId(), 'Set breakpoint', self.OnSetBreakPoint),
                                   (NewId(), 'Run to cursor', self.OnRunToCursor),
                                   (-1, '-', None),
                                   (NewId(), 'Add module info', self.OnAddModuleInfo)), -1)
        self.active = true
        self.model = model
        self.pos = 0
        self.nonUserModification  = false 
        self.SetFont(wxFont(9, wxMODERN, wxNORMAL, wxNORMAL, false))

        self.lastSearchResults = []
        self.lastSearchPattern = ''
        self.lastMatchPosition = None

        EVT_KEY_UP(self, self.OnKeyDown) 

    def addViewTools(self, toolbar):
        AddToolButtonBmpObject(self.model.editor, toolbar, self.refreshBmp, 'Refresh from source code', self.OnRefresh)
        toolbar.AddSeparator() 
        AddToolButtonBmpObject(self.model.editor, toolbar, self.undoBmp, 'Undo', self.OnEditUndo)
        AddToolButtonBmpObject(self.model.editor, toolbar, self.redoBmp, 'Redo', self.OnEditRedo)
        toolbar.AddSeparator() 
        AddToolButtonBmpObject(self.model.editor, toolbar, self.cutBmp, 'Cut', self.OnEditCut)
        AddToolButtonBmpObject(self.model.editor, toolbar, self.copyBmp, 'Copy', self.OnEditCopy)
        AddToolButtonBmpObject(self.model.editor, toolbar, self.pasteBmp, 'Paste', self.OnEditPaste)
        toolbar.AddSeparator() 
        AddToolButtonBmpObject(self.model.editor, toolbar, self.findBmp, 'Find', self.OnFind)
        AddToolButtonBmpObject(self.model.editor, toolbar, self.findAgainBmp, 'Find again', self.OnFindAgain)
        toolbar.AddSeparator() 
        AddToolButtonBmpObject(self.model.editor, toolbar, self.runBmp, 'Run', self.OnRun)
        AddToolButtonBmpObject(self.model.editor, toolbar, self.debugBmp, 'Debug', self.OnDebug)
        toolbar.AddSeparator() 
        AddToolButtonBmpObject(self.model.editor, toolbar, self.breakBmp, 'Set breakpoint', self.OnSetBreakPoint)
        AddToolButtonBmpObject(self.model.editor, toolbar, self.runCrsBmp, 'Run to cursor', self.OnRunToCursor)
        toolbar.AddSeparator() 
        AddToolButtonBmpObject(self.model.editor, toolbar, self.modInfoBmp, 'Add module info block', self.OnAddModuleInfo)


    def setReadOnly(self, val):
        EditorView.readOnly(self, val)
        self.SetEditable(val)
    
    def refreshCtrl(self):
        self.pos = self.GetInsertionPoint() 
        self.SetValue('')
        self.WriteText(self.model.data)
        self.SetInsertionPoint(self.pos)
        self.ShowPosition(self.pos)
        self.DiscardEdits()
        self.nonUserModification = false 
        self.updatePageName()
    
    def refreshModel(self):
        src = self.GetValue()
        lns = string.split(src, os.linesep)
        src = string.join(lns, '\012')
        self.model.data = src
        if self.isModified():
            self.model.modified = true
        self.nonUserModification = false 
        self.DiscardEdits()
        EditorView.refreshModel(self) 
        if self.model.viewsModified.count(self.viewName):
             self.model.viewsModified.remove(self.viewName)
        self.updateEditor()
    
    def OnRefresh(self, event):
        self.refreshModel()

    def gotoLine(self, lineno):
        self.SetInsertionPoint(self.XYToPosition(0, lineno))

    def selectSection(self, lineno, start, word):
        self.gotoLine(lineno)
        length = len(word)
        startPos = self.XYToPosition(start, lineno)
        endPos = self.XYToPosition(start + length, lineno)
        self.ShowPosition(startPos)
        self.SetSelection(startPos, endPos)
        self.SetFocus()
 
    def selectLine(self, lineno):
        self.gotoLine(lineno)
        length = self.GetLineLength(lineno)
        startPos = self.XYToPosition(0, lineno)
        endPos = self.XYToPosition(length, lineno)
        self.SetSelection(startPos, endPos)
    
    def updatePageName(self):
        currName = self.notebook.GetPageText(self.pageIdx)
        if self.isModified(): newName = '~%s~' % self.viewName
        else: newName = self.viewName

        if currName != newName:
            if not self.model.viewsModified.count(self.viewName):
                 self.model.viewsModified.append(self.viewName)
            self.notebook.SetPageText(self.pageIdx, newName)
            self.notebook.Refresh()
            self.updateEditor()

    def updateStatusBar(self):
        rc = self.PositionToXY(self.GetInsertionPoint())
        self.model.editor.updateStatusRowCol(rc[0], rc[1])
    
    def updateEditor(self):
        self.model.editor.updateModulePage(self.model)
        self.model.editor.updateTitle()
    
    def updateViewState(self):
        self.updatePageName()
        self.updateStatusBar()

    def insertCodeBlock(self, text):
        self.WriteText(text)
        self.nonUserModification = true
        self.updateViewState()
        self.SetFocus()  

    def isModified(self):
        return self.IsModified() or self.nonUserModification

    def OnSetBreakPoint(self, event):
        rc = self.PositionToXY(self.GetInsertionPoint())
        self.model.editor.debugger.set_breakpoint_here(self.model.filename, rc[1]+1, 0)        
    
    def OnRunToCursor(self, event):
        rc = self.PositionToXY(self.GetInsertionPoint())
        self.model.editor.debugger.set_breakpoint_here(self.model.filename, rc[1]+1, 1)        
        if self.model.defaultName == 'App':
            self.model.editor.debugger.debug_file(self.model.filename)
        elif self.model.app:
            self.model.editor.debugger.debug_file(self.model.app.filename)
#        else return  
        # XXX Case where module is run, outside app

    def OnRun(self, event):
        if not self.model.savedAs: #modified or len(self.model.viewsModified):
            wxMessageBox('Cannot run an unsaved module.')
            return
        self.model.run()

    def OnDebug(self, event):
        if not self.model.savedAs or self.model.modified or len(self.model.viewsModified):
            wxMessageBox('Cannot debug an unsaved or modified module.')
            return
        self.model.debug()

    def OnEditCut(self, event):
        self.Cut()   

    def OnEditCopy(self, event):
        self.Copy()   

    def OnEditPaste(self, event):
        self.Paste()

    def OnEditUndo(self, event):
        self.Undo()

    def OnEditRedo(self, event):
        self.Redo()

    def OnFind(self, event):
        dlg = wxTextEntryDialog(self.model.editor, 'Enter text:', 'Find in module', self.lastSearchPattern)
        try:
            if dlg.ShowModal() == wxID_OK:
                self.lastSearchResults = Search.findInText(string.split(self.GetValue(), '\012'), dlg.GetValue(), false)
                self.lastSearchPattern = dlg.GetValue()
                if len(self.lastSearchResults):
                    self.lastMatchPosition = 0
        finally:
            dlg.Destroy()         

        if self.lastMatchPosition is not None:
            pos = self.lastSearchResults[self.lastMatchPosition]
            self.selectSection(pos[0], pos[1], self.lastSearchPattern)
        else:
            dlg = wxMessageDialog(self.model.editor, 'No matches',
                      'Find in module', wxOK | wxICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()                

    def OnFindAgain(self, event):
        if self.lastMatchPosition is None:
            self.OnFind(event)
        else: 
            if self.lastMatchPosition < len(self.lastSearchResults) -1:  
                self.lastMatchPosition = self.lastMatchPosition + 1
                pos = self.lastSearchResults[self.lastMatchPosition]
                self.selectSection(pos[0], pos[1], self.lastSearchPattern)
            else:
                dlg = wxMessageDialog(self.model.editor, 'No further matches',
                          'Find in module', wxOK | wxICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()                
                self.lastMatchPosition = None

    def OnAddModuleInfo(self, event):
        self.refreshModel() 
        prefs = staticInfoPrefs.copy() 
        self.model.addModuleInfo(prefs)
        self.updateEditor()

    def OnKeyDown(self, event):
        event.Skip()
        self.updateViewState()
            
    def OnRightClick(self, event):
        self.menu.Enable(wxID_SOURCECOPY, self.CanCopy())
        self.menu.Enable(wxID_SOURCECUT, self.CanCut())
        self.menu.Enable(wxID_SOURCEPASTE, self.CanPaste())
        self.menu.Enable(wxID_SOURCEUNDO, self.CanUndo())
        self.menu.Enable(wxID_SOURCEREDO, self.CanRedo())

        EditorView.OnRightClick(self, event)

class ListCtrlView(wxListCtrl, EditorView):
    viewName = 'List (abstract)'
    def __init__(self, parent, model, listStyle, actions, dclickActionIdx = 0):
        wxListCtrl.__init__(self, parent, -1, style = listStyle)
        EditorView.__init__(self, actions, dclickActionIdx)

        EVT_LIST_ITEM_SELECTED(self, -1, self.OnItemSelect)
        EVT_LIST_ITEM_DESELECTED(self, -1, self.OnItemDeselect)
        self.selected = -1

        self.active = true
        self.model = model

    def OnItemSelect(self, event):
        self.selected = event.m_itemIndex

    def OnItemDeselect(self, event):
        self.selected = -1

    def refreshCtrl(self):
        self.DeleteAllItems()

class AppView(ListCtrlView):
    openBmp = wxBitmap('Images/Editor/Open.bmp', wxBITMAP_TYPE_BMP)
    openAllBmp = wxBitmap('Images/Editor/OpenAll.bmp', wxBITMAP_TYPE_BMP)
    addModBmp = wxBitmap('Images/Editor/AddToApp.bmp', wxBITMAP_TYPE_BMP)
    remModBmp = wxBitmap('Images/Editor/RemoveFromApp.bmp', wxBITMAP_TYPE_BMP)
    runBmp = wxBitmap('Images/Debug/Run.bmp', wxBITMAP_TYPE_BMP)
    debugBmp = wxBitmap('Images/Debug/Debug.bmp', wxBITMAP_TYPE_BMP)
    importsBmp = wxBitmap('Images/Editor/Imports.bmp', wxBITMAP_TYPE_BMP)

    viewName = 'Application'
    def __init__(self, parent, model):
        ListCtrlView.__init__(self, parent, model, wxLC_REPORT, 
          ((NewId(), 'Open', self.OnOpen),
           (NewId(), 'Open all modules', self.OnOpenAll), 
           (-1, '-', None),
           (NewId(), 'Add', self.OnAdd),
           (NewId(), 'Edit', self.OnEdit),
           (NewId(), 'Remove', self.OnRemove),
           (-1, '-', None),
           (NewId(), 'Run application', self.OnRun),
           (NewId(), 'Debugger', self.OnDebugger),
           (-1, '-', None),
           (NewId(), 'Imports...', self.OnImports)))
           
	self.InsertColumn(0, 'Module', width = 100)
	self.InsertColumn(1, 'Autocreate', wxLIST_FORMAT_CENTRE, 50)
	self.InsertColumn(2, 'Description', width = 150)
	self.InsertColumn(3, 'Path', width = 220)

        self.SetImageList(model.editor.modelImageList, wxIMAGE_LIST_SMALL)

        self.active = true
        self.model = model

    def addViewTools(self, toolbar):
        AddToolButtonBmpObject(self.model.editor, toolbar, self.openBmp, 'Open selected module', self.OnOpen)
        AddToolButtonBmpObject(self.model.editor, toolbar, self.openAllBmp, 'Open all modules in application', self.OnOpenAll)
        toolbar.AddSeparator() 
        AddToolButtonBmpObject(self.model.editor, toolbar, self.addModBmp, 'Add to application', self.OnAdd)
        AddToolButtonBmpObject(self.model.editor, toolbar, self.remModBmp, 'Remove from application', self.OnRemove)
        toolbar.AddSeparator() 
        AddToolButtonBmpObject(self.model.editor, toolbar, self.runBmp, 'Run', self.OnRun)
        AddToolButtonBmpObject(self.model.editor, toolbar, self.debugBmp, 'Debugger', self.OnDebugger)
        toolbar.AddSeparator() 
        AddToolButtonBmpObject(self.model.editor, toolbar, self.importsBmp, 'Show import relationship between modules', self.OnImports)

    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)
        i = 0
        modSort = self.model.modules.keys()
        modSort.sort()
        for mod in modSort:
            # XXX Determine if file exists and if so the model type
            imgIdx = -1
            if self.model.moduleModels.has_key(mod): imgIdx = self.model.moduleModels[mod].imgIdx

            self.InsertImageStringItem(i, mod, imgIdx)
            self.SetStringItem(i, 1, `self.model.modules[mod][0]`)
            self.SetStringItem(i, 2, self.model.modules[mod][1])
            self.SetStringItem(i, 3, self.model.modules[mod][2])
            i = i + 1

    def OnOpen(self, event):
        if self.selected >= 0:
            self.model.openModule(self.GetItemText(self.selected))
            
    def OnAdd(self, event):
        self.model.viewAddModule()

    def OnEdit(self, event):
        pass

    def OnRemove(self, event):
        if self.selected >= 0:
            self.model.removeModule(self.GetItemText(self.selected))

    def OnRun(self, event):
        self.model.run()

    def OnDebugger(self, event):
        self.model.debug()  
    
    def OnImports(self, events):
        self.model.showImportsView()
        if self.model.views.has_key('Imports'):
            self.model.views['Imports'].focus()
        self.model.update()
        self.model.notify()

    def OnOpenAll(self, event):
        modules = self.model.modules.keys()
        modules.sort() 
        for mod in modules:
            try:
                self.model.editor.openOrGotoModule(\
                  self.model.modules[mod][2])
            except: pass

        
# XXX Add structured text/wiki option for doc strings
# XXX Option to only list documented methods
class DocView(wxHtmlWindow, EditorView):
    prevBmp = wxBitmap('Images/Shared/Previous.bmp', wxBITMAP_TYPE_BMP)
    nextBmp = wxBitmap('Images/Shared/Next.bmp', wxBITMAP_TYPE_BMP)

    viewName = 'Documentation'
    def __init__(self, parent, model):
        wxHtmlWindow.__init__(self, parent)
        EditorView.__init__(self, ((NewId(), 'Back', self.OnPrev),
                                   (NewId(), 'Forward', self.OnNext)), 5)
        self.SetRelatedFrame(model.editor, 'Editor')
        self.SetRelatedStatusBar(2)

        model.editor.statusBar.hint.SetLabel('')

        self.active = true
        self.model = model

    def addViewTools(self, toolbar):
        AddToolButtonBmpObject(self.model.editor, toolbar, self.prevBmp, 'Back', self.OnPrev)
        AddToolButtonBmpObject(self.model.editor, toolbar, self.nextBmp, 'Forward', self.OnNext)

    def generatePage(self):
        page = wxwHeaderTemplate
        
        page = self.genCustomPage(page)

        page = page + wxwFooterTemplate             
        
        return page

    def genCustomPage(self, page):
        """ Override to make the page a little more interesting """
        return page

    def refreshCtrl(self):
        self.SetPage(self.generatePage())

    def OnPrev(self, event):
        self.HistoryBack()

    def OnNext(self, event):
        self.HistoryForward()

class ModuleDocView(DocView):

    def genCustomPage(self, page):
        return self.genModuleSect(page)

    def genModuleSect(self, page):
        modBody = wxwModuleTemplate
        synopsis = self.model.module.getModuleDoc()
        modBody = string.replace(modBody, '[[ModuleSynopsis]]', synopsis)
        modBody = string.replace(modBody, '[[Module]]', self.model.moduleName)

        classList, classNames = self.genClassListSect()
        modBody = string.replace(modBody, '[[ClassList]]', classList)

        page = page + modBody

        page = self.genClassesSect(page, classNames)

        return page

    def genClassListSect(self):
        clssLst = []
        classNames = self.model.module.classes.keys()
        classNames.sort()
        for aclass in classNames:
            clssLst.append('<a href="#%s">%s</a>' %(aclass, aclass))

        return string.join(clssLst, '<BR>'), classNames
                
    def genClassesSect(self, page, classNames):
        for aclass in classNames:
            clsBody = wxwClassTemplate
            clsBody = string.replace(clsBody, '[[Class]]', aclass)
            supers = []
            for super in self.model.module.classes[aclass].super:
                try:
                    supers.append('<a href="#%s">%s</a>'%(super.name, super.name))
                except:
                    supers.append(super)
            if len(supers) > 0:
                supers = string.join(supers, ', ')
            else:
                supers = ''
                
            clsBody = string.replace(clsBody, '[[ClassSuper]]', supers)
            synopsis = self.model.module.getClassDoc(aclass)
            clsBody = string.replace(clsBody, '[[ClassSynopsis]]', synopsis)

            methlist, meths = self.genMethodSect(aclass)

            clsBody = string.replace(clsBody, '[[MethodList]]', methlist)
            clsBody = string.replace(clsBody, '[[MethodDetails]]', meths)
            page = page + clsBody
 
        return page

    def genMethodSect(self, aclass):
        methlist = ''
        meths = ''
        methods = self.model.module.classes[aclass].methods.keys()
        methods.sort()
        for ameth in methods:
            methlist = methlist + '<a href="#'+aclass+ameth + '">'+ameth +'</a><br>'
            methBody = wxwMethodTemplate
            methBody = string.replace(methBody, '[[Class]]', aclass)
            methBody = string.replace(methBody, '[[Method]]', ameth)
            synopsis = self.model.module.getClassMethDoc(aclass, ameth)
            methBody = string.replace(methBody, '[[MethodSynopsis]]', synopsis)
            asig = self.model.module.classes[aclass].methods[ameth].signature
            methBody = string.replace(methBody, '[[Params]]', asig)
            meths = meths + methBody

        return methlist, meths

class AppModuleDocView(ModuleDocView):
    viewName = 'Application Documentation'

    def OnLinkClicked(self, linkinfo):
        url = linkinfo.GetHref()

        # Virtuals in the base class have been renamed with base_ on the front.
        if url[0] == '#':
            self.base_OnLinkClicked(linkinfo)
        else:
            mod = path.splitext(url)[0]
            newMod = self.model.openModule(mod)
            newMod.views['Documentation'].focus()

    def genModuleListSect(self):
        modLst = []
        modNames = self.model.modules.keys()
        modNames.sort()
        for amod in modNames:
            desc = string.strip(self.model.modules[amod][1])
            modLst.append('<tr><td width="25%%"><a href="%s.html">%s</a></td><td>%s</td></tr>' %(amod, amod, desc))

        return '<table BORDER=0 CELLSPACING=0 CELLPADDING=0>'+string.join(modLst, '<BR>')+'</table>', modNames

    def genModuleSect(self, page):
        modBody = wxwAppModuleTemplate
        synopsis = self.model.module.getModuleDoc()
        modBody = string.replace(modBody, '[[ModuleSynopsis]]', synopsis)
        modBody = string.replace(modBody, '[[Module]]', self.model.moduleName)

        modList, modNames = self.genModuleListSect()
        modBody = string.replace(modBody, '[[ModuleList]]', modList)

        classList, classNames = self.genClassListSect()
        modBody = string.replace(modBody, '[[ClassList]]', classList)

        page = page + modBody

        page = self.genClassesSect(page, classNames)

        return page
        	
 
class ExploreView(wxTreeCtrl, EditorView):
    tokenImgLst = wxImageList(16, 16)
    tokenImgLst.Add(wxBitmap('Images/Views/Explore/class.bmp', wxBITMAP_TYPE_BMP))
    tokenImgLst.Add(wxBitmap('Images/Views/Explore/method.bmp', wxBITMAP_TYPE_BMP))
    tokenImgLst.Add(wxBitmap('Images/Views/Explore/event.bmp', wxBITMAP_TYPE_BMP))
    tokenImgLst.Add(wxBitmap('Images/Views/Explore/function.bmp', wxBITMAP_TYPE_BMP))
    tokenImgLst.Add(wxBitmap('Images/Views/Explore/attribute.bmp', wxBITMAP_TYPE_BMP))
    viewName = 'Explore'
    gotoLineBmp = wxBitmap('Images/Editor/GotoLine.bmp', wxBITMAP_TYPE_BMP)

    def __init__(self, parent, model):
        wxTreeCtrl.__init__(self, parent, -1)
        EditorView.__init__(self, ((NewId(), 'Goto line', self.OnGoto),), 0)

        self.SetImageList(self.tokenImgLst)

        self.model = model
        self.active = true

    def addViewTools(self, toolbar):
        AddToolButtonBmpObject(self.model.editor, toolbar, self.gotoLineBmp, 'Goto line', self.OnGoto)

    def refreshCtrl(self):
        self.DeleteAllItems()
        # XXX Add root node as module name
        rootItem = self.AddRoot(self.model.moduleName, -1, -1, wxTreeItemData(CodeBlock('', 0, 0)))
        for className in self.model.module.class_order:
            classItem = self.AppendItem(rootItem, className, 0, -1, wxTreeItemData(self.model.module.classes[className].block))
            for attrib in self.model.module.classes[className].attributes.keys():
                attribItem = self.AppendItem(classItem, attrib, 4, -1, 
                  wxTreeItemData(self.model.module.classes[className].attributes[attrib]))
            for method in self.model.module.classes[className].method_order:
                if (len(method) >= 3) and (method[:2] == 'On') and \
                  (method[2] in string.uppercase):
                    methodsItem = self.AppendItem(classItem, method, 2, -1, 
                      wxTreeItemData(self.model.module.classes[className].methods[method]))
                else:
                    methodsItem = self.AppendItem(classItem, method, 1, -1, 
                      wxTreeItemData(self.model.module.classes[className].methods[method]))

        functionList = self.model.module.functions.keys()
        functionList.sort() 	               
        for func in functionList:
            funcItem = self.AppendItem(rootItem, func, 3, -1,
              wxTreeItemData(self.model.module.functions[func]))

        self.Expand(rootItem)

    def OnGoto(self, event):
        if self.model.views.has_key('Source'):
            srcView = self.model.views['Source']
            idx = self.GetSelection()
            if idx.IsOk():
                srcView.focus()
                srcView.gotoLine(self.GetPyData(idx).start -1)

idGotoLine = NewId()    
class ToDoView(ListCtrlView):
    viewName = 'ToDo'
    gotoLineBmp = wxBitmap('Images/Editor/GotoLine.bmp', wxBITMAP_TYPE_BMP)

    def __init__(self, parent, model):
        ListCtrlView.__init__(self, parent, -1, wxLC_REPORT, 
          ((idGotoLine, 'Goto line', self.OnGoto),))
        self.InsertColumn(0, 'Line#')
        self.InsertColumn(1, 'Urgency')
        self.InsertColumn(2, 'Entry')
        self.SetColumnWidth(0, 40)
        self.SetColumnWidth(1, 75)
        self.SetColumnWidth(2, 350)

        self.model = model
        self.active = true

    def addViewTools(self, toolbar):
        AddToolButtonBmpObject(self.model.editor, toolbar, self.gotoLineBmp, 'Goto line', self.OnGoto)
        
    def refreshCtrl(self):
        self.DeleteAllItems()
        i = 0
        for todo in self.model.module.todos:
            self.InsertStringItem(i, `todo[0]`)
            self.SetStringItem(i, 1, 'Unknown')
            self.SetStringItem(i, 2, todo[1])
            i = i + 1

    def OnGoto(self, event):
        if self.model.views.has_key('Source'):
            srcView = self.model.views['Source']
            # XXX Implement an interface for views to talk
            srcView.focus()
            srcView.gotoLine(int(self.model.module.todos[self.selected][0]) -1)

class HierarchyView(wxTreeCtrl, EditorView):
    tokenImgLst = wxImageList(16, 16)
    tokenImgLst.Add(wxBitmap('Images/Views/Hierarchy/inherit.bmp', wxBITMAP_TYPE_BMP))
    tokenImgLst.Add(wxBitmap('Images/Views/Hierarchy/inherit_base.bmp', wxBITMAP_TYPE_BMP))
    tokenImgLst.Add(wxBitmap('Images/Views/Hierarchy/inherit_outside.bmp', wxBITMAP_TYPE_BMP))
    viewName = 'Hierarchy'
    gotoLineBmp = wxBitmap('Images/Editor/GotoLine.bmp', wxBITMAP_TYPE_BMP)

    def __init__(self, parent, model):
        self.model = model
        id = NewId()
        wxTreeCtrl.__init__(self, parent, id)
        EditorView.__init__(self, ((idGotoLine, 'Goto line', self.OnGoto),), 0)
#          style = wxTR_HAS_BUTTONS | wxTR_LINES_AT_ROOT)# | wxTR_EDIT_LABELS)
        self.active = true

        self.SetImageList(self.tokenImgLst)

    def addViewTools(self, toolbar):
        AddToolButtonBmpObject(self.model.editor, toolbar, self.gotoLineBmp, 'Goto line', self.OnGoto)

    def buildTree(self, parent, dict):
        for item in dict.keys():
            child = self.AppendItem(parent, item, 0)
	    if len(dict[item].keys()):
	        self.buildTree(child, dict[item])

    def refreshCtrl(self):
        self.DeleteAllItems()
        hierc = self.model.module.createHierarchy()
        
        root = self.AddRoot(self.model.moduleName, 0)#, 0, wxTreeItemData(CodeBlock('', 0, 0)))
        for top in hierc.keys():
            if self.model.module.classes.has_key(top): imgIdx = 1
            else: imgIdx = 2
            
            self.buildTree(self.AppendItem(root, top, imgIdx), hierc[top])
        
        self.Expand(root)


    def OnGoto(self, event):
        idx  = self.GetSelection()
        if idx.IsOk():
            name = self.GetItemText(idx)
            if self.model.views.has_key('Source') and \
              self.model.module.classes.has_key(name):
                srcView = self.model.views['Source']
                srcView.focus()
                srcView.gotoLine(int(self.model.module.classes[name].block.start) -1)
            
tPopupIDPackageOpen = 300

class PackageView(ListCtrlView):
    viewName = 'Package'
    def __init__(self, parent, model):
        ListCtrlView.__init__(self, parent, model, wxLC_LIST, 
          ((tPopupIDPackageOpen, 'Open', self.OnOpen),))

        self.SetImageList(model.editor.modelImageList, wxIMAGE_LIST_SMALL)

               
    def refreshCtrl(self):
        ListCtrlView.refreshCtrl(self)

        self.filenames = {}
        self.packageFiles = self.model.generateFileList()
        self.packageFiles.reverse()
        for file in self.packageFiles:
            self.filenames[file[0]] = file[1]
            self.InsertImageStringItem(0, file[0], file[1].imgIdx)

    def OnOpen(self, event):
        if self.selected >= 0:
            name = self.GetItemText(self.selected)
            modCls = self.filenames[name]
            if modCls.defaultName == 'package':
                self.model.openPackage(name)
            else:
                self.model.openFile(name)

class InfoView(wxTextCtrl, EditorView):
##    addInfoBmp = wxBitmap('Editor/Refresh.bmp', wxBITMAP_TYPE_BMP)

    viewName = 'Info'
    def __init__(self, parent, model):
        wxTextCtrl.__init__(self, parent, -1, '', style = wxTE_MULTILINE | wxTE_RICH | wxHSCROLL)
        EditorView.__init__(self, ((NewId(), 'Add comment block to code', self.OnAddInfo),), 5)
        self.active = true
        self.model = model
        self.SetFont(wxFont(9, wxMODERN, wxNORMAL, wxNORMAL, false))

    def setReadOnly(self, val):
        EditorView.readOnly(self, val)
        self.SetEditable(val)
    
    def refreshCtrl(self):
        pass
        self.SetValue('')
        info = self.model.module.getInfoBlock()
        self.WriteText(`info`)
    
    def OnAddInfo(self, event):
        self.model.addInfoBlock()


#class CVSView : Shows conflicts after merging CVS    

#class ImportView(wxOGL, EditorView) -> AppModel: implimented in UMLView.py

#class ContainmentView(wxTreeCtrl, EditorView) -> FrameModel: 
#      parent/child relationship tree hosted in inspector

#class XMLView(wxTextCtrl, EditorView) -> FrameModel: for frames' components

#class CASEView(wxOGL, EditorView): implimented in UMLView.py
    
#class DesignerView implemented in Designer
