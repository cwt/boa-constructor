#----------------------------------------------------------------------
# Name:        Explorer.py
# Purpose:     Controls to explore different data sources
#
# Author:      Riaan Booysen
#
# Created:     2000/11/02
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

from os import path
import os, sys
import string, time

from wxPython.wx import *

import Preferences, Utils
from Preferences import IS, wxFileDialog
from types import StringType
import EditorModels

import ExplorerNodes, FileExplorer, ZopeExplorer, CVSExplorer, SSHExplorer, ZipExplorer, FTPExplorer

(wxID_PFE, wxID_PFT, wxID_PFL) = map(lambda x: wxNewId(), range(3))

class PackageFolderTree(wxTreeCtrl):
    def __init__(self, parent, images, root):
        wxTreeCtrl.__init__(self, parent, wxID_PFT)
        EVT_TREE_ITEM_EXPANDING(self, wxID_PFT, self.OnOpen)
        EVT_TREE_ITEM_EXPANDED(self, wxID_PFT, self.OnOpened)
        EVT_TREE_ITEM_COLLAPSED(self, wxID_PFT, self.OnClose)
        self.SetImageList(images)

        self.globClip = ExplorerNodes.GlobalClipper()
        self.fsclip = FileExplorer.FileSysExpClipboard(self.globClip)
        self.sshClip = SSHExplorer.SSHExpClipboard(self.globClip)
        self.ftpClip = FTPExplorer.FTPExpClipboard(self.globClip)

        conf = Utils.createAndReadConfig('Explorer')
        self.boaRoot = ExplorerNodes.RootNode('Boa Constructor')
        rootItem = self.AddRoot('', EditorModels.imgBoaLogo, -1,
              wxTreeItemData(self.boaRoot))
        bookCatNode = ExplorerNodes.BookmarksCatNode(self.fsclip, conf, None)

        self.boaRoot.entries = [FileExplorer.FileSysCatNode(self.fsclip, conf,
              None, bookCatNode), bookCatNode,
              ExplorerNodes.SysPathNode(self.fsclip, None, bookCatNode)]
        if conf.has_option('explorer', 'zope'):
            self.boaRoot.entries.append(ZopeExplorer.ZopeCatNode(conf, None,
            self.globClip))
        if conf.has_option('explorer', 'ssh'):
            self.boaRoot.entries.append(SSHExplorer.SSHCatNode(self.sshClip,
            conf, None))
        if conf.has_option('explorer', 'ftp'):
            self.boaRoot.entries.append(FTPExplorer.FTPCatNode(self.ftpClip,
            conf, None))

        self.SetItemHasChildren(rootItem, true)
        self.Expand(rootItem)

        ws = self.getChildNamed(rootItem, 'Bookmarks')
        self.Expand(ws)

#        ws = self.getChildNamed(ws, 'Bookmarks')
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
                lst = data.openList()
                hasFolders = false
                for itm in lst:
                    if itm.isFolderish():
                        hasFolders = true
                        new = self.AppendItem(item, itm.treename or itm.name,
                              itm.imgIdx, -1, wxTreeItemData(itm))
                        self.SetItemHasChildren(new, true)
                        if itm.bold: self.SetItemBold(new, true)
            finally:
                wxEndBusyCursor()

        self.SetItemHasChildren(item, hasFolders)

    def OnClose(self, event):
        item = event.GetItem()
        data = self.GetPyData(item)
        data.closeList()
##        if type(data) == StringType: pass
##        elif issubclass(data.__class__, ZopeItemNode):
##            data.closeList()
##            self.DeleteChildren(item)

class PackageFolderList(wxListCtrl):
    def __init__(self, parent, filepath, pos = wxDefaultPosition, size = wxDefaultSize, updateNotify = None, style = 0):
        wxListCtrl.__init__(self, parent, wxID_PFL, pos = pos, size = size, style = wxLC_LIST | wxLC_EDIT_LABELS | style)
        self.filepath = filepath
#        self.exts = map(lambda C: C.ext, modelReg.values())
        self.idxOffset = 0
        self.updateNotify = updateNotify
        self.node = None

##        EVT_LIST_ITEM_SELECTED(self, wxID_PFL, self.OnItemSelect)
##        EVT_LIST_ITEM_DESELECTED(self, wxID_PFL, self.OnItemDeselect)

        self.selected = -1

        self.items = None
        self.currImages = None

    def selectItemNamed(self, name):
        for idx in range(self.GetItemCount()):
            item = self.GetItem(idx)
            if item.GetText() == name:
                item.SetState(wxLIST_STATE_FOCUSED | wxLIST_STATE_SELECTED)
                self.SetItem(item)

    def getSelection(self):
        if self.selected >= self.idxOffset:
            return self.items[self.selected-self.idxOffset]
        else:
            return None

    def getMultiSelection(self):
        """ Returns list of indexes that map back to node list"""
        res = []
        for idx in range(self.idxOffset, self.GetItemCount()):
            if self.GetItemState(idx, wxLIST_STATE_SELECTED):
                res.append(idx-self.idxOffset)
        return res

    def refreshCurrent(self):
        self.refreshItems(self.currImages, self.node)

    def refreshItems(self, images, explNode):
        """ Display ExplorerNode items """
        self.selected = -1

#        if explNode: explNode.destroy()

        self.node = explNode
        self.DeleteAllItems()
        self.SetImageList(images, wxIMAGE_LIST_SMALL)
        self.currImages = images

        wxBeginBusyCursor()
        try: self.items = explNode.openList()
        finally: wxEndBusyCursor()

        self.InsertImageStringItem(self.GetItemCount(), '..', explNode.upImgIdx)
        self.idxOffset = 1
        for itm in self.items:
            self.InsertImageStringItem(self.GetItemCount(),
                  itm.treename or itm.name, itm.imgIdx)

        self.filepath = explNode.resourcepath

        if self.updateNotify:
            self.updateNotify()

    def OnItemSelect(self, event):
        self.selected = event.m_itemIndex
        event.Skip()

    def OnItemDeselect(self, event):
        self.selected = -1
        event.Skip()

class ExplorerSplitter(wxSplitterWindow):
    def __init__(self, parent, modimages, root, editor):
        wxSplitterWindow.__init__(self, parent, wxID_PFE, style = wxNO_3D|wxSP_3D)#style = wxSP_3D) #wxSP_NOBORDER)

        self.editor = editor
        self.list = PackageFolderList(self, root, updateNotify = self.OnUpdateNotify)
        self.modimages = modimages

        EVT_LEFT_DCLICK(self.list, self.OnOpen)
        EVT_KEY_UP(self.list, self.OnKeyPressed)
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
                FTPExplorer.FTPController(editor, self.list),#, editor.inspector),
              ExplorerNodes.CategoryNode.protocol: \
                ExplorerNodes.CategoryController(editor, self.list, editor.inspector),
              }

        self.tree = PackageFolderTree(self, modimages, root)
        EVT_TREE_SEL_CHANGING(self, wxID_PFT, self.OnSelecting)
        EVT_TREE_SEL_CHANGED(self, wxID_PFT, self.OnSelect)

        EVT_LIST_BEGIN_LABEL_EDIT(self, wxID_PFL, self.OnBeginLabelEdit)
        EVT_LIST_END_LABEL_EDIT(self, wxID_PFL, self.OnEndLabelEdit)

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
        del self.editor

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
#        self.addTools(self.editor.toolBar)
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
                        self.tree.Expand(tItm)
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

    def OnEndLabelEdit(self, event):
        newText = event.GetText()
        if newText != self.oldLabelVal:# and isinstance(self.list.node, ZopeItemNode):
            event.Skip()
            self.list.node.renameItem(self.oldLabelVal, newText)
            self.list.refreshCurrent()

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
