import ExplorerNodes, EditorModels
from ExternalLib import zipfile
import string, os
from wxPython.wx import wxMenu, EVT_MENU, wxMessageBox, wxPlatform, wxNewId

true = 1
false = 0

def isZip(file):
    return os.path.splitext(file)[1] == '.zip'
##(wxID_FSOPEN, wxID_FSTEST, wxID_FSNEW, wxID_FSNEWFOLDER, wxID_FSCVS ) \
## = map(lambda x: wxNewId(), range(5))

wxID_ZIPOPEN = wxNewId()

class ZipController(ExplorerNodes.Controller, ExplorerNodes.ClipboardControllerMix):
    def __init__(self, editor, list):
        ExplorerNodes.ClipboardControllerMix.__init__(self)
        ExplorerNodes.Controller.__init__(self, editor)

        self.list = list
        self.menu = wxMenu()

        self.setupMenu(self.menu, self.list,
              ( (wxID_ZIPOPEN, 'Open', self.OnOpenItems, '-'),
#                (wxID_DAVINSPECT, 'Inspect', self.OnInspectItem, '-'),
                (-1, '-', None, '') ) + self.clipMenuDef)

        mi = self.menu.GetMenuItems()
        for m in mi:
            if m.GetId() != ExplorerNodes.wxID_CLIPCOPY:
                m.Enable(false)
        self.toolbarMenus = [self.clipMenuDef]

    def destroy(self):
        ExplorerNodes.ClipboardControllerMix.destroy(self)
        self.toolbarMenus = ()

    def __del__(self):
        pass#self.menu.Destroy()

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

        imgIdx = isFolder and EditorModels.FolderModel.imgIdx or \
              EditorModels.TextModel.imgIdx
        if not isFolder:
            imgIdx = EditorModels.identifyFile(name, localfs=false)[0].imgIdx
        return ZipItemNode(name, resourcepath and resourcepath+'/'+name or name, self.clipboard,
              isFolder, imgIdx, self, self.zipFileNode)

    def openList(self, resourcepath = None):
        if resourcepath is None: resourcepath = self.resourcepath
        res = []
        files = self.zipFileNode.getFiles(resourcepath)
        for file in files:
            segs = string.split(file, '/')
            if segs[-1] == '':
                base = segs[-2]
                dir = string.join(segs[:-2], '/')
            else:
                base = segs[-1]
                dir = string.join(segs[:-1], '/')

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
        if self.isFolderish():
            # XXX directories should be recursively copied or complete list
            # XXX should be build by ZipClip
            os.mkdir(fn)
        else:
            open(fn, 'w').write(zf.read(self.resourcepath))
        zf.close()

    def load(self):
        zf = zipfile.ZipFile(self.zipFileNode.resourcepath)
        return zf.read(self.resourcepath)

    def save(self, filename, data):
        pass


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

    def isDir(self, path = ''):
        if path:
            return path[-1] == '/'
        else:
            return false

    def openList(self):
        zf = zipfile.ZipFile(self.resourcepath)
        self.allFiles = zf.filelist
        zf.close()

        self.allFileNames = map(lambda fl: fl.filename, self.allFiles)
        return ZipItemNode.openList(self, '')

    def getFiles(self, base):
        files = []
        for file in self.allFiles:
            if file.filename[-1] == '/':
                fn = file.filename[:-1]
            else:
                fn = file.filename
            if os.path.dirname(fn) == base:
                files.append(file.filename)
        return files
