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
import os, zipfile
from StringIO import StringIO

from wxPython.wx import wxMenu, EVT_MENU, wxMessageBox, wxPlatform, wxNewId

import ExplorerNodes, FileExplorer
from Models import EditorModels, EditorHelper
#from ExternalLib import zipfile

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
            [ (wxID_ZIPOPEN, 'Open', self.OnOpenItems, '-'),
              (-1, '-', None, '') ] + self.clipMenuDef)

        #mi = self.menu.GetMenuItems()
        #for m in mi:
        #    if m.GetId() != ExplorerNodes.wxID_CLIPCOPY:
        #        m.Enable(false)
        self.toolbarMenus = [self.clipMenuDef]

    def destroy(self):
        ExplorerNodes.ClipboardControllerMix.destroy(self)
        self.toolbarMenus = []
        self.menu.Destroy()


class ZipExpClipboard(ExplorerNodes.ExplorerClipboard):
    def clipPaste_FileSysExpClipboard(self, node, nodes, mode):
        for clipnode in nodes:
            if mode == 'cut':
                node.copyFromFS(clipnode)
                self.clipNodes = []
            elif mode == 'copy':
                node.copyFromFS(clipnode)

class ZipItemNode(ExplorerNodes.ExplorerNode):
    protocol = 'zip'
    def __init__(self, name, resourcepath, clipboard, isFolder, imgIdx, parent, zipFileNode):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, clipboard, imgIdx,
              parent)
        self.isFolder = isFolder
        self.zipFileNode = zipFileNode
        self.lineSep = None # meaning binary

    def isFolderish(self):
        return self.isFolder

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
        segs = file.split('/')
        # ends on /
        if segs[-1] == '':
            base = segs[-2]
            dir = '/'.join(segs[:-2])
            isdir = 1
        else:
            base = segs[-1]
            dir = '/'.join(segs[:-1])
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

    def getArcDir(self):
        if self.isFolderish():
            return self.resourcepath
        else:
            return os.path.dirname(self.resourcepath)
    
    def walkFS(self, (files, excludes), dirname, names):
        for name in names:
            if name not in excludes:
                filename = os.path.join(dirname, name)
                if os.path.isfile(filename):
                    files.append(filename)
                    
    def copyFromFS(self, fsNode, fn=''):
        if not fn:
            fn = os.path.basename(fsNode.resourcepath)
        
        if fsNode.isFolderish():
            fsFiles = []
            fsDir = fsNode.resourcepath
            fsDirDir = os.path.dirname(fsNode.resourcepath)
            os.path.walk(fsDir, self.walkFS, (fsFiles, ()))
            new = []
            replace = []
            for fn in fsFiles:
                if os.path.isabs(self.resourcepath):
                    pref = ''
                else:
                    pref = self.resourcepath + '/'
                destName = pref+fn[len(fsDirDir)+1:]
                if destName in self.zipFileNode.allFileNames:
                    replace.append( (destName, fn) )
                else:
                    new.append( (destName, fn) )
            # replace existing
            filesData = [ (arcname, '', open(filename, 'rb').read())
                          for arcname, filename in replace ]  
            self.replaceFilesInArchive(filesData)

            # append new
            if new:
                zf = zipfile.ZipFile(self.zipFileNode.resourcepath, 'a')
                try:
                    for arcname, filename in new:
                        zi = zipfile.ZipInfo(arcname)
                        zi.compress_type = zipfile.ZIP_DEFLATED
                        zf.writestr(zi, open(filename, 'rb').read())
                finally:
                    zf.close()
                self.zipFileNode.allFiles = None
        else:
            data = fsNode.load(mode='rb')
            # if already in archive, must be replaced, else can be appended
            #arcDir = os.path.dirname(self.resourcepath)
            destName = '/'.join([self.getArcDir(), fn])
            if destName in self.zipFileNode.allFileNames:
                # XXX prompt?
                self.replaceFilesInArchive([(destName, '', data)])
            else:
                zf = zipfile.ZipFile(self.zipFileNode.resourcepath, 'a')
                try:
                    zi = zipfile.ZipInfo(destName)
                    zi.compress_type = zipfile.ZIP_DEFLATED
                    zf.writestr(zi, data)
                finally:
                    zf.close()
                self.zipFileNode.allFiles = None

    def copyToFS(self, fsFolderNode):
        fn = os.path.join(fsFolderNode.resourcepath, self.name)

        zf = zipfile.ZipFile(self.zipFileNode.resourcepath)
        try:
            if self.isFolderish():
                try: os.mkdir(fn)
                except OSError: pass
                files = self.zipFileNode.getFiles(self.resourcepath, True)
                for arcName in files:
                    fn = os.path.join(fsFolderNode.resourcepath, arcName)
                    try: os.makedirs(os.path.dirname(fn))
                    except OSError: pass
                    open(fn, 'wb').write(zf.read(arcName))
            else:
                open(fn, 'wb').write(zf.read(self.resourcepath))
        finally:
            zf.close()

    def newFolder(self, name):
        zf = zipfile.ZipFile(self.zipFileNode.resourcepath, 'a')
        try:
            ad = self.getArcDir()
            if ad: ad +='/'
            newArcName = '%s%s/'%(ad, name)
            zi = zipfile.ZipInfo(newArcName)
            zi.flag_bits = 0x02
            zf.writestr(zi, '')
            self.zipFileNode.allFiles = None
        finally:
            zf.close()
        return name
        #raise Exception, 'The zipfile module does not suppport adding empty folders'

    def newBlankDocument(self, name=''):
        zf = zipfile.ZipFile(self.zipFileNode.resourcepath, 'a')
        try:
            ad = self.getArcDir()
            if ad: ad +='/'
            newArcName = '%s%s'%(ad, name)
            zi = zipfile.ZipInfo(newArcName)
            zf.writestr(zi, '')
            self.zipFileNode.allFiles = None
        finally:
            zf.close()
        return name

    def load(self, mode='rb'):
        zf = zipfile.ZipFile(self.zipFileNode.resourcepath, 'r')
        data = zf.read(self.resourcepath)
        if os.path.splitext(self.resourcepath)[1] in EditorHelper.binaryFilesReg:
            self.lineSep = None
            return data
        else:
            if data.find('\r\n') != -1:
                self.lineSep = '\r\n'
                return data.replace('\r\n', '\n')
            else:
                self.lineSep = '\n'
                return data
                

    def save(self, filename, data, mode='wb', overwriteNewer=true):
        self.replaceFilesInArchive([(self.resourcepath, filename, data)])

    def renameItem(self, name, newName):
        arcDir = self.getArcDir()
        oldfile = '/'.join([arcDir, name])
        newfile = '/'.join([arcDir, newName])
        self.replaceFilesInArchive([(oldfile, newfile, None)])

    def replaceFilesInArchive(self, filesData):
        # There seems to be no way to replace a zip entry.
        # Here the whole archive is recreated
        zipStream = StringIO(open(self.zipFileNode.resourcepath, 'rb').read())
        zfSrc = zipfile.ZipFile(zipStream, 'r')
        changed = False
        try:
            zfDst = zipfile.ZipFile(self.zipFileNode.resourcepath, 'w')
            try:
                for zi in zfSrc.filelist:
                    for fn, nfn, data in filesData:
                        if zi.filename == fn:
                            changed = True
                            if nfn:
                                zi.filename = nfn
                            if data is None:
                                zipData = data = zfSrc.read(fn)
                            elif os.path.splitext(zi.filename)[1] in \
                                  EditorHelper.binaryFilesReg:
                                zipData = data
                            # XXX wrong!
                            elif self.lineSep == '\r\n':
                                zipData = data.replace('\n', '\r\n')
                            else:
                                zipData = data
                            break
                    else:
                        zipData = zfSrc.read(zi.filename)
                    zfDst.writestr(zi, zipData)
            finally:
                zfDst.close()
        finally:
            zfSrc.close()

        if changed:
            self.zipFileNode.allFiles = None
        

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

    def getArcDir(self):
        return ''

    def openList(self):
        self.updateFilelists()
        # Add implicit folder entries
        for filename in self.allFileNames[:]:
            if filename[-1] == '/':
                # don't build if zip has folder entries
                break
            while 1:
                filename = os.path.dirname(filename)
                path = filename +'/'
                if path == '/':
                    break
                if path not in self.allFileNames:
                    self.allFileNames.insert(0, path)
                    self.allFiles.insert(0, zipfile.ZipInfo(path))
                
        return ZipItemNode.openList(self, '')

    def getFiles(self, base, nested=False):
        files = []
        if self.allFiles is None:
            self.updateFilelists()
            
        for file in self.allFiles:
            if file.filename[-1] == '/':
                fn = file.filename[:-1]
            else:
                fn = file.filename
            
            if nested:
                if fn.startswith(base):
                    files.append(file.filename)
            else:
                dir = os.path.dirname(fn)
                dirdir = os.path.dirname(dir)
                if dir and dirdir == base:
                    try: idx = files.index(dir+'/')
                    except ValueError: files.append(dir+'/')
                    
                if dir == base:
                    try: files.index(file.filename)
                    except ValueError: files.append(file.filename)
        return files

    def updateFilelists(self):
        zf = zipfile.ZipFile(self.resourcepath)
        self.allFiles = zf.filelist
        zf.close()

        self.allFileNames = [fl.filename for fl in self.allFiles]


def uriSplitZip(filename, zipfile, zipentry):
    return 'zip', zipfile, zipentry, filename

def findZipExplorerNode(category, respath, transports):
    zf = ZipFileNode(os.path.basename(category), category, None, -1, None, None)
    zf.openList()
    return zf.getNodeFromPath(respath)

#-------------------------------------------------------------------------------
# Register zip files as a subtype of file explorers
FileExplorer.FileSysNode.subExplorerReg['file'].append(
      (ZipFileNode, isZip, EditorHelper.imgZipFileModel))
ExplorerNodes.register(ZipItemNode, clipboard=ZipExpClipboard,
      controller=ZipController)
ExplorerNodes.uriSplitReg[('zip', 3)] = uriSplitZip
ExplorerNodes.transportFindReg['zip'] = findZipExplorerNode
ExplorerNodes.fileOpenDlgProtReg.append('zip')