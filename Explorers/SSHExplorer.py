import string, os, sys

from wxPython.wx import wxMenu, EVT_MENU, wxMessageBox, wxPlatform, wxOK, wxNewId, true, false

#sys.path.append('..')
import ExplorerNodes, EditorModels
from ProcessProgressDlg import ProcessProgressDlg

wxID_SSHOPEN = wxNewId()

class SSHController(ExplorerNodes.Controller, ExplorerNodes.ClipboardControllerMix):
    def __init__(self, editor, list):
        ExplorerNodes.ClipboardControllerMix.__init__(self)
        ExplorerNodes.Controller.__init__(self, editor)

        self.list = list
        self.menu = wxMenu()

        self.setupMenu(self.menu, self.list,
              ( (wxID_SSHOPEN, 'Open', self.OnOpenItems, '-'),
                (-1, '-', None, '') ) + self.clipMenuDef)
        self.toolbarMenus = [self.clipMenuDef]

    def destroy(self):
        ExplorerNodes.ClipboardControllerMix.destroy(self)
        self.toolbarMenus = ()
        self.menu.Destroy()

    def __del__(self):
        pass#self.menu.Destroy()


class SSHCatNode(ExplorerNodes.CategoryNode):
    defName = 'SSH'
    defaultStruct = {'username': '',
                     'cipher': '',
                     'host': '',
                     'scp_pass': '',
                     'root': '~'}
    def __init__(self, clipboard, config, parent):
        ExplorerNodes.CategoryNode.__init__(self, 'SSH', ('explorer', 'ssh'),
              clipboard, config, parent)

    def createParentNode(self):
        return self

    def createChildNode(self, name, props):
        return SSHItemNode(name, props, props['root'], self.clipboard, true,
              EditorModels.imgFSDrive, self)

    def createCatCompanion(self, catNode):
        comp = ExplorerNodes.CategoryDictCompanion(catNode.treename, self)
        return comp

class SSHItemNode(ExplorerNodes.ExplorerNode):
    protocol = 'ssh'
    def __init__(self, name, props, resourcepath, clipboard, isFolder, imgIdx, parent):
        ExplorerNodes.ExplorerNode.__init__(self, name, resourcepath, clipboard, imgIdx,
              parent, props)
        self.isFolder = isFolder

    def isFolderish(self):
        return self.isFolder

    def createChildNode(self, name, isFolder, props):
        item = SSHItemNode(name, props, self.resourcepath+'/'+name, self.clipboard,
              isFolder, isFolder and EditorModels.FolderModel.imgIdx or \
              EditorModels.TextModel.imgIdx, self)
        if not isFolder:
            item.imgIdx = EditorModels.identifyFile(name, localfs=false)[0].imgIdx
        return item

    def openList(self):
        res = []
        ls = self.execCmd('ls %s -la' % self.resourcepath)[1:]
        for line in ls:
            name = string.strip(string.split(line, ' ')[-1])
            if name not in ('.', '..'):
                res.append(self.createChildNode(name, line[0] == 'd', self.properties))
        return res

    def execCmd(self, cmd):
        dlg = ProcessProgressDlg(None,
            self.sshCmd(cmd), 'SSH listing', linesep = '\012')
        try:
            if dlg.ShowModal() == wxOK:
                return dlg.output
        finally:
            dlg.Destroy()

        return []

    def sshCmd(self, command):
        return 'ssh -v -l %(username)s -c %(cipher)s %(host)s '% self.properties + command

    def remotePath(self, filename):
        return '%(username)s@%(host)s:'%self.properties + self.resourcepath+\
               (filename and '/'+filename or '')

    def execSCP(self, cmd, dispCmd):
        dlg = ProcessProgressDlg(None, cmd, 'SCP copy', linesep = '\012',
              overrideDisplay = dispCmd)
        try:
            dlg.ShowModal()
        finally:
            dlg.Destroy()

    def buildSCPStrs(self, source, dest):
        return 'pscp -pw %s %s %s' % (self.properties['scp_pass'], source, dest), \
        'pscp -pw %s %s %s' %(len(self.properties['scp_pass'])*'*', source, dest)

    def copyFromFS(self, fsNode, fn=''):
        if not fn:
            fn = os.path.basename(fsNode.resourcepath)
        cmd, dispCmd = self.buildSCPStrs(fsNode.resourcepath, self.remotePath(fn))
        self.execSCP(cmd, dispCmd)

    def copyToFS(self, fsFolderNode, fn=''):
        if not fn:
            fn = os.path.basename(self.resourcepath)
        cmd, dispCmd = self.buildSCPStrs(self.remotePath(''),
             os.path.join(fsFolderNode.resourcepath, fn))
        self.execSCP(cmd, dispCmd)

    def moveFileFrom(self, other):
        fn = os.path.basename(other.resourcepath)
        self.execCmd('mv %s %s' % (other.resourcepath,
                                   self.resourcepath + '/' + fn))

    def copyFileFrom(self, other):
        fn = os.path.basename(other.resourcepath)
        self.execCmd('cp %s %s' % (other.resourcepath,
                                   self.resourcepath + '/' + fn))

    def deleteItems(self, names):
        absNames = []
        for name in names:
            absNames.append(self.resourcepath + '/' +name)
        self.execCmd('rm '+string.join(absNames, ' '))

    def renameItem(self, name, newName):
        self.execCmd('mv %s %s' % (self.resourcepath + '/' + name,
                                   self.resourcepath + '/' + newName))

    def load(self, mode='rb'):
        from FileExplorer import PyFileNode
        import tempfile
        fn = tempfile.mktemp()
        try:
            self.copyToFS(PyFileNode('', os.path.dirname(fn), None, -1, None, None), os.path.basename(fn))
            try:
                return open(fn, mode).read()
            finally:
                os.remove(fn)
        except Exception, error:
            raise ExplorerNodes.TransportLoadError(error, self.resourcepath)

    def save(self, filename, data, mode='wb'):
        from FileExplorer import PyFileNode
        import tempfile
        name = os.path.basename(self.resourcepath)
        fn = tempfile.mktemp()
        try:
            open(fn, mode).write(data)
            try:
                if self.parent:
                    self.parent.copyFromFS(PyFileNode('', fn, None, -1, None, None),
                          name)
                else:
                    raise 'No Parent!'
            finally:
                os.remove(fn)
        except Exception, error:
            raise ExplorerNodes.TransportSaveError(error, self.resourcepath)


class SSHExpClipboard(ExplorerNodes.ExplorerClipboard):
    def clipPaste_FileSysExpClipboard(self, node, nodes, mode):
        for clipnode in nodes:
            if mode == 'cut':
                node.copyFromFS(clipnode)
#                node.moveFileFrom(clipnode)
                self.clipNodes = []
            elif mode == 'copy':
                node.copyFromFS(clipnode)
#                node.copyFileFrom(clipnode)

    def clipPaste_SSHExpClipboard(self, node, nodes, mode):
        for sshNode in nodes:
            if mode == 'cut':
                node.moveFileFrom(sshNode)
                self.clipNodes = []
            elif mode == 'copy':
                node.copyFileFrom(sshNode)
 