import ExplorerNodes
from wxPython.wx import *
import EditorModels, Utils, Preferences
import string, os, time, stat
import CVSExplorer, ZipExplorer

class FileSysCatNode(ExplorerNodes.CategoryNode):
#    protocol = 'config.file'
    defName = Preferences.explorerFileSysRootDefault[0]
    defaultStruct = Preferences.explorerFileSysRootDefault[1]
    def __init__(self, clipboard, config, parent, bookmarks):
        ExplorerNodes.CategoryNode.__init__(self, 'Filesystem', ('explorer', 'filesystem'),
              clipboard, config, parent)
        self.bookmarks = bookmarks

    def createParentNode(self):
        return self

    def createCatCompanion(self, catNode):
        comp = ExplorerNodes.CategoryStringCompanion(catNode.treename, self)
        return comp

    def createChildNode(self, entry, value):
        return NonCheckPyFolderNode(entry, value, self.clipboard, 
              EditorModels.imgFSDrive, self, self.bookmarks)

##    def newItem(self):
##        name = ExplorerNodes.CategoryNode.newItem()
##        self.entries[name] = copy.copy(self.defaultStruct)
##        self.updateConfig()
##        return name

    def renameItem(self, name, newName):
        if self.entries.has_key(newName):
            raise Exception, 'Name exists'
        self.entries[newName] = newName
        del self.entries[name]
        self.updateConfig()

        
(wxID_FSOPEN, wxID_FSTEST, wxID_FSNEW, wxID_FSNEWFOLDER, wxID_FSCVS,
 wxID_FSBOOKMARK, wxID_FSFILTERBOAMODULES, wxID_FSFILTERALLMODULES, 
 wxID_FSFILTER, wxID_FSFILTERINTMODULES 
) = map(lambda x: wxNewId(), range(10))

class FileSysController(ExplorerNodes.Controller, ExplorerNodes.ClipboardControllerMix):
    bookmarkBmp = 'Images/Shared/Bookmark.bmp'
    findBmp = 'Images/Shared/Find.bmp'
    def __init__(self, editor, list, cvsController = None):
        ExplorerNodes.Controller.__init__(self, editor)
        ExplorerNodes.ClipboardControllerMix.__init__(self)
        self.editor = editor

        self.list = list
        self.cvsController = cvsController
        self.menu = wxMenu()
        
        self.fileMenuDef = (
              (wxID_FSOPEN, 'Open', self.OnOpenFSItems, '-'),
#              (wxID_FSTEST, 'Test', self.OnTest),
              (-1, '-', None, '') ) +\
              self.clipMenuDef +\
            ( (-1, '-', None, ''),
              (wxID_FSBOOKMARK, 'Find', self.OnFindFSItem, self.findBmp),
              (wxID_FSBOOKMARK, 'Bookmark', self.OnBookmarkFSItem, self.bookmarkBmp),
        )        
        self.setupMenu(self.menu, self.list, self.fileMenuDef)

        self.fileFilterMenuDef = (
              (wxID_FSFILTERBOAMODULES, '+Boa files', self.OnFilterFSItemBoa, '-'),
              (wxID_FSFILTERINTMODULES, '+Internal files', self.OnFilterFSItemInt, '-'),
              (wxID_FSFILTERALLMODULES, '+All files', self.OnFilterFSItemAll, '-'),
        )
        self.fileFilterMenu = wxMenu()
        self.setupMenu(self.fileFilterMenu, self.list, self.fileFilterMenuDef)

        # Check default option
        self.fileFilterMenu.Check(wxID_FSFILTERBOAMODULES, true)

        self.menu.AppendMenu(wxID_FSFILTER, 'Filter', self.fileFilterMenu)
        
        self.newMenu = wxMenu()
        self.setupMenu(self.newMenu, self.list, (
              (wxID_FSNEWFOLDER, 'Folder', self.OnNewFolderFSItems, '-'),
        ))
        self.menu.AppendMenu(wxID_FSNEW, 'New', self.newMenu)

        if cvsController:
            self.menu.AppendMenu(wxID_FSCVS, 'CVS', cvsController.fileCVSMenu)

        self.toolbarMenus = [self.fileMenuDef]
        
    def OnOpenFSItems(self, event):
        if self.list.node:
            nodes = self.getNodesForSelection(self.list.getMultiSelection())
            for node in nodes:
                if not node.isFolderish():
                    self.editor.openOrGotoModule(node.resourcepath)

    def OnNewFolderFSItems(self, event):
        if self.list.node:
            name = self.list.node.newFolder()
            self.list.refreshCurrent()
            self.list.selectItemNamed(name)
            self.list.EditLabel(self.list.selected)
    
    def OnBookmarkFSItem(self, event):
        if self.list.node:
            nodes = self.getNodesForSelection(self.list.getMultiSelection())
            for node in nodes:
                if node.isFolderish():
                    node.bookmarks.add(node.resourcepath)

    def OnTest(self, event):
        print self.list.node.clipboard.globClip.currentClipboard                

    def OnFilterFSItemBoa(self, event):
        self.groupCheckMenu(self.fileFilterMenu, self.fileFilterMenuDef, 
              wxID_FSFILTERBOAMODULES, true)
        self.list.node.setFilter('BoaFiles')
        self.list.refreshCurrent()

    def OnFilterFSItemAll(self, event):
        self.groupCheckMenu(self.fileFilterMenu, self.fileFilterMenuDef, 
              wxID_FSFILTERALLMODULES, true)
        self.list.node.setFilter('AllFiles')
        self.list.refreshCurrent()

    def OnFilterFSItemInt(self, event):
        self.groupCheckMenu(self.fileFilterMenu, self.fileFilterMenuDef, 
              wxID_FSFILTERINTMODULES, true)
        self.list.node.setFilter('BoaInternalFiles')
        self.list.refreshCurrent()
    
    def OnFindFSItem(self, event):
        import Search
        dlg = wxTextEntryDialog(self.list, 'Enter text:', 
          'Find in files', '')
        try:
            if dlg.ShowModal() == wxID_OK:
                res = Search.findInFiles(self.list, self.list.node.resourcepath, 
                      dlg.GetValue(), filemask = self.list.node.getFilterExts(), 
                      progressMsg = 'Search files...', joiner = os.sep)
                nd = self.list.node
                self.list.node = ResultsFolderNode('Results', nd.resourcepath, nd.clipboard, -1, nd, nd.bookmarks)
                #self.list.node.results = map(lambda r: r[1], res)
                self.list.node.results = res
                self.list.node.lastSearch = dlg.GetValue()
                self.list.refreshCurrent()
        finally:
            dlg.Destroy()
        
class FileSysExpClipboard(ExplorerNodes.ExplorerClipboard):
    def clipPaste_FileSysExpClipboard(self, node, nodes, mode): 
        for clipnode in nodes:
            if mode == 'cut':
                node.moveFileFrom(clipnode)
                self.clipNodes = []
            elif mode == 'copy':
                node.copyFileFrom(clipnode)

    def clipPaste_ZopeEClip(self, node, nodes, mode):
        # XXX Pasting a cut from Zope does not delete the cut items from Zope
        for file in nodes:
            file.zopeConn.download(file.resourcepath+'/'+file.name, 
                  os.path.join(node.resourcepath, file.name))

    def clipPaste_SSHExpClipboard(self, node, nodes, mode):
        for sshNode in nodes:
            if mode == 'cut':
                sshNode.copyToFS(node)
                #self.clipNodes = []
            elif mode == 'copy':
                sshNode.copyToFS(node)

    def clipPaste_ZipExpClipboard(self, node, nodes, mode):
        for zipNode in nodes:
            zipNode.copyToFS(node)

    def clipPaste_FTPExpClipboard(self, node, nodes, mode):
        # XXX Pasting a cut from FTP does not delete the cut items from FTP
        for file in nodes:
#            print file.resourcepath+'/'+file.name, os.path.join(node.resourcepath, file.name)
            file.ftpConn.download(file.resourcepath, 
                  os.path.join(node.resourcepath, file.name))

class PyFileNode(ExplorerNodes.ExplorerNode):
    protocol = 'file'
    filter = 'BoaFiles'
    lastSearch = ''
    def __init__(self, name, resourcepath, clipboard, imgIdx, parent, bookmarks, properties = {}):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, clipboard, imgIdx, 
              parent, properties or {})
        self.bookmarks = bookmarks
#        self.exts = map(lambda C: C.ext, EditorModels.modelReg.values())
        self.exts = EditorModels.extMap.keys() + ['.py']
        self.doCVS = true
        self.doZip = true
        self.entries = []

    def isDir(self):
        return os.path.isdir(self.resourcepath)
        
    def isFolderish(self): 
        return self.isDir() or ZipExplorer.isZip(self.resourcepath)
    
    def createParentNode(self):
        parent = os.path.abspath(os.path.join(self.resourcepath, '..'))
        if parent[-2:] == '..':
            parent = parent[:-2]
        return PyFileNode(os.path.basename(parent), parent, self.clipboard,
                  EditorModels.FolderModel.imgIdx, self, self.bookmarks)

    def createChildNode(self, file, filename = ''):
        if not filename:
            filename = os.path.join(self.resourcepath, file)
            
        ext = os.path.splitext(filename)[1]
        if (ext in self.exts) and os.path.isfile(filename):
            if self.doZip and ZipExplorer.isZip(filename):
                return 'fol', ZipExplorer.ZipFileNode(file, filename, 
                      self.clipboard, EditorModels.ZipFileModel.imgIdx, self)
            else:
                return 'mod', PyFileNode(file, filename, self.clipboard,
                  EditorModels.identifyFile(filename)[0].imgIdx, self, self.bookmarks,
                  {'datetime': time.strftime('%a %b %d %H:%M:%S %Y', 
                               time.gmtime(os.stat(filename)[stat.ST_MTIME]))})
        elif os.path.isdir(filename):
            if os.path.exists(os.path.join(filename, EditorModels.PackageModel.pckgIdnt)):
                return 'fol', PyFileNode(file, filename, self.clipboard,
                  EditorModels.PackageModel.imgIdx, self, self.bookmarks)
            elif self.doCVS and CVSExplorer.isCVS(filename):
                return 'fol', CVSExplorer.FSCVSFolderNode(file, filename, 
                      self.clipboard, self)
            else:
                return 'fol', PyFileNode(file, filename, self.clipboard,
                      EditorModels.FolderModel.imgIdx, self, self.bookmarks)
        elif self.filter == 'AllFiles':
            return 'mod', PyFileNode(file, filename, self.clipboard,
              EditorModels.UnknownFileModel.imgIdx, self, self.bookmarks)
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

        self.entries = entries['fol'] + entries['mod']
        return self.entries

    def open(self, editor):
        apps = editor.getAppModules()
        for app in apps:
            mods = app.absModulesPaths()
            if self.resourcepath in mods:
                editor.openOrGotoModule(self.resourcepath, app)
                return
        return editor.openOrGotoModule(self.resourcepath)

    def deleteItems(self, names):
        for name in names:
            path = os.path.join(self.resourcepath, name)
            if os.path.isdir(path):
                os.rmdir(path)
            else:
                os.remove(path)
        
    def renameItem(self, name, newName):
        oldfile = os.path.join(self.resourcepath, name)
        newfile = os.path.join(self.resourcepath, newName)
        os.rename(oldfile, newfile)
    
    def newFolder(self):
        name = Utils.getValidName(map(lambda n: n.name, self.entries), 'Folder')
        os.mkdir(os.path.join(self.resourcepath, name))
        return name

    def copyFileFrom(self, node):
        import shutil
        if not node.isDir():
            shutil.copy(node.resourcepath, self.resourcepath)
        else:
            shutil.copytree(node.resourcepath, os.path.join(self.resourcepath, node.name))
            
    def moveFileFrom(self, node):
        # Moving into directory being moved should not be allowed
        sp = os.path.normpath(node.resourcepath)
        dp = os.path.normpath(self.resourcepath)
        if dp[:len(sp)] == sp:
            raise Exception('Cannot move into itself')

        self.copyFileFrom(node)
        if not node.isFolderish():
            os.remove(node.resourcepath)
        else:
            import shutil
            shutil.rmtree(node.resourcepath)
        
    def setFilter(self, filter):
        self.__class__.filter = filter
        
    def getFilterExts(self):
        if self.filter == 'BoaFiles':
            return self.exts + ['.py']
        if self.filter == 'BoaInsternalFiles':
            return self.exts
        if self.filter == 'AllFiles':
            return ('.*',)
        
class ResultsFolderNode(PyFileNode):
    results = []
    def openList(self):
        self.parentOpensChildren = true
        self.results.sort()
        self.results.reverse()
        entries = []
        
        for occrs, filename in self.results:
            tp, node = self.createChildNode('(%d) %s'%(occrs, filename), 
                  os.path.join(self.resourcepath, filename))
            if node:
                entries.append(node)

        self.entries = entries
        return self.entries
    
    def openParent(self, editor):
        editor.explorer.tree.SelectItem(editor.explorer.tree.GetSelection())
        return true
    
    def open(self, node, editor):
        mod = node.open(editor)
        if mod.views.has_key('Source'):
            mod.views['Source'].doFind(self.lastSearch)
            mod.views['Source'].doNextMatch()
            
    def getTitle(self):
        return 'Find results for %s in %s' % (self.lastSearch, self.resourcepath)
        
class NonCheckPyFolderNode(PyFileNode):
    def isFolderish(self): 
        return true
