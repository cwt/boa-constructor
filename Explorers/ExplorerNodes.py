#-----------------------------------------------------------------------------
# Name:        ExplorerNodes.py
# Purpose:     Explorer base classes for nodes, controllers and companions
#
# Author:      Riaan Booysen
#
# Created:     2001
# RCS-ID:      $Id$
# Copyright:   (c) 2001 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------

from os import path
import string, sys, os, time, stat, copy, pprint

from wxPython import wx

import EditorHelper, Utils, Preferences
import scrm
false = 0;true = 1

sensitive_properties = ('passwd', 'scp_pass')

# Folderish objects are creators
# Folderish objects are connected to a clipboard and maintain their children

# XXX Active models open in the editors should be returned on list queries

# XXX define a filtering interface

# Guidelines
#  Creation of a node should be cheap and not significant resources
#  Opening/getting the contents/sublists should start connections/resources

# Accelerator shortcuts
    
class GlobalClipper:
    def __init__(self):
        self.currentClipboard = None

class ClipboardException(Exception):
    def __init__(self, source, dest):
        self.source = source
        self.dest = dest

class ExplorerClipboard:
    """ """
    # XXX Base class should implement recursive traversal by using explorer intf

    def __init__(self, globClip):
        self.globClip = globClip
        self.clipNodes = []
        self.clipMode = ''
    def clipCut(self, node, nodes):
        self.globClip.currentClipboard = self
        self.clipNodes = nodes
        self.clipMode = 'cut'
    def clipCopy(self, node, nodes):
        self.globClip.currentClipboard = self
        self.clipNodes = nodes
        self.clipMode = 'copy'
    def clipPaste_Default(self, destNode, sourceNodes, clipMode):
        for srcNode in sourceNodes:
            destName = destNode.resourcepath+'/'+srcNode.name
            newDestNode = destNode.getNodeFromPath(destName)
            newDestNode.save(destName, srcNode.load())
            if clipMode == 'cut':
                # XXX delete items
                pass
    def clipPaste(self, node):
        if self.globClip.currentClipboard:
            methName = 'clipPaste_'+self.globClip.currentClipboard.__class__.__name__
            try:
                clipMeth = eval('self.%s' % methName)
            except AttributeError, message:
                clipMeth = self.clipPaste_Default
            clipMeth(node, self.globClip.currentClipboard.clipNodes,
                  self.globClip.currentClipboard.clipMode)

class Controller:
    Node = None
    def __init__(self, editor):
        self.editor = editor

    def editorUpdateNotify(self, info=''):
        pass

    def setupMenu(self, menu, win, menus):
        for wId, help, method, bmp in menus:
            if help != '-':
                if help[0] == '+':
                    canCheck = true
                    help = help[1:]
                else:
                    canCheck = false
                
                if type(method) == type(()):
                    subMenu = wx.wxMenu()
                    self.setupMenu(subMenu, win, method)
                    menu.AppendMenu(wId, help, subMenu)
                else:
                    menu.Append(wId, help, checkable = canCheck)
                    wx.EVT_MENU(win, wId, method)
                    wx.EVT_MENU(self.editor, wId, method)
            else:
                menu.AppendSeparator()

    def destroy(self):
        # break circular references here
        pass

    def groupToggleCheckMenu(self, menu, menuDef, wCheckId):
        checked = not menu.IsChecked(wCheckId)
        self.groupCheckMenu(menu, menuDef, wCheckId, checked)

    def groupCheckMenu(self, menu, menuDef, wCheckId, checked):
        for wId, help, method, bmp in menuDef:
            if wId == wCheckId:
                menu.Check(wId, checked)
            else:
                menu.Check(wId, not checked)

    def getName(self, item):
        if item.treename:
            return item.treename
        elif item.name:
            return item.name

    def getNamesForSelection(self, idxs):
        res = []
        for idx in idxs:
            res.append(self.getName(self.list.items[idx]))
        return res

    def getNodesForSelection(self, idxs):
        res = []
        for idx in idxs:
            res.append(self.list.items[idx])
        return res

    def createNode(self, category, name, resourcepath, uri):
        return self.Node(name, resourcepath, None, -1, None, None,
              properties = {})
        

(wxID_CLIPCUT, wxID_CLIPCOPY, wxID_CLIPPASTE, wxID_CLIPDELETE, wxID_CLIPRENAME,
 wxID_CLIPNEWFOLDER, wxID_CLIPNEWBLANKDOC, wxID_CLIPRELOAD, wxID_CLIPBOOKMARK) \
 = Utils.winIdRange(9)

# XXX Maybe needs to be called StandardControllerMixin ??
class ClipboardControllerMix:
    cutBmp = 'Images/Shared/Cut.bmp'
    copyBmp = 'Images/Shared/Copy.bmp'
    pasteBmp = 'Images/Shared/Paste.bmp'
    deleteBmp = 'Images/Shared/Delete.bmp'
    bookmarkBmp = 'Images/Shared/Bookmark.bmp'
    def __init__(self):
        self.clipMenuDef = ( (wxID_CLIPRELOAD, 'Reload', self.OnReloadItems, '-'),
                             (-1, '-', None, '-'),
                             (wxID_CLIPCUT, 'Cut', self.OnCutItems, self.cutBmp),
                             (wxID_CLIPCOPY, 'Copy', self.OnCopyItems, self.copyBmp),
                             (wxID_CLIPPASTE, 'Paste', self.OnPasteItems, self.pasteBmp),
                             (-1, '-', None, ''),
                             (wxID_CLIPDELETE, 'Delete', self.OnDeleteItems, self.deleteBmp),
                             (wxID_CLIPRENAME, 'Rename', self.OnRenameItems, '-'),
                             (-1, '-', None, ''),
                             (wxID_CLIPBOOKMARK, 'Bookmark folder', self.OnBookmarkItems, self.bookmarkBmp),
                             (wx.wxNewId(), 'New', (
                               (wxID_CLIPNEWFOLDER, 'Folder', self.OnNewFolder, '-'),
                               (wxID_CLIPNEWBLANKDOC, 'Blank document', self.OnNewBlankDoc, '-'),
                             ), '-'),
                              )
    def destroy(self):
        self.clipMenuDef = ()

    def OnCutItems(self, event):
        if self.list.node:
            nodes = self.getNodesForSelection(self.list.getMultiSelection())
            self.list.node.clipCut(nodes)

    def OnCopyItems(self, event):
        if self.list.node:
            nodes = self.getNodesForSelection(self.list.getMultiSelection())
            self.list.node.clipCopy(nodes)

    def OnPasteItems(self, event):
        if self.list.node:
            wx.wxBeginBusyCursor()
            try:
                self.list.node.clipPaste()
                self.list.refreshCurrent()
            finally:
                wx.wxEndBusyCursor()

    def OnDeleteItems(self, event):
        if self.list.node:
            wx.wxBeginBusyCursor()
            try:
                names = self.getNamesForSelection(self.list.getMultiSelection())
                self.list.node.deleteItems(names)
                self.list.refreshCurrent()
            finally:
                wx.wxEndBusyCursor()

    def OnRenameItems(self, event):
        self.list.EditLabel(self.list.selected)

    def OnOpenItems(self, event):
        if self.list.node:
            nodes = self.getNodesForSelection(self.list.getMultiSelection())
            for node in nodes:
                if not node.isFolderish():
                    node.open(self.editor)

    def OnNewFolder(self, event):
        if self.list.node:
            name = Utils.getValidName(self.list.getAllNames(), 'Folder')
            wx.wxBeginBusyCursor()
            try:
                self.list.node.newFolder(name)
            finally:
                wx.wxEndBusyCursor()
            self.list.refreshCurrent()
            self.list.selectItemNamed(name)
            self.list.EnsureVisible(self.list.selected)
            self.list.EditLabel(self.list.selected)

    def OnNewBlankDoc(self, event):
        if self.list.node:
            name = Utils.getValidName(self.list.getAllNames(), 'BlankDoc')
            wx.wxBeginBusyCursor()
            try:
                self.list.node.newBlankDocument(name)
            finally:
                wx.wxEndBusyCursor()
            self.list.refreshCurrent()
            self.list.selectItemNamed(name)
            self.list.EnsureVisible(self.list.selected)
            self.list.EditLabel(self.list.selected)

    def OnReloadItems(self, event):
        if self.list.node:
            self.list.refreshCurrent()

    def OnBookmarkItems(self, event):
        if self.list.node:
            nodes = self.getNodesForSelection(self.list.getMultiSelection())
            for node in nodes:
                if node.bookmarks:
                    if node.isFolderish():
                        node.bookmarks.add(node.getURI())
                        self.editor.statusBar.setHint('Bookmarked %s'% node.resourcepath, 'Info')
                    else:
                        self.editor.statusBar.setHint('Not a directory: %s'% node.resourcepath, 'Error')

class TransportError(Exception):
    def __str__(self): 
        return str(self.args[0])

class TransportLoadError(TransportError): 
    pass
class TransportSaveError(TransportError): 
    pass   
 

class ExplorerNode:
    """ Base class for items in the explorer. """
    # Protocol identifier, used to associate with controller
    protocol = 'none'
    images = None
    viewMode = 'list'
    pathSep = '/'
    # Is it a stateless protocol or does it require a connection
    connection = false
    filter = ''
    # Should the node keep a reference to it's possible tree item
    refTree = false
    def __init__(self, name, resourcepath, clipboard, imgIdx, parent = None, properties = None):
        self.name = name
        self.resourcepath = resourcepath
        self.imgIdx = imgIdx
        if properties is None: properties = {}
        self.properties = properties
        self.clipboard = clipboard
        self.parent = parent
        self.treename = name
        self.treeitem = None
        self.bold = false
        self.vetoRequery = false
        self.vetoSort = false
        self.upImgIdx = EditorHelper.imgFolderUp
        self.parentOpensChildren = false
        self.category = ''
        self.stdAttrs = {'size': 0,
                         'creation-date': 0.0,
                         'modify-date': 0.0,
                         'read-only': 0}
##    def __del__(self): pass
##        print '__del__', self.__class__.__name__
    def destroy(self):pass
    def createParentNode(self): return self.parent
    def createChildNode(self, value): pass
    def openList(self): pass
    def closeList(self): pass
    def isFolderish(self): return false
    def getTitle(self):
        if self.resourcepath: return self.resourcepath
        else: return self.name
    def getURI(self):
        return '%s://%s%s'%(self.protocol, self.category, self.getTitle())
    def getDescription(self):
        return self.getURI()
    def notifyBeginLabelEdit(self, event):
        if event.GetLabel() == '..': event.Veto()
    def getNodeFromPath(self, respath):
        return None
    def setFilter(self, filter):
        pass
#---Default item actions--------------------------------------------------------
    def open(self, editor):
        return editor.openOrGotoModule(self.getURI(), transport = self)
    def openParent(self, editor): return false
    def checkOpenInEditor(self): return false

#---Methods on sub items--------------------------------------------------------
    def deleteItems(self, names): pass
    def renameItem(self, name, newName): pass
    def newFolder(self, name): pass
    def newBlankDocument(self, name): pass

#---Clipboard methods-----------------------------------------------------------
    def clipCut(self, nodes):
        self.clipboard.clipCut(self, nodes)
    def clipCopy(self, nodes):
        self.clipboard.clipCopy(self, nodes)
    def clipPaste(self):
        self.clipboard.clipPaste(self)

    def canAdd(self, paletteName):
        return false

#---Persistance (loading and saving)--------------------------------------------
    def assertFilename(self, filename):
        """ Utility function to strip and arrert the protocol from the uri """
        from Explorers.Explorer import splitURI
        prot, cat, res, uri = splitURI(filename)
        assert self.protocol==prot, 'Illegal protocol change'
        return res
            
    def load(self, mode='r'):
        """ Return item data from appropriate transport """
        return None
    def save(self, filename, data, mode='w'):
        """ Persist data on appropriate transport. Should handle renames """
        pass

class CachedNodeMixin:
    """ Only read from datasource when uninitialised or invalidated
        Not used yet
    """
    def __init__(self):
        self.valid = false
        self.cache = None

    def openList(self):
        if self.valid:
            return self.cache
        else:
            # define this method
            self.cache = self.openList_cache()

            self.valid = true
            return self.cache

class ContainerNode(ExplorerNode):
    protocol = 'fol'
    def __init__(self, name, imgIdx):
        ExplorerNode.__init__(self, name, '', None, imgIdx, None)
        self.entries = []
        self.vetoRequery = true
        self.vetoSort = true
    def destroy(self): pass
    def isFolderish(self): return true
    def createParentNode(self): return self
    def createChildNode(self, value): return value
    def openList(self): return self.entries
    def getTitle(self): return self.name
    def notifyBeginLabelEdit(self, event):
        event.Veto()

class RootNode(ContainerNode):
    protocol = 'root'
    def __init__(self, name, imgIdx=EditorHelper.imgBoaLogo):
        ContainerNode.__init__(self, name, imgIdx)
        
cat_section = 0
cat_option = 1
class CategoryNode(ExplorerNode):
    protocol = 'config'
    defName = 'config'
    defaultStruct = {}
    itemProtocol = ''
    def __init__(self, name, resourcepath, clipboard, config, parent, imgIdx = EditorHelper.imgFolder):
        ExplorerNode.__init__(self, name, resourcepath, clipboard,
              imgIdx, parent)
        self.config = config
        self.bold = true
        self.refresh()

    def destroy(self):
        pass

    def isFolderish(self):
        return true

    def getTitle(self):
        return self.name

    def refresh(self):
        try:
            self.entries = eval(self.config.get(self.resourcepath[cat_section],
                  self.resourcepath[cat_option]))
        except:
            message = sys.exc_info()[1]
            print 'invalid config entry for', \
                  self.resourcepath[cat_option], message
            self.entries = copy.copy(self.defaultStruct)
        else:
            # unscramble sensitive properties
            if type(self.entries) == type({}):
                for item in self.entries.keys():
                    if type(self.entries[item]) == type({}):
                        dict = self.entries[item]
                        for name in dict.keys():
                            if name in sensitive_properties:
                                dict[name] = scrm.scramble(dict[name])[2:]

    def openList(self):
        res = []
        entries = self.entries.keys()
        entries.sort()
        for entry in entries:
            node = self.createChildNode(entry, self.entries[entry])
            if node:
                res.append(node)
        return res

    def deleteItems(self, names):
        for name in names:
            try:
                del self.entries[name]
            except KeyError:
                wx.wxLogWarning('Could not find %s in %s for deletion'%(name, 
                      self.entries.keys()))
        self.updateConfig()

    illegal_substrs = ('://', '::', '/', '\\')
    def renameItem(self, name, newName):
        for ill_substr in self.illegal_substrs:
            if string.find(newName, ill_substr) != -1:
                raise Exception('Contains invalid string sequence or char: "%s"'%ill_substr)
        if self.entries.has_key(newName):
            raise Exception, 'Name exists'
        self.entries[newName] = self.entries[name]
        del self.entries[name]
        self.updateConfig()

    def newItem(self):
        name = Utils.getValidName(self.entries.keys(), self.defName)
        self.entries[name] = copy.copy(self.defaultStruct)
        self.updateConfig()
        return name

    def updateConfig(self):
        self.config.set(self.resourcepath[cat_section],
                  self.resourcepath[cat_option], pprint.pformat(self.entries))
        self.config.write(open(self.config.confFile, 'w'))

(wxID_CATNEW, wxID_CATINSPECT, wxID_CATDELETE, wxID_CATRENAME, wxID_CATRELOAD) \
 = Utils.wxNewIds(5)

class CategoryController(Controller):
    newBmp = 'Images/Shared/NewItem.bmp'
    inspectBmp = 'Images/Shared/Inspector.bmp'
    deleteBmp = 'Images/Shared/Delete.bmp'

    def __init__(self, editor, list, inspector, menuDefs = ()):
        Controller.__init__(self, editor)
        self.list = list
        self.menu = wx.wxMenu()
        self.inspector = inspector

        self.catMenuDef = ( (wxID_CATNEW, 'New', self.OnNewItem, self.newBmp),
                            (wxID_CATINSPECT, 'Inspect', self.OnInspectItem, self.inspectBmp),
                            (wxID_CATRELOAD, 'Reload', self.OnReloadItems, '-'),
                            (-1, '-', None, ''),
                            (wxID_CATDELETE, 'Delete', self.OnDeleteItems, self.deleteBmp),
                            (wxID_CATRENAME, 'Rename', self.OnRenameItem, '-') )

        self.setupMenu(self.menu, self.list, self.catMenuDef + menuDefs)
        self.toolbarMenus = [self.catMenuDef + menuDefs]

    def destroy(self):
        self.catMenuDef = ()
        self.toolbarMenus = ()
        self.menu.Destroy()

    def OnInspectItem(self, event):
        if self.list.node:
            # Create new companion for selection
            catItem = self.list.getSelection()
            if not catItem: return #zopeItem = self.list.node
            catComp = self.list.node.createCatCompanion(catItem)
            catComp.updateProps()

            # Select in inspector
            if self.inspector.pages.GetSelection() != 1:
                self.inspector.pages.SetSelection(1)
            self.inspector.selectObject(catComp, false)

    def OnNewItem(self, event):
        if self.list.node:
            name = self.list.node.newItem()
            self.list.refreshCurrent()
            self.list.selectItemNamed(name)
            # XXX Also select in inspector
            self.list.EditLabel(self.list.selected)

    def OnDeleteItems(self, event):
        if self.list.node:
            ms = self.list.getMultiSelection()
            names = self.getNamesForSelection(ms)
            self.list.node.deleteItems(names)
            self.list.refreshCurrent()

    def OnRenameItem(self, event):
        self.list.EditLabel(self.list.selected)

    def OnReloadItems(self, event):
        if self.list.node:
            self.list.refreshCurrent()

class BookmarksCatNode(CategoryNode):
    """ Stores folderish references to any transport protocol """
#    protocol = 'config.bookmark'
    defName = 'Bookmark'
    defaultStruct = Preferences.explorerFileSysRootDefault[1]
    refTree = true
    def __init__(self, clipboards, config, parent, catTransports, tree=None):
        CategoryNode.__init__(self, 'Bookmarks', ('explorer', 'bookmarks'),
              None, config, parent)
        self.catTransports = catTransports
        self.tree = tree
        self.treeitem = None
        self.clipboards = clipboards
        self.imgIdx = EditorHelper.imgFolderBookmark
        
    def createChildNode(self, name, value):
        from Explorers.Explorer import splitURI, getTransport
        prot, cat, res, uri = splitURI(value)
        node = getTransport(prot, cat, res, self.catTransports)
        if not node:
            return None
        if prot == 'file':
            node.imgIdx = EditorHelper.imgFSDrive
        elif prot == 'zope':
            node.imgIdx = EditorHelper.imgZopeConnection
        else:
            node.imgIdx = EditorHelper.imgNetDrive
            
        node.treename = name
        return node

    def getDefault(self):
        try:
            return self.entries[self.config.get(self.resourcepath[0],
                  'defaultbookmark')]
        except KeyError:
            return ''

    def add(self, respath):
        respath=str(respath)
        if respath[-1] in ('/', '\\'):
            name = path.splitext(path.basename(respath[:-1]))[0]
        else:
            name = path.splitext(path.basename(respath))[0]
        if self.entries.has_key(name):
            name = Utils.getValidName(self.entries.keys(), name)
        self.entries[name] = respath
        self.updateConfig()
        
        if self.tree and self.treeitem and self.treeitem.IsOk():
            if self.tree.IsExpanded(self.treeitem):
                self.tree.CollapseAndReset(self.treeitem)
                self.tree.Expand(self.treeitem)

    def createCatCompanion(self, catNode):
        comp = CategoryStringCompanion(catNode.treename, self)
        return comp

class SysPathNode(ExplorerNode):
    protocol = 'syspath'
    def __init__(self, clipboard, parent, bookmarks):
        ExplorerNode.__init__(self, 'sys.path', '', clipboard,
              EditorHelper.imgPathFolder, parent)
        self.bookmarks = bookmarks
        self.bold = true
        self.vetoSort = true
        #self.refresh()
        #self.imgIdx = EditorHelper.imgPathFolder

    def isFolderish(self):
        return true

    def createChildNode(self, shpth, pth):
        import FileExplorer
        return FileExplorer.PyFileNode(shpth, pth, self.clipboard,
              EditorHelper.imgPathFolder, self, self.bookmarks)

    def refresh(self):
        self.entries = []
        pythonDir = path.dirname(sys.executable)
        for pth in sys.path:
            pth = os.path.abspath(pth)
            shortPath = pth
            if pth:
                if pth[0:len(pythonDir)] == pythonDir:
                    shortPath = pth[len(pythonDir):]
                    if not shortPath:
                        shortPath = '<Python root>'
                self.entries.append( (shortPath, pth) )

    def openList(self):
        self.refresh()
        res = []
        for short, entry in self.entries:
            res.append(self.createChildNode(short, entry))
        return res

#---Companions------------------------------------------------------------------

from Companions.BaseCompanions import Companion
from PropEdit.PropertyEditors import StrConfPropEdit, EvalConfPropEdit, PasswdStrConfPropEdit
import RTTI
import types

class ExplorerCompanion(Companion):
    def __init__(self, name):
        Companion.__init__(self, name)
        # list of (name, value) tuples
        self.propItems = []
        self.designer = None
        self.control = None
        self.mutualDepProps = ()
    def constructor(self):
        return {}
    def extraConstrProps(self):
        return {}
    def events(self):
        return ()
    def getEvents(self):
        return ()
    def getPropEditor(self, prop):
        return None
    def getPropOptions(self, prop):
        return ()
    def getPropNames(self, prop):
        return ()
    def checkTriggers(self, name, oldValue, value):
        pass
    def persistProp(self, name, setterName, value):
        pass
    def propIsDefault(self, name, setterName):
        return true
    def persistedPropVal(self, name, setterName):
        return ''
    
    def getPropList(self):
        propLst = []
        for prop in self.propItems:
            propLst.append(RTTI.PropertyWrapper(prop[0], 'NameRoute',
                  self.GetProp, self.SetProp))
        return {'constructor':[], 'properties': propLst}

    def findProp(self, name):
        for idx in range(len(self.propItems)):
            if self.propItems[idx][0] == name:
                return self.propItems[idx], idx
        else:
            return None, -1

    def GetProp(self, name):
        return self.findProp(name)[0][1]

    def SetProp(self, name, value):
        prop, idx = self.findProp(name)
        if self.setPropHook(name, value, prop):
            self.propItems[idx] = (name, value) + prop[2:]
    
    def GetClass(self, dummy=None):
        # XXX Add protocol from transport
        return 'Explorer Item'
        
    def SetClass(self, value):
        pass

    def updateProps(self):
        self.propItems = self.getPropertyItems()

    def addProperty(self, name, value, tpe):
        pass

    def delProperty(self, name):
        pass

    def setPropHook(self, name, value, oldProp = None):
        """ Override to do something before a property is set """
        pass

    def getPropertyItems(self):
        """ Override this to read the properties of the object, and return it

            Should return a list of tuples where the first two items are the
            property name and value, the rest of the items may store other
            propery information. """
        return []

class CategoryCompanion(ExplorerCompanion):
    """ Inspectable objects, driven from config files """
    propMapping = {type('') : StrConfPropEdit,
                   'password' : PasswdStrConfPropEdit,
                   'default': EvalConfPropEdit}
    def __init__(self, name, catNode):
        ExplorerCompanion.__init__(self, name)
        self.catNode = catNode

    def getPropEditor(self, prop):
        if prop in sensitive_properties:
            return self.propMapping['password']
        else:
            return self.propMapping.get(type(self.GetProp(prop)), self.propMapping['default'])


class CategoryDictCompanion(CategoryCompanion):
    def getPropertyItems(self):
        return self.catNode.entries[self.name].items()

    def setPropHook(self, name, value, oldProp = None):
        # scramble sensitive properties before saving
        entry = self.catNode.entries[self.name]
        entry[name] = value

        scrams = []
        for entry in self.catNode.entries.values():
            for key in entry.keys():
                if key in sensitive_properties:
                    val = entry[key]
                    entry[key] = scrm.scramble(val)
                    scrams.append((entry, key, val))

        self.catNode.updateConfig()
        # unscramble sensitive properties
        for entry, key, val in scrams:
            entry[key] = val

        return true

class CategoryStringCompanion(CategoryCompanion):
    def getPropertyItems(self):
        return [ ('Item', self.catNode.entries[self.name]) ]

    def setPropHook(self, name, value, oldProp = None):
        self.catNode.entries[self.name] = value
        self.catNode.updateConfig()
