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
 wxID_FSBOOKMARK ) \
 = map(lambda x: wxNewId(), range(6))

class FileSysController(ExplorerNodes.Controller, ExplorerNodes.ClipboardControllerMix):
    def __init__(self, list, cvsController = None):
        ExplorerNodes.ClipboardControllerMix.__init__(self)

        self.list = list
        self.cvsController = cvsController
        self.menu = wxMenu()

        self.setupMenu(self.menu, self.list, (\
              (wxID_FSOPEN, 'Open', self.OnOpenFSItems),
#              (wxID_FSTEST, 'Test', self.OnTest),
              (-1, '-', None) ) +
              self.clipMenuDef +
            ( (-1, '-', None),
              (wxID_FSBOOKMARK, 'Bookmark', self.OnBookmarkFSItem),
        ))
        self.newMenu = wxMenu()
        self.setupMenu(self.newMenu, self.list, (\
              (wxID_FSNEWFOLDER, 'Folder', self.OnNewFolderFSItems),
        ))
        self.menu.AppendMenu(wxID_FSNEW, 'New', self.newMenu)

        if cvsController:
            self.menu.AppendMenu(wxID_FSCVS, 'CVS', cvsController.fileCVSMenu)
        
    def OnOpenFSItems(self, event): pass

    def OnNewFolderFSItems(self, event):
        if self.list.node:
            name = self.list.node.newFolder()
            self.list.refreshCurrent()
            self.list.selectItemNamed(name)
            self.list.EditLabel(self.list.selected)
    
    def OnBookmarkFSItem(self, event):
        print 'OnBookmarkFSItem'
        if self.list.node:
            nodes = self.getNodesForSelection(self.list.getMultiSelection())
            for node in nodes:
                if node.isFolderish():
                    print node.resourcepath
                    node.bookmarks.add(node.resourcepath)
            

    def OnTest(self, event):
        print self.list.node.clipboard.globClip.currentClipboard                

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

class PyFileNode(ExplorerNodes.ExplorerNode):
    protocol = 'file'
    def __init__(self, name, resourcepath, clipboard, imgIdx, parent, bookmarks, properties = {}):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, clipboard, imgIdx, 
              parent, properties or {})
        self.bookmarks = bookmarks
#        self.exts = map(lambda C: C.ext, EditorModels.modelReg.values())
        self.exts = EditorModels.extMap.keys() + ['.py']
        self.doCVS = true
        self.doZip = true
        self.entries = []

    def isFolderish(self): 
        return os.path.isdir(self.resourcepath) or ZipExplorer.isZip(self.resourcepath)
    
    def createParentNode(self):
        parent = os.path.abspath(os.path.join(self.resourcepath, '..'))
        return PyFileNode(os.path.basename(parent), parent, self.clipboard,
                  EditorModels.FolderModel.imgIdx, self, self.bookmarks)

    def createChildNode(self, file):
        filename = os.path.join(self.resourcepath, file)
        ext = os.path.splitext(file)[1]
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
        else:
            return '', None

    def openList(self):
        print self.resourcepath
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
        editor.openOrGotoModule(self.resourcepath)

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
        if not node.isFolderish():
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
            
class NonCheckPyFolderNode(PyFileNode):
    def isFolderish(self): 
        return true
