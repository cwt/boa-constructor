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

from ExternalLib.ConfigParser import ConfigParser
from os import path
import os, sys
import string, time, ftplib
from stat import *
import Preferences, Zope.LoginDialog, Utils
from Preferences import IS, wxFileDialog
from types import StringType
from Zope.ZopeFTP import ZopeFTP
from Zope import ImageViewer
from Companions.ZopeCompanions import ZopeConnection, ZopeCompanion
#import FileDlg

# Zope explorer

ctrl_pnl = 'Control_Panel'
prods = 'Products'
acl_usr = 'acl_users'

(wxID_PFE, wxID_PFT, wxID_PFL, wxID_ZOPEUP, wxID_ZOPECUT, wxID_ZOPECOPY, 
 wxID_ZOPEPASTE, wxID_ZOPEDELETE, wxID_ZOPERENAME, wxID_ZOPEEXPORT, 
 wxID_ZOPEIMPORT, wxID_ZOPEINSPECT) = map(lambda x: wxNewId(), range(12))

def isCVS(filename):
    file = path.basename(filename)
    return string.lower(file) == string.lower('cvs') and \
                      path.exists(path.join(filename, 'Entries')) and \
                      path.exists(path.join(filename, 'Repository')) and \
                      path.exists(path.join(filename, 'Root'))

class ExplorerClipboard:
    def clipCut(self, node, nodes): 
        pass
    def clipCopy(self, node, nodes): 
        pass
    def clipPaste(self, node): 
        pass
    
class ZopeEClip(ExplorerClipboard):
    def __init__(self, props):
        self.clipRef = ''

        self.props = props
        self.zc = ZopeConnection()
        self.zc.connect(props['host'], props['httpport'], 
                        props['username'], props['passwd'])
    def callAndSetRef(self, objpath, method, nodes):
        mime, res = self.zc.call(objpath, method, ids = nodes)
#        print mime, res
        self.clipRef = string.split(mime.get('Set-Cookie'), '"')[1]
    def clipCut(self, node, nodes):
        self.callAndSetRef(node.zopeObj.whole_name(), 'manage_cutObjects', nodes)
    def clipCopy(self, node, nodes):
        self.callAndSetRef(node.zopeObj.whole_name(), 'manage_copyObjects', nodes)
    def clipPaste(self, node):
        mime, res = self.zc.call(node.zopeObj.whole_name(), 
              'manage_pasteObjects', cb_copy_data = self.clipRef)
#        print mime, res
        
        
class ExplorerNode:
    protocol = None
    images = None
    def __init__(self, name, resourcepath, clipboard, imgIdx, parent = None, properties = None):
        self.name = name
        self.resourcepath = resourcepath
        self.imgIdx = imgIdx
        if properties is None: properties = {}
        self.properties = properties
        self.clipboard = clipboard
        self.parent = parent
        self.treename = ''
        self.bold = false
        self.vetoRequery = false
        self.upImgIdx = imgFolderUp
                
    def createChildNode(self, value): pass
    def openList(self): pass
    def closeList(self): pass
    def isFolderish(self): return false
    def getTitle(self):
        if self.resourcepath: return self.resourcepath
        else: return self.name

    def open(self, editor): pass
    
#---Methods on sub items--------------------------------------------------------
    def deleteItems(self, names): pass
    def renameItem(self, name, newName): pass

#---Clipboard methods-----------------------------------------------------------
    def clipCut(self, nodes):
        self.clipboard.clipCut(self, nodes)
    def clipCopy(self, nodes):
        self.clipboard.clipCopy(self, nodes)
    def clipPaste(self):
        self.clipboard.clipPaste(self)

class RootNode(ExplorerNode):
    def __init__(self, name):
        ExplorerNode.__init__(self, name, '', None, imgBoaLogo, None)
        self.entries = []
        self.vetoRequery = true
    def isFolderish(self): return true
    def createChildNode(self, value): return value    
    def openList(self): return self.entries
    def getTitle(self): return 'Boa Constructor'
    
class CategoryNode(ExplorerNode):
    protocol = 'config'
    def __init__(self, name, resourcepath, clipboard, config, parent, imgIdx = FolderModel.imgIdx):
        ExplorerNode.__init__(self, name, resourcepath, clipboard, 
              imgIdx, parent)
        self.config = config
        self.bold = true
        self.refresh()
    
    def isFolderish(self):
        return true

    def getTitle(self):
        return self.name
        
    def refresh(self):
        try:
            self.entries = eval(self.config.get(self.resourcepath[0], 
                  self.resourcepath[1]))
        except Exception, message:
            print 'invalid config entry for', self.resourcepath[1], message
            self.entries = []

class FileSysCatNode(CategoryNode):
    def __init__(self, clipboard, config, parent):
        CategoryNode.__init__(self, 'Filesystem', ('explorer', 'filesystem'),
              clipboard, config, parent)

    def createParentNode(self):
        return self

    def createChildNode(self, entry):
        return NonCheckPyFolderNode(entry, entry, self.clipboard, imgFSDrive, self)
        
    def openList(self):
        res = []
        for entry in self.entries:
            res.append(self.createChildNode(entry))
        return res

class BookmarksCatNode(CategoryNode):
    def __init__(self, clipboard, config, parent):
        CategoryNode.__init__(self, 'Bookmarks', ('explorer', 'bookmarks'),
              clipboard, config, parent)

    def createChildNode(self, name, value):
        return PyFileNode(name, value, self.clipboard, imgFolderBookmark, self)
        
    def openList(self):
        res = []
        for entry in self.entries.keys():
            res.append(self.createChildNode(entry, self.entries[entry]))
        return res

    def getDefault(self):
        try:
            return self.entries[self.config.get(self.resourcepath[0], 
                  'defaultbookmark')]
        except KeyError:
            return ''

class SysPathNode(ExplorerNode):
    protocol = 'syspath'
    def __init__(self, clipboard, parent):
        ExplorerNode.__init__(self, 'sys.path', '', clipboard, 
              FolderModel.imgIdx, parent)
        self.bold = true
        self.refresh()
    
    def isFolderish(self):
        return true

    def createChildNode(self, shpth, pth):
        return PyFileNode(shpth, pth, self.clipboard, SysPathFolderModel.imgIdx, self)
        
    def refresh(self):
        self.entries = []
        pythonDir = path.dirname(sys.executable)
        for pth in sys.path:
            pth = path.abspath(pth)
            shortPath = pth
            if pth:
                if pth[0:len(pythonDir)] == pythonDir:
                    shortPath = pth[len(pythonDir):]
                    if not shortPath:
                        shortPath = '<Python root>'
                self.entries.append( (shortPath, pth) )
                
    def openList(self):
        res = []
        for short, entry in self.entries:
            res.append(self.createChildNode(short, entry))
        return res

class ZopeCatNode(CategoryNode):
    def __init__(self, config, parent):
        CategoryNode.__init__(self, 'Zope', ('explorer', 'zope'), None, config, 
              parent)

    def createChildNode(self, name, props):
        clipboard = ZopeEClip(props)
        return ZopeConnectionNode(name, props, clipboard, self)
        
    def openList(self):
        res = []
        for entry in self.entries.keys():
            res.append(self.createChildNode(entry, self.entries[entry]))
        return res

##    def getDefault(self):
##        try:
##            return self.wsref[self.wsref.index(self.config.get(self.resourcepath[0], 
##                  'defaultbookmark'))]
##        except ValueError:
##            return None

    
class ZopeItemNode(ExplorerNode):
    protocol = 'zope'
    def __init__(self, name, resourcepath, clipboard, imgIdx, parent, zftp, zftpi, root, properties):
        ExplorerNode.__init__(self, name, resourcepath, clipboard, imgIdx, 
              parent, properties)
        self.zopeConn = zftp
        self.zopeObj = zftpi
        self.root = root
        self.cache = []

    def createChildNode(self, obj, root):
        def getZopeFolderImg(node):
            if node.name == '..': return imgZopeFolder
            elif node.name == ctrl_pnl: return imgZopeControlPanel
            elif node.name == prods and node.parent.name == ctrl_pnl : 
                return imgZopeProductFolder
            elif node.parent.name == prods and \
                  node.parent.parent.name == ctrl_pnl: 
                return imgZopeInstalledProduct
            return imgZopeFolder

        if obj.name != '..':
            itm = ZopeItemNode(obj.name, obj.path, self.clipboard, -1, 
                  self, self.zopeConn, obj, root, self.properties)

            if itm.isFolderish(): imgIdx = getZopeFolderImg(itm)
            elif itm.name == acl_usr: imgIdx = imgZopeUserFolder
            elif string.lower(os.path.splitext(itm.name)[1]) in ImageViewer.imgs.keys(): 
                imgIdx = imgZopeImage
            elif itm.zopeObj.isSysObj(): imgIdx = imgZopeSystemObj
            else: imgIdx = imgZopeDTMLDoc
            
            itm.imgIdx = imgIdx

            return itm
        else:
            return None
        
    def openList(self, root = None):
        try:
            wxBeginBusyCursor()
            try:
                items = self.zopeConn.dir(self.zopeObj.whole_name())
            finally:
                wxEndBusyCursor()
        except ftplib.error_perm, resp:
            Utils.ShowMessage(None, 'Zope Error', resp)
            raise
            
        if not root: root = self.root
        self.cache = {}
        result = []
        for obj in items:
            z = self.createChildNode(obj, self.root)
            if z:
                result.append(z)
                self.cache[obj.name] = z
        
        return result
    
    def isFolderish(self): 
        return self.zopeObj.isFolder()

    def getTitle(self):
        return 'Zope - '+self.zopeObj.whole_name()

    def open(self, editor):
        editor.openOrGotoZopeDocument(self.zopeConn, self.zopeObj)

    def deleteItems(self, names):
        mime, res = self.clipboard.zc.call(self.zopeObj.whole_name(), 
              'manage_delObjects', ids = [names])

    def renameItem(self, name, newName):
        mime, res = self.clipboard.zc.call(self.zopeObj.whole_name(), 
              'manage_renameObject', id = name, new_id = newName)

    def exportObj(self):
        mime, res = self.clipboard.zc.call(self.zopeObj.whole_name(), 
              'manage_exportObject', download = 1)
        return res

    def listImportFiles(self):
        if self.properties.has_key('localpath'):
            return filter(lambda f: path.splitext(f)[1] == '.zexp', os.listdir(\
                path.join(self.properties['localpath'], 'import')))
        else:
            return []

    def importObj(self, name):
        mime, res = self.clipboard.zc.call(self.zopeObj.whole_name(), 
              'manage_importObject', file = name)

class ZopeConnectionNode(ZopeItemNode):
    protocol = 'zope'
    def __init__(self, name, properties, clipboard, parent):
        zopeConn = ZopeFTP()
        zopeObj = zopeConn.folder_item(properties['name'], properties['path'])
        ZopeItemNode.__init__(self, zopeObj.name, zopeObj.path, clipboard, 
            imgZopeConnection, parent, zopeConn, zopeObj, self, properties)
        self.connected = false
        self.treename = name
        
    def openList(self):
        if not self.connected:
            if not string.strip(self.properties['username']):
                ld = Zope.LoginDialog.create(None)
                try:
                    ld.setup(self.properties['host'], self.properties['ftpport'],
                      self.properties['httpport'], self.properties['username'], 
                      self.properties['passwd'])
                    if ld.ShowModal() == wxOK:
                        self.properties['host'], self.properties['ftpport'],\
                          self.properties['httpport'], self.properties['username'],\
                          self.properties['passwd'] = ld.getup()
                finally:
                    ld.Destroy()
            self.zopeConn.connect(self.properties['username'], 
              self.properties['passwd'], self.properties['host'],
              self.properties['ftpport'])
        return ZopeItemNode.openList(self, self)
    
    def closeList(self):
        if self.connected:
            self.zopeConn.disconnect
        self.connected = false
        
class PyFileNode(ExplorerNode):
    protocol = 'file'
    def __init__(self, name, resourcepath, clipboard, imgIdx, parent, properties = {}):
        ExplorerNode.__init__(self, name, resourcepath, clipboard, imgIdx, 
              parent, properties or {})
        self.exts = map(lambda C: C.ext, modelReg.values())
        self.doCVS = true

    def isFolderish(self): 
        return path.isdir(self.resourcepath)
    
    def createParentNode(self):
        parent = path.abspath(path.join(self.resourcepath, '..'))
        return PyFileNode(path.basename(parent), parent, self.clipboard,
                  FolderModel.imgIdx, self)

    def createChildNode(self, file):
        filename = path.join(self.resourcepath, file)
        ext = path.splitext(file)[1]
        if (ext in self.exts) and path.isfile(filename):
            return 'mod', PyFileNode(file, filename, self.clipboard,
                  identifyFile(filename)[0].imgIdx, self,
                  {'datetime': time.strftime('%a %b %d %H:%M:%S %Y', 
                               time.gmtime(os.stat(filename)[ST_MTIME]))})
        elif path.isdir(filename):
            if path.exists(path.join(filename, PackageModel.pckgIdnt)):
                return 'fol', PyFileNode(file, filename, self.clipboard,
                  PackageModel.imgIdx, self)
            elif self.doCVS and isCVS(filename):
                return 'fol', FSCVSFolderNode(file, filename, self.clipboard, self)
            else:
                return 'fol', PyFileNode(file, filename, self.clipboard,
                  FolderModel.imgIdx, self)
        else:
            return '', None

    def openList(self):
        files = os.listdir(self.resourcepath)
        files.sort()
        entries = {'mod': [], 'fol': []}
        
        for file in files:
            tp, node = self.createChildNode(file)
            if node:
                entries[tp].append(node)

        return entries['fol'] + entries['mod']

    def open(self, editor):
        editor.openOrGotoModule(self.resourcepath)

class NonCheckPyFolderNode(PyFileNode):
    def isFolderish(self): 
        return true

class CVSFolderNode(ExplorerNode):
    protocol = 'cvs'
    def __init__(self, entriesLine, resourcepath, dirpos, parent):
        if entriesLine:
            name, self.revision, self.timestamp, self.options, self.tagdate = \
              string.split(entriesLine[2:], '/')
        else:
            name=self.revision=self.timestamp=self.options=self.tagdate = ''
    
        ExplorerNode.__init__(self, name, resourcepath, None, 5, parent)
        
        self.dirpos = dirpos

##    def text(self):
##        return string.join(('D', self.name, self.revision, self.timestamp, self.options, self.tagdate), '/')

    def isFolderish(self): 
        return false

    def createParentNode(self):
        parent = path.abspath(path.join(self.resourcepath, '..'))
        return PyFileNode(path.basename(parent), parent, self.clipboard,
                  FolderModel.imgIdx, self)

    def open(self, editor):
        # XXX Rather hacky...
        tree = editor.explorer.tree
        par = tree.GetItemParent(tree.GetSelection())
        chd = tree.getChildNamed(par, self.name)
        if not tree.IsExpanded(chd):
            tree.Expand(chd)
        cvsChd = tree.getChildNamed(chd, 'CVS')
        tree.SelectItem(cvsChd)
#        editor.openOrGotoModule(self.resourcepath)

class CVSFileNode(ExplorerNode):
    protocol = 'cvs'
    def __init__(self, entriesLine, resourcepath, parent):
        if entriesLine:
            name , self.revision, self.timestamp, self.options, self.tagdate = \
              string.split(string.strip(entriesLine)[1:], '/')
        else:
            name=self.revision=self.timestamp=self.options=self=tagdate = ''

        ExplorerNode.__init__(self, name, resourcepath, None, -1, parent)

        self.missing = false
        self.imgIdx = 0
        if self.timestamp:
            filename = path.abspath(path.join(self.resourcepath, '..', name))
            if path.exists(filename):
                filets = strftime('%a %b %d %H:%M:%S %Y', gmtime(os.stat(filename)[ST_MTIME]))
                self.modified = self.timestamp != filets
            else:
                self.missing = true
                self.modified = false
        else:
            self.modified = false
        
        self.imgIdx = self.options == '-kb' or self.modified << 1 or self.missing << 2

    def isFolderish(self): 
        return false

    def open(self, editor):
        # XXX Rather hacky...
        tree = editor.explorer.tree
        tree.SelectItem(tree.GetItemParent(tree.GetSelection()))
        editor.explorer.list.selectItemNamed(self.name)
        
##    def text(self):
##        return string.join(('D', self.name, self.revision, self.timestamp, self.options, self.tagdate), '/')
    
class FSCVSFolderNode(ExplorerNode):
    protocol = 'cvs'
    def __init__(self, name, resourcepath, clipboard, parent):
        ExplorerNode.__init__(self, name, resourcepath, clipboard, 
              CVSFolderModel.imgIdx, parent)
        self.dirpos = 0
        self.upImgIdx = 6

    def isFolderish(self): 
        return true

    def createParentNode(self):
        if self.parent:
            return self.parent
        else:
            parent = path.abspath(path.join(self.resourcepath, path.join('..', 'CVS')))
            return FSCVSFolderNode(path.basename(parent), parent, self.clipboard,
                      CVSFolderModel.imgIdx, self)

    def createChildNode(self, txtEntry):
        if not txtEntry or txtEntry == 'D':
            return None
            # XXX Maybe add all dirs?   
        elif txtEntry[0] == 'D':
            return CVSFolderNode(txtEntry, self.resourcepath, self.dirpos, self)
            self.dirpos = self.dirpos + 1
        else:
            try:
                return CVSFileNode(txtEntry, self.resourcepath, self)
            except IOError:
                return None

    def openList(self):
        def rdFl(self, name):
            return string.strip(open(path.join(self.resourcepath, name)).read())

        self.root = rdFl(self, 'Root')#string.strip(open(path.join(self.resourcepath, 'Root')).read())
        self.repository = rdFl(self, 'Repository')#string.strip(open(path.join(self.resourcepath, 'Repository')).read())
        self.entries = []

        res = []
        self.dirpos = 0
        txtEntries = open(path.join(self.resourcepath, 'Entries')).readlines()
        for txtEntry in txtEntries:
            cvsNode = self.createChildNode(string.strip(txtEntry))
            if cvsNode: res.append(cvsNode)
        
        self.entries = res
        return res

    def open(self, editor):
        editor.openOrGotoModule(self.resourcepath)

        
class PackageFolderTree(wxTreeCtrl):
    def __init__(self, parent, images, root):
        wxTreeCtrl.__init__(self, parent, wxID_PFT)
        EVT_TREE_ITEM_EXPANDING(self, wxID_PFT, self.OnOpen)
        EVT_TREE_ITEM_EXPANDED(self, wxID_PFT, self.OnOpened)
        EVT_TREE_ITEM_COLLAPSED(self, wxID_PFT, self.OnClose)
        self.SetImageList(images)
        self.list = list
        
        conf = ConfigParser()
        if wxPlatform == '__WXMSW__': plat = 'msw'
        else: plat = 'gtk'
        
        conf.read(Preferences.pyPath+'/Explorer.'+plat+'.cfg')

        self.boaRoot = RootNode('Boa Constructor')
        rootItem = self.AddRoot('', imgBoaLogo, -1, wxTreeItemData(self.boaRoot))
        self.boaRoot.entries = [FileSysCatNode(None, conf, None), 
                                BookmarksCatNode(None, conf, None),
                                ZopeCatNode(conf, None),
                                SysPathNode(None, None)]

        self.SetItemHasChildren(rootItem, true)
        self.Expand(rootItem)
        
        ws = self.getChildNamed(rootItem, 'Bookmarks')
        self.Expand(ws)

#        ws = self.getChildNamed(ws, 'Bookmarks')
        self.defaultBookmarkItem = self.getChildNamed(ws, self.boaRoot.entries[1].getDefault())
    
    def addCatTreeItem(self, treeNode, explNode):
        newCat = self.AppendItem(treeNode, explNode.name, FolderModel.imgIdx, -1, 
              wxTreeItemData(explNode))
        
        self.SetItemBold(newCat, true)
        self.SetItemHasChildren(newCat, true)

        return newCat

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
##        hasFolders = 0
##        if type(data) == StringType:
##            print 'open string'
##        else:
        hasFolders = true
        if data:
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

        self.SetItemHasChildren(item, hasFolders)
              
    def OnClose(self, event):
        item = event.GetItem()
        data = self.GetPyData(item)
        if type(data) == StringType: pass
        elif issubclass(data.__class__, ZopeItemNode):
            data.closeList()
            self.DeleteChildren(item)

class PackageFolderList(wxListCtrl):
    def __init__(self, parent, filepath, pos = wxDefaultPosition, size = wxDefaultSize):
        wxListCtrl.__init__(self, parent, wxID_PFL, pos = pos, size = size, style = wxLC_LIST | wxLC_EDIT_LABELS)
#        self.InsertColumn(0, 'Name', wxLIST_FORMAT_LEFT, 150) 
#        self.InsertColumn(1, 'Rev.', wxLIST_FORMAT_LEFT, 50)
#        self.InsertColumn(2, 'Date', wxLIST_FORMAT_LEFT, 150)
#        self.InsertColumn(3, 'Options', wxLIST_FORMAT_LEFT, 50)
        self.filepath = filepath
        self.exts = map(lambda C: C.ext, modelReg.values())
        self.idxOffset = 0
#        self.viewing = 'files'

        self.zopeMenu = wxMenu()
        self.menu = None
        self.node = None
        
        self.zopeMenu.Append(wxID_ZOPEINSPECT, 'Inspect')
        self.zopeMenu.AppendSeparator()
        self.zopeMenu.Append(wxID_ZOPECUT, 'Cut')
        self.zopeMenu.Append(wxID_ZOPECOPY, 'Copy')
        self.zopeMenu.Append(wxID_ZOPEPASTE, 'Paste')
        self.zopeMenu.AppendSeparator()
        self.zopeMenu.Append(wxID_ZOPEDELETE, 'Delete')
        self.zopeMenu.Append(wxID_ZOPERENAME, 'Rename')
        self.zopeMenu.AppendSeparator()
        self.zopeMenu.Append(wxID_ZOPEEXPORT, 'Export')
        self.zopeMenu.Append(wxID_ZOPEIMPORT, 'Import')

        EVT_LIST_ITEM_SELECTED(self, wxID_PFL, self.OnItemSelect)
        EVT_LIST_ITEM_DESELECTED(self, wxID_PFL, self.OnItemDeselect)
                
        EVT_RIGHT_DOWN(self, self.OnRightDown)
            # for wxMSW
#            EVT_COMMAND_RIGHT_CLICK(self, -1, self.OnRightClick)
            # for wxGTK
        EVT_RIGHT_UP(self, self.OnRightUp)        
        self.selected = -1
        
        self.list = []
    
    def selectItemNamed(self, name):
        for idx in range(self.GetItemCount()):
            item = self.GetItem(idx)
            if item.GetText() == name:
                item.SetState(wxLIST_STATE_FOCUSED | wxLIST_STATE_SELECTED)
                self.SetItem(item)
                
##    def refreshPath(self, images, filepath = ''):
###        self.viewing = 'files'
##        self.DeleteAllItems()
##        self.SetSingleStyle(wxLC_LIST, true)
##        self.SetSingleStyle(wxLC_REPORT, false)
###        self.SetWindowStyleFlag(wxLC_LIST)
##        self.SetImageList(images, wxIMAGE_LIST_SMALL)
##        if filepath: self.filepath = filepath 
##        files = os.listdir(filepath)
##        
##        files.sort()
##        packages = []
##        modules = []
##        for file in files:
##            filename = path.join(self.filepath, file)
##            ext = path.splitext(file)[1]
###            if file == PackageModel.pckgIdnt: continue
##            if (ext in self.exts) and path.isfile(filename):
##                modules.append((file, identifyFile(filename)[0], 
##                  time.strftime('%a %b %d %H:%M:%S %Y', 
##                  time.gmtime(os.stat(filename)[ST_MTIME]))))
###                print os.stat(filename)  
##            elif path.isdir(filename):
##                if path.exists(path.join(filename, PackageModel.pckgIdnt)):
##                    packages.append((file, PackageModel))
##                elif isCVS(filename):
##                    packages.append((file, CVSFolderModel))
##                else:
##                    packages.append((file, FolderModel))
##
##        self.InsertImageStringItem(self.GetItemCount(), '..', FolderModel.imgIdx)
##        packages.sort()
##        for name, model in packages:
##            self.InsertImageStringItem(self.GetItemCount(), name, model.imgIdx)
##
##        modules.sort()
##                
##        for name, model, date in modules:
##            self.InsertImageStringItem(self.GetItemCount(), name, model.imgIdx)
##            self.SetStringItem(self.GetItemCount()-1, 2, date)
##
##        self.items = packages + modules
    
    def getSelection(self):
        if self.selected >= self.idxOffset:
            return self.items[self.selected-self.idxOffset]    
        else:
            return None

    def getMultiSelection(self):
        pass
        
    def refreshItems(self, images, explNode):
        """ Display ExplorerNode items """
        self.selected = -1
        
        # XXX This still needs to be made generic along with toolbar actions
        if isinstance(explNode, ZopeItemNode):
            self.menu = self.zopeMenu
        else:
            self.menu = None

        self.node = explNode
        self.DeleteAllItems()
        self.SetImageList(images, wxIMAGE_LIST_SMALL)
        self.items = explNode.openList()
        self.InsertImageStringItem(self.GetItemCount(), '..', explNode.upImgIdx)
        self.idxOffset = 1
        for itm in self.items:
            self.InsertImageStringItem(self.GetItemCount(), 
                  itm.treename or itm.name, itm.imgIdx)

        self.filepath = explNode.resourcepath

    def OnItemSelect(self, event):
        self.selected = event.m_itemIndex

    def OnItemDeselect(self, event):
        self.selected = -1
#        event.Veto()
    
    def OnRightDown(self, event):
        self.popx = event.GetX()
        self.popy = event.GetY()

    def OnRightUp(self, event):
        if self.menu:
            self.PopupMenu(self.menu, wxPoint(self.popx, self.popy))

class PackageFolderExplorer(wxSplitterWindow):
    def __init__(self, parent, modimages, root, editor):
        wxSplitterWindow.__init__(self, parent, wxID_PFE, style = wxNO_3D|wxSP_3D)#style = wxSP_3D) #wxSP_NOBORDER)

        self.editor = editor
        self.list = PackageFolderList(self, root)#, editor.palette)
        self.modimages = modimages
        self.cvsimages = wxImageList(16, 16)
        self.cvsimages.Add(IS.load('Images/CVSPics/File.bmp'))
        self.cvsimages.Add(IS.load('Images/CVSPics/BinaryFile.bmp'))
        self.cvsimages.Add(IS.load('Images/CVSPics/ModifiedFile.bmp'))
        self.cvsimages.Add(IS.load('Images/CVSPics/ModifiedBinaryFile.bmp'))
        self.cvsimages.Add(IS.load('Images/CVSPics/MissingFile.bmp'))
        self.cvsimages.Add(IS.load('Images/CVSPics/Dir.bmp'))
        self.cvsimages.Add(IS.load('Images/Modules/FolderUp_s.bmp'))
        
        FSCVSFolderNode.images = self.cvsimages
        
        EVT_LEFT_DCLICK(self.list, self.OnOpen)
        EVT_KEY_UP(self.list, self.OnKeyPressed)
        EVT_LEFT_DOWN(self.list, self.OnListClick)
        
        self.tree = PackageFolderTree(self, modimages, root)
        EVT_TREE_SEL_CHANGING(self, wxID_PFT, self.OnSelecting)
        EVT_TREE_SEL_CHANGED(self, wxID_PFT, self.OnSelect)
        
        EVT_MENU(self.list, wxID_ZOPECUT, self.OnCutZopeItem)
        EVT_MENU(self.list, wxID_ZOPECOPY, self.OnCopyZopeItem)
        EVT_MENU(self.list, wxID_ZOPEPASTE, self.OnPasteZopeItem)
        EVT_MENU(self.list, wxID_ZOPEDELETE, self.OnDeleteZopeItem)
        EVT_MENU(self.list, wxID_ZOPERENAME, self.OnRenameZopeItem)
        EVT_MENU(self.list, wxID_ZOPEEXPORT, self.OnExportZopeItem)
        EVT_MENU(self.list, wxID_ZOPEIMPORT, self.OnImportZopeItem)
        EVT_MENU(self.list, wxID_ZOPEINSPECT, self.OnInspectZopeItem)

        EVT_LIST_BEGIN_LABEL_EDIT(self, wxID_PFL, self.OnBeginLabelEdit)
        EVT_LIST_END_LABEL_EDIT(self, wxID_PFL, self.OnEndLabelEdit)
        
        self.clipRef = ''

        self.SplitVertically(self.tree, self.list, 200)
        self.list.SetFocus()
    
    def destroy(self):
        del self.editor

    def selectTreeItem(self, item):
        data = self.tree.GetPyData(item)
        title = self.tree.GetItemText(item)
        if data:
            imgs = data.images
            if not imgs: imgs = self.modimages
            title = data.getTitle()
            self.list.refreshItems(imgs, data)
    
        self.editor.SetTitle('Editor - Explorer - %s' % title)

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
            if name == '..':
                self.tree.SelectItem(self.tree.GetItemParent(self.tree.GetSelection()))
            else:
                item = self.list.items[self.list.selected-1]
                if item.isFolderish():
                    tItm = self.tree.GetSelection()
                    if not self.tree.IsExpanded(tItm):
                        self.tree.Expand(tItm)
                    chid = self.tree.getChildNamed(self.tree.GetSelection(), 
                      item.name)
                    self.tree.SelectItem(chid)
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
        # Create Zope object in folder
        if isinstance(self.list.node, ZopeItemNode) and palette.componentSB.selection:
            node = self.tree.GetSelection()
            zopeItem = self.tree.GetPyData(node)

            props = zopeItem.root.properties
            name, desc, Compn = palette.componentSB.selection
            cmp = Compn(Utils.getValidName(zopeItem.cache.keys(), name),
                zopeItem.zopeObj.whole_name(), props.get('localpath', ''))
            cmp.connect(props['host'], props['httpport'], 
                        props['username'], props['passwd'])
            cmp.create()
    
            self.selectTreeItem(node)
                
            palette.componentSB.selectNone()
            self.list.selectItemNamed(cmp.name)
        else:    
            event.Skip()

    def OnRenameZopeItem(self, event):
        self.list.EditLabel(self.list.selected)

    def getSelectedZopeItem(self):
        if isinstance(self.list.node, ZopeItemNode) and self.list.selected != -1: 
            node = self.tree.GetSelection()
            zopeItem = self.tree.GetPyData(node)
            selItemName = self.list.GetItem(self.list.selected).GetText()
            return node, zopeItem, selItemName
        else:
            return None, None, None

    def OnCutZopeItem(self, event):
        node, zopeItem, selItemName = self.getSelectedZopeItem()
        if zopeItem:
            zopeItem.clipCut(selItemName)

    def OnCopyZopeItem(self, event):
        node, zopeItem, selItemName = self.getSelectedZopeItem()
        if zopeItem:
            zopeItem.clipCopy(selItemName)

    def OnPasteZopeItem(self, event):
#        node, zopeItem, selItemName = self.getSelectedZopeItem()
        zopeItem = self.list.node#getSelection()
        if zopeItem:
            zopeItem.clipPaste()
            self.selectTreeItem(self.tree.GetSelection())

    def OnExportZopeItem(self, event):
        node, zopeItem, selItemName = self.getSelectedZopeItem()
        zopeItem = self.list.getSelection()
        if zopeItem:
            zexp = zopeItem.exportObj()

            dlg = wxFileDialog(self, 'Save as...', '.', zopeItem.name+'.zexp', '', 
              wxSAVE | wxOVERWRITE_PROMPT)
            try:
                if dlg.ShowModal() == wxID_OK:
                    open(dlg.GetPath(), 'wb').write(zexp)
            finally: 
                dlg.Destroy()
            
    def OnImportZopeItem(self, event):
        fls = self.list.node.listImportFiles()
        
        if fls:
            dlg = wxSingleChoiceDialog(self, 'Choose the file to import', 'Import object', fls)
            try:
                if dlg.ShowModal() == wxID_OK:
                    zexp = dlg.GetStringSelection()
                else:
                    return
            finally:
                dlg.Destroy()
        else:
            dlg = wxTextEntryDialog(self, 'Enter file to import', 'Import object', '.zexp')
            try:
                if dlg.ShowModal() == wxID_OK:
                    zexp = dlg.GetValue()
                else:
                    return
            finally:
                dlg.Destroy()

        self.list.node.importObj(zexp)
        self.selectTreeItem(self.tree.GetSelection())
    
    def OnDeleteZopeItem(self, event):
        selItem = self.list.getSelection()
        if selItem:
            self.list.node.deleteItems(selItem.name)
            self.selectTreeItem(self.tree.GetSelection())
        
    def OnBeginLabelEdit(self, event):
        self.oldLabelVal = event.GetText()

    def OnEndLabelEdit(self, event):
        newText = event.GetText()
#        event.Veto()
        if newText != self.oldLabelVal and isinstance(self.list.node, ZopeItemNode): 
            self.list.node.renameItem(self.oldLabelVal, newText)
            self.selectTreeItem(self.tree.GetSelection())
                
    def OnInspectZopeItem(self, event):
        if isinstance(self.list.node, ZopeItemNode):
            # Create new companion for selection
            zopeItem = self.list.getSelection()
            if not zopeItem: zopeItem = self.list.node
            props = zopeItem.root.properties
            zc = ZopeCompanion(zopeItem.name, zopeItem.resourcepath+'/'+zopeItem.name)
            zc.connect(props['host'], props['httpport'], 
                       props['username'], props['passwd'])
            zc.updateZopeProps()
    
            # Select in inspector
            insp = self.editor.inspector
            if insp.pages.GetSelection() != 1:
                insp.pages.SetSelection(1)
            insp.selectObject(zc, false)
     