#----------------------------------------------------------------------
# Name:        Explorer.py
# Purpose:     Controls to explore different data sources
#
# Author:      Riaan Booysen
#
# Created:     2000/11/02
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2001 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

print 'importing Explorers'

from os import path
import os, sys
import string, time
from types import StringType

##sys.path.append('..')

from wxPython.wx import *

import Preferences, Utils
from Preferences import IS, wxFileDialog
import EditorHelper

import ExplorerNodes, FileExplorer, ZopeExplorer, CVSExplorer, SSHExplorer
import ZipExplorer, FTPExplorer, PrefsExplorer
try: import DAVExplorer
except ImportError: DAVExplorer = None

from ExplorerNodes import TransportLoadError, TransportSaveError

#---Explorer utility functions--------------------------------------------------

# Global reference to container for all transport protocols
# The first Explorer Tree created will define this
all_transports = None

def openEx(filename, transports=None):
    prot, category, respath, filename = splitURI(filename)
    if transports is None and all_transports:
        transports = all_transports
    return getTransport(prot, category, respath, transports)

def splitURI(filename):
    protsplit = string.split(filename, '://')
    # check FS (No prot defaults to 'file')
    if len(protsplit) == 1:
        return 'file', '', filename, 'file://'+filename
    elif len(protsplit) == 2:
        prot, filepath = protsplit
        # file://[path] format
        if prot == 'file':
            return prot, '', filepath, filename
        # zope://[category]/<[meta type]>/[path] format
        elif prot == 'zope':
            segs = string.split(filepath, '/')
            category = segs[0]+'|'+segs[1][1:-1]
            return prot, category, string.join(segs[2:], '/'), filename
        # Other transports [prot]://[category]/[path] format
        else:
            idx = string.find(filepath, '/')
            if idx == -1:
                raise 'No category found: '+`filepath`
                #category, filepath = filepath, ''
                #respath = fname
            else:
                category, respath = filepath[:idx], filepath[idx+1:]
                #respath = os.path.split(filepath)#dirname+'/'+fname

            return prot, category, respath, filename
    elif len(protsplit) == 3:
        prot, zipfile, zipentry = protsplit
        if prot == 'zip':
            return prot, zipfile, zipentry, filename
        else:
            raise 'Unhandled prot'
    else:
        raise 'Too many ://s'

def getTransport(prot, category, respath, transports):
    if prot == 'file':
        for tp in transports.entries:
            if tp.itemProtocol == 'file':
                return tp.getNodeFromPath(respath)
        raise 'FileSysCatNode not found in transports'
    elif prot == 'zip':
        from ZipExplorer import ZipFileNode
        zf = ZipFileNode(os.path.basename(category), category, None, 
                    -1, None, None)                
        zf.openList()
        return zf.getNodeFromPath(respath)
    elif prot == 'zope':
        return findZopeExplorerNode(category, respath, transports)
    elif category:
        return findCatExplorerNode(prot, category, respath, transports)
    else:
        print 'Unhandled transport (%s, %s, %s)'%(prot, category, respath)
        return None

def findCatExplorerNode(prot, category, respath, transports):
    for cat in transports.entries:
        if cat.itemProtocol == prot:
            itms = cat.openList()
            for itm in itms:
                if itm.name == category or itm.treename == category:
                    # connect if not a stateless protocol
                    #if itm.connection:
                    #    itm.openList()
                    return itm.getNodeFromPath(respath)
    return None

def findZopeExplorerNode(catandmeta, respath, transports):
    category, metatype = string.split(catandmeta, '|')
    for cat in transports.entries:
        if cat.itemProtocol == 'zope':
            itms = cat.openList()
            for itm in itms:
                if itm.name == category or itm.treename == category:
                    return itm.getNodeFromPath('/'+respath, metatype)
    return None

(wxID_PFE, wxID_PFT, wxID_PFL) = Utils.wxNewIds(3)

class PackageFolderTree(wxTreeCtrl):
    def __init__(self, parent, images, root):
        wxTreeCtrl.__init__(self, parent, wxID_PFT)
        EVT_TREE_ITEM_EXPANDING(self, wxID_PFT, self.OnOpen)
        EVT_TREE_ITEM_EXPANDED(self, wxID_PFT, self.OnOpened)
        EVT_TREE_ITEM_COLLAPSED(self, wxID_PFT, self.OnClose)
        self.SetImageList(images)
        self.itemCache = None
        self._ref_all_transp = false
        
        self.globClip = ExplorerNodes.GlobalClipper()
        self.fsclip = FileExplorer.FileSysExpClipboard(self.globClip)
        self.sshClip = SSHExplorer.SSHExpClipboard(self.globClip)
        self.ftpClip = FTPExplorer.FTPExpClipboard(self.globClip)
        clipboards = {'global': self.globClip, 'file': self.fsclip,
                      'ssh': self.sshClip, 'ftp': self.ftpClip}
        if DAVExplorer:
            self.davClip = DAVExplorer.DAVExpClipboard(self.globClip)
            clipboards['dav'] = self.davClip

        conf = Utils.createAndReadConfig('Explorer')
        self.boaRoot = ExplorerNodes.RootNode('Boa Constructor')
        rootItem = self.AddRoot('', EditorHelper.imgBoaLogo, -1,
              wxTreeItemData(self.boaRoot))

        self.transports = ExplorerNodes.ContainerNode('Transport', EditorHelper.imgFolder)
        global all_transports
        if all_transports is None:
            all_transports = self.transports
            self._ref_all_transp = true
        
        self.transports.bold = true

        bookmarkCatNode = ExplorerNodes.BookmarksCatNode(clipboards, conf, None, 
              self.transports, self)

        self.boaRoot.entries = [
            bookmarkCatNode,
            self.transports,
            ExplorerNodes.SysPathNode(self.fsclip, None, bookmarkCatNode),
            FileExplorer.CurWorkDirNode(self.fsclip, None, bookmarkCatNode),
            PrefsExplorer.BoaPrefGroupNode(self.boaRoot),
            ]
        
        self.transports.entries.append(FileExplorer.FileSysCatNode(self.fsclip, 
              conf, None, bookmarkCatNode))
        if conf.has_option('explorer', 'zope'):
            self.transports.entries.append(ZopeExplorer.ZopeCatNode(conf, None,
            self.globClip, bookmarkCatNode))
        if conf.has_option('explorer', 'ssh'):
            self.transports.entries.append(SSHExplorer.SSHCatNode(self.sshClip,
            conf, None, bookmarkCatNode))
        if conf.has_option('explorer', 'ftp'):
            self.transports.entries.append(FTPExplorer.FTPCatNode(self.ftpClip,
            conf, None, bookmarkCatNode))
        if DAVExplorer and conf.has_option('explorer', 'dav'):
            self.transports.entries.append(DAVExplorer.DAVCatNode(self.davClip,
            conf, None, bookmarkCatNode))

    def destroy(self):
        if self._ref_all_transp:
            global all_transports
            all_transports = None

    def openDefaultNodes(self):
        rootItem = self.GetRootItem()
        self.SetItemHasChildren(rootItem, true)
        self.Expand(rootItem)

        ws = self.getChildNamed(rootItem, 'Bookmarks')
        self.Expand(ws)

        ws = self.getChildNamed(rootItem, 'Transport')
        self.Expand(ws)

        self.defaultBookmarkItem = self.getChildNamed(ws,
              self.boaRoot.entries[1].getDefault())

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

    def getChildNamed(self, node, name):
        cookie = 0
        child, cookie = self.GetFirstChild(node, cookie)
        while child.IsOk() and self.GetItemText(child) != name:
            child, cookie = self.GetNextChild(node, cookie)
        return child

    def OnOpened(self, event):
        pass

    def OnOpen(self, event):
        item = event.GetItem()
        if self.IsExpanded(item): return
        data = self.GetPyData(item)
        hasFolders = true
        if data:
            wxBeginBusyCursor()
            try:
                self.DeleteChildren(item)
                if self.itemCache:
                    lst = self.itemCache[:]
                else:
                    lst = data.openList()
                hasFolders = false
                for itm in lst:
                    if itm.isFolderish():
                        hasFolders = true
                        new = self.AppendItem(item, itm.treename or itm.name,
                              itm.imgIdx, -1, wxTreeItemData(itm))
                        self.SetItemHasChildren(new, true)
                        if itm.bold: 
                            self.SetItemBold(new, true)
                        if itm.refTree:
                            itm.treeitem = new
            finally:
                wxEndBusyCursor()

        self.SetItemHasChildren(item, hasFolders)

    def OnClose(self, event):
        item = event.GetItem()
        data = self.GetPyData(item)
        data.closeList()


class PackageFolderList(wxListCtrl):
    def __init__(self, parent, filepath, pos=wxDefaultPosition, 
          size=wxDefaultSize, updateNotify=None, style=0):
        wxListCtrl.__init__(self, parent, wxID_PFL, pos=pos, size=size, 
              style=wxLC_LIST | wxLC_EDIT_LABELS | style)
        self.filepath = filepath
        self.idxOffset = 0
        self.updateNotify = updateNotify
        self.node = None

##        EVT_LIST_ITEM_SELECTED(self, wxID_PFL, self.OnItemSelect)
##        EVT_LIST_ITEM_DESELECTED(self, wxID_PFL, self.OnItemDeselect)

        self.selected = -1

        self.items = None
        self.currImages = None

    def destroy(self):
        if self.node:
            self.node.destroy()
        self.currImages = None
        self.items = None
        self.node = None

    def selectItemNamed(self, name):
        for idx in range(self.GetItemCount()):
            item = self.GetItem(idx)
            if item.GetText() == name:
                item.SetState(wxLIST_STATE_FOCUSED | wxLIST_STATE_SELECTED)
                self.SetItem(item)
                return item

    def selectItemByIdx(self, idx):
        item = self.GetItem(idx)
        item.SetState(wxLIST_STATE_FOCUSED | wxLIST_STATE_SELECTED)
        self.SetItem(item)
        return item

    def hasItemNamed(self, name):
        for idx in range(self.GetItemCount()):
            if self.GetItemText(idx) == name:
                return true
        return false

    def getAllNames(self):
        names = []
        for idx in range(self.GetItemCount()):
            name = self.GetItemText(idx)
            if name != '..':
                names.append(name)
        return names

    def getSelection(self):
        # XXX Fix, this can return IndexErrors !!!
        if self.selected >= self.idxOffset:
            return self.items[self.selected-self.idxOffset]
        else:
            return None

    def getMultiSelection(self):
        """ Returns list of indexes that map back to node list """
        res = []
        # if deselection occured, ignore item state and return []
        if self.selected == -1:
            return res
        for idx in range(self.idxOffset, self.GetItemCount()):
            if self.GetItemState(idx, wxLIST_STATE_SELECTED):
                res.append(idx-self.idxOffset)
        return res

    def refreshCurrent(self):
        self.refreshItems(self.currImages, self.node)

    def refreshItems(self, images, explNode):
        """ Display ExplorerNode items """
        self.selected = -1

        if self.node:
            self.node.destroy()

        self.node = explNode
        self.DeleteAllItems()
        self.SetImageList(images, wxIMAGE_LIST_SMALL)
        self.currImages = images

        wxBeginBusyCursor()
        try: items = explNode.openList()
        finally: wxEndBusyCursor()
        
        orderedList = []
        for itm in items:
            name = itm.treename or itm.name
            orderedList.append( (not itm.isFolderish(), string.lower(name), 
                                 name, itm) )
        if not explNode.vetoSort:
            orderedList.sort()

        self.items = []
        self.InsertImageStringItem(self.GetItemCount(), '..', explNode.upImgIdx)
        self.idxOffset = 1
        for dummy, dummy, name, itm in orderedList:
            self.items.append(itm)
            self.InsertImageStringItem(self.GetItemCount(), name, itm.imgIdx)

        self.filepath = explNode.resourcepath

        if self.updateNotify:
            self.updateNotify()

    def OnItemSelect(self, event):
        self.selected = event.m_itemIndex
        event.Skip()

    def OnItemDeselect(self, event):
        if not self.GetSelectedItemCount():
            self.selected = -1
        event.Skip()

class ExplorerSplitter(wxSplitterWindow):
    def __init__(self, parent, modimages, root, editor):
        wxSplitterWindow.__init__(self, parent, wxID_PFE, style = wxNO_3D|wxSP_3D)

        self.editor = editor
        self.list = PackageFolderList(self, root, updateNotify = self.OnUpdateNotify)
        self.modimages = modimages

        EVT_KEY_UP(self.list, self.OnKeyPressed)
 
        EVT_LEFT_DCLICK(self.list, self.OnOpen)
        EVT_LEFT_DOWN(self.list, self.OnListClick)

        EVT_RIGHT_DOWN(self.list, self.OnListRightDown)
        EVT_RIGHT_UP(self.list, self.OnListRightUp)

        EVT_LIST_ITEM_SELECTED(self.list, wxID_PFL, self.OnItemSelect)
        EVT_LIST_ITEM_DESELECTED(self.list, wxID_PFL, self.OnItemDeselect)

        cvsController = CVSExplorer.CVSController(editor, self.list)
        self.controllers = { \
              FileExplorer.PyFileNode.protocol: \
                FileExplorer.FileSysController(editor, self.list, cvsController),
              ZopeExplorer.ZopeItemNode.protocol: \
                ZopeExplorer.ZopeController(editor, self.list, editor.inspector),
              CVSExplorer.FSCVSFolderNode.protocol: cvsController,
              SSHExplorer.SSHItemNode.protocol: \
                SSHExplorer.SSHController(editor, self.list),
              ZipExplorer.ZipItemNode.protocol: \
                ZipExplorer.ZipController(editor, self.list),
              FTPExplorer.FTPItemNode.protocol: \
                FTPExplorer.FTPController(editor, self.list),
              ExplorerNodes.CategoryNode.protocol: \
                ExplorerNodes.CategoryController(editor, self.list, editor.inspector),
              ZopeExplorer.ZopeCatNode.protocol: \
                ZopeExplorer.ZopeCatController(editor, self.list, editor.inspector),
              }
        if DAVExplorer:
            self.controllers[DAVExplorer.DAVItemNode.protocol] = \
                DAVExplorer.DAVController(editor, self.list, editor.inspector)

        self.tree = PackageFolderTree(self, modimages, root)
        EVT_TREE_SEL_CHANGING(self, wxID_PFT, self.OnSelecting)
        EVT_TREE_SEL_CHANGED(self, wxID_PFT, self.OnSelect)

        EVT_LIST_BEGIN_LABEL_EDIT(self, wxID_PFL, self.OnBeginLabelEdit)
        EVT_LIST_END_LABEL_EDIT(self, wxID_PFL, self.OnEndLabelEdit)

        EVT_KEY_UP(self.tree, self.OnTreeKeyPressed)

        self.SplitVertically(self.tree, self.list, 200)
        self.list.SetFocus()

    def addTools(self, toolbar):
        if self.list.node and self.controllers.has_key(self.list.node.protocol):
            prot = self.list.node.protocol
            tbMenus = []
            for menuLst in self.controllers[prot].toolbarMenus:
                tbMenus.extend(list(menuLst))

            for wID, name, meth, bmp in tbMenus:
                if name == '-' and not bmp:
                    toolbar.AddSeparator()
                elif bmp != '-':
                    if name[0] == '+':
                        # XXX Add toggle button
                        name = name [1:]
                    Utils.AddToolButtonBmpObject(self.editor, toolbar,
                          IS.load(bmp), name, meth)

    def getMenu(self):
        if self.list.node and self.controllers.has_key(self.list.node.protocol):
            return self.controllers[self.list.node.protocol].menu
        else:
            return None

    def destroy(self):
        self.modimages = None
        self.list.destroy()
        self.tree.destroy()
        for contr in self.controllers.values():
            contr.destroy()
        del self.controllers
        del self.list
        del self.editor
    
    def editorUpdateNotify(self):
        if self.list.node and self.controllers.has_key(self.list.node.protocol):
            self.controllers[self.list.node.protocol].editorUpdateNotify()
        
    def selectTreeItem(self, item):
        data = self.tree.GetPyData(item)
        title = self.tree.GetItemText(item)
        if data:
            imgs = data.images
            if not imgs: imgs = self.modimages
            self.list.refreshItems(imgs, data)
            title = data.getTitle()

        self.editor.SetTitle('Editor - Explorer - %s' % title)

    def OnUpdateNotify(self):
        tItm = self.tree.GetSelection()
        # XXX this should be smarter, only refresh on folderish name change
        # XXX add or remove
        if not self.selecting and self.tree.IsExpanded(tItm):
            self.tree.Collapse(tItm)
            self.tree.Expand(tItm)

        # XXX this is ugly :(
        # only update toolbar when the explorer is active
        if self.editor.tabs.GetSelection() == 1:
            self.editor.setupToolBar(1)

    def OnSelecting(self, event):
        self.selecting = true

    def OnSelect(self, event):
        # Event is triggered twice, work around with flag
        if self.selecting:
            item = event.GetItem()
            self.selectTreeItem(item)
        self.selecting = false

        event.Skip()

    def OnOpen(self, event):
        if self.list.selected != -1:
            name = self.list.GetItemText(self.list.selected)
            nd = self.list.node
            if name == '..':
                if not nd.openParent(self.editor):
                    treeItem = self.tree.GetItemParent(self.tree.GetSelection())
                    if treeItem.IsOk():
                        self.tree.SelectItem(treeItem)
            else:
                item = self.list.items[self.list.selected-1]
                if item.isFolderish():
                    tItm = self.tree.GetSelection()
                    if not self.tree.IsExpanded(tItm):
                        self.tree.itemCache = self.list.items
                        try: self.tree.Expand(tItm)
                        finally: self.tree.itemCache = None
                    chid = self.tree.getChildNamed(self.tree.GetSelection(), name)
                    self.tree.SelectItem(chid)
                elif nd.parentOpensChildren:
                    nd.open(item, self.editor)
                else:
                    item.open(self.editor)

    def OnKeyPressed(self, event):
        key = event.KeyCode()
        if key == 13:
            self.OnOpen(event)
        elif key == 9:
            self.tree.SetFocus()
        else:
            event.Skip()

    def OnListClick(self, event):
        palette = self.editor.palette

        if palette.componentSB.selection and self.list.node and \
              self.list.node.canAdd(palette.componentSB.prevPage.name):
            name, desc, Compn = palette.componentSB.selection
            newName = self.list.node.newItem(name, Compn)
            try:
                self.list.refreshCurrent()
                self.list.selectItemNamed(newName)
            finally:
                palette.componentSB.selectNone()
        else:
            event.Skip()

    def OnBeginLabelEdit(self, event):
        self.oldLabelVal = event.GetText()
        if self.list.node:
            self.list.node.notifyBeginLabelEdit(event)

    def OnEndLabelEdit(self, event):
        newText = event.GetText()
        if newText != self.oldLabelVal:
            event.Skip()
            self.list.node.renameItem(self.oldLabelVal, newText)
            self.list.refreshCurrent()
            #self.list.selectItemNamed(newText)

    def OnListRightDown(self, event):
        self.listPopPt = wxPoint(event.GetX(), event.GetY())

    def OnListRightUp(self, event):
        if self.list.node and self.controllers.has_key(self.list.node.protocol):
            self.list.PopupMenu(self.controllers[self.list.node.protocol].menu,
                  self.listPopPt)

    def OnItemSelect(self, event):
        self.list.OnItemSelect(event)
        if self.list.node:
            sel = self.list.getSelection()
            if not sel: sel = self.list.node
            self.editor.statusBar.setHint(sel.getDescription())

    def OnItemDeselect(self, event):
        self.list.OnItemDeselect(event)
        if self.list.node:
            self.editor.statusBar.setHint(self.list.node.getDescription())

    def OnTreeKeyPressed(self, event):
        key = event.KeyCode()
        if key == 9:
            self.list.SetFocus()
        else:
            event.Skip()

 