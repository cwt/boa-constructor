import ExplorerNodes, EditorModels
from ExternalLib import zipfile
import string, os
from wxPython.wx import wxMenu, EVT_MENU, wxMessageBox, wxPlatform

true = 1
false = 0

def isZip(file):
    return os.path.splitext(file)[1] == '.zip'
##(wxID_FSOPEN, wxID_FSTEST, wxID_FSNEW, wxID_FSNEWFOLDER, wxID_FSCVS ) \
## = map(lambda x: wxNewId(), range(5))

class ZipController(ExplorerNodes.Controller, ExplorerNodes.ClipboardControllerMix):
    def __init__(self, list):
        ExplorerNodes.ClipboardControllerMix.__init__(self)

        self.list = list
        self.menu = wxMenu()

        self.setupMenu(self.menu, self.list, self.clipMenuDef)
        
        mi = self.menu.GetMenuItems()
        for m in mi:
            if m.GetId() != ExplorerNodes.wxID_CLIPCOPY:
                m.Enable(false)
            

class ZipExpClipboard(ExplorerNodes.ExplorerClipboard): pass
##    def clipPaste_FileSysExpClipboard(self, node, nodes, mode):
##        for clipnode in nodes:
##            if mode == 'cut':
##                node.copyFromFS(clipnode)
###                node.moveFileFrom(clipnode)
##                self.clipNodes = []
##            elif mode == 'copy':
##                node.copyFromFS(clipnode)
###                node.copyFileFrom(clipnode)

class ZipItemNode(ExplorerNodes.ExplorerNode):
    protocol = 'zip'
    def __init__(self, name, resourcepath, clipboard, isFolder, imgIdx, parent, zipFileNode):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, clipboard, imgIdx, 
              parent)
        self.isFolder = isFolder
        self.zipFileNode = zipFileNode

    def isFolderish(self):
        return self.isFolder
#        return self.zipFileNode.isDir(self.resourcepath+'/'+self.name)

    def createChildNode(self, name, resourcepath, isFolder):
        print isFolder, EditorModels.FolderModel.imgIdx, EditorModels.TextModel.imgIdx
        
        imgIdx = isFolder and EditorModels.FolderModel.imgIdx or \
              EditorModels.TextModel.imgIdx
        print 'rp', resourcepath, 'base', resourcepath and resourcepath+'/'+name or name
        return ZipItemNode(name, resourcepath and resourcepath+'/'+name or name, self.clipboard,
              isFolder, imgIdx, self, self.zipFileNode)
        
    def openList(self, resourcepath = None):
        if resourcepath is None: resourcepath = self.resourcepath
        res = []
        files = self.zipFileNode.getFiles(resourcepath)
        for file in files:
#            print 'file:', file
            segs = string.split(file, '/')
            if segs[-1] == '': 
                base = segs[-2]
                dir = string.join(segs[:-2], '/')
            else:
                base = segs[-1]
                dir = string.join(segs[:-1], '/')
                
#            print 'base, dir', base, dir                
        
            res.append(self.createChildNode(base, dir, self.zipFileNode.isDir(file)) )
        return res
    
##    def copyFromFS(self, fsNode):
##        fn = os.path.basename(fsNode.resourcepath)
##        cmd = 'pscp -pw %s %s %s' %(self.properties['scp_pass'], 
##              fsNode.resourcepath,  self.remotePath(fn))
##        self.execSCP(cmd)

    def copyToFS(self, fsFolderNode):
        fn = os.path.join(fsFolderNode.resourcepath, self.name)

        zf = zipfile.ZipFile(self.zipFileNode.resourcepath)        
        print 'read', self.resourcepath, fn
        if self.isFolderish():
            # XXX directories should be recursively copied or complete list 
            # XXX should be build by ZipClip
            os.mkdir(fn)
        else:
            open(fn, 'w').write(zf.read(self.resourcepath))
        zf.close()
        
class ZipFileNode(ZipItemNode):
    protocol = 'zip'
    def __init__(self, name, resourcepath, clipboard, imgIdx, parent):
        if clipboard:
            zipClip = ZipExpClipboard(clipboard.globClip)
        else:
            zipClip = None
        ZipItemNode.__init__(self, name, resourcepath, zipClip, true, imgIdx, 
              parent, self)
        self.allFiles = []
        self.allFileNames = []

    def isFolderish(self):
        return true
    
    def isDir(self, path):
        return path[-1] == '/'
#        print 'isDir', path
#        return path in self.allFileNames

    def openList(self):
        zf = zipfile.ZipFile(self.resourcepath)        
        self.allFiles = zf.filelist
        zf.close()
        
        self.allFileNames = map(lambda fl: fl.filename, self.allFiles)
#        print self.allFileNames
        return ZipItemNode.openList(self, '')
        
    def getFiles(self, base):
        files = []
        for file in self.allFiles:
            if file.filename[-1] == '/':
                fn = file.filename[:-1]
            else:
                fn = file.filename
#            print 'getfiles', file.filename, base, os.path.dirname(fn)
            if os.path.dirname(fn) == base:
#            if file.filename[:len(base)] == base:
                files.append(file.filename)
#                files.append(file.filename[len(base):])
        return files
    

    
