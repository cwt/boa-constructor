#----------------------------------------------------------------------
# Name:        Explorer.py
# Purpose:     Controls to explore and initialise different data sources
#
# Author:      Riaan Booysen
#
# Created:     2000/11/02
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2002 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

print 'importing Explorers'

from os import path
import os, sys
import string, time, glob, fnmatch
from types import StringType, ClassType

from wxPython.wx import *

import Preferences, Utils
from Preferences import IS, wxFileDialog

from Models import EditorHelper

import ExplorerNodes
from ExplorerNodes import TransportError, TransportLoadError, TransportSaveError

class TransportCategoryError(TransportError): pass

#---Explorer utility functions--------------------------------------------------

# Global reference to container for all transport protocols
# The first Explorer Tree created will define this
# XXX This attribute should move to ExplorerNodes
all_transports = None

def openEx(filename, transports=None):
    prot, category, respath, filename = splitURI(filename)
    if transports is None and all_transports:
        transports = all_transports
    return getTransport(prot, category, respath, transports)

def listdirEx(filepath, extfilter = ''):
    return filter(lambda f, extfilter=extfilter: \
          not extfilter or string.lower(os.path.splitext(f)[1]) == extfilter,
          map(lambda n: n.treename, openEx(filepath).openList()))

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
            if len(segs) < 2:
                raise TransportCategoryError('Category not found', filepath)
            category = segs[0]+'|'+segs[1][1:-1]
            return prot, category, string.join(segs[2:], '/'), filename

        # Other transports [prot]://[category]/[path] format
        elif prot == 'reg':
            try:
                category, respath = string.split(filepath, '//', 1)
            except:
                raise
            return prot, category, respath, filename
        else:
            idx = string.find(filepath, '/')
            if idx == -1:
                raise TransportCategoryError('Category not found', filepath)
            else:
                category, respath = filepath[:idx], filepath[idx+1:]
            return prot, category, respath, filename
    # Multiprot URIs
    elif len(protsplit) == 3:
        prot, zipfile, zipentry = protsplit
        if prot == 'zip':
            return prot, zipfile, zipentry, filename
        else:
            raise TransportError('Unhandled protocol: %s'%prot)
    else:
        raise TransportError('Too many protocol separators (://)')

def getTransport(prot, category, respath, transports):
    if prot == 'file':
        for tp in transports.entries:
            if tp.itemProtocol == 'file':
                return tp.getNodeFromPath(respath, forceFolder=false)
        raise 'FileSysCatNode not found in transports %s'%transports.entries
    elif prot == 'zip':
        from ZipExplorer import ZipFileNode
        zf = ZipFileNode(os.path.basename(category), category, None, -1, None, None)
        zf.openList()
        return zf.getNodeFromPath(respath)
    elif prot == 'zope':
        return findZopeExplorerNode(category, respath, transports)
    elif category:
        return findCatExplorerNode(prot, category, respath, transports)
    else:
        raise TransportError('Unhandled transport', (prot, category, respath))

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
        wxTreeCtrl.__init__(self, parent, wxID_PFT, style=wxTR_HAS_BUTTONS|wxCLIP_CHILDREN)
        EVT_TREE_ITEM_EXPANDING(self, wxID_PFT, self.OnOpen)
        EVT_TREE_ITEM_EXPANDED(self, wxID_PFT, self.OnOpened)
        EVT_TREE_ITEM_COLLAPSED(self, wxID_PFT, self.OnClose)
        self.SetImageList(images)
        self.itemCache = None
        self._ref_all_transp = false

        self.buildTree()

    def buildTree(self):
        conf = Utils.createAndReadConfig('Explorer')
        self.importExplorers(conf)

        # Create clipboards for all registered nodes
        self.clipboards = {'global': ExplorerNodes.GlobalClipper()}
        for Clss, info in ExplorerNodes.explorerNodeReg.items():
            Clip = info['clipboard']
            if type(Clip) == ClassType:
                self.clipboards[Clss.protocol] = Clip(self.clipboards['global'])

        # Root node and transports
        self.boaRoot = ExplorerNodes.RootNode('Boa Constructor')
        rootItem = self.AddRoot('', EditorHelper.imgBoaLogo, -1,
              wxTreeItemData(self.boaRoot))
        self.transports = ExplorerNodes.ContainerNode('Transport', EditorHelper.imgFolder)
        self.transports.entriesByProt = {}

        global all_transports
        if all_transports is None:
            all_transports = self.transports
            self._ref_all_transp = true

        self.transports.bold = true

        self.bookmarks = bookmarkCatNode = \
            ExplorerNodes.BookmarksCatNode(self.clipboards, conf, None,
            self.transports, self)

        assert self.clipboards.has_key('file'), 'File system transport must be loaded'

        # root level of the tree
        self.boaRoot.entries = [
            bookmarkCatNode,
            self.transports,
            ExplorerNodes.nodeRegByProt['sys.path'](self.clipboards['file'], None, bookmarkCatNode),
            ExplorerNodes.nodeRegByProt['os.cwd'](self.clipboards['file'], None, bookmarkCatNode),
            ExplorerNodes.nodeRegByProt['boa.prefs.group'](self.boaRoot),
            ]

        # Populate transports with registered node categories
        # Protocol also has to be defined in the explorer section of the config
        transport_order = eval(conf.get('explorer', 'transportstree'))
        for name in transport_order:
            for Clss in ExplorerNodes.explorerNodeReg.keys():
                if Clss.protocol == name:
                    Cat = ExplorerNodes.explorerNodeReg[Clss]['category']
                    if not Cat: break

                    Clip = ExplorerNodes.explorerNodeReg[Clss]['clipboard']
                    if type(Clip) == type(''):
                        clip = self.clipboards[Clip]
                    elif self.clipboards.has_key(Clss.protocol):
                        clip = self.clipboards[Clss.protocol]
                    else:
                        clip = None

                    confSect, confItem = ExplorerNodes.explorerNodeReg[Clss]['confdef']
                    if conf.has_option(confSect, confItem):
                        try:
                            cat = Cat(clip, conf, None, bookmarkCatNode)
                            self.transports.entries.append(cat)
                            self.transports.entriesByProt[Cat.itemProtocol] = cat
                        except Exception, error:
                            wxLogWarning('Transport category %s not added: %s'\
                                   %(Cat.defName, str(error)))
                    break

    def destroy(self):
        if self._ref_all_transp:
            global all_transports
            all_transports = None
        self.transports = None
        self.boaRoot = None
        self.clipboards = None
        self.defaultBookmarkItem = None
        self.bookmarks.cleanup()
        self.bookmarks = None

    def importExplorers(self, conf):
        """ Import names defined in the config files to register them """
        installedTransports = ['Explorers.PrefsExplorer'] + \
              eval(conf.get('explorer', 'installedtransports'))

        warned = false
        for moduleName in installedTransports:
            #moduleName = 'Explorers.%s'%moduleName
            try: 
                __import__(moduleName, globals())
            except ImportError, error: 
                wxLogWarning('%s not installed: %s' %(moduleName, str(error)))
                warned = true
            else: 
                ExplorerNodes.installedModules.append(moduleName)
        if warned:
            wxLogWarning('One or more transports could not be loaded, if the problem '
                         'is not rectifiable,\nconsider removing the transport from the '
                         '"installedtransports" list in the Explorer config. Click "Details"')

    def openDefaultNodes(self):
        rootItem = self.GetRootItem()
        self.SetItemHasChildren(rootItem, true)
        self.Expand(rootItem)

        bktn = self.getChildNamed(rootItem, 'Bookmarks')
        self.Expand(bktn)

        trtn = self.getChildNamed(rootItem, 'Transport')
        self.Expand(trtn)

        self.defaultBookmarkItem = self.getChildNamed(bktn,
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

        self.selected = -1

        self.items = None
        self.currImages = None
        
        self._destr = false

        self.setLocalFilter()

        Utils.ListCtrlLabelEditFixEH(self)

    def destroy(self, dont_pop=0):
        if self._destr: return
        
        self.DeleteAllItems()
        # XXX workaround for a crash, (better to leak than to crash ;)
        if not dont_pop:
            self.PopEventHandler(true)
        
        if self.node:
            self.node.destroy()
        self.currImages = None
        self.items = None
        self.node = None
        self._destr = true

    def EditLabel(self, index):
        try: return wxListCtrl.EditLabel(self, index)
        except AttributeError: return 0

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

    def setLocalFilter(self, filter='*'):
        if glob.has_magic(filter):
            self.localFilter = filter
        else:
            self.localFilter = '*'

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

        # Build a filtered, sorted list
        orderedList = []
        for itm in items:
            name = itm.treename or itm.name
            if fnmatch.fnmatch(name, self.localFilter):
                if Preferences.exCaseInsensitiveSorting:
                    sortName = string.lower(name)
                else:
                    sortName = name
                orderedList.append( (not itm.isFolderish(), sortName, name, itm) )
        if not explNode.vetoSort :
            orderedList.sort()

        # Populate the ctrl
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
        wxSplitterWindow.__init__(self, parent, wxID_PFE, 
              style = wxCLIP_CHILDREN | wxNO_3D|wxSP_3D)

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

        self.tree = PackageFolderTree(self, modimages, root)
        EVT_TREE_SEL_CHANGING(self, wxID_PFT, self.OnSelecting)
        EVT_TREE_SEL_CHANGED(self, wxID_PFT, self.OnSelect)

        self.controllers = self.initInstalledControllers()

        EVT_LIST_BEGIN_LABEL_EDIT(self, wxID_PFL, self.OnBeginLabelEdit)
        EVT_LIST_END_LABEL_EDIT(self, wxID_PFL, self.OnEndLabelEdit)

        #EVT_KEY_UP(self.tree, self.OnTreeKeyPressed)

        self.SplitVertically(self.tree, self.list, Preferences.exDefaultTreeWidth)

        self.SetMinimumPaneSize(self.GetSashSize())

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
        unqDct = {}
        for contr in self.controllers.values():
            unqDct[contr] = None
        for contr in unqDct.keys():
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

#---Create Controllers----------------------------------------------------------
    def initInstalledControllers(self):
        """ Creates controllers for built-in, plugged-in and installed nodes
            in the order specified by installedModules """
        controllers = {}
        links = []
        for instMod in ['Explorers.ExplorerNodes', 'PaletteMapping'] +\
                       ExplorerNodes.installedModules:
            for Clss, info in ExplorerNodes.explorerNodeReg.items():
                if Clss.__module__ == instMod and info['controller']:
                    Ctrlr = info['controller']
                    if type(Ctrlr) == type(''):
                        links.append((Clss.protocol, Ctrlr))
                    else:
                        controllers[Clss.protocol] = Ctrlr(self.editor,
                          self.list, self.editor.inspector, controllers)
        for protocol, link in links:
            controllers[protocol] = controllers[link]

        return controllers

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
                if event and event.AltDown() and \
                      self.controllers.has_key(self.list.node.protocol):
                    ctrlr = self.controllers[self.list.node.protocol]
                    if hasattr(ctrlr, 'OnInspectItem'):
                        ctrlr.OnInspectItem(None)
                        return
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
##        elif key == 9:
##            self.tree.SetFocus()
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
        
        if event.IsAllowed():
            event.Skip()

    def OnEndLabelEdit(self, event):
        newText = event.GetText()
        if newText != self.oldLabelVal:
            event.Skip()
            self.list.node.renameItem(self.oldLabelVal, newText)
            self.list.refreshCurrent()
            #self.list.selectItemNamed(newText)
        event.Skip()

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

##    def OnTreeKeyPressed(self, event):
##        key = event.KeyCode()
##        if key == 9:
##            self.list.SetFocus()
##        else:
##            event.Skip()

    def OnSplitterDoubleClick(self, event):
        pass
