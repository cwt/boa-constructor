#-----------------------------------------------------------------------------
# Name:        FileDlg.py
# Purpose:     
#                
# Author:      Riaan Booysen
#                
# Created:     2000/09/17
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:wxBoaFileDialog

from wxPython.wx import *
from wxPython.lib.anchors import LayoutAnchors
from os import path
import os

openStr = 'Open'
saveStr = 'Save'

[wxID_WXBOAFILEDIALOGSTATICTEXT1, wxID_WXBOAFILEDIALOGBTCANCEL, wxID_WXBOAFILEDIALOGTCFILENAME, wxID_WXBOAFILEDIALOGPANEL1, wxID_WXBOAFILEDIALOGSTATICTEXT2, wxID_WXBOAFILEDIALOGSTPATH, wxID_WXBOAFILEDIALOGBTOK, wxID_WXBOAFILEDIALOGCHTYPES, wxID_WXBOAFILEDIALOG] = map(lambda _init_ctrls: wxNewId(), range(9))

class wxBoaFileDialog(wxDialog):
    currentDir = '.'
    def _init_utils(self): 
        pass

    def _init_ctrls(self, prnt): 
        wxDialog.__init__(self, size = wxSize(408, 283), id = wxID_WXBOAFILEDIALOG, title = 'File Dialog', parent = prnt, name = 'wxBoaFileDialog', style = wxRESIZE_BORDER | wxDEFAULT_DIALOG_STYLE, pos = wxPoint(174, 117))
        self._init_utils()
        self.SetAutoLayout(true)

        self.panel1 = wxPanel(size = wxSize(400, 256), id = wxID_WXBOAFILEDIALOGPANEL1, parent = self, name = 'panel1', style = wxTAB_TRAVERSAL, pos = wxPoint(0, 0))
        self.panel1.SetConstraints(LayoutAnchors(self.panel1, true, true, true, true))
        self.panel1.SetAutoLayout(true)

        self.btOK = wxButton(label = 'OK', id = wxID_WXBOAFILEDIALOGBTOK, parent = self.panel1, name = 'btOK', size = wxSize(72, 24), style = 0, pos = wxPoint(320, 184))
        self.btOK.SetConstraints(LayoutAnchors(self.btOK, false, false, true, true))
        EVT_BUTTON(self.btOK, wxID_WXBOAFILEDIALOGBTOK, self.OnBtokButton)

        self.btCancel = wxButton(label = 'Cancel', id = wxID_WXBOAFILEDIALOGBTCANCEL, parent = self.panel1, name = 'btCancel', size = wxSize(72, 24), style = 0, pos = wxPoint(320, 216))
        self.btCancel.SetConstraints(LayoutAnchors(self.btCancel, false, false, true, true))
        EVT_BUTTON(self.btCancel, wxID_WXBOAFILEDIALOGBTCANCEL, self.OnBtcancelButton)

        self.staticText1 = wxStaticText(label = 'File name:', id = wxID_WXBOAFILEDIALOGSTATICTEXT1, parent = self.panel1, name = 'staticText1', size = wxSize(48, 16), style = 0, pos = wxPoint(8, 192))
        self.staticText1.SetConstraints(LayoutAnchors(self.staticText1, true, false, false, true))

        self.staticText2 = wxStaticText(label = 'Files of type:', id = wxID_WXBOAFILEDIALOGSTATICTEXT2, parent = self.panel1, name = 'staticText2', size = wxSize(64, 16), style = 0, pos = wxPoint(8, 224))
        self.staticText2.SetConstraints(LayoutAnchors(self.staticText2, true, false, false, true))

        self.tcFilename = wxTextCtrl(size = wxSize(224, 24), value = '', pos = wxPoint(80, 184), parent = self.panel1, name = 'tcFilename', style = 0, id = wxID_WXBOAFILEDIALOGTCFILENAME)
        self.tcFilename.SetConstraints(LayoutAnchors(self.tcFilename, true, false, true, true))
        EVT_TEXT_ENTER(self.tcFilename, wxID_WXBOAFILEDIALOGTCFILENAME, self.OnTcfilenameTextEnter)

        self.chTypes = wxChoice(size = wxSize(224, 21), id = wxID_WXBOAFILEDIALOGCHTYPES, choices = ['Boa files', 'Internal files', 'All files'], parent = self.panel1, name = 'chTypes', validator = wxDefaultValidator, style = 0, pos = wxPoint(80, 216))
        self.chTypes.SetConstraints(LayoutAnchors(self.chTypes, true, false, true, true))
        EVT_CHOICE(self.chTypes, wxID_WXBOAFILEDIALOGCHTYPES, self.OnChtypesChoice)

        self.stPath = wxStaticText(label = ' ', id = wxID_WXBOAFILEDIALOGSTPATH, parent = self.panel1, name = 'stPath', size = wxSize(3, 13), style = 0, pos = wxPoint(8, 8))

    def OnSize(self, event):
        self.panel1.Layout()
        
    def __init__(self, parent, message = 'Choose a file', defaultDir = '.', defaultFile = '', wildcard = '*.py; *.txt', style = wxOPEN, pos = wxDefaultPosition): 
        self._init_ctrls(parent)
        self.SetStyle(style)
        self.SetWildcard(wildcard)
        
        EVT_SIZE(self.panel1, self.OnSize)
        
        # XXX This is a bit convoluted ;)
        # XXX The late importing is the only way to avoid import problems because 
        # XXX the dialog swapping code is initialised so early on

        from Explorers import Explorer

        class FileDlgFolderList(Explorer.PackageFolderList):
            def __init__(self, parent, dlg, filepath, pos = wxDefaultPosition, size = wxDefaultSize):
                from Explorers import Explorer
                Explorer.PackageFolderList.__init__(self, parent, filepath, pos, size)
                self.dlg = dlg
                EVT_LIST_ITEM_SELECTED(self, self.GetId(), self.OnItemSelect)
                EVT_LIST_ITEM_DESELECTED(self, self.GetId(), self.OnItemDeselect)
                EVT_RIGHT_UP(self, self.OnListRightUp)
                self.menu = wxMenu()
                menuId = wxNewId()
                self.menu.Append(menuId, 'New Folder')
                EVT_MENU(self, menuId, self.OnNewFolder)
                EVT_LIST_BEGIN_LABEL_EDIT(self, self.GetId(), self.OnBeginLabelEdit)
                EVT_LIST_END_LABEL_EDIT(self, self.GetId(), self.OnEndLabelEdit)
                
                
            def OnItemSelect(self, event):
                from Explorers import Explorer
                Explorer.PackageFolderList.OnItemSelect(self, event)
                item = self.getSelection()
                if item:
                    self.dlg.SelectItem(item.name)
                elif self.selected == 0:
                    self.dlg.SelectItem('..')
                event.Skip()

            def OnItemDeselect(self, event):
                from Explorers import Explorer
                Explorer.PackageFolderList.OnItemDeselect(self, event)
                self.dlg.SelectItem(None)
                event.Skip()

            def OnListRightUp(self, event):
                self.PopupMenu(self.menu, wxPoint(event.GetX(), event.GetY()))
                
            def OnNewFolder(self, event):
                name = self.node.newFolder()
                self.refreshCurrent()
                self.selectItemNamed(name)
                self.EditLabel(self.selected)

            def OnBeginLabelEdit(self, event):
                self.oldLabelVal = event.GetText()
        
            def OnEndLabelEdit(self, event):
                newText = event.GetText()
                if newText != self.oldLabelVal:# and isinstance(self.list.node, ZopeItemNode):
                    event.Skip()
                    self.node.renameItem(self.oldLabelVal, newText)
                    self.refreshCurrent()
                

        if defaultDir == '.':
            defaultDir = path.abspath(self.currentDir)
        else:
            defaultDir = defaultDir and path.abspath(defaultDir) or path.abspath(self.currentDir)
        self.lcFiles = FileDlgFolderList(self.panel1, self, 
              defaultDir, pos = wxPoint(8, 21), size = wxSize(384, 152))
        self.lcFiles.SetConstraints(LayoutAnchors(self.lcFiles, true, true, true, true))

        EVT_LEFT_DCLICK(self.lcFiles, self.OnOpen)
        
        self.btOK.SetDefault()
        
        self.SetDirectory(defaultDir)
        self.SetFilename(defaultFile)

        self.editorFilter = self.lcFiles.node.filter
        self.editorFilterNode = self.lcFiles.node

        if self.lcFiles.node.filter == 'BoaFiles':
            self.chTypes.SetStringSelection('Boa files')
        elif self.lcFiles.node.filter == 'BoaInternalFiles':
            self.chTypes.SetStringSelection('Internal files')
        if self.lcFiles.node.filter == 'AllFiles':
            self.chTypes.SetStringSelection('All files')

    def newFileNode(self, defaultDir):
        from Explorers import FileExplorer, Explorer
        return FileExplorer.PyFileNode(path.basename(defaultDir), defaultDir, None, 
              Explorer.EditorModels.FolderModel.imgIdx, None, None)

    def updatePathLabel(self):
        self.stPath.SetLabel(self.GetPath())

    def open(self, node):
        if node:
            if node.isFolderish():
                self.lcFiles.refreshItems(self.modImages, node)
                self.updatePathLabel()
                if self.style & wxSAVE: btn = saveStr
                else: btn = openStr
                self.btOK.SetLabel(btn)
                return
        if self.tcFilename.GetValue():           
            self.editorFilterNode.setFilter(self.editorFilter)
            wxBoaFileDialog.currentDir = self.GetDirectory()
            self.EndModal(wxID_OK)
                    
    def OnOpen(self, event):
        self.ok()

    def ok(self):
        if self.lcFiles.selected == 0:
            node = self.lcFiles.node.createParentNode()
            if node: node.doCVS = false
            if node.resourcepath == self.lcFiles.node.resourcepath:
                from ExternalLib.ConfigParser import ConfigParser
                import Preferences
                from Explorers import FileExplorer
                conf = ConfigParser()
                conf.read(Preferences.pyPath+'/Explorer.'+\
                      (wxPlatform == '__WXMSW__' and 'msw' or 'gtk')+'.cfg')
                fsn = FileExplorer.FileSysCatNode(None, conf, None, None)
                self.lcFiles.refreshItems(self.modImages, fsn)
                self.stPath.SetLabel(fsn.name)
                if self.style & wxSAVE: btn = saveStr
                else: btn = openStr
                self.btOK.SetLabel(btn)
                return
        else:
            node = self.lcFiles.getSelection()
            if node: node.doCVS = false

        if (node and not node.isFolderish() or not node) and self.style & wxOVERWRITE_PROMPT:
            if path.exists(self.GetPath()):
                dlg = wxMessageDialog(self, 'This file already exists.'+os.linesep+\
                      'Do you want to overwrite the file?', 'Overwrite file?', 
                      wxYES_NO | wxICON_WARNING)
                try:
                    if dlg.ShowModal() == wxID_NO:
                        return
                finally:
                    dlg.Destroy()
        self.open(node)

    def OnBtokButton(self, event):
        self.ok()
        
    def OnBtcancelButton(self, event):
        self.editorFilterNode.setFilter(self.editorFilter)
        self.EndModal(wxID_CANCEL)
        
    def OnTcfilenameTextEnter(self, event):
        self.ok()

#---wxFileDialog lookalike meths------------------------------------------------

#class wxBoaFileDialog(BoaFileDialog):
#    def __init__(self, parent, message = 'Choose a file', defaultDir = '', defaultFile = '', wildcard = '*.*', style = wxOPEN, wildcard = '*.py; *.txt', pos = wxDefaultPosition): 
#        BoaFileDialog.__init__(self, FileDlgFolderList, parent, message = 'Choose a file', defaultDir = '', defaultFile = '', style = wxOPEN, wildcard = '*.py; *.txt', pos = wxDefaultPosition)
    
    def SelectItem(self, name):
        # deselect
        if not name:
            if self.style & wxSAVE: btn = saveStr
            else: btn = openStr
        # file
        elif name != '..' and not path.isdir(path.join(self.GetDirectory(), name)):
            self.SetFilename(name)
            if self.style & wxSAVE: btn = saveStr
            else: btn = openStr
        # dir
        else:
            btn = openStr

        self.btOK.SetLabel(btn)

    def GetDirectory(self):
        return self.lcFiles.filepath
    def GetFilename(self):
        return self.tcFilename.GetValue()
    def GetFilterIndex(self, *_args, **_kwargs):
        pass
    def GetMessage(self):
        return self.GetTitle()
    def GetPath(self):
        return path.join(self.GetDirectory(), self.GetFilename())
    def GetStyle(self):
        return self.style
    def GetWildcard(self):
        return self.wildcard
    def SetDirectory(self, newDir):
        node = self.newFileNode(newDir)
        node.doCVS = false
        self.lcFiles.refreshItems(self.modImages, node)
        self.updatePathLabel()
    def SetFilename(self, filename):
        self.tcFilename.SetValue(filename)
        self.updatePathLabel()
    def SetFilterIndex(self, *_args, **_kwargs):
        pass
    def SetMessage(self, mess):
        self.SetTitle(mess)
    def SetPath(self, newPath):
        pass
    def SetStyle(self, style):
        title = 'File Dialog'
        btn = 'OK'
        print style
        if style & wxOPEN:
            title = 'Open'
            btn = openStr
        if style & wxSAVE:
            title = 'Save As'
            btn = saveStr
            
        self.SetTitle(title)
        self.btOK.SetLabel(btn)
        self.style = style
    def SetWildcard(self, wildcard):
        self.wildcard = wildcard
        self.chTypes.SetStringSelection(wildcard)
##    def ShowModal(self, *_args, **_kwargs):
##        pass
##    def GetFilenames(self, *_args, **_kwargs):
##        val = apply(cmndlgsc.wxFileDialog_GetFilenames,(self,) + _args, _kwargs)
##        return val
##    def GetPaths(self, *_args, **_kwargs):
##        val = apply(cmndlgsc.wxFileDialog_GetPaths,(self,) + _args, _kwargs)
##        return val
    def __repr__(self):
        return '<C wxBoaFileDialog instance at %s>' % (self.this,)

    def OnChtypesChoice(self, event):
        fType = self.chTypes.GetStringSelection()
        if fType == 'Boa files':
            self.lcFiles.node.setFilter('BoaFiles')
        elif fType == 'Internal files':
            self.lcFiles.node.setFilter('BoaInternalFiles')
        elif fType == 'All files':
            self.lcFiles.node.setFilter('AllFiles')
        self.lcFiles.refreshCurrent()
    