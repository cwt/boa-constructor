#----------------------------------------------------------------------
# Name:        Explorer.py
# Purpose:     Browse filesystem for Boa files
#
# Author:      Riaan Booysen
#
# Created:     2000/11/02
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

from wxPython.wx import *

from EditorModels import *

from ConfigParser import ConfigParser
from os import path

[wxID_PFE, wxID_PFT, wxID_PFL] = map(lambda x: NewId(), range(3))

# XXX Add CVS View for folders with CVS sub folders containing Entries, Repository & Root

class PackageFolderTree(wxTreeCtrl):
    def __init__(self, parent, images, root):
        wxTreeCtrl.__init__(self, parent, wxID_PFT)
        EVT_TREE_ITEM_EXPANDING(self, wxID_PFT, self.OnOpen)
        EVT_TREE_ITEM_COLLAPSED(self, wxID_PFT, self.OnClose)
        self.SetImageList(images)
        self.list = list
        
        conf = ConfigParser()
        if wxPlatform == '__WXMSW__':
            plat = 'msw'
        else:
            plat = 'gtk'
        
        conf.read('Explorer.'+plat+'.cfg')
        rootItem = self.AddRoot('Boa', FolderModel.imgIdx, -1, wxTreeItemData(''))

        newFS = self.AppendItem(rootItem, 'Filesystem', FolderModel.imgIdx, -1, wxTreeItemData(''))
        self.SetItemBold(newFS, true)
        try:
            volumes = eval(conf.get('Explorer', 'Filesystem'))
        except Exception, message:
            print 'invalid config entry for Filesystem: list expected,', message
        else:
            for fs in volumes:
                newFSV = self.AppendItem(newFS, fs, FolderModel.imgIdx, -1, wxTreeItemData(fs))
                self.SetItemHasChildren(newFSV, true)

        newWS = self.AppendItem(rootItem, 'Workspace', FolderModel.imgIdx, -1, wxTreeItemData(''))
        self.SetItemBold(newWS, true)
        try:
            spaces = eval(conf.get('Explorer', 'Workspaces'))
        except Exception, message:
            print 'invalid config entry for Workspaces: dict expected,', message
        else:
            for ws in spaces.keys():
                newS = self.AppendItem(newWS, ws, FolderModel.imgIdx, -1, wxTreeItemData(spaces[ws]))
                self.SetItemHasChildren(newS, true)
        self.Expand(newWS)

        newP = self.AppendItem(rootItem, 'sys.path', FolderModel.imgIdx, -1, wxTreeItemData(''))
        self.SetItemBold(newP, true)
        for pth in sys.path:
            if pth:
                abspth = path.abspath(pth)
                ni = self.AppendItem(newP, abspth, FolderModel.imgIdx, -1, wxTreeItemData(abspth))
                self.SetItemHasChildren(ni, true)
        
        self.SetItemHasChildren(rootItem, true)
        self.Expand(rootItem)

    def getChildren(self):
        children = []
        cookie = 0
        selection = self.GetSelection()
        child, cookie = self.GetFirstChild(selection, cookie)
        while child.IsOk():
            children.append(child)
            child, cookie = self.GetNextChild(selection, cookie)
        return children

    def getChildrenNames(self):
        return map(lambda id, tree = self: tree.GetItemText(id), self.getChildren())

    def getChildNamed(self, name):
        cookie = 0
        selection = self.GetSelection()
        child, cookie = self.GetFirstChild(selection, cookie)
        while child.IsOk() and self.GetItemText(child) != name:
            child, cookie = self.GetNextChild(selection, cookie)
        return child

    def OnOpen(self, event):
        item = event.GetItem()
        filepath = self.GetPyData(item)
        if filepath:  
            self.DeleteChildren(item)
            files = os.listdir(filepath)
            files.sort()
            found = 0
            for file in files:
                filename = path.join(filepath, file)
                if path.isdir(filename):
                    if path.exists(path.join(filename, '__init__.py')):
                        model = PackageModel
                    else:
                        model = FolderModel
                    found = 1
      
                    new = self.AppendItem(item, file, model.imgIdx, -1,
                                      wxTreeItemData(filename))
                    self.SetItemHasChildren(new, true)
        else:
            found = true

        self.SetItemHasChildren(item, found)
              
    def OnClose(self, event):
        item = event.GetItem()
#        self.DeleteChildren(item)

#            if dir(new_obj):
#                self.SetItemHasChildren(new_item, wx.TRUE)

 

class PackageFolderList(wxListCtrl):
    def __init__(self, parent, images, filepath):
        wxListCtrl.__init__(self, parent, wxID_PFL, style = wxLC_LIST)
        self.SetImageList(images, wxIMAGE_LIST_SMALL)
        self.filepath = filepath
        self.exts = map(lambda C: C.ext, modelReg.values())

        EVT_LIST_ITEM_SELECTED(self, wxID_PFL, self.OnItemSelect)
        EVT_LIST_ITEM_DESELECTED(self, wxID_PFL, self.OnItemDeselect)
        self.selected = -1

    def refreshPath(self, filepath = ''):
        self.DeleteAllItems()
        if filepath: self.filepath = filepath 
        files = os.listdir(filepath)
        
        files.sort()
        packages = []
        modules = []
        for file in files:
            filename = path.join(self.filepath, file)
            ext = path.splitext(file)[1]
            if file == PackageModel.pckgIdnt: continue
            elif (ext in self.exts) and path.isfile(filename):
                modules.append((file, identifyFile(filename)[0]))
            elif path.isdir(filename):
                if path.exists(path.join(filename, PackageModel.pckgIdnt)):
                    packages.append((file, PackageModel))
                else:
                    packages.append((file, FolderModel))

        packages.sort()
        for name, model in packages:
            self.InsertImageStringItem(self.GetItemCount(), name, model.imgIdx)

        modules.sort()
        for name, model in modules:
            self.InsertImageStringItem(self.GetItemCount(), name, model.imgIdx)

    def refreshTree(self, items):
        self.DeleteAllItems()
        self.filepath = ''

        for item in items:
            self.InsertImageStringItem(self.GetItemCount(), item, FolderModel.imgIdx)

    def OnItemSelect(self, event):
        self.selected = event.m_itemIndex

    def OnItemDeselect(self, event):
        self.selected = -1
           
class PackageFolderExplorer(wxSplitterWindow):
    def __init__(self, parent, images, root, editor):
        wxSplitterWindow.__init__(self, parent, wxID_PFE, style = wxSP_3D) #wxSP_NOBORDER)

        self.editor = editor
        self.list = PackageFolderList(self, images, root)
        EVT_LEFT_DCLICK(self.list, self.OnOpen)
        self.tree = PackageFolderTree(self, images, root)
        EVT_TREE_SEL_CHANGED(self, wxID_PFT, self.OnSelect)

        self.SplitVertically(self.tree, self.list, 200)

    def OnSelect(self, event):
        item = event.GetItem()
        filepath = self.tree.GetPyData(item)
        if filepath:
            self.list.refreshPath(filepath)
        else:
            self.list.refreshTree(self.tree.getChildrenNames())

    def OnOpen(self, event):
        if self.list.selected != -1:
            self.tree.Expand(self.tree.GetSelection())
            
            name = self.list.GetItemText(self.list.selected)
            file = path.join(self.list.filepath, name)
            if path.isdir(file) or not (self.list.filepath):
                chid = self.tree.getChildNamed(name)
                if chid >= 0:
                    self.tree.SelectItem(chid)
            else: 
                self.editor.openOrGotoModule(file)
