#-----------------------------------------------------------------------------
# Name:        ZipExplorer.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2001
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2003
# Licence:     GPL
#-----------------------------------------------------------------------------

print 'importing Explorers.ZipExplorer'
import string, os

from wxPython.wx import wxMenu, EVT_MENU, wxMessageBox, wxPlatform, wxNewId

import ExplorerNodes, FileExplorer
from Models import EditorModels, EditorHelper
from ExternalLib import zipfile

true = 1
false = 0

def isZip(file):
    return os.path.splitext(file)[1] == '.zip'

wxID_ZIPOPEN = wxNewId()

class ZipController(ExplorerNodes.Controller, ExplorerNodes.ClipboardControllerMix):
    def __init__(self, editor, list, inspector, controllers):
        ExplorerNodes.ClipboardControllerMix.__init__(self)
        ExplorerNodes.Controller.__init__(self, editor)

        self.list = list
        self.menu = wxMenu()

        self.setupMenu(self.menu, self.list,
              ( (wxID_ZIPOPEN, 'Open', self.OnOpenItems, '-'),
                (-1, '-', None, '') ) + self.clipMenuDef)

        mi = self.menu.GetMenuItems()
        for m in mi:
            if m.GetId() != ExplorerNodes.wxID_CLIPCOPY:
                m.Enable(false)
        self.toolbarMenus = [self.clipMenuDef]

    def destroy(self):
        ExplorerNodes.ClipboardControllerMix.destroy(self)
        self.toolbarMenus = ()
        self.menu.Destroy()


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

        imgIdx = isFolder and EditorHelper.imgFolder or \
              EditorHelper.imgTextModel
        if not isFolder:
            from Models import Controllers
            imgIdx = Controllers.identifyFile(name, localfs=false)[0].imgIdx
        zin = ZipItemNode(name, resourcepath and resourcepath+'/'+name or name, self.clipboard,
              isFolder, imgIdx, self, self.zipFileNode)
        zin.category = self.category
        return zin

    def splitBaseDir(self, file):
        if not file:
            return '', '', true
#        print 'splitBaseDir %s'%file
        segs = string.split(file, '/')
        # ends on /
        if segs[-1] == '':
            base = segs[-2]
            dir = string.join(segs[:-2], '/')
            isdir = 1
        else:
            base = segs[-1]
            dir = string.join(segs[:-1], '/')
            isdir = 0
        return base, dir, isdir

    def openList(self, resourcepath = None):
        if resourcepath is None: resourcepath = self.resourcepath
        res = []
        files = self.zipFileNode.getFiles(resourcepath)
        for file in files:
            base, dir, isdir = self.splitBaseDir(file)

            res.append(self.createChildNode(base, dir, self.zipFileNode.isDir(file)) )
        return res

    def copyToFS(self, fsFolderNode):
        fn = os.path.join(fsFolderNode.resourcepath, self.name)

        zf = zipfile.ZipFile(self.zipFileNode.resourcepath)

        if self.isFolderish():
            # XXX directories should be recursively copied or complete list
            # XXX should be build by ZipClip
            os.mkdir(fn)
        else:
            open(fn, 'wb').write(zf.read(self.resourcepath))
        zf.close()

    def load(self, mode='rb'):
#        try:
        zf = zipfile.ZipFile(self.zipFileNode.resourcepath, 'r')
        return zf.read(self.resourcepath)
##        except Exception, error:
##            raise ExplorerNodes.TransportLoadError(error, self.resourcepath)

    def save(self, filename, data, mode='wb'):
        raise ExplorerNodes.TransportSaveError(\
              'Saving not supported on Zip files (yet)', self.resourcepath)

    def getNodeFromPath(self, respath):
        base, dir, isdir = self.splitBaseDir(respath)
        return self.createChildNode(base, dir, self.zipFileNode.isDir(respath))

class ZipFileNode(ZipItemNode):
    protocol = 'zip'
    def __init__(self, name, resourcepath, clipboard, imgIdx, parent, bookmarks=None):
        if clipboard:
            zipClip = ZipExpClipboard(clipboard.globClip)
        else:
            zipClip = None
        ZipItemNode.__init__(self, name, resourcepath, zipClip, true,
            imgIdx, parent, self)
        self.allFiles = []
        self.allFileNames = []
        self.category = self.getTitle()+'://'

    def getURI(self):
        return '%s://%s' % (self.protocol, self.getTitle())

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


def uriSplitZip(filename, zipfile, zipentry):
    return 'zip', zipfile, zipentry, filename

def findZipExplorerNode(category, respath, transports):
    zf = ZipFileNode(os.path.basename(category), category, None, -1, None, None)
    zf.openList()
    return zf.getNodeFromPath(respath)

#-------------------------------------------------------------------------------
# Register zip files as a subtype of file explorers
FileExplorer.PyFileNode.subExplorerReg['file'].append(
      (ZipFileNode, isZip, EditorHelper.imgZipFileModel))
ExplorerNodes.register(ZipItemNode, clipboard=ZipExpClipboard,
      controller=ZipController)
ExplorerNodes.uriSplitReg[('zip', 3)] = uriSplitZip
ExplorerNodes.transportFindReg['zip'] = findZipExplorerNode