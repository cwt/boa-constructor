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
import string, time
from stat import *
import Preferences, Zope.LoginDialog
from Preferences import IS
from types import StringType
from Zope.ZopeFTP import ZopeFTP
from Zope import ImageViewer

# Zope explorer

ctrl_pnl = 'Control_Panel'
prods = 'Products'
acl_usr = 'acl_users'

[wxID_PFE, wxID_PFT, wxID_PFL] = map(lambda x: NewId(), range(3))

def isCVS(filename):
    file = path.basename(filename)
    return string.lower(file) == string.lower('cvs') and \
                      path.exists(path.join(filename, 'Entries')) and \
                      path.exists(path.join(filename, 'Repository')) and \
                      path.exists(path.join(filename, 'Root'))

class ExplorerNode:
    protocol = None
    def __init__(self, name, resourcepath, imgIdx, folderish, properties = {}):
        self.name = name
        self.resourcepath = resourcepath
        self.imgIdx = imgIdx
        self.folderish = folderish
        self.properties = properties
        
    def openList(self): pass
    def closeList(self): pass
    def isFolderish(self): return self.folderish
    def getTitle(self): return self.name

class ZopeItemNode(ExplorerNode):
    protocol = 'Zope'
    def __init__(self, name, resourcepath, imgIdx, zftp, zftpi, properties = {}):
        ExplorerNode.__init__(self, name, resourcepath, imgIdx, zftpi.isFolder(), 
          properties)
        self.zopeConn = zftp
        self.zopeObj = zftpi
         
    def openList(self):
        items = self.zopeConn.dir(self.zopeObj.whole_name())
        result = []
        for obj in items:
            if obj.name != '..':
                result.append(ZopeItemNode(obj.name, obj.path, -1, self.zopeConn,
                  obj, obj.isFolder()))
        return result

    def isFolderish(self): 
        return self.zopeObj.isFolder()

class ZopeConnectionNode(ZopeItemNode):
    protocol = 'Zope'
    def __init__(self, properties):
        zopeConn = ZopeFTP()
        zopeObj = zopeConn.folder_item(properties['name'], properties['path'])
        ZopeItemNode.__init__(self, zopeObj.name, zopeObj.path, -1, zopeConn, 
          zopeObj, properties)
        self.connected = false
        
    def openList(self):
        if not self.connected:
            if not string.strip(self.properties['username']):
                print 'dialog'
                ld = Zope.LoginDialog.create(None)
                ld.setup(self.properties['host'], self.properties['ftpport'],
                  self.properties['httpport'], self.properties['username'], 
                  self.properties['passwd'])
                if ld.ShowModal() == wxOK:
                    self.properties['host'], self.properties['ftpport'],\
                      self.properties['httpport'], self.properties['username'],\
                      self.properties['passwd'] = ld.getup()
                ld.Destroy()
            self.zopeConn.connect(self.properties['username'], 
              self.properties['passwd'], self.properties['host'],
              self.properties['ftpport'])
        return ZopeItemNode.openList(self)
    
    def closeList(self):
        if self.connected:
            self.zopeConn.disconnect
        self.connected = false
    
    def getTitle(self):
        return self.zopeObj.whole_name()
    
    
class PyFileNode(ExplorerNode):
    protocol = 'file'
    def __init__(self, name, resourcepath, imgIdx, folderish):
        ExplorerNode.__init__(self, name, resourcepath, imgIdx, folderish)
        self.exts = map(lambda C: C.ext, modelReg.values())
    def listing(self):
        files = os.listdir(self.resourcepath)
        files.sort()
        modules = []
        packages = []
        
        for file in files:
            filename = path.join(self.filepath, file)
            ext = path.splitext(file)[1]
#            if file == PackageModel.pckgIdnt: continue
            if (ext in self.exts) and path.isfile(filename):
                modules.append(PyFileNode(file, filename, 
                  identifyFile(filename)[0].imgIdx, false,
                  {'datetime': time.strftime('%a %b %d %H:%M:%S %Y', 
                     time.gmtime(os.stat(filename)[ST_MTIME]))}))
#                print os.stat(filename)  
            elif path.isdir(filename):
                if path.exists(path.join(filename, PackageModel.pckgIdnt)):
                    packages.append(PyFileNode(file, filename, 
                      PackageModel.imgIdx, true))
                elif isCVS(filename):
                    packages.append(PyFileNode(file, filename, 
                      CVSFolderModel.imgIdx, true))
                else:
                    packages.append(PyFileNode(file, filename, 
                      FolderModel.imgIdx, true))
        return modules, packages


def getSpecialFolderImg(ftpi, tree, item):
    if ftpi.name == '..': return 12
    elif ftpi.name == ctrl_pnl: return 13
    elif ftpi.name == prods and tree.GetItemText(item) == ctrl_pnl : return 14
    elif tree.GetItemText(item) == prods and \
      tree.GetItemText(tree.GetItemParent(item)) == ctrl_pnl: return 15
    return 12
        
class PackageFolderTree(wxTreeCtrl):
    def __init__(self, parent, images, root):
        wxTreeCtrl.__init__(self, parent, wxID_PFT)
        EVT_TREE_ITEM_EXPANDING(self, wxID_PFT, self.OnOpen)
        EVT_TREE_ITEM_COLLAPSED(self, wxID_PFT, self.OnClose)
        self.SetImageList(images)
        self.list = list
        
        conf = ConfigParser()
        if wxPlatform == '__WXMSW__': plat = 'msw'
        else: plat = 'gtk'
        
        print Preferences.pyPath
        conf.read(Preferences.pyPath+'/Explorer.'+plat+'.cfg')
        rootItem = self.AddRoot('', 21, -1, wxTreeItemData(''))

        newFS = self.AppendItem(rootItem, 'Filesystem', FolderModel.imgIdx, -1, 
          wxTreeItemData(''))
        self.SetItemBold(newFS, true)
        try:
            volumes = eval(conf.get('Explorer', 'Filesystem'))
        except Exception, message:
            print 'invalid config entry for Filesystem: list expected,', message
        else:
            for fs in volumes:
                newFSV = self.AppendItem(newFS, fs, FolderModel.imgIdx, -1, 
                  wxTreeItemData(fs))
                self.SetItemHasChildren(newFSV, true)

        newWS = self.AppendItem(rootItem, 'Workspace', FolderModel.imgIdx, -1, 
          wxTreeItemData(''))
        self.SetItemBold(newWS, true)
        try:
            spaces = eval(conf.get('Explorer', 'Workspaces'))
        except Exception, message:
            print 'invalid config entry for Workspaces: dict expected,', message
        else:
            wsref = {}
            for ws in spaces.keys():
                newS = self.AppendItem(newWS, ws, FolderModel.imgIdx, -1, 
                  wxTreeItemData(spaces[ws]))
                self.SetItemHasChildren(newS, true)
                wsref[ws] = newS 
        self.Expand(newWS)

        newP = self.AppendItem(rootItem, 'sys.path', FolderModel.imgIdx, -1, 
          wxTreeItemData(''))
        self.SetItemBold(newP, true)
        for pth in sys.path:
            if pth:
                abspth = path.abspath(pth)
                ni = self.AppendItem(newP, abspth, SysPathFolderModel.imgIdx, -1, 
                  wxTreeItemData(abspth))
                self.SetItemHasChildren(ni, true)

#        try:
        self.defaultWorkspaceItem = wsref[conf.get('Explorer', 'DefaultWorkspace')]
#        self.SelectItem(wsref[conf.get('Explorer', 'DefaultWorkspace')])
#        except Exception, message: print message

        newWS = self.AppendItem(rootItem, 'Zope', FolderModel.imgIdx, -1, 
          wxTreeItemData(''))
        self.SetItemBold(newWS, true)
        try:
            zopes = eval(conf.get('Explorer', 'Zope'))
        except Exception, message:
            print 'invalid config entry for Workspaces: dict expected,', message
        else:
            wsref = {}
            for ws in zopes.keys():
                newS = self.AppendItem(newWS, ws, 20, -1, 
                  wxTreeItemData(ZopeConnectionNode(zopes[ws])))
                self.SetItemHasChildren(newS, true)
                wsref[ws] = newS 
        self.Expand(newWS)

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

    def getChildNamed(self, node, name):
        cookie = 0
        child, cookie = self.GetFirstChild(node, cookie)
        while child.IsOk() and self.GetItemText(child) != name:
            child, cookie = self.GetNextChild(node, cookie)
        return child

    def OnOpen(self, event):
        item = event.GetItem()
        data = self.GetPyData(item)
        hasFolders = 0
        if type(data) == StringType:
            filepath = data
            if filepath:  
                self.DeleteChildren(item)
                files = os.listdir(filepath)
                files.sort()
                hasFolders = 0
                for file in files:
                    filename = path.join(filepath, file)
                    if path.isdir(filename):
                        if path.exists(path.join(filename, '__init__.py')):
                            model = PackageModel
                        elif isCVS(filename):
                            model = CVSFolderModel
                        else:
                            model = FolderModel
                        hasFolders = 1
          
                        new = self.AppendItem(item, file, model.imgIdx, -1,
                                          wxTreeItemData(filename))
                        self.SetItemHasChildren(new, true)
            else:
                hasFolders = true
        else:
            if issubclass(data.__class__, ZopeItemNode):
                lst = data.openList()
                hasFolders = false
                for itm in lst:
                    if itm.isFolderish():
                        hasFolders = true
                        imgIdx = getSpecialFolderImg(itm, self, item)
                        new = self.AppendItem(item, itm.name, imgIdx, -1,
                                          wxTreeItemData(itm))
                        self.SetItemHasChildren(new, true)
                        
            
        self.SetItemHasChildren(item, hasFolders)
              
    def OnClose(self, event):
        item = event.GetItem()
        data = self.GetPyData(item)
        if type(data) == StringType: pass
        elif issubclass(data.__class__, ZopeItemNode):
            data.closeList()
            self.DeleteChildren(item)

#            if dir(new_obj):
#                self.SetItemHasChildren(new_item, wx.TRUE)

 

class PackageFolderList(wxListCtrl):
    def __init__(self, parent, filepath):
        wxListCtrl.__init__(self, parent, wxID_PFL, style = wxLC_LIST)
#        self.InsertColumn(0, 'Name', wxLIST_FORMAT_LEFT, 150) 
#        self.InsertColumn(1, 'Rev.', wxLIST_FORMAT_LEFT, 50)
#        self.InsertColumn(2, 'Date', wxLIST_FORMAT_LEFT, 150)
#        self.InsertColumn(3, 'Options', wxLIST_FORMAT_LEFT, 50)
        self.filepath = filepath
        self.exts = map(lambda C: C.ext, modelReg.values())
        self.viewing = 'files'

        EVT_LIST_ITEM_SELECTED(self, wxID_PFL, self.OnItemSelect)
        EVT_LIST_ITEM_DESELECTED(self, wxID_PFL, self.OnItemDeselect)
        self.selected = -1
        
        self.list = []

    def refreshPath(self, images, filepath = ''):
        self.viewing = 'files'
        self.DeleteAllItems()
        self.SetSingleStyle(wxLC_LIST, true)
        self.SetSingleStyle(wxLC_REPORT, false)
#        self.SetWindowStyleFlag(wxLC_LIST)
        self.SetImageList(images, wxIMAGE_LIST_SMALL)
        if filepath: self.filepath = filepath 
        files = os.listdir(filepath)
        
        files.sort()
        packages = []
        modules = []
        for file in files:
            filename = path.join(self.filepath, file)
            ext = path.splitext(file)[1]
#            if file == PackageModel.pckgIdnt: continue
            if (ext in self.exts) and path.isfile(filename):
                modules.append((file, identifyFile(filename)[0], 
                  time.strftime('%a %b %d %H:%M:%S %Y', 
                  time.gmtime(os.stat(filename)[ST_MTIME]))))
#                print os.stat(filename)  
            elif path.isdir(filename):
                if path.exists(path.join(filename, PackageModel.pckgIdnt)):
                    packages.append((file, PackageModel))
                elif isCVS(filename):
                    packages.append((file, CVSFolderModel))
                else:
                    packages.append((file, FolderModel))

        packages.sort()
        for name, model in packages:
            self.InsertImageStringItem(self.GetItemCount(), name, model.imgIdx)

        modules.sort()
        for name, model, date in modules:
            self.InsertImageStringItem(self.GetItemCount(), name, model.imgIdx)
            self.SetStringItem(self.GetItemCount()-1, 2, date)

    def refreshItems(self, images, explNode, tree):
        self.viewing = 'other'
        self.DeleteAllItems()
        self.SetImageList(images, wxIMAGE_LIST_SMALL)
        item = tree.GetSelection()
        self.items = explNode.openList()
        for itm in self.items:
            imgIdx = getSpecialFolderImg(itm, tree, item)

            if itm.isFolderish(): imgIdx = getSpecialFolderImg(itm, tree, item)
            elif itm.name == acl_usr: imgIdx = 16
            elif string.lower(os.path.splitext(itm.name)[1]) in ImageViewer.imgs.keys(): imgIdx = 18
            elif itm.zopeObj.isSysObj(): imgIdx = 19
            else: imgIdx = 17

            self.InsertImageStringItem(self.GetItemCount(), itm.name, imgIdx)

    def refreshTree(self, images, items, parentName = ''):
        self.DeleteAllItems()
        self.SetSingleStyle(wxLC_LIST, true)
        self.SetSingleStyle(wxLC_REPORT, false)
#        self.SetWindowStyleFlag(wxLC_LIST)
        self.SetImageList(images, wxIMAGE_LIST_SMALL)
        self.filepath = ''

        if parentName and parentName == 'sys.path':
            mod = SysPathFolderModel
        else:
            mod = FolderModel
        for item in items:
            self.InsertImageStringItem(self.GetItemCount(), item, 
              mod.imgIdx)

    def refreshCVS(self, images, filepath, editor):
        self.viewing = 'cvs'
#        print 'refresh CVS' 

        self.DeleteAllItems()

        self.SetSingleStyle(wxLC_REPORT, true)
        self.SetSingleStyle(wxLC_LIST, false)

#        self.SetWindowStyleFlag(wxLC_REPORT)

        self.InsertColumn(0, 'Name', wxLIST_FORMAT_LEFT, 150) 
        self.InsertColumn(1, 'Rev.', wxLIST_FORMAT_LEFT, 50)
        self.InsertColumn(2, 'Date', wxLIST_FORMAT_LEFT, 150)
        self.InsertColumn(3, 'Options', wxLIST_FORMAT_LEFT, 50)
        self.SetImageList(images, wxIMAGE_LIST_SMALL)
        self.filepath = filepath
        self.CVSModel = CVSFolderModel('', filepath, editor, filepath)

#        self.InsertStringItem(0, 'Root', -1)
#        self.SetStringItem(0, 1, self.CVSModel.root)
#        self.InsertStringItem(0, 'Repository', -1)
#        self.SetStringItem(1, 1, self.CVSModel.repository)

        for entry in self.CVSModel.entries:
#            print 'refresh CVS', entry 
            self.InsertImageStringItem(self.GetItemCount(), entry.name, 
              entry.imgIdx)
            self.SetStringItem(self.GetItemCount()-1, 1, entry.revision)
            self.SetStringItem(self.GetItemCount()-1, 2, entry.timestamp)
            self.SetStringItem(self.GetItemCount()-1, 3, entry.options)

    def OnItemSelect(self, event):
        self.selected = event.m_itemIndex

    def OnItemDeselect(self, event):
        self.selected = -1
           
class PackageFolderExplorer(wxSplitterWindow):
    def __init__(self, parent, modimages, root, editor):
        wxSplitterWindow.__init__(self, parent, wxID_PFE, style = wxNO_3D|wxSP_3D)#style = wxSP_3D) #wxSP_NOBORDER)

        self.editor = editor
        self.list = PackageFolderList(self, root)
        self.modimages = modimages
        self.cvsimages = wxImageList(16, 16)
        self.cvsimages.Add(IS.load('Images/CVSPics/File.bmp'))
        self.cvsimages.Add(IS.load('Images/CVSPics/BinaryFile.bmp'))
        self.cvsimages.Add(IS.load('Images/CVSPics/ModifiedFile.bmp'))
        self.cvsimages.Add(IS.load('Images/CVSPics/ModifiedBinaryFile.bmp'))
        self.cvsimages.Add(IS.load('Images/CVSPics/MissingFile.bmp'))
        self.cvsimages.Add(IS.load('Images/CVSPics/Dir.bmp'))
        EVT_LEFT_DCLICK(self.list, self.OnOpen)
        self.tree = PackageFolderTree(self, modimages, root)
        EVT_TREE_SEL_CHANGED(self, wxID_PFT, self.OnSelect)

        self.SplitVertically(self.tree, self.list, 200)
        self.list.SetFocus()
    
    def destroy(self):
        del self.editor

    def OnSelect(self, event):
        item = event.GetItem()
        data = self.tree.GetPyData(item)
        if type(data) == StringType:
            filepath = data
            if filepath:
                title = filepath 
                if isCVS(filepath):
                    self.list.refreshCVS(self.cvsimages, filepath, self.editor)
                else:
                    self.list.refreshPath(self.modimages, filepath)
            else:
                title = 'Section'
                self.list.refreshTree(self.modimages, self.tree.getChildrenNames(),
                  self.tree.GetItemText(item))
        else:
            title = 'Zope' 
            if issubclass(data.__class__, ZopeItemNode):
                title = 'Zope - %s' % data.getTitle()
                self.list.refreshItems(self.modimages, data, self.tree)
    
        self.editor.SetTitle('Editor - Explorer - %s' %(title))

    def OnOpen(self, event):
        if self.list.selected != -1:
            if self.list.viewing == 'files':
                
                name = self.list.GetItemText(self.list.selected)
                file = path.join(self.list.filepath, name)
                if path.isdir(file) or not (self.list.filepath):
                    self.tree.Expand(self.tree.GetSelection())
                    chid = self.tree.getChildNamed(self.tree.GetSelection(), name)
    #                if chid >= 0:
                    self.tree.SelectItem(chid)
                else: 
                    print 'expl', name, file
                    self.editor.openOrGotoModule(file)
            elif self.list.viewing == 'cvs':
                prnt = self.tree.GetItemParent(self.tree.GetSelection())
                dir = self.tree.getChildNamed(prnt, 
                  self.list.GetItemText(self.list.selected))
                self.tree.Expand(dir)
                subdir = self.tree.getChildNamed(dir, 'CVS')
                self.tree.SelectItem(subdir)
            else:
                item = self.list.items[self.list.selected]
                if item.isFolderish():
                    tItm = self.tree.GetSelection()
                    if not self.tree.IsExpanded(tItm):
                        self.tree.Expand(tItm)
                    chid = self.tree.getChildNamed(self.tree.GetSelection(), 
                      item.name)
    #                if chid >= 0:
                    self.tree.SelectItem(chid)
                else: 
                    self.editor.openOrGotoZopeDocument(item.zopeConn, item.zopeObj)






              
              
              
              
              
              
     