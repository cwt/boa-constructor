#-----------------------------------------------------------------------------
# Name:        FileExplorer.py
# Purpose:     Classes for filesystem exploring
#
# Author:      Riaan Booysen
#
# Created:     2001/03/06
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2002 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Explorers.FileExplorer'

import string, os, time, stat

from wxPython.wx import *

import Preferences, Utils

import ExplorerNodes
from Models import Controllers, PythonEditorModels, EditorHelper

class FileSysCatNode(ExplorerNodes.CategoryNode):
#    protocol = 'config.file'
    itemProtocol = 'file'
    defName = Preferences.explorerFileSysRootDefault[0]
    defaultStruct = Preferences.explorerFileSysRootDefault[1]
    def __init__(self, clipboard, config, parent, bookmarks):
        ExplorerNodes.CategoryNode.__init__(self, 'Filesystem', ('explorer', 'file'),
              clipboard, config, parent)
        self.bookmarks = bookmarks

        if not self.entries and wxPlatform == '__WXMSW__':
            drives = {}
            for x in range(67, 90):
                driveName = '%s:\\'%(chr(x))
                if os.path.exists(driveName):
                    drives[driveName] = driveName

            self.entries = drives
            self.updateConfig()
            wxLogMessage('%d drives added to the filesystem definition.'%len(drives))

    def createParentNode(self):
        return self.parent

    def createCatCompanion(self, catNode):
        comp = ExplorerNodes.CategoryStringCompanion(catNode.treename, self)
        return comp

    def createChildNode(self, entry, value, forceFolder=true):
        if forceFolder: Node = NonCheckPyFolderNode
        else: Node = PyFileNode

        return Node(entry, value, self.clipboard, EditorHelper.imgFSDrive, self,
            self.bookmarks)

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

    def getNodeFromPath(self, respath, forceFolder=true):
        cn = self.createChildNode(os.path.basename(respath), respath, forceFolder)
        return cn


(wxID_FSOPEN, wxID_FSTEST, wxID_FSNEW, wxID_FSNEWFOLDER, wxID_FSCVS,
 wxID_FSBOOKMARK, wxID_FSFINDINFILES, wxID_FSFINDFILES, wxID_FSFILTERIMAGES,
 wxID_FSSETASCWD,
) = Utils.wxNewIds(10)

(wxID_FSFILTER, wxID_FSFILTERBOAMODULES, wxID_FSFILTERSTDMODULES,
 wxID_FSFILTERINTMODULES, wxID_FSFILTERALLMODULES,
) = Utils.wxNewIds(5)

filterDescrOrd = ['BoaFiles', 'StdFiles', 'BoaIntFiles', 'ImageFiles', 'AllFiles']

filterDescr = {'BoaFiles': ('Boa files', wxID_FSFILTERBOAMODULES),
               'StdFiles': ('Standard files', wxID_FSFILTERSTDMODULES),
               'BoaIntFiles': ('Internal files', wxID_FSFILTERINTMODULES),
               'ImageFiles': ('Image files', wxID_FSFILTERIMAGES),
               'AllFiles': ('All files', wxID_FSFILTERALLMODULES)}

class FileSysController(ExplorerNodes.Controller, ExplorerNodes.ClipboardControllerMix):
    bookmarkBmp = 'Images/Shared/Bookmark.png'
    findBmp = 'Images/Shared/Find.png'
    def __init__(self, editor, list, inspector, controllers):
        ExplorerNodes.Controller.__init__(self, editor)
        ExplorerNodes.ClipboardControllerMix.__init__(self)
        self.editor = editor

        self.list = list
        if controllers.has_key('cvs'):
            self.cvsController = controllers['cvs']
        else:
            self.cvsController = None

        self.menu = wxMenu()

        self.fileMenuDef = (
              (wxID_FSOPEN, 'Open', self.OnOpenItems, '-'),
              (-1, '-', None, '') ) +\
              self.clipMenuDef +\
            ( (wxID_FSSETASCWD, 'Set as os.cwd', self.OnSetAsSysCwd, '-'),
              (-1, '-', None, ''),
              (wxID_FSFINDINFILES, 'Find', self.OnFindFSItem, self.findBmp),
        )
        self.setupMenu(self.menu, self.list, self.fileMenuDef)

        filters = []
        for filter in filterDescrOrd:
            descr, wid = filterDescr[filter]
            filters.append( (wid, '+'+descr, self.OnFilterFSItems , '-') )

        self.fileFilterMenuDef = tuple(filters)
        self.fileFilterMenu = wxMenu()
        self.setupMenu(self.fileFilterMenu, self.list, self.fileFilterMenuDef)

        # Check default option
        self.fileFilterMenu.Check(wxID_FSFILTERBOAMODULES, true)

        self.menu.AppendMenu(wxID_FSFILTER, 'Filter', self.fileFilterMenu)

        if controllers.has_key('cvs'):
            self.menu.AppendMenu(wxID_FSCVS, 'CVS', controllers['cvs'].fileCVSMenu)

        self.toolbarMenus = [self.fileMenuDef]

    def destroy(self):
        ExplorerNodes.ClipboardControllerMix.destroy(self)
        self.fileFilterMenuDef = ()
        self.fileMenuDef = ()
        self.toolbarMenus = ()
        #print 'FileSysController', self.menu
        self.menu.Destroy()

    def OnTest(self, event):
        print self.list.node.clipboard.globClip.currentClipboard

    def OnFilterFSItems(self, event):
        evtid = event.GetId()
        self.groupCheckMenu(self.fileFilterMenu, self.fileFilterMenuDef, evtid, true)
        for filter in filterDescrOrd:
            descr, wid = filterDescr[filter]
            if wid == evtid:
                self.list.node.setFilter(filter)
                self.list.refreshCurrent()
                break

    def OnFindFSItem(self, event):
        import Search
        dlg = wxTextEntryDialog(self.list, 'Enter text:',
          'Find in files', '')
        try:
            if dlg.ShowModal() == wxID_OK:
                exts = self.list.node.getFilterExts()
                for ext in EditorHelper.getBinaryFiles():
                    try: exts.remove(ext)
                    except ValueError: pass

                res = Search.findInFiles(self.list, self.list.node.resourcepath,
                      dlg.GetValue(), filemask = exts,
                      progressMsg = 'Search files...', joiner = os.sep)
                nd = self.list.node
                self.list.node = ResultsFolderNode('Results', nd.resourcepath, nd.clipboard, -1, nd, nd.bookmarks)
                self.list.node.results = res
                self.list.node.lastSearch = dlg.GetValue()
                self.list.refreshCurrent()
        finally:
            dlg.Destroy()

    def OnSetAsSysCwd(self, event):
        node = self.list.getSelection()
        if node: path = node.resourcepath
        else: path  = self.list.node.resourcepath

        if os.path.isfile(path): path = os.path.split(path)[0]
        os.chdir(path)

        self.editor.setStatus('Updated os.cwd to %s'%path, ringBell=true)

class FileSysExpClipboard(ExplorerNodes.ExplorerClipboard):
    def clipPaste_FileSysExpClipboard(self, node, nodes, mode):
        # XXX Delayed cut (delete on paste or move) should clear the clipboard
        # XXX or refresh clipboard with new paths and clear 'cut' mode
        for clipnode in nodes:
            if mode == 'cut':
                node.moveFileFrom(clipnode)
                self.clipNodes = []
            elif mode == 'copy':
                node.copyFileFrom(clipnode)

    clipPaste_DefaultClipboard = clipPaste_FileSysExpClipboard

    def _genericFSPaste(self, node, nodes, mode):
        for other in nodes:
            other.copyToFS(node)

    def clipPaste_ZopeEClip(self, node, nodes, mode):
        # XXX Pasting a cut from Zope does not delete the cut items from Zope
        for zopeNode in nodes:
            zopeNode.downloadToFS(os.path.join(node.resourcepath, zopeNode.name))

    def clipPaste_FTPExpClipboard(self, node, nodes, mode):
        # XXX Pasting a cut from FTP does not delete the cut items from FTP
        for file in nodes:
            file.ftpConn.download(file.resourcepath,
                  os.path.join(node.resourcepath, file.name))

    clipPaste_SSHExpClipboard = _genericFSPaste
    clipPaste_ZipExpClipboard = _genericFSPaste
    clipPaste_DAVExpClipboard = _genericFSPaste

class PyFileNode(ExplorerNodes.ExplorerNode):
    protocol = 'file'
    filter = 'BoaFiles'
    lastSearch = ''
    subExplorerReg = {'file': [], 'folder': []}
    connection = false
    pathSep = os.sep
    def __init__(self, name, resourcepath, clipboard, imgIdx, parent,
          bookmarks = None, properties = {}):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, clipboard,
              imgIdx, parent, properties or {})
        self.bookmarks = bookmarks
        self.exts = EditorHelper.extMap.keys() + ['.py']
        self.entries = []

        self.doCVS = true
        self.doZip = true
        self.allowedProtocols = ['*']
        self.updateStdAttrs()

    def destroy(self):
        self.entries = []

    def isDir(self):
        return os.path.isdir(self.resourcepath)

    def isFolderish(self):
        return self.isDir() or filter(lambda se, rp=self.resourcepath,
              ap=self.allowedProtocols : (ap == ['*'] or se[0].protocol in ap) and se[1](rp),
              self.subExplorerReg['file'])

    def createParentNode(self):
        parent = os.path.abspath(os.path.join(self.resourcepath, '..'))
        if parent[-2:] == '..':
            parent = parent[:-2]
        return PyFileNode(os.path.basename(parent), parent, self.clipboard,
                  EditorHelper.imgFolder, self, self.bookmarks)

    def createChildNode(self, file, filename = ''):
        if not filename:
            filename = os.path.join(self.resourcepath, file)

        ext = string.lower(os.path.splitext(filename)[1])
        exts = self.getFilterExts()
        # Files
        if ('.*' in exts or ext in exts) and os.path.isfile(filename):
            for other, otherIdFunc, imgIdx in self.subExplorerReg['file']:
                if '*' in self.allowedProtocols or \
                      other.protocol in self.allowedProtocols:
                    if otherIdFunc(filename):
                        return 'fol', other(file, filename, self.clipboard,
                              imgIdx, self, self.bookmarks)
            return 'mod', PyFileNode(file, filename, self.clipboard,
              Controllers.identifyFile(filename,
              localfs=self.filter == 'BoaFiles')[0].imgIdx, self, self.bookmarks,
              {'datetime': time.strftime('%a %b %d %H:%M:%S %Y',
                           time.gmtime(os.stat(filename)[stat.ST_MTIME]))})
        # Directories
        elif os.path.isdir(filename):
            for other, otherIdFunc, imgIdx in self.subExplorerReg['folder']:
                if self.filter == 'BoaFiles' and \
                  imgIdx == PythonEditorModels.PackageModel.imgIdx and \
                  '*' in self.allowedProtocols or '*' in self.allowedProtocols or \
                      other.protocol in self.allowedProtocols:
                    if otherIdFunc(filename):
                        return 'fol', other(file, filename, self.clipboard,
                              imgIdx, self, self.bookmarks)
            return 'fol', PyFileNode(file, filename, self.clipboard,
                  EditorHelper.imgFolder, self, self.bookmarks)
        else:
            return '', None

    def openList(self):
        try:
            files = os.listdir(self.resourcepath)
        except Exception, err:
            raise ExplorerNodes.TransportError(err)
        files.sort()
        entries = {'mod': [], 'fol': []}

        for file in files:
            tp, node = self.createChildNode(file)
            if node:
                entries[tp].append(node)

        self.entries = entries['fol'] + entries['mod']
        return self.entries

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

    def newFolder(self, name):
        os.mkdir(os.path.join(self.resourcepath, name))
        return name

    def newBlankDocument(self, name=''):
        newpath = os.path.join(self.resourcepath, name)
        if not os.path.exists(newpath):
            open(newpath, 'w').write(' ')
        return name

    def copyFileFrom(self, node):
        """ Copy node into self (only called for folders)"""
        import shutil
        if not node.isDir():
            if node.resourcepath == os.path.join(self.resourcepath, node.name):
                newNameBase = os.path.join(self.resourcepath, 'copy%s_of_'+node.name)
                num = ''
                while 1:
                    newName = newNameBase%num
                    if os.path.exists(newName):
                        try: num = str(int(num) + 1)
                        except: num = '2'
                    else:
                        shutil.copy(node.resourcepath, newName)
                        break
            else:
                shutil.copy(node.resourcepath, self.resourcepath)
##                names = map(lambda n: n.name, self.entries)
##                dir, name = os.path.split(self.resourcepath)
##                name, ext = os.path.splitext(name)
##                name = Util.getValidName(names, name, ext)
##                shutil.copy(node.resourcepath, name)
##            else:
##            shutil.copy(node.resourcepath, self.resourcepath)
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
        return {'BoaFiles': self.exts + ['.py'],
                'StdFiles': self.exts + ['.py'],
                'BoaIntFiles': EditorHelper.internalFilesReg +\
                               EditorHelper.pythonBinaryFilesReg ,
                'ImageFiles': EditorHelper.imageExtReg,
                'AllFiles': ('.*',)}[self.filter]

    def load(self, mode='rb'):
        try:
            return open(self.resourcepath, mode).read()
        except IOError, error:
            raise ExplorerNodes.TransportLoadError(error, self.resourcepath)

    def save(self, filename, data, mode='wb'):
        if self.resourcepath != filename:
            self.resourcepath = filename
            self.name = os.path.basename(self.resourcepath)
        try:
            open(self.resourcepath, mode).write(data)
        except IOError, error:
            raise ExplorerNodes.TransportSaveError(error, self.resourcepath)
        self.updateStdAttrs()

    def getNodeFromPath(self, respath):
        name = os.path.basename(respath)
        return self.createChildNode(name, respath)

    def updateStdAttrs(self):
        self.stdAttrs['read-only'] = os.path.exists(self.resourcepath) and \
              not os.access(self.resourcepath, os.W_OK)

    def setStdAttr(self, attr, value):
        if attr == 'read-only':
            os.chmod(self.resourcepath, value and 0444 or 0666)

        self.updateStdAttrs()

FileSysController.Node = PyFileNode

def isPackage(filename):
    return os.path.exists(os.path.join(filename, PythonEditorModels.PackageModel.pckgIdnt))

# Register Packages as a File Explorer sub type
PyFileNode.subExplorerReg['folder'].append(
      (PyFileNode, isPackage, PythonEditorModels.PackageModel.imgIdx),
)

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
        mod, cntrl = node.open(editor)
        if mod.views.has_key('Source'):
            mod.views['Source'].doFind(self.lastSearch)
            mod.views['Source'].doNextMatch()
        return mod, cntrl

    def getTitle(self):
        return 'Find results for %s in %s' % (self.lastSearch, self.resourcepath)

class NonCheckPyFolderNode(PyFileNode):
    def isFolderish(self):
        return true

class CurWorkDirNode(PyFileNode):
    protocol = 'os.cwd'
    def __init__(self, clipboard, parent, bookmarks):
        self.cwd = os.path.abspath(os.getcwd())
        PyFileNode.__init__(self, 'os.cwd', self.cwd, clipboard,
              EditorHelper.imgPathFolder, parent)
        self.bookmarks = bookmarks
        self.bold = true
        #self.setFilter('AllFiles')

    def openList(self):
        self.cwd = self.resourcepath = os.path.abspath(os.getcwd())
        return PyFileNode.openList(self)

    def getTitle(self):
        return 'os.cwd://%s'%self.cwd
    def getURI(self):
        return self.getTitle()

#-------------------------------------------------------------------------------
ExplorerNodes.register(PyFileNode, clipboard=FileSysExpClipboard,
      confdef=('explorer', 'file'), controller=FileSysController,
      category=FileSysCatNode)
ExplorerNodes.register(CurWorkDirNode, clipboard='file', controller='file')
